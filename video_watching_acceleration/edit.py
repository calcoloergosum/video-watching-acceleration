"""
Given voice activity and transcription, edit the videos.
"""
import argparse
import re
from pathlib import Path
from typing import Tuple

import pandas as pd
import scipy.interpolate
from moviepy.editor import VideoFileClip, concatenate_videoclips


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ext", type=str, help='Video extension e.g. "mp4"')
    parser.add_argument("src", type=Path, help="Directory where audio files are under")
    parser.add_argument("dst", type=Path, help="Directory where the csv files will be saved under")
    args = parser.parse_args()

    for src in args.src.glob(f"*.{args.ext}"):
        dst = args.dst / src.name
        if dst.exists():
            print(f"Already processed {src.stem}. Skipping.")
            continue

        print(f'Processing "{src.stem}"')
        try:
            df = pd.read_csv(src.parent / f"{src.stem}_vad.csv")
        except FileNotFoundError:
            print(f"vad file missing")
            continue

        # Process video
        clip = VideoFileClip(src.as_posix())
        
        clip_merged = concatenate_videoclips([clip.subclip(r['start'], r['end']) for _, r in df.iterrows()])
        clip_merged.to_videofile(dst.as_posix(), codec="libx264", temp_audiofile='/tmp/_vad_merge_audio.m4a', remove_temp=True, audio_codec='aac')

        # Process subtitle
        dst_subtitle = args.dst / f"{src.stem}.srt"
 
        try:
            subtitles = (src.parent / f"{src.stem}.srt").open().read().split("\n\n")
        except FileNotFoundError:
            print("Subtitle file missing")
            continue

        # make time interpolation
        bef2aft = [(0, 0)]
        cur = 0
        for s, t in zip(df['start'], df['end']):
            bef2aft.append((s, cur))
            cur += t - s
        bef2aft.append((df['end'].max() + 100000, cur))
        interp = scipy.interpolate.interp1d(*list(zip(*bef2aft)), kind='linear')

        # snap to VAD
        _subtitles = []
        for subtitle in subtitles:
            idx, ts, txt = subtitle.split("\n", maxsplit=2)
            m = re.match(r'^(.*) --> (.*)$', ts)
            stime, ttime = list(map(str2time, m.groups()))

            sframe, tframe = time2frame(*stime), time2frame(*ttime)
            sframe, tframe = interp(sframe), interp(tframe)
            stime, ttime = frame2time(sframe), frame2time(tframe)
            ts = f"{time2str(*stime)} --> {time2str(*ttime)}"

            _subtitles.append('\n'.join([idx, ts, txt]))

        with dst_subtitle.open('w') as fp:
            fp.write("\n\n".join(_subtitles))


def str2time(s: str) -> Tuple[int, int, int, int]:
    return tuple(map(int, re.match(r'(\d+):(\d+):(\d+),(\d+)', s).groups()))

def time2frame(shour, smin, ssec, smils) -> float:
    return (60 * 60 * shour + 60 * smin + ssec + 0.001 * smils)

def frame2time(f: float) -> Tuple[int, int, int, int]:
    """
    >>> frame2time(12345.5)
    "03:25:45,500"
    """
    return int(f // 3600), int((f % 3600) // 60), int((f % 60) // 1), int((f % 1) * 1000) // 1

def time2str(h, m, s, ms) -> str:
    ret = f"{h:0>2}:{m:0>2}:{s:0>2},{ms:0>3}"
    if h > 100 or m > 100 or s > 100 or ms > 1000:
        raise RuntimeError("Time too long " + ret)
    return ret


if __name__ == '__main__':
    main()
