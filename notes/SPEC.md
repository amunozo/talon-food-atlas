# Talon Food Atlas — tier list spec

Source: `talon-food-atlas-rankings.csv` (UTF-8 with BOM, 835 rows: 813 `food`, 22 `food group`).
Output: one self-contained, read-only `index.html` at the repo root (no network needed, data inlined),
TierMaker look: dark page, tier rows with a coloured label cell on the left and square tiles to the right.

## Files
- `build_data.py` — reads the CSV, writes `data.json` (schema below). Stdlib only.
- `test_build_data.py` — pytest tests for build_data.py.
- `template.html` — UI (HTML+CSS+vanilla JS, no external libs, no CDN). Contains the literal
  placeholder `/*__DATA__*/null` where the JSON goes, e.g. `const DATA = /*__DATA__*/null;`.
  For development it may fall back to `fetch('data.json')` when DATA is null.
- `build.py` — runs build_data and writes `index.html` = template with placeholder replaced by data.json.
- `sample_data.json` — small hand-made sample following the schema, for UI work before real data exists.

## data.json schema
```json
{
  "tiers": [{"id": "★", "label": "★", "color": "#ff7f7f"}, ...],
  "groups": [{"name": "Fruits", "emoji": "🍎", "color": "#2e7d32",
              "group_tier": "★", "group_chapter_url": "https://...", "count": 78}, ...],
  "foods": [{"id": 0, "name": "Kefir", "group": "Dairy", "tier": "★", "original_tier": "A",
             "moved": true, "correction": "Talon later moved Kefir to ★ ...",
             "video_title": "...", "published": "2026-10-29",
             "chapter_url": "...", "board_url": "...", "nutrition_frame_url": "...",
             "serving_basis": "...", "evidence_note": "...",
             "why": "Talon's reasoning, paraphrased (\"\" if missing)",
             "why_source": "captions" | "transcript",   // transcript = Gemini transcript (Breads)
             "card": null | {"basis": "per 100 g", "calories": 180, "protein_g": 25, "fat_g": 8,
                             "carbs_g": null, "fiber_g": null, "sugar_g": null, "sodium_mg": null,
                             "approx": ["fat_g"], "lt": [], "omega3": "2600 mg" | null,
                             "micros": [{"n": "Vitamin D", "dv": 88}, ...]}}, ...]
}
```
- `why`/`card` come from `pipeline/out/why/<video>.json` (matched by food id) and
  `pipeline/out/cards/<video>.json` (matched by video id + food name); absent files give
  `why: ""` and `card: null`. tier_on_board, repairs, confidence and notes stay internal.
- `card`: numeric fields are numbers or null (never strings). `approx` lists fields whose source had
  "~"; `lt` lists fields that had "<" (stored as the bound, e.g. "<1" -> 1). `basis` is normalised
  ("per 8 fl oz", "per 100 g"). `omega3` is a display string ("2600 mg") or null. `micros` are sorted
  by dv descending (% daily value, number).
- Tier order and colours (TierMaker palette): ★ #ff7f7f, A #ffbf7f, B #ffdf7f, C #ffff7f,
  D #bfff7f, F #7fff7f, V #7fbfff. `tiers` lists all seven; the UI hides any row that is empty
  in the current view (in practice only V, which holds Curry Powder only).
- `groups`: all 28 distinct `food_group` values, sorted by name. `group_tier` is Talon's ranking of
  the group (from the 22 `food group` rows) or null when the group was not ranked. Each group gets
  a fitting emoji and a distinct, mid-dark tile background colour that keeps white text readable.
- `foods`: every `food` row, one entry per row (duplicate names across videos stay separate).
  Empty CSV strings become "" (not null). `moved` = tier != original_tier.

## Corrections (tier = corrected tier, original_tier = CSV value)
Apply to every row with that name (Lentils: only the Seeds row, which carries the correction text; the Plant Proteins row stays B, moved=false. Total moved = 12):
Kefir → ★; Macadamia Nuts → A; Canola Oil, Safflower Oil, Sunflower Oil → C; Beer → F; Wine → F;
Swordfish → C; Lentils → A; Sardine → A; Diet Soda → D; Eggplant → C (one tier up from D).
Unchanged but keep the correction text: Olive, Fig (Dried), Portobella, Milk, Chia Seed, Hemp Seed.
Curry Powder keeps tier V.

