# 🤖 InsightEngine AI

### An Advanced Graph-Orchestrated Multi-Agent Research Framework for Autonomous Technical Intelligence

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/LangGraph-v0.2-FF4F00.svg)](https://python.langchain.com/docs/langgraph)
[![UI](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io)
[![LLM Backend](https://img.shields.io/badge/Groq-Llama--3.3--70b-black.svg)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

# 📖 Overview

**InsightEngine AI** is an enterprise-grade, graph-orchestrated, multi-agent research automation system designed to perform autonomous web research, deep information extraction, iterative report refinement, and quality-controlled content synthesis.

Traditional Retrieval-Augmented Generation (RAG) systems often suffer from:

* Linear execution pipelines
* Context pollution between tasks
* Hallucination amplification
* Poor revision mechanisms
* Lack of state management
* Inadequate source verification

InsightEngine AI addresses these limitations by replacing conventional sequential chains with a **stateful LangGraph-based multi-agent architecture** that coordinates multiple specialized AI agents through cyclical feedback loops.

Instead of relying on a single monolithic LLM prompt, the framework decomposes the research workflow into independent cognitive units:

1. Search Intelligence Agent
2. Deep Reading Agent
3. Research Synthesis Agent
4. Quality Assurance Agent

Each agent is responsible for a specific domain of reasoning, dramatically improving factual grounding, response quality, and maintainability.

The system continuously refines its output until either:

* The report satisfies quality requirements, or
* A user-defined revision ceiling is reached.

The final output is a **production-ready Markdown research artifact** complete with citations, structured sections, and source references.

---

# 🎯 Project Objectives

The primary goals of InsightEngine AI are:

### ✅ Automate End-to-End Research Workflows

Perform autonomous research without requiring users to manually search, extract, and summarize information.

### ✅ Reduce Hallucinations

Isolate responsibilities among specialized agents to minimize context contamination and improve factual consistency.

### ✅ Introduce Controlled Self-Correction

Enable iterative improvement loops through Critic → Writer feedback cycles.

### ✅ Provide Source Grounding

Generate reports supported by validated web sources and extracted content.

### ✅ Enable Human-Monitored Execution

Offer real-time visibility into graph execution using an interactive Streamlit interface.

---

# 🚀 Key Features

## 🧠 Multi-Agent Cognitive Architecture

The framework employs specialized agents that operate independently:

| Agent        | Responsibility                          |
| ------------ | --------------------------------------- |
| Search Agent | Query generation and source discovery   |
| Reader Agent | Web scraping and information extraction |
| Writer Agent | Report drafting and synthesis           |
| Critic Agent | Quality assurance and revision requests |

This separation of concerns significantly reduces hallucinations and improves output reliability.

---

## 🔄 Stateful Cyclical Revision Loops

Unlike linear chains, the system supports:

Writer → Critic → Writer → Critic

feedback cycles.

Benefits:

* Self-correction
* Improved report quality
* Enhanced factual consistency
* Controlled token consumption

The maximum number of revision loops can be configured directly from the UI.

```python
max_loops = 1 → Fast execution
max_loops = 5 → Extensive refinement
```

---

## 🛡️ Tool-Enforced Execution Layer

Open-weight models frequently ignore tool-calling instructions and return conversational responses.

InsightEngine AI solves this problem through:

* Strict `tool_choice` enforcement
* Typed function schemas
* Automatic argument validation
* JSON sanitization pipelines

This ensures agents produce valid structured outputs instead of free-form text.

---

## 🔌 Dual Web Ingestion Pipeline

The framework implements a robust scraping architecture:

### Strategy 1

BeautifulSoup DOM Extraction

### Strategy 2

Headless Markdown Extraction Fallback

Benefits:

* Removes navigation menus
* Removes advertisements
* Removes tracking scripts
* Removes styling noise
* Extracts high-density textual content

This dramatically improves downstream summarization quality.

---

## 📊 Real-Time Stream Monitoring

The Streamlit frontend listens to LangGraph event streams and displays:

* Active node execution
* Search results
* Extracted URLs
* Critic feedback
* Iteration count
* Final report generation

This provides complete transparency into the reasoning pipeline.

---

# 🏗️ System Architecture

The entire application is orchestrated using **LangGraph StateGraph**.

The graph passes a strongly typed immutable state object:

```python
ResearchState
```

between all execution nodes.

---

# 🔄 System Graph Topology

```text
                  +---------------------------------------+
                  |         Streamlit UI Layer            |
                  | (Parameters, Topic, Stream Terminal)  |
                  +-------------------+-------------------+
                                      |
                                      v
                        +---------------------------+
                        |  LangGraph Orchestrator   |
                        |      (pipeline.py)        |
                        +-------------+-------------+
                                      |
            +-------------------------+-------------------------+
            |                                                   |
            v                                                   v
  +-------------------+                               +-------------------+
  |   Search Agent    |                               |   Reader Agent    |
  | (Queries & Links) |                               | (Deep Web Scrape) |
  +---------+---------+                               +---------+---------+
            |                                                   |
            +-------------------------+-------------------------+
                                      |
                                      v
                            +-------------------+
                            |   Writer Agent    |
                            | (Draft Synthesis) |
                            +---------+---------+
                                      |
                                      v
                            +-------------------+
                            |   Critic Agent    |
                            | (Quality Audit)   |
                            +---------+---------+
                                      |
                        Revision Needed? (Yes)
                                      |
                                      |
                                      v
                            +-------------------+
                            |   Writer Agent    |
                            +-------------------+
                                      |
                        Approved OR Loop Limit
                                      |
                                      v
                            +-------------------+
                            | Finished Artifact |
                            +-------------------+
```

---

# 🧩 Execution Flow

## Step 1: User Prompt Submission

Example:

```text
Analyze the impact of zero-knowledge proofs on Layer-2 blockchain scalability.
```

---

## Step 2: Search Agent

Responsibilities:

* Generate search queries
* Discover reliable sources
* Collect URLs
* Rank information relevance

Output:

```python
{
    "queries": [...],
    "sources": [...]
}
```

---

## Step 3: Reader Agent

Responsibilities:

* Scrape discovered websites
* Remove boilerplate HTML
* Extract meaningful text
* Normalize content

Output:

```python
{
    "documents": [...]
}
```

---

## Step 4: Writer Agent

Responsibilities:

* Analyze extracted content
* Generate research report
* Produce structured markdown
* Add citations and references

Output:

```markdown
# Executive Summary
# Technical Analysis
# Findings
# Conclusion
```

---

## Step 5: Critic Agent

Responsibilities:

* Check factual consistency
* Check completeness
* Verify report quality
* Request revisions if necessary

Output:

```python
{
    "verdict":"REVISE",
    "feedback":"Expand scalability limitations section."
}
```

or

```python
{
    "verdict":"APPROVED"
}
```

---

# 📂 Project Structure

```text
insightengine-ai/
│
├── src/
│
├── config.py
│
├── agents/
│   ├── __init__.py
│   ├── search_agent.py
│   ├── reader_agent.py
│   ├── writer_agent.py
│   └── critic_agent.py
│
├── graph/
│   ├── __init__.py
│   ├── state.py
│   ├── nodes.py
│   └── pipeline.py
│
├── tools/
│   ├── __init__.py
│   ├── search.py
│   └── scraper.py
│
├── ui/
│   └── app.py
│
├── .env.example
├── requirements.txt
├── README.md
└── LICENSE
```

---

# ⚙️ Technology Stack

| Layer         | Technologies                       |
| ------------- | ---------------------------------- |
| Orchestration | LangGraph                          |
| LLM Backend   | Groq (Llama-3.3-70B)               |
| Framework     | LangChain                          |
| Search Engine | Tavily Search API                  |
| Scraping      | BeautifulSoup, Markdown Extraction |
| Frontend      | Streamlit                          |
| Configuration | Pydantic Settings                  |
| Language      | Python 3.9+                        |

---

# 🛠 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/insightengine-ai.git
cd insightengine-ai
```

---

## Create Virtual Environment

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

---

## Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create:

```bash
cp .env.example .env
```

Add:

```env
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxx
```

---

# ▶️ Running the Application

```bash
streamlit run src/ui/app.py
```

---

# 🖥 Dashboard Features

### Sidebar Controls

* Research Topic Input
* Maximum Revision Loops
* Execution Parameters

### Live Terminal

Displays:

* Current Node
* Tool Calls
* Search Results
* Critic Feedback
* Runtime Events

### Output Tabs

* Final Report
* Critique Logs
* Source References
* Execution Metadata

---

# 🛡 Engineering Safeguards

## Path Resolution Injection

```python
sys.path.insert(0, ROOT_DIR)
```

Prevents import failures across nested directories.

---

## JSON Sanitization Layer

Automatically repairs malformed tool outputs:

```python
"{'query':'AI'}"
```

↓

```python
{
   "query":"AI"
}
```

---

## Loop Ceiling Protection

Prevents infinite recursion:

```python
if loops >= max_loops:
    return END
```

---

## Tool Enforcement

Guarantees structured function calls:

```python
tool_choice="required"
```

---

# 📈 Why LangGraph Instead of Traditional Chains?

| Traditional Chains      | InsightEngine AI          |
| ----------------------- | ------------------------- |
| Linear execution        | Stateful graph execution  |
| No feedback loops       | Cyclical revision loops   |
| Single agent            | Multi-agent architecture  |
| Weak memory             | Shared state management   |
| High hallucination risk | Isolated cognitive agents |
| Limited observability   | Real-time monitoring      |

---

# 👨‍💻 Author

## Rohan Goswami

**AI Engineer | Data Science Enthusiast**

Passionate about building production-grade AI systems involving:

* Agentic AI
* Multi-Agent Systems
* LangGraph
* LLM Engineering
* Generative AI
* Research Automation
* Data Science

---

# 📜 License

This project is licensed under the MIT License.

See the `LICENSE` file for additional information.

---

# ⭐ If you found this project useful, consider giving it a star on GitHub!
