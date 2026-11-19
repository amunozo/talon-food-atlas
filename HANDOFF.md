# HANDOFF

**Last updated:** 2026-11-19 11:14 CET, Claude Code. Task: Talon Food Atlas — v1 + per-food reasons/cards done; awaiting owner OK to publish.

## Where things stand
`index.html` (~1.06 MB, self-contained) + `og.png`, `favicon.png`, `apple-touch-icon.png`. Food dialogs now show "Why this tier" (AI summary from captions; Breads from a Gemini transcript) and the nutrition card (AI-read by Gemini 3.1 Flash Lite). Veal/Walnut Oil corrected to B.
Check: `python3 build.py && python3 -m pytest -q test_build_data.py` → 813 foods, 12 moved; 34 passed.

## Last changes (2026-11-19)
- Pipeline in `pipeline/`: fetch_captions.py, slice_all.py, extract_cards.py (Flash Lite, $1.26 for 30 eps), why_from_video.py (--transcribe for caption-less episodes). Outputs in `pipeline/out/` (why/, cards/, tier_disputes.json). `pipeline/cache/` = Talon's captions/transcripts, git-ignored, never publish.
- build_data.py merges why + normalised cards; override tables for CSV fixes (Lentils, Grains board link, notes, Veal/Walnut → B) and Talon's card errata.
- Audit (`notes/audit-why-and-tiers.md`): strict error ~3% of foods in sample; 31 why texts edited (uncertain compound names dropped). OpenRouter spend total ≈ $2.55.

## Next steps
1. Owner OK to publish: create public repo amunozo/talon-food-atlas (About links its Issues; exclude pipeline/cache) and copy the 4 site files to `talon-food-atlas/` in amunozo.github.io (main) and push.
2. Optional: README + write-up for amunozo.com (owner to give name/role line).
3. Post: Show HN / r/nutrition (check rules) / Talon's audience.

## Watch out
- Edit `template.html`, never `index.html`; rerun `python3 build.py`.
- Owner rule: code via subagents, Sonnet/Haiku; Opus only for front-end; Fable only when asked.
- Give each parallel subagent its own scratch folder (shared folders got overwritten once).
- Flash Lite's `tier_on_board` confuses A and ★ (44 cases) — don't use it as tier truth; CSV + captions are.
- Card duplicates left as extracted: French Bread B3, Heart (Turkey) B6, Romano Calcium, Sweet Tea Iron, Pinto Beans B6.
- Not a git repo yet.

## Notes
- `notes/SPEC.md` — schema, corrections, data fixes, UI contract (Round 3/4 sections override older bullets).
- `notes/audit-why-and-tiers.md` — faithfulness audit + tier disputes.
- `notes/pilot-reasons-seaweed.md` (+ `notes/pilot/`) — model pilots (Neon vs Flash Lite vs captions), costs.
- `notes/costs.tsv` — agentcost ledger.
- `reports/Talon tier list open questions.md` — V tier + fan transcription research.
