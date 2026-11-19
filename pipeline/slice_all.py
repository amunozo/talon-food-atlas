#!/usr/bin/env python3
"""Cut per-food caption slices for every episode (run fetch_captions.py first).

Writes pipeline/cache/slices/<video_id>.json: list of
  {id, name, group, csv_tier, original_tier, start, end, text}
and pipeline/cache/slices/index.json (per-episode summary + problem foods).
Foods are matched to chapters by the start seconds in chapter_url (&t=NNNs);
end = end of that chapter (next chapter start / conclusion). Text is
word-level from start-PAD to end+PAD (PAD = 6 s overlap), so verdict sentences
that straddle chapter boundaries are kept.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAP = ROOT / "pipeline" / "cache" / "captions"
OUT = ROOT / "pipeline" / "cache" / "slices"
PAD = 6
SHORT = 15


def load_words(vid):
    j = json.load(open(CAP / f"{vid}.en.json3"))
    words = []
    for e in j["events"]:
        for s in e.get("segs", []):
            t = s["utf8"].replace("\n", " ").strip()
            if t:
                words.append((e["tStartMs"] / 1000 + s.get("tOffsetMs", 0) / 1000, t))
    return words


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    foods = json.load(open(ROOT / "data.json"))["foods"]
    eps = {}
    for f in foods:
        m = re.search(r"v=([\w-]+)&t=(\d+)", f["chapter_url"])
        eps.setdefault(m.group(1), []).append((int(m.group(2)), f))
    index, seen = {}, 0
    for vid, items in eps.items():
        info = json.load(open(CAP / f"{vid}.info.json"))
        has_caps = (CAP / f"{vid}.en.json3").exists()
        words = load_words(vid) if has_caps else []
        chs = info.get("chapters") or []
        starts = sorted(c["start_time"] for c in chs)
        sl, problems = [], []
        for t, f in items:
            c = min(chs, key=lambda c: abs(c["start_time"] - t), default=None)
            if c is not None and abs(c["start_time"] - t) <= 1:
                a, b = c["start_time"], c["end_time"]
            else:  # no matching chapter: end at next chapter start or video end
                a = t
                b = next((s for s in starts if s > t), info["duration"])
                problems.append({"id": f["id"], "name": f["name"], "issue": "no chapter match"})
            text = " ".join(w for s, w in words if a - PAD <= s < b + PAD)
            n = len(text.split())
            if not has_caps:
                problems.append({"id": f["id"], "name": f["name"], "issue": "no captions available"})
            elif n < SHORT:
                problems.append({"id": f["id"], "name": f["name"], "issue": f"short ({n} words)"})
            sl.append({"id": f["id"], "name": f["name"], "group": f["group"], "csv_tier": f["tier"],
                       "original_tier": f["original_tier"], "start": a, "end": b, "text": text})
        json.dump(sl, open(OUT / f"{vid}.json", "w"), indent=1, ensure_ascii=False)
        seen += len(sl)
        index[vid] = {"title": info["title"], "foods": len(sl), "duration": info["duration"],
                      "captions": (CAP / f"{vid}.type").read_text() if has_caps else "missing", "problems": problems}
    json.dump(index, open(OUT / "index.json", "w"), indent=1, ensure_ascii=False)
    print(len(index), "episodes,", seen, "foods")


if __name__ == "__main__":
    main()
