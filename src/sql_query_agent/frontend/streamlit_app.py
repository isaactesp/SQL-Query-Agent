"""
Streamlit interface for the query engine.
Requires the vector store to be trained first (`sql-query-agent train`).

Run with:  sql-query-agent ui
"""

import streamlit as st

from sql_query_agent.agent.vanna_client import get_vanna
from sql_query_agent.config import settings

st.set_page_config(
    page_title="Ask Your Data", page_icon="chart_with_upwards_trend", layout="centered"
)

st.title("Ask Your Data")
st.caption(f"Powered by Vanna, Ollama {settings.ollama_model} and DuckDB")


@st.cache_resource(show_spinner="Loading AI model...")
def load_vanna():
    return get_vanna()


vn = load_vanna()

question = st.text_input(
    "Ask a business question",
    placeholder="e.g. What is total revenue by product category?",
)

if question:
    with st.spinner("Generating SQL..."):
        try:
            sql = vn.generate_sql(question)
        except Exception as e:
            st.error(f"Could not generate SQL: {e}")
            st.stop()

    st.subheader("Generated SQL")
    st.code(sql, language="sql")

    with st.spinner("Running query..."):
        try:
            result = vn.run_sql(sql)
        except Exception as e:
            st.error(f"Query failed: {e}")
            st.stop()

    st.subheader("Results")
    st.dataframe(result, use_container_width=True)
