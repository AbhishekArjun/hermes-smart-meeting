import streamlit as st
from main import HermesAgent
from config import Config
import os
import json

st.set_page_config(page_title="Hermes Smart Meeting Assistant", page_icon="🤖", layout="wide")

def initialize_agent():
    # Check if API key is set
    try:
        Config.validate()
        return HermesAgent()
    except ValueError:
        st.warning("⚠️ OpenAI API Key is missing. Please add it to your .env file or input it below.")
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            Config.OPENAI_API_KEY = api_key
            st.success("API Key set for this session!")
            st.rerun()
        return None

# UI Header
st.title("🤖 Hermes Smart Meeting Assistant")
st.markdown("""
Upload a meeting transcript or paste the text below. 
Hermes will automatically analyze the discussion, extract action items, and draft a follow-up email.
""")

agent = initialize_agent()

# Sidebar for options
with st.sidebar:
    st.header("Settings")
    current_key = Config.OPENAI_API_KEY if Config.OPENAI_API_KEY else ""
    api_key_input = st.text_input("API Key (Override)", type="password", value=current_key, key="sidebar_api_key")
    if api_key_input and api_key_input != Config.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = api_key_input
        Config.OPENAI_API_KEY = api_key_input
        st.success("API Key updated for this session!")
        st.rerun()
        
    st.markdown("---")
    st.header("Upload Transcript")
    uploaded_file = st.file_uploader("Choose a .txt file", type=["txt"])
    
    st.markdown("---")
    st.markdown("### Hermes Workflow Capabilities")
    st.markdown("- 📝 **Summarization**")
    st.markdown("- ✅ **Task Extraction**")
    st.markdown("- 📧 **Follow-up Generation**")
    st.markdown("- ⚙️ **Multi-step Orchestration**")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Meeting Transcript")
    raw_text = ""
    
    if uploaded_file is not None:
        raw_text = uploaded_file.getvalue().decode("utf-8")
        st.text_area("Uploaded Content:", value=raw_text, height=300, disabled=True)
    else:
        raw_text = st.text_area("Paste meeting transcript here:", height=300, placeholder="Alice: Let's discuss the project...\nBob: I will handle the backend.")
        
    process_btn = st.button("🚀 Run Hermes Agent Workflow", type="primary", use_container_width=True)

with col2:
    st.subheader("Agent Output Dashboard")
    
    if process_btn:
        if not agent:
            st.error("Cannot run workflow: API Key missing.")
        elif not raw_text.strip():
            st.warning("Please provide a transcript to process.")
        else:
            with st.spinner("Hermes is processing the meeting..."):
                results = agent.run_workflow(raw_text)
                
            if results["status"] == "success":
                tab1, tab2, tab3 = st.tabs(["📝 Summary", "✅ Action Items", "📧 Follow-up Draft"])
                
                with tab1:
                    st.markdown("### Meeting Summary")
                    st.write(results["summary"])
                    
                with tab2:
                    st.markdown("### Extracted Tasks")
                    tasks = results["tasks"]
                    if not tasks:
                        st.info("No action items found.")
                    else:
                        for idx, task in enumerate(tasks):
                            with st.expander(f"Task {idx+1}: {task.get('what', 'No description')}", expanded=True):
                                st.markdown(f"**Who**: {task.get('who', 'Unassigned')}")
                                st.markdown(f"**Deadline**: {task.get('deadline', 'TBD')}")
                                
                with tab3:
                    st.markdown("### Follow-up Email Draft")
                    st.text_area("Copy and send:", value=results["followup_email"], height=300)
                    
            else:
                st.error(f"Workflow failed: {results.get('error', 'Unknown error')}")
    else:
        st.info("Upload a transcript and click 'Run Hermes Agent Workflow' to see results.")
