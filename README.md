# Hermes Smart Meeting Assistant

Hermes is a modular, AI-powered Smart Meeting Assistant that automates post-meeting workflows. Built using Streamlit and powered by Groq's fast LLMs (using the `llama-3.3-70b-versatile` model), Hermes analyzes meeting transcripts to generate summaries, extract action items, and draft follow-up emails.

## Features

- **Multi-step Orchestration**: A modular agent framework (`HermesAgent`) coordinates specialized tasks.
- **Transcript Processing**: Cleans and formats raw meeting text.
- **Meeting Summarization**: Generates a concise, professional summary of the discussion.
- **Task Extraction**: Uses structured output parsing to identify action items, assignees, and deadlines.
- **Follow-up Generation**: Drafts a ready-to-send email based on the summary and extracted tasks.
- **Interactive Dashboard**: A user-friendly Streamlit interface for uploading transcripts and reviewing outputs.

## Architecture

The project consists of the following components:
- `main.py`: Contains the `HermesAgent` orchestrator that runs the end-to-end pipeline.
- `dashboard.py`: The Streamlit frontend for user interaction.
- `transcript_processor.py`: Cleans and prepares raw transcripts.
- `summarizer.py`: Prompts the LLM to generate meeting summaries.
- `task_extractor.py`: Identifies and structured JSON action items from the text.
- `followup_generator.py`: Drafts a follow-up email.
- `config.py`: Manages environment variables and API configurations.

## Prerequisites

- Python 3.8+
- A valid [Groq API Key](https://console.groq.com/keys)

## Installation

1. **Clone the repository or navigate to the project directory:**
   ```bash
   cd smart_meeting_agent
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Environment:**
   Copy the example environment file and add your Groq API key:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set your key:
   ```env
   OPENAI_API_KEY=gsk_your_groq_api_key_here
   ```
   *Note: Hermes uses the official `openai` python library configured to point to Groq's API endpoint.*

## Usage

You can run the application via the Streamlit dashboard:

```bash
streamlit run dashboard.py
```

### Using the Dashboard

1. Open the local URL provided by Streamlit (usually `http://localhost:8501`).
2. If your API key isn't set in the `.env` file, you can enter it directly via the **Settings** section in the sidebar.
3. Paste a meeting transcript into the text area or upload a `.txt` file.
4. Click **🚀 Run Hermes Agent Workflow**.
5. View the resulting Summary, Action Items, and Follow-up Email Draft in the respective tabs.

## Troubleshooting

- **API Key Errors**: Ensure you have entered a valid Groq API key in the `.env` file or in the Streamlit sidebar. 
- **JSON Parsing Errors**: The task extractor is designed to handle conversational filler around JSON responses, but if the LLM output deviates significantly, tasks might default to an "Unassigned" fallback. 
