# Web Content Analyzer

This project is a web-based application that allows users to analyze the content of any webpage using an AI agent. The application uses a combination of Python (FastAPI) for the backend and simple HTML/CSS/JavaScript for the frontend.

## Folder Structure

```
project/
├── .env
├── .gitignore
├── app.js
├── app.py
├── index.html
├── style.css
├── agent.py
└── web.ipynb
```

## Project Overview

### How It Works

1. **User Input**: Users enter a URL and a question in the web interface.
2. **Backend Processing**: The FastAPI backend (`app.py`) handles the request and invokes the AI agent (`agent.py`).
3. **AI Agent Analysis**:
   - **Content Extraction**: Fetches and extracts relevant content from the provided URL.
   - **Relevance Detection**: Uses semantic analysis to determine if the content is relevant to the user's question.
   - **Answer Generation**: Generates an answer based on the content or performs a web search if the content is irrelevant.
4. **Frontend Display**: The results are displayed in the web interface, including the answer and metrics like relevance score.

### Key Components

- **AI Agent (`agent.py`)**: Contains the core logic for web content analysis, including content extraction, relevance detection, and answer generation.
- **Backend (`app.py`)**: FastAPI application that handles HTTP requests and interacts with the AI agent.
- **Frontend (`index.html`, `style.css`, `app.js`)**: Web interface for user interaction and result display.

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python packages (listed in `requirements.txt`)

### Setup

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   - Create a `.env` file with your API keys:
     ```
     GROQ_API_KEY=your_groq_api_key
     ```

3. **Run the Backend**:
   ```bash
   uvicorn app:app --reload
   ```

4. **Open the Frontend**:
   - Open `index.html` in a web browser.

## Usage

1. **Enter URL and Question**:
   - In the web interface, enter the URL of the webpage you want to analyze.
   - Enter your question about the webpage.

2. **Analyze**:
   - Click the "Analyze" button to start the analysis.

3. **View Results**:
   - The answer and metrics (relevance score, source) will be displayed in the results section.

## Requirements

### Python Packages

Create a `requirements.txt` file with the following dependencies:

```
fastapi
uvicorn
python-dotenv
httpx
beautifulsoup4
sentence-transformers
scikit-learn
duckduckgo-search
groq
```

### Frontend

- Simple HTML/CSS/JavaScript (no Node.js required)

## Contributing

1. **Fork the Repository**: Fork the project on GitHub.
2. **Clone the Repository**: Clone the forked repository to your local machine.
3. **Create a New Branch**: Create a new branch for your changes.
4. **Make Changes**: Implement your changes or fixes.
5. **Test**: Ensure your changes work as expected.
6. **Commit and Push**: Commit your changes and push them to your fork.
7. **Create a Pull Request**: Create a pull request from your fork to the main repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.