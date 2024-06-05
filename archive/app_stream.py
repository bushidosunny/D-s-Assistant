import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from streamlit_float import float_css_helper

from langchain_core.messages import HumanMessage, AIMessage
from prompts import *
from archive.utils import *

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
        


def handle_user_input_container():
    input_container = st.container()
    input_container.float(float_css_helper(bottom="50px"))
    with input_container:
        user_question = st.chat_input("How may I help you?", key="widget2")
        if user_question:
            handle_user_input(user_question)


def display_chat_history():
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            avatar_url = message.get("avatar", user_avatar_url)
            with st.chat_message(message["role"], avatar=avatar_url):
                st.markdown(message["content"], unsafe_allow_html=True)

def process_queries():
    if st.session_state["user_question"]:
        handle_user_input(st.session_state["user_question"])

def create_new_thread():
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.chat_history = []
    st.rerun()

def generate_response_stream(stream):
    for response in stream:
        if response.event == 'thread.message.delta':
            for delta in response.data.delta.content:
                if delta.type == 'text':
                    yield delta.text.value

def handle_user_input(user_question):
    if user_question is not None and user_question != "":
        st.session_state.chat_history.append(HumanMessage(user_question))

        with st.chat_message("user"):
            st.markdwon(user_question)
    
    
    
    
    
    client.beta.threads.messages.create(thread_id=st.session_state.thread_id, role="user", content=user_question)
    
    with client.beta.threads.runs.stream(thread_id=st.session_state.thread_id, assistant_id=st.session_state.assistant_id) as stream:
        assistant_response = "".join(generate_response_stream(stream))
        
    specialist_avatar = specialist_id_caption[st.session_state.specialist]["avatar"]
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response, "avatar": specialist_avatar})

def main():
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        
    initialize_session_state()
    display_header()
    #handle_user_input_container()
    process_queries()
    display_chat_history()

if __name__ == '__main__':
    main()