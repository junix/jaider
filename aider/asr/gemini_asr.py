import os


def do_asr(file, **kwargs):
    if not os.path.exists(file):
        raise FileNotFoundError(f"File not found: {file}")

    from llms.google import chat

    res = chat(
        prompt="对音频进行语音识别,并整理成流畅的文字。",
        audio=file,
        model="gemini-1.5-pro-latest",
    )
    return res
