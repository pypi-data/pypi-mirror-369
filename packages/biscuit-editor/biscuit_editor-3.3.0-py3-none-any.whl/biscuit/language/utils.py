"""
Code is taken from Porcupine's LSP plugin https://github.com/Akuli/porcupine/

MIT License

Copyright (c) 2017-2023 Akuli

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
from pathlib import Path
from typing import Iterator, Optional
from urllib.request import url2pathname

import tarts as lsp


# Copyright (c) 2021-2024 tomlin7
def to_document_symbol(infos: list[lsp.SymbolInformation]) -> list[lsp.DocumentSymbol]:
    if not infos:
        return []

    infos.sort(
        key=lambda x: (
            (x.location.range.start.line, x.location.range.start.character),
            (-x.location.range.end.line, -x.location.range.end.character),
        )
    )
    res: list[lsp.DocumentSymbol] = []
    parents: list[lsp.DocumentSymbol] = []

    for info in infos:
        element = lsp.DocumentSymbol(
            name=info.name or "Error Symbol",
            kind=info.kind,
            children=[],
            range=info.location.range,
            selectionRange=info.location.range,
        )

        while True:
            if not parents:
                parents.append(element)
                res.append(element)
                break
            parent = parents[-1]
            if contains_range(parent.range, element.range) and not equals_range(
                parent.range, element.range
            ):
                # TODO avoid adding the same named element twice to same parent
                parent.children.append(element)
                parents.append(element)
                break
            parents.pop()

    return res


def get_completion_item_doc(item: lsp.CompletionItem) -> str:
    if not item.documentation:
        return item.label
    if isinstance(item.documentation, lsp.MarkupContent):
        return item.label + "\n" + item.documentation.value
    return item.label + "\n" + item.documentation


def decode_path_uri(file_url: str) -> str:
    if sys.platform == "win32":
        if file_url.startswith("file:///"):
            return url2pathname(file_url[8:])
        else:
            return url2pathname(file_url[5:])
    else:
        return url2pathname(file_url[7:])


def jump_paths_and_ranges(
    locations: list[lsp.Location] | lsp.Location,
) -> Iterator[tuple[Path, lsp.Range]]:
    if not locations:
        locations = []
    if not isinstance(locations, list):
        locations = [locations]

    for location in locations:
        if isinstance(location, lsp.LocationLink):
            yield (decode_path_uri(location.targetUri), location.targetSelectionRange)
        else:
            yield (decode_path_uri(location.uri), location.range)


def hover_filter(
    content: lsp.MarkupContent | str,
) -> list[Optional[list[str, str]], str]:
    if not isinstance(content, lsp.MarkupContent):
        return None, None

    value = content.value.strip()
    if value.startswith("```"):
        value = [i.strip() for i in value[3:].split("```", 1)]
        return value[0].split("\n"), value[1]

    return None, value


def encode_position(pos: str | list[int]) -> lsp.Position:
    if isinstance(pos, str):
        line, column = map(int, pos.split("."))
    else:
        line, column = pos
    return lsp.Position(line=line - 1, character=column)


def decode_position(pos: lsp.Position) -> str:
    return f"{pos.line + 1}.{pos.character}"


def contains_range(range: lsp.Range, pos: lsp.Range) -> bool:
    if pos.start.line < range.start.line or pos.end.line > range.end.line:
        return False
    if (
        pos.start.line == range.start.line
        and pos.start.character < range.start.character
    ):
        return False
    if pos.end.line == range.end.line and pos.end.character > range.end.character:
        return False
    return True


def equals_range(a: lsp.Range, b: lsp.Range) -> bool:
    if not (a or b):
        return True

    return (
        a
        and b
        and a.start.line == b.start.line
        and a.start.character == b.start.character
        and a.end.line == b.end.line
        and a.end.character == b.end.character
    )
