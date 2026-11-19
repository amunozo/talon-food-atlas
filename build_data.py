#!/usr/bin/env python3
"""Build data.json from talon-food-atlas-rankings.csv (stdlib only)."""
import copy
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "talon-food-atlas-rankings.csv")
OUT_PATH = os.path.join(HERE, "data.json")
WHY_DIR = os.path.join(HERE, "pipeline", "out", "why")
CARDS_DIR = os.path.join(HERE, "pipeline", "out", "cards")
NUM_FIELDS = ["calories", "protein_g", "fat_g", "carbs_g", "fiber_g", "sugar_g", "sodium_mg"]

TIERS = [
    {"id": "★", "label": "★", "color": "#ff7f7f"},
    {"id": "A", "label": "A", "color": "#ffbf7f"},
    {"id": "B", "label": "B", "color": "#ffdf7f"},
    {"id": "C", "label": "C", "color": "#ffff7f"},
    {"id": "D", "label": "D", "color": "#bfff7f"},
    {"id": "F", "label": "F", "color": "#7fff7f"},
    {"id": "V", "label": "V", "color": "#7fbfff"},
]

# name -> corrected tier (applied to every row with that name, e.g. both Lentils rows)
CORRECTIONS = {
    "Kefir": "★", "Macadamia Nuts": "A",
    "Canola Oil": "C", "Safflower Oil": "C", "Sunflower Oil": "C",
    "Beer": "F", "Wine": "F", "Swordfish": "C", "Lentils": "A",  # Lentils: Seeds row only, see below
    "Sardine": "A", "Diet Soda": "D", "Eggplant": "C",
}

# Lentils appears twice; the correction applies only to the row carrying the
# correction text (Seeds). The Plant Proteins row stays B, moved=false.
def correction_applies(r):
    if r["food_or_group"] == "Lentils":
        return bool(r["creator_correction"])
    return r["food_or_group"] in CORRECTIONS


# The CSV's board_url for every Grains row is &t=870s (Triticale's chapter, mid-video).
# The final board is the "Conclusion" chapter of the Grains video, which starts at 1031s
# (chapters: ... Wheat 893, Wild Rice 999, Conclusion 1031; video length 1117s).
GRAINS_BOARD_URL = "https://www.youtube.com/watch?v=dp_1u2KJx-0&t=1031s"

# Evidence notes that pointed to "Sources", which does not exist in the page; the transcription
# is a viewer comment on the video, described in the About dialog.
OLD_NOTE = "Late placement cross-checked against the fan transcription linked in Sources."
NEW_NOTE = "Late placement cross-checked against a viewer's transcription in the video comments (see About)."
NOTE_OVERRIDES = {("Grains", n): NEW_NOTE for n in ("Teff", "Triticale", "Wheat", "Wild Rice")}

# Talon's own card errata (CSV creator_correction column, CSV untouched): (group, name) -> fixer(card).
def _rename_micro(old, new, which):
    """Rename the smaller/second duplicate micro `old` to `new`."""
    def fix(card):
        idx = [i for i, m in enumerate(card["micros"]) if m["n"] == old]
        if len(idx) < 2:
            return
        idx = min(idx, key=lambda i: card["micros"][i]["dv"]) if which == "smaller" else idx[1]
        card["micros"][idx]["n"] = new
    return fix


def _drop_micro(name):
    def fix(card):
        card["micros"] = [m for m in card["micros"] if m["n"] != name]
    return fix


def _set_num(field, value):
    def fix(card):
        card[field] = value
        card["approx"] = [k for k in card["approx"] if k != field]
        card["lt"] = [k for k in card["lt"] if k != field]
    return fix


CARD_ERRATA = {
    ("Drinks", "Milk"): [_rename_micro("Phosphorus", "Potassium", "smaller")],
    ("Mushrooms", "Portobella"): [_rename_micro("Vitamin B3", "Vitamin B6", "second")],
    ("Seeds", "Chia Seed"): [_set_num("carbs_g", 42), _drop_micro("Vitamin K")],
    ("Seeds", "Hemp Seed"): [_drop_micro("Vitamin E")],
}


def duplicate_micros(foods):
    """-> {(group, name): [duplicate micro names]} for foods whose card repeats a micro name."""
    res = {}
    for f in foods:
        c = f.get("card")
        if c:
            names = [m["n"] for m in c["micros"]]
            d = sorted({n for n in names if names.count(n) > 1})
            if d:
                res[(f["group"], f["name"])] = d
    return res


