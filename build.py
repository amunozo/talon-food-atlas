#!/usr/bin/env python3
"""Run build_data, then inline data.json into template.html -> index.html."""
import os
import sys

import build_data

HERE = os.path.dirname(os.path.abspath(__file__))
PLACEHOLDER = "/*__DATA__*/null"


def main():
    tpl_path = os.path.join(HERE, "template.html")
    if not os.path.exists(tpl_path):
        sys.exit("build.py: template.html not found; the UI template has not been written yet.")
    build_data.main()
    with open(build_data.OUT_PATH, encoding="utf-8") as f:
        payload = f.read().replace("</", "<\\/")
    with open(tpl_path, encoding="utf-8") as f:
        tpl = f.read()
    if PLACEHOLDER not in tpl:
        sys.exit(f"build.py: placeholder {PLACEHOLDER} missing from template.html")
    out = tpl.replace(PLACEHOLDER, payload, 1)
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote index.html ({len(out)} bytes)")


if __name__ == "__main__":
    main()
