import json,os,sys,time,urllib.request,urllib.error
mode=sys.argv[1]
retry=len(sys.argv)>2
key=json.load(open(os.path.expanduser('~/.pi/agent/auth.json')))['openrouter']['key']
foods=[("Chlorella",129),("Dulse",237),("Irish Moss",284),("Kelp",341),("Nori",397),("Ogo",439),("Sea Grapes",472),("Spirulina",510),("Wakame",582)]
flist="\n".join(f"- {n} (chapter starts at {t}s)" for n,t in foods)
STRICT="\n\nIMPORTANT: output must be a single valid JSON object that parses with json.loads: no markdown fences, no commentary, no trailing commas, all strings properly escaped."
prompt=f"""You are watching an episode of Talon Fitness's "Nutrition Tier Lists" (Seaweed Ranked). For each food below, extract from the video:
- "why": 1-2 sentences paraphrasing Talon's reasons (key nutrients/benefits, downsides, verdict). No long quotes; nothing he does not say.
- "key_nutrients": read from the on-screen nutrition card for that food: list of objects {{"nutrient","amount","unit","pct_dv" (null if not shown),"basis" (e.g. "per 100 g")}}. Include the numbers visible on the card (up to 8 most prominent). Do not invent numbers; use [] if the card is not legible.
- "tier_on_board": the tier this food is placed in on the final tier-list board (use the symbol shown, e.g. "A","B", or the star tier as "★").
Also give "episode_summary": 2-3 sentences.
Foods:
{flist}
Return strict JSON only, no markdown fences: {{"episode_summary": "...", "foods": [{{"food","why","key_nutrients","tier_on_board"}}]}}"""
if retry: prompt+=STRICT
if mode=='url':
    vid={"type":"video_url","video_url":{"url":"https://www.youtube.com/watch?v=0U_cjYFpwqE"}}
else:
    import base64
    b=base64.b64encode(open('dl/video.mp4','rb').read()).decode()
    vid={"type":"video_url","video_url":{"url":"data:video/mp4;base64,"+b}}
body={"model":"google/gemini-3.1-flash-lite","messages":[{"role":"user","content":[{"type":"text","text":prompt},vid]}],"usage":{"include":True},"temperature":0}
req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
t=time.time()
try:
    r=urllib.request.urlopen(req,timeout=900); raw=r.read().decode(); code=r.status
except urllib.error.HTTPError as e:
    raw=e.read().decode(); code=e.code
dt=time.time()-t
open(f'rawC_flashlite{'_retry' if retry else ''}.json','w').write(raw.replace(key,'REDACTED'))
print(code,round(dt,1),'s'); print(raw[:1500].replace(key,'REDACTED'))
