import re

# Function to divide schema into chunks and save to a new file
def divide_schema_into_chunks(file_path, output_file_path):
    try:
        # Read the schema content from the input file
        with open(file_path, 'r') as f:
            schema_content = f.read()

        # Define a regex pattern to match table headers (assuming the tables start with "Table Name")
        table_pattern = r"(Table Name: [\w_]+(?:[\s\w_]+)*)\n(.*?)(?=Table Name:|\Z)"
        
        # Find all tables using the pattern
        tables = re.findall(table_pattern, schema_content, re.DOTALL)

        # Initialize a list to store the chunks
        table_chunks = []

        # Process each table
        for table_name, table_content in tables:
            # Split the content into columns and description
            table_description = table_content.split("Columns:")[0].strip()
            column_content = table_content.split("Columns:")[1].strip()

            # Extract the column details
            column_pattern = r"Column:\s([\w_]+),\sType:\s([\w_]+),\sMode:\s([\w_]+),\sDescription:\s(.*?)(?=\nColumn:|\Z)"
            columns = re.findall(column_pattern, column_content)

            # Prepare the chunks for the table description and columns
            table_chunks.append({
                "table_name": table_name,
                "description": table_description,
                "columns": columns
            })

        # Save the chunks to the output file
        with open(output_file_path, 'w') as out_file:
            for table_chunk in table_chunks:
                out_file.write(f"Table Name: {table_chunk['table_name']}\n")
                out_file.write(f"Description: {table_chunk['description']}\n")
                for col in table_chunk['columns']:
                    out_file.write(f"Column: {col[0]}, Type: {col[1]}, Mode: {col[2]}, Description: {col[3]}\n")
                out_file.write("-" * 50 + "\n")

        print(f"Schema data saved to {output_file_path}")

    except Exception as e:
        print(f"Error processing schema: {e}")