from __future__ import annotations

import typing

from biscuit.common.ui import Icon

from .kinds import kinds

if typing.TYPE_CHECKING:
    from .item import CompletionItem


class Kind(Icon):
    def __init__(self, master: CompletionItem, kind: int = 0, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.base = master.base

        self.config(**self.base.theme.editors.autocomplete.item, cursor="hand2")
        self.set_kind(kind)

    def set_kind(self, kind: int = 0):
        if not kind:
            return

        kind = kinds[kind - 1] if kind <= len(kinds) and kind > 0 else kinds[0]
        self.set_icon(kind[0])
        self.set_color(kind[1] or self.base.theme.editors.foreground)
