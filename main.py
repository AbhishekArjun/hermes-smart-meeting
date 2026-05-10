from transcript_processor import TranscriptProcessor
from summarizer import Summarizer
from task_extractor import TaskExtractor
from followup_generator import FollowupGenerator
from fastapi import FastAPI
from pydantic import BaseModel

class HermesAgent:
    """
    The main orchestrator for the Smart Meeting Assistant workflow.
    Coordinates the execution of various specialized modules.
    """
    
    def __init__(self):
        self.processor = TranscriptProcessor()
        self.summarizer = Summarizer()
        self.task_extractor = TaskExtractor()
        self.followup_generator = FollowupGenerator()
        
    def run_workflow(self, raw_transcript: str) -> dict:
        """
        Executes the end-to-end meeting processing pipeline.
        """
        results = {
            "status": "processing",
            "summary": None,
            "tasks": [],
            "followup_email": None,
            "error": None
        }
        
        try:
            # Step 1: Process and clean transcript
            clean_transcript = self.processor.process(raw_transcript)
            
            # Step 2: Generate Summary
            results["summary"] = self.summarizer.summarize(clean_transcript)
            
            # Step 3: Extract Action Items
            results["tasks"] = self.task_extractor.extract_tasks(clean_transcript)
            
            # Step 4: Generate Follow-up Draft
            results["followup_email"] = self.followup_generator.generate_followup(
                results["summary"], 
                results["tasks"]
            )
            
            results["status"] = "success"
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            
        return results

