from contextlib import contextmanager

import numpy as np
import pyaudio
from playsound import playsound


def play(audio_file: str):
    try:
        playsound(audio_file)
    except Exception as e:
        print(f"Error playing audio: {str(e)}")


class Player:
    def __init__(self, sample_rate=48000):
        self._sample_rate = sample_rate
        self._player = None
        self._stream = None

    def open(self):
        """Initialize the audio player and open a stream."""
        self._player = pyaudio.PyAudio()
        self._stream = self._player.open(
            format=pyaudio.paInt16, channels=1, rate=self._sample_rate, output=True
        )
        print("Audio player initialized and stream opened.")

    def update(self, frame):
        """Update the audio stream with a new frame of audio data."""
        if self._stream is not None:
            # Ensure the frame is in the correct format
            if isinstance(frame, np.ndarray):
                frame = frame.astype(np.int16).tobytes()
            elif isinstance(frame, bytes):
                pass
            else:
                raise ValueError("Frame must be a bytes object or a numpy ndarray.")

            self._stream.write(frame)
            print("Audio frame updated.")

    def close(self):
        """Stop and close the audio stream, and terminate the player."""
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        if self._player is not None:
            self._player.terminate()
            self._player = None
        print("Audio player closed and stream terminated.")


@contextmanager
def stream_player(sample_rate=48000):
    p = Player(sample_rate)
    p.open()
    try:
        yield p
    finally:
        p.close()
