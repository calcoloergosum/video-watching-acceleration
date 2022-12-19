"""
Read audio files under a directory and transcribe them all into srt files.
Shallow wrapper of `whisper` and `stable_whisper`.
"""
import argparse
from pathlib import Path
from typing import Optional
import whisper
from stable_whisper import modify_model, results_to_sentence_srt


TOP30 = [
    'en', 'zh', 'de', 'es', 'ru',
    'fr', 'pt', 'ko', 'ja', 'tr',
    'pl', 'it', 'sv', 'nl', 'ca',
    'fi', 'id', 'ar', 'uk', 'vi',
    'he', 'el', 'da', 'ms', 'hu',
    'ro', 'no', 'th', 'cs', 'ta',
]

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("ext", type=str, help="Audio extension")
    parser.add_argument("src", type=Path, help="Directory where audio files are under")
    parser.add_argument("dst", type=Path, help="Directory where the csv files will be saved under")
    parser.add_argument("--whisper-model", type=str, help="whisper model name", default='large-v2')
    parser.add_argument("--language", type=str, default=None, help="Language code",
        choices=sorted([*whisper.tokenizer.LANGUAGES]) + [None, 'all'])
    args = parser.parse_args()

    model = whisper.load_model(args.whisper_model)
    modify_model(model)
    for src in sorted(args.src.glob(f"*.{args.ext}")):
        if args.language == 'top30':
            for language in TOP30:  # only top 30 languages
                run(src, args.dst, language, model)
        elif args.language == 'all':
            for language in sorted(whisper.tokenizer.LANGUAGES):
                run(src, args.dst, language, model)
        else:
            run(src, args.dst, args.language, model)


def run(src: Path, dstdir: Path, language: Optional[str], model):
    if language is None:
        filename = f'{src.stem}.srt'
    else:
        filename = f'{src.stem}_{language}.srt'
    dst = dstdir / filename
    if dst.exists():
        print(f"Already processed {src.stem} (with language {language}). Skipping.")
        return
    print(f'Processing "{src.stem} (language: {language})"')
    result = model.transcribe(src.as_posix(), language=language,
        max_initial_timestamp=None, suppress_silence=True, ts_num=16)
    # after you get results from modified model
    results_to_sentence_srt(result, dst.as_posix())


if __name__ == '__main__':
    main()
