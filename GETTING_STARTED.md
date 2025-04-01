# Getting Started with Mini-Project Agent

This guide will help you set up and use the Mini-Project Agent, a Streamlit-powered tool that helps you kickstart mini-projects by leveraging AI reasoning, GitHub search, and automated documentation generation.

## Prerequisites

- Python 3.7 or higher
- Tavily API key (for GitHub searches)
- Internet connection

## Setup Instructions

1. **Clone the repository**

```bash
git clone <repository-url>
cd mini-project-agent
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory by copying the `.env.example` file:

```bash
cp .env.example .env
```

Then edit the `.env` file and add your API keys:

```
TAVILY_API_KEY=your_tavily_api_key_here
MODEL_API_KEY=your_model_api_key_here  # Optional
```

To get a Tavily API key, sign up at [Tavily's website](https://tavily.com).

4. **Run the Streamlit app**

```bash
python -m streamlit run app.py
```

The application should open in your browser at `http://localhost:8501`.

## Using the Mini-Project Agent

The Mini-Project Agent guides you through four steps:

### Step 1: Clarify Your Idea

1. Enter your project idea in the text box
2. Click "Clarify My Idea"
3. Review the project summary and clarify if needed
4. Click "Proceed to GitHub Search"

### Step 2: Find Relevant GitHub Projects

1. Review your project summary and the auto-generated search query
2. Click "Search with Tavily"
3. Explore the GitHub projects found
4. Click "Proceed to Evaluation"

### Step 3: Evaluate and Plan Enhancements

1. Review the evaluation of each GitHub project
2. Select a base project from the dropdown
3. Describe how you want to enhance the selected project
4. Outline integration steps if combining multiple projects
5. Click "Create Enhancement Plan" and then "Proceed to README Generation"

### Step 4: Generate README

1. Review the generated README.md
2. Download the README using the provided link
3. Use this README with tools like Cursor or Agentic Sonnet 3.7 to generate code
4. Start a new project or go back to make adjustments

## Troubleshooting

- **Tavily API Key Issues**: Ensure your API key is correctly entered in the `.env` file
- **Streamlit Installation**: If you encounter problems with Streamlit, try reinstalling with `pip install --upgrade streamlit`
- **Search Results**: If you get poor search results, try refining your project idea or providing more details

## Next Steps

After generating your README, you can:

1. Use tools like Cursor to generate code based on the README
2. Fork or clone the selected GitHub project
3. Implement the enhancements you've planned
4. Build and test your mini-project

Happy coding! 