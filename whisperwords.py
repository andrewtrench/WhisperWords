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


def split_audio(input_file, chunk_duration):
    audio = AudioSegment.from_file(input_file)
    audio_segments = audio[::chunk_duration * 1000]
    progress_bar = st.progress(0)
    total_iteration = 100
    i = 1
    if not os.path.exists("uploads/chunks"):
        os.mkdir("uploads/chunks")
    for chunk in audio_segments:
        chunk_name = f"{i}.mp3"
        filepath = os.path.join("uploads/chunks", chunk_name)
        chunk.export(filepath, format="mp3")
        i += 1
        progress = (i / total_iteration)
        progress_bar.progress(progress)
    filelist = []
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            filename = os.path.join(root, file)
            filelist.append(filename)
    st.write(filelist)
    # Get the list of files in the 'chunks' directory and sort it
    sorted_files = sorted(os.listdir("uploads/chunks"))

    st.write(f"Sorted chunk directory:{sorted_files}")
    for audio in sorted_files:
        st.write(audio)
        _transcribe_chunks(audio)



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
            if st.button("Split Audio"):
                split_audio(filepath, 60)
                # chunk_size = 1024 * 1024
                #
                # audio = AudioSegment.from_file(filepath)
                # chunks = audio[::chunk_size]
                # for i, chunk in enumerate(chunks):
                #     chunk.export(f"chunks/{filename}_{i}.mp3", format="mp3")

        else:
            return filepath
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

def _transcribe_chunks(audio_path: str):
    audio_file = open(f"chunks/{audio_path}", "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file,
                                             response="verbose_json",
                                             temperature=0.5, )
    st.write(transcript['text'])


def _transcribe(audio_path: str):
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
    file_path = upload_file()

    transcribe_button = st.button("Transcribe")
    if transcribe_button:
        _transcribe(file_path)




