"""Encrypt plaintext personal documents into committable .enc blobs.

Reads ``PERSONAL_DOCS_KEY`` (a Fernet key) from the environment / .env, then for every
supported plaintext file in ``data/personal/`` writes an encrypted ``<name>.enc`` next to
it. Stale ``.enc`` files whose plaintext source is gone are removed. Plaintext originals
stay local (gitignored); only the ``.enc`` blobs are committed to the public repo.

Re-encryption only happens when content actually changed — Fernet output is randomized,
so unconditionally re-encrypting would create noisy diffs on every run.

Usage: python scripts/encrypt_personal_docs.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DOCS_DIR = ROOT / "data" / "personal"
PLAINTEXT_SUFFIXES = {".pdf", ".docx", ".xlsx", ".txt", ".md"}


def main() -> int:
    from cryptography.fernet import Fernet

    key = os.environ.get("PERSONAL_DOCS_KEY")
    if not key:
        print("PERSONAL_DOCS_KEY is not set. Add it to .env (generate one with:\n"
              '  python -c "from cryptography.fernet import Fernet; '
              'print(Fernet.generate_key().decode())")', file=sys.stderr)
        return 1

    fernet = Fernet(key.encode())
    sources: set[str] = set()
    changes: list[str] = []

    for path in sorted(DOCS_DIR.iterdir()):
        if path.stem.lower() == "readme" or path.suffix.lower() not in PLAINTEXT_SUFFIXES:
            continue
        sources.add(path.name)
        enc = path.with_name(path.name + ".enc")
        plaintext = path.read_bytes()

        if enc.exists():
            try:
                if fernet.decrypt(enc.read_bytes()) == plaintext:
                    continue  # unchanged — leave the existing blob alone
            except Exception:
                pass  # unreadable/old key — rewrite it

        enc.write_bytes(fernet.encrypt(plaintext))
        changes.append(f"encrypted {path.name}")

    for path in sorted(DOCS_DIR.iterdir()):
        if path.suffix.lower() == ".enc" and path.name[:-4] not in sources:
            path.unlink()
            changes.append(f"removed orphaned {path.name}")

    for c in changes:
        print(c)
    if not changes:
        print("personal docs already up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
