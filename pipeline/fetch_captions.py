#!/usr/bin/env python3
"""Download English captions + info json for every episode in data.json.

Usage: python3 pipeline/fetch_captions.py [video_id ...]
With no ids, uses all distinct video ids found in data.json foods[].chapter_url.
Output (git-ignored, Talon's content, never publish) in pipeline/cache/captions/:
  <id>.en.json3   captions (manual if the video has them, else auto)
  <id>.info.json  yt-dlp info (title, duration, chapters)
  <id>.type       'manual' or 'auto'
Skips episodes already downloaded. Requires the yt-dlp CLI.
"""
import json, re, subprocess, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pipeline" / "cache" / "captions"


def episode_ids():
    foods = json.load(open(ROOT / "data.json"))["foods"]
    ids = []
    for f in foods:
        m = re.search(r"v=([\w-]+)", f["chapter_url"])
        if m and m.group(1) not in ids:
            ids.append(m.group(1))
    return ids


def run(vid, manual):
    flag = "--write-subs" if manual else "--write-auto-subs"
    tmp = OUT / f"{vid}.tmp"
    subprocess.run(["yt-dlp", "--skip-download", flag, "--sub-langs", "en", "--sub-format", "json3",
                    "--write-info-json", "-o", str(OUT / vid) + ".%(ext)s",
                    f"https://www.youtube.com/watch?v={vid}"],
                   check=False, capture_output=True, text=True)


def fetch(vid):
    if (OUT / f"{vid}.type").exists():
        return "cached"
    sub = OUT / f"{vid}.en.json3"
    info = OUT / f"{vid}.info.json"
    for manual in (True, False):
        for p in (sub,):
            p.unlink(missing_ok=True)
        run(vid, manual)
        if sub.exists() and info.exists():
            (OUT / f"{vid}.type").write_text("manual" if manual else "auto")
            return "manual" if manual else "auto"
    return "FAILED"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for vid in (sys.argv[1:] or episode_ids()):
        print(vid, fetch(vid), flush=True)
