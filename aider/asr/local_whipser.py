import os
import pathlib
import re
import subprocess
import tempfile

from audios.record import is_ffmpeg_available

WHISPER_BIN = pathlib.Path("~/whisper-bin").expanduser()


def convert_audio_to_format(input_file: str, output_file: str):
    if not is_ffmpeg_available():
        raise EnvironmentError(
            "ffmpeg is not installed or not available in the system path"
        )

    cmd = f'ffmpeg -i "{input_file}" -ar 16000 -ac 1 -c:a pcm_s16le "{output_file}"'
    subprocess.run(cmd, shell=True)


def do_asr(file, *, language: str = None, **kwargs):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "output.wav")
        convert_audio_to_format(input_file=file, output_file=output_file)
        cmd = [
            f"{WHISPER_BIN}/main",
            "-m",
            f"{WHISPER_BIN}/ggml-large-v3.bin",
            "-f",
            output_file,
        ]
        if language:
            cmd += ["-l", language]

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        acc = []
        for line in process.stdout:
            match = re.search(
                r"\[\d\d:\d\d:\d\d\.\d{3} --> \d\d:\d\d:\d\d\.\d{3}\]\s*(.*)", line
            )
            if not match:
                continue
            text = match.group(1)
            if not text:
                continue
            text = text.strip()
            if text[-1] not in [",", ".", "!", "?"]:
                text += ","
            acc.append(text)
        return "".join(acc)
