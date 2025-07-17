# Import necessary libraries
import pandas as pd
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Define the path to the FAQ CSV data file
faqs_path = Path(__file__).parent / "resources/faq_data.csv"

# Initialize ChromaDB client
chroma_client = chromadb.Client()

# Define collection name for storing FAQ embeddings
collection_name_faq = 'faqs'

# Initialize Groq LLM client
groq_client = Groq()

# Initialize sentence embedding function using a pre-trained model
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Define function to ingest FAQ data into ChromaDB
def ingest_faq_data(path):
    # Check if the collection already exists
    if collection_name_faq not in [c.name for c in chroma_client.list_collections()]:
        print("Ingesting faq data into Chromadb...")

        # Create new collection with the specified embedding function
        collection = chroma_client.get_or_create_collection(
            name=collection_name_faq,
            embedding_function=ef
        )

        # Read FAQ data from CSV file
        df = pd.read_csv(path)

        # Extract list of questions and corresponding answers
        docs = df['question'].to_list()
        metadata = [{'answer': ans} for ans in df['answer'].to_list()]

        # Generate unique IDs for each document
        ids = [f"id_{i}" for i in range(len(docs))]

        # Add data to the ChromaDB collection
        collection.add(
            documents=docs,
            metadatas=metadata,
            ids=ids
        )
        print(f"FAQ data successfully ingested into Chroma collection {collection_name_faq}")
    else:
        print(f"Collection {collection_name_faq} already exists")


# Define function to retrieve the most relevant Q&A pairs based on query
def get_relevant_qa(query):
    # Fetch the existing FAQ collection
    collection = chroma_client.get_collection(collection_name_faq)

    # Perform similarity search on query
    result = collection.query(
        query_texts=[query],
        n_results=2
    )
    return result


# Define function to handle full FAQ retrieval and answer generation pipeline
def faq_chain(query):
    # Retrieve top relevant Q&A entries
    result = get_relevant_qa(query)

    # Extract context (answers) from metadata
    context = ''.join([r.get('answer') for r in result['metadatas'][0]])

    # Generate and return final answer using LLM
    answer = generate_answer(query, context)
    return answer


# Define function to send query and context to LLM and receive an answer
def generate_answer(query, context):
    # Construct prompt for LLM with clear instruction to avoid hallucination
    prompt = f'''
    Given the question and context below, generate the answer based on the context only.
    If you don't find the answer inside the context then say "I don't know".
    Do not make things up.

    QUESTION: {query}

    CONTEXT: {context}
    '''

    # Make chat completion request to Groq LLM using model defined in environment variables
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=os.environ['GROQ_MODEL'],
    )

    # Return the generated message content
    return chat_completion.choices[0].message.content


# Execute ingestion and querying when script is run directly
if __name__ == "__main__":
    # Ingest FAQ data into ChromaDB
    ingest_faq_data(faqs_path)

    # Sample query for testing the FAQ chain
    query = "Do you take cash as a payment option?"

    # Get generated answer from pipeline
    answer = faq_chain(query)
    print(answer)
