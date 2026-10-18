"""Stamp a release version into pyproject.toml.

The release pipeline takes the version from the git tag that semantic-release
creates, so the repository never carries a hand-maintained version bump.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_TABLE = re.compile(r"(?m)^\[project\]\s*$")
NEXT_TABLE = re.compile(r"(?m)^\[")
VERSION_ENTRY = re.compile(
    r'(?m)^(version[ \t]*=[ \t]*)(["\'])[^"\']*(\2)([ \t]*(?:#.*)?)$'
)


def project_table_span(text: str) -> tuple[int, int] | None:
    """Return the span of the body of the [project] table, without its header."""
    table = PROJECT_TABLE.search(text)
    if table is None:
        return None

    start = table.end()
    next_table = NEXT_TABLE.search(text, start)
    return start, next_table.start() if next_table else len(text)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {Path(argv[0]).name} <version>", file=sys.stderr)
        return 2

    version = argv[1].lstrip("v")
    path = Path("pyproject.toml")
    text = path.read_text(encoding="utf-8")

    span = project_table_span(text)
    if span is None:
        print(f"error: {path} has no [project] table", file=sys.stderr)
        return 1

    start, end = span
    body, replacements = VERSION_ENTRY.subn(
        lambda match: (
            f"{match.group(1)}{match.group(2)}{version}{match.group(3)}{match.group(4)}"
        ),
        text[start:end],
        count=1,
    )
    if replacements != 1:
        print(
            f"error: {path} has no static version entry in its [project] table. "
            "A project that derives its version dynamically must set it another way.",
            file=sys.stderr,
        )
        return 1

    path.write_text(text[:start] + body + text[end:], encoding="utf-8")
    print(f"{path}: version = {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
