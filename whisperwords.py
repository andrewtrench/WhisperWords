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


from pydub import AudioSegment


def split_audio(input_file, output_folder, chunk_duration):
    audio = AudioSegment.from_file(input_file)
    chunk_count = int(audio.duration_seconds / chunk_duration) + 1

    for i in range(chunk_count):
        start_time = i * chunk_duration * 1000
        end_time = (i + 1) * chunk_duration * 1000
        chunk = audio[start_time:end_time]

        # Find the last silence in the chunk and trim the chunk there
        last_silence = chunk.reverse().fade_in(1000).apply_gain(-20).find_silence(1000, 100)
        if len(last_silence) > 0:
            last_silence_end = len(chunk) - last_silence[0][0] + 1000
            chunk = chunk[:last_silence_end]

        # Save the chunk to a file
        chunk_name = f"{i}.mp3"
        chunk.export(f"{output_folder}/{chunk_name}", format="mp3")


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
            with st.spinner("Splitting file into chunks...Please wait"):

                try:
                    os.mkdir("chunks")
                except FileExistsError:
                    pass
                split_audio(filepath, "chunks", 60)
                # chunk_size = 1024 * 1024
                #
                # audio = AudioSegment.from_file(filepath)
                # chunks = audio[::chunk_size]
                # for i, chunk in enumerate(chunks):
                #     chunk.export(f"chunks/{filename}_{i}.mp3", format="mp3")
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
        text = ""
        st.write(os.listdir(audio_path))

        for audio in os.listdir(audio_path):

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
    filepath = upload_file()
    transcribe_button = st.button("Transcribe")
    if transcribe_button:
        with st.spinner("Transcribing...Please wait"):
            _transcribe(filepath)
        st.success("Transcription complete")
