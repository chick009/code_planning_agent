"""
Utility functions for the code planning agent.
"""

import os
import re
import base64
from datetime import datetime
import shutil

def get_download_link(content, filename="README.md"):
    """
    Generate a download link for text content.
    
    Args:
        content (str): The content to make downloadable
        filename (str): The filename for the download
        
    Returns:
        str: HTML link for downloading the content
    """
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/markdown;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def generate_step_files(implementation_plan, output_dir="implementation_steps"):
    """
    Generate individual text files for each implementation step from a single plan.
    
    Args:
        implementation_plan (str): The full implementation plan text
        output_dir (str): Directory to save step files
        
    Returns:
        list: List of generated filenames
    """
    try:
        # Create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")
        
        # Check if we have a full implementation plan text
        if not implementation_plan or not isinstance(implementation_plan, str):
            print("No valid implementation plan provided")
            return []
        
        # Parse the implementation plan to extract steps
        steps = []
        
        # Try to find step sections using regex
        step_sections = re.findall(r'(## Step \d+: .*?)(?=## Step \d+:|$)', implementation_plan, re.DOTALL)
        
        if step_sections:
            # We found structured sections, use them directly
            for i, section in enumerate(step_sections):
                section = section.strip()
                step_number = i + 1
                
                # Extract title from the section header
                title_match = re.search(r'## Step \d+: (.*?)(?:\n|$)', section)
                title = title_match.group(1).strip() if title_match else f"Step {step_number}"
                
                # Create a safe filename
                safe_title = "".join([c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in title.lower()])
                safe_title = safe_title.replace(' ', '_')
                
                # Write to file
                step_filename = f"{output_dir}/step_{step_number:02d}_{safe_title}.txt"
                with open(step_filename, "w") as f:
                    f.write(section)
                
                print(f"Created step file: {step_filename}")
                steps.append(step_filename)
        else:
            # No clear sections found, create steps by splitting content
            # Split by "Implementation Steps" section or similar
            plan_parts = implementation_plan.split("## Implementation Steps")
            if len(plan_parts) > 1:
                steps_content = plan_parts[1]
                
                # Try to find numbered items
                step_items = re.findall(r'(\d+\.\s.*?)(?=\d+\.\s|$)', steps_content, re.DOTALL)
                
                if step_items:
                    for i, item in enumerate(step_items):
                        step_number = i + 1
                        
                        # Extract title
                        title_match = re.search(r'\d+\.\s(.*?)(?:\n|$)', item)
                        title = title_match.group(1).strip() if title_match else f"Step {step_number}"
                        
                        # Create content with header
                        content = f"# Step {step_number}: {title}\n\n{item.strip()}"
                        
                        # Create a safe filename
                        safe_title = "".join([c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in title.lower()])
                        safe_title = safe_title.replace(' ', '_')
                        
                        # Write to file
                        step_filename = f"{output_dir}/step_{step_number:02d}_{safe_title}.txt"
                        with open(step_filename, "w") as f:
                            f.write(content)
                        
                        print(f"Created step file: {step_filename}")
                        steps.append(step_filename)
                else:
                    # If we can't find clear numbered items, create generic steps
                    steps_content = steps_content.strip()
                    paragraphs = re.split(r'\n\n+', steps_content)
                    
                    # Create up to 5 logical steps
                    num_steps = min(5, len(paragraphs))
                    chunk_size = max(1, len(paragraphs) // num_steps)
                    
                    for i in range(num_steps):
                        start_idx = i * chunk_size
                        end_idx = min(start_idx + chunk_size, len(paragraphs))
                        
                        step_number = i + 1
                        title = f"Implementation Phase {step_number}"
                        
                        # Join paragraphs for this step
                        content = f"# {title}\n\n" + "\n\n".join(paragraphs[start_idx:end_idx])
                        
                        # Write to file
                        step_filename = f"{output_dir}/step_{step_number:02d}_implementation_phase_{step_number}.txt"
                        with open(step_filename, "w") as f:
                            f.write(content)
                        
                        print(f"Created step file: {step_filename}")
                        steps.append(step_filename)
        
        return steps
    except Exception as e:
        print(f"Error generating step files: {str(e)}")
        return []

def timestamp():
    """
    Get current timestamp for logging.
    
    Returns:
        str: Current timestamp as string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def clean_project_files():
    """
    Clean up project files when starting a new project.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Remove implementation plan if it exists
        if os.path.exists("implementation_plan.txt"):
            try:
                os.remove("implementation_plan.txt")
            except Exception as e:
                print(f"Error removing implementation_plan.txt: {str(e)}")
                
        # Remove implementation steps directory if it exists
        if os.path.exists("implementation_steps"):
            try:
                shutil.rmtree("implementation_steps")
            except Exception as e:
                print(f"Error removing implementation_steps directory: {str(e)}")
                
        return True
    except Exception as e:
        print(f"Error cleaning project files: {str(e)}")
        return False

def create_fallback_implementation_doc(project_summary, selected_project, enhancement_plan):
    """
    Create a fallback implementation document when LLM generation fails.
    
    Args:
        project_summary (dict): Project requirements
        selected_project (dict): The selected GitHub project
        enhancement_plan (dict): The enhancement plan
        
    Returns:
        str: A simple implementation plan document
    """
    # Format the implementation steps if available
    implementation_steps_text = ""
    
    if enhancement_plan and enhancement_plan.get("implementation_steps"):
        for i, step in enumerate(enhancement_plan["implementation_steps"]):
            step_number = i + 1
            title = step.get('title', f'Step {step_number}')
            description = step.get('description', 'No description provided')
            tasks = step.get('tasks', 'No tasks specified')
            expected_outcome = step.get('expected_outcome', 'No expected outcome specified')
            resources = step.get('resources', 'No resources specified')
            
            implementation_steps_text += f"## Step {step_number}: {title}\n\n"
            implementation_steps_text += f"### Description\n{description}\n\n"
            implementation_steps_text += f"### Tasks\n{tasks}\n\n"
            implementation_steps_text += f"### Expected Outcome\n{expected_outcome}\n\n"
            implementation_steps_text += f"### Resources\n{resources}\n\n"
    else:
        # Provide a minimal structure when no steps are available
        implementation_steps_text = """## Step 1: Project Setup
### Description
Set up the development environment and clone the repository.

### Tasks
- Clone the repository
- Install dependencies
- Configure development environment

## Step 2: Implementation
### Description
Implement the required features.

### Tasks
- Analyze requirements
- Implement core features
- Test implementation

## Step 3: Deployment
### Description
Deploy and finalize the project.

### Tasks
- Prepare for deployment
- Deploy application
- Document the implementation
"""
    
    # Format the full implementation plan
    plan = f"""# Implementation Plan for {project_summary.get('project_purpose', 'Mini-Project')}

## 1. Project Overview
- Purpose: {project_summary.get('project_purpose', 'Not specified')}
- Platform: {project_summary.get('platform', 'Not specified')}
- Tech Stack: {project_summary.get('tech_stack', 'Not specified')}
- Key Features: {project_summary.get('key_features', 'Not specified')}

## 2. Base Project
- Title: {selected_project.get('title', 'Not specified')}
- URL: {selected_project.get('url', 'Not specified')}
- Description: {selected_project.get('description', 'Not specified')}

## 3. Enhancement Strategy
{enhancement_plan.get('enhancement_description', 'Adapt the project to meet your requirements.')}

## 4. Implementation Steps
{implementation_steps_text}

## 5. Next Steps After Implementation
1. Test the application thoroughly
2. Document any changes from the original plan
3. Consider improvements for future iterations
"""
    return plan 