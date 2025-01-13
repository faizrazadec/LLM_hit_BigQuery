from langchain_core.messages import SystemMessage, HumanMessage
from custom_prompts import SYSTEM_PROMPT

def get_response(user_input, llm, vector_store, k=3):
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
            system_message = SystemMessage(content=SYSTEM_PROMPT_2)
            response_2 = llm.invoke([system_message, human_message])
            return response_2.content
        else:
            return response.content
            
    except Exception as e:
        return f"Error generating response: {str(e)}"
