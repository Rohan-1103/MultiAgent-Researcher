import streamlit as st
from src.graph.pipeline import app

# 1. Premium Page Configuration
st.set_page_config(
    page_title="InsightEngine AI | Multi-Agent Research Framework",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS styling for an ultra-clean layout
st.markdown("""
    <style>
    .report-title { font-size: 2.4rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.5rem; }
    .subtitle { font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem; }
    div[data-testid="stExpander"] { border: 1px solid #E5E7EB; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar Branding & Control Panel
with st.sidebar:
    st.markdown("### 🛠️ Framework Engine")
    st.caption("Orchestrator: **LangGraph v0.2**")
    st.caption("Backend LLM: **Groq / Llama-3.3-70b**")
    st.divider()
    
    st.markdown("### ⚙️ Pipeline Parameters")
    max_loops = st.slider("Max Revision Cycles", min_value=1, max_value=5, value=3)
    st.info("The Critic Agent will force-finalize the output if it hits this revision ceiling.")
    st.divider()
    
    st.caption("⚡ Built by Rohan Goswami")

# 4. Main Header Component
st.markdown("<div class='report-title'>🤖 InsightEngine AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Advanced Multi-Agent Automated Research Framework</div>", unsafe_allow_html=True)

# 5. Core Operational Input Box
topic = st.text_input(
    "Identify your research objective:",
    placeholder="e.g., Quantum computing breakthroughs in cryptographic systems"
)

# 6. Execution Pipeline Trigger
if st.button("Launch Autonomous Agents", type="primary", use_container_width=True):
    if not topic.strip():
        st.warning("⚠️ Action required: Please enter a clear research topic before initiating.")
        st.stop()

    st.markdown("### 🪐 Live Orchestration Stream")
    status_container = st.container()
    
    # Initialize global tracking dictionary
    final_state = {}
    current_loop_display = 0

    with status_container:
        with st.status("⚡ Initializing multi-agent graph coordination...", expanded=True) as graph_status:
            
            # Pass user-selected max_loops explicitly to the graph state
            for event in app.stream({"topic": topic, "loop_count": 0, "max_loops": max_loops}, stream_mode="updates"):
                
                # --- 1. Intercept Search Agent Updates ---
                if "search" in event:
                    st.markdown("🔍 **Search Agent** has compiled web citations and snippets.")
                    node_output = event.get("search") or {}
                    if "search_results" in node_output:
                        final_state["search_results"] = node_output["search_results"]
                
                # --- 2. Intercept Reader Agent Updates ---
                if "reader" in event:
                    st.markdown("📖 **Reader Agent** extracted deep main-article content from selected URLs.")
                    node_output = event.get("reader") or {}
                    if "scraped_content" in node_output:
                        final_state["scraped_content"] = node_output["scraped_content"]
                        
                # --- 3. Intercept Copywriting and Critique Loops ---
                if "writer" in event:
                    node_output = event.get("writer") or {}
                    current_loop_display = node_output.get("loop_count", current_loop_display)
                    st.markdown(f"📝 **Writer Agent** compiled an updated report draft. *(Cycle Iteration: {current_loop_display})*")
                    if "report" in node_output:
                        final_state["report"] = node_output["report"]
                        
                if "critic" in event:
                    node_output = event.get("critic") or {}
                    feedback_text = node_output.get("feedback", "")
                    final_state["feedback"] = feedback_text
                    
                    if "Verdict: APPROVED" in feedback_text:
                        st.markdown("✅ **Critic Agent** formally verified and approved the report structure.")
                    else:
                        st.markdown("🔄 **Critic Agent** issued a change request. Re-routing workflow back to Writer.")

            graph_status.update(label="🚀 Autonomous Research Complete!", state="complete", expanded=False)

    # 7. Presentation Layer (Render Results)
    st.divider()
    st.markdown("### 📊 Generated Analytical Artifacts")
    
    # Organize outputs into clean, functional tabbed segments
    tab_report, tab_critic, tab_sources = st.tabs([
        "📄 Executive Report", 
        "🧐 Quality Control Logs", 
        "🌐 Extracted Context Items"
    ])
    
    with tab_report:
        if "report" in final_state and final_state["report"]:
            st.markdown(final_state["report"])
        else:
            st.info("No report markdown artifact found in final state.")
            
    with tab_critic:
        if "feedback" in final_state and final_state["feedback"]:
            st.markdown(f"**Total Workflow Revisions Ran:** `{current_loop_display}`")
            st.divider()
            st.markdown(final_state["feedback"])
        else:
            st.info("No editing or compliance logs recorded.")
            
    with tab_sources:
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("Raw Web Snippets (Tavily Index)", expanded=False):
                st.text(final_state.get("search_results", "Empty query data."))
        with col2:
            with st.expander("Raw Extracted Webpage Strings", expanded=False):
                st.text(final_state.get("scraped_content", "Empty document collection."))