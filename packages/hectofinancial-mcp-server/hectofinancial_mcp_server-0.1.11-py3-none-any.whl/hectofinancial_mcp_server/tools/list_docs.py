from ..core.document_repository import get_repository


def list_docs(category: str | list[str] | None = None) -> dict[str, object]:
    """
    헥토파이낸셜 연동 문서 목록을 조회합니다.

    Args:
        category (str|list[str]|None): 조회할 문서 카테고리
            - 사용 가능한 값: "PG", "내통장결제", "간편현금결제", "화이트라벨"
            - 단일 카테고리: "PG" (PG 결제 관련 문서만 조회)
            - 다중 카테고리: ["PG", "내통장결제"] (복수 카테고리 동시 조회)
            - None: 전체 문서 조회 (기본값)
            - 각 카테고리 설명:
              * "PG": 전자결제 연동 관련 문서 (신용카드, 계좌이체 등)
              * "내통장결제": 내통장결제 서비스 관련 문서 (ezauth)
              * "간편현금결제": 간편현금결제 서비스 관련 문서 (ezcp)
              * "화이트라벨": 화이트라벨 서비스 관련 문서 (whitelabel)

    Returns:
        dict: 조회 성공 시
            {
                "문서목록": list[dict],        # 문서 목록 배열
                "안내": str                    # 사용 안내 메시지
            }

            문서목록 각 항목 구조:
            {
                "문서ID": str,                # 문서 고유 식별자 (get_docs 호출 시 사용)
                "제목": str,                  # 문서 제목 (마크다운 # 제목)
                "카테고리": str,              # 문서 카테고리 (PG, 내통장결제, 간편현금결제, 화이트라벨)
                "파일명": str,                # 원본 파일명 (확장자 포함)
                "태그": list[str]             # 문서 태그 목록
            }

        dict: 조회 실패 시
            {
                "오류": str                   # 오류 메시지
            }
    """
    try:
        repository = get_repository()
        result = repository.list_documents(
            sort_by="id",
            order="asc",
            category=category,
            page=1,
            page_size=50,
        )
        return {
            "문서목록": result["문서목록"],
            "안내": "문서 ID를 참고해 get_docs로 상세 내용을 확인할 수 있습니다.",
        }
    except Exception as e:
        return {"오류": f"문서 목록 처리 중 문제가 발생했습니다: {e}"}