# CSV misreads (placement read from the item's transition): captions say "round out our list in the
# B tier" and the final board shows B. (group, name) -> corrected original tier and evidence note.
TIER_FIX_NOTE = ("Tier corrected from A to B: Talon says \u201cround out our list in the B tier\u201d and the final "
                 "board shows B; the source data had read A from the item\u2019s transition.")
TIER_OVERRIDES = {("Meats", "Veal"): "B", ("Fats & Oils", "Walnut Oil"): "B"}

# emoji, colour (all >= 4.5:1 against white)
GROUP_STYLE = {
    "Beans": ("🫘", "#86412c"),
    "Breads": ("🍞", "#8b492a"),
    "Breakfast": ("🥞", "#b2580b"),
    "Candy": ("🍬", "#c2185b"),
    "Cereals": ("🥣", "#946d00"),
    "Cheese": ("🧀", "#a66403"),
    "Condiments": ("🧂", "#5d6d7e"),
    "Dairy": ("🥛", "#666db4"),
    "Drinks": ("🥤", "#0260a6"),
    "Eggs": ("🥚", "#8a6d3b"),
    "Fats & Oils": ("🫒", "#45712d"),
    "Flours": ("🌾", "#715d40"),
    "Fruits": ("🍎", "#c62828"),
    "Grains": ("🌽", "#7a770f"),
    "Herbs & Spices": ("🌿", "#2e7d32"),
    "Meats": ("🥩", "#9f1c35"),
    "Milks": ("🍼", "#4a6fa5"),
    "Mushrooms": ("🍄", "#795b56"),
    "Nuts": ("🥜", "#9b540e"),
    "Organ Meats": ("🫀", "#8e244d"),
    "Plant Proteins": ("🌱", "#3b7d4f"),
    "Seafood": ("🐟", "#277596"),
    "Seaweed": ("🪸", "#056965"),
    "Seeds": ("🌻", "#86720e"),
    "Snacks": ("🍿", "#b34700"),
    "Soy": ("🫛", "#4a7a27"),
    "Sweets": ("🍰", "#ad1457"),
    "Vegetables": ("🥦", "#1b7a43"),
}


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _video_id(url):
    m = re.search(r"[?&]v=([\w-]+)", url or "")
    return m.group(1) if m else None


def parse_num(v):
    """-> (number or None, flag) where flag is "approx" ("~"), "lt" ("<") or None."""
    if v is None or isinstance(v, bool):
        return None, None
    if isinstance(v, (int, float)):
        return v, None
    m = re.fullmatch(r"\s*([~<]?)\s*(\d+(?:\.\d+)?)\s*(?:g|mg)?\s*", str(v))
    if not m:
        return None, None
    n = float(m.group(2))
    n = int(n) if n == int(n) else n
    return n, {"~": "approx", "<": "lt"}.get(m.group(1))


def normalise_basis(b):
    if not b:
        return None
    b = re.sub(r"\s+", " ", str(b).strip()).replace("fl.", "fl").rstrip(".")
    return b[0].lower() + b[1:] if b[:3].lower() == "per" else b


def normalise_card(c):
    if not isinstance(c, dict):
        return None
    out = {"basis": normalise_basis(c.get("basis"))}
    approx, lt = [], []
    for k in NUM_FIELDS:
        n, flag = parse_num(c.get(k))
        out[k] = n
        if n is not None and flag == "approx":
            approx.append(k)
        elif n is not None and flag == "lt":
            lt.append(k)
    out["approx"], out["lt"] = approx, lt
    o = c.get("omega3")
    if isinstance(o, dict) and o.get("amount") not in (None, ""):
        o = f"{o['amount']} {o.get('unit') or ''}".strip()
    out["omega3"] = str(o) if o not in (None, "") and not isinstance(o, dict) else None
    micros = []
    for m in c.get("micros") or []:
        dv, _ = parse_num(m.get("pct_dv"))
        if dv is not None and m.get("nutrient"):
            micros.append({"n": m["nutrient"], "dv": dv})
    micros.sort(key=lambda m: -m["dv"])
    out["micros"] = micros
    return out


def load_why():
    """food id -> (why, why_source)."""
    res = {}
    if not os.path.isdir(WHY_DIR):
        return res
    for fn in sorted(os.listdir(WHY_DIR)):
        if not fn.endswith(".json") or fn.endswith(".usage.json"):
            continue
        items = _load_json(os.path.join(WHY_DIR, fn))
        if not isinstance(items, list):
            continue
        for it in items:
            if isinstance(it, dict) and isinstance(it.get("id"), int):
                src = "transcript" if "transcript" in str(it.get("note") or "").lower() else "captions"
                res[it["id"]] = (it.get("why") or "", src)
    return res


