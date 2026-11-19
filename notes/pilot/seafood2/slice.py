import json
j=json.load(open('dl/rjsi_Dz3wAM.en.json3'))
info=json.load(open('dl/rjsi_Dz3wAM.info.json'))
words=[]  # (start_s, text) per seg word
for e in j['events']:
    if 'segs' not in e: continue
    for s in e['segs']:
        t=s['utf8'].replace('\n',' ')
        if t.strip(): words.append((e['tStartMs']/1000+s.get('tOffsetMs',0)/1000,t.strip()))
chs=[c for c in info['chapters'] if c['title'] not in('Intro','Conclusion')]
PAD=6
out={}
for c in chs:
    a,b=c['start_time'],c['end_time']
    # word-level slice: from a-PAD to b+PAD (overlap), mark core
    ws=[(s,t) for s,t in words if a-PAD<=s<b+PAD]
    out[c['title']]={"start":a,"end":b,"text":' '.join(t for s,t in ws),"core":' '.join(t for s,t in words if a<=s<b)}
json.dump(out,open('slices.json','w'),indent=1)
print(len(words),sum(len(v['text']) for v in out.values()))
