# Personal documents

Drop the documents the **About Saurabh** page should answer from into this folder:

- `resume.pdf` / `resume.docx`
- `cover_letter.pdf` / `cover_letter.docx`
- any other supporting docs

Supported formats: **`.pdf`, `.docx`, `.xlsx`, `.txt`, `.md`**.

## Privacy: plaintext stays local, only encrypted blobs are committed

This is a **public** repo, so the plaintext files here are **gitignored** and never
pushed. Instead, each file is encrypted to a `<name>.enc` blob (Fernet), and only those
`.enc` blobs are committed. The app decrypts them at runtime using `PERSONAL_DOCS_KEY`.

The pre-commit hook (`scripts/git-hooks/pre-commit`) encrypts changed files and stages the
`.enc` automatically on every commit. Enable it once per clone with:

```
git config core.hooksPath scripts/git-hooks
```

To encrypt manually: `python scripts/encrypt_personal_docs.py`.

### Deploying (Streamlit Cloud)

Add `PERSONAL_DOCS_KEY` (the same Fernet key as your local `.env`) to the app's
**Settings → Secrets**. Without it, the encrypted documents can't be read.
