import re
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    id: int
    text: str
    word_count: int
    origin_title: str
    filename: str
    category: str


class DynamicKeywordProcessor:
    """문서 내용을 학습하여 동적으로 키워드를 분해하는 클래스"""

    def __init__(self, documents: list[DocumentChunk]):
        self.documents = documents
        self.document_keywords = self._extract_document_keywords()
        self.keyword_patterns = self._learn_keyword_patterns()
        self.frequent_combinations = self._find_frequent_combinations()

    def _extract_document_keywords(self) -> set[str]:
        """문서에서 실제 사용되는 키워드 자동 추출"""
        keywords = set()

        for doc in self.documents:
            # 1. 마크다운 헤더에서 키워드 추출
            headers = re.findall(r'^#{1,6}\s+(.+)$', doc.text, re.MULTILINE)
            for header in headers:
                # 헤더에서 특수문자 제거하고 단어 추출
                clean_header = re.sub(r'[^\w\s가-힣]', ' ', header)
                words = clean_header.split()
                keywords.update(words)

            # 2. 강조된 텍스트에서 키워드 추출
            bold_texts = re.findall(r'\*\*(.+?)\*\*', doc.text)
            for bold in bold_texts:
                clean_bold = re.sub(r'[^\w\s가-힣]', ' ', bold)
                words = clean_bold.split()
                keywords.update(words)

            # 3. 코드 블록에서 키워드 추출
            code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', doc.text, re.DOTALL)
            for code in code_blocks:
                # 코드에서 한글 키워드만 추출
                korean_words = re.findall(r'[가-힣]+', code)
                keywords.update(korean_words)

            # 4. 일반 텍스트에서 한글 키워드 추출
            korean_words = re.findall(r'[가-힣]+', doc.text)
            keywords.update(korean_words)

        # 길이가 2글자 이상인 키워드만 유지
        return {kw for kw in keywords if len(kw) >= 2}

    def _learn_keyword_patterns(self) -> dict[str, list[str]]:
        """문서 키워드에서 분해 패턴 학습"""
        patterns = {}

        for keyword in self.document_keywords:
            if len(keyword) > 4:
                # 2-3글자 단위로 분해 패턴 생성
                for i in range(2, min(4, len(keyword))):
                    if i < len(keyword):
                        part1, part2 = keyword[:i], keyword[i:]

                        # 분해된 부분이 문서에 실제 존재하는지 확인
                        if part1 in self.document_keywords or part2 in self.document_keywords:
                            pattern_key = f"{part1}{part2}"
                            if pattern_key not in patterns:
                                patterns[pattern_key] = [part1, part2]

        return patterns

    def _find_frequent_combinations(self) -> dict[str, int]:
        """문서에서 자주 사용되는 키워드 조합 찾기"""
        combinations = defaultdict(int)

        for doc in self.documents:
            # 연속된 두 단어 조합 찾기
            words = re.findall(r'[가-힣]+', doc.text)
            for i in range(len(words) - 1):
                combination = f"{words[i]}{words[i+1]}"
                combinations[combination] += 1

            # 띄어쓰기로 구분된 조합도 찾기
            spaced_words = doc.text.split()
            for i in range(len(spaced_words) - 1):
                if any('\uac00' <= c <= '\ud7a3' for c in spaced_words[i]) and \
                   any('\uac00' <= c <= '\ud7a3' for c in spaced_words[i+1]):
                    combination = f"{spaced_words[i]}{spaced_words[i+1]}"
                    combinations[combination] += 1

        # 빈도가 2회 이상인 조합만 반환
        return {k: v for k, v in combinations.items() if v >= 2}

    def decompose_keyword(self, keyword: str) -> list[str]:
        """동적 키워드 분해"""
        decomposed = [keyword]

        # 1. 학습된 패턴에서 매칭
        if keyword in self.keyword_patterns:
            decomposed.extend(self.keyword_patterns[keyword])

        # 2. 빈도 기반 조합에서 분해 (개선된 로직)
        if keyword in self.frequent_combinations:
            # 빈도 조합이 있어도 더 나은 분해 시도
            # 4-5글자 단위로 먼저 시도 (더 의미있는 분해)
            for i in range(4, min(6, len(keyword))):
                if i < len(keyword):
                    part1, part2 = keyword[:i], keyword[i:]

                    # 분해된 부분이 문서에 존재하는지 확인
                    if part1 in self.document_keywords or part2 in self.document_keywords:
                        decomposed.extend([part1, part2])
                        break  # 의미있는 분해를 찾으면 중단

        # 3. 기존 2-3글자 단위 분해 (빈도 조합이 없거나 분해 실패한 경우)
        if len(decomposed) == 1:  # 아직 분해가 안된 경우
            for i in range(2, min(4, len(keyword))):
                if i < len(keyword):
                    part1, part2 = keyword[:i], keyword[i:]

                    # 분해된 부분이 문서에 존재하는지 확인
                    if part1 in self.document_keywords or part2 in self.document_keywords:
                        decomposed.extend([part1, part2])

        # 4. 한국어 복합어 추정 분해 (기존 로직 유지)
        if len(keyword) > 4 and any('\uac00' <= c <= '\ud7a3' for c in keyword):
            # 2-3글자 단위로 분해 시도
            for i in range(2, min(4, len(keyword))):
                if i < len(keyword):
                    part1, part2 = keyword[:i], keyword[i:]

                    # 분해된 부분 중 하나라도 문서에 존재하면 추가
                    if part1 in self.document_keywords or part2 in self.document_keywords:
                        decomposed.extend([part1, part2])

        return list(set(decomposed))

    def get_search_suggestions(self, keyword: str) -> list[str]:
        """검색 제안 키워드 생성"""
        suggestions = []

        # 1. 분해 제안
        decomposed = self.decompose_keyword(keyword)
        if len(decomposed) > 1:
            suggestions.append(f"'{' '.join(decomposed[1:])}'로 검색해보세요")

        # 2. 유사한 패턴 제안
        for pattern, parts in self.keyword_patterns.items():
            if keyword in pattern or any(part in keyword for part in parts):
                suggestions.append(f"'{pattern}'로 검색해보세요")

        # 3. 자주 사용되는 조합 제안
        for combination in self.frequent_combinations:
            if keyword in combination:
                suggestions.append(f"'{combination}'로 검색해보세요")

        return suggestions[:3]  # 최대 3개 제안

    def get_statistics(self) -> dict[str, int]:
        """처리기 통계 정보"""
        return {
            "total_documents": len(self.documents),
            "extracted_keywords": len(self.document_keywords),
            "learned_patterns": len(self.keyword_patterns),
            "frequent_combinations": len(self.frequent_combinations)
        }
