"""
Handlers for Streamlit events and user interactions.
"""

import streamlit as st
import os
from datetime import datetime

from src.api import (
    evaluate_idea_clarity,
    process_project_summary,
    search_github_projects,
    extract_github_content,
    evaluate_repository,
    select_best_project,
    create_enhancement_plan,
    create_simplified_plan,
    generate_implementation_document
)
from src.utils import get_download_link, generate_step_files

def add_message(role, content):
    """
    Add a message to the chat history.
    
    Args:
        role (str): The role of the sender (user or assistant)
        content (str): The message content
    """
    st.session_state.messages.append({
        "role": role, 
        "content": content, 
        "timestamp": datetime.now()
    })

def handle_initial_message(prompt):
    """
    Handle the initial user message when no project summary exists.
    
    Args:
        prompt (str): The user's initial project idea
    """
    # Store original idea
    st.session_state.original_idea = prompt
    
    # First message - evaluate idea clarity
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your project idea..."):
            # Evaluate idea clarity
            rating, reflection = evaluate_idea_clarity(prompt)
            st.session_state.idea_rating = rating
            st.session_state.idea_reflection = reflection
            
            # Process with reasoning model regardless of rating
            initial_summary = process_project_summary(prompt)
            
            # Always set project summary regardless of rating
            st.session_state.project_summary = initial_summary
            
            if rating < 8:
                # Explicitly set awaiting_clarification state
                st.session_state.awaiting_clarification = True
                
                # Format response with current understanding + what's missing
                response = f"I've evaluated your project idea (clarity rating: {rating}/10).\n\n"
                response += f"Here's what I understand so far:\n{initial_summary.get('project_purpose', '')}\n\n"
                response += f"{reflection}\n\n"
                response += "Please provide more details, or click the 'Search GitHub Projects Now' button below to continue."
            else:
                # Explicitly set awaiting_clarification to False
                st.session_state.awaiting_clarification = False
                
                # Format and display the response - indicate we'll proceed to GitHub search automatically
                response = f"I've evaluated your project idea (clarity rating: {rating}/10).\n\n"
                response += f"{initial_summary.get('project_purpose', '')}\n\n"
                response += "I'll search for relevant GitHub projects that match your requirements."
                
                # Set up for auto-transition to search
                st.session_state.auto_search = True
            
            # Add the message and display it
            add_message("assistant", response)
            st.markdown(response)
            
    # Force UI refresh to immediately show the search button
    st.rerun()

def handle_clarification(prompt):
    """
    Handle user clarification messages.
    
    Args:
        prompt (str): The user's clarification message
    """
    with st.chat_message("assistant"):
        with st.spinner("Processing your clarification..."):
            # Combine original idea with clarification
            combined_idea = f"{st.session_state.original_idea} {prompt}"
            st.session_state.original_idea = combined_idea  # Update the original idea with combined input
            
            # Re-evaluate clarity
            rating, reflection = evaluate_idea_clarity(combined_idea)
            st.session_state.idea_rating = rating
            
            # Process with reasoning model
            updated_summary = process_project_summary(combined_idea)
            
            # Check if we've reached sufficient clarity
            if rating >= 8:
                # Idea is now clear enough, proceed
                st.session_state.awaiting_clarification = False
                st.session_state.project_summary = updated_summary
                
                # Format and display the response - indicate we'll proceed to GitHub search automatically
                response = f"Thanks for the clarification! Your project idea now has a clarity rating of {rating}/10, which is sufficient.\n\n"
                response += f"Updated project summary:\n{updated_summary.get('project_purpose', '')}\n\n"
                response += "I'll search for relevant GitHub projects that match your requirements."
                
                # Set up for auto-transition to search
                st.session_state.auto_search = True
            else:
                # Still need more clarification
                st.session_state.project_summary = updated_summary  # Update project summary even if not clear enough
                
                response = f"Thanks for the clarification! Your project idea now has a clarity rating of {rating}/10, but I still need more details.\n\n"
                response += f"Current understanding:\n{updated_summary.get('project_purpose', '')}\n\n"
                response += f"{reflection}\n\n"
                response += "Please provide more information, or click the 'Search GitHub Projects Now' button below to continue."
            
            st.markdown(response)
            add_message("assistant", response)

