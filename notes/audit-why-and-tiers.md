# Audit: per-food "why" texts and tier cross-checks

Date: 2026-11-19. Read-only audit by an independent agent; inputs `pipeline/out/why/*.json` (784 foods, Breads `65zUfWGF_wQ` skipped), `pipeline/cache/slices/*.json`, `pipeline/out/cards/*.json`, `data.json`, `talon-food-atlas-rankings.csv`. Machine-readable disputes: `pipeline/out/tier_disputes.json`.

## 1. Summary

**Faithfulness.** The why texts are very faithful to the caption slices. In the 87-item random sample (3 per episode x 29 episodes, seed 20261119) and 25 extra items (every `low` confidence item and every item with an "(uncertain)"/"(approx.)" repair that was not already drawn), 112 items in total, I compared every claim with the slice text.

| | Random sample (n=87) | Whole audited set (n=112, biased toward risky items) |
|---|---|---|
| Contradicted (claim or verdict contradicts the slice) | 1 (1.1%, 95% CI 0.2-6.2%) | 2 |
| Unsupported / overstated vs slice (outside the repair issue) | 2 (2.3%) | 3 |
| Contradicted or unsupported (strict error) | 3 (3.4%, 95% CI 1.2-9.7%) | 5 |
| Repair-dependent claim stated flat (guessed compound name from a garbled caption, presented as fact) | 3 flagged (+7 low-risk) | 18 flagged (+8 low-risk) |
| Any of the above (item has at least one issue to fix) | 6 (6.9%, 95% CI 3.2-14.2%) | 23 |

Intervals are Wilson 95% on item-level counts. At claim level (about 9 to 10 factual claims per why, roughly 1,000 claims in the sample) the strict error rate is about 0.5%.

Other population-wide checks (all 784 whys, mechanical):
- **Verdict tier vs `original_tier`: 784/784 match** (the last "X tier" in each why equals `original_tier`; 4 texts also mention an alternative tier in a hedge, which is faithful to the caption: Brussels Sprout, Mini Wheats, Safflower Oil, Sunflower Oil).
- **Numbers not in the slice:** only 4 of 784 whys contain a numeral that is absent from its slice: Chestnuts "about 10 grams" (slice: 10.6, harmless rounding), Kale "indole-3-carbinol" (the 3 comes from a repair of "endocrine carbonyl"), Hash Browns "half-baked" (word, not a number), Salmon "0.022 ppm" (caption "0.8 022", a best-guess repair). No invented figures.
- **Outside nutrition knowledge:** none added as new claims in the 112 items read. The only outside knowledge is inside caption repairs (guessing which compound a garbled word is), see section 3.
- Tiers that follow `original_tier` against a caption that says something else: Veal and Walnut Oil (below). All other garbled tier words ("beads here", "seeds here", "AIDS here") decode to the stated verdict.

**Tier disputes.** 47 foods have a Flash Lite `tier_on_board` different from the CSV `original_tier` (737/784 agree, 94.0%). Caption verdicts (own verdict decoded from the slice; 774 of 784 foods have one, 10 have none that I could attribute to this food) agree with the CSV in 772/774. Result: **2 strong** (captions and board both against the CSV: Veal and Walnut Oil, both CSV A, caption and board B), **0 captions-only**, **45 board-only**. Of the 45 board-only cases, 44 are A/star swaps or a one-off misread where the caption explicitly confirms the CSV (28 CSV A read as star, 16 CSV star read as A, plus Pomegranate star read as B), and 1 (Soybeans) has an ambiguous caption. Treat board-only as Flash Lite noise unless a human looks at the frame; the strong pair is where the CSV is probably wrong.

## 2. Method

