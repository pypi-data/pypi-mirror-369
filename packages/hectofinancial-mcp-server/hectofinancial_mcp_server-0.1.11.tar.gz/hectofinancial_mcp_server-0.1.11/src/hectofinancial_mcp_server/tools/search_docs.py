import re

from ..core.document_repository import get_repository
from ..core.utils.markdown_utils import format_search_result_entry


class SearchValidator:
    MAX_QUERY_LENGTH = 200
    MAX_KEYWORDS = 10
    MIN_KEYWORD_LENGTH = 1
    MAX_KEYWORD_LENGTH = 50

    @staticmethod
    def validate_and_clean_query(query: str) -> tuple[bool, str, list[str]]:
        if not query:
            return False, "검색어를 입력해 주세요.", []

        if len(query) > SearchValidator.MAX_QUERY_LENGTH:
            return (
                False,
                f"검색어가 너무 깁니다. (최대 {SearchValidator.MAX_QUERY_LENGTH}자)",
                [],
            )

        safe_query = re.sub(r"[^\w\s가-힣,.-]", "", query)

        try:
            keywords = [
                kw.strip() for kw in re.split(r"[,\s]+", safe_query) if kw.strip()
            ]
        except re.error:
            return False, "검색어 형식이 올바르지 않습니다.", []

        valid_keywords = []
        for kw in keywords:
            if (
                SearchValidator.MIN_KEYWORD_LENGTH
                <= len(kw)
                <= SearchValidator.MAX_KEYWORD_LENGTH
            ):
                valid_keywords.append(kw)

        if not valid_keywords:
            return False, "유효한 검색어가 없습니다.", []

        if len(valid_keywords) > SearchValidator.MAX_KEYWORDS:
            valid_keywords = valid_keywords[: SearchValidator.MAX_KEYWORDS]

        return True, "검증 성공", valid_keywords


def search_docs(
    query: str, category: str | list[str] | None = None
) -> dict[str, object]:
    """
    헥토파이낸셜 연동 문서에서 키워드 기반 검색을 수행합니다.

    Args:
        query (str): 검색할 키워드 문자열
            - 형식: 쉼표(,) 또는 공백으로 구분된 키워드
            - 제약: 1-200자, 최대 10개 키워드, 각 키워드 1-50자
            - 예시: "신용카드 결제", "API 연동 방법", "ezauth,내통장결제"
            - 한국어 키워드 자동 조합 지원 (예: "내통장 결제" → "내통장결제")

        category (str|list[str]|None): 검색 범위를 제한할 카테고리
            - 사용 가능한 값: "PG", "내통장결제", "간편현금결제", "화이트라벨"
            - 단일 카테고리: "PG" (PG 결제 관련 문서만 검색)
            - 다중 카테고리: ["PG", "내통장결제"] (복수 카테고리 동시 검색)
            - None: 전체 문서에서 검색 (기본값)
            - 각 카테고리 설명:
              * "PG": 전자결제 연동 관련 문서
              * "내통장결제": 내통장결제 서비스 관련 문서
              * "간편현금결제": 간편현금결제 서비스 관련 문서
              * "화이트라벨": 화이트라벨 서비스 관련 문서

    Returns:
        dict: 검색 성공 시
            {
                "검색어": list[str],           # 실제 검색에 사용된 키워드 목록
                "검색결과": list[dict],        # BM25 점수 기반 정렬된 문서 섹션
                "안내": str                    # 검색 결과 설명
            }

            검색결과 각 항목 구조:
            {
                "문서제목": str,              # 문서의 제목
                "문서ID": str,                # 문서 고유 식별자
                "카테고리": str,              # 문서 카테고리 (PG, 내통장결제, 간편현금결제, 화이트라벨)
                "본문": str                   # 매칭된 문서 섹션 내용
            }

        dict: 검색 실패 시
            {
                "오류": str,                  # 오류 메시지
                "안내": str                   # 해결 방법 안내 (선택적)
            }
    """
    is_valid, message, keywords = SearchValidator.validate_and_clean_query(query)
    if not is_valid:
        return {"오류": message}

    try:
        repository = get_repository()
        results = repository.search_documents(keywords, category=category, top_n=20)

        if "오류" in results:
            return results

        result_entries = []
        for entry in results.get("검색결과", []):
            meta = entry.get("meta", {})
            content = entry.get("content", "")
            result_entries.append(format_search_result_entry(meta, content))

        # 검색 제안 생성
        suggestions = []
        if len(result_entries) < 3:
            repository = get_repository()
            search_engine = repository.search_engine
            for keyword in keywords:
                suggestions.extend(search_engine.keyword_processor.get_search_suggestions(keyword))

        return {
            "검색어": keywords,
            "검색결과": result_entries,
            "검색제안": suggestions[:3],  # 최대 3개 제안
            "안내": results.get(
                "안내", "관련성이 높은 문서 섹션을 정렬하여 제공합니다."
            ),
        }

    except Exception as e:
        return {
            "오류": f"검색 중 문제가 발생했습니다: {e}",
            "안내": "다시 시도해 주세요. 문제가 지속되면 관리자에게 문의하세요.",
        }
