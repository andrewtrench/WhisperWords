# from config import MEDIA_DIR
# from db import ENGINE, Media, Segment, Transcript

import os
import re
from pydub import AudioSegment, silence
import openai
import ffmpeg
import streamlit as st
from pathlib import Path
from pydub import AudioSegment

from pydub import AudioSegment, silence

openai.api_key = st.secrets['OPENAI_API_KEY']


# upload a file from local to streamlit and save it to a directory called uploads

def id_questions(text):
    pattern = r"([^.!?]*\?)"
    new_text = re.sub(pattern, r"\n\n\1</strong>", text)
    new_text = new_text.replace("?", "?\n\n<strong>")
    return new_text


def split_audio(input_file, output_folder, chunk_duration):
    audio = AudioSegment.from_file(input_file)
    st.write(audio)
    chunk_count = int(audio.duration_seconds / chunk_duration) + 1
    with st.spinner("Splitting audio into chunks"):
        for i in range(chunk_count):
            start_time = i * chunk_duration * 1000
            end_time = (i + 1) * chunk_duration * 1000
            chunk = audio[start_time:end_time]
            # Save the chunk to a file
            chunk_name = f"{i}.mp3"
            chunk.export(f"{output_folder}/{chunk_name}", format="mp3")
    st.success("Audio split into chunks")


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
            st.success(f"File saved to {filepath}")

        # if file greater than 24mb split it into 1mb chunks using ffmpeg
        filesize = os.path.getsize(filepath) / (1024 * 1024)
        if filesize > 24:
            st.success("File is greater than 24mb, splitting into 1mb chunks")

            if not os.path.exists("chunks"):
              os.mkdir("chunks")
              split_audio(filepath, "chunks", 60)
                # chunk_size = 1024 * 1024
                #
                # audio = AudioSegment.from_file(filepath)
                # chunks = audio[::chunk_size]
                # for i, chunk in enumerate(chunks):
                #     chunk.export(f"chunks/{filename}_{i}.mp3", format="mp3")
              new_filepath = "chunks"
             _transcribe(new_filepath)
        else:
            _transcribe(filepath)

def delete_files():
    if not os.path.exists("uploads"):
        os.mkdir("uploads")
    if not os.path.exists("chunks"):
        os.mkdir("chunks")
    for file in os.listdir("uploads"):
        file_path = os.path.join("uploads", file)
        os.remove(file_path)
    for file in os.listdir("chunks"):
        file_path = os.path.join("chunks", file)
        os.remove(file_path)
    st.success("Files deleted from uploads and processing directories")
    return


def _transcribe(audio_path: str):
    transcribe_button = st.button("Transcribe")
    st.write(audio_path)
    if transcribe_button:

        """Transcribe the audio file using whisper"""
        if "chunks" in audio_path:
            text = ""
            file_list = os.listdir(audio_path).sort()
            st.write(file_list)
            for audio in file_list:
                audio_file = open(f"chunks/{audio}", "rb")
                transcript = openai.Audio.transcribe("whisper-1", audio_file,
                                                     response="verbose_json",
                                                     temperature=0.5, )
                text.append = id_questions(transcript['text'])
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
    # make sure all folders are empty first
    delete_files()
    st.title("Whisper UI")
    upload_file()