# Optional FastAPI setup for Vercel deployment
try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel
    import os
    from config import Config

    app = FastAPI(title="Hermes Smart Meeting API")

    class MeetingRequest(BaseModel):
        transcript: str

    @app.post("/api/process")
    async def process_meeting(meeting_request: MeetingRequest, req: Request):
        # Allow dynamic API key override from the frontend
        api_key = req.headers.get("X-API-Key")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            Config.OPENAI_API_KEY = api_key
            
        agent = HermesAgent()
        return agent.run_workflow(meeting_request.transcript)

    @app.get("/", response_class=HTMLResponse)
    def serve_ui():
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hermes Smart Meeting Assistant</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
                
                :root {
                    --bg-grad: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                    --glass-bg: rgba(255, 255, 255, 0.05);
                    --glass-border: rgba(255, 255, 255, 0.1);
                    --primary: #3b82f6;
                    --primary-hover: #2563eb;
                    --text-main: #f8fafc;
                    --text-muted: #cbd5e1;
                }

                body {
                    font-family: 'Inter', sans-serif;
                    background: var(--bg-grad);
                    color: var(--text-main);
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    justify-content: center;
                    align-items: flex-start;
                    padding: 2rem;
                    box-sizing: border-box;
                }

                .container {
                    width: 100%;
                    max-width: 900px;
                    background: var(--glass-bg);
                    backdrop-filter: blur(16px);
                    -webkit-backdrop-filter: blur(16px);
                    border: 1px solid var(--glass-border);
                    border-radius: 24px;
                    padding: 2.5rem;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                    animation: fadeIn 0.8s ease-out;
                }

                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }

                h1 {
                    font-weight: 600;
                    font-size: 2.5rem;
                    margin-top: 0;
                    background: linear-gradient(to right, #60a5fa, #a78bfa);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    text-align: center;
                }

                p.subtitle {
                    text-align: center;
                    color: var(--text-muted);
                    margin-bottom: 2rem;
                }

                .input-group {
                    margin-bottom: 1.5rem;
                }

                label {
                    display: block;
                    margin-bottom: 0.5rem;
                    font-weight: 600;
                    color: var(--text-muted);
                    font-size: 0.9rem;
                }

                input[type="password"], textarea {
                    width: 100%;
                    background: rgba(0, 0, 0, 0.2);
                    border: 1px solid var(--glass-border);
                    border-radius: 12px;
                    color: white;
                    font-family: 'Inter', sans-serif;
                    padding: 1rem;
                    box-sizing: border-box;
                    transition: all 0.3s ease;
                    font-size: 1rem;
                }

                input[type="password"]:focus, textarea:focus {
                    outline: none;
                    border-color: var(--primary);
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
                }

                textarea {
                    resize: vertical;
                    min-height: 200px;
                }

                button {
                    width: 100%;
                    background: var(--primary);
                    color: white;
                    border: none;
                    padding: 1rem;
                    border-radius: 12px;
                    font-size: 1.1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }

                button:hover {
                    background: var(--primary-hover);
                    transform: translateY(-2px);
                    box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
                }

                .spinner {
                    display: none;
                    width: 20px;
                    height: 20px;
                    border: 3px solid rgba(255,255,255,0.3);
                    border-radius: 50%;
                    border-top-color: white;
                    animation: spin 1s ease-in-out infinite;
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    margin-top: -10px;
                    margin-left: -10px;
                }

                @keyframes spin {
                    to { transform: rotate(360deg); }
                }

                .button-text.hidden { opacity: 0; }

                #results {
                    display: none;
                    margin-top: 2rem;
                    animation: fadeIn 0.5s ease-out;
                }

                .tabs {
                    display: flex;
                    gap: 1rem;
                    margin-bottom: 1.5rem;
                    border-bottom: 1px solid var(--glass-border);
                    padding-bottom: 0.5rem;
                }

                .tab {
                    background: none;
                    border: none;
                    color: var(--text-muted);
                    font-size: 1rem;
                    font-weight: 600;
                    padding: 0.5rem 1rem;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    border-radius: 8px;
                    width: auto;
                }

                .tab:hover {
                    color: white;
                    background: rgba(255,255,255,0.05);
                }

                .tab.active {
                    color: #60a5fa;
                    background: rgba(96, 165, 250, 0.1);
                }

                .tab-content {
                    display: none;
                    background: rgba(0,0,0,0.2);
                    border: 1px solid var(--glass-border);
                    border-radius: 12px;
                    padding: 1.5rem;
                    white-space: pre-wrap;
                    font-size: 0.95rem;
                    line-height: 1.6;
                    color: #e2e8f0;
                }

                .tab-content.active {
                    display: block;
                    animation: fadeIn 0.4s ease-out;
                }

                .task-card {
                    background: rgba(255,255,255,0.03);
                    border: 1px solid var(--glass-border);
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                    transition: transform 0.2s;
                }
                .task-card:hover {
                    transform: translateX(5px);
                    border-color: rgba(255,255,255,0.2);
                }
                .task-who { font-weight: 600; color: #a78bfa; margin-bottom: 0.25rem; }
                .task-what { color: #f1f5f9; margin-bottom: 0.5rem; }
                .task-deadline { font-size: 0.85rem; color: #94a3b8; display: inline-block; background: rgba(0,0,0,0.3); padding: 0.2rem 0.5rem; border-radius: 4px; }

                .error {
                    color: #ef4444;
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                    padding: 1rem;
                    border-radius: 8px;
                    margin-top: 1rem;
                    display: none;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Hermes Assistant</h1>
                <p class="subtitle">AI-powered meeting summarization and task extraction</p>

                <div class="input-group">
                    <label for="apiKey">Groq API Key (Optional if set in environment)</label>
                    <input type="password" id="apiKey" placeholder="gsk_...">
                </div>

                <div class="input-group">
                    <label for="transcript">Meeting Transcript</label>
                    <textarea id="transcript" placeholder="Paste your meeting transcript here..."></textarea>
                </div>

                <button id="runBtn" onclick="runWorkflow()">
                    <span class="button-text">🚀 Run Hermes Agent</span>
                    <div class="spinner" id="spinner"></div>
                </button>

                <div id="errorBox" class="error"></div>

                <div id="results">
                    <div class="tabs">
                        <button class="tab active" onclick="switchTab('summary')">📝 Summary</button>
                        <button class="tab" onclick="switchTab('tasks')">✅ Action Items</button>
                        <button class="tab" onclick="switchTab('followup')">📧 Follow-up Email</button>
                    </div>

                    <div id="summaryContent" class="tab-content active"></div>
                    <div id="tasksContent" class="tab-content"></div>
                    <div id="followupContent" class="tab-content"></div>
                </div>
            </div>

            <script>
                function switchTab(tabId) {
                    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                    event.target.classList.add('active');
                    document.getElementById(tabId + 'Content').classList.add('active');
                }

                async function runWorkflow() {
                    const transcript = document.getElementById('transcript').value;
                    const apiKey = document.getElementById('apiKey').value;
                    const btn = document.getElementById('runBtn');
                    const btnText = document.querySelector('.button-text');
                    const spinner = document.getElementById('spinner');
                    const errorBox = document.getElementById('errorBox');
                    const results = document.getElementById('results');

                    if (!transcript.trim()) {
                        showError("Please enter a transcript.");
                        return;
                    }

                    btn.disabled = true;
                    btnText.classList.add('hidden');
                    spinner.style.display = 'block';
                    errorBox.style.display = 'none';
                    results.style.display = 'none';

                    try {
                        const headers = { 'Content-Type': 'application/json' };
                        if (apiKey) headers['X-API-Key'] = apiKey;

                        const response = await fetch('/api/process', {
                            method: 'POST',
                            headers: headers,
                            body: JSON.stringify({ transcript: transcript })
                        });

                        const data = await response.json();

                        if (!response.ok) throw new Error(data.detail || 'API request failed');
                        if (data.status === 'failed') throw new Error(data.error || 'Agent workflow failed');

                        document.getElementById('summaryContent').textContent = data.summary || "No summary generated.";

                        const tasksContainer = document.getElementById('tasksContent');
                        tasksContainer.innerHTML = '';
                        if (data.tasks && data.tasks.length > 0) {
                            data.tasks.forEach(task => {
                                const card = document.createElement('div');
                                card.className = 'task-card';
                                card.innerHTML = `
                                    <div class="task-who">👤 ${escapeHtml(task.who || 'Unassigned')}</div>
                                    <div class="task-what">${escapeHtml(task.what || 'No description')}</div>
                                    <div class="task-deadline">⏳ Due: ${escapeHtml(task.deadline || 'TBD')}</div>
                                `;
                                tasksContainer.appendChild(card);
                            });
                        } else {
                            tasksContainer.innerHTML = '<i>No action items identified.</i>';
                        }

                        document.getElementById('followupContent').textContent = data.followup_email || "No follow-up email generated.";

                        results.style.display = 'block';
                        document.querySelector('.tab').click(); // switch to first tab
                    } catch (err) {
                        showError(err.message);
                    } finally {
                        btn.disabled = false;
                        btnText.classList.remove('hidden');
                        spinner.style.display = 'none';
                    }
                }

                function showError(msg) {
                    const errorBox = document.getElementById('errorBox');
                    errorBox.textContent = "⚠️ Error: " + msg;
                    errorBox.style.display = 'block';
                }

                function escapeHtml(unsafe) {
                    return (unsafe || '').toString()
                         .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
                         .replace(/"/g, "&quot;").replace(/'/g, "&#039;");
                }
            </script>
        </body>
        </html>
        """
        return html_content

except ImportError:
    pass

if __name__ == "__main__":
    # A simple test for the orchestrator
    sample_text = """
    Alice: Let's start the meeting. We need to discuss the Q3 marketing plan.
    Bob: I've looked at the numbers, and we should increase our social media spend by 15%.
    Alice: Agreed. Bob, can you finalize the budget by next Friday?
    Bob: Yes, I'll have it done.
    Charlie: What about the new website launch?
    Alice: Charlie, please ensure the landing pages are ready by Wednesday.
    Charlie: Will do.
    """
    
    agent = HermesAgent()
    print("Running Hermes Agent workflow...")
    output = agent.run_workflow(sample_text)
    
    if output["status"] == "success":
        print("\n=== SUMMARY ===")
        print(output["summary"])
        print("\n=== TASKS ===")
        for t in output["tasks"]:
            print(t)
        print("\n=== FOLLOW-UP EMAIL ===")
        print(output["followup_email"])
    else:
        print(f"Workflow failed: {output['error']}")
