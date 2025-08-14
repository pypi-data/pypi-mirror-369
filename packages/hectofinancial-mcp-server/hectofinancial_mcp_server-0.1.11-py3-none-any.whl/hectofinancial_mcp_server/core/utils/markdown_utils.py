from dataclasses import dataclass
from typing import Any

import mistune


def md_parse_to_ast(markdown_text: str):
    markdown = mistune.create_markdown(renderer="ast")
    return markdown(markdown_text)


@dataclass
class ChunkContext:
    headings: list[str]
    filename: str | None = None
    category: str | None = None


@dataclass
class RawMarkdownBlock:
    type: str
    content: str
    ast: dict[str, Any]


@dataclass
class SectionMeta:
    context: ChunkContext
    start_line: int | None = None
    end_line: int | None = None
    ast_nodes: list[dict[str, Any]] | None = None


@dataclass
class Section:
    context: list[str]
    body: str


class HeadingContextTracker:
    def __init__(self):
        self.context_stack = []
        self.last_level2 = None

    def update(self, heading_text: str, level: int):
        self.context_stack = self.context_stack[: level - 1] + [heading_text]
        if level == 2:
            self.last_level2 = heading_text

    def get_context(self):
        ctx_stack = self.context_stack
        last_level2 = self.last_level2
        if len(ctx_stack) == 2 and ctx_stack[0] == ctx_stack[1]:
            return [ctx_stack[0]]
        if len(ctx_stack) == 2 and ctx_stack[0] in ctx_stack[1]:
            return [ctx_stack[1]]
        if len(ctx_stack) == 1 and last_level2:
            if last_level2 == ctx_stack[0]:
                return [ctx_stack[0]]
            if last_level2 in ctx_stack[0]:
                return [ctx_stack[0]]
            return [last_level2, ctx_stack[0]]
        return ctx_stack.copy()


def get_node_text(node):
    if not isinstance(node, dict):
        return str(node) if node is not None else ""
    if "raw" in node:
        return node["raw"]
    if "text" in node:
        return node["text"]
    if "children" in node:
        return "".join(get_node_text(child) for child in node["children"])
    return ""


class MarkdownChunkFormatter:
    def extract_text(self, children):
        if not children:
            return ""
        texts = []
        for node in children:
            if isinstance(node, dict):
                t = node.get("type")
                if t == "emphasis":
                    inner = self.extract_text(node.get("children", []))
                    texts.append(f"_{inner}_")
                    continue
                if t == "strong":
                    inner = self.extract_text(node.get("children", []))
                    texts.append(f"**{inner}**")
                    continue
                if t == "codespan":
                    inner = node.get("text", "")
                    texts.append(f"`{inner}`")
                    continue
                if t == "linebreak":
                    texts.append("<br>")
                    continue
                if t == "html_inline" or t == "html_block":
                    texts.append(node.get("text", ""))
                    continue
                text_val = get_node_text(node)
                if text_val:
                    texts.append(text_val)
            else:
                texts.append(str(node))
        return "".join(texts)

    def table_to_markdown(self, node):
        if not isinstance(node, dict):
            return ""
        header = node.get("header", [])
        cells = node.get("cells", [])
        n_cols = len(header)
        header_line = (
            "| "
            + " | ".join(
                [
                    self.extract_text(h.get("children", []))
                    for h in header
                    if isinstance(h, dict)
                ]
            )
            + " |"
        )
        sep_line = "|" + "---|" * n_cols
        cell_lines = []
        for row in cells:
            row_cells = [
                self.extract_text(c.get("children", [])) if isinstance(c, dict) else ""
                for c in row
            ]
            if len(row_cells) < n_cols:
                row_cells += ["" for _ in range(n_cols - len(row_cells))]
            elif len(row_cells) > n_cols:
                row_cells = row_cells[:n_cols]
            cell_lines.append("| " + " | ".join(row_cells) + " |")
        return "\n".join([header_line, sep_line] + cell_lines)

    def list_to_markdown(self, node):
        if not isinstance(node, dict):
            return ""
        items = node.get("children", [])
        ordered = node.get("ordered", False)
        lines = []
        for idx, item in enumerate(items, 1):
            prefix = f"{idx}. " if ordered else "- "
            if isinstance(item, dict):
                lines.append(prefix + self.extract_text(item.get("children", [])))
        return "\n".join(lines)


class SectionSplitter:
    def __init__(self, formatter=None, context_tracker=None):
        self.formatter = formatter or MarkdownChunkFormatter()
        self.context_tracker = context_tracker or HeadingContextTracker()

    def split(
        self, content: str, filename: str | None = None, category: str | None = None
    ) -> list[Section]:
        ast = md_parse_to_ast(content)
        sections = []
        buffer = []
        meta_buffer = []
        for node in ast:
            if not isinstance(node, dict):
                continue
            if node.get("type") == "heading":
                if buffer:
                    context = self.context_tracker.get_context()
                    sections.append(Section(context=context, body="\n".join(buffer)))
                    buffer = []
                    meta_buffer = []
                heading_text = "".join(
                    [
                        c.get("raw", "")
                        for c in node.get("children", [])
                        if isinstance(c, dict)
                    ]
                )
                level = node.get("attrs", {}).get("level")
                if level is not None:
                    self.context_tracker.update(heading_text, level)
                meta_buffer.append(node)
            elif node.get("type") == "table":
                buffer.append(self.formatter.table_to_markdown(node))
                meta_buffer.append(node)
            elif node.get("type") == "list":
                buffer.append(self.formatter.list_to_markdown(node))
                meta_buffer.append(node)
            elif node.get("type") == "block_code":
                info = node.get("info")
                code = node.get("text", "")
                buffer.append(
                    f"```{info}\n{code}\n```" if info else f"```\n{code}\n```"
                )
                meta_buffer.append(node)
            elif node.get("type") == "paragraph":
                buffer.append(self.formatter.extract_text(node.get("children", [])))
                meta_buffer.append(node)
            elif node.get("type") == "text":
                buffer.append(node.get("text", ""))
                meta_buffer.append(node)
        if buffer:
            context = self.context_tracker.get_context()
            sections.append(Section(context=context, body="\n".join(buffer)))
        return sections


def md_split_to_sections(
    content: str, filename: str | None = None, category: str | None = None
) -> list[Section]:
    splitter = SectionSplitter()
    return splitter.split(content, filename=filename, category=category)


def format_search_result_entry(meta: dict[str, Any], content: str) -> dict[str, Any]:
    return {
        "문서제목": meta.get("title"),
        "문서ID": str(meta.get("id")),
        "카테고리": meta.get("category"),
        "본문": content,
    }
