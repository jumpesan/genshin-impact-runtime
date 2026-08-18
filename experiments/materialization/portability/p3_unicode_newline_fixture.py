# -*- coding: utf-8 -*-
"""P3 Unicode/newline exact-byte fixture."""

LABEL_JA = "原神・元素反応"
LABEL_EMOJI = "月🌙星⭐"
COMPOSED = "é"
DECOMPOSED = "é"

def snapshot():
    return {
        "ja": LABEL_JA,
        "emoji": LABEL_EMOJI,
        "composed": COMPOSED,
        "decomposed": DECOMPOSED,
    }

if __name__ == "__main__":
    raise SystemExit("owner execution is outside P3 scope")