## UI behaviour
- Header: title "Talon Food Atlas", subtitle "Nutrition tier lists from Talon Fitness videos".
- View selector (a dropdown or tab strip, keyboard accessible) with:
  (Removed 2026-11-19 at the owner's request: an "All foods" board. Talon's tiers are relative within
  each video, so mixing all foods on one board compares unlike scales.)
  1. "Food groups" (default view) — Talon's ranking of the 22 groups: one tile per group (emoji + name), in its group_tier.
  2. One entry per food group with foods (26; Eggs and Soy have none), "<emoji> <name> (<count>)", showing only that group's foods.
- Tile: square (~80px, TierMaker style), group background colour, emoji at top, food name below
  (wraps, shrinks for long names), title attribute with full name. Moved tiles show a small badge
  (e.g. "↑"/"↓" or "✎") in a corner; tiles with a correction but no move show a smaller "i" badge.
- Within a tier row, tiles sort by name.
- Click (or Enter) on a tile opens a details panel/modal: name, group, tier (and "originally X" when
  moved), correction text, serving basis, video title + published date, links "Chapter",
  "Final board", "Nutrition frame" (only those that exist; open in new tab), evidence note. Esc closes.
  Group tiles in "Food groups" view: show group_tier, food count, link to chapter, and a button
  "Show foods" that switches to that group's view.
- Counts: each tier label shows the tier; a small count of tiles in that row.
- Read-only: no drag and drop. Responsive: works at phone width (tiles wrap, no horizontal scroll).
- URL hash keeps the current view (`#groups`, `#group=Fruits`; anything else falls back to `#groups`) so reload/share keeps it.

## Round 3 changes (2026-11-19, owner)
- Font: Arial stack everywhere (owner matched TierMaker visually).
- Clicking a group tile opens its board directly; no group modal. Eggs/Soy (0 foods) don't navigate.
- Group boards show links to the group's own episode(s) from the start (`groups[].videos`), not the
  timestamp into the Food Groups video. Food modals keep per-food timestamp links.
- Food tiles in group boards are text-only (no emoji); group tiles on the ranking board keep emoji.

## Round 4 changes (2026-11-19, Fable design review applied by Opus, owner-approved)
- Unranked tray under the groups board ("–" row) with the 6 groups Talon didn't rank; chip cloud removed.
- Groups board shows an empty D row (48px) so the scale reads ★ A B C D F; group boards still hide empty rows.
- Group colours retuned in build_data.py GROUP_STYLE to separate the browns (contrast still ≥4.5).
- Flat 2px mosaic, no stripe on text tiles, inset-ring hover, smaller header, no "Food groups" button on #groups.
- Food dialog: tier-coloured square with the letter, formatted date, "▶ Watch chapter" as primary link.
- Footer: "Unofficial. Rankings from Talon Fitness's Nutrition Tier Lists videos."

## Data fixes (2026-11-19)
- Grains `board_url` overridden to the Conclusion chapter (`&t=1031s`); CSV had 870s (Triticale).
- Teff/Triticale/Wheat/Wild Rice evidence_note no longer mentions "Sources" (viewer transcription in comments, see About).
- data.json has a top-level `meta` {placements, distinct_names, food_episodes, food_groups_episode{title,url,published}, moved}; JSON is minified.
- Veal (Meats) and Walnut Oil (Fats & Oils): CSV read A from the item's transition, but captions say "round out our list in the B tier" and the board shows B. `TIER_OVERRIDES` in build_data.py sets `original_tier` = `tier` = B (moved=false) and replaces `evidence_note` (CSV untouched).
- Card errata from the CSV creator_correction column (`CARD_ERRATA` in build_data.py): Milk (Drinks) smaller Phosphorus micro renamed Potassium; Portobella second Vitamin B3 renamed Vitamin B6; Chia Seed carbs_g = 42 and Vitamin K micro removed; Hemp Seed Vitamin E micro removed. Remaining duplicate micro names with no erratum (left as extracted): French Bread B3, Heart (Turkey) B6, Romano Calcium, Sweet Tea Iron, Pinto Beans B6.
- Why texts: audit pass (2026-11-19) removed compound names that rested on guessed caption repairs (replaced by general terms) and fixed overstatements; each edited item carries an `audit_edit` field (old -> new) in pipeline/out/why/*.json.
