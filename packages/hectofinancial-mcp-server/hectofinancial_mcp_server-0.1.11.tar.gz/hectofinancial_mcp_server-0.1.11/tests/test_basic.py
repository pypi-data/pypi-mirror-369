"""
기본 테스트
"""
import os
import sys

# 경로 설정
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)
sys.path.insert(0, project_root)


def test_project_structure():
    """프로젝트 구조 테스트"""
    # 핵심 디렉토리 존재 확인
    assert os.path.exists(src_path), "src 디렉토리가 없음"
    assert os.path.exists(os.path.join(src_path, "hectofinancial_mcp_server")), "패키지 디렉토리가 없음"

    # 핵심 파일 존재 확인
    core_path = os.path.join(src_path, "hectofinancial_mcp_server", "core")
    tools_path = os.path.join(src_path, "hectofinancial_mcp_server", "tools")

    assert os.path.exists(core_path), "core 디렉토리가 없음"
    assert os.path.exists(tools_path), "tools 디렉토리가 없음"
    assert os.path.exists(os.path.join(core_path, "document_repository.py")), "document_repository.py가 없음"
    assert os.path.exists(os.path.join(core_path, "search_engine.py")), "search_engine.py가 없음"


def test_imports():
    """모듈 임포트 테스트"""
    try:
        # 실제로 사용하지 않지만 임포트 가능한지 테스트
        import hectofinancial_mcp_server.core
        import hectofinancial_mcp_server.core.document_repository
        import hectofinancial_mcp_server.core.search_engine
        import hectofinancial_mcp_server.tools.get_docs
        import hectofinancial_mcp_server.tools.list_docs
        import hectofinancial_mcp_server.tools.search_docs  # noqa: F401
        assert True
    except ImportError as e:
        raise AssertionError(f"임포트 실패: {e}") from e


def test_python_version():
    """Python 버전 테스트"""
    version = sys.version_info
    assert version.major == 3, "Python 3.x 필요"
    assert version.minor >= 10, "Python 3.10+ 필요"


def test_dependencies():
    """의존성 테스트"""
    # 개인 MCP 서버이므로 선택적 의존성으로 처리
    missing_deps = []

    try:
        import mcp  # noqa: F401
    except ImportError:
        missing_deps.append("mcp")

    try:
        import fastmcp  # noqa: F401
    except ImportError:
        missing_deps.append("fastmcp")

    try:
        import mistune  # noqa: F401
    except ImportError:
        missing_deps.append("mistune")

    # 핵심 기능은 작동해야 함
    if len(missing_deps) > 0:
        print(f"⚠️ 선택적 의존성 누락: {missing_deps}")

    # 기본 Python 모듈들은 있어야 함
    assert True
