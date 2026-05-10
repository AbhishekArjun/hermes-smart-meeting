from openai import OpenAI
from config import Config

class Summarizer:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY, base_url=Config.OPENAI_BASE_URL)
        
    def summarize(self, text: str) -> str:
        """
        Uses the LLM to generate a professional summary of the meeting transcript.
        """
        prompt = f"""
        You are an expert executive assistant. Summarize the following meeting transcript clearly and concisely.
        Focus on the main topics discussed, key decisions made, and overall context.
        Use professional formatting with bullet points where appropriate.
        
        Transcript:
        {text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional meeting assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating summary: {str(e)}"
