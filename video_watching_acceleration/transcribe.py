"""
Read audio files under a directory and transcribe them all into srt files.
Shallow wrapper of `whisper` and `stable_whisper`.
"""
import argparse
from pathlib import Path

import whisper
from stable_whisper import modify_model, results_to_sentence_srt


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("ext", type=str, help="Audio extension")
    parser.add_argument("src", type=Path, help="Directory where audio files are under")
    parser.add_argument("dst", type=Path, help="Directory where the csv files will be saved under")
    parser.add_argument("--whisper-model", type=str, help="whisper model name", default=None)
    args = parser.parse_args()

    model = whisper.load_model(args.whisper_model)
    modify_model(model)
    for p in sorted(args.src.glob(f"*.{args.ext}")):
        dstname = args.dst / f'{p.stem}.srt'
        if dstname.exists():
            print(f"Already processed {p.stem}. Skipping.")
            continue
        print(f'Processing "{p.stem}"')
        result = model.transcribe(p.as_posix(), language='en', max_initial_timestamp=None, suppress_silence=True, ts_num=16)
        # after you get results from modified model
        results_to_sentence_srt(result, dstname.as_posix())


if __name__ == '__main__':
    main()
