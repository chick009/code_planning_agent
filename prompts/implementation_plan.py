"""
Prompts for creating implementation plans.
"""

ENHANCEMENT_PLAN_PROMPT = """You are an expert software architect. Your task is to create a comprehensive enhancement plan 
to modify an existing GitHub project to meet specific requirements. 

Project Requirements:
- Purpose: {project_purpose}
- Platform: {platform}
- Tech Stack: {tech_stack}
- Key Features: {key_features}

Base Project:
- Title: {project_title}
- URL: {project_url}
- Description: {project_description}

Your output should include:
1. A detailed enhancement description
2. A set of implementation steps, each with:
   - Title
   - Description
   - Specific tasks to complete
   - Expected outcome
   - Resources needed (libraries, tools, etc.)

Return your response as a JSON object with:
1. "enhancement_description": A comprehensive overview of the planned enhancements
2. "implementation_steps": An array of step objects, where each step has:
   - "title": Short name for the step
   - "description": Detailed explanation of what this step involves
   - "tasks": List of specific tasks to complete, as a bulleted string
   - "expected_outcome": What the result of this step should be
   - "resources": External resources or references that might be helpful
"""

SIMPLIFIED_PLAN_PROMPT = """You are a software development expert. Create a simple enhancement plan for a GitHub project.
Your response must be a valid JSON with these exact keys:
1. "enhancement_description": A paragraph describing the plan
2. "implementation_steps": An array of steps, where each step has:
   - "title": Name of the step
   - "description": What to do
   - "tasks": The specific tasks, as a bulleted list
   - "expected_outcome": What will be achieved
   - "resources": Helpful references
"""

FULL_IMPLEMENTATION_PLAN_PROMPT = """You are a software development expert. Create a detailed implementation plan in Markdown format.
The plan should be comprehensive and include:

1. Project Overview section
2. Base Project details 
3. Enhancement Strategy section
4. Detailed Implementation Steps - For each step include:
   - A descriptive title
   - A detailed description
   - Specific tasks to be completed
   - Expected outcomes
   - Resources/references

Format the document with proper Markdown headings, lists, and organization.
""" 