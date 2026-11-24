#!/usr/bin/env python3
"""Write THE LINE to $MAKEFUN_OUTPUT_DIR/entry.txt.

Stdlib only, deterministic. Writes via a temp file in the output
directory, chmod 0644 before and after os.replace, then the temp
file is gone and only entry.txt remains. After the replace, the
written file is read back and checked byte-for-byte against LINE
and its mode is checked, so a short write or a wrong file can
never pass silently.
"""

import os
import tempfile

LINE = "The Leftover Eater: a fridge that eats your leftovers before they go off and leaves a tiny receipt saying 'you're welcome', so guilt never gets a chance to grow mould."


def _validate(text: str) -> None:
    assert isinstance(text, str)
    assert 1 <= len(text) <= 220, f"length {len(text)} outside 1-220"
    assert text.strip(), "entry is only whitespace"
    assert text == text.strip(), "entry has leading or trailing whitespace"
    assert "\n" not in text and "\r" not in text, "entry must be one line"
    assert text.endswith("."), "entry must be a single sentence ending in '.'"
    assert text.count(".") == 1, "entry must contain exactly one sentence"
    text.encode("utf-8")


def main() -> None:
    _validate(LINE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(LINE)
        os.chmod(tmp, 0o644)
        os.replace(tmp, target)
        os.chmod(target, 0o644)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    # Read-back: the file on disk must be byte-identical to LINE
    # and keep mode 0644, or the run fails loudly.
    with open(target, "rb") as f:
        written = f.read()
    assert written == LINE.encode("utf-8"), "read-back mismatch"
    assert os.stat(target).st_mode & 0o777 == 0o644, "entry.txt mode is not 0644"


if __name__ == "__main__":
    main()
