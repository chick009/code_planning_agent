"""
Project Implementation Planner - A Streamlit app for planning projects using AI and GitHub.
"""

import streamlit as st
import os
from dotenv import load_dotenv

from src.session import init_session_state, reset_session_state
from src.handlers import (
    add_message,
    handle_initial_message,
    handle_clarification,
    handle_github_search,
    handle_project_selection,
    evaluate_and_plan_projects,
    skip_clarification
)

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Project Implementation Planner",
    page_icon="��",
    layout="wide",
    initial_sidebar_state="expanded"  # Ensure sidebar is always expanded
)

def main():
    """
    Main application entry point.
    """
    # Initialize session state
    init_session_state()
    
    # Sidebar - Always visible
    with st.sidebar:
        st.header("🚀 Project Implementation Planner")
        st.markdown("Transform your project idea into a step-by-step implementation plan using AI and GitHub")
        st.markdown("---")
        
        # About section
        st.header("About")
        st.markdown("This tool helps you plan your project implementation using AI and GitHub reference projects.")
        st.markdown("It analyzes your idea, finds similar projects, and creates detailed step-by-step guides.")
        
        # Start New Project button - Always visible
        st.markdown("---")
        if st.button("🔄 Start New Project", type="primary", use_container_width=True):
            # Reset the state when explicitly starting a new project
            reset_session_state()
            st.rerun()
    
    # Main content area
    st.title("🚀 Project Implementation Planner")
    st.markdown("Transform your project idea into a step-by-step implementation plan using AI and GitHub")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Check if we need to auto-search (after the first prompt has been processed)
    if len(st.session_state.messages) > 1 and st.session_state.get("auto_search", False):
        st.session_state.auto_search = False  # Reset the flag
        handle_github_search()
        return  # Return early to avoid chat input
    
    # Check if we need to show the GitHub usage choice buttons
    if (st.session_state.search_results and 
        isinstance(st.session_state.search_results, list) and 
        st.session_state.evaluation_state == "github_usage_choice"):
        
        # Add a visual separator
        st.markdown("---")
        
        # Create a container for the buttons with some styling
        button_container = st.container()
        with button_container:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("### Use GitHub as a starting point")
                st.markdown("Clone the repository and build upon it")
                
                # Button to use GitHub as starting point
                if st.button("🔄 Start with GitHub Project", 
                           key="use_github_button", 
                           type="primary", 
                           use_container_width=True):
                    print("Using GitHub project as starting point")
                    st.session_state.use_github_as_base = True
                    st.session_state.evaluation_state = "plan_options"
                    st.rerun()  # Trigger evaluation
            
            with col2:
                st.markdown("### Use GitHub as reference only")
                st.markdown("Build from scratch with inspiration")
                
                # Button to use GitHub as reference only
                if st.button("🆕 Start Fresh with References", 
                           key="reference_only_button", 
                           type="primary", 
                           use_container_width=True):
                    print("Using GitHub projects as reference only")
                    st.session_state.use_github_as_base = False
                    st.session_state.evaluation_state = "plan_options"
                    st.rerun()  # Trigger evaluation
        
        # Add another visual separator
        st.markdown("---")
        
        # Return early to avoid chat input while showing buttons
        return
    
    # Check if we're in the middle of project evaluation and planning
    if (st.session_state.search_results and 
        "evaluation_state" in st.session_state and 
        st.session_state.evaluation_state in ["planning", "start", "plan_options"]):
        evaluate_and_plan_projects()
        return  # Return early to avoid chat input
    
    # Show GitHub search button if appropriate and not processing clarification
    if (len(st.session_state.messages) >= 2 and
        st.session_state.project_summary and
        st.session_state.evaluation_state != "completed" and
        (not st.session_state.search_results or st.session_state.awaiting_clarification) and # Haven't searched OR awaiting clarification
        not st.session_state.get("processing_clarification", False)):
        
        # Debug print to understand button visibility conditions
        print(f"Button visibility check passed. Conditions: messages={len(st.session_state.messages)>=2}, summary={bool(st.session_state.project_summary)}, eval_state!='completed'={st.session_state.evaluation_state!='completed'}, search_results={not st.session_state.search_results}, awaiting_clarification={st.session_state.awaiting_clarification}, not_processing={not st.session_state.get('processing_clarification', False)}")
        
        # Add a visual separator
        st.markdown("---")
        
        # Create a container for the button with some styling
        button_container = st.container()
        with button_container:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("### Ready to find GitHub projects?")
                
                # Create large, clearly visible button
                if st.button("🔍 Search GitHub Projects Now", 
                           key="search_github_button", 
                           type="primary", 
                           use_container_width=True):
                    print("GitHub search button clicked")
                    st.session_state.awaiting_clarification = False
                    # Show assistant logo during search
                    with st.chat_message("assistant"):
                        with st.spinner("Searching GitHub for relevant projects..."):
                            success = skip_clarification(st.session_state.project_summary)
                            if success:
                                st.rerun()
                            else:
                                st.error("Failed to search GitHub. Please try again.")
        
        # Add another visual separator
        st.markdown("---")
    
    # Chat input
    if prompt := st.chat_input("What kind of project would you like to build?"):
        # Add user message to chat history
        add_message("user", prompt)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the message based on conversation state
        if not st.session_state.project_summary and not st.session_state.awaiting_clarification:
            # First message - evaluate idea clarity
            handle_initial_message(prompt)
        
        elif st.session_state.awaiting_clarification:
            # Process clarification
            handle_clarification(prompt)
        
        elif not st.session_state.search_results:
            # Second message - search GitHub
            handle_github_search()
        
        elif not st.session_state.selected_project:
            # Third message - evaluate projects (this step is now automatic)
            handle_project_selection()
        
        elif not st.session_state.enhancement_plan:
            # Fourth message - create implementation plan
            evaluate_and_plan_projects()

if __name__ == "__main__":
    main() 