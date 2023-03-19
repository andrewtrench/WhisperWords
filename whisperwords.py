import os
import pathlib
import subprocess

import ffmpeg
import openai
import streamlit as st
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()
openai.api_key= os.getenv("OPENAI_API_KEY")






def convert_to_wav(path):
    #converts a file to mp3
    print (path)
    sound = AudioSegment.from_file(path)
    name = path.split(".")[0]
    sound.export(f"converted/{name}.wav", format="wav")
    new_path = f"converted/{name}.wav"
    return new_path

def split_audio(path):
    #splits audio into 60 second chunks
    sound = AudioSegment.from_file(path)
    sound = sound.set_channels(1)
    name = path.split(".")[0].split("/")[1]
    print (name)
    chunks = sound[::6000]
    x=1
    for chunk in chunks:
        chunk.export(f"chunks/{name}_{x}.mp3", format="mp3")
        x+=1
    return

def convert_mp3_to_wav(path):
    sound = AudioSegment.from_file(path)
    sound.export(f"converted/{path.split('.')[0]}.mp3", format="mp3")
    return f"converted/{path.split('.')[0]}.mp3"


# global variables
uploaded_mp3_file = None
uploaded_mp3_file_length = 0
filename = None
downloadfile = None


@st.cache_data
def convert_file_to_mp3_bytes2bytes(input_data: bytes) -> bytes:
    """
    It converts file to mp3 using ffmpeg
    :param input_data: bytes object of an audio file
    :return: A bytes object of a mp3 file.
    """
    # print('convert_mp3_to_wav_ffmpeg_bytes2bytes')
    args = (ffmpeg
            .input('pipe:', format=['mp3','aac','wav','mp4'])
            .output('pipe:', format='mp3')
            .global_args('-loglevel', 'error')
            .get_args()
            )
    # print(args)
    proc = subprocess.Popen(
        ['ffmpeg'] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return proc.communicate(input=input_data)[0]


@st.cache_data
def on_file_change(uploaded_file):
    return convert_file_to_mp3_bytes2bytes(uploaded_file.getvalue())


def on_change_callback():
    """
    It prints a message to the console. Just for testing of callbacks.
    """
    print(f'on_change_callback: {uploaded_file}')


# The below code is a simple streamlit web app that allows you to upload an mp3 file
# and then download the converted wav file.
if __name__ == '__main__':
    st.title('WhisperWords')
    st.markdown("""Upload file for transcription""")

    uploaded_file = st.file_uploader('Upload Your File', type=['mp3','aac','wav','mp4'], on_change=on_change_callback)

    if uploaded_mp3_file:
        uploaded_file_length = len(uploaded_file.getvalue())
        filename = pathlib.Path(uploaded_file.name).stem
        if uploaded_file_length > 0:
            st.text(f'Size of uploaded "{uploaded_file.name}" file: {uploaded_file_length} bytes')
            downloadfile = on_file_change(uploaded_file)

    st.markdown("""---""")
    if downloadfile:
        length = len(downloadfile)
        if length > 0:
            st.subheader('After conversion to MP3 you can download it below')
            button = st.download_button(label="Download .mp3 file",
                            data=downloadfile,
                            file_name=f'{filename}.mp3',
                            mime='audio/mp3')
            st.text(f'Size of "{filename}.mp3" file to download: {length} bytes')
    st.markdown("""---""")
