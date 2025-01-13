from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY,
    task_type="retrieval_document"
)

# Initialize the Chroma vector store (assumed to be stored in './chroma_langchain_db')
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db"  # Path where Chroma DB is persisted
)

# Function to test retrieval
def test_retrieval(query, k=3):
    try:
        # Perform similarity search
        results = vector_store.similarity_search(query, k=k)
        
        # Print the results
        if results:
            print(f"Top {k} results for the query: '{query}'")
            for idx, res in enumerate(results):
                print(f"{idx + 1}. {res.page_content} [{res.metadata}]")
        else:
            print("No results found.")
    
    except Exception as e:
        print(f"Error during retrieval: {e}")

if __name__ == "__main__":
    query = 'Provide me the names of the students that have paid their challanform and are in semester fall 2025?'
    test_retrieval(query)
