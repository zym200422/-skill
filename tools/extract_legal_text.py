import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
        if tag in {"p", "div", "li", "tr", "h1", "h2", "h3", "br", "table"}:
            self.chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth and data.strip():
            self.chunks.append(data)


def html_to_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    lines = [re.sub(r"[ \t\u3000]+", " ", line).strip() for line in "".join(parser.chunks).splitlines()]
    return "\n".join(line for line in lines if line)


def slice_between(text: str, start: str, end: str) -> str:
    start_pos = text.find(start)
    if start_pos < 0:
        raise SystemExit(f"start marker not found: {start}")
    end_pos = text.find(end, start_pos + len(start))
    section = text[start_pos:end_pos] if end_pos >= 0 else text[start_pos:]
    return section.strip()


def main() -> None:
    src, dst, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    html = Path(src).read_text(encoding="utf-8", errors="ignore")
    text = html_to_text(html)
    if mode == "range":
        start, end = sys.argv[4], sys.argv[5]
        text = slice_between(text, start, end)
    elif mode == "civil_code_lease":
        text = slice_between(text, "第七百零三条", "第七百三十五条")
        text = "第十四章 租赁合同\n\n" + text
    Path(dst).write_text(text + "\n", encoding="utf-8")
    print(f"{dst}: {len(text)} chars")


if __name__ == "__main__":
    main()
