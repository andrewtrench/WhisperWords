# from config import MEDIA_DIR
# from db import ENGINE, Media, Segment, Transcript

import os
import re
from pydub import AudioSegment
import openai
import streamlit as st
import ffmpeg
import streamlit as st

openai.api_key = st.secrets['OPENAI_API_KEY']


# upload a file from local to streamlit and save it to a directory called uploads

def id_questions(text):
    pattern = r"([^.!?]*\?)"
    new_text = re.sub(pattern, r"\n\n\1</strong>", text)
    new_text = new_text.replace("?", "?\n\n<strong>")
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
        # if file greater than 24mb split it into 1mb chunks using ffmpeg
        filesize = os.path.getsize(filepath)/(1024*1024)
        if filesize > 24:
            os.mkdir("chunks")
            chunk_size = 1024*1024
            input_file_size = os.path.getsize(filepath)
            audio = AudioSegment.from_file(filepath)
            for i,chunk in enumerate(chunks):
                chunk.export(f"chunks/{filename}_{i}.wav", format="wav")
            filepath = os.listdir("chunks")
            return filepath

        # Print a success message
        st.success(f"File saved to {filepath}")
        return filepath


def _transcribe(audio_path: str):
    """Transcribe the audio file using whisper"""
    if type(audio_path) == list:
        for audio in audio_path:
            audio_file = open(audio_path, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file,
                                                 response="verbose_json",
                                                 temperature=0.5, )
            text = id_questions(transcript['text'])
            st.markdown(text, unsafe_allow_html=True)

    else:
        audio_file = open(audio_path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file,
                                            response="verbose_json",
                                            temperature=0.5, )
        text = id_questions(transcript['text'])
        st.markdown(text,unsafe_allow_html=True)


if __name__ == "__main__":
    st.title("Whisper UI")
    filepath = upload_file()
    transcribe_button = st.button("Transcribe")
    if transcribe_button:
        _transcribe(filepath)
