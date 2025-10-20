from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, Property, QCoreApplication, QSettings, Signal, Slot
from PySide6.QtCore import QTranslator


class LocalizationManager(QObject):
    """Bridge that exposes translation control to QML and manages Qt translators."""

    languageChanged = Signal()

    def __init__(self, translations_dir: Path | str, default_language: str = "zh_CN") -> None:
        super().__init__()
        self._dir = Path(translations_dir)
        self._translator: Optional[QTranslator] = None
        self._language: str = "zh_CN"

        # Predefined language list so QML can show friendly labels.
        self._languages: List[Dict[str, str]] = [
            {"code": "zh_CN", "label": "\u7b80\u4f53\u4e2d\u6587"},
            {"code": "en_US", "label": "English"},
            {"code": "ja_JP", "label": "\u65e5\u672c\u8a9e"},
        ]

        # Apply persisted value on startup; fall back if invalid.
        self._apply_language(default_language or "zh_CN", force=True)

    # --- Properties exposed to QML -------------------------------------------------

    @Property("QVariantList", constant=True)
    def availableLanguages(self) -> List[Dict[str, str]]:
        return self._languages

    @Property(str, notify=languageChanged)
    def currentLanguage(self) -> str:
        return self._language

    @currentLanguage.setter  # type: ignore[override]
    def currentLanguage(self, code: str) -> None:
        self.setLanguage(code)

    # --- Public slots --------------------------------------------------------------

    @Slot(str, result=str)
    def displayName(self, code: str) -> str:
        code = str(code)
        for item in self._languages:
            if item.get("code") == code:
                return item.get("label", code)
        return code or ""

    @Slot(str)
    def setLanguage(self, code: str) -> None:
        self._apply_language(str(code or "zh_CN"))

    # --- Internal helpers ---------------------------------------------------------

    def _apply_language(self, code: str, *, force: bool = False) -> None:
        code = code or "zh_CN"
        code = code if any(item["code"] == code for item in self._languages) else "zh_CN"

        # Avoid redundant installer work unless explicitly forced.
        if not force and code == self._language:
            if code == "zh_CN" and self._translator is None:
                return
            if code != "zh_CN" and self._translator is not None:
                return

        if code == "zh_CN":
            if self._translator is not None:
                QCoreApplication.removeTranslator(self._translator)
                self._translator = None
            self._language = code
            self.languageChanged.emit()
            return

        translator = QTranslator()
        base_name = f"app_{code}"
        candidates = [
            self._dir / f"{base_name}.qm",
            self._dir / code / f"{base_name}.qm",
        ]

        loaded = False
        for candidate in candidates:
            if candidate.exists() and translator.load(str(candidate)):
                loaded = True
                break

        if loaded:
            if self._translator is not None:
                QCoreApplication.removeTranslator(self._translator)
            QCoreApplication.installTranslator(translator)
            self._translator = translator
            self._language = code
            self.languageChanged.emit()
            return

        # Fallback: remove translator and revert to default language.
        if self._translator is not None:
            QCoreApplication.removeTranslator(self._translator)
            self._translator = None
        self._language = "zh_CN"
        self.languageChanged.emit()


def read_persisted_language(default: str = "zh_CN") -> str:
    """Helper to fetch the stored language from QSettings before QML loads."""
    settings = QSettings()
    value = str(settings.value("language", default) or default)
    return value if value else default
