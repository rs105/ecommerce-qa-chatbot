# Import necessary modules
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq LLM client
groq_client = Groq()

# Define a function to interact with the LLM for small talk
def talk(query):
    # Create a chat completion request using the provided query and system instructions
    completion = groq_client.chat.completions.create(
        model=os.environ['GROQ_MODEL'],  # Use the model name from environment variables
        messages=[
            {
                'role': 'system',
                'content': ( # Role assigned to the LLM for conversational topics
                    "You are a friendly and conversational assistant designed for small talk. "
                    "You can answer questions about the weather, your name, your purpose, and more. "
                    "If you don’t know something, just say 'I don’t know' instead of making it up."
                )
            },
            {
                'role': 'user',
                'content': query  # User's input question or message
            }
        ]
    )

    # Return the LLM's response content
    return completion.choices[0].message.content
