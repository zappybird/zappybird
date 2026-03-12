#!/usr/bin/env python3
# ⒸAngelaMos | 2025 | CertGames.com
import sys
import json
from pathlib import Path

# ============================
#  Custom Language Colors
# ============================
LANGUAGE_COLORS = {
    "Python":     "#3572A5",
    "JavaScript": "#F1E05A",
    "TypeScript": "#2B7489",
    "HTML":       "#E34C26",
    "CSS":        "#563D7C",
    "Rust":       "#DEA584",
    "Go":         "#00ADD8",
    "Shell":      "#89E051",
    "TOML":       "#FF0000",
    "INI":        "#FFFFFF",
    "JSON":       "#292929",
    "Markdown":   "#083FA1",
}
DEFAULT_COLOR = "#ff4444"


def format_number(num):
    return f"{num:,}"


def merge_repos(loc_data):
    """
    Handles Tokei multi-repo JSON where top-level keys are repo/directory names:
    {
      "Repo1": { "Python": { "code": X, ... }, "Total": { "code": Y, ... } },
      "Repo2": { ... }
    }
    Merges into a single flat dict:
    {
      "Total": { "code": X, "files": Y },
      "Python": { "code": A },
      ...
    }
    Falls back gracefully if structure is unexpected.
    """
    combined = {"Total": {"code": 0, "files": 0}}
    languages = {}

    for repo_name, repo_data in loc_data.items():
        if not isinstance(repo_data, dict):
            print(f"Warning: skipping unexpected entry '{repo_name}'", file=sys.stderr)
            continue

        # Merge totals
        total = repo_data.get("Total", {})
        combined["Total"]["code"]  += int(total.get("code",  0))
        combined["Total"]["files"] += int(total.get("files", 0))

        # Merge per-language stats
        for lang, stats in repo_data.items():
            if lang == "Total":
                continue
            if isinstance(stats, dict):
                code = int(stats.get("code", 0))
                if code > 0:
                    languages[lang] = languages.get(lang, 0) + code

    for lang, code in languages.items():
        combined[lang] = {"code": code}

    return combined


def generate_svg(loc_data):
    total_code  = int(loc_data.get("Total", {}).get("code",  0))
    total_files = int(loc_data.get("Total", {}).get("files", 0))

    if total_code == 0:
        print("Warning: total code count is 0 — SVG will be empty", file=sys.stderr)

    # Extract and sort languages
    languages = {
        lang: stats["code"]
        for lang, stats in loc_data.items()
        if lang != "Total" and isinstance(stats, dict) and "code" in stats and stats["code"] > 0
    }

    top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]

    if not top_langs:
        print("Error: no language data found — cannot generate SVG", file=sys.stderr)
        sys.exit(1)

    # Dynamic height based on actual number of language rows
    row_height   = 28
    header_space = 170
    footer_pad   = 30
    height = header_space + len(top_langs) * row_height + footer_pad

    svg = f"""<svg width="800" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="{height}" fill="#000000" rx="10"/>

  <!-- Total lines -->
  <text x="40" y="55" font-family="monospace" font-size="32" fill="#ffffff">{format_number(total_code)}</text>
  <text x="40" y="78" font-family="monospace" font-size="13" fill="#aaaaaa">LINES OF CODE</text>

  <!-- Total files -->
  <text x="760" y="55" font-family="monospace" font-size="24" fill="#ffffff" text-anchor="end">{format_number(total_files)}</text>
  <text x="760" y="75" font-family="monospace" font-size="12" fill="#aaaaaa" text-anchor="end">FILES</text>

  <!-- Divider -->
  <line x1="30" y1="100" x2="770" y2="100" stroke="#30363d" stroke-width="1"/>

  <!-- Section heading -->
  <text x="40" y="132" font-family="monospace" font-size="15" fill="#ff4444">TOP LANGUAGES</text>
"""

    y         = header_space
    max_width = 450
    max_code  = top_langs[0][1] if top_langs else 1

    for lang, code in top_langs:
        bar_width = max(1, (code / max_code) * max_width)
        bar_color = LANGUAGE_COLORS.get(lang, DEFAULT_COLOR)
        svg += f"""
  <text x="40" y="{y}" font-family="monospace" font-size="13" fill="#ffffff">{lang}</text>
  <rect x="180" y="{y - 13}" width="{max_width}" height="16" fill="#21262d" rx="4"/>
  <rect x="180" y="{y - 13}" width="{bar_width:.1f}" height="16" fill="{bar_color}" rx="4"/>
  <text x="650" y="{y}" font-family="monospace" font-size="12" fill="#cccccc">{format_number(code)}</text>
"""
        y += row_height

    svg += "\n</svg>"
    return svg


def main():
    loc_file = Path("loc-data.json")

    if not loc_file.exists():
        print("Error: loc-data.json not found", file=sys.stderr)
        sys.exit(1)

    if loc_file.stat().st_size == 0:
        print("Error: loc-data.json is empty", file=sys.stderr)
        sys.exit(1)

    with open(loc_file) as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: loc-data.json is not valid JSON — {e}", file=sys.stderr)
            sys.exit(1)

    if not isinstance(raw_data, dict) or not raw_data:
        print("Error: loc-data.json has unexpected structure or is empty", file=sys.stderr)
        sys.exit(1)

    # Debug: show top-level keys so you can verify Tokei's output shape
    print(f"Debug: top-level keys in loc-data.json: {list(raw_data.keys())[:10]}", file=sys.stderr)

    # Detect flat (single-run) vs multi-repo format
    if "Total" not in raw_data:
        print("Debug: 'Total' not found at top level — treating as multi-repo format", file=sys.stderr)
        merged = merge_repos(raw_data)
    else:
        print("Debug: flat Tokei output detected", file=sys.stderr)
        merged = raw_data

    print(f"Debug: total code={merged.get('Total', {}).get('code', 0)}, "
          f"files={merged.get('Total', {}).get('files', 0)}", file=sys.stderr)

    svg = generate_svg(merged)

    with open("loc-stats.svg", "w") as f:
        f.write(svg)

    print("SVG generated successfully")


if __name__ == "__main__":
    main()
