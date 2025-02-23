import json
import numpy as np
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, HttpUrl
from agent import agent, is_relevant

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    url: HttpUrl = Field(..., example="https://example.com")
    question: str = Field(..., min_length=3, example="What is this website about?")

def convert_numpy_types(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    return obj

@app.post("/analyze")
def analyze(request_data: AnalysisRequest):
    try:
        result = agent.invoke({
            "url": str(request_data.url),
            "question": request_data.question,
            "content": "",
            "final_answer": ""
        })
        
        content = result.get("content", "")
        relevance_score = float(is_relevant(request_data.question, content))
        source = "Web Page" if relevance_score > 0.6 else "Web Search"
        
        answer_words = result["final_answer"].split()
        
        def generate():
            for word in answer_words:
                yield f'data: {json.dumps({"answer": word + " "})}\n\n'
            
            metrics = convert_numpy_types({
                "relevance_score": relevance_score,
                "source": source
            })
            
            yield f'data: {json.dumps({"metrics": metrics})}\n\n'
        
        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)