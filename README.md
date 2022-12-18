# Video Watching Acceleration

Better experience for watching videos where people talk.

This script was intended to watch small scale math lectures/seminars, usually hours long.

## Motivation

I watch videos fast-forward, usually x1.25. Faster than that I cannot fully comprehend the utterance anymore.
Then when I was watching a random video on youtube, I realized that with subtitles, I can comfortably follow the argument of the speaker with playback speed of x1.5.

## Methodology

1. Prepare subtitle

    [Whisper by OpenAI](https://github.com/openai/whisper)(MIT license) was used.
    To better adjust timestamps, [stable-ts](https://github.com/jianfch/stable-ts) was used.

2. Clip long pauses

    [Silero-VAD](https://github.com/snakers4/silero-vad)(MIT License) was used.

3. When watching, fast-forward according to your preference

    Any media player with playback speed control will do; e.g. VLC.

## How to use

After installing requirements by `pip install -r requirements.txt`,

Start with a directory that contains videos.

```
data_src/
    - lecture01.mp4
    - lecture02.mp4
    - ...
```

Run ```python -m video_watching_acceleration.transcribe mp4 data_src data_src --whisper-model small```

```
data_src/
    - lecture01.mp4
    - lecture01.srt
    - lecture02.mp4
    - ...
```

Run ```python -m video_watching_acceleration.vad mp4 data_src data_src```
```
data_src/
    - lecture01.mp4
    - lecture01.srt
    - lecture01_vad.csv
    - lecture02.mp4
    - ...
```

Finally, run ```python -m video_watching_acceleration.edit mp4 data_src data_dst```
```
data_src/
    - lecture01.mp4
    - lecture01.srt
    - lecture01_vad.csv
    - lecture02.mp4
    - ...
data_dst/
    - lecture01.mp4
    - lecture01.srt
    - lecture02.mp4
    ...
```

Enjoy!
