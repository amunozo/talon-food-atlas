#!/usr/bin/env python3
"""Extract on-screen nutrition cards from Talon Fitness tier-list episodes.

Calls google/gemini-3.1-flash-lite via OpenRouter (non-batch) with the YouTube
URL as video_url. One call per episode; on truncated/invalid JSON the episode
is split in halves (by chapter order) and each half retried once.

Usage:
  extract_cards.py [--video ID ...] [--workers 3] [--budget 4.00] [--force]
Output: pipeline/out/cards/<video_id>.json and summary.json.
The API key is read from Pi's auth file and never printed or written.
"""
import argparse, json, os, re, sys, threading, time, urllib.request, urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'pipeline', 'out', 'cards')
MODEL = 'google/gemini-3.1-flash-lite'
KEY = json.load(open(os.path.expanduser('~/.pi/agent/auth.json')))['openrouter']['key']

lock = threading.Lock()
state = {'cost': 0.0, 'calls': 0, 'stop': False}

PROMPT = """You are watching an episode of Talon Fitness's "Nutrition Tier Lists" ("{title}"). For each food below, read the on-screen nutrition card shown for that food and the tier it is placed in on the board.
Per food return:
- "food": the food name exactly as listed below
- "start": the chapter start in seconds, as listed below
- "tier_on_board": the tier the food is placed in on the tier-list board (the symbol shown, e.g. "A","B","C","D", or the star tier as "★")
- "card": the nutrition card exactly as shown: {{"basis": serving basis printed on the card (e.g. "per 100 g"), "calories", "protein_g", "fat_g", "carbs_g", "fiber_g", "sugar_g", "sodium_mg" (numbers only, null if not on the card), "omega3": {{"amount","unit"}} or null if not shown, "micros": a list of {{"nutrient","pct_dv"}} for every micronutrient shown on the card (up to 15; pct_dv is a number without the % sign)}}
Copy numbers exactly as displayed on the card; never estimate, infer or use outside knowledge; use null when a value is not shown. Use "card": null if no card is legible.
Foods:
{flist}
Return strict JSON only: a single valid JSON object that parses with json.loads, no markdown fences, no commentary: {{"foods": [{{"food","start","tier_on_board","card"}}]}}"""


def call(vid, title, foods):
    flist = "\n".join(f"- {f['name']} (chapter starts at {f['start']}s)" for f in foods)
    body = {"model": MODEL, "temperature": 0, "usage": {"include": True},
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": PROMPT.format(title=title, flist=flist)},
                {"type": "video_url", "video_url": {"url": f"https://www.youtube.com/watch?v={vid}"}}]}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=1200); raw = r.read().decode()
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
    except Exception as e:
        raw = json.dumps({"error": str(e)})
    dt = time.time() - t
    raw = raw.replace(KEY, 'REDACTED')
    try:
        j = json.loads(raw)
    except Exception:
        j = {"error": "non-json response"}
    usage = j.get('usage') or {}
    cost = float(usage.get('cost') or 0)
    with lock:
        state['cost'] += cost; state['calls'] += 1
        if state['cost'] >= BUDGET:
            state['stop'] = True
    parsed, err = None, None
    try:
        ch = j['choices'][0]
        txt = ch['message']['content'].strip()
        txt = re.sub(r'^```(?:json)?\s*|\s*```$', '', txt)
        if ch.get('finish_reason') == 'length':
            err = 'truncated'
        else:
            parsed = json.loads(txt)['foods']
    except Exception as e:
        err = err or f'invalid: {type(e).__name__} {str(j.get("error", ""))[:200]}'
    return parsed, err, {"cost": cost, "tokens": {k: usage.get(k) for k in ('prompt_tokens', 'completion_tokens', 'total_tokens')}, "wall_s": round(dt, 1)}


def run_part(vid, title, foods, usages, failures, depth=0):
    if state['stop']:
        failures.append({"foods": [f['name'] for f in foods], "error": "budget stop"}); return []
    parsed, err, u = call(vid, title, foods); usages.append(u)
    if parsed is not None:
        return parsed
    if len(foods) > 1 and depth == 0:  # one retry: split in halves
        m = len(foods) // 2
        return run_part(vid, title, foods[:m], usages, failures, 1) + run_part(vid, title, foods[m:], usages, failures, 1)
    failures.append({"foods": [f['name'] for f in foods], "error": err}); return []


def do_episode(vid, title, foods):
    path = os.path.join(OUT, vid + '.json')
    usages, failures = [], []
    t = time.time()
    res = run_part(vid, title, foods, usages, failures)
    rec = {"video_id": vid, "title": title, "n_expected": len(foods), "foods": res, "failures": failures,
           "usage": {"cost": round(sum(u['cost'] for u in usages), 6), "calls": usages, "wall_s": round(time.time() - t, 1)}}
    json.dump(rec, open(path, 'w'), indent=1, ensure_ascii=False)
    print(f"{vid} {len(res)}/{len(foods)} cost={rec['usage']['cost']:.4f} cum={state['cost']:.4f} fail={len(failures)}", flush=True)
    return rec


def episodes():
    d = json.load(open(os.path.join(ROOT, 'data.json')))
    eps = defaultdict(list)
    for f in d['foods']:
        m = re.search(r'v=([\w-]{11}).*?[?&]t=(\d+)', f['chapter_url'])
        eps[m.group(1)].append({"id": f['id'], "name": f['name'], "start": int(m.group(2)), "title": f['video_title']})
    for v in eps:
        eps[v].sort(key=lambda x: x['start'])
    return eps


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--video', nargs='*'); ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--budget', type=float, default=4.00); ap.add_argument('--force', action='store_true')
    a = ap.parse_args(); BUDGET = a.budget
    os.makedirs(OUT, exist_ok=True)
    eps = episodes(); vids = a.video or sorted(eps)
    t0 = time.time(); recs = {}
    # resume: count cost of existing outputs
    todo = []
    for v in vids:
        p = os.path.join(OUT, v + '.json')
        if os.path.exists(p) and not a.force:
            recs[v] = json.load(open(p)); state['cost'] += recs[v]['usage']['cost']
        else:
            todo.append(v)
    with ThreadPoolExecutor(a.workers) as ex:
        for v, r in zip(todo, ex.map(lambda v: do_episode(v, eps[v][0]['title'], eps[v]), todo)):
            recs[v] = r
    summ = {"total_cost": round(sum(r['usage']['cost'] for r in recs.values()), 6), "budget_stopped": state['stop'],
            "wall_s_this_run": round(time.time() - t0, 1),
            "episodes": {v: {"cost": r['usage']['cost'], "n": len(r['foods']), "expected": r['n_expected'],
                             "tokens": {k: sum((u['tokens'].get(k) or 0) for u in r['usage']['calls']) for k in ('prompt_tokens', 'completion_tokens', 'total_tokens')},
                             "wall_s": r['usage']['wall_s'], "failures": r['failures']} for v, r in recs.items()}}
    json.dump(summ, open(os.path.join(OUT, 'summary.json'), 'w'), indent=1)
    print("TOTAL", summ['total_cost'], "stopped" if state['stop'] else "")
