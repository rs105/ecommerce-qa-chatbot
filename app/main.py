# Import Streamlit for UI, router for intent classification,
# faq, sql, and smalltalk modules for handling respective queries
import streamlit as st
from router import router
from faq import ingest_faq_data, faq_chain
from pathlib import Path
from sql import sql_chain
from smalltalk import talk

# Define path to FAQ CSV data file (relative to this script)
faqs_path = Path(__file__).parent / "resources/faq_data.csv"

# Ingest FAQ data into vector database at app startup to prepare for queries
ingest_faq_data(faqs_path)


# Define main routing logic function that takes user query and routes it
def ask(query):
    # Use semantic router to identify intent route based on the query
    route_result = router(query)
    if route_result is None:
        # Return fallback message if no matching route found
        return "Sorry, I didn't understand that."

    # Extract the name of the identified route (intent category)
    route = route_result.name

    # Dispatch query to the corresponding handler function based on route
    if route == 'faq':
        # Handle FAQ queries by fetching relevant answers using faq_chain
        return faq_chain(query)
    elif route == 'sql':
        # Handle product-related queries using SQL-based search chain
        return sql_chain(query)
    elif route == 'small-talk':
        # Handle casual conversation queries via smalltalk LLM function
        return talk(query)
    else:
        # Provide placeholder response for any unimplemented routes
        return f"Route `{route}` not implemented yet."


# Streamlit UI setup starts here

# Set the app title shown at the top of the page
st.title("🛒 E-Commerce Bot")

# Create a chat input box for the user to type queries
query = st.chat_input("Write your query")

# Initialize chat history storage in session state if it doesn't exist yet
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Render the chat history messages in the UI
for message in st.session_state["messages"]:
    # Use Streamlit's chat_message container to style each message by role
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Process the new user input query if present
if query:
    # Display the new user message in the chat UI
    with st.chat_message("user"):
        st.markdown(query)
    # Append the user message to the session state history
    st.session_state["messages"].append({"role": "user", "content": query})

    # Call the routing logic to generate a response to the query
    response = ask(query)

    # Display the assistant's response in the chat UI
    with st.chat_message("assistant"):
        st.markdown(response)
    # Append the assistant's response to the session state history
    st.session_state["messages"].append({"role": "assistant", "content": response})
