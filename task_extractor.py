import json
from openai import OpenAI
from config import Config

class TaskExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY, base_url=Config.OPENAI_BASE_URL)
        
    def extract_tasks(self, text: str) -> list:
        """
        Extracts action items, responsibilities, and deadlines from the transcript.
        Returns a list of dictionaries.
        """
        prompt = f"""
        You are a meticulous task manager. Extract all action items from the following meeting transcript.
        For each action item, identify:
        1. The person responsible (Who)
        2. The task description (What)
        3. The deadline, if mentioned (When)
        
        Respond ONLY with a JSON array of objects. Each object should have the keys: "who", "what", "deadline".
        If a deadline is not mentioned, use "TBD" for the "deadline" field.
        
        Transcript:
        {text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional task extraction assistant. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={ "type": "json_object" } if Config.DEFAULT_MODEL in ["gpt-4-turbo-preview", "gpt-3.5-turbo-0125"] else None
            )
            
            # Basic parsing of the response content to JSON
            content = response.choices[0].message.content
            
            # Extract JSON block using regex in case of conversational filler
            import re
            json_match = re.search(r'```(?:json)?(.*?)```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1).strip()
            else:
                content = content.strip()
                
            try:
                tasks = json.loads(content)
                if isinstance(tasks, dict) and "tasks" in tasks:
                    tasks = tasks["tasks"] # if the model returns {"tasks": [...]}
                
                if not isinstance(tasks, list):
                    tasks = [tasks]
                    
                valid_tasks = []
                for t in tasks:
                    if isinstance(t, dict):
                        valid_tasks.append(t)
                    else:
                        valid_tasks.append({"who": "Unassigned", "what": str(t), "deadline": "TBD"})
                return valid_tasks
            except json.JSONDecodeError:
                # Fallback if json parsing fails
                return [{"who": "System", "what": "Failed to parse tasks into JSON format. Raw output: " + content, "deadline": "N/A"}]
                
        except Exception as e:
            return [{"who": "System", "what": f"Error extracting tasks: {str(e)}", "deadline": "N/A"}]
