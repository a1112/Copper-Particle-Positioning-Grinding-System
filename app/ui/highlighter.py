from __future__ import annotations

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtQuick import QQuickTextDocument
import re


class SimpleSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)
        # Prepare text formats
        self.fmt_cmd = QTextCharFormat()
        self.fmt_cmd.setForeground(QColor('#6aa9ff'))  # G/M codes

        self.fmt_axis = QTextCharFormat()
        self.fmt_axis.setForeground(QColor('#ffd166'))  # X/Y/Z/F/S/T

        self.fmt_comment = QTextCharFormat()
        self.fmt_comment.setForeground(QColor('#7d7d7d'))

        self._rx_cmd = re.compile(r"\b([GM])\d+\b")
        self._rx_axis = re.compile(r"\b([XYZFST])\s*-?\d+(?:\.\d+)?\b")
        self._rx_comment = re.compile(r";.*$|\((?:[^)]*)\)")

    def highlightBlock(self, text: str) -> None:  # type: ignore[override]
        # Comments first (they can overlap others visually)
        for m in self._rx_comment.finditer(text):
            self.setFormat(m.start(), m.end() - m.start(), self.fmt_comment)
        # G/M commands
        for m in self._rx_cmd.finditer(text):
            self.setFormat(m.start(), m.end() - m.start(), self.fmt_cmd)
        # Axis/params
        for m in self._rx_axis.finditer(text):
            self.setFormat(m.start(), m.end() - m.start(), self.fmt_axis)


class HighlighterBridge(QObject):
    def __init__(self) -> None:
        super().__init__()
        self._hl = None

    @Slot(QObject)
    def attach(self, doc_obj: QObject) -> None:
        try:
            if not isinstance(doc_obj, QQuickTextDocument):
                return
            qdoc = doc_obj.textDocument()
            self._hl = SimpleSyntaxHighlighter(qdoc)
        except Exception:
            pass

