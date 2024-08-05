import os
import pathlib

from groq import Groq


def do_asr(file, prompt: str = None, **kwargs):
    file = pathlib.Path(file)
    client = Groq()
    if not os.path.exists(file):
        raise FileNotFoundError(f"File not found: {file}")

    prompt = prompt or "对音频进行中文语音识别,并整理成流畅的文字。"
    transcription = client.audio.transcriptions.create(
        file=(str(file), file.read_bytes()),
        prompt=prompt,
        model="whisper-large-v3",
    )
    return transcription.text