- Sample: 29 episodes (30 minus Breads), `random.Random(20261119).sample(foods_in_episode, 3)` per episode = 87 random items. Added the 4 `low`-confidence items (Veal, Walnut Oil, Nopal, Graham Crackers) and every item with an "(uncertain)"/"(approx.)" repair; 29 flagged items in total, 4 of which were already in the random draw, so 25 extras (112 audited). The ask said 90; there are 29 audited episodes so 87 is the exact 3-per-episode count.
- Each why was read against its full slice. Claims classified: supported / unsupported / contradicted / repair-dependent. Tier verdict checked against `original_tier` and the slice. Slices overlap neighbours (the previous food's verdict opens the slice; the next food's intro closes it), so verdicts were read from the passage that follows this food's own description.
- Disputes: for every one of the 784 foods, CSV `original_tier` vs Flash Lite `tier_on_board` and vs the caption verdict. Caption verdict extracted with a regex over decoded tier words (a/aids/eights/aer/a tear = A; b/be/beads/beets/beats/beach = B; c/sea/seeds/se/ca/seats = C; d/deeds/deter/dti/detier = D; f = F; top tier/top-tier/top two here = star; v = V), taking the verdict that sits right before the next food's intro, cross-checked against the early part of the next slice (697 agree, 8 conflict, all 8 resolved by reading: 7 are next-food bleed or hedges, 1 is the Safflower/Sunflower oil high-oleic split). Every dispute and every conflict was then read by hand. Limit: 10 foods have no attributable caption verdict (Chlorella, Soybeans, Frozen Yogurt, Peach ("Z tier"), Liver (Turkey) (verdict not spoken), Mozzarella, Herring, Chinook Salmon, Venison, Butter). For Chlorella, Herring, Chinook Salmon and Venison the phrase read by hand ("top tier placement" / "a tier placement") agrees with the CSV; the other six give no usable caption evidence, and their board reading equals the CSV except Soybeans. Salmon (id 690) was filled in by hand ("comfortable top tier placement").

## 3. Problem items (faithfulness)

### 3a. Contradicted

| id | Food | Offending phrase in why | Slice says | Suggested fix |
|---|---|---|---|---|
| 420 | Veal | "so the verdict is the A tier" | "it's going to round out our list in the B tier" (also board B) | Verdict B tier, or keep A only if the CSV is intentionally kept and add "(caption says B)"; better to fix CSV to B. Also unlisted repair: "conjugated lolic acid" -> conjugated linoleic acid, add to repairs. |
| 618 | Walnut Oil | "which the board places in the A tier" | "round out our list in the B tier"; Flash Lite board also B | "he puts it in the B tier" (or A only if CSV is kept deliberately). The sentence also invents "the board" as a source. |

### 3b. Unsupported or overstated (minor)

| id | Food | Offending phrase | Slice says | Fix |
|---|---|---|---|---|
| 773 | Brazil Nuts | "among the best copper, vitamin B1 and antioxidants" | copper among the best; B1 only "rounding out the notable micronutrients" | "among the best copper, plus notable vitamin B1" |
| 634 | Milk | "whey lowers blood pressure" | "Whey is shown to manage blood pressure levels" | "whey helps manage blood pressure" |
| 468 | Nutritional Yeast (Fortified) | "a leading plant-based B12 source" | "often one of the better sources for plant-based diets of vitamin B12" | "often one of the better plant-based B12 sources" |

### 3c. Repair-dependent claims stated flat (guessed compound names)

The caption words are garbled and the why states the guessed compound as fact. Suggested general fix: hedge in the text ("an antioxidant (name garbled in the captions, likely quercetin)") or drop the name and keep the benefit.

