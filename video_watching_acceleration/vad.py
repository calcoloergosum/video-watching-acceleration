"""
Reads audio files under a directory and record voice activity segments into csv files.
Shallow wrapper for `silero_vad`
"""
import argparse
from pathlib import Path

import pandas as pd
import torch

SAMPLING_RATE = 16000  # sample rate that Silero VAD was trained with


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ext", type=str, help="Audio extension")
    parser.add_argument("src", type=Path, help="Directory where audio files are under")
    parser.add_argument("dst", type=Path, help="Directory where the csv files will be saved under")
    args = parser.parse_args()

    model, (get_speech_timestamps, _, read_audio, _, _) = \
        torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=True,
            onnx=False
        )

    for path in args.src.glob(f"*.{args.ext}"):
        dstname = args.dst / f'{path.stem}_vad.csv'
        if dstname.exists():
            print(f"Already processed {path.stem}. Skipping.")
            continue

        print(f'Processing "{path.stem}"')
        y = read_audio(path.as_posix(), SAMPLING_RATE)
        speech_timestamps = get_speech_timestamps(y, model, sampling_rate=SAMPLING_RATE)
        pd.DataFrame([
            {"start": d["start"] / SAMPLING_RATE, "end": d["end"] / SAMPLING_RATE}
            for d in speech_timestamps
        ]).to_csv(dstname.as_posix(), index=False)


if __name__ == '__main__':
    main()
