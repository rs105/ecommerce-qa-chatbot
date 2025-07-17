import sqlite3
import pandas as pd
from groq import Groq
import os
import re
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the Groq model name from environment variables
GROQ_MODEL = os.getenv('GROQ_MODEL')

# Define path to the SQLite database file
db_path = Path(__file__).parent / "db.sqlite"

# Initialize Groq client for calling the LLM
client_sql = Groq()

# Define the system prompt instructing the LLM on how to generate SQL queries
sql_prompt = """You are an expert in understanding the database schema and generating SQL queries for a natural language question asked
pertaining to the data you have. The schema is provided in the schema tags. 
<schema> 
table: product 

fields: 
product_link - string (hyperlink to product)	
title - string (name of the product)	
brand - string (brand of the product)	
price - integer (price of the product in Indian Rupees)	
discount - float (discount on the product. 10 percent discount is represented as 0.1, 20 percent as 0.2, and such.)	
avg_rating - float (average rating of the product. Range 0-5, 5 is the highest.)	
total_ratings - integer (total number of ratings for the product)

</schema>
Make sure whenever you try to search for the brand name, the name can be in any case. 
So, make sure to use %LIKE% to find the brand in condition. Never use "ILIKE". 
Create a single SQL query for the question provided. 
The query should have all the fields in SELECT clause (i.e. SELECT *)

Just the SQL query is needed, nothing more. Always provide the SQL in between the <SQL></SQL> tags.
"""

# Define function to generate SQL query from natural language question using LLM
def generate_sql_query(question):
    # Send chat completion request with system prompt and user question
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": sql_prompt,  # SQL generation instructions and schema
            },
            {
                "role": "user",
                "content": question,  # User's natural language question
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0.2,  # Low temperature to reduce creativity in SQL generation
        max_tokens=1024
    )

    # Return the full text response (includes <SQL> tags with the query)
    return chat_completion.choices[0].message.content

# Define function to run a SQL query against the SQLite database and return results as DataFrame
def run_query(query):
    # Validate the generated query starts with SELECT to prevent unwanted queries
    if query.strip().upper().startswith('SELECT'):
        # Connect to SQLite DB using a context manager
        with sqlite3.connect(db_path) as conn:
            # Execute the SQL query and fetch results into a pandas DataFrame
            df = pd.read_sql_query(query, conn)
            return df

# Main function chaining SQL query generation, execution, and answer generation
def sql_chain(question):
    # Generate SQL query string from the question using LLM
    sql_query = generate_sql_query(question)

    # Use regex to extract SQL query text wrapped inside <SQL> tags
    pattern = "<SQL>(.*?)</SQL>"
    matches = re.findall(pattern, sql_query, re.DOTALL)  # DOTALL to include newlines

    # Handle case where no valid SQL query is found in LLM response
    if len(matches) == 0:
        return "Sorry, LLM is not able to generate a query for your question"

    # Print the extracted SQL query for debugging or logging
    print("SQL QUERY:", matches[0].strip())

    # Run the extracted SQL query against the database
    response = run_query(matches[0].strip())

    # Handle case where SQL query execution fails or returns nothing
    if response is None:
        return "Sorry, there was a problem executing your query"

    # Convert the query result DataFrame to a list of dictionaries (records)
    context = response.to_dict(orient='records')

    # Pass the question and query result data to a comprehension function to generate a natural language answer
    answer = data_comprehension(question, context)
    return answer

# Define system prompt for LLM to generate human-friendly answers based on query results
comprehension_prompt = """
You are an expert in understanding the context of the question and replying based on the data pertaining to the question provided. 
You will be provided with Question: and Data:. The data will be in the form of an array or a dataframe or dict. 
Reply based on only the data provided as Data for answering the question asked as Question. 
Do not write anything like 'Based on the data' or any other technical words. Just a plain simple natural language response.
The Data would always be in context to the question asked. 
For example is the question is “What is the average rating?” and data is “4.3”, then answer should be “The average rating for the product is 4.3”. 
So make sure the response is curated with the question and data. 
Make sure to note the column names to have some context, if needed, for your response.
There can also be cases where you are given an entire dataframe in the Data: field. 
Always remember that the data field contains the answer of the question asked. 
All you need to do is to always reply in the following format when asked about a product: 
Product title, price in indian rupees, discount, and rating, and then product link. 
Take care that all the products are listed in list format, one line after the other. Not as a paragraph.
For example:
1. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
2. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
3. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
"""

# Define function to generate natural language answer from data and question using LLM
def data_comprehension(question, context):
    # Call LLM with system prompt and user content combining question and query result data
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": comprehension_prompt,
            },
            {
                "role": "user",
                "content": f"QUESTION: {question} DATA: {context}",
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0.2,  # Low temperature for consistent answers
        # max_tokens=1024  # Optional token limit
    )

    # Return the generated natural language answer
    return chat_completion.choices[0].message.content

# Main block for testing
if __name__ == '__main__':
    # Example question for testing the full SQL question-answer pipeline
    question = "Give me PUMA shoes with rating higher than 4.5 and more than 30% discount"

    # Get the final natural language answer from the chain
    answer = sql_chain(question)

    # Print the answer to console
    print(answer)

    # Uncomment below to test running a direct SQL query
    # query = "SELECT * from product where brand LIKE '%nike%'"
    # df = run_query(query)
    # pass