| id | Food | Phrase in why | Garbled caption | Fix |
|---|---|---|---|---|
| 348 | Pawpaw | "It contains annonacin, which can be toxic" | "anisin" (marked uncertain) | "contains a compound (likely annonacin) that can be toxic in large amounts" |
| 333 | Custard Apple | "a carotenoid (lutein) and kaurenoic acid" | "the coronoid ludian and Carino acid" (uncertain x2) | "a carotenoid and an acid with antimicrobial benefits" |
| 341 | Kumquat | "beta-cryptoxanthin and limonene" | "lemon" (uncertain) | drop limonene or hedge |
| 346 | Mulberry | "cyanidin ... rutin, myricetin" | "those cyanin / routin / myosin" | say "anthocyanins and other flavonoids (names garbled)" |
| 352 | Prickly Pear | "piscidic acid ... quercetin and kaempferol ... betacyanin" | "paciic acid / cortin and cherol / beta cyanin" (uncertain) | keep "phenolics good for skin, flavonoids, pigments protecting the liver" |
| 353 | Quince | "flavonoid antioxidants like quercetin" | "cortin and cerol" | "common flavonoid antioxidants" |
| 361 | Star Fruit | "antioxidants like quercetin and gallic acid" | "cortin epin and gallic acid" | keep gallic acid only, "plus other flavonoids" |
| 363 | Tomatillo | "lutein and zeaxanthin ... withanolide-type compounds" | "ludian and zanthin / with analyes" | hedge; the "-type" hedge is good, lutein/zeaxanthin should get one too |
| 465 | Shiitake | "eritadenine, beta-glucan and sterols lower LDL" | "aeronine" (likely) | "a compound (likely eritadenine)" |
| 470 | Anise | "quercetin, gallic acid, limonene and shikimic acid" | "cortin ... lemon" | hedge quercetin and limonene |
| 482 | Coriander Seed | "a terpene and tocopherols" | "portin turpine and Toco ferals" | already semi-hedged; fine if kept "approx." |
| 493 | Nutmeg | "with terpenes combat inflammation" | "tpin" (approx.) | "with other compounds" |
| 498 | Rosemary | "flavonoids and terpenes" | "derpo" (approx.) | "and other compounds" |
| 499 | Saffron | "safranal for brain cell health, memory and mood" | "saffronolive" (approx.) | "a signature compound for brain cell health" |
| 725 | Chili Pepper | "sinapic and ferulic acids" | "looting synaptic acid" (approx.) | "ferulic acid and another phenolic acid" |
| 386 | Nopal | "flavonoids like quercetin" | "cortin and cherol" (approx.) | already noted in `note`; hedge in text |
| 168 | Quinoa Flour | "antioxidants like quercetin" | "corsetin and ceforall" (approx.) | hedge |
| 644 | Water | "tap water has only minuscule calcium..." | "drinking water" (repair "likely tap water", uncertain) | use "drinking water", which is what the caption says |

Found outside the audited sample by scanning all repairs flagged "best guess"/"likely" (caption snippets read): 411 Pheasant ("palmitoleic" from "palic acid"), 571 Tangerine ("nobiletin" from "nobility"), 113 Quinoa ("kaempferol" from "ceerol"), 458 Enoki ("quercetin" from "cortin"), 96 Buckwheat ("D-chiro-inositol" from "DCI"; "rutin" from "routtin"), 804 Salmon ("0.022 ppm" from "0.8 022"). Same fix pattern.

Lower risk (context pins the compound, but the repair is unlisted or unflagged): 334 Dragon Fruit (quercetin from "cortin" not in repairs), 344 Lychee (rutin from "routin" not in repairs), 406 Goose (linoleic from "lolic acid" not in repairs), 442 Salsa and 351 Pomelo (quercetin / lycopene repairs listed but not marked uncertain), 280 Spirulina (copper from "Co"), 488 Ginger (spice) (shogaol from "shal"), 654 Freekeh (B3/B5 from "D3/D5"; listed, context-pinned). Hedged well (no change needed): Chanterelle, Lion's Mane, American, Asparagus, Chickpea Flour.

### 3d. Notes that are fine

No outside facts were found. Statements such as "He mentions no downsides" (Prickly Pear, Custard Apple, Tomatillo, Quinoa Flour, Barley Flour, Heart (Lamb), Nutritional Yeast) are true of the slice. Minor smoothing seen, not counted: Spirulina "fairly complete" for "often considered a complete protein", Half & Half "less calorically dense option" for a garbled "sweetener".

## 4. Tier disputes

Sorted strongest first. `strong` = captions and board both disagree with the CSV in the same direction (2). `captions_only` (0). `board_only` (45): within it, rows where the caption is silent or ambiguous come first, then larger tier distance, then A/star swaps. In every board-only row except Soybeans the caption explicitly confirms the CSV tier. The CSV evidence_note column is blank unless the CSV has one.

Confirmed candidates:
- **Walnut Oil** (Fats & Oils, CSV A, board B, caption B): confirmed strong. Caption: "going to round out our list in the B tier". CSV note: "Placement read from the item's transition onto the board."
- **Veal** (Meats Part 2, CSV A, board B, caption B): confirmed strong. Caption: "going to round out our list in the B tier". Same CSV note. Both are the last food in their episode, which is where a transition-based reading is most error-prone.
- **Pomegranate** (Fruits, CSV star, board B, caption star): NOT confirmed. Caption: "they just offer too much for me to not put them in the top tier". Board B is probably the neighbouring Plum (B) read by Flash Lite. Board-only, low priority.

