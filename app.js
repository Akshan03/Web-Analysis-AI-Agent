let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];
let currentStream = null;

function updateHistoryDisplay() {
    const container = document.getElementById('history-container');
    container.innerHTML = chatHistory.map((item, index) => `
        <div class="history-item" onclick="loadHistory(${index})">
            ${item.question.substring(0, 40)}...
        </div>
    `).join('');
}

function loadHistory(index) {
    const item = chatHistory[index];
    document.getElementById('urlInput').value = item.url;
    document.getElementById('questionInput').value = item.question;
    document.getElementById('answer-container').innerHTML = item.answer;
    document.getElementById('metrics-container').innerHTML = `
        Relevance Score: ${item.relevance_score}<br>
        Source: ${item.source}
    `;
}

async function analyzeContent() {
    const url = document.getElementById('urlInput').value;
    const question = document.getElementById('questionInput').value;
    
    if (!url || !question) return;
    
    // Clear previous content
    document.getElementById('answer-container').innerHTML = '▌';
    document.getElementById('metrics-container').innerHTML = 'Analyzing...';

    try {
        const response = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                question: question
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let answer = '';
        let metricsReceived = false;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (!line.startsWith('data: ')) continue; // Skip invalid lines
                
                try {
                    // Remove "data: " prefix and parse JSON
                    const data = JSON.parse(line.replace(/^data: /, ''));
                    
                    if (data.answer) {
                        answer += data.answer;
                        document.getElementById('answer-container').textContent = answer + '▌';
                    }
                    
                    if (data.metrics) {
                        metricsReceived = true;
                        document.getElementById('metrics-container').innerHTML = `
                            Relevance Score: ${data.metrics.relevance_score.toFixed(2)}<br>
                            Source: ${data.metrics.source}
                        `;
                    }
                } catch (e) {
                    console.error('Error parsing chunk:', e);
                }
            }
        }

        // Remove typing cursor after completion
        if (!metricsReceived) {
            document.getElementById('metrics-container').innerHTML = 
                'Analysis completed without metrics';
        }
        document.getElementById('answer-container').textContent = answer;

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('metrics-container').innerHTML = 
            `Error: ${error.message}`;
    }
}

// Initial history load
updateHistoryDisplay();