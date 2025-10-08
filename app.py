import asyncio

import streamlit as st

from src.agent.alpha_agent import run_manual_react, setup_runtime

# --- Page Configuration ---
st.set_page_config(
    page_title="AlphaAgent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Title and Description ---
st.title("AlphaAgent 🤖")
st.markdown(
    """
    <p align="center"><i>Financial Clarity, Powered by AI</i></p>
    """,
    unsafe_allow_html=True,
)
st.info(
    "Welcome to AlphaAgent. Enter a financial query below to get started. For example: "
    "**'What are the main risks for Microsoft (MSFT) according to its latest 10-K filing, and what is its current P/E ratio?'**"
)


# --- Caching and Agent Setup ---
@st.cache_resource
def load_agent_tools():
    """
    Loads and caches the tools required by the agent.
    This function is decorated with @st.cache_resource to ensure that the
    heavy components (LLM, RAG tool, etc.) are loaded only once.
    """
    _, rag_tool, q_tool = setup_runtime()
    return rag_tool, q_tool


rag_tool, q_tool = load_agent_tools()


# --- Asynchronous Event Loop Management ---
def get_or_create_eventloop():
    """
    Gets the current asyncio event loop or creates a new one if none exists.
    This is necessary for running asynchronous agent functions within
    Streamlit's synchronous execution model.
    """
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop


# --- User Input and Agent Execution ---
user_query = st.text_input("Enter your financial query:", key="query_input")

if st.button("Analyse", key="analyse_button"):
    if user_query:
        with st.spinner("AlphaAgent is thinking..."):
            try:
                loop = get_or_create_eventloop()
                response = loop.run_until_complete(
                    run_manual_react(user_query, rag_tool, q_tool)
                )

                st.subheader("Analysis Complete")
                st.markdown(response.text)

                # Display provenance for transparency
                with st.expander("View Tools Used"):
                    st.json(
                        {
                            "pipeline": response.pipeline,
                            "tools": response.tools,
                        }
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query to analyse.")
