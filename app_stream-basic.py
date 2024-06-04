import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.messages import HumanMessage, AIMessage
from prompts import *
from utils import *

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("API Key not found! Please check your environment variables.")

client = OpenAI(api_key=api_key)

# Avatar URLs
user_avatar_url = "https://api.dicebear.com/8.x/pixel-art/svg?seed=Simon&beardProbability=0&eyesColor=876658&glassesProbability=0&hairColor=28150a&skinColor=cb9e6e"

specialist_id_caption = {
    "Diana's assistant": {
        "assistant_id": "asst_d1mG01RGb8UEA1Anue9QgkQF",
        "caption": "role is multifaceted, encompassing elements of an assistant, AI journal, therapist, friend, and counselor.",
        "avatar": "https://api.dicebear.com/8.x/bottts/svg?seed=Lucky"
    },
    "Mindfulness Teacher": {
        "assistant_id": "asst_bnFm27eqedaYK9Ulekh8Yjd9",
        "caption": "Goes Deep",
        "avatar": "https://cdn.pixabay.com/photo/2013/07/12/19/30/enlightenment-154910_1280.png"
    }
}

def initialize_session_state():
    primary_specialist = list(specialist_id_caption.keys())[0]
    primary_specialist_id = specialist_id_caption[primary_specialist]["assistant_id"]
    primary_specialist_avatar = specialist_id_caption[primary_specialist]["avatar"]
    state_keys_defaults = {
        "chat_history": [],
        "user_question": "",
        "json_data": {},
        "critical_actions": {},
        "sidebar_state": 1,
        "assistant_response": "",
        "specialist_input": "",
        "specialist": primary_specialist,
        "assistant_id": primary_specialist_id,
        "specialist_avatar": primary_specialist_avatar,
        "should_rerun": False        
    }
    for key, default in state_keys_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

def display_header():
    st.set_page_config(page_title="DA", page_icon="🫡")
    specialist = st.session_state.specialist
    specialist_avatar = specialist_id_caption[st.session_state.specialist]["avatar"]
    st.markdown(
            f"""
            <div style="text-align: center;">
                <h1>
                    <img src="{specialist_avatar}" alt="Avatar" style="width:60px;height:60px;border-radius:50%;">
                    Diana's Assistant
                </h1>
            </div>
            """, 
            unsafe_allow_html=True
        )

def generate_response_stream(stream):
    for response in stream:
        if response.event == 'thread.message.delta':
            for delta in response.data.delta.content:
                if delta.type == 'text':
                    yield delta.text.value


def get_response(user_question):
    client.beta.threads.messages.create(thread_id=st.session_state.thread_id, role="user", content=user_question)

    response_placeholder = st.empty()  # Placeholder for streaming response text
    response_text = ""  # To accumulate response text

    # Stream response from the assistant
    with client.beta.threads.runs.stream(thread_id=st.session_state.thread_id, assistant_id=st.session_state.assistant_id) as stream:
        for chunk in stream:
            if chunk.event == 'thread.message.delta':  # Check if it is the delta message
                for delta in chunk.data.delta.content:
                    if delta.type == 'text':
                        response_text += delta.text.value  # Append new text fragment to response text
                        response_placeholder.markdown(response_text)  # Update the placeholder with new response text as markdown

    return response_text

def display_chat_history():    
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            avatar_url = message.avatar
            with st.chat_message("user", avatar=user_avatar_url):                
                st.markdown(message.content, unsafe_allow_html=True)
        else:
            avatar_url = st.session_state.specialist_avatar
            with st.chat_message("AI", avatar=avatar_url):
                st.markdown(message.content, unsafe_allow_html=True)


def user_input():
    user_question = st.chat_input("How may I help you?")
    if user_question is not None and user_question != "":
        st.session_state.chat_history.append(HumanMessage(user_question, avatar=user_avatar_url))

        with st.chat_message("user", avatar=user_avatar_url):
            st.markdown(user_question)
        
        with st.chat_message("AI", avatar=st.session_state.specialist_avatar):
            ai_response = get_response(user_question)
            assistant_response = ai_response
        
        st.session_state.chat_history.append(AIMessage(assistant_response, avatar=st.session_state.specialist_avatar))
    


def main():
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        
    initialize_session_state()
    display_header()
    display_chat_history()
    user_input()


if __name__ == '__main__':
    main()