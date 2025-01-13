import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_chroma import Chroma
from custom_prompts import SYSTEM_PROMPT

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY,
    task_type="retrieval_document"
)
# Initialize the LLM model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    api_key=GEMINI_API_KEY
)
# Initialize the Chroma vector store (assumed to be stored in './chroma_langchain_db')
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db"  # Path where Chroma DB is persisted
)

# Get response using context from ChromaDB
def get_response(user_input, k=3):
    try:
        # Retrieve relevant schema information from ChromaDB
        results = vector_store.similarity_search(user_input, k=k)

        # Flatten the list of results to extract content
        flattened_context = [item.page_content for item in results]

        # Concatenate retrieved schema context
        context = "\n".join(flattened_context)

        # Use SystemMessage and HumanMessage
        system_message = SystemMessage(content=f"{SYSTEM_PROMPT}\nSchema Context:\n{context}")
        human_message = HumanMessage(content=user_input)

        # Generate response
        response = llm.invoke([system_message, human_message])

        SYSTEM_PROMPT_2 = f"""
        The previous attempt to generate a SQL query was unsuccessful. Now, you are tasked with helping the user refine the prompt for a better SQL generation.
        Also tell the user why the {user_input} was wrong and couldn't generate the sql query.
        
        Here is the user's query that needs refinement: 
        {user_input}

        Based on the schema context provided below, suggest a better version of the user's query that will lead to a more accurate SQL query generation. 

        Schema Context:
        {context}

        Your goal is to improve the user's query so it can be better understood by the model to generate the correct SQL query. Provide suggestions, clarifications, or ask for more details if needed to ensure the SQL query is generated correctly.
        """

        if response.content == 'I cannot generate a SQL query for this request based on the provided schema.':
            system_message = SystemMessage(content=f"{SYSTEM_PROMPT_2}")
            response_2 = llm.invoke([system_message, human_message])
            return response_2.content
        else:
            return response.content

    except Exception as e:
        print(f"Error generating response: {e}")
        return None

# Example usage
# if __name__ == "__main__":
#     user_query = "Provide me the names of the students that have paid their challanform and are in semester fall 2025?"
#     response = get_response(user_query)
    
#     if response:
#         print("Response:", response)
#     else:
        # print("No response generated.")
