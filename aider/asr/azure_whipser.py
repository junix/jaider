import os

import openai


def do_asr(file: str, promt: str = "", **kwargs):
    client = openai.AzureOpenAI(
        api_key=os.getenv("WLJ_TTS_OPENAI_API_KEY"),
        api_version="2024-02-15-preview",
        azure_endpoint=os.getenv("WLJ_TTS_OPENAI_API_BASE"),
    )
    with open(file, "rb") as file:
        if promt:
            translation = client.audio.translations.create(
                model="whisper", file=file, prompt=promt
            )
        else:
            translation = client.audio.translations.create(model="whisper", file=file)
        return translation.text
