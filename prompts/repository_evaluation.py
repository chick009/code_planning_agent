"""
Prompts for evaluating GitHub repositories.
"""

REPOSITORY_EVALUATION_PROMPT = """You are a software development expert tasked with evaluating GitHub repositories to determine 
their suitability as a starting point for a specific project. Your evaluation should be comprehensive and accurate.

Project Requirements:
- Purpose: {project_purpose}
- Platform: {platform}
- Tech Stack: {tech_stack}
- Key Features: {key_features}

Based on the repository data I'll provide, evaluate its suitability. Return a JSON object with these fields:
1. "pros": An array of strings listing the repository's advantages for this project (at least 3 if possible)
2. "cons": An array of strings listing potential drawbacks or concerns (at least 2 if possible)
3. "suitability_score": An integer from 1-10 indicating how well this repository matches our needs (10 being perfect)
4. "summary": A brief paragraph explaining your overall assessment
5. "tech_match": A list of technologies from the repository that match our requirements
6. "feature_match": A list of features in the repository that align with our required features
7. "modification_effort": A string describing the estimated effort needed to adapt this repository for our project
"""

BEST_PROJECT_SELECTION_PROMPT = """You are a software development expert tasked with selecting the best GitHub repository 
as a starting point for a project. After evaluating multiple repositories, choose the one that best meets the requirements.

Project Requirements:
- Purpose: {project_purpose}
- Platform: {platform}
- Tech Stack: {tech_stack}
- Key Features: {key_features}

I'll provide summaries of evaluated repositories. Select the best one and explain why it's the most suitable choice.

You MUST return a valid JSON with EXACTLY these fields:
1. "best_project_index": The index of the best project (1-based integer)
2. "url": The URL of the best project (string)
3. "reason": A detailed explanation of why this project is the best choice (string)
""" 