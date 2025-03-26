"""
API module for handling interactions with LLMs and external services.
"""

import os
import json
import requests
from openai import OpenAI
from tavily import TavilyClient

from prompts import (
    IDEA_CLARITY_PROMPT,
    PROJECT_SUMMARY_PROMPT,
    REPOSITORY_EVALUATION_PROMPT,
    BEST_PROJECT_SELECTION_PROMPT,
    ENHANCEMENT_PLAN_PROMPT,
    SIMPLIFIED_PLAN_PROMPT,
    FULL_IMPLEMENTATION_PLAN_PROMPT
)

def get_llm_client():
    """
    Creates and returns a properly configured LLM client based on available API keys.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("MODEL_API_KEY")
    
    if not api_key:
        print("Warning: No API key found for LLM access")
        return None
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        return client
    except Exception as e:
        print(f"Error initializing LLM client: {str(e)}")
        return None

def evaluate_idea_clarity(idea_text):
    """
    Evaluate the clarity of a project idea and return a rating and reflection.
    
    Args:
        idea_text (str): The project idea to evaluate
        
    Returns:
        tuple: (rating, reflection) where rating is an integer from 1-10 and 
               reflection is a string with feedback
    """
    try:
        client = get_llm_client()
        if not client:
            # Fallback to a basic rating if client is unavailable
            return 7, "Our services are currently busy. I'll proceed with your idea as is."
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": IDEA_CLARITY_PROMPT},
                {"role": "user", "content": f"Evaluate this project idea: {idea_text}"}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Extract values with defaults in case they're missing
        rating = result.get("rating", 5)
        reflection = result.get("reflection", "Could you provide more details about your project idea?")
        missing_elements = result.get("missing_elements", [])
        advice = result.get("advice", "Consider adding more specific details about your project.")
        
        # Create a more helpful reflection that includes advice
        enhanced_reflection = reflection
        if missing_elements and len(missing_elements) > 0:
            enhanced_reflection += "\n\nYour idea is missing: " + ", ".join(missing_elements) + "."
        
        if advice:
            enhanced_reflection += f"\n\n{advice}"
        
        return rating, enhanced_reflection
        
    except Exception as e:
        print(f"Evaluation error: {str(e)}")
        # Return a default rating and reflection if the API call fails
        return 5, "I couldn't fully analyze your idea. Could you provide more details about your project, such as its purpose, target platform, and key features?"

def process_project_summary(prompt):
    """
    Process a project idea and create a structured summary.
    
    Args:
        prompt (str): The project idea to process
        
    Returns:
        dict: A dictionary with project_purpose, platform, tech_stack, and key_features keys
    """
    try:
        client = get_llm_client()
        if not client:
            return {
                "error": "Our services are currently busy. Please try again later."
            }
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": PROJECT_SUMMARY_PROMPT},
                {"role": "user", "content": f"Analyze this project idea: {prompt}"}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Normalize the keys to ensure consistent key names
        normalized_result = {}
        
        # Map expected keys from model response to our standardized keys
        key_mapping = {
            "Project Purpose": "project_purpose",
            "Platform": "platform", 
            "Tech Stack": "tech_stack",
            "Key Features": "key_features"
        }
        
        # Transfer values using our mapping, with empty string fallbacks
        for old_key, new_key in key_mapping.items():
            if old_key in result:
                normalized_result[new_key] = result[old_key]
            else:
                normalized_result[new_key] = ""
                
        return normalized_result
    
    except Exception as e:
        return {
            "error": f"Processing error: {str(e)}. Please try again later."
        }

def search_github_projects(query):
    """
    Search for GitHub projects using the Tavily API.
    
    Args:
        query (str): The search query
        
    Returns:
        list: A list of GitHub projects, or a dict with an error message
    """
    try:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            return {
                "error": "Search service is currently unavailable. Please try again later."
            }
        
        client = TavilyClient(api_key=tavily_api_key)
        
        # Limit query length to prevent API errors
        max_query_length = 500
        truncated_query = query[:max_query_length] if len(query) > max_query_length else query
        
        try:
            # Add search parameters to focus on GitHub results
            response = client.search(
                query=f"{truncated_query} GitHub repository",
                search_depth="advanced",
                include_domains=["github.com"],
                max_results=5
            )
        except Exception as api_error:
            print(f"Tavily API Error: {str(api_error)}")
            # Try again with a simpler query
            simplified_query = " ".join(truncated_query.split()[:10]) + " GitHub repository"
            
            response = client.search(
                query=simplified_query,
                search_depth="basic",
                include_domains=["github.com"],
                max_results=5
            )
        
        github_projects = []
        if "results" in response:
            for result in response["results"]:
                if "github.com" in result.get("url", ""):
                    project = {
                        "title": result.get("title", "Untitled"),
                        "url": result.get("url", ""),
                        "description": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", "")
                    }
                    github_projects.append(project)
        
        # If no results found, return error
        if not github_projects:
            return {
                "error": "No relevant GitHub projects found. Try adjusting your search terms."
            }
        
        return github_projects[:5]
        
    except Exception as e:
        return {
            "error": f"Search failed: {str(e)}. Please try again with a simpler query."
        }

def extract_github_content(github_url):
    """
    Extract content from a GitHub repository using Tavily API.
    
    Args:
        github_url (str): The URL of the GitHub repository
        
    Returns:
        dict: A dictionary with repository information
    """
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not tavily_api_key:
        return {
            "raw_content": f"No content available for {github_url}",
            "extracted_content": False,
            "stars": 0,
            "forks": 0,
            "languages": [],
            "readme": "No README available",
            "files": []
        }
    
    url = "https://api.tavily.com/extract"
    
    payload = {
        "urls": github_url,
        "include_images": False,
        "extract_depth": "basic"
    }
    
    headers = {
        "Authorization": f"Bearer {tavily_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        data = response.json()
        
        if "results" not in data or not data["results"]:
            print(f"No results returned from Tavily for {github_url}")
            # Return a properly structured empty repository data object
            return {
                "raw_content": f"No content available for {github_url}",
                "extracted_content": False,
                "stars": 0,
                "forks": 0,
                "languages": [],
                "readme": "No README available",
                "files": []
            }
        
        # Extract repository details from Tavily response
        repo_content = data["results"][0]["raw_content"]
        
        # Parse basic information and return it
        import re
        
        repo_data = {
            "raw_content": repo_content,
            "extracted_content": True,
            "stars": 0,  # Default values
            "forks": 0,
            "languages": [],
            "readme": "No README detected",
            "files": []
        }
        
        # Extract stars
        stars_match = re.search(r'(\d+)\s+stars?', repo_content)
        if stars_match:
            repo_data["stars"] = int(stars_match.group(1))
            
        # Extract forks
        forks_match = re.search(r'(\d+)\s+forks?', repo_content)
        if forks_match:
            repo_data["forks"] = int(forks_match.group(1))
            
        # Extract languages
        languages = []
        languages_section = re.search(r'Languages\s*\n(.*?)\n\n', repo_content, re.DOTALL)
        if languages_section:
            lang_content = languages_section.group(1)
            lang_matches = re.findall(r'([A-Za-z\+\#]+)\s+(\d+\.?\d*)%', lang_content)
            languages = [lang for lang, percentage in lang_matches]
            repo_data["languages"] = languages
            
        # Extract README content
        readme_match = re.search(r'README\s*\n\n(.*?)(?:\n\n[A-Z]|\Z)', repo_content, re.DOTALL)
        if readme_match:
            repo_data["readme"] = readme_match.group(1).strip()
        
        # Extract file structure
        files_section = re.search(r'Folders and files\s*\n(.*?)(?:\n\nREADME|\n\nAbout|\Z)', repo_content, re.DOTALL)
        if files_section:
            file_content = files_section.group(1)
            file_names = re.findall(r'\|\s*([^\|]+\.[\w]+)\s*\|', file_content)
            repo_data["files"] = [name.strip() for name in file_names if name.strip()]
        
        return repo_data
        
    except Exception as e:
        print(f"Error extracting content: {str(e)}")
        # Return a properly structured empty repository data
        return {
            "raw_content": f"Error extracting content: {str(e)}",
            "extracted_content": False,
            "stars": 0,
            "forks": 0,
            "languages": [],
            "readme": "No README available",
            "files": []
        }

def evaluate_repository(repo_data, project_summary):
    """
    Evaluate a repository based on its content and the project requirements.
    
    Args:
        repo_data (dict): Repository data
        project_summary (dict): Project summary with requirements
        
    Returns:
        dict: Evaluation results
    """
    try:
        client = get_llm_client()
        if not client:
            return {
                "project": {
                    "url": repo_data.get("url", ""),
                    "title": repo_data.get("title", ""),
                    "description": repo_data.get("description", "")
                },
                "pros": ["Repository appeared in search results", "May align with project requirements"],
                "cons": ["Limited information available for evaluation", "Would need manual inspection"],
                "summary": "This project was found in the search results but detailed evaluation failed.",
                "suitability_score": 3,
                "metadata": {}
            }
        
        # Format the prompt with project summary details
        formatted_prompt = REPOSITORY_EVALUATION_PROMPT.format(
            project_purpose=project_summary.get('project_purpose', 'Not specified'),
            platform=project_summary.get('platform', 'Not specified'),
            tech_stack=project_summary.get('tech_stack', 'Not specified'),
            key_features=project_summary.get('key_features', 'Not specified')
        )
        
        # Prepare repository data as user message
        user_message = f"""Repository: {repo_data.get('title', 'Unknown')}
URL: {repo_data.get('url', 'Unknown')}
Description: {repo_data.get('description', 'No description')}
Stars: {repo_data.get('stars', 'Unknown')}
Forks: {repo_data.get('forks', 'Unknown')}
Languages: {', '.join(repo_data.get('languages', ['Unknown']))}

Files: {', '.join(repo_data.get('files', ['Unknown']))[:300]}

README Content:
{repo_data.get('readme', 'No README available')[:3000]}

Additional Raw Content (excerpt):
{repo_data.get('raw_content', 'No content available')[:2000]}

Based on this information, evaluate how well this repository matches our project requirements.
"""
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Create a consistent evaluation object
        evaluation = {
            "project": {
                "url": repo_data.get("url", ""),
                "title": repo_data.get("title", ""),
                "description": repo_data.get("description", "")
            },
            "pros": result.get("pros", []),
            "cons": result.get("cons", []),
            "summary": result.get("summary", ""),
            "suitability_score": result.get("suitability_score", 0),
            "tech_match": result.get("tech_match", []),
            "feature_match": result.get("feature_match", []),
            "modification_effort": result.get("modification_effort", "Unknown"),
            "metadata": {
                "stars": repo_data.get("stars", "N/A"),
                "forks": repo_data.get("forks", "N/A"),
                "languages": repo_data.get("languages", [])
            }
        }
        
        return evaluation
        
    except Exception as e:
        print(f"Error in evaluation: {str(e)}")
        return {
            "project": {
                "url": repo_data.get("url", ""),
                "title": repo_data.get("title", ""),
                "description": repo_data.get("description", "")
            },
            "pros": ["Repository appeared in search results"],
            "cons": ["Could not evaluate due to an error"],
            "summary": f"Evaluation failed with error: {str(e)}",
            "suitability_score": 1,
            "metadata": {}
        }

def select_best_project(evaluations, project_summary):
    """
    Select the best project from the evaluated repositories.
    
    Args:
        evaluations (list): List of repository evaluations
        project_summary (dict): Project requirements
        
    Returns:
        dict: The best project with reason
    """
    try:
        # Validate inputs first
        if not evaluations or len(evaluations) == 0:
            return {"title": "No valid project found", "url": "", "description": "No evaluations provided."}
        
        # If only one project, return it
        if len(evaluations) == 1:
            best_project = evaluations[0].get("project", {})
            best_project["reason"] = "This is the only project found."
            return best_project
        
        # Get LLM client
        client = get_llm_client()
        if not client:
            # Just use the highest score if no LLM available
            best_eval = max(evaluations, key=lambda x: x.get("suitability_score", 0))
            best_project = best_eval.get("project", {})
            best_project["reason"] = "Selected as the best match based on suitability score."
            return best_project
        
        # Format prompt with project requirements
        formatted_prompt = BEST_PROJECT_SELECTION_PROMPT.format(
            project_purpose=project_summary.get('project_purpose', 'Not specified'),
            platform=project_summary.get('platform', 'Not specified'),
            tech_stack=project_summary.get('tech_stack', 'Not specified'),
            key_features=project_summary.get('key_features', 'Not specified')
        )
        
        # Create a summary of all evaluated projects
        projects_summary = []
        for i, eval in enumerate(evaluations):
            project = eval.get("project", {})
            pros = eval.get("pros", [])
            cons = eval.get("cons", [])
            score = eval.get("suitability_score", 0)
            
            # Create a structured summary with clear indices
            project_summary_text = f"""
