import os
from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

def initialize_components():
    load_dotenv()
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not GEMINI_API_KEY:
        try:
            GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        except:
            if 'GEMINI_API_KEY' not in st.session_state:
                st.session_state.GEMINI_API_KEY = None
            
            if not st.session_state.GEMINI_API_KEY:
                st.warning("No API key found in environment or secrets.")
                api_key = st.text_input("Please enter your Gemini API key:", type="password")
                if api_key:
                    st.session_state.GEMINI_API_KEY = api_key
                    GEMINI_API_KEY = api_key
                else:
                    st.stop()
            else:
                GEMINI_API_KEY = st.session_state.GEMINI_API_KEY
    
    if not GEMINI_API_KEY:
        st.error("API key is required to proceed.")
        st.stop()
    
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GEMINI_API_KEY,
            task_type="retrieval_document"
        )
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            api_key=GEMINI_API_KEY
        )
        
        vector_store = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db"
        )
        
        return llm, vector_store
    
    except Exception as e:
        st.error(f"Error initializing components: {str(e)}")
        st.stop()