def handle_github_search():
    """
    Search for GitHub projects based on project summary.
    """
    # Show assistant logo during search
    with st.chat_message("assistant"):
        with st.spinner("Searching GitHub projects..."):
            # Use the original idea as the primary search query
            search_query = st.session_state.original_idea
            
            # Add any structured data that might be helpful
            summary = st.session_state.project_summary
            if summary and isinstance(summary, dict):
                project_purpose = summary.get('project_purpose', '')
                platform = summary.get('platform', '')
                tech_stack = summary.get('tech_stack', '')
                
                # Only add these details if they're not empty and would keep query reasonably sized
                if project_purpose and project_purpose != st.session_state.original_idea:
                    if len(search_query) + len(project_purpose) < 400:
                        search_query += f" {project_purpose}"
                if platform and len(search_query) + len(platform) < 450:
                    search_query += f" for {platform}"
                if tech_stack and len(search_query) + len(tech_stack) < 500:
                    # Just take the first few terms of tech stack to keep query reasonable
                    tech_terms = tech_stack.split(',')[:3]  # Take at most 3 terms
                    search_query += f" using {', '.join(tech_terms)}"
            
            # Use this query for the search
            results = search_github_projects(search_query)
            st.session_state.search_results = results
            
            if isinstance(results, dict) and "error" in results:
                response = f"**Search Error**: {results['error']}\n\n"
                response += "Please try again with a more specific or simpler description."
                
                # Show error but keep the conversation going
                st.error(results["error"])
            else:
                response = f"I found {len(results)} relevant GitHub projects. I'll now evaluate them to find the best match for your requirements:\n\n"
                for i, project in enumerate(results):
                    response += f"{i+1}. **{project['title']}**\n"
                    response += f"   URL: {project['url']}\n"
                    response += f"   Description: {project['description']}\n\n"
            
            st.markdown(response)
            add_message("assistant", response)
            
            # Automatically transition to evaluation if we found valid projects
            if isinstance(results, list) and results:
                st.session_state.evaluation_state = "start"
                st.rerun()  # Trigger evaluation

def handle_project_selection():
    """
    Handle the project selection stage
    """
    if not st.session_state.search_results:
        st.error("No projects found to evaluate. Please try searching again.")
        return

    # Set state to proceed to evaluation
    st.session_state.current_stage = "project_evaluation"
    st.session_state.awaiting_project_selection = False
    st.session_state.evaluation_state = "start"
    
    # Trigger evaluation process directly
    evaluate_and_plan_projects()

