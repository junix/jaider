import torch


def vad(file):
    torch.set_num_threads(1)

    model, utils = torch.hub.load(repo_or_dir="snakers4/silero-vad", model="silero_vad")
    (get_speech_timestamps, _, read_audio, _, _) = utils

    wav = read_audio("path_to_audio_file")
    speech_timestamps = get_speech_timestamps(wav, model)
    return speech_timestamps
