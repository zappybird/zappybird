#!/usr/bin/env python3
# ⒸAngelaMos | 2025 | CertGames.com
import sys
import json
from pathlib import Path

# ============================
#  Custom Language Colors
# ============================
LANGUAGE_COLORS = {
    "Python": "#3572A5",   # blue
    "TOML": "#FF0000",     # red
    "HTML": "#E34C26",     # orange
    "INI": "#FFFFFF",      # white
}

DEFAULT_COLOR = "#ff4444"  # fallback (your original red)

def format_number(num):
    return f"{num:,}"

def generate_svg(loc_data):
    total_code = int(loc_data.get('Total', {}).get('code', 0))
    total_files = int(loc_data.get('Total', {}).get('files', 0))

    languages = {}
    for lang, stats in loc_data.items():
        if lang == "Total":
            continue
        if isinstance(stats, dict):
            code = int(stats.get("code", 0))
            if code > 0:
                languages[lang] = code

    top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]

    svg = f"""
<svg width="800" height="320" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="320" fill="#000000" rx="10"/>
  <text x="40" y="55" font-family="monospace" font-size="32" fill="#ffffff">{format_number(total_code)}</text>
  <text x="40" y="80" font-family="monospace" font-size="14" fill="#ffffff">LINES OF CODE</text>
  <text x="760" y="55" font-family="monospace" font-size="24" fill="#ffffff" text-anchor="end">{format_number(total_files)}</text>
  <text x="760" y="75" font-family="monospace" font-size="12" fill="#ffffff" text-anchor="end">FILES</text>
  <line x1="30" y1="100" x2="770" y2="100" stroke="#30363d" stroke-width="1"/>
  <text x="40" y="130" font-family="monospace" font-size="16" fill="#ff4444">TOP LANGUAGES</text>
"""

    y = 160
    max_width = 450
    max_code = top_langs[0][1] if top_langs else 1

    for lang, code in top_langs:
        width = (code / max_code) * max_width

        # Pick correct color
        bar_color = LANGUAGE_COLORS.get(lang, DEFAULT_COLOR)

        svg += f"""
  <text x="40" y="{y}" font-family="monospace" font-size="13" fill="#ffffff">{lang}</text>
  <rect x="180" y="{y-12}" width="{max_width}" height="16" fill="#21262d" rx="4"/>
  <rect x="180" y="{y-12}" width="{width}" height="16" fill="{bar_color}" rx="4"/>
  <text x="650" y="{y}" font-family="monospace" font-size="12" fill="#ffffff">{format_number(code)}</text>
"""
        y += 25

    svg += "</svg>"
    return svg

def main():
    loc_file = Path("loc-data.json")
    if not loc_file.exists():
        print("loc-data.json not found", file=sys.stderr)
        sys.exit(1)

    with open(loc_file) as f:
        data = json.load(f)

    svg = generate_svg(data)
    with open("loc-stats.svg", "w") as f:
        f.write(svg)

    print("SVG generated successfully")

if __name__ == "__main__":
    main()

