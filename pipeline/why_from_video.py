#!/usr/bin/env python3
"""Write per-food "why" texts for a caption-less Talon Fitness episode by having
google/gemini-3.1-flash-lite watch the YouTube video (OpenRouter, one call).
Usage: why_from_video.py VIDEO_ID [--title "Episode title"]
Reads pipeline/cache/slices/<id>.json (id,name,original_tier,start,end);
writes pipeline/out/why/<id>.json and pipeline/out/why/<id>.usage.json.
Key is read from Pi's auth file; never printed or written."""
import argparse, json, os, re, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = 'google/gemini-3.1-flash-lite'
KEY = json.load(open(os.path.expanduser('~/.pi/agent/auth.json')))['openrouter']['key']
TIERS = {'★': 'top tier'}

PROMPT = """You are watching the episode "{title}" of Talon Fitness's "Nutrition Tier Lists". The video has no captions, so listen to what Talon says in each food's chapter (times in seconds below).
For EACH food write "why": exactly 2 sentences (about 40-60 words, never more than 80) paraphrasing Talon's reasons for that food, following these rules:
(a) the second sentence ends with his verdict using the given tier (write "{star}" as "top tier", e.g. "He puts it in B tier." / "He ranks it top tier.");
(b) include any serving/portion limits he gives;
(c) name 4-6 nutrients/benefits he mentions;
(d) include the downsides/warnings he mentions (sodium, sugar, processing, allergies, etc.);
(e) use only what Talon says in that food's chapter; never add outside nutrition knowledge; no quotes longer than 5 words; ignore speech that belongs to neighbouring chapters.
If you cannot support a confident summary, write what is supported and set "confidence" to "low" with a short "note" reason; otherwise "confidence" is "high" and "note" is "".
Foods (id | name | tier he gave | chapter start-end seconds):
{flist}
Return strict JSON only (no markdown fences, no commentary), parseable by json.loads: {{"foods": [{{"id": int, "why": str, "confidence": "high"|"low", "note": str}}]}} in the order listed."""


TPROMPT = """You are watching the episode "{title}". For EACH food below, transcribe verbatim, in English, everything Talon says in that food's chapter (chapter start-end in seconds from the start of the video): his whole spoken segment about that food, from the first sentence introducing it through his tier verdict. Do not summarize or skip anything; use correct nutrition terms; do not include speech about other foods.
Foods (name | chapter start-end):
{flist}
Return strict JSON only (no markdown fences): {{"foods": [{{"name": str, "text": str}}]}} in the order listed."""


def _chunk(video, title, group):
    flist = "\n".join(f"{f['name']} | {int(f['start'])}-{int(f['end'])}" for f in group)
    body = {"model": MODEL, "temperature": 0, "usage": {"include": True}, "max_tokens": 16000,
            "messages": [{"role": "user", "content": [{"type": "text", "text": TPROMPT.format(title=title, flist=flist)},
                {"type": "video_url", "video_url": {"url": f"https://www.youtube.com/watch?v={video}"}}]}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    try:
        raw = urllib.request.urlopen(req, timeout=1500).read().decode()
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
    j = json.loads(raw.replace(KEY, 'REDACTED')); u = j.get('usage') or {}
    txt = re.sub(r'^```(?:json)?\s*|\s*```$', '', j['choices'][0]['message']['content'].strip())
    foods = {x['name']: x['text'] for x in json.loads(txt)['foods'] if 'name' in x and 'text' in x}
    return foods, float(u.get('cost') or 0), (u.get('prompt_tokens') or 0, u.get('completion_tokens') or 0)


def transcribe(video, title='Nutrition Tier List', per=3):
    """Gemini ignores time windows for YouTube video_url, so ask for the verbatim speech of `per`
    consecutive chapters at a time (by food name) and put it in the slice text fields."""
    from concurrent.futures import ThreadPoolExecutor
    sp = os.path.join(ROOT, 'pipeline/cache/slices', video + '.json'); sl = json.load(open(sp))
    groups = [sl[i:i + per] for i in range(0, len(sl), per)]
    t0 = time.time()
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda g: _chunk(video, title, g), groups))
    d = os.path.join(ROOT, 'pipeline/cache/captions'); os.makedirs(d, exist_ok=True)
    cost = sum(r[1] for r in res); wall = round(time.time() - t0, 1)
    allt = {k: v for r in res for k, v in r[0].items()}
    json.dump({"foods": allt, "usage": {"cost": cost, "wall_s": wall, "tokens": [r[2] for r in res]}},
              open(os.path.join(d, video + '.gemini.json'), 'w'), indent=1, ensure_ascii=False)
    for f in sl:
        f['text'] = allt.get(f['name'], '')
    json.dump(sl, open(sp, 'w'), indent=1, ensure_ascii=False)
    print('cost', cost, 'wall', wall, 'empty:', [f['name'] for f in sl if len(f['text'].split()) < 40])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--title', default='Nutrition Tier List')
    ap.add_argument('--transcribe', action='store_true', help='transcribe via Gemini, fill slice text, then stop')
    a = ap.parse_args()
    if a.transcribe:
        return transcribe(a.video, a.title)
    foods = json.load(open(os.path.join(ROOT, 'pipeline/cache/slices', a.video + '.json')))
    flist = "\n".join(f"{f['id']} | {f['name']} | {f['original_tier']} | {int(f['start'])}-{int(f['end'])}" for f in foods)
    body = {"model": MODEL, "temperature": 0, "usage": {"include": True},
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": PROMPT.format(title=a.title, flist=flist, star='★')},
                {"type": "video_url", "video_url": {"url": f"https://www.youtube.com/watch?v={a.video}"}}]}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t = time.time()
    try:
        raw = urllib.request.urlopen(req, timeout=1200).read().decode()
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
    wall = round(time.time() - t, 1)
    j = json.loads(raw.replace(KEY, 'REDACTED'))
    u = j.get('usage') or {}
    outdir = os.path.join(ROOT, 'pipeline/out/why'); os.makedirs(outdir, exist_ok=True)
    json.dump({"cost": u.get('cost'), "prompt_tokens": u.get('prompt_tokens'), "completion_tokens": u.get('completion_tokens'),
               "wall_s": wall}, open(os.path.join(outdir, a.video + '.usage.json'), 'w'), indent=1)
    txt = j['choices'][0]['message']['content'].strip()
    txt = re.sub(r'^```(?:json)?\s*|\s*```$', '', txt)
    got = {x['id']: x for x in json.loads(txt)['foods']}
    out = [{"id": f['id'], "name": f['name'], "why": got[f['id']]['why'].strip(), "repairs": [],
            "confidence": got[f['id']].get('confidence', 'high'),
            "note": "source: video (no captions)" + (f"; {got[f['id']]['note']}" if got[f['id']].get('note') else "")}
           for f in foods if f['id'] in got]
    json.dump(out, open(os.path.join(outdir, a.video + '.json'), 'w'), indent=1, ensure_ascii=False)
    print(len(out), '/', len(foods), 'cost', u.get('cost'), 'wall', wall)

main()
