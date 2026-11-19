import pytest
from build_data import build, TIERS


@pytest.fixture(scope="module")
def data():
    return build()


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def by_name(data, n):
    return [f for f in data["foods"] if f["name"] == n]


def test_counts(data):
    assert len(data["foods"]) == 813
    assert len(data["groups"]) == 28
    assert sum(g["group_tier"] is not None for g in data["groups"]) == 22
    assert sum(g["count"] for g in data["groups"]) == 813
    assert [g["name"] for g in data["groups"]] == sorted(g["name"] for g in data["groups"])


def test_tiers(data):
    ids = [t["id"] for t in TIERS]
    assert ids == ["★", "A", "B", "C", "D", "F", "V"]
    assert all(f["tier"] in ids and f["original_tier"] in ids for f in data["foods"])
    assert all(g["group_tier"] in ids for g in data["groups"] if g["group_tier"])


@pytest.mark.parametrize("name,tier,orig", [
    ("Kefir", "★", "A"), ("Eggplant", "C", "D"), ("Diet Soda", "D", "F"),
    ("Beer", "F", "D"), ("Wine", "F", "D"),
    ("Canola Oil", "C", "B"), ("Safflower Oil", "C", "A"), ("Sunflower Oil", "C", "A"),
    ("Swordfish", "C", "B"), ("Sardine", "A", "B"), ("Macadamia Nuts", "A", "B"),
])
def test_corrections(data, name, tier, orig):
    rows = by_name(data, name)
    assert rows
    for f in rows:
        assert f["tier"] == tier and f["original_tier"] == orig and f["moved"]


def test_lentils_two_rows(data):
    rows = by_name(data, "Lentils")
    assert len(rows) == 2
    for f in rows:
        if f["group"] == "Seeds":
            assert (f["tier"], f["original_tier"], f["moved"]) == ("A", "B", True)
        else:
            assert f["group"] == "Plant Proteins"
            assert (f["tier"], f["original_tier"], f["moved"]) == ("B", "B", False)


def test_grains_board_url(data):
    rows = [f for f in data["foods"] if f["group"] == "Grains"]
    assert rows and all(f["board_url"] == "https://www.youtube.com/watch?v=dp_1u2KJx-0&t=1031s" for f in rows)


def test_evidence_notes(data):
    assert not any("Sources" in f["evidence_note"] for f in data["foods"])
    for n in ("Teff", "Triticale", "Wheat", "Wild Rice"):
        for f in by_name(data, n):
            assert "viewer's transcription in the video comments (see About)" in f["evidence_note"]


def test_meta(data):
    m = data["meta"]
    assert m["placements"] == 813 and m["food_episodes"] == 30 and m["moved"] == 12
    assert m["distinct_names"] == len({f["name"] for f in data["foods"]})
    assert m["food_groups_episode"]["published"] == "2026-11-12"
    assert m["food_groups_episode"]["url"] == "https://www.youtube.com/watch?v=S_2GOvD6Y8k"


@pytest.mark.parametrize("name", ["Olive", "Fig (Dried)", "Portobella", "Milk", "Chia Seed", "Hemp Seed"])
def test_unchanged(data, name):
    rows = by_name(data, name)
    assert rows and any(f["correction"] for f in rows)
    assert all(not f["moved"] for f in rows)


def test_curry(data):
    assert [f["tier"] for f in by_name(data, "Curry Powder")] == ["V"]


def test_moved_flag(data):
    assert all(f["moved"] == (f["tier"] != f["original_tier"]) for f in data["foods"])


def test_colours(data):
    cols = [g["color"] for g in data["groups"]]
    assert len(set(cols)) == 28
    for c in cols:
        assert 1.05 / (lum(c) + 0.05) >= 4.5, c


def test_group_videos(data):
    import re
    g = {x["name"]: x for x in data["groups"]}
    d = g["Dairy"]["videos"]
    assert len(d) == 1 and d[0]["title"] == "Dairy Ranked - Nutrition Tier Lists"
    assert "t=" not in d[0]["url"]
    assert re.match(r"^https://www\.youtube\.com/watch\?v=[\w-]+$", d[0]["url"])
    for n in ("Meats", "Fruits"):
        v = g[n]["videos"]
        assert len(v) == 2 and "Part 2" in v[1]["title"] and "Part 2" not in v[0]["title"]
    for x in data["groups"]:
        if x["count"] > 0:
            assert len(x["videos"]) >= 1
    assert g["Eggs"]["videos"] == [] and g["Soy"]["videos"] == []


