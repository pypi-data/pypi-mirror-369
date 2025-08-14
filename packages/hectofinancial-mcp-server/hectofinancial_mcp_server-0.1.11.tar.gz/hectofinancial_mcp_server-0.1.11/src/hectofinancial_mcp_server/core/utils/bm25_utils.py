import math
from typing import Any


def calculate_idf(df: int, n: int) -> float:
    if df <= 0 or n <= 0 or df >= n:
        return 0.0

    numerator = n - df + 0.5
    denominator = df + 0.5

    if denominator <= 0:
        return 0.0

    ratio = numerator / denominator
    if ratio <= 0:
        return 0.0

    return math.log(ratio)


class BM25Params:
    def __init__(
        self,
        k1: float = 1.2,
        b: float = 0.75,
        average_doc_length: float = 0.0,
        n: float = 0.0,
    ):
        self.k1 = k1
        self.b = b
        self.average_doc_length = float(average_doc_length)
        self.n = float(n)


class BM25Result:
    def __init__(self, id: int, score: float, total_tf: int):
        self.id = id
        self.score = score
        self.total_tf = total_tf


def minimal_pattern_expand(keywords: list[str]) -> list[str]:
    expanded = set(keywords)

    for keyword in keywords:
        if any("\uac00" <= c <= "\ud7a3" for c in keyword):
            expanded.add(keyword.replace(" ", ""))
            expanded.update(keyword.split())

        if keyword.isalpha():
            expanded.add(keyword.upper())
            expanded.add(keyword.lower())

    return list(expanded)


def auto_calculate_weight(
    keyword: str, doc_frequencies: dict[str, int], total_docs: int
) -> float:
    df = doc_frequencies.get(keyword, 0)
    if df == 0 or total_docs == 0:
        return 1.0

    frequency_ratio = df / total_docs
    freq_weight = 1.0

    if frequency_ratio > 0.7:
        freq_weight = 0.6

    elif 0.1 <= frequency_ratio <= 0.3:
        freq_weight = 1.4

    elif frequency_ratio < 0.05:
        freq_weight = 0.8

    length_weight = 1.0
    if len(keyword) >= 6:
        length_weight = 1.6
    elif len(keyword) >= 4:
        length_weight = 1.3
    elif len(keyword) <= 2:
        length_weight = 0.7

    return freq_weight * length_weight


def detect_structural_importance(chunk_text: str, keywords: list[str]) -> float:
    if not chunk_text:
        return 1.0

    lines = chunk_text.splitlines()
    if not lines:
        return 1.0

    first_line = lines[0].strip()
    boost = 1.0

    has_keyword = any(keyword.lower() in first_line.lower() for keyword in keywords)
    if not has_keyword:
        return boost

    if first_line.startswith("#"):
        level = len(first_line) - len(first_line.lstrip("#"))
        if level <= 3:
            boost = 3.5 - (level * 0.4)

    elif first_line.startswith("[") and "]" in first_line:
        boost = 2.2

    elif "**" in first_line or "__" in first_line:
        boost = 1.8

    elif any(first_line.startswith(f"{i}.") for i in range(1, 10)):
        boost = 1.6

    elif any(
        first_line.startswith(f"{i}.{j}") for i in range(1, 10) for j in range(1, 10)
    ):
        boost = 2.0

    return boost


def bm25_score(
    term_frequencies: dict[int, dict[str, int]],
    doc_frequencies: dict[str, int],
    chunks: list[Any],
    params: BM25Params,
    keywords: list[str],
) -> list[BM25Result]:
    results = []

    expanded_keywords = keywords

    for chunk in chunks:
        if chunk.id not in term_frequencies:
            continue

        tf = term_frequencies[chunk.id]
        if not tf:
            continue

        length = chunk.word_count
        main_score = 0.0

        matched_keywords = []
        for keyword in expanded_keywords:
            if keyword in tf:
                matched_keywords.append(keyword)
                df = doc_frequencies.get(keyword, 0)
                if df == 0:
                    continue

                idf = calculate_idf(df, int(params.n))
                term_freq = tf[keyword]

                weight = auto_calculate_weight(keyword, doc_frequencies, int(params.n))

                numerator = term_freq * (params.k1 + 1)

                if params.average_doc_length > 0:
                    denominator = term_freq + params.k1 * (
                        1 - params.b + params.b * (length / params.average_doc_length)
                    )
                else:
                    denominator = term_freq + params.k1

                if denominator > 0:
                    main_score += idf * (numerator / denominator) * weight

        if not matched_keywords:
            continue

        structural_bonus = detect_structural_importance(chunk.text, matched_keywords)

        final_score = main_score * structural_bonus
        total_tf = sum(tf[keyword] for keyword in matched_keywords if keyword in tf)

        results.append(BM25Result(id=chunk.id, score=final_score, total_tf=total_tf))

    return deduplicate_search_results(results, chunks)


def deduplicate_search_results(
    results: list[BM25Result], chunks: list[Any]
) -> list[BM25Result]:
    import hashlib
    from collections import defaultdict

    content_groups = defaultdict(list)

    for result in results:
        chunk = chunks[result.id] if result.id < len(chunks) else None
        if chunk:
            content_lines = chunk.text.split("\n")
            body_content = (
                "\n".join(content_lines[1:]) if len(content_lines) > 1 else chunk.text
            )
            content_hash = hashlib.md5(body_content.encode()).hexdigest()
            content_groups[content_hash].append(result)

    deduplicated = []
    for group in content_groups.values():
        if group:
            best_result = max(group, key=lambda x: x.score)
            deduplicated.append(best_result)

    return deduplicated
