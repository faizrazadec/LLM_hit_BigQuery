import streamlit as st
import asyncio
from test import get_data, summary
from components_test import initialize_components
from response_handler import get_response_async
from big_query_manager import BigQueryManager
import os
from dotenv import load_dotenv
load_dotenv()

PROJECT_ID = os.getenv('PROJECT_ID')
DATASET_ID = os.getenv("DATASET_ID")
bq_manager = BigQueryManager(project_id=PROJECT_ID, dataset_id=DATASET_ID)

async def main():
    # Configure the page
    st.set_page_config(page_title="SQL Query Generator", page_icon="🔍", layout="wide")
    
    # Application title and description
    st.title("🔍 SQL Query Generator")
    st.write("Enter your query in natural language, and I'll help you generate the corresponding SQL query.")

    # Initialize components (e.g., LLM and Vector Store)
    try:
        if "llm" not in st.session_state or "vector_store" not in st.session_state:
            st.session_state.llm, st.session_state.vector_store = await initialize_components()
        llm = st.session_state.llm
        vector_store = st.session_state.vector_store
    except Exception as e:
        st.error(f"Failed to initialize components. Error: {e}")
        return

    # User input for natural language query
    user_query = st.text_area(
        "Enter your query:",
        height=68,
        placeholder="Example: Provide me the names of the students that have paid their challan form and are in semester Fall 2025"
    )

    # Generate SQL Query Button
    if st.button("Generate SQL Query"):
        if user_query.strip():
            with st.spinner("Generating SQL query..."):
                try:
                    # Call the asynchronous query generation function
                    response = await get_response_async(user_query, llm, vector_store, k=5)

                    if response:
                        st.success("Query generated successfully!")
                        st.markdown("### Response:")
                        st.code(response, language="sql")
                        
                        df = get_data(response)
                        st.success("Result!")
                        st.dataframe(df)
                        st.markdown("### Summary")
                        summ = summary(user_query, llm)
                        st.write(summ)
                    else:
                        st.error("Failed to generate a response. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred while processing your request: {e}")
        else:
            st.warning("Please enter a query first.")

    # Sidebar with additional information
    with st.sidebar:
        st.header("About")
        st.write("""
        This application uses LangChain and Google's Gemini model to:
        1. Understand your natural language query
        2. Search relevant schema context
        3. Generate appropriate SQL queries
        """)
        
        st.header("Tips")
        st.write("""
        - Be specific about the data you want to retrieve.
        - Include relevant time periods or conditions.
        - Mention specific table names if you know them.
        - Use clear and concise language.
        """)

if __name__ == "__main__":
    asyncio.run(main())
