import os
import threading
import time
import wave
from collections import deque

import numpy as np
import pyaudio
from pynput import keyboard


class AudioRecorder:
    """A class to handle the recording of audio using the PyAudio library."""

    def __init__(
        self,
        *,
        verbose=False,
        input_device_index=None,
        audio_folder="audio_files",
        filename="temp_recording.wav",
    ):
        """
        Initialize the AudioRecorder.

        :param verbose: If True, print detailed information during recording and saving.
        :param input_device_index: Explicitly set the index of the input device to use.
        """
        self.filename = filename
        self.recording = False
        self.frames = deque()
        self.record_thread = None
        self.start_time = None
        self.audio_folder = audio_folder
        self.verbose = verbose

        # PyAudio object and open the stream
        self.audio = pyaudio.PyAudio()
        self.stream = None
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=11025,
                input=True,
                frames_per_buffer=512,
                start=False,
                input_device_index=input_device_index,  # Use the specified device index
            )
        except Exception as e:
            if self.verbose:
                import traceback

                traceback.print_exc()
            else:
                print(f"Failed to open audio stream: {e}")

    def list_devices(self):
        """List all available input devices."""
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get("deviceCount")
        for i in range(0, num_devices):
            if (
                self.audio.get_device_info_by_host_api_device_index(0, i).get(
                    "maxInputChannels"
                )
            ) > 0:
                print(
                    "Input Device id ",
                    i,
                    " - ",
                    self.audio.get_device_info_by_host_api_device_index(0, i).get(
                        "name"
                    ),
                )

    def start_recording(self):
        if not self.recording and self.stream is not None:
            self.recording = True
            self.frames.clear()
            self.start_time = time.time()
            self.record_thread = threading.Thread(target=self.record_audio, daemon=True)
            try:
                self.stream.start_stream()
                self.record_thread.start()
                if self.verbose:
                    print("Recording started...")
            except Exception as e:
                self.recording = False
                if self.verbose:
                    import traceback

                    traceback.print_exc()
                else:
                    print(f"Failed to start recording: {e}")

    def record_audio(self):
        try:
            while self.recording:
                data = self.stream.read(512, exception_on_overflow=False)
                self.frames.append(np.frombuffer(data, dtype=np.int16))
        except Exception as e:
            self.recording = False
            if self.verbose:
                import traceback

                traceback.print_exc()
            else:
                print(f"Error during recording: {e}")

    def stop_recording(self, cancel=False):
        if self.recording:
            self.recording = False
            self.record_thread.join()
            if self.stream is not None:
                self.stream.stop_stream()
            if not cancel:
                self.save_recording()

    def save_recording(self):
        if self.frames:
            recording = np.concatenate(self.frames)
            recording = np.clip(recording, -32768, 32767).astype(np.int16)
            directory = self.audio_folder
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            filename = os.path.join(directory, self.filename)
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(11025)
                wf.writeframes(recording.tobytes())
            if self.verbose:
                print(f"Recording saved to {filename}")

    def __del__(self):
        if self.stream is not None:
            self.stream.close()
        self.audio.terminate()


def recording_with_key_interrupt(
    audio_folder="audio_files", filename="temp_recording.wav"
):
    r = AudioRecorder(
        verbose=True, input_device_index=0, audio_folder=audio_folder, filename=filename
    )
    try:
        r.start_recording()
        time.sleep(1000)
    except KeyboardInterrupt:
        r.stop_recording()
        print("Recording stopped.")


class AudioRecorderWithHotkey:
    def __init__(self, start_hotkey, stop_hotkey):
        self.recorder = AudioRecorder(verbose=True, input_device_index=0)
        self.start_hotkey = start_hotkey
        self.stop_hotkey = stop_hotkey
        self.listener = None

    def start_listening(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        print(
            f"Press {self.start_hotkey} to start recording, {self.stop_hotkey} to stop."
        )
        self.listener.join()

    def on_press(self, key):
        if key == self.start_hotkey:
            print("Start hotkey pressed. Recording started.")
            self.recorder.start_recording()
        elif key == self.stop_hotkey:
            self.recorder.stop_recording()
            print("Stop hotkey pressed. Recording stopped.")
            self.listener.stop()


def main():
    start_hotkey = keyboard.Key.f9
    stop_hotkey = keyboard.Key.f10
    recorder = AudioRecorderWithHotkey(start_hotkey, stop_hotkey)
    recorder.start_listening()


if __name__ == "__main__":
    main()
