from openai import OpenAI
from config import Config

class FollowupGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY, base_url=Config.OPENAI_BASE_URL)
        
    def generate_followup(self, summary: str, tasks: list) -> str:
        """
        Generates a professional email draft based on the meeting summary and tasks.
        """
        
        # Format tasks into a readable string
        tasks_str = ""
        for task in tasks:
            who = task.get('who', 'Unassigned')
            what = task.get('what', 'No description')
            deadline = task.get('deadline', 'TBD')
            tasks_str += f"- **{who}**: {what} (Due: {deadline})\n"
            
        if not tasks_str:
            tasks_str = "- No specific action items identified.\n"
            
        prompt = f"""
        You are an expert executive assistant. Based on the following meeting summary and action items, 
        draft a professional follow-up email to be sent to all meeting attendees.
        
        The email should be polite, concise, and clearly outline the next steps and responsibilities.
        Use "Abhishek Arjun" as the sender name at the end of the email.
        
        Meeting Summary:
        {summary}
        
        Action Items:
        {tasks_str}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional email drafting assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating follow-up email: {str(e)}"
