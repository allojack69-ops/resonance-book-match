#!/usr/bin/env python3
"""Generate an embedded 500+ book catalog for Resonance Book Match."""
from __future__ import annotations
import csv, io, json, re, urllib.request
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/melaniewalsh/responsible-datasets-in-context/refs/heads/main/datasets/top-500-novels/top-500-novels-metadata_2025-01-11.csv"
ASSET_DIR = Path("app/src/main/assets")
BOOKS_JS = ASSET_DIR / "books-extra.js"
INDEX = ASSET_DIR / "index.html"

# The existing app already has these seed books. Avoid obvious duplicates.
SKIP = {
    "1984", "the trial", "the plague", "lord of the flies",
    "the master and margarita", "picnic by the roadside",
    "the city and the city", "flowers for algernon",
}

def norm(s: str) -> str:
    s = s.lower().replace("ё", "е").replace("’", "'")
    s = re.sub(r"[^a-zа-я0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def profile(genre: str, title: str) -> dict[str, float]:
    g, t, p = (genre or "").lower(), (title or "").lower(), {}

    def add(k, v):
        p[k] = max(p.get(k, 0.0), v)

    # Base mapping into the graph axes already used by the app.
    if "mystery" in g:
        add("mystery_vs_structure", 1); add("truth_vs_uncertainty", .8)
        add("ambiguity_vs_resolution", .7); add("depth_vs_pace", .4)
    elif "fantasy" in g:
        add("idea_vs_reality", .9); add("mystery_vs_structure", .8)
        add("ambiguity_vs_resolution", .6); add("idea_vs_style", .8)
    elif "scifi" in g or "science" in g:
        add("idea_vs_reality", 1); add("truth_vs_uncertainty", .9)
        add("mystery_vs_structure", .7); add("freedom_vs_control", .5)
    elif "political" in g:
        add("person_vs_system", 1); add("freedom_vs_control", 1)
        add("identity_vs_society", .8); add("choice_vs_consequence", .7)
    elif "romance" in g:
        add("person_vs_self", .9); add("identity_vs_society", .9)
        add("choice_vs_consequence", .7); add("depth_vs_pace", .7)
    elif "history" in g or "action" in g:
        add("choice_vs_consequence", .9); add("ethics_vs_price", .7)
        add("person_vs_system", .5); add("depth_vs_pace", .6)
    elif "horror" in g:
        add("truth_vs_uncertainty", .9); add("mystery_vs_structure", .8)
        add("idea_vs_reality", .8); add("ambiguity_vs_resolution", .7)
    elif "bildungs" in g:
        add("person_vs_self", 1); add("identity_vs_society", .8)
        add("choice_vs_consequence", .8); add("depth_vs_pace", .7)
    elif "allegor" in g:
        add("idea_vs_reality", .9); add("idea_vs_style", .9)
        add("perspective_vs_truth", .7); add("ethics_vs_price", .7)
    else:
        add("person_vs_self", .7); add("idea_vs_reality", .7)
        add("identity_vs_society", .6); add("depth_vs_pace", .6)

    # Title signals reinforce relevant edges.
    if re.search(r"\bwar|battle|soldier|army|revolution|rebellion|empire\b", t):
        add("choice_vs_consequence", .9); add("ethics_vs_price", .7)
    if re.search(r"\bking|queen|prince|princess|government|state|law|politic|capital\b", t):
        add("person_vs_system", .8); add("freedom_vs_control", .7)
    if re.search(r"\bdeath|dead|grave|murder|crime|blood|monster|dracula|ghost\b", t):
        add("truth_vs_uncertainty", .8); add("ambiguity_vs_resolution", .6)
    if re.search(r"\bjourney|voyage|adventure|island|sea|world|travel\b", t):
        add("choice_vs_consequence", .8); add("depth_vs_pace", .5)
    if re.search(r"\blove|marriage|husband|wife|heart|passion\b", t):
        add("person_vs_self", .8); add("identity_vs_society", .7)
    if re.search(r"\bdream|night|mirror|shadow|secret|mystery|unknown\b", t):
        add("truth_vs_uncertainty", .8); add("mystery_vs_structure", .7)
    if re.search(r"\btime|future|machine|moon|mars|space|star|earth\b", t):
        add("idea_vs_reality", .8); add("truth_vs_uncertainty", .7)

    return {k: round(v, 2) for k, v in p.items() if v > 0}

def description(genre: str) -> str:
    g = (genre or "").lower()
    if "mystery" in g: return "Таємниця, пошук правди, приховані мотиви та поступове розкриття структури історії."
    if "fantasy" in g: return "Незвичайний світ, уява, правила реальності та вибір героя всередині нього."
    if "scifi" in g or "science" in g: return "Ідея про людину, технологію або майбутнє, що змушує переосмислити реальність."
    if "political" in g: return "Влада, суспільний порядок, свобода та конфлікт людини із системою."
    if "romance" in g: return "Стосунки, внутрішній вибір, соціальні очікування та емоційні наслідки."
    if "history" in g or "action" in g: return "Випробування, події, рішення та наслідки, які змінюють життя героїв."
    if "horror" in g: return "Страх, невідомість, межа між реальністю та неможливим."
    if "bildungs" in g: return "Формування особистості, дорослішання, самоусвідомлення та пошук власного місця."
    if "allegor" in g: return "Образна історія, що через сюжет говорить про мораль, суспільство та людську природу."
    return "Історія про людей, вибір, реальність та ідеї, що залишають простір для власної інтерпретації."

def main():
    raw = urllib.request.urlopen(SOURCE, timeout=30).read().decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(raw)))
    rows.sort(key=lambda r: int(r["top_500_rank"]))

    books, seen = [], set()
    for r in rows:
        title, author = r["title"].strip(), r["author"].strip()
        key = norm(title)
        if key in SKIP or key in seen:
            continue
        seen.add(key)
        books.append([title, author, profile(r.get("genre", ""), title), description(r.get("genre", ""))])

    if len(books) < 492:
        raise SystemExit(f"Catalog source unexpectedly contains only {len(books)} usable books")

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    BOOKS_JS.write_text(
        "const EXTRA_BOOKS=" + json.dumps(books, ensure_ascii=False, separators=(",", ":")) +
        ";\nB.push(...EXTRA_BOOKS);\n",
        encoding="utf-8"
    )

    html = INDEX.read_text(encoding="utf-8")
    tag = '<script src="books-extra.js"></script>'
    if tag not in html:
        if "</body>" not in html:
            raise SystemExit("index.html has no </body> marker")
        INDEX.write_text(html.replace("</body>", tag + "</body>"), encoding="utf-8")

    print(f"RESonance catalog: {len(books) + 8} total books ({len(books)} added)")

if __name__ == "__main__":
    main()