def load_cards():
    """(video id, food name) -> normalised card."""
    res = {}
    if not os.path.isdir(CARDS_DIR):
        return res
    for fn in sorted(os.listdir(CARDS_DIR)):
        if not fn.endswith(".json") or fn == "summary.json":
            continue
        d = _load_json(os.path.join(CARDS_DIR, fn))
        if not isinstance(d, dict):
            continue
        vid = d.get("video_id") or fn[:-5]
        for x in d.get("foods") or []:
            card = normalise_card(x.get("card"))
            if card and x.get("food"):
                res[(vid, x["food"])] = card
    return res


def build():
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    group_rank = {}
    foods = []
    for r in rows:
        if r["entry_type"] == "food group":
            group_rank[r["food_or_group"]] = r
            continue
        orig = r["original_tier"]
        key = (r["food_group"], r["food_or_group"])
        if key in TIER_OVERRIDES:
            orig = TIER_OVERRIDES[key]
        tier = orig
        corr = r["creator_correction"]
        if correction_applies(r):
            tier = CORRECTIONS[r["food_or_group"]]
        board_url = GRAINS_BOARD_URL if r["food_group"] == "Grains" else r["board_url"]
        note = r["evidence_note"]
        if (r["food_group"], r["food_or_group"]) in NOTE_OVERRIDES:
            note = note.replace(OLD_NOTE, NOTE_OVERRIDES[(r["food_group"], r["food_or_group"])])
        if key in TIER_OVERRIDES:
            note = TIER_FIX_NOTE
        foods.append({
            "id": len(foods),
            "name": r["food_or_group"],
            "group": r["food_group"],
            "tier": tier,
            "original_tier": orig,
            "moved": tier != orig,
            "correction": corr,
            "video_title": r["video_title"],
            "published": r["published"],
            "chapter_url": r["chapter_url"],
            "board_url": board_url,
            "nutrition_frame_url": r["nutrition_frame_url"],
            "serving_basis": r["serving_basis"],
            "evidence_note": note,
        })
    why, cards = load_why(), load_cards()
    for f in foods:
        w, src = why.get(f["id"], ("", "captions"))
        f["why"], f["why_source"] = w, src
        card = cards.get((_video_id(f["chapter_url"]), f["name"]))
        if card is not None and (f["group"], f["name"]) in CARD_ERRATA:
            card = copy.deepcopy(card)
            for fix in CARD_ERRATA[(f["group"], f["name"])]:
                fix(card)
        f["card"] = card
    counts = {}
    for f in foods:
        counts[f["group"]] = counts.get(f["group"], 0) + 1
    vids = {}
    for f in foods:
        m = re.search(r"[?&]v=([\w-]+)", f["chapter_url"])
        if m:
            vids.setdefault(f["group"], {})[m.group(1)] = (f["published"], f["video_title"])
    groups = []
    all_groups = set(counts) | {r["food_group"] for r in rows}  # Eggs, Soy have only a group row
    for name in sorted(all_groups):
        emoji, color = GROUP_STYLE[name]
        gr = group_rank.get(name)
        groups.append({
            "name": name, "emoji": emoji, "color": color,
            "group_tier": gr["original_tier"] if gr else None,
            "group_chapter_url": gr["chapter_url"] if gr else "",
            "count": counts.get(name, 0),
            "videos": [
                {"title": t, "url": "https://www.youtube.com/watch?v=" + v, "published": p}
                for v, (p, t) in sorted(vids.get(name, {}).items(), key=lambda kv: (kv[1][0], kv[1][1]))
            ],
        })
    fg = [r for r in rows if r["entry_type"] == "food group"]
    meta = {
        "placements": len(foods),
        "distinct_names": len({f["name"] for f in foods}),
        "food_episodes": len({m.group(1) for f in foods
                              for m in [re.search(r"[?&]v=([\w-]+)", f["chapter_url"])] if m}),
        "food_groups_episode": {
            "title": "Food Groups Ranked",
            "url": "https://www.youtube.com/watch?v=S_2GOvD6Y8k",
            "published": fg[0]["published"],
        },
        "moved": sum(f["moved"] for f in foods),
    }
    return {"tiers": TIERS, "groups": groups, "foods": foods, "meta": meta}


def main():
    data = build()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    moved = sum(x["moved"] for x in data["foods"])
    print(f"wrote {OUT_PATH}: {len(data['foods'])} foods, "
          f"{len(data['groups'])} groups, {moved} moved")


if __name__ == "__main__":
    main()
