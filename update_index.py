#!/usr/bin/env python3
"""Regenerates games.json, README.md, and index.html in chronological order.
Usage when adding a new game:
  python3 update_index.py \
    --add-slug <slug> \
    --date "YYYY-MM-DD HH:MM" \
    --title "<Title>" \
    --genre "<Genre>" \
    --phase "Phase 5: QQ Classics 3D & Bilibili Remakes" \
    --desc "<1-sentence gameplay highlight>"
"""
import argparse, json, os, re

DIR = os.path.dirname(os.path.abspath(__file__))
GAMES_PATH = os.path.join(DIR, "games.json")
README_PATH = os.path.join(DIR, "README.md")
HTML_PATH = os.path.join(DIR, "index.html")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add-slug", help="GitHub repo slug of new game")
    parser.add_argument("--date", help="Created UTC date (YYYY-MM-DD HH:MM)")
    parser.add_argument("--title", help="Game title")
    parser.add_argument("--genre", help="Engine / Genre badge")
    parser.add_argument("--phase", default="Phase 5: QQ Classics 3D & Bilibili Remakes", help="Phase bucket")
    parser.add_argument("--desc", help="Short 1-sentence gameplay highlight")
    args = parser.parse_args()

    with open(GAMES_PATH, "r", encoding="utf-8") as f:
        games = json.load(f)

    if args.add_slug:
        games = [g for g in games if g["slug"] != args.add_slug]
        games.append({
            "num": len(games) + 1,
            "numStr": f"{len(games) + 1:02d}",
            "date": args.date,
            "slug": args.add_slug,
            "title": args.title,
            "genre": args.genre,
            "phase": args.phase,
            "desc": args.desc,
            "playUrl": f"https://kunruiw1991.github.io/{args.add_slug}/",
            "repoUrl": f"https://github.com/kunruiw1991/{args.add_slug}",
            "thumbUrl": f"https://raw.githubusercontent.com/kunruiw1991/{args.add_slug}/main/screenshot.jpg"
        })

    games.sort(key=lambda g: g["date"])
    for idx, g in enumerate(games, 1):
        g["num"] = idx
        g["numStr"] = f"{idx:02d}"

    with open(GAMES_PATH, "w", encoding="utf-8") as f:
        json.dump(games, f, indent=2, ensure_ascii=False)

    total = len(games)
    last_num = f"{total:02d}"
    first_date = games[0]["date"][:10]
    last_date = games[-1]["date"][:10]

    # 1. Update README.md (keeping existing Phase summary footer if present)
    with open(README_PATH, "r", encoding="utf-8") as f:
        old_readme = f.read()
    footer = ""
    if "\n---\n\n## 📊 Summary by Phase" in old_readme:
        footer = "\n---\n\n## 📊 Summary by Phase" + old_readme.split("\n---\n\n## 📊 Summary by Phase", 1)[1]

    md_lines = [
        f"# 📌 Complete Chronological Game Index (`#01` → `#{last_num}`)",
        "",
        f"> **Live Arcade Homepage**: [https://kunruiw1991.github.io/](https://kunruiw1991.github.io/) · **{total} Playable Kids' Web Games & Interactive Studios** (`{first_date}` to `{last_date}`, sorted in chronological order).",
        "",
        "## 📱 Quick Play List (tap a game — newest first)",
        "",
        *[f"- **#{g['numStr']}** · [{g['title']}]({g['playUrl']})" for g in reversed(games)],
        "",
        "## 🗂️ Full Chronological Table",
        "",
        "| # | Created (UTC) | Game Title | Live Game (GitHub Pages) | GitHub Repo | Engine / Genre | Highlights |",
        "| :-: | :--- | :--- | :---: | :--- | :--- | :--- |",
    ]
    for g in games:
        md_lines.append(
            f"| **{g['numStr']}** | `{g['date']}` | **{g['title']}** | [▶️ Play Live]({g['playUrl']}) | [`{g['slug']}`]({g['repoUrl']}) | {g['genre']} | {g['desc']} |"
        )
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n" + footer)

    # 2. Update index.html (header counts, phase badge counts, and const GAMES JSON — visual image cards only, no top table)
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(r'<section class="pinned-section">.*?</section>\s*', "", html, flags=re.S)
    html = re.sub(r"#01 → #\d+", f"#01 → #{last_num}", html)
    html = re.sub(r"#01→#\d+", f"#01→#{last_num}", html)
    html = re.sub(r"#\d+→#01", f"#{last_num}→#01", html)
    html = re.sub(r"All \d+ Games", f"All {total} Games", html)
    html = re.sub(r"<strong>\d+ Kids' Web Games", f"<strong>{total} Kids' Web Games", html)
    html = re.sub(r"to <strong>\d{4}-\d{2}-\d{2}</strong> in strict", f"to <strong>{last_date}</strong> in strict", html)
    for ph in sorted({g["phase"] for g in games}):
        n = sum(1 for g in games if g["phase"] == ph)
        html = re.sub(r'(data-phase="' + re.escape(ph).replace("&", "&(?:amp;)?") + r'">[^<]*\()\d+(\)</button>)', lambda m: f"{m.group(1)}{n}{m.group(2)}", html)
    html = re.sub(
        r"const GAMES = \[.*?\];\n    let activePhase",
        f"const GAMES = {json.dumps(games, ensure_ascii=False)};\n    let activePhase",
        html,
        flags=re.S
    )
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Updated games.json, README.md, and index.html ({total} games: #01 -> #{last_num})")

if __name__ == "__main__":
    main()
