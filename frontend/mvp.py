"""
app.py
------
Streamlit interface for the Vanna query engine.
Requires ai_layer/setup.py to have been run first (trains ChromaDB).

Run with:  streamlit run app/app.py
"""

import os
import sys

import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
from ai_layer.setup import get_vanna

st.set_page_config(
    page_title="Ask Your Data", page_icon="chart_with_upwards_trend", layout="centered"
)

st.title("Ask Your Data")
st.caption("Powered by Vanna, Ollama llama3.1 and DuckDB")


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