Project {i+1}: {project.get('title', 'Unknown')}
URL: {project.get('url', 'Unknown')}
Score: {score}/10
Pros: {', '.join(pros[:3])}
Cons: {', '.join(cons[:2])}
"""
            projects_summary.append(project_summary_text)
        
        # Create a clear user message with numbered projects
        user_message = "Here are the evaluated repositories, numbered from 1 to " + str(len(projects_summary)) + ":\n\n" + "\n".join(projects_summary)
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            timeout=30
        )
        
        # Parse the JSON response
        result = json.loads(response.choices[0].message.content)
                
        # Extract the best project index with validation
        try:
            best_index = int(result.get("best_project_index", 1)) - 1
            if best_index < 0 or best_index >= len(evaluations):
                # Default to highest score if index is invalid
                best_eval = max(evaluations, key=lambda x: x.get("suitability_score", 0))
                best_project = best_eval.get("project", {})
            else:
                best_project = evaluations[best_index].get("project", {})
        except (ValueError, TypeError):
            # Fallback to highest score if index parsing fails
            best_eval = max(evaluations, key=lambda x: x.get("suitability_score", 0))
            best_project = best_eval.get("project", {})
        
        # Add the reason
        best_project["reason"] = result.get("reason", "This project best matches your requirements based on our evaluation.")
        
        return best_project
        
    except Exception as e:
        print(f"Error selecting best project: {str(e)}")
        
        # Provide a robust fallback
        if evaluations and len(evaluations) > 0:
            try:
                # Sort by suitability score as a safe fallback
                sorted_evals = sorted(evaluations, key=lambda x: x.get("suitability_score", 0), reverse=True)
                if sorted_evals:
                    best_project = sorted_evals[0].get("project", {})
                    best_project["reason"] = "Selected as the best match based on suitability score."
                    return best_project
            except Exception:
                pass
        
        # If all else fails, return an empty project with a helpful message
        return {
            "title": "Could not select project", 
            "url": "", 
            "description": "An error occurred during project selection."
        }

def create_enhancement_plan(selected_project, project_summary):
    """
    Create a detailed enhancement plan for implementing the project.
    
    Args:
        selected_project (dict): The selected GitHub project
        project_summary (dict): Project requirements
        
    Returns:
        dict: Enhancement plan with description and implementation steps
    """
    try:
        client = get_llm_client()
        if not client:
            return {
                "enhancement_description": "Unable to generate enhancement plan due to service unavailability.",
                "implementation_steps": []
            }
        
        # Format the prompt with project and requirements details
        formatted_prompt = ENHANCEMENT_PLAN_PROMPT.format(
            project_purpose=project_summary.get('project_purpose', 'Not specified'),
            platform=project_summary.get('platform', 'Not specified'),
            tech_stack=project_summary.get('tech_stack', 'Not specified'),
            key_features=project_summary.get('key_features', 'Not specified'),
            project_title=selected_project.get('title', 'Not specified'),
            project_url=selected_project.get('url', 'Not specified'),
            project_description=selected_project.get('description', 'Not specified')
        )
        
        user_message = f"""Create an enhancement plan to adapt the following GitHub project:

