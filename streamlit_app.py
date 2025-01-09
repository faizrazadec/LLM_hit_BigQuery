import streamlit as st
from main import get_response # Import your LLM logic

st.title("Natural Language to BigQuery SQL")

# Input form
with st.form("query_form"):
    user_query = st.text_area("Enter your natural language query:", height=68)
    submit_button = st.form_submit_button(label="Generate SQL")

# Process user input
if submit_button:
    if user_query.strip():
        st.write("Processing your query...")
        try:
            # Call the function to generate SQL
            sql_query = get_response(user_query)
            st.success("Generated SQL Query:")
            st.code(sql_query, language="sql")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Please enter a query before submitting.")