def evaluate_and_plan_projects():
    """
    Evaluate projects and create an implementation plan.
    """
    # First check if we have valid projects to evaluate
    if not st.session_state.search_results or isinstance(st.session_state.search_results, dict):
        with st.chat_message("assistant"):
            error_msg = "No valid GitHub projects to evaluate. Please try searching again."
            st.error(error_msg)
            add_message("assistant", error_msg)
        return
    
    try:
        # Set a flag to track our progress
        if "evaluation_state" not in st.session_state:
            st.session_state.evaluation_state = "start"
        
        # Evaluate repositories in the first step
        if st.session_state.evaluation_state == "start":
            # Show assistant logo with spinner while evaluating
            with st.chat_message("assistant"):
                with st.spinner("Analyzing GitHub repositories in depth..."):
                    # Process each project
                    evaluations = []
                    for project in st.session_state.search_results:
                        # Extract content
                        repo_data = extract_github_content(project["url"])
                        
                        # Add basic project info
                        repo_data["title"] = project.get("title", "Unknown Title")
                        repo_data["description"] = project.get("description", "No description available")
                        repo_data["url"] = project.get("url", "")
                        
                        # Evaluate the repository
                        evaluation = evaluate_repository(repo_data, st.session_state.project_summary)
                        evaluations.append(evaluation)
                    
                    # Select the best project
                    best_project = select_best_project(evaluations, st.session_state.project_summary)
                    
                    # Sort by score (highest first)
                    evaluations.sort(key=lambda x: x.get("suitability_score", 0), reverse=True)
                    
                    # Mark the best project and add reasons
                    for eval in evaluations:
                        if eval.get("project", {}).get("url") == best_project.get("url"):
                            eval["is_best_match"] = True
                            eval["best_match_reason"] = best_project.get("reason", "")
                            # Add a clear indicator in the project title
                            eval["project"]["title"] = f"✅ BEST MATCH: {eval['project']['title']}"
                        else:
                            eval["is_best_match"] = False
            
            # Store evaluations in session state
            st.session_state.evaluations = evaluations
            
            # Build the evaluation response
            response = "Based on my analysis of these GitHub repositories, here's what I found:\n\n"
            
            for i, eval in enumerate(evaluations):
                project = eval["project"]
                metadata = eval.get("metadata", {})
                
                # Mark best match
                best_match_indicator = "🏆 **BEST MATCH** 🏆 " if eval.get("is_best_match", False) else ""
                
                response += f"### {best_match_indicator}Project {i+1}: {project['title']}\n"
                response += f"**URL**: {project['url']}\n"
                
                # Show GitHub stats if available
                stars = metadata.get("stars", "N/A")
                forks = metadata.get("forks", "N/A")
                languages = ", ".join(metadata.get("languages", [])[:5])
                
                if stars != "N/A" or languages:
                    response += "**Repository Stats**: "
                    if stars != "N/A":
                        response += f"⭐ {stars} stars | 🍴 {forks} forks"
                    if languages:
                        response += f" | 💻 Languages: {languages}"
                    response += "\n"
                
                # Show match assessment
                score = eval.get("suitability_score", 0)
                response += f"**Match Score**: {'🟢' * int(score/2)}{'⚪' * (5-int(score/2))} ({score}/10)\n"
                
                # Show tech & feature matches
                tech_match = eval.get("tech_match", [])
                if tech_match:
                    response += f"**Matching Technologies**: {', '.join(tech_match)}\n"
                
                feature_match = eval.get("feature_match", [])
                if feature_match:
                    response += f"**Matching Features**: {', '.join(feature_match)}\n"
                
                # Show modification effort
                modification = eval.get("modification_effort", "")
                if modification:
                    response += f"**Modification Effort**: {modification}\n"
                
                # Show summary
                if "summary" in eval and eval["summary"]:
                    response += f"\n**Assessment**: {eval['summary']}\n"
                
                # Show best match reason
                if eval.get("is_best_match", False) and eval.get("best_match_reason"):
                    response += f"\n**Why this is the best match**: {eval['best_match_reason']}\n"
                
                # Show pros and cons
                response += "\n**Pros**:\n"
                for pro in eval["pros"]:
                    response += f"- {pro}\n"
                
                response += "\n**Cons**:\n"
                for con in eval["cons"]:
                    response += f"- {con}\n"
                
                response += "\n---\n\n"
            
            # Select the best project
            best_project = next(
                (eval["project"] for eval in evaluations if eval.get("is_best_match", False)), 
                evaluations[0]["project"]
            )
            
            # Store the selected project
            st.session_state.current_stage = "enhancement_planning"
            st.session_state.selected_project = best_project
            
            # Add transition message
            transition_message = "\n\nI'll now create a detailed implementation plan based on this project."
            response += transition_message
            
            # Display the evaluation in a chat message
            with st.chat_message("assistant"):
                st.markdown(response)
                add_message("assistant", response)
            
            # Update state to trigger the implementation plan on next run
            st.session_state.evaluation_state = "planning"
            st.rerun()
        
        # Create implementation plan in the second step
        elif st.session_state.evaluation_state == "planning":
            # Reset the evaluation state
            st.session_state.evaluation_state = "done"
            
            # Create the implementation plan
            create_implementation_plan()
        
    except Exception as e:
        error_msg = f"Error evaluating projects: {str(e)}"
        print(error_msg)
        
        with st.chat_message("assistant"):
            st.error(error_msg)
            add_message("assistant", f"I encountered an error while evaluating the projects: {str(e)}")