Project: {selected_project.get('title', 'Not specified')}
URL: {selected_project.get('url', 'Not specified')}
Description: {selected_project.get('description', 'Not specified')}

to fulfill these requirements:
Purpose: {project_summary.get('project_purpose', 'Not specified')}
Platform: {project_summary.get('platform', 'Not specified')}
Tech Stack: {project_summary.get('tech_stack', 'Not specified')}
Key Features: {project_summary.get('key_features', 'Not specified')}
"""
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Ensure correct structure
        if "enhancement_description" not in result:
            result["enhancement_description"] = "No enhancement description provided."
        
        if "implementation_steps" not in result or not isinstance(result["implementation_steps"], list):
            result["implementation_steps"] = []
        
        return result
        
    except Exception as e:
        print(f"Error creating enhancement plan: {str(e)}")
        return {
            "enhancement_description": f"Error creating enhancement plan: {str(e)}",
            "implementation_steps": []
        }

def create_simplified_plan(selected_project, project_summary):
    """
    Create a simplified enhancement plan when the detailed plan fails.
    
    Args:
        selected_project (dict): The selected GitHub project
        project_summary (dict): Project requirements
        
    Returns:
        dict: A simplified enhancement plan
    """
    try:
        client = get_llm_client()
        if not client:
            return {
                "enhancement_description": "Plan to adapt the GitHub project to meet requirements.",
                "implementation_steps": []
            }
        
        user_message = f"""Project: {selected_project.get('title')}