Near-misses (caption hedges, CSV matches the main statement, not counted as disputes): Mini Wheats (C, "almost want to put them in the B tier"), Brussels Sprout (A, "argument for a top-tier placement"), Peanuts (B, "argument for an a-tier placement"), Soybeans (star, "top-tier bean without question ... you might have them down a tier or two"; board A; no explicit verdict word in the slice), Safflower and Sunflower Oil (A for high-oleic, C for high-linoleic; CSV A, creator correction C is already in the data).

Pattern: 44 of 47 board disagreements are A <-> star. Episodes affected: Meats Part 2 (9), Organ Meats (6), Seafood (6), Flours (4), Nuts (4). Where the caption is explicit it agrees with the CSV in all of these, so the board reader is probably confusing the two top rows; do not change the CSV from the board alone. Not counted: `creator_correction` values (e.g. Kefir A -> star, Lentils B -> A) which are later statements, not placement disputes.

| # | id | Food | Episode | CSV original | Board | Caption | Strength | Caption phrase | CSV evidence_note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 420 | Veal | Meats Part 2 | A | B | B | strong | y ve is still a great choice with a couple of notable shortcomings it's going to round out our list in the B tier now as you guys should have figured  | Placement read from the item’s transition onto the board. |
| 2 | 618 | Walnut Oil | Fats & Oils | A | B | B | strong | ooking but overall I think this is a really underutilized Choice that's going to round out our list in the B tier so fats and oils literally calories  | Placement read from the item’s transition onto the board. |
| 3 | 770 | Soybeans | Beans | ★ | A | none clear | board_only | from a purely nutritional standpoint soybeans are a top-tier bean without question but ... I can understand why you might have them down a tier or two |  |
| 4 | 566 | Pomegranate | Fruits | ★ | B | ★ | board_only | have a bit more sugar than most fruits but overall they just offer too much for me to not put them in the top tier pumpkin is a very low calorie fruit |  |
| 5 | 20 | Mr. Goodbar | Candy | A | ★ | A | board_only | fat, and fiber. And for that relative nutrient complexity, I'm putting Mr. Goodbar in the A tier. Nerd is a lower calorie candy with an overwhelmingly |  |
| 6 | 22 | Payday | Candy | A | ★ | A | board_only | with a solid fiber and fat content compared to sugar, too. I absolutely have to put PayDay in the A tier. Reese's Peanut Butter Cups are a high calori |  |
| 7 | 23 | Reese's | Candy | A | ★ | A | board_only | out trading sugar for peanuts is all it takes to accomplish that. So, I feel I have to put Reese's in the A tier. Rollo is an average calorie candy wi |  |
| 8 | 152 | Acorn Flour | Flours | A | ★ | A | board_only | But that doesn't have anything to do with its nutrition, and I feel acorn flour best belongs in the A tier. Allpurpose flour is an average calorie flo |  |
| 9 | 155 | Amaranth Flour | Flours | A | ★ | A | board_only | to take with this previously praised pseudo grain. And so, I'm going to put amaranth flour in the A tier. Barley flour is an average calorie flour wit |  |
| 10 | 158 | Buckwheat Flour | Flours | A | ★ | A | board_only | many times before because it has no real shortcomings. And so I'm going to put buckwheat flour in the A tier. Cake flour is an average calorie flour w |  |
| 11 | 165 | Oat Flour | Flours | A | ★ | A | board_only | flour. Really, this is just another opportunity for oats to strut their stuff as oat flour is going in the A tier. Peanut flour is a high calorie flou |  |
| 12 | 205 | Ambrosia | Sweets | A | ★ | A | board_only | tamer. And as far as sweets go, it's about as good as we're going to get. I'm going to put ambrosia in the A tier. Baklava is a higher calorie dessert |  |
| 13 | 213 | Dark Chocolate | Sweets | A | ★ | A | board_only | ually find a place in a healthy diet. As long as you're smart about it, I think dark chocolate goes in the A tier. Milk chocolate is a higher calorie  |  |
| 14 | 250 | Heart (Lamb) | Organ Meats | A | ★ | A | board_only | to Aid with fat loss an excellent food as all Hearts seem to be I'm going to put lamb heart in the a tier pork heart is an average calorie organ meet  |  |
| 15 | 251 | Heart (Pork) | Organ Meats | A | ★ | A | board_only | ht up more nutritious than pork meat it's hard to go wrong with heart and the pork variety is going in the a tier turkey heart is an average calori or |  |
| 16 | 252 | Heart (Turkey) | Organ Meats | A | ★ | A | board_only | urkey meat another heart preserving heart that's really hard to go wrong with turkey heart is going in the a tier beef kidney is an average calori org |  |
| 17 | 253 | Kidney (Beef) | Organ Meats | A | ★ | A | board_only | rst glance this is one of the most nutritious foods that I've ever talked about and here it's going in the a tier lamb kidney is a lower calori organ  |  |
| 18 | 254 | Kidney (Lamb) | Organ Meats | A | ★ | A | board_only | very nutrient-dense food that only seems tame because it's on this list lamb kidney is going in the a tier pork kidney is an average calori organ meat |  |
| 19 | 255 | Kidney (Pork) | Organ Meats | A | ★ | A | board_only | as possible as it joins the a tier because that Spotlight is about to be ripped straight from |  |
| 20 | 309 | Shad | Seafood Part 2 | ★ | A | ★ | board_only | mercury fish too making it pretty close to the perfect package overall an easy choice for the top tier shark is an average calori mostly saltwater set |  |
| 21 | 328 | Boysenberry | Fruits Part 2 | A | ★ | A | board_only | aspberry and you mash them together you'd get something pretty good I'm going to put poison berries in the a tier Capers are a very low calorie fruit  |  |
| 22 | 403 | Elk | Meats Part 2 | A | ★ | A | board_only | in all there's no consistent downsides to elk meat it's lean and nutritious and I'm going to put it in the a tier emu is an average calori meat with a |  |
| 23 | 405 | Frog Legs | Meats Part 2 | A | ★ | A | board_only | safe when prepared properly and they're pretty nutritious and I'm going to put frog legs in the a tier goose is a higher calori meat with a respectabl |  |
| 24 | 406 | Goose | Meats Part 2 | A | ★ | A | board_only | well rounded and I'm going to put it in the a tier okay this next one personally feels a little wrong but hors |  |
| 25 | 409 | Moose | Meats Part 2 | A | ★ | A | board_only | meat it checks all the boxes of what you should expect from meat and I'm going to put it in the a tier ostrich is a lower calori meat with a pretty im |  |
| 26 | 410 | Ostrich | Meats Part 2 | A | ★ | A | board_only | ch is another one of those meats that just provides everything you'd expect and I'm going to put it in the a tier pheasant is a higher calori meat wit |  |
| 27 | 413 | Raccoon | Meats Part 2 | A | ★ | A | board_only | avoid potential diseases overall raccoon meat is a nutritious choice that I'm going to put in the a tier breakfast sausage links are a high calorie me |  |
| 28 | 417 | Squirrel | Meats Part 2 | A | ★ | A | board_only | meat has everything that you'd look for in a meat with no real shortcomings and I'm going to put it in the a tier turkey bacon is a very high calorie  |  |
| 29 | 419 | Turkey Leg | Meats Part 2 | A | ★ | A | board_only | but overall it's a choice that's hard to go wrong with and I'm going to put it in the a tier and last on this list ve is an average calori meat with a |  |
| 30 | 500 | Sage | Herbs & Spices | ★ | A | ★ | board_only | probably the herb that provides the single most potential health benefits I'm going to put sage in the top tier summer Savory is an average calori her |  |
| 31 | 564 | Pineapple | Fruits | ★ | A | ★ | board_only | blood thinners but overall pineapple is one of the healthiest fruits available and I'm gonna put it in the top tier plums are a lower calorie fruit wi |  |
| 32 | 567 | Pumpkin | Fruits | ★ | A | ★ | board_only | healthiest and most nutritious fruits out there and should be eaten more consistently it's gonna go in the top tier raspberries are an average calorie |  |
| 33 | 661 | Rye | Grains | ★ | A | ★ | board_only | unt of phytic acid than most grains cooking somewhat offsets this and I believe that rye is a solid top-tier grain sorghum is an average calorie grain |  |
| 34 | 666 | Wheat | Grains | ★ | A | ★ | board_only | quarters of grain products come from wheat I feel all in all it's earned itself a spot in the top tier and last on this list is wild rice which by the | Late placement cross-checked against a viewer's transcription in the video comments (see About). |
| 35 | 677 | Cuttlefish | Seafood | ★ | A | ★ | board_only | is high protein and unique microprofile is unmatched on this list earning cuttlefish a secure spot in the top tier eel is a higher calorie fish with o |  |
| 36 | 687 | Mussel | Seafood | ★ | A | ★ | board_only | ore prone to lead to foodborne illnesses overall mussels are very nutritious and they'll be joining the top tier octopus is an average calorie food wi |  |
| 37 | 688 | Octopus | Seafood | ★ | A | ★ | board_only | ad and arsenic obviously keep an eye out for those but octopus is so nutritious I'll have to put it in the top tier oysters are like the Brussels spro |  |
| 38 | 689 | Oyster | Seafood | ★ | A | ★ | board_only | a loogie oysters are very nutrient dense and will be joining many of its other shellfish companions in the top tier Atlantic salmon is a higher calori |  |
| 39 | 690 | Salmon | Seafood | ★ | A | ★ | board_only | leads salmon into another comfortable top tier placement |  |
| 40 | 700 | Yellowtail | Seafood | ★ | A | ★ | board_only | a lower Mercury contents at about .06 parts per million Yellow Tail will be rounding out this list in the top tier so Seafood it's amazing to me just  |  |
| 41 | 710 | Sesame Seed | Seeds | ★ | A | ★ | board_only | Sprinkle of sesame seeds is going to help anyone who eats them and I believe they've earned a spot in the top tier sunflower seeds are the highest cal |  |
| 42 | 774 | Cashews | Nuts | A | ★ | A | board_only | ee nut allergies overall cashews are a very nutritious and healthy nuts and I feel they best belong in the a-tier Eastern chestnuts are very low calor |  |
| 43 | 776 | Hazelnuts | Nuts | A | ★ | A | board_only | of them if you have tree nut allergies but overall hazelnuts are a great food and will land safely in the a tier on this list macadamia nuts are the h |  |
| 44 | 780 | Pine Nuts | Nuts | A | ★ | A | board_only | nut allergies but overall pine nuts are really nutritious and have safely earned themselves a place in the AIDS here pistachios are an average calorie |  |
| 45 | 781 | Pistachios | Nuts | A | ★ | A | board_only | pistachios are a great and healthy nut with a unique nutritional profile and they will land safely in the a tier last on our list is walnuts walnuts a |  |
| 46 | 798 | Mutton | Meats | ★ | A | ★ | board_only | standpoint mutton is generally A Cut Above the Rest of the red meats and I think it's earned a spot in the top tier pepperoni is a very high calorie m |  |
| 47 | 810 | Turkey Breast | Meats | ★ | A | ★ | board_only | more splashable Meats in no small part thanks to how ridiculously lean it is I believe it belongs in the top tier cooked ground turkey is a mid-calori |  |

