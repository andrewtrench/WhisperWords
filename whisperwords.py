import os
import pathlib
import subprocess
import filetype
import ffmpeg
import openai
import streamlit as st
from dotenv import load_dotenv
from pydub import AudioSegment


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
# global variables
uploaded_file = None
uploaded_file_length = 0
filename = None
downloadfile = None


def convert_to_wav(path):
    # converts a file to mp3
    print(path)
    sound = AudioSegment.from_file(path)
    name = path.split(".")[0]
    sound.export(f"converted/{name}.wav", format="wav")
    new_path = f"converted/{name}.wav"
    return new_path


def split_audio(path):
    # splits audio into 60 second chunks
    sound = AudioSegment.from_file(path)
    sound = sound.set_channels(1)
    name = path.split(".")[0].split("/")[1]
    print(name)
    chunks = sound[::6000]
    x = 1
    for chunk in chunks:
        chunk.export(f"chunks/{name}_{x}.mp3", format="mp3")
        x += 1
    return


def convert_mp3_to_wav(path):
    sound = AudioSegment.from_file(path)
    sound.export(f"converted/{path.split('.')[0]}.mp3", format="mp3")
    return f"converted/{path.split('.')[0]}.mp3"




def detect_file_type(file: bytes) -> str:

    """
    It detects the file type of a file.
    :param file: bytes object of a file.
    :return: A string with the file type.
    """
    try:
        file_type = filetype.guess(file)
        if file_type.extension==None:
            return 'mp3'
        return file_type.extension
    except ValueError:
        return 'mp3'

def enter_details():
    details = st.text_input("Enter details about the interview including names of people, location and any organisations mentioned for a better transcript")
    return details


def convert_file_to_mp3_bytes2bytes(input_data: bytes) -> bytes:

    """
    It converts file to mp3 using ffmpeg
    :param input_data: bytes object of an audio file
    :return: A bytes object of a mp3 file.
    """
    # Detect file type
    file_type = detect_file_type(input_data)
    input_format = file_type

    # Convert to mp3
    args = (ffmpeg
                .input('pipe:', format=input_format)
                .output('pipe:', format='mp3')
                .global_args('-loglevel', 'error')
                .get_args()
                )
    proc = subprocess.Popen(
            ['ffmpeg'] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE
            )
    converted_file = proc.communicate(input=input_data)[0]
    parent_path = pathlib.Path(__file__).parent.parent.resolve()
    save_path = os.path.join(parent_path, "converted")
    complete_name = os.path.join(save_path, uploaded_file.name)
    st.write(f"Place where file is stored {complete_name}")
    with open(f"{complete_name}", "wb") as f:
        f.write(converted_file)

    # Display a success message
    st.success("File converted successfully!")

    return complete_name

@st.cache_data
def on_file_change(uploaded_file):
    return convert_file_to_mp3_bytes2bytes(uploaded_file.getvalue())


def on_change_callback():
    """
    It prints a message to the console. Just for testing of callbacks.
    """
    print(f'Processing: {uploaded_file}')


def transcript_with_whisper(path):
    # This function transcribes the audio file and returns the transcript using openai's whisperwords api

    # get the details of the interview
    details = enter_details()

    openai.api_key = os.getenv("OPENAI_API_KEY")
    audio_file = path
    audio_file = open(audio_file, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file,
                                         prompt=details,
                                         temperature=0.5,)
    transcript = transcript['text']
    display_transcript = st.empty()
    display_transcript.write(transcript)
    return


def upload_file_for_transcription():

    uploaded_file = st.file_uploader('Upload Your File', type=['mp3', 'aac', 'wav', 'mp4'],
                                     on_change=on_change_callback)
    converted_file = convert_file_to_mp3_bytes2bytes(uploaded_file.getvalue())
    transcript_with_whisper(converted_file)



# The below code is a simple streamlit web app that allows you to upload an mp3 file
# and then download the converted wav file.
if __name__ == '__main__':
    st.title('WhisperWords')
    st.markdown("""Upload file for transcription""")
    upload_file_for_transcription()

    st.markdown("""---""")
