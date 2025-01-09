import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
import chromadb
from chromadb.config import Settings
from custom_prompts import SYSTEM_PROMPT

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize ChromaDB client and collection
chroma_client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(anonymized_telemetry=False)
)
collection = chroma_client.get_or_create_collection(name="my_collection")

# Initialize embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)
# Initialize the LLM model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    api_key=GEMINI_API_KEY
)

# Get response using context from ChromaDB
def get_response(user_input):
    # Embed user query
    query_embedding = embeddings.embed_query(user_input)

    # Retrieve relevant schema information from ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5  # Adjust number of results as needed
    )

    # Flatten the list of lists in results["documents"]
    flattened_context = [item for sublist in results["documents"] for item in sublist]

    # Concatenate retrieved schema context
    context = "\n".join(flattened_context)

    # Use SystemMessage and HumanMessage
    system_message = SystemMessage(content=f"{SYSTEM_PROMPT}\nSchema Context:\n{context}")
    human_message = HumanMessage(content=user_input)

    # Generate response
    try:
        response = llm.invoke([system_message, human_message])
        return response.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Example user query
    user_query = "How many tasks were completed in December 2024?"
    response = get_response(user_query)
    
    if response:
        print(response)
    else:
        print("No response generated.")