## 5. Per-item audit table (112 items)

Status "supported" = every claim matched the slice (trivial repairs such as "manganesees" -> manganese and tier-word decoding not counted as issues).

| id | Food | Episode | Draw | Why confidence | original_tier | Status |
|---|---|---|---|---|---|---|
| 280 | Spirulina | Seaweed | random | high | ★ | repair-dependent (low risk / unlisted) |
| 276 | Kelp | Seaweed | random | high | B | supported |
| 279 | Sea Grapes | Seaweed | random | high | B | supported |
| 751 | Adzuki Beans | Beans | random | high | B | supported |
| 759 | Fava Beans | Beans | random | high | B | supported |
| 765 | Mung Beans | Beans | random | high | B | supported |
| 459 | King Oyster | Mushrooms | random | high | B | supported |
| 467 | Wood Ear | Mushrooms | random | high | B | supported |
| 454 | Beech | Mushrooms | random | high | B | supported |
| 101 | Flaxseeds | Plant Proteins | random | high | C | supported |
| 112 | Pistachios | Plant Proteins | random | high | C | supported |
| 94 | Amaranth | Plant Proteins | random | high | B | supported |
| 781 | Pistachios | Nuts | random | high | A | supported |
| 782 | Walnuts | Nuts | random | high | ★ | supported |
| 773 | Brazil Nuts | Nuts | random | high | B | UNSUPPORTED (minor) |
| 420 | Veal | Meats Part 2 | random | low | A | CONTRADICTED |
| 406 | Goose | Meats Part 2 | random | high | A | repair-dependent (low risk / unlisted) |
| 397 | Beaver | Meats Part 2 | random | high | ★ | supported |
| 452 | Wasabi | Condiments | random | high | B | supported |
| 453 | Worcestershire Sauce | Condiments | random | high | C | supported |
| 442 | Salsa | Condiments | random | high | A | repair-dependent (low risk / unlisted) |
| 488 | Ginger | Herbs & Spices | random | high | ★ | repair-dependent (low risk / unlisted) |
| 504 | Turmeric | Herbs & Spices | random | high | ★ | supported |
| 482 | Coriander Seed | Herbs & Spices | random | high | B | REPAIR-DEPENDENT (flagged guess stated flat) |
| 207 | Brownies | Sweets | random | high | D | supported |
| 204 | Almond Butter | Sweets | random | high | ★ | supported |
| 218 | Cookies | Sweets | random | high | C | supported |
| 514 | Goat Cheese | Cheese | random | high | B | supported |
| 522 | Ricotta | Cheese | random | high | B | supported |
| 508 | Blue | Cheese | random | high | C | supported |
| 334 | Dragon Fruit | Fruits Part 2 | random | high | C | repair-dependent (low risk / unlisted) |
| 344 | Lychee | Fruits Part 2 | random | high | B | repair-dependent (low risk / unlisted) |
| 348 | Pawpaw | Fruits Part 2 | random | high | ★ | REPAIR-DEPENDENT (flagged guess stated flat) |
| 525 | Almond Milk | Milks | random | high | B | supported |
| 536 | Sheep Milk | Milks | random | high | A | supported |
| 537 | Soy Milk | Milks | random | high | B | supported |
| 546 | Coconut | Fruits | random | high | B | supported |
| 572 | Tomato | Fruits | random | high | A | supported |
| 558 | Nectarine | Fruits | random | high | D | supported |
| 652 | Farro | Grains | random | high | B | supported |
| 664 | Teff | Grains | random | high | A | supported |
| 654 | Freekeh | Grains | random | high | A | repair-dependent (low risk / unlisted) |
| 718 | Bok Choy | Vegetables | random | high | B | supported |
| 740 | Onion | Vegetables | random | high | A | supported |
| 741 | Parsnip | Vegetables | random | high | B | supported |
| 270 | Tongue (Lamb) | Organ Meats | random | high | D | supported |
| 262 | Pancreas (Lamb) | Organ Meats | random | high | C | supported |
| 250 | Heart (Lamb) | Organ Meats | random | high | A | supported |
| 33 | Tootsie Roll | Candy | random | high | F | supported |
| 19 | Mounds | Candy | random | high | C | supported |
| 2 | Airheads | Candy | random | high | F | supported |
| 582 | Custard | Dairy | random | high | C | supported |
| 586 | Half & Half | Dairy | random | high | B | supported |
| 575 | Butter | Dairy | random | high | A | supported |
| 673 | Clam | Seafood | random | high | ★ | supported |
| 674 | Cod | Seafood | random | high | D | supported |
| 697 | Tilapia | Seafood | random | high | C | supported |
| 44 | Cinnamon Toast Crunch | Cereals | random | high | F | supported |
| 52 | Fruity Pebbles | Cereals | random | high | F | supported |
| 59 | Lucky Charms | Cereals | random | high | F | supported |
| 81 | French Toast | Breakfast | random | high | D | supported |
| 70 | Bacon | Breakfast | random | high | C | supported |
| 84 | Muffin | Breakfast | random | high | F | supported |
| 318 | Sucker | Seafood Part 2 | random | high | B | supported |
| 299 | Mullet | Seafood Part 2 | random | high | A | supported |
| 286 | Chinook Salmon | Seafood Part 2 | random | high | ★ | supported |
| 197 | Rice Cakes | Snacks | random | high | B | supported |
| 186 | French Fries | Snacks | random | high | D | supported |
| 198 | Shrimp Crackers | Snacks | random | high | D | supported |
| 703 | Flax Seed | Seeds | random | high | ★ | supported |
| 711 | Sunflower Seed | Seeds | random | high | A | supported |
| 708 | Pumpkin Seed | Seeds | random | high | A | supported |
| 393 | Swiss Chard | Vegetables Part 2 | random | high | ★ | supported |
| 390 | Rhubarb | Vegetables Part 2 | random | high | C | supported |
| 378 | Ginger | Vegetables Part 2 | random | high | ★ | supported |
| 164 | Millet Flour | Flours | random | high | B | supported |
| 166 | Peanut Flour | Flours | random | high | ★ | supported |
| 156 | Barley Flour | Flours | random | high | B | supported |
| 644 | Water | Drinks | random | high | ★ | REPAIR-DEPENDENT (flagged guess stated flat) |
| 634 | Milk | Drinks | random | high | A | UNSUPPORTED (minor) |
| 619 | Apple Juice | Drinks | random | high | C | supported |
| 793 | Goat | Meats | random | high | A | supported |
| 785 | Bison | Meats | random | high | A | supported |
| 806 | Shrimp | Meats | random | high | A | supported |
| 607 | Margarine | Fats & Oils | random | high | F | supported |
| 596 | Chicken Fat | Fats & Oils | random | high | A | supported |
| 614 | Shortening | Fats & Oils | random | high | F | supported |
| 455 | Chanterelle | Mushrooms | flagged extra | high | A | supported |
| 460 | Lion's Mane | Mushrooms | flagged extra | high | ★ | supported |
| 465 | Shiitake | Mushrooms | flagged extra | high | A | REPAIR-DEPENDENT (flagged guess stated flat) |
| 468 | Nutritional Yeast (Fortified) | Mushrooms | flagged extra | high | ★ | UNSUPPORTED (minor) |
| 470 | Anise | Herbs & Spices | flagged extra | high | B | REPAIR-DEPENDENT (flagged guess stated flat) |
| 493 | Nutmeg | Herbs & Spices | flagged extra | high | C | REPAIR-DEPENDENT (flagged guess stated flat) |
| 497 | Parsley | Herbs & Spices | flagged extra | high | A | supported |
| 498 | Rosemary | Herbs & Spices | flagged extra | high | D | REPAIR-DEPENDENT (flagged guess stated flat) |
| 499 | Saffron | Herbs & Spices | flagged extra | high | A | REPAIR-DEPENDENT (flagged guess stated flat) |
| 507 | American | Cheese | flagged extra | high | D | supported |
| 333 | Custard Apple | Fruits Part 2 | flagged extra | high | C | REPAIR-DEPENDENT (flagged guess stated flat) |
| 341 | Kumquat | Fruits Part 2 | flagged extra | high | B | REPAIR-DEPENDENT (flagged guess stated flat) |
| 346 | Mulberry | Fruits Part 2 | flagged extra | high | A | REPAIR-DEPENDENT (flagged guess stated flat) |
| 351 | Pomelo | Fruits Part 2 | flagged extra | high | A | repair-dependent (low risk / unlisted) |
| 352 | Prickly Pear | Fruits Part 2 | flagged extra | high | A | REPAIR-DEPENDENT (flagged guess stated flat) |
| 353 | Quince | Fruits Part 2 | flagged extra | high | D | REPAIR-DEPENDENT (flagged guess stated flat) |
| 361 | Star Fruit | Fruits Part 2 | flagged extra | high | B | REPAIR-DEPENDENT (flagged guess stated flat) |
| 363 | Tomatillo | Fruits Part 2 | flagged extra | high | A | REPAIR-DEPENDENT (flagged guess stated flat) |
| 715 | Asparagus | Vegetables | flagged extra | high | A | supported |
| 725 | Chili Pepper | Vegetables | flagged extra | high | ★ | REPAIR-DEPENDENT (flagged guess stated flat) |
| 188 | Graham Crackers | Snacks | flagged extra | low | D | supported |
| 386 | Nopal | Vegetables Part 2 | flagged extra | low | A | REPAIR-DEPENDENT (flagged guess stated flat) |
| 161 | Chickpea Flour | Flours | flagged extra | high | ★ | supported |
| 168 | Quinoa Flour | Flours | flagged extra | high | B | REPAIR-DEPENDENT (flagged guess stated flat) |
| 618 | Walnut Oil | Fats & Oils | flagged extra | low | A | CONTRADICTED |
