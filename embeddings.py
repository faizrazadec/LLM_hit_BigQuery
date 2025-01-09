import os
import uuid
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import chromadb
from chromadb.config import Settings

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
chroma_client = chromadb.PersistentClient(
    path="./chroma_db", 
    settings=Settings(anonymized_telemetry=False))

collection = chroma_client.create_collection(name="my_collection")

# Initialize embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)

# Read the schema from schema.txt
def read_schema(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    return lines

# Generate embeddings and store in ChromaDB
def store_schema_embeddings(schema_file):
    schema_lines = read_schema(schema_file)

    for line in schema_lines:
        # Skip empty lines or lines without meaningful content
        if not line.strip():
            continue

        # Create embeddings for each line (e.g., table/column description)
        try:
            embedding = embeddings.embed_query(line)
        except Exception as e:
            print(f"Error generating embedding for line: {line.strip()}. Error: {e}")
            continue
        # Generate a unique ID for each line
        unique_id = str(uuid.uuid4())

        # Store the embedding in ChromaDB
        try:
            collection.add(
                ids=[unique_id],  # Use a unique ID
                documents=[line],  # Store the schema description text
                embeddings=[embedding]  # Store the embedding vector
            )
            print(f"Stored embedding for: {line.strip()}")
        except Exception as e:
            print(f"Error storing embedding for line: {line.strip()}. Error: {e}")