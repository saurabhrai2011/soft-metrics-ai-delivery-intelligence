"""Answer questions about the owner from their personal documents (resume, cover letter, etc.).

Documents live in ``data/personal/`` as PDF, DOCX, TXT, or Markdown. Their text is
loaded into a single Claude system prompt — no vector store, since a handful of
personal documents fit comfortably in context.
"""
from __future__ import annotations

import os
from contextlib import nullcontext
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


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _read_docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


_READERS = {
    ".pdf": _read_pdf,
    ".docx": _read_docx,
    ".txt": _read_text,
    ".md": _read_text,
}


def load_documents(docs_dir: Path = DOCS_DIR) -> dict[str, str]:
    """Return {filename: extracted_text} for every supported document in docs_dir."""
    if not docs_dir.exists():
        return {}
    out: dict[str, str] = {}
    for path in sorted(docs_dir.iterdir()):
        if path.stem.lower() == "readme":  # folder instructions, not a personal doc
            continue
        reader = _READERS.get(path.suffix.lower())
        if not reader:
            continue
        try:
            text = reader(path).strip()
        except Exception as e:  # a single unreadable file shouldn't break the page
            text = f"[Could not read {path.name}: {e}]"
        if text:
            out[path.name] = text
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