URL: {selected_project.get('url')}
Description: {selected_project.get('description')}

Requirements:
- Purpose: {project_summary.get('project_purpose')}
- Platform: {project_summary.get('platform')}
- Tech Stack: {project_summary.get('tech_stack')}
- Features: {project_summary.get('key_features')}

Create a simple, 3-step plan to adapt this GitHub project to the requirements."""
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SIMPLIFIED_PLAN_PROMPT},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            timeout=30
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Ensure correct structure
        if "enhancement_description" not in result:
            result["enhancement_description"] = "Plan to adapt the GitHub project to meet requirements."
        
        if "implementation_steps" not in result or not isinstance(result["implementation_steps"], list):
            result["implementation_steps"] = []
        
        return result
        
    except Exception as e:
        print(f"Error creating simplified plan: {str(e)}")
        return {
            "enhancement_description": "Adapt the GitHub project to meet the requirements.",
            "implementation_steps": []
        }

def generate_implementation_document(project_summary, selected_project, enhancement_plan):
    """
    Generate a comprehensive implementation plan document.
    
    Args:
        project_summary (dict): Project requirements
        selected_project (dict): The selected GitHub project
        enhancement_plan (dict): The enhancement plan
        
    Returns:
        str: The implementation plan as a Markdown document
    """
    try:
        client = get_llm_client()
        if not client:
            # Return a simple implementation plan if LLM is unavailable
            return create_fallback_implementation_doc(project_summary, selected_project, enhancement_plan)
        
        user_message = f"""Project: {selected_project.get('title')}
URL: {selected_project.get('url')}
Description: {selected_project.get('description')}

Requirements:
- Purpose: {project_summary.get('project_purpose')}
- Platform: {project_summary.get('platform')}
- Tech Stack: {project_summary.get('tech_stack')}
- Features: {project_summary.get('key_features')}

Enhancement plan:
{enhancement_plan.get('enhancement_description')}

Implementation steps:
{json.dumps(enhancement_plan.get('implementation_steps', []), indent=2)}

Format this as a comprehensive Markdown implementation plan document with all the sections mentioned in your instructions.
"""
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": FULL_IMPLEMENTATION_PLAN_PROMPT},
                {"role": "user", "content": user_message}
            ],
            timeout=60
        )
        
        # Return the LLM-generated implementation plan
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating implementation document: {str(e)}")
        return create_fallback_implementation_doc(project_summary, selected_project, enhancement_plan)

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