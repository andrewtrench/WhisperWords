# from config import MEDIA_DIR
# from db import ENGINE, Media, Segment, Transcript

import os

import openai
import streamlit as st
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# global variables


# upload a file from local to streamlit and save it to a directory called uploads

def upload_file():
    file = st.file_uploader("Upload file")
    # If the user uploads a file
    if file is not None:
        # Get the file name
        filename = file.name
        # Create a file path to save the uploaded file
        filepath = os.path.join("uploads", filename)
        # Write the file to the uploads folder
        with open(filepath, "wb") as f:
            f.write(file.getbuffer())
        # Print a success message
        st.success(f"File saved to {filepath}")


def _transcribe(self, audio_path: str):
    """Transcribe the audio file using whisper"""
    audio_file = open(audio_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file,
                                         response="verbose_json",
                                         temperature=0.5, )
    st.write(transcript)
    return transcript

if __name__ == "__main__":
    st.title("Whisper UI")
    upload_file()
    _transcribe()
