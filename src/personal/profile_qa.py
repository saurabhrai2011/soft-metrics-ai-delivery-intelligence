"""Answer questions about the owner from their personal documents (resume, cover letter, etc.).

Documents live in ``data/personal/`` as PDF, DOCX, XLSX, TXT, or Markdown. To keep them
out of the public repo, the committed copies are Fernet-encrypted ``<name>.enc`` blobs;
the plaintext originals stay local (gitignored). At load time ``.enc`` files are decrypted
in memory using ``PERSONAL_DOCS_KEY``. Plaintext originals, when present locally, take
precedence so local edits show up without re-encrypting.

Their text is loaded into a single Claude system prompt — no vector store, since a handful
of personal documents fit comfortably in context.
"""
from __future__ import annotations

import os
from contextlib import nullcontext
from io import BytesIO
from pathlib import Path

from anthropic import Anthropic

from src.observability.tracing import get_langfuse, propagate_attributes

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = PROJECT_ROOT / "data" / "personal"

_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5")

SYSTEM_PROMPT = (
    "You answer questions about a person using only the documents provided below "
    "(their resume, cover letter, and related materials). Speak about them in the "
    "third person by name when known. Ground every claim in the documents — if the "
    "answer is not present, say you don't have that information rather than guessing. "
    "Be concise and professional.\n\n"
    "=== DOCUMENTS ===\n{documents}\n=== END DOCUMENTS ==="
)


def _read_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _read_docx(data: bytes) -> str:
    from docx import Document

    doc = Document(BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)


def _read_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def _read_xlsx(data: bytes) -> str:
    import pandas as pd

    sheets = pd.read_excel(BytesIO(data), sheet_name=None)  # all sheets
    parts = []
    for name, df in sheets.items():
        parts.append(f"[Sheet: {name}]\n{df.to_csv(index=False)}")
    return "\n\n".join(parts)


_READERS = {
    ".pdf": _read_pdf,
    ".docx": _read_docx,
    ".txt": _read_text,
    ".md": _read_text,
    ".xlsx": _read_xlsx,
}


def _decrypt(blob: bytes, key: str) -> bytes:
    from cryptography.fernet import Fernet

    return Fernet(key.encode()).decrypt(blob)


def _extract(reader, get_bytes, name: str) -> str:
    """Run a reader over lazily-fetched bytes, turning any failure into inline text."""
    try:
        return reader(get_bytes()).strip()
    except Exception as e:  # a single unreadable/undecryptable file shouldn't break the page
        return f"[Could not read {name}: {e}]"


def load_documents(docs_dir: Path = DOCS_DIR, key: str | None = None) -> dict[str, str]:
    """Return {filename: extracted_text} for every supported document in docs_dir.

    Reads plaintext originals when present (local dev) and falls back to decrypting the
    committed ``<name>.enc`` blobs. ``key`` defaults to the ``PERSONAL_DOCS_KEY`` env var.
    """
    if not docs_dir.exists():
        return {}
    key = key or os.environ.get("PERSONAL_DOCS_KEY")
    out: dict[str, str] = {}

    # Plaintext originals first — these win over their encrypted counterparts.
    for path in sorted(docs_dir.iterdir()):
        if path.suffix.lower() == ".enc" or path.stem.lower() == "readme":
            continue
        reader = _READERS.get(path.suffix.lower())
        if not reader:
            continue
        text = _extract(reader, path.read_bytes, path.name)
        if text:
            out[path.name] = text

    # Encrypted blobs — only for docs whose plaintext isn't present locally.
    for path in sorted(docs_dir.iterdir()):
        if path.suffix.lower() != ".enc":
            continue
        inner = Path(path.stem)  # e.g. "SaurabhRai_Resume.docx.enc" -> "SaurabhRai_Resume.docx"
        reader = _READERS.get(inner.suffix.lower())
        if not reader or inner.name in out:
            continue
        if not key:
            out[inner.name] = "[Encrypted document — PERSONAL_DOCS_KEY not configured]"
            continue
        text = _extract(reader, lambda p=path: _decrypt(p.read_bytes(), key), inner.name)
        if text:
            out[inner.name] = text

    return out


def _build_documents_block(documents: dict[str, str]) -> str:
    return "\n\n".join(f"--- {name} ---\n{text}" for name, text in documents.items())


def answer_about_me(
    question: str,
    documents: dict[str, str],
    user_id: str | None = None,
    session_id: str | None = None,
    source: str | None = None,
) -> str:
    """Answer a question about the owner, grounded in their documents. Returns the answer text."""
    if not documents:
        return "No personal documents found. Add files to `data/personal/` to enable this."

    system = SYSTEM_PROMPT.format(documents=_build_documents_block(documents))
    messages = [{"role": "user", "content": question}]

    lf = get_langfuse()
    observe = lf.start_as_current_observation if lf else lambda **_: nullcontext()
    attrs = (
        propagate_attributes(
            trace_name="about-me",
            user_id=user_id,
            session_id=session_id,
            tags=[source] if source else None,
        )
        if lf
        else nullcontext()
    )

    with attrs, observe(name="about-me", as_type="generation", model=MODEL,
                        model_parameters={"max_tokens": 1024}, input=messages):
        resp = _client.messages.create(
            model=MODEL, max_tokens=1024, system=system, messages=messages,
        )
        answer = "".join(b.text for b in resp.content if b.type == "text")
        if lf:
            lf.update_current_generation(
                output=answer,
                usage_details={"input": resp.usage.input_tokens, "output": resp.usage.output_tokens},
            )
            lf.flush()

    return answer
