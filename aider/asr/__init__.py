import os
import tempfile
from typing import Literal

from audios.record import record_with_silence_detection


def record_and_asr(
    *,
    language: str = "zh",
    duration: int = None,
    engine: Literal["whisper", "gemini", "local", "groq"],
):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "output.wav")
        record_with_silence_detection(output_file=output_file, duration=duration or 30)
        if not os.path.exists(output_file):
            return

        if engine == "gemini":
            from asr.gemini_asr import do_asr

            return do_asr(output_file)
        elif engine == "local":
            from asr.local_whipser import do_asr as local_do_asr

            return local_do_asr(output_file, language=language)
        elif engine == "whisper":
            from asr.azure_whipser import do_asr

            return do_asr(output_file, prompt="中文普通话的输入", language=language)
        elif engine == "groq":
            from asr.groqs import do_asr

            return do_asr(output_file, prompt="中文普通话的输入", language=language)
        else:
            raise ValueError(f"Unsupported ASR engine: {engine}")
