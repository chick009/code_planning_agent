"""
Prompt collection module for the code planning agent.
"""

from prompts.idea_clarity import IDEA_CLARITY_PROMPT
from prompts.project_summary import PROJECT_SUMMARY_PROMPT
from prompts.repository_evaluation import (
    REPOSITORY_EVALUATION_PROMPT,
    BEST_PROJECT_SELECTION_PROMPT
)
from prompts.implementation_plan import (
    ENHANCEMENT_PLAN_PROMPT,
    SIMPLIFIED_PLAN_PROMPT,
    FULL_IMPLEMENTATION_PLAN_PROMPT
)

__all__ = [
    'IDEA_CLARITY_PROMPT',
    'PROJECT_SUMMARY_PROMPT',
    'REPOSITORY_EVALUATION_PROMPT',
    'BEST_PROJECT_SELECTION_PROMPT',
    'ENHANCEMENT_PLAN_PROMPT',
    'SIMPLIFIED_PLAN_PROMPT',
    'FULL_IMPLEMENTATION_PLAN_PROMPT'
] 