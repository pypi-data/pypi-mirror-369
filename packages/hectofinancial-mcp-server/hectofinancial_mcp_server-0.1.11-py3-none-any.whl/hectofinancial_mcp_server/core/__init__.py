import os

from .document_repository import (
    HectoDocumentRepository,
    get_repository,
    initialize_repository,
)

__all__ = [
    "HectoDocumentRepository",
    "get_repository",
    "initialize_repository",
    "documents",
    "load_docs",
]


def load_docs(base_dir):
    docs = {}
    if not os.path.exists(base_dir):
        print(f"⚠️ 문서 디렉토리를 찾을 수 없습니다: {base_dir}")
        return docs

    for dirpath, _, filenames in os.walk(base_dir):
        for filename in filenames:
            if filename.startswith("."):
                continue
            if not (filename.endswith(".md") or filename.endswith(".js")):
                continue
            if filename.lower() == "instructions.md":
                continue
            abs_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(abs_path, base_dir)

            try:
                with open(abs_path, encoding="utf-8") as f:
                    docs[rel_path] = f.read()
            except Exception as e:
                print(f"⚠️ 문서 로딩 실패: {rel_path} ({e})")
                continue

    return docs


documents = load_docs(os.path.join(os.path.dirname(__file__), "..", "resource", "docs"))
