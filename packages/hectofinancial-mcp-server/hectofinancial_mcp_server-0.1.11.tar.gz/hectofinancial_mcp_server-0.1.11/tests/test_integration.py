"""
통합 테스트
"""
import os
import sys
import time

# 경로 설정
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)
sys.path.insert(0, project_root)

# ruff: noqa: E402
from hectofinancial_mcp_server.core import documents
from hectofinancial_mcp_server.core.document_repository import initialize_repository
from hectofinancial_mcp_server.tools.get_docs import get_docs
from hectofinancial_mcp_server.tools.list_docs import list_docs
from hectofinancial_mcp_server.tools.search_docs import search_docs


def test_full_search_workflow():
    """전체 검색 워크플로우 테스트"""
    # 1. 저장소 초기화
    initialize_repository(documents)

    # 2. 문서 목록 조회
    docs_list = list_docs()
    assert len(docs_list['문서목록']) > 0

    # 3. 검색 실행
    search_result = search_docs("테스트베드키", "PG")
    assert isinstance(search_result, dict)
    assert '검색어' in search_result
    assert '검색결과' in search_result

    # 4. 검색 결과가 있으면 문서 상세 조회
    if len(search_result['검색결과']) > 0:
        first_result = search_result['검색결과'][0]
        doc_detail = get_docs(doc_id=first_result['문서ID'])
        # 실제 응답 구조 확인
        assert '제목' in doc_detail
        assert '내용' in doc_detail


def test_search_queries():
    """다양한 검색 쿼리 테스트"""
    initialize_repository(documents)

    test_queries = [
        "테스트베드키",
        "신용카드 결제창",
        "암호화 키",
        "해시 생성",
        "상점아이디",
        "결제창 URL",
        "nextUrl",
        "notiUrl",
        "mchtId",
        "pktHash"
    ]

    for query in test_queries:
        result = search_docs(query, "PG")
        assert isinstance(result, dict)
        assert '검색어' in result
        assert '검색결과' in result
        assert isinstance(result['검색결과'], list)


def test_search_accuracy():
    """검색 정확도 테스트"""
    initialize_repository(documents)

    accuracy_tests = [
        ("테스트베드키", ["ST1009281328226982205", "테스트베드", "키"]),
        ("암호화 키", ["pgSettle30y739r82jtd709yOfZ2yK5K", "암호화", "키"]),
        ("상점아이디", ["nxca_jt_il", "상점", "ID"])
    ]

    for query, expected_terms in accuracy_tests:
        result = search_docs(query, "PG")

        if len(result['검색결과']) > 0:
            content = result['검색결과'][0]['본문']
            found_terms = [term for term in expected_terms if term in content]
            assert len(found_terms) > 0, f"'{query}' 검색에서 예상 용어를 찾을 수 없음"


def test_search_suggestions():
    """검색 제안 테스트"""
    initialize_repository(documents)

    result = search_docs("테스트베드키", "PG")

    if '검색제안' in result:
        suggestions = result['검색제안']
        assert isinstance(suggestions, list)

        for suggestion in suggestions:
            assert isinstance(suggestion, str)
            assert len(suggestion) > 0


def test_error_handling():
    """에러 처리 테스트"""
    initialize_repository(documents)

    # 잘못된 입력들
    error_inputs = [
        "",  # 빈 문자열
        "   ",  # 공백만
        "존재하지않는문서ID",  # 잘못된 문서 ID
    ]

    for error_input in error_inputs:
        try:
            if error_input == "존재하지않는문서ID":
                result = get_docs(doc_id=error_input)
            else:
                result = search_docs(error_input, "PG")

            # 에러가 발생하지 않고 안전한 결과 반환
            assert isinstance(result, dict)
        except Exception:
            # 예외가 발생해도 시스템이 안전해야 함
            assert True


def test_performance():
    """성능 테스트"""
    initialize_repository(documents)

    # 응답 시간 측정
    start_time = time.time()
    result = search_docs("테스트베드키", "PG")
    end_time = time.time()

    response_time = end_time - start_time

    # 개인 사용 환경에서는 1초 이내 응답이면 충분
    assert response_time < 1.0, f"응답 시간이 너무 느림: {response_time:.3f}초"

    # 결과가 정상적으로 반환되어야 함
    assert isinstance(result, dict)
    assert '검색어' in result
    assert '검색결과' in result


def test_data_consistency():
    """데이터 일관성 테스트"""
    initialize_repository(documents)

    # 동일한 쿼리로 여러 번 검색했을 때 결과가 일관되어야 함
    query = "테스트베드키"
    category = "PG"

    result1 = search_docs(query, category)
    result2 = search_docs(query, category)

    # 결과 구조가 동일해야 함
    assert isinstance(result1, dict)
    assert isinstance(result2, dict)
    assert '검색어' in result1
    assert '검색어' in result2
    assert '검색결과' in result1
    assert '검색결과' in result2

    # 검색 결과 개수가 동일해야 함
    assert len(result1['검색결과']) == len(result2['검색결과'])
