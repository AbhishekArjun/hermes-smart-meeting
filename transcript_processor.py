class TranscriptProcessor:
    def process(self, raw_text: str) -> str:
        """
        Cleans and formats the raw transcript text before sending it to the LLM.
        """
        if not raw_text:
            raise ValueError("Transcript text cannot be empty.")
        
        # In a real-world scenario, we might remove filler words, correct obvious OCR/STT errors,
        # or split very large texts into chunks. For now, we do basic cleaning.
        cleaned_text = raw_text.strip()
        
        # Replace multiple newlines with a single space or standard spacing
        import re
        cleaned_text = re.sub(r'\n+', '\n', cleaned_text)
        
        return cleaned_text

    def load_from_file(self, file_path: str) -> str:
        """
        Loads a transcript from a text file.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return self.process(f.read())
