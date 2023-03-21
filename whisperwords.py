# from config import MEDIA_DIR
# from db import ENGINE, Media, Segment, Transcript

import os
import re

import openai
import streamlit as st

import streamlit as st

openai.api_key = st.secrets['OPENAI_API_KEY']


# upload a file from local to streamlit and save it to a directory called uploads

def id_questions(text):
    pattern = r"([^.!?]*\?)"
    new_text = re.sub(pattern, r"\n\n\1<b>", text)
    new_text = new_text.replace("?", "?\n\n,</b>")
    return new_text


def upload_file():
    file = st.file_uploader("Upload file")
    # If the user uploads a file
    if file is not None:
        if not os.path.exists("uploads"):
            os.mkdir("uploads")
        # Get the file name
        filename = file.name
        # Create a file path to save the uploaded file
        filepath = os.path.join("uploads", filename)
        # Write the file to the uploads folder
        with open(filepath, "wb") as f:
            f.write(file.getbuffer())
        # Print a success message
        st.success(f"File saved to {filepath}")
        return filepath


def _transcribe(audio_path: str):
    """Transcribe the audio file using whisper"""
    if audio_path:
        audio_file = open(audio_path, "rb")
        transcript = openai.Audio.translate("whisper-1", audio_file,
                                            response="verbose_json",
                                            temperature=0.5, )
        text = id_questions(transcript['text'])
        st.markdown(text)
        return transcript


if __name__ == "__main__":
    st.title("Whisper UI")
    filepath = upload_file()

    _transcribe(filepath)
