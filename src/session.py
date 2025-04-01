"""
Module for managing Streamlit session state.
"""

import streamlit as st
from src.utils import clean_project_files

def init_session_state():
    """
    Initialize session state variables.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "project_summary" not in st.session_state:
        st.session_state.project_summary = None
    if "search_results" not in st.session_state:
        st.session_state.search_results = None
    if "selected_project" not in st.session_state:
        st.session_state.selected_project = None
    if "enhancement_plan" not in st.session_state:
        st.session_state.enhancement_plan = None
    if "readme_content" not in st.session_state:
        st.session_state.readme_content = ""
    if "idea_rating" not in st.session_state:
        st.session_state.idea_rating = 0
    if "idea_reflection" not in st.session_state:
        st.session_state.idea_reflection = ""
    if "awaiting_clarification" not in st.session_state:
        st.session_state.awaiting_clarification = False
    if "original_idea" not in st.session_state:
        st.session_state.original_idea = ""
    if "evaluation_state" not in st.session_state:
        st.session_state.evaluation_state = "not_started"
    if "evaluations" not in st.session_state:
        st.session_state.evaluations = []
    if "auto_search" not in st.session_state:
        st.session_state.auto_search = False
    if "processing_clarification" not in st.session_state:
        st.session_state.processing_clarification = False
    if "github_choice_shown" not in st.session_state:
        st.session_state.github_choice_shown = False
    if "use_github_as_base" not in st.session_state:
        st.session_state.use_github_as_base = True
    if "plan_options" not in st.session_state:
        st.session_state.plan_options = []
    if "selected_plan_option" not in st.session_state:
        st.session_state.selected_plan_option = None
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = "not_started"
    if "awaiting_project_selection" not in st.session_state:
        st.session_state.awaiting_project_selection = False

def reset_session_state():
    """
    Reset all session state variables to defaults when starting a new project.
    """
    # Reset all state variables to their initial values
    st.session_state.messages = []
    st.session_state.project_summary = None
    st.session_state.search_results = None
    st.session_state.selected_project = None
    st.session_state.enhancement_plan = None
    st.session_state.readme_content = ""
    st.session_state.idea_rating = 0
    st.session_state.idea_reflection = ""
    st.session_state.awaiting_clarification = False
    st.session_state.original_idea = ""
    st.session_state.evaluation_state = "not_started"
    st.session_state.evaluations = []
    st.session_state.auto_search = False
    st.session_state.processing_clarification = False
    st.session_state.github_choice_shown = False
    st.session_state.use_github_as_base = True
    st.session_state.plan_options = []
    st.session_state.selected_plan_option = None
    st.session_state.current_stage = "not_started"
    st.session_state.awaiting_project_selection = False
    
    # Clean up any files created
    clean_project_files() 