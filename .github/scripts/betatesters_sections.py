"""Names a person (not the bot) added below "# Auto-added" go back to the manual section.

Usage: betatesters_sections.py <sha before the push>
Rewrites allowed_betatesters.txt in place and writes `moved=<names>` to $GITHUB_OUTPUT.
"""
import os
import subprocess
import sys

FILE = "allowed_betatesters.txt"
HEADER = "# auto-added"


def split(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for i, ln in enumerate(lines):
        if ln.casefold().startswith(HEADER):
            return lines[:i], lines[i], lines[i + 1:]
    return lines, None, []


def fix(old_text, new_text):
    """Returns (fixed text, moved names); the text is unchanged when nothing was misplaced."""
    _, old_header, old_auto = split(old_text)
    manual, header, auto = split(new_text)
    if header is None or old_header is None:
        return new_text, []
    known = {n.casefold() for n in old_auto}
    moved = [n for n in auto if not n.startswith("#") and n.casefold() not in known]
    if not moved:
        return new_text, []
    in_manual = {n.casefold() for n in manual}
    manual += [n for n in moved if n.casefold() not in in_manual]
    auto = [n for n in auto if n not in moved]
    return "\n".join(manual + [header] + auto) + "\n", moved


def main():
    before = sys.argv[1] if len(sys.argv) > 1 else ""
    old = subprocess.run(["git", "show", f"{before}:{FILE}"], capture_output=True, text=True)
    old_text = old.stdout if old.returncode == 0 else ""
    with open(FILE, encoding="utf-8") as f:
        new_text = f.read()
    text, moved = fix(old_text, new_text)
    if not moved:
        print("Nothing added under # Auto-added.")
        return
    with open(FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    for name in moved:
        print(f"::warning file={FILE}::{name} was added under '# Auto-added'; moving it to the manual section.")
    with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as out:
        out.write(f"moved={', '.join(moved)}\n")


if __name__ == "__main__":
    main()
