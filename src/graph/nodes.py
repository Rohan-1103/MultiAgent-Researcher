import sys
from src.graph.state import ResearchState
from src.agents import search_agent, reader_agent, writer_chain, critic_chain
from src.tools import web_search, scrape_url

def call_search_agent(state: ResearchState) -> dict:
    """
    Node 1: Executes the Search Agent to extract web context.
    Safely forces tool parsing from standard or legacy message payloads.
    """
    print("\n🚀 [Node: Search] Analysing research scope...", flush=True)
    
    # We pass a clean string prompt to guide the engine
    response = search_agent.invoke({"input": f"Find recent, reliable information about: {state['topic']}"})
    
    # Extract tool calls using a highly protective multi-layered fallback check
    tool_calls = getattr(response, 'tool_calls', [])
    if not tool_calls and 'tool_calls' in response.additional_kwargs:
        tool_calls = response.additional_kwargs['tool_calls']

    # If the LLM requested a tool, handle it dynamically right here
    if tool_calls:
        try:
            # Safely parse arguments regardless of format (dict vs list structure)
            args = tool_calls[0]['args'] if isinstance(tool_calls[0], dict) else tool_calls[0].args
            print(f"   ↳ 🛠️ Running web_search tool with arguments: {args}", flush=True)
            
            # Execute the tool synchronously to guarantee data alignment
            tool_output = web_search.invoke(args)
            
            # Commit data straight to the state key
            return {"search_results": str(tool_output)}
        except Exception as e:
            print(f"   ⚠️ Tool execution error in Search Node: {str(e)}", flush=True)
            return {"search_results": f"Error running search engine tool: {str(e)}"}
            
    # Fallback if the model simply replied with a standard content string
    return {"search_results": response.content}


def call_reader_agent(state: ResearchState) -> dict:
    """
    Node 2: Selects key candidate URLs and processes them via the deep scraping pipeline.
    """
    print("\n📖 [Node: Reader] Processing top search results...", flush=True)
    
    search_context = state.get("search_results", "")
    
    # Defensive check: if the search context is thin or missing, force an internal fallback query
    if not search_context or "Error" in search_context or len(search_context) < 50:
        search_context = f"Perform alternative analysis directly for topic: {state['topic']}"

    prompt_input = (
        f"Based on the following search results about '{state['topic']}', "
        f"pick the most relevant URL and scrape it for deeper content.\n\n"
        f"Search Results:\n{search_context}"
    )
    
    response = reader_agent.invoke({"input": prompt_input})
    
    # Extract tool calls safely using the multi-layered fallback check
    tool_calls = getattr(response, 'tool_calls', [])
    if not tool_calls and 'tool_calls' in response.additional_kwargs:
        tool_calls = response.additional_kwargs['tool_calls']

    if tool_calls:
        try:
            args = tool_calls[0]['args'] if isinstance(tool_calls[0], dict) else tool_calls[0].args
            print(f"   ↳ 🛠️ Running scrape_url tool with arguments: {args}", flush=True)
            
            tool_output = scrape_url.invoke(args)
            return {"scraped_content": str(tool_output)}
        except Exception as e:
            print(f"   ⚠️ Tool execution error in Reader Node: {str(e)}", flush=True)
            return {"scraped_content": f"Error running scraper tool: {str(e)}"}
            
    return {"scraped_content": response.content}


def call_writer_chain(state: ResearchState) -> dict:
    """
    Node 3: Formulates or updates the markdown report draft, integrating previous feedback loops.
    """
    print("\n📝 [Node: Writer] Generating or refining the technical research report...", flush=True)
    
    research_combined = (
        f"SEARCH ENGINE HIGHLIGHTS:\n{state.get('search_results', '')}\n\n"
        f"DEEP SCRAPED CONTENT:\n{state.get('scraped_content', '')}"
    )
    
    previous_feedback = state.get("feedback", "No historical feedback. This is the first draft.")
    
    report_markdown = writer_chain.invoke({
        "topic": state['topic'],
        "research": research_combined,
        "feedback": previous_feedback
    })
    
    current_loops = state.get("loop_count", 0)
    return {
        "report": report_markdown, 
        "loop_count": current_loops + 1
    }


def call_critic_chain(state: ResearchState) -> dict:
    """
    Node 4: Evaluates the compiled draft against quality and compliance guidelines.
    """
    print("\n🧐 [Node: Critic] Stress-testing document structure...", flush=True)
    report_to_assess = state.get("report", "Empty draft. Assessment aborted.")
    evaluation_logs = critic_chain.invoke({"report": report_to_assess})
    return {"feedback": evaluation_logs}