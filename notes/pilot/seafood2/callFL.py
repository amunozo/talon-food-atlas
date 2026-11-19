import json,os,sys,time,urllib.request,urllib.error
# usage: callFL.py <tag> [lo hi]  (lo/hi = food index range for split calls)
tag=sys.argv[1]
lo,hi=(int(sys.argv[2]),int(sys.argv[3])) if len(sys.argv)>3 else (0,42)
key=json.load(open(os.path.expanduser('~/.pi/agent/auth.json')))['openrouter']['key']
import csv
rows=[r for r in csv.DictReader(open('/home/alberto/projects/personal/data/talon-food-atlas/talon-food-atlas-rankings.csv',encoding='utf-8-sig')) if r['video_title'].startswith('Seafood Ranked Part 2')]
rows.sort(key=lambda r:int(r['chapter_seconds']))
foods=[(r['food_or_group'],int(r['chapter_seconds'])) for r in rows][lo:hi]
flist="\n".join(f"- {n} (chapter starts at {t}s)" for n,t in foods)
prompt=f"""You are watching an episode of Talon Fitness's "Nutrition Tier Lists" ("Seafood Ranked Part 2"). For each food below, extract from the video:
- "why": EXACTLY 2 sentences paraphrasing what Talon says about that food. They must include, whenever he gives them: (a) his tier verdict (which tier he puts it in, or that it is top tier / star), (b) any serving or portion limits he gives (e.g. "no more than X oz per week"), (c) 4 to 6 named nutrients or health benefits he mentions, (d) downsides he mentions (e.g. mercury, sodium, purines, contaminants). Paraphrase only what he says in the video; add nothing from general knowledge. No long quotes.
- "key_nutrients": read from the on-screen nutrition card shown for that food: a list of up to 10 objects {{"nutrient","amount","unit","pct_dv","basis"}} where "amount" is the number only (null if not shown), "unit" is the unit of the amount (g, mg, mcg, kcal; null if none), "pct_dv" is the percent daily value as a number only without the % sign (null if not shown) and "basis" is the serving basis printed on the card (e.g. "per 100 g"). Always include (if shown) calories, protein, fat, omega-3 (DHA+EPA) and sodium, then fill the remaining slots with the card's top micronutrients. Do not invent numbers; use [] if the card is not legible.
- "tier_on_board": the tier this food is placed in on the tier-list board (use the symbol shown, e.g. "A","B","C","D", or the star tier as "★").
Also give "episode_summary": 2-3 sentences that name the foods in the top (star) tier.
Foods:
{flist}
Return strict JSON only: a single valid JSON object that parses with json.loads, no markdown fences, no commentary: {{"episode_summary": "...", "foods": [{{"food","why","key_nutrients","tier_on_board"}}]}}"""
vid={"type":"video_url","video_url":{"url":"https://www.youtube.com/watch?v=rjsi_Dz3wAM"}}
body={"model":"google/gemini-3.1-flash-lite","messages":[{"role":"user","content":[{"type":"text","text":prompt},vid]}],"usage":{"include":True},"temperature":0}
req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
t=time.time()
try:
    r=urllib.request.urlopen(req,timeout=1200); raw=r.read().decode(); code=r.status
except urllib.error.HTTPError as e:
    raw=e.read().decode(); code=e.code
dt=time.time()-t
open(f'raw_{tag}.json','w').write(raw.replace(key,'REDACTED'))
open(f'wall_{tag}.txt','w').write(str(round(dt,1)))
print(code,round(dt,1),'s'); print(raw[:600].replace(key,'REDACTED'))
