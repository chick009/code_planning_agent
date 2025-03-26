# Project Implementation Planner

## Overview
Project Implementation Planner is an AI-powered application that helps users transform their project ideas into detailed implementation plans. It leverages natural language processing and GitHub repositories to provide tailored step-by-step guidance for implementing new software projects.

## Features
- **Idea Analysis**: Evaluates project clarity and provides feedback for improvement
- **GitHub Search**: Automatically searches for relevant GitHub repositories that match your project requirements
- **Repository Evaluation**: Analyzes repositories for suitability, including features, technologies, and implementation effort
- **Best Match Selection**: Identifies the most suitable GitHub repository as a starting point
- **Implementation Plan Generation**: Creates a comprehensive implementation plan with detailed steps
- **Step Files**: Generates individual implementation step files for easier tracking

## Getting Started

### Prerequisites
- Python 3.7+
- Streamlit
- OpenAI API key
- Tavily API key

### Installation
1. Clone the repository
```bash
git clone https://github.com/chick009/code_planning_agent.git
cd code_planning_agent
```

2. Install required packages
```bash
pip install -r requirements.txt
```

3. Set up environment variables in a `.env` file:
```
TAVILY_API_KEY=your_tavily_api_key
OPENAI_API_KEY=your_openai_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### Usage
Run the application:
```bash
streamlit run app_new.py
```

Navigate to the provided URL (typically http://localhost:8501) in your web browser.

## Project Structure
- `app_new.py`: Main application file
- `prompts/`: Directory containing system prompts for the AI models
- `src/`: Source code directory
  - `api.py`: API interactions for LLMs and external services
  - `handlers.py`: Event handlers for user interactions
  - `session.py`: Session state management
  - `utils.py`: Utility functions

## How It Works
1. Enter your project idea in the chat interface
2. The AI evaluates the clarity of your idea and may ask for clarifications
3. Once your idea is clear enough, the app searches for relevant GitHub repositories
4. The AI evaluates each repository against your requirements
5. The best matching repository is selected as a starting point
6. A detailed implementation plan is generated
7. Individual step files are created for tracking progress

## License
MIT

## Acknowledgments
- OpenAI for AI services
- Tavily for search capabilities
- Streamlit for the UI framework
