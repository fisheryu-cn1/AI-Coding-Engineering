#!/usr/bin/env python3
"""Replace .diagram ASCII art blocks with SVG <img> references in the HTML."""
import re

HTML_PATH = "llm_app_architecture_guide.html"
SVG_PREFIX = "./llm_app_diagrams/"

# Ordered list of SVG files matching the 9 .diagram blocks in the HTML
SVG_FILES = [
    "01_landscape.svg",
    "02_combo1_rag.svg",
    "03_combo2_data.svg",
    "04_combo3_crew.svg",
    "05_combo4_dotnet.svg",
    "06_combo5_migrate.svg",
    "07_combo6_mvp.svg",
    "08_memory.svg",
    "09_matrix.svg",
]

with open(HTML_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern to match <div class="diagram">...</div>
# We use a non-greedy match but need to be careful not to cross div boundaries.
# Since diagram blocks contain plain text (no nested tags), this regex is safe.
pattern = re.compile(r'<div class="diagram">.*?</div>', re.DOTALL)

matches = list(pattern.finditer(content))
print(f"Found {len(matches)} .diagram blocks (expecting {len(SVG_FILES)})")

if len(matches) != len(SVG_FILES):
    raise RuntimeError(f"Mismatch: found {len(matches)} blocks but have {len(SVG_FILES)} SVGs")

# Build replacements from end to start so earlier indices aren't shifted
for idx in range(len(matches) - 1, -1, -1):
    m = matches[idx]
    svg_file = SVG_FILES[idx]
    replacement = (
        f'<div class="diagram-svg">\n'
        f'  <img src="{SVG_PREFIX}{svg_file}" alt="diagram" style="max-width:100%;height:auto;display:block;margin:0 auto;">\n'
        f'</div>'
    )
    content = content[:m.start()] + replacement + content[m.end():]

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Replacement complete.")
