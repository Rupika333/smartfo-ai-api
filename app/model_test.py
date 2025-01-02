import streamlit as st
from langchain.chat_models import ChatOpenAI
import json

# Initialize OpenAI API (or other LLM API)
openai_api_key = '373446e8af1a462fa4d245d9a92a7697'
llm = ChatOpenAI(openai_api_key=openai_api_key)

# Define the required fields and the conversation logic
required_fields = ["Name", "Department", "Region", "PID"]

# Initialize session state to store user input and chat history
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to get chatbot response using LangChain
def get_chat_completion(messages):
    # Create a completion request using the messages (chat history)
    response = llm.chat_completions.create(
        model='gpt-4',  # You can use other models here if required
        messages=messages
    )
    return response['choices'][0]['message']['content']

# Function to display chat-like interface
def display_chat():
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**You**: {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Assistant**: {message['content']}")

# Function to collect missing fields and get chatbot response
def collect_required_fields():
    missing_fields = [field for field in required_fields if field not in st.session_state.user_data]
    
    if missing_fields:
        # Ask for the first missing field
        field_to_ask = missing_fields[0]
        user_input = st.text_input(f"Please provide your {field_to_ask}:")
        
        if user_input:
            st.session_state.user_data[field_to_ask] = user_input
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.success(f"Got your {field_to_ask}!")
            
            # Prepare messages with conversation history
            messages = [{"role": "system", "content": "You are a helpful assistant collecting details from the user."}]
            for message in st.session_state.chat_history:
                messages.append(message)
            
            # Generate a conversational response from the chatbot
            assistant_response = get_chat_completion(messages)
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        else:
            st.warning(f"Please provide your {field_to_ask}.")
    else:
        st.success("All required fields are provided!")
        st.write(st.session_state.user_data)

# Streamlit UI to run the chatbot
st.title("Conversational Chatbot to Collect Information")

# Display the chat history (like WhatsApp chat)
display_chat()

# Collect user information until all fields are provided
collect_required_fields()

# Button to reset the session (optional)
if st.button("Reset"):
    st.session_state.user_data.clear()
    st.session_state.chat_history.clear()
    st.experimental_rerun()
