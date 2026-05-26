import argparse
import uvicorn
import json
import sys
from main import app, HermesAgent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes Smart Meeting Agent")
    parser.add_argument("--transcript", type=str, help="Path to transcript file to process locally")
    args = parser.parse_args()

    if args.transcript:
        print(f"Processing transcript: {args.transcript}")
        try:
            with open(args.transcript, "r") as f:
                transcript_text = f.read()
            
            agent = HermesAgent()
            results = agent.run_workflow(transcript_text)
            
            with open("results.json", "w") as f:
                json.dump(results, f, indent=4)
                
            print("Processing complete. Results saved to results.json")
            sys.exit(0)
        except Exception as e:
            print(f"Error processing transcript: {e}")
            sys.exit(1)

    print("Starting Hermes Smart Meeting Assistant (FastAPI Frontend)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
