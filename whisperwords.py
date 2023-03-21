# from config import MEDIA_DIR
# from db import ENGINE, Media, Segment, Transcript

import os
import re
from pydub import AudioSegment
import openai
import streamlit as st
import ffmpeg
import streamlit as st
from pathlib import Path

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
        filesize = os.path.getsize(filepath) / (1024 * 1024)
        if filesize > 24:
            try:
                os.mkdir("chunks")
            except FileExistsError:
                pass
            chunk_size = 1024 * 1024

            audio = AudioSegment.from_file(filepath)
            chunks = audio[::chunk_size]
            for i, chunk in enumerate(chunks):
                chunk.export(f"chunks/{filename}_{i}.mp3", format="mp3")
            filepath = "chunks"
            return filepath

        # Print a success message
        st.success(f"File saved to {filepath}")
        return filepath


def delete_files():
    for file in os.listdir("uploads"):
        file_path = os.path.join("uploads", file)
        os.remove(file_path)
    for file in os.listdir("chunks"):
        file_path = os.path.join("chunks", file)
        os.remove(file_path)
    st.success("Files deleted from uploads and processing directories")


def _transcribe(audio_path: str):
    """Transcribe the audio file using whisper"""
    if "chunks" in audio_path:

        for audio in os.listdir(audio_path):

            audio_file = open(f"chunks/{audio}", "rb")
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
        st.markdown(text, unsafe_allow_html=True)
    delete_files()


if __name__ == "__main__":
    st.title("Whisper UI")
    filepath = upload_file()
    transcribe_button = st.button("Transcribe")
    if transcribe_button:
        with st.spinner("Transcribing...Please wait"):
            _transcribe(filepath)
        st.success("Transcription complete")
