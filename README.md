# Multi-Agent Research Agent

A Python prototype that orchestrates a research workflow using four cooperating agents: Search, Reader, Writer, and Critic.

## What this project does

This repository demonstrates a research pipeline where:

- a **Search Agent** locates relevant content and URLs,
- a **Reader Agent** scrapes and extracts meaningful page text,
- a **Writer Agent** composes a structured report,
- a **Critic Agent** evaluates the final output.

The pipeline is built with a graph-based orchestrator and exposed through a simple Streamlit application.

## Architecture

The application is divided into four primary layers:

- `app.py` — Streamlit UI for user input and display.
- `agents.py` — LLM prompt definitions, tool bindings, and agent chains.
- `pipeline.py` — workflow orchestration using `langgraph`.
- `tools.py` — external search and web scraping helpers.

```text
User -> Streamlit UI (app.py)
             |
             v
        Workflow Graph (pipeline.py)
             |
    +--------+--------+
    |                 |
 Search Agent      Reader Agent
    |                 |
    +--------+--------+
             |
        Writer Agent
             |
        Critic Agent
             |
          Output
```

## How it works

1. The user enters a topic in the Streamlit page.
2. The UI triggers the pipeline with the topic.
3. The Search Agent runs a web search using the `web_search` tool.
4. The Reader Agent selects a URL and scrapes text via the `scape_url` tool.
5. The Writer Agent generates a structured report from search and scraped content.
6. The Critic Agent reviews the report and returns a score, strengths, and improvements.

## Key files

- `app.py`: Launches the Streamlit interface and presents results.
- `agents.py`: Defines LLM models, prompts, chains, and tool bindings.
- `pipeline.py`: Defines the `ResearchState`, nodes, and execution graph.
- `tools.py`: Implements `web_search` and `scape_url` helper tools.
- `requirements.txt`: Lists Python dependencies.
- `pyproject.toml`: Project metadata and Python version requirement.

## Setup and run

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Add your Tavily API key to a `.env` file:

```text
TAVILY_API_KEY=your_api_key_here
```

4. Run the Streamlit app:

```powershell
streamlit run app.py
```

## Pros

- Modular separation of UI, agents, orchestration, and tools.
- Clear workflow with discrete search, read, write, and critique stages.
- Tool-enabled agents can call external functions for grounding.
- Streamlit UI makes it easy to explore the research workflow interactively.

## Future improvements

- Add multi-source aggregation and source ranking.
- Improve scraping with article extraction or readability parsing.
- Add result caching and retry logic.
- Add a fact-checking or citation validation agent.
- Build automated tests for each pipeline node.
- Add Docker support and a deployable service layer.

## Notes
This project is intended as a prototype for agent orchestration and research workflows, not as a production-grade research assistant.
