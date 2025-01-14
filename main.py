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

def get_response(user_input, llm, vector_store, k=3):
    try:
        # Retrieve relevant schema information from ChromaDB
        results = vector_store.similarity_search(user_input, k=k)

        # Flatten the list of results to extract content
        flattened_context = [item.page_content for item in results]

        # Concatenate retrieved schema context
        context = "\n".join(flattened_context)

        # Initial system prompt and message
        system_message = SystemMessage(content=f"{SYSTEM_PROMPT}\nSchema Context:\n{context}")
        human_message = HumanMessage(content=user_input)

        # Generate initial response
        response = llm.invoke([system_message, human_message])

        # Debugging output
        print("Initial Response:", response.content)

        if "I cannot generate a SQL query for this request based on the provided schema." in response.content.strip():
            print("Triggering fallback logic with SYSTEM_PROMPT_2")

            # Fallback system prompt
            SYSTEM_PROMPT_2 = f"""
            You are an assistant tasked with refining natural language queries for better SQL generation. 

            **IMPORTANT INSTRUCTIONS:**
            1. **You are strictly bounded NOT to generate or include any SQL queries under any circumstances.**
            2. Your task is to:
            - Explain why the user's original query could not generate a valid SQL query.
            - You are strictly bound to return at least 3 refined natural language prompts that address the issues in the original query.
            3. Your response must strictly contain:
            - A short explanation of why the original query failed.
            - Refined natural language prompts, formatted as bullet points.
            4. **Do NOT explain how to write SQL queries.**
            5. **Do NOT mention SQL query structures, examples, or any SQL-related code in your response.**

            **Here is the user's query that needs refinement:**  
            {user_input}

            **Schema Context:**  
            {context}

            **Response Format:**
            1. **Why the Query Failed:**  
            - [Brief explanation of failure]

            2. **Refined Prompts:**  
            - Refined Prompt 1: [First refined query]  
            - Refined Prompt 2: [Second refined query]  
            - Refined Prompt 3: [Third refined query]  

            **Strict Reminder:**  
            - You are strictly bound NOT to generate or include SQL queries in your response.
            - You are strictly bound NOT to NOT discuss SQL syntax, query examples, or anything related to SQL query writing.
            - You are strictly bound not to **Suggested SQL Query:**
            - You are strictly bound not to return Improved SQL (based on Refined Prompt)
            """

            # Use fallback system prompt
            refined_system_message = SystemMessage(content=SYSTEM_PROMPT_2)
            refined_response = llm.invoke([refined_system_message, human_message])

            # Debugging output
            print("Refined Response:", refined_response.content)
            return refined_response.content.strip()
        else:
            # Return the initial response if successful
            return response.content.strip()

    except Exception as e:
        print(f"Error generating response: {e}")
        return "An error occurred while processing your request. Please try again later."


# Get response using context from ChromaDB
# def get_response(user_input, k=3):
#     try:
#         # Retrieve relevant schema information from ChromaDB
#         results = vector_store.similarity_search(user_input, k=k)

#         # Flatten the list of results to extract content
#         flattened_context = [item.page_content for item in results]

#         # Concatenate retrieved schema context
#         context = "\n".join(flattened_context)

#         # Use SystemMessage and HumanMessage
#         system_message = SystemMessage(content=f"{SYSTEM_PROMPT}\nSchema Context:\n{context}")
#         human_message = HumanMessage(content=user_input)

#         # Generate response
#         response = llm.invoke([system_message, human_message])

#         SYSTEM_PROMPT_2 = f"""
#         The previous attempt to generate a SQL query was unsuccessful. Now, you are tasked with helping the user refine the prompt for a better SQL generation.
#         Also tell the user why the {user_input} was wrong and couldn't generate the sql query.
        
#         Here is the user's query that needs refinement: 
#         {user_input}

#         Based on the schema context provided below, suggest a better version of the user's query that will lead to a more accurate SQL query generation. 

#         Schema Context:
#         {context}

#         Your goal is to improve the user's query so it can be better understood by the model to generate the correct SQL query. Provide suggestions, clarifications, or ask for more details if needed to ensure the SQL query is generated correctly.
#         """

#         if response.content == 'I cannot generate a SQL query for this request based on the provided schema.':
#             system_message = SystemMessage(content=f"{SYSTEM_PROMPT_2}")
#             response_2 = llm.invoke([system_message, human_message])
#             return response_2.content
#         else:
#             return response.content

#     except Exception as e:
#         print(f"Error generating response: {e}")
#         return None

# Example usage
if __name__ == "__main__":
    user_query = "provide me the student names from the course computer science'"
    response = get_response(user_query, llm, vector_store, k=5)
    
    if response:
        print("Response:", response)
    else:
        print("No response generated.")
