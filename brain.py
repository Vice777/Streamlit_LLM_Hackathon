import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,    
    HumanMessagePromptTemplate,
)
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st

OPENAI_API = os.getenv("OPENAI_API")

template = (""" 
    I'm preparing notes from a video titled "{title}". I need you to
    act as an expert professor and provide me with comprehensive and well-structured 
    notes from the following text. 

    Here is the tex:
    {transcription}

    Condition: Please ensure the notes cover the following topics: ALL THE TOPICS.
    Also do make sure you are printing everything in MARKDOWN. 
    Strictly do not print anything else other than the notes.
    """)

def video_title(url):
        yt = YouTube(url)
        return yt.title

def text_extractor(url):
    try:
        video_id = url.split("?v=")[1]
    except IndexError:
        video_id = url.split("/")[-1]

    try:
        response = YouTubeTranscriptApi.get_transcript(video_id)
        final = "".join([i['text'] for i in response])

        if len(final) > 5:
            return final
    except ConnectionError as e:
         st.error(e)

@st.cache_data
def notes_generator(url):
    chat = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API)

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    gpt_response = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    
    response = chat(
        gpt_response.format_prompt(
            title=video_title(url), transcription=text_extractor(url), text=url
        ).to_messages()
    )

    return response.content