#!/usr/bin/env python3
"""Clean a Jupyter notebook (e.g. one executed/downloaded from Google Colab) so it is
safe and tidy to commit:

* removes every cell output and resets execution counts
* blanks any hard-coded secret assignments such as ``COMET_API_KEY = "...."``
  (also dict-style ``"api_key": "...."``); put secrets in the environment or Colab
  Secrets instead -- never in the file
* normalizes the kernelspec so diffs stay small
* reports any secret-like leftovers it could not rewrite

Usage:
    python scripts/clean_notebook.py NOTEBOOK.ipynb [NOTEBOOK2.ipynb ...]

Exit code is non-zero if secret-like text is still found after cleaning.
"""
import json
import re
import sys

# matches:   VAR = "non-empty-value"    where the variable name advertises a secret
KEY_LITERAL_RE = re.compile(
    r"^(\s*[A-Za-z_][A-Za-z0-9_]*(?:_API_KEY|_TOKEN|_SECRET|_PASSWORD|PASSWD)"
    r"\s*=\s*['\"])[^'\"]+(['\"])",
    re.M,
)
# matches dict style:   "api_key": "value"   /   'token': 'value'
DICT_KEY_RE = re.compile(
    r"(['\"][A-Za-z0-9_]*?(?:api[_-]?key|token|secret|password)['\"]\s*:\s*['\"])[^'\"]+(['\"])",
    re.I,
)

# patterns used for the final verification pass
LEFT_PATTERNS = [
    r'COMET_API_KEY\s*=\s*"[^"]+"',
    r'(?i)[A-Za-z0-9_]*(?:api[_-]?key|token|secret|password)\s*[=:]\s*["\'][A-Za-z0-9]{8,}["\']',
]


def blank_secrets(text):
    def _blank(m):
        return m.group(1) + m.group(2)

    text, n1 = KEY_LITERAL_RE.subn(_blank, text)
    text, n2 = DICT_KEY_RE.subn(_blank, text)
    return text, n1 + n2


def clean(path):
    with open(path, encoding="utf-8") as fh:
        nb = json.load(fh)
    original = open(path, encoding="utf-8").read()  # raw text for ascii-mode detection

    cleared = 0
    scrubbed = 0
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        new_src, n = blank_secrets(src)
        scrubbed += n
        if new_src != src:
            cell["source"] = new_src.splitlines(keepends=True)
        if cell.get("outputs"):
            cell["outputs"] = []
            cleared += 1
        cell["execution_count"] = None

    # normalize kernelspec to avoid churn between local / Colab kernels
    ks = nb.get("metadata", {}).get("kernelspec")
    if ks:
        ks["display_name"] = "Python 3"
        ks["name"] = "python3"
        ks["language"] = "python"

    # Match the formatting this repo commits in (JSON indent=2, no trailing newline,
    # LF endings) so that running the cleaner after a Colab round-trip produces a
    # small, reviewable diff instead of whole-file churn.
    has_non_ascii = any(ord(ch) > 127 for ch in original)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(nb, fh, ensure_ascii=not has_non_ascii, indent=2)

    # final verification pass
    blob = open(path, encoding="utf-8").read()
    leftovers = []
    for pat in LEFT_PATTERNS:
        leftovers.extend(re.findall(pat, blob))
    if leftovers:
        leftovers = sorted(set(leftovers))
    print(f"{path}: cleared outputs of {cleared} code cells, scrubbed {scrubbed} hard-coded key(s)")
    if leftovers:
        print(f"  !! WARNING -- secret-like text still present, review before committing:\n    " + "\n    ".join(leftovers))
        return 1
    print(f"{path}: OK -- no secret-like text found")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    rc = 0
    for p in sys.argv[1:]:
        rc |= clean(p)
    sys.exit(rc)
