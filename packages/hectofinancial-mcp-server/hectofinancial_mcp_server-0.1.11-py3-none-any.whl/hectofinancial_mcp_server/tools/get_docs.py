from typing import Any

from ..core.document_repository import (
    find_doc_meta_by_identifier,
    format_doc_meta,
    get_repository,
)


def get_docs(doc_id: str = "1") -> dict[str, Any]:
    """
    특정 문서의 전체 내용을 조회합니다.

    Args:
        doc_id (str): 조회할 문서 식별자
            - 문서 ID 형식: "1", "2", "3" (숫자 문자열)
            - 파일 경로 형식: "pg/hecto_financial_pg.md", "ezauth/ezauth_guide.md"
            - 기본값: "1" (첫 번째 문서)
            - 유효한 문서 ID는 list_docs 도구를 통해 확인 가능
            - 파일 경로는 실제 파일 구조와 정확히 일치해야 함

    Returns:
        dict: 조회 성공 시
            {
                "문서ID": str,                # 요청한 문서 식별자
                "내용": str,                  # 마크다운 원문 전체 (제목, 본문, 코드 예시 포함)
                "안내": str                   # 사용 안내 메시지
            }

            추가 메타데이터 (사용 가능한 경우):
            {
                "제목": str,                  # 문서 제목
                "카테고리": str,              # 문서 카테고리
                "파일명": str,                # 원본 파일명
                "태그": list[str]             # 문서 태그
            }

        dict: 조회 실패 시
            {
                "오류": str                   # 오류 메시지 (문서 미존재, 접근 권한 등)
            }
    """
    try:
        repository = get_repository()

        doc_id = str(doc_id)

        if doc_id.isdigit():
            content = repository.get_document_by_id(int(doc_id))
        else:
            doc_meta = find_doc_meta_by_identifier(repository.documents, doc_id)
            content = repository.get_document_by_filename(doc_id) if doc_meta else None

        if not content:
            return {
                "오류": f"문서 ID 또는 경로 '{doc_id}'에 해당하는 문서를 찾을 수 없습니다."
            }

        doc_meta = find_doc_meta_by_identifier(repository.documents, doc_id)
        meta_info = format_doc_meta(doc_meta) if doc_meta else {"문서ID": doc_id}
        meta_info["내용"] = content
        meta_info["안내"] = "해당 문서의 전체 내용을 반환합니다."
        return meta_info

    except Exception as e:
        return {"오류": f"문서 조회 중 오류가 발생했습니다: {e}"}
