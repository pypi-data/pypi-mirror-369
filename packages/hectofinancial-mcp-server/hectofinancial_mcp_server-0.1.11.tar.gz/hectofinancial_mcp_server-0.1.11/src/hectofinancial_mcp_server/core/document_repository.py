import re
from typing import Any

from .search_engine import DocumentChunk, HectoSearchEngine
from .utils.category_utils import extract_category
from .utils.markdown_utils import (
    md_split_to_sections,
)


def extract_tags(content: str) -> list[str]:
    tag_patterns = [r"#([\w가-힣]+)", r"\[([\w가-힣]+)\]"]
    tags = set()
    for pattern in tag_patterns:
        tags.update(re.findall(pattern, content))
    return list(tags)


def format_doc_meta(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "문서ID": str(doc.get("id")) if doc.get("id") is not None else None,
        "제목": doc.get("title"),
        "카테고리": doc.get("category"),
        "파일명": doc.get("filename"),
        "태그": doc.get("tags", []),
    }


def find_doc_meta_by_identifier(
    documents: list[dict[str, Any]], identifier: str
) -> dict[str, Any] | None:
    return next(
        (
            doc
            for doc in documents
            if str(doc.get("id")) == identifier or doc.get("filename") == identifier
        ),
        None,
    )


class HectoDocumentRepository:
    def __init__(self, documents: dict[str, str]):
        self._documents_raw = documents
        self.documents = self._build_metadata(documents)
        self.chunks = self._build_chunks(documents)
        self.search_engine = HectoSearchEngine(self.chunks)

    def _build_metadata(self, documents: dict[str, str]) -> list[dict[str, Any]]:
        doc_list = []
        for i, (filename, content) in enumerate(documents.items()):
            if not (filename.endswith(".md") or filename.endswith(".js")):
                continue
            title = next(
                (line.strip() for line in content.splitlines() if line.strip()),
                filename,
            )
            doc_list.append(
                {
                    "id": i,
                    "filename": filename,
                    "title": title,
                    "category": extract_category(filename),
                    "tags": extract_tags(content),
                }
            )
        return doc_list

    def _build_chunks(self, documents: dict[str, str]) -> list[DocumentChunk]:
        chunks = []
        for rel_path, content in documents.items():
            if not rel_path.endswith(".md"):
                continue
            category = extract_category(rel_path)
            sections = md_split_to_sections(content)
            for section in sections:
                context_str = (
                    f"[{' > '.join(section.context)}]" if section.context else "[]"
                )
                section_text = context_str + "\n" + section.body
                word_count = len(section_text.split())
                if word_count > 0:
                    chunks.append(
                        DocumentChunk(
                            id=len(chunks),
                            text=section_text,
                            word_count=word_count,
                            origin_title=rel_path,
                            filename=rel_path,
                            category=category,
                        )
                    )
        return chunks

    def list_documents(
        self,
        sort_by: str = "id",
        order: str = "asc",
        category: str | list[str] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        docs = self.documents
        if category:
            if isinstance(category, str):
                docs = [doc for doc in docs if doc.get("category") == category]
            elif isinstance(category, list):
                docs = [doc for doc in docs if doc.get("category") in category]
        reverse = order == "desc"
        docs = sorted(docs, key=lambda d: d.get(sort_by, ""), reverse=reverse)
        total = len(docs)
        start = (page - 1) * page_size
        end = start + page_size
        docs_page = docs[start:end]
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "문서목록": [format_doc_meta(doc) for doc in docs_page],
        }

    def get_document_by_id(self, doc_id: int) -> str | None:
        if 0 <= doc_id < len(self.documents):
            return self._load_document_content(self.documents[doc_id]["filename"])
        return None

    def get_document_by_filename(self, filename: str) -> str | None:
        return self._documents_raw.get(filename)

    def _load_document_content(self, filename: str) -> str | None:
        return self._documents_raw.get(filename)

    def search_documents(
        self,
        keywords: list[str],
        category: str | list[str] | None = None,
        top_n: int = 20,
    ) -> dict[str, Any]:
        query = " ".join(keywords)
        scored_results = self.search_engine.calculate(query, top_n=top_n)
        entries = []
        for result in scored_results:
            chunk = self.search_engine.get_chunk_by_id(result.id)
            if not chunk:
                continue
            doc_meta = next(
                (doc for doc in self.documents if doc["filename"] == chunk.filename), {}
            )
            if category:
                if isinstance(category, str):
                    if chunk.category != category:
                        continue
                elif isinstance(category, list):
                    if chunk.category not in category:
                        continue
            content = chunk.text
            entries.append({"meta": doc_meta, "content": content})
        return {
            "검색어": keywords,
            "검색결과": entries,
            "안내": "관련성이 높은 문서 섹션을 정렬하여 제공합니다.",
        }


_repository: HectoDocumentRepository | None = None


def initialize_repository(documents: dict[str, str]) -> None:
    global _repository
    _repository = HectoDocumentRepository(documents)


def get_repository() -> HectoDocumentRepository:
    if _repository is None:
        raise RuntimeError(
            "문서 저장소가 초기화되지 않았습니다. initialize_repository(documents)를 먼저 호출하세요."
        )
    return _repository
