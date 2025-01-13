import streamlit as st
from components import initialize_components
from response_handler import get_response

def main():
    st.set_page_config(page_title="SQL Query Generator", page_icon="🔍", layout="wide")
    
    st.title("🔍 SQL Query Generator")
    st.write("Enter your query in natural language, and I'll help you generate the corresponding SQL query.")
    
    # Initialize components
    llm, vector_store = initialize_components()
    
    # Create input field for user query
    user_query = st.text_area("Enter your query:", height=100,
                             placeholder="Example: Provide me the names of the students that have paid their challanform and are in semester fall 2025")
    
    # Add a slider for the number of context results
    k_value = 3
    
    # Add a button to generate response
    if st.button("Generate SQL Query"):
        if user_query:
            with st.spinner("Generating SQL query..."):
                response = get_response(user_query, llm, vector_store, k=k_value)
                
                if response:
                    st.success("Query generated successfully!")
                    st.markdown("### Response:")
                    st.markdown(response)
                else:
                    st.error("Failed to generate a response. Please try again.")
        else:
            st.warning("Please enter a query first.")
    
    # Add some helpful information in the sidebar
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
        - Be specific about the data you want to retrieve
        - Include relevant time periods or conditions
        - Mention specific table names if you know them
        - Use clear and concise language
        """)

if __name__ == "__main__":
    main()
