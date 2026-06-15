import streamlit as st
from pipeline import app

# Page Configuration
st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔎",
    layout="wide"
)

# Title
st.title("🔎 Multi-Agent Research System")
st.markdown(
    "Research any topic using a **Search Agent**, **Reader Agent**, "
    "**Writer Agent**, and **Critic Agent**."
)

st.divider()

# User Input
topic = st.text_input(
    "Enter a Research Topic",
    placeholder="Example: Latest advancements in Generative AI"
)

# Run Button
if st.button("Generate Research Report", type="primary"):

    if not topic.strip():
        st.warning("Please enter a research topic.")
        st.stop()

    # Progress Indicator
    progress = st.progress(0)
    status = st.empty()

    try:
        status.info("🔍 Running Search Agent...")
        progress.progress(25)

        final_state = app.invoke({"topic": topic})

        progress.progress(100)
        status.success("✅ Research Pipeline Completed!")

        # Display Results
        st.divider()

        with st.expander("🔍 Search Results", expanded=False):
            st.write(final_state.get("search_results", "No search results found."))

        with st.expander("📚 Scraped Content", expanded=False):
            st.write(final_state.get("scraped_content", "No content scraped."))

        st.subheader("📝 Research Report")
        st.write(final_state.get("report", "No report generated."))

        st.subheader("🧐 Critic Feedback")
        st.write(final_state.get("feedback", "No feedback generated."))

    except Exception as e:
        st.error(f"Error: {e}")