import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_chroma import Chroma
from custom_prompts import SYSTEM_PROMPT
from big_query_manager import BigQueryManager
import regex as re
import pandas as pd

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

PROJECT_ID = os.getenv('PROJECT_ID')
DATASET_ID = os.getenv("DATASET_ID")
bq_manager = BigQueryManager(project_id=PROJECT_ID, dataset_id=DATASET_ID)

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

def generate_initial_response(user_input, llm, vector_store, k=3):
    """Generate the initial response from the LLM based on user input and schema context."""
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
        # print("Initial Response generated:")
        # print(response.content.strip())

        return response.content.strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return "An error occurred while processing your request. Please try again later."

def trigger_fallback_logic(user_input, llm, context, human_message):
    """Trigger the fallback logic when the initial response cannot generate a SQL query."""
    try:
        print("Triggering fallback logic")

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
        print("Refined Response generated:")
        print(refined_response.content.strip())
        
        # Return refined response (this means no further processing or BigQuery execution)
        return refined_response.content.strip()

    except Exception as e:
        print(f"Error triggering fallback logic: {e}")
        return "An error occurred while processing the fallback logic. Please try again later."
    
def get_response(user_input, llm, vector_store, k=3):
    """Main function to get response and handle fallback logic if needed."""
    try:
        # Generate initial response
        response = generate_initial_response(user_input, llm, vector_store, k)

        if "I cannot generate a SQL query for this request based on the provided schema." in response:
            # If the response indicates fallback is needed, trigger fallback logic
            print("Fallback triggered.")
            # Retrieve schema context from ChromaDB again to pass to the fallback logic
            results = vector_store.similarity_search(user_input, k=k)
            flattened_context = [item.page_content for item in results]
            context = "\n".join(flattened_context)
            # Call the fallback logic
            return trigger_fallback_logic(user_input, llm, context, HumanMessage(content=user_input))
        
        # Return the initial response if successful (i.e., SQL query generation)
        return response

    except Exception as e:
        print(f"Error in get_response: {e}")
        return "An error occurred while processing your request. Please try again later."
    
def refine_response(response):
    # Remove the 'sql' tag if it exists at the start of the response
    response = re.sub(r"^sql\s*", "", response)

    # Remove triple backticks or single backticks at both ends
    response = re.sub(r"^```(.*)```$", r"\1", response, flags=re.DOTALL)
    response = re.sub(r"^`(.*)`$", r"\1", response, flags=re.DOTALL)

    # Strip any leading or trailing whitespace
    return response.strip()

def get_data(bq_manager, reg):
    # Execute the BigQuery query
    data = bq_manager.execute_query(reg)
    return data

def data_handler(data: pd.DataFrame, user_input, llm):
    # Convert DataFrame to JSON (simplified)
    data_json = data.to_json(orient='records', lines=False)

    # New and improved system prompt
    improved_prompt = f"""
    You are an expert data analysis assistant tasked with analyzing the dataset provided in JSON format and summarizing it based on the user's query.

    ### Instructions:
    1. The dataset you receive has already been preprocessed to directly align with the user's query, so it contains only the relevant information.
    2. Your job is to:
        - Directly address the user's query using the provided dataset.
        - Provide insights, trends, or patterns based on the data.
        - If the dataset has already been filtered or processed, acknowledge that and focus only on summarizing it in response to the query.
    3. If the dataset does not contain enough information to fully answer the user's query, mention the limitation and suggest how the query could be modified for more complete results.

    ### Examples:

    **Example 1: List the total number of students.**  
    Dataset: [9]  
    *System Hint*: The dataset contains only the number of students, so there is no need to count or process it further. Just provide the number directly.  
    Response: "There are 9 students in the dataset."

    **Example 2: List the students who have a warning count greater than 0.**  
    Dataset:
    'Name': [ 'Rachel White', 'Olivia Harris', 'George Carter', 'Diana Green', 'Bob Smith', 'Karen Black', 'Ian Wright', 'Mia Davis', 'Samuel King' ]

    *System Hint*: The dataset only includes the names of students who have a warning count greater than 0. The data has already been filtered, so you do not need to perform any additional checks on the warning count. Just list the names of the students as requested.  
    Response: "The students with a warning count greater than 0 are: Rachel White, Olivia Harris, George Carter, Diana Green, Bob Smith, Karen Black, Ian Wright, Mia Davis, Samuel King."

    ### Your Task:
    - Given the dataset: {data_json}
    - And the user's query: {user_input}
    Please summarize the data accordingly.
    """

    # Call LLM to get a refined response based on the dataset and user query
    result = llm.invoke(improved_prompt)
    return result.content.strip()

# Example usage
if __name__ == "__main__":
    user_query = "List the names of students who have a WarningCount greater than 0"
    
    # Step 1: Get initial response from LLM (generate SQL query or error message)
    initial_response = generate_initial_response(user_query, llm, vector_store, k=5)
    # print("Initial Response from LLM:")
    print(initial_response)

    # Step 2: Check if initial response indicates fallback is needed
    if "I cannot generate a SQL query for this request based on the provided schema." in initial_response:
        print("Fallback response generated.")
        # Trigger fallback logic if SQL generation is not possible
        fallback_response = trigger_fallback_logic(user_query, llm, "", HumanMessage(content=user_query))
        # print("Fallback Response:")
        print(fallback_response)
    else:
        # print("SQL query generated:")
        # Proceed with further steps if SQL query is generated

        # Step 3: Refine the response to remove backticks if any
        refined_response = refine_response(initial_response)
        print("Refined Response:")
        print(refined_response)

        # Step 4: Get data from BigQuery (based on the refined response, which is the SQL query)
        data = get_data(bq_manager, refined_response)
        print("Data retrieved from BigQuery:")
        print(data)

        # Step 5: Handle and summarize the data (if data exists)
        if isinstance(data, pd.DataFrame) and not data.empty:
            summary = data_handler(data, user_query, llm)
            print("Data Summary:")
            print(summary)
        else:
            print("No relevant data found.")