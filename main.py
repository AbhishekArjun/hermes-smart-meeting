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

# Vercel Serverless Function App Entrypoint
app = FastAPI(title="Hermes Smart Meeting API")

class MeetingRequest(BaseModel):
    transcript: str

@app.post("/api/process")
def process_meeting(request: MeetingRequest):
    agent = HermesAgent()
    return agent.run_workflow(request.transcript)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Hermes API is running."}

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
