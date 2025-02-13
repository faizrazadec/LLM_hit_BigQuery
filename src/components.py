"""
Module for initializing core components of the application.

This module sets up and initializes the following components needed for the application:
1. **BigQueryManager:** Manages interactions with Google BigQuery for executing SQL queries.
2. **ChatGoogleGenerativeAI:** Provides an interface to the Gemini LLM for AI-powered
chat functionalities.
3. **Chroma Vector Store:** A persistent storage solution for document embeddings,
used in retrieval-based AI systems.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from big_query_manager import BigQueryManager

load_dotenv()

async def initialize_components():
    """
    Initializes the necessary components for the application.
    """
    # Load environment variables
    load_dotenv()

    # BigQuery configuration
    project_id = os.getenv("PROJECT_ID")
    dataset_id = os.getenv("DATASET_ID")
    bq_manager = BigQueryManager(project_id=project_id, dataset_id=dataset_id)

    # Gemini API Key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=gemini_api_key)

    # Initialize vector store
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=gemini_api_key,
        task_type="retrieval_document",
    )
    vector_store = Chroma(
        collection_name="schema_collection",
        embedding_function=embeddings,
        persist_directory="./langchain_chroma_db",
    )

    return llm, vector_store, bq_manager
