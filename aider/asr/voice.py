import math
import queue
import sys
import tempfile
import time

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style

# 定义样式字典
style = Style.from_dict(
    {
        "magenta": "ansimagenta",
        "red-on-magenta": "fg:ansired bg:ansimagenta",
        "yellow": "ansiyellow",
        "brightcyan": "ansibrightcyan",
        "red": "ansired",
    }
)

try:
    import soundfile as sf
except (OSError, ModuleNotFoundError):
    sf = None


recording = HTML("<ansired>  </ansired> ")


class SoundDeviceError(Exception):
    pass


class Voice:
    max_rms = 0
    min_rms = 1e5
    pct = 0

    threshold = 0.15

    def __init__(self):
        if sf is None:
            raise SoundDeviceError
        try:
            import sounddevice as sd

            self.sd = sd
        except (OSError, ModuleNotFoundError):
            raise SoundDeviceError

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        import numpy as np

        rms = np.sqrt(np.mean(indata**2))
        self.max_rms = max(self.max_rms, rms)
        self.min_rms = min(self.min_rms, rms)

        rng = self.max_rms - self.min_rms
        if rng > 0.001:
            self.pct = (rms - self.min_rms) / rng
        else:
            self.pct = 0.5

        self.q.put(indata.copy())

    def get_prompt(self):
        num = 10
        if math.isnan(self.pct) or self.pct < self.threshold:
            cnt = 0
        else:
            cnt = int(self.pct * 10)

        # bar = "░" * cnt + "█" * (num - cnt)
        bar = "󰹞" * cnt + "󰹟" * (num - cnt)
        bar = bar[:num]

        dur = time.time() - self.start_time
        # return f"{red_bold(' ')} press ↵ for done {dur:.1f}sec {bar}"
        return HTML(
            f"<ansired>  </ansired> "
            f"<ansiyellow>  {dur:.1f} </ansiyellow> "
            f"<ansibrightcyan>{bar}</ansibrightcyan> "
            "<ansired> 󰌑 </ansired>"
        )

    def is_pipeline(self):
        return not sys.stdout.isatty()

    def record_and_transcribe(self, history=None, language=None):
        try:
            return self.raw_record_and_transcribe(history, language)
        except KeyboardInterrupt:
            return

    def raw_record_and_transcribe(self, history, language):
        self.q = queue.Queue()

        filename = tempfile.mktemp(suffix=".wav")

        try:
            sample_rate = int(
                self.sd.query_devices(None, "input")["default_samplerate"]
            )
        except (TypeError, ValueError):
            sample_rate = 16000  # fallback to 16kHz if unable to query device

        self.start_time = time.time()

        try:
            with self.sd.InputStream(
                samplerate=sample_rate, channels=1, callback=self.callback
            ):
                if self.is_pipeline():
                    print("Recording... Press Ctrl+C to stop.", file=sys.stderr)
                    while True:
                        time.sleep(0.1)
                        dur = time.time() - self.start_time
                        print(
                            f"\rRecording duration: {dur:.1f} seconds",
                            end="",
                            file=sys.stderr,
                        )
                else:
                    prompt(self.get_prompt, refresh_interval=0.1)
        except self.sd.PortAudioError as err:
            print(err, file=sys.stderr)
            return
        except KeyboardInterrupt:
            print("\nRecording stopped.", file=sys.stderr)

        print("\nProcessing audio...", file=sys.stderr)

        with sf.SoundFile(
            filename, mode="x", samplerate=sample_rate, channels=1
        ) as file:
            while not self.q.empty():
                file.write(self.q.get())

        from asr.groqs import do_asr

        res = do_asr(filename)
        print("\nProcessing audio...", res, file=sys.stderr)
        return res


if __name__ == "__main__":
    print(Voice().record_and_transcribe())
