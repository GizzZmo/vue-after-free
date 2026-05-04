#!/usr/bin/env python3
"""
Patch the README.md screenshots section so it always reflects the latest
generated preview images stored in docs/screenshots/.

The script looks for a fenced block between these two HTML comment markers:
  <!-- SCREENSHOTS_START -->
  <!-- SCREENSHOTS_END -->

If the markers are missing they are inserted after the first top-level
heading that contains the word "screenshot" (case-insensitive); or, if no
such heading exists, immediately before the "# Credits" section.  If
"# Credits" is also absent the block is appended at the end of the file.
"""

import os
import re

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
README = os.path.join(REPO_ROOT, "README.md")
SCREENSHOTS_DIR = os.path.join(REPO_ROOT, "docs", "screenshots")

BRANCH = "main"
GITHUB_RAW = "https://raw.githubusercontent.com/GizzZmo/vue-after-free"

START_MARKER = "<!-- SCREENSHOTS_START -->"
END_MARKER = "<!-- SCREENSHOTS_END -->"

CAPTION = {
    "main_menu.png": "Main Menu",
    "success.png": "Success Screen",
    "fail.png": "Failure Screen",
}


def build_block() -> str:
    lines = [START_MARKER, ""]
    lines.append("## Screenshots\n")
    for filename, caption in CAPTION.items():
        path = os.path.join(SCREENSHOTS_DIR, filename)
        if not os.path.exists(path):
            continue
        raw_url = f"{GITHUB_RAW}/{BRANCH}/docs/screenshots/{filename}"
        lines.append(f"### {caption}")
        lines.append(f"![{caption}]({raw_url})\n")
    lines.append(END_MARKER)
    return "\n".join(lines) + "\n"


def patch(content: str, block: str) -> str:
    # Replace existing block if markers present
    pattern = re.compile(
        r"<!-- SCREENSHOTS_START -->.*?<!-- SCREENSHOTS_END -->",
        re.DOTALL,
    )
    if pattern.search(content):
        return pattern.sub(block.rstrip("\n"), content)

    # Insert before "# Credits"
    credits_match = re.search(r"^# Credits", content, re.MULTILINE)
    if credits_match:
        pos = credits_match.start()
        return content[:pos] + block + "\n" + content[pos:]

    # Fallback: append
    return content.rstrip("\n") + "\n\n" + block


def main() -> None:
    with open(README, encoding="utf-8") as fh:
        content = fh.read()

    block = build_block()
    patched = patch(content, block)

    if patched == content:
        print("README.md is already up to date.")
        return

    with open(README, "w", encoding="utf-8") as fh:
        fh.write(patched)
    print("README.md updated with latest screenshots.")


if __name__ == "__main__":
    main()