NUM = ["calories", "protein_g", "fat_g", "carbs_g", "fiber_g", "sugar_g", "sodium_mg"]
BASES = {"per 100 g", "per 8 fl oz", "per 5 g", "per 85 g", "per 50 g", "per 57 g", "per 45 g",
         "per 113 g", "per 30 g", "per 28 g", "per 67 g", "per 56 g"}


def test_why(data):
    assert all(f["why"] and f["why_source"] in ("captions", "transcript") for f in data["foods"])
    assert all("tier_on_board" not in f and "repairs" not in f and "confidence" not in f for f in data["foods"])
    assert [f["why_source"] for f in data["foods"] if f["group"] == "Breads"] == \
        ["transcript"] * sum(f["group"] == "Breads" for f in data["foods"])


def test_cards(data):
    cards = [f["card"] for f in data["foods"] if f["card"]]
    assert len(cards) >= 800
    for c in cards:
        for k in NUM:
            assert c[k] is None or (isinstance(c[k], (int, float)) and not isinstance(c[k], bool))
        assert c["basis"] in BASES
        assert set(c["approx"]) <= set(NUM) and set(c["lt"]) <= set(NUM)
        assert all(c[k] is not None for k in c["approx"] + c["lt"])
        assert c["omega3"] is None or isinstance(c["omega3"], str)
        assert all(isinstance(m["dv"], (int, float)) and isinstance(m["n"], str) for m in c["micros"])
        dv = [m["dv"] for m in c["micros"]]
        assert dv == sorted(dv, reverse=True)
        assert set(c) == {"basis", *NUM, "approx", "lt", "omega3", "micros"}


def test_parse_num():
    from build_data import parse_num, normalise_basis
    assert parse_num("~5g") == (5, "approx") and parse_num("<1") == (1, "lt")
    assert parse_num("860") == (860, None) and parse_num(None) == (None, None) and parse_num("x") == (None, None)
    assert normalise_basis("per 8 fl. oz.") == "per 8 fl oz" == normalise_basis("Per 8 fl. oz")


@pytest.mark.parametrize("name", ["Veal", "Walnut Oil"])
def test_veal_walnut_oil_b(data, name):
    (f,) = by_name(data, name)
    assert (f["tier"], f["original_tier"], f["moved"]) == ("B", "B", False)
    assert f["evidence_note"] == ("Tier corrected from A to B: Talon says “round out our list in the B tier” "
                                  "and the final board shows B; the source data had read A from the item’s transition.")
    assert "B tier" in f["why"] and "A tier" not in f["why"]


def _micro(f, n):
    return [m["dv"] for m in f["card"]["micros"] if m["n"] == n]


def test_card_errata(data):
    milk = next(f for f in by_name(data, "Milk") if f["group"] == "Drinks")
    assert _micro(milk, "Phosphorus") == [22] and _micro(milk, "Potassium") == [10]
    (porto,) = by_name(data, "Portobella")
    assert _micro(porto, "Vitamin B3") == [24] and _micro(porto, "Vitamin B6") == [7]
    (chia,) = by_name(data, "Chia Seed")
    assert chia["card"]["carbs_g"] == 42 and "carbs_g" not in chia["card"]["approx"]
    assert _micro(chia, "Vitamin K") == []
    (hemp,) = by_name(data, "Hemp Seed")
    assert _micro(hemp, "Vitamin E") == []
    dairy = next(f for f in by_name(data, "Milk") if f["group"] == "Dairy")
    assert _micro(dairy, "Phosphorus") == [12]  # Dairy Milk card untouched


def test_no_new_duplicate_micros(data):
    from build_data import duplicate_micros
    # Remaining duplicates are source-card ambiguities with no creator erratum (left as extracted).
    assert duplicate_micros(data["foods"]) == {
        ("Breads", "French Bread"): ["Vitamin B3"], ("Organ Meats", "Heart (Turkey)"): ["Vitamin B6"],
        ("Cheese", "Romano"): ["Calcium"], ("Drinks", "Sweet Tea"): ["Iron"],
        ("Beans", "Pinto Beans"): ["Vitamin B6"],
    }
