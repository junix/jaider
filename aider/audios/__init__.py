# from pydub import AudioSegment

# song = AudioSegment.from_mp3("good_morning.mp3")

# # PyDub handles time in milliseconds
# ten_minutes = 10 * 60 * 1000

# first_10_minutes = song[:ten_minutes]

# first_10_minutes.export("good_morning_10.mp3", format="mp3")


from pydub import AudioSegment


def do_segments(input_file, output_prefix, segment_duration):
    # Load the audio file
    audio = AudioSegment.from_file(input_file)

    # Calculate the number of segments
    total_duration = len(audio)
    num_segments = total_duration // (segment_duration * 1000)

    # Segment the audio and export each segment
    for i in range(num_segments):
        start_time = i * segment_duration * 1000
        end_time = (i + 1) * segment_duration * 1000
        segment = audio[start_time:end_time]

        output_file = f"{output_prefix}_{i+1}.{input_file.split('.')[-1]}"
        segment.export(output_file, format=input_file.split(".")[-1])

    # Export the remaining part if any
    if total_duration % (segment_duration * 1000) != 0:
        start_time = num_segments * segment_duration * 1000
        segment = audio[start_time:]
        output_file = f"{output_prefix}_{num_segments+1}.{input_file.split('.')[-1]}"
        segment.export(output_file, format=input_file.split(".")[-1])