def skip_clarification(summary_data):
    """
    Skip clarification and search GitHub directly.
    
    Args:
        summary_data (dict): Project summary data
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("Skip clarification function started")
        
        # Update state flags first
        st.session_state.awaiting_clarification = False
        st.session_state.evaluation_state = "not_started"  # Reset evaluation state
        
        # Use original idea when summary is invalid
        if not summary_data or not isinstance(summary_data, dict):
            print("Using original idea as fallback")
            search_query = st.session_state.original_idea
        else:
            # Just use the original idea with the project summary as context
            search_query = st.session_state.original_idea
            
            # If we have structured data, add it to enhance the search
            project_purpose = summary_data.get('project_purpose', '')
            platform = summary_data.get('platform', '')
            tech_stack = summary_data.get('tech_stack', '')
            
            # Only add these details if they're not empty and would keep query reasonably sized
            if project_purpose and project_purpose != st.session_state.original_idea:
                if len(search_query) + len(project_purpose) < 400:
                    search_query += f" {project_purpose}"
            if platform and len(search_query) + len(platform) < 450:
                search_query += f" for {platform}"
            if tech_stack and len(search_query) + len(tech_stack) < 500:
                # Just take the first few terms of tech stack to keep query reasonable
                tech_terms = tech_stack.split(',')[:3]  # Take at most 3 terms
                search_query += f" using {', '.join(tech_terms)}"
        
        print(f"Search query: {search_query}")
        
        # Perform the search
        results = search_github_projects(search_query)
        
        # Update session state
        st.session_state.search_results = results
        
        # Create response message
        if isinstance(results, dict) and "error" in results:
            search_response = f"**Error during search**: {results['error']}\n\n"
            search_response += "Please try providing a more specific or simpler project description."
            
            # We want the user to know there was an error, but we'll allow them to continue
            # by adding a message to try alternative searches
            st.error(results["error"])
        else:
            search_response = f"I found {len(results)} relevant GitHub projects:\n\n"
            for i, project in enumerate(results):
                search_response += f"**Project {i+1}: {project['title']}**\n"
                search_response += f"URL: {project['url']}\n"
                search_response += f"Description: {project['description']}\n\n"
            search_response += "Would you like me to evaluate these projects and suggest enhancements?"
        
        # Add message to chat history
        add_message("assistant", search_response)
        
        print("Skip clarification function completed successfully")
        return True
        
    except Exception as e:
        print(f"Error in skip_clarification: {str(e)}")
        st.error(f"An error occurred during search: {str(e)}")
        return False

def create_implementation_plan():
    """
    Create a detailed implementation plan with step-by-step instructions.
    """
    try:
        # Verify we have a selected project
        if not st.session_state.selected_project:
            with st.chat_message("assistant"):
                error_msg = "No project selected to create implementation plan. Please try again."
                st.error(error_msg)
                add_message("assistant", error_msg)
            return
        
        # Create detailed enhancement plan with implementation steps using LLM
        with st.spinner("Creating detailed implementation plan..."):
            try:
                # Try to create the detailed plan with the LLM
                enhancement_plan = create_enhancement_plan(
                    st.session_state.selected_project, 
                    st.session_state.project_summary
                )
                
                # Check if the plan is valid and contains implementation steps
                if (not isinstance(enhancement_plan, dict) or 
                    "enhancement_description" not in enhancement_plan or
                    not enhancement_plan.get("implementation_steps")):
                    
                    print("First attempt failed, trying again with a simplified prompt")
                    # Try again with a simplified approach
                    enhancement_plan = create_simplified_plan(
                        st.session_state.selected_project,
                        st.session_state.project_summary
                    )
            except Exception as e:
                print(f"Error creating enhancement plan: {str(e)}")
                # Try the simplified approach as a fallback
                enhancement_plan = create_simplified_plan(
                    st.session_state.selected_project,
                    st.session_state.project_summary
                )
            
            # Save the plan to session state
            st.session_state.enhancement_plan = enhancement_plan
            
            # Generate a comprehensive implementation plan as a single text file
            try:
                structured_plan = generate_implementation_document(
                    st.session_state.project_summary,
                    st.session_state.selected_project,
                    enhancement_plan
                )
            except Exception as e:
                print(f"Error generating full implementation plan: {str(e)}")
                # Generate a simple fallback plan if the document generation fails
                from src.utils import create_fallback_implementation_doc
                structured_plan = create_fallback_implementation_doc(
                    st.session_state.project_summary,
                    st.session_state.selected_project,
                    enhancement_plan
                )
            
            # Create output directory if it doesn't exist
            output_dir = "implementation_steps"
            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except Exception as e:
                    print(f"Error creating directory: {str(e)}")
            
            # Write the full plan to a file
            main_plan_filename = "implementation_plan.txt"
            try:
                with open(main_plan_filename, "w") as f:
                    f.write(structured_plan)
                print(f"Wrote main implementation plan to {main_plan_filename}")
            except Exception as e:
                print(f"Error writing main plan file: {str(e)}")
                main_plan_filename = None
            
            # Split the implementation plan into separate step files
            try:
                step_files = generate_step_files(structured_plan)
            except Exception as e:
                print(f"Error generating step files: {str(e)}")
                step_files = []
            
            # Build response message
            response = "I've created a detailed implementation plan for your project:\n\n"
            
            # Include plan overview
            response += "## Plan Overview\n"
            response += f"Based on the **{st.session_state.selected_project.get('title')}** project, I've created a plan to implement your requirements.\n\n"
            
            # Include enhancement description
            response += "## Enhancement Strategy\n"
            response += enhancement_plan.get("enhancement_description", "No enhancement description available.") + "\n\n"
            
            # Include implementation steps summary
            response += "## Implementation Steps\n"
            if enhancement_plan.get("implementation_steps"):
                for i, step in enumerate(enhancement_plan.get("implementation_steps", [])):
                    step_number = i + 1
                    title = step.get('title', f'Step {step_number}')
                    desc = step.get('description', 'No description')
                    desc_summary = desc[:100] + "..." if len(desc) > 100 else desc
                    response += f"{step_number}. **{title}** - {desc_summary}\n"
            
            # Include download links for files
            response += "\n## Implementation Files\n"
            if main_plan_filename or step_files:
                response += "I've created the following files to guide your implementation:\n\n"
                
                # Add link for main plan
                if main_plan_filename:
                    response += f"1. [Complete Implementation Plan]({main_plan_filename}) - The full detailed implementation plan\n"
                
                # Add links for step files
                for i, filename in enumerate(step_files):
                    # Extract step title from filename
                    step_name = os.path.basename(filename)
                    step_title = step_name.replace('.txt', '').replace('step_', '').replace('_', ' ').title()
                    response += f"{i+2 if main_plan_filename else i+1}. [{step_name}]({filename}) - {step_title}\n"
            else:
                response += "Unfortunately, I couldn't generate the implementation files. Please try again or modify your project requirements.\n"
            
            # Display the response in a new chat message
            with st.chat_message("assistant"):
                st.markdown(response)
                add_message("assistant", response)
            
            # Add a message about starting a new project
            with st.chat_message("assistant"):
                new_project_msg = "Would you like to start a new project? Click the 'Start New Project' button in the sidebar to begin."
                st.markdown(new_project_msg)
                add_message("assistant", new_project_msg)
            
            # Update state to indicate completion without resetting
            st.session_state.evaluation_state = "completed"
        
    except Exception as e:
        error_msg = f"Error creating implementation plan: {str(e)}"
        print(error_msg)
        
        with st.chat_message("assistant"):
            st.error(error_msg)
            
            response = "I encountered an error while creating the implementation plan. Here's what happened:\n\n"
            response += f"**Error**: {str(e)}\n\n"
            response += "Please try again with a different project or simplify your requirements."
            
            st.markdown(response)
            add_message("assistant", response) 