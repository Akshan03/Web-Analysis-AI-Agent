from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from trafilatura import fetch_url, extract
from langchain_openai import ChatOpenAI
from duckduckgo_search import DDGS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import httpx
import json
import os
import re
from groq import Groq
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")  
groq_client = Groq(api_key=groq_api_key)

def fetch_web_content(url: str) -> str:
    """Improved technical content extraction with browser headers"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = httpx.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content = soup.find('div', class_='entry-content') or soup.find('article') or soup.find('main')
        if not content:
            content = soup.body
            
        text = content.get_text('\n', strip=True)
        return '\n'.join([line for line in text.split('\n') if len(line) > 40])[:15000]
    except Exception as e:
        print(f"Error fetching content: {e}")
        return ""

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def get_embeddings(text: str) -> List[float]:
    return model.encode(text, convert_to_tensor=False).tolist()

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def is_relevant(question: str, context: str, threshold: float = 0.6) -> float:
    if not context:
        return 0.0
    
    question_keywords = set(question.lower().split())
    
    chunks = chunk_text(context, chunk_size=1000)
    if not chunks:
        return 0.0
    
    question_emb = model.encode(question, convert_to_tensor=False)
    context_embs = model.encode(chunks, convert_to_tensor=False)
    similarities = cosine_similarity([question_emb], context_embs)[0]
    
    top_indices = sorted(range(len(similarities)), key=lambda i: -similarities[i])[:2]
    top_chunks = [chunks[i] for i in top_indices]
    
    keyword_found = any(any(kw in chunk.lower() for kw in question_keywords) for chunk in top_chunks)
    
    max_score = max(similarities)
    
    if not keyword_found:
        max_score = 0.0
    
    return max_score if max_score > threshold else 0.0

def answer_from_web(question: str, context: str) -> str:
    chunks = chunk_text(context, chunk_size=2000)
    relevant_chunks = []
    
    question_emb = model.encode(question, convert_to_tensor=False)
    chunk_embs = model.encode(chunks, convert_to_tensor=False)
    similarities = cosine_similarity([question_emb], chunk_embs)[0]
    
    top_indices = sorted(range(len(similarities)), key=lambda i: -similarities[i])[:4]
    for idx in top_indices:
        relevant_chunks.append(chunks[idx])
    
    prompt = f"""
    Analyze the following information from the web to answer the question.
    Avoid hallucination and stick strictly to the provided context. If unsure, state that no precise information is available.

    Context:
    ---
    {''.join(relevant_chunks)}
    ---

    Question: {question}
    
    Answer in detail:
    """
    
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0.2,
            max_tokens=500
        )
        return f"[Web Context Answer] {response.choices[0].message.content}"
    except Exception as e:
        print(f"Error generating web answer: {e}")
        return answer_from_ddg(question)

def answer_from_ddg(question: str) -> str:
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(question, max_results=5)]  # More results
        
        context = "\n".join([f"{r['title']}: {r['body']}" for r in results])
        
        prompt = f"""Answer this question based on web search results:
        Question: {question}
        Search Results: {context}
        Answer in a clear paragraph:"""
        
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0.5,
        )
        return f"[Web Search Answer] {response.choices[0].message.content}"
    except Exception as e:
        print(f"Error in DDG answer: {e}")
        return "Could not generate an answer at this time"

class AgentState(TypedDict):
    url: str
    question: str
    content: str
    final_answer: str

def fetch_content(state: AgentState):
    content = fetch_web_content(state["url"])
    return {"content": content}

def generate_answer(state: AgentState):
    question = state["question"]
    content = state["content"]
    
    if is_relevant(question, content):
        return {"final_answer": answer_from_web(question, content)}
    return {"final_answer": answer_from_ddg(question)}

workflow = StateGraph(AgentState)
workflow.add_node("fetch_content", fetch_content)
workflow.add_node("generate_answer", generate_answer)
workflow.set_entry_point("fetch_content")
workflow.add_edge("fetch_content", "generate_answer")
workflow.add_edge("generate_answer", END)
agent = workflow.compile()