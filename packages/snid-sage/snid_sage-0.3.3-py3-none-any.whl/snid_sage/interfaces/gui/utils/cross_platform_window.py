"""
Cross-platform window utilities and keyboard shortcuts provider.

This minimal module exists to provide `CrossPlatformWindowManager` so that
imports in GUI components resolve correctly. It centralizes platform-aware
keyboard shortcut strings and can be extended with additional windowing helpers.
"""

from __future__ import annotations

import platform
from typing import Dict, Optional

try:
    import PySide6.QtCore as QtCore
    import PySide6.QtGui as QtGui
except Exception:  # Allow non-Qt environments to import this module
    QtCore = None  # type: ignore
    QtGui = None   # type: ignore


class CrossPlatformWindowManager:
    """Cross-platform helpers for GUI behavior.

    Currently provides keyboard shortcuts mapping with OS-aware modifiers.
    """

    @staticmethod
    def get_keyboard_shortcuts() -> Dict[str, str]:
        """Return a minimal set of keyboard shortcuts adjusted per OS.

        Returns a mapping used by dialogs to present shortcuts consistently.
        """
        is_mac = platform.system() == "Darwin"
        mod = "Cmd" if is_mac else "Ctrl"
        return {
            "quick_workflow": f"{mod}+Enter",
            "quit": f"{mod}+Q",
            "copy": f"{mod}+C",
            "paste": f"{mod}+V",
        }

    # ==== New helpers for platform-aware shortcuts ====
    @staticmethod
    def is_macos() -> bool:
        return platform.system() == "Darwin"

    @staticmethod
    def platform_modifier_label() -> str:
        """Human-readable modifier for UI text: 'Cmd' on macOS, 'Ctrl' otherwise."""
        return "Cmd" if CrossPlatformWindowManager.is_macos() else "Ctrl"

    @staticmethod
    def _qt_modifier_token() -> str:
        """The token understood by QKeySequence text: 'Meta' on macOS, 'Ctrl' otherwise."""
        return "Meta" if CrossPlatformWindowManager.is_macos() else "Ctrl"

    @staticmethod
    def map_display_shortcut(combo: str) -> str:
        """Return display string with platform modifier label.

        Example: 'Ctrl+,' -> 'Cmd+,' on macOS.
        """
        mod_label = CrossPlatformWindowManager.platform_modifier_label()
        # Replace standalone 'Ctrl' tokens only
        return CrossPlatformWindowManager._replace_ctrl_token(combo, mod_label)

    @staticmethod
    def make_sequence(combo: str) -> "QtGui.QKeySequence":  # type: ignore[name-defined]
        """Create a QKeySequence from a generic combo using Ctrl as the logical modifier.

        On macOS, 'Ctrl' is converted to 'Meta' (Command) so shortcuts follow platform conventions.
        """
        if QtGui is None:
            raise RuntimeError("Qt is not available; cannot create QKeySequence")
        qt_token = CrossPlatformWindowManager._qt_modifier_token()
        combo_qt = CrossPlatformWindowManager._replace_ctrl_token(combo, qt_token)
        return QtGui.QKeySequence(combo_qt)

    @staticmethod
    def create_shortcut(parent, combo: str, callback) -> Optional["QtGui.QShortcut"]:  # type: ignore[name-defined]
        """Create and return a QShortcut using a platform-aware combo.

        Returns None if Qt is not available.
        """
        if QtGui is None:
            return None
        sequence = CrossPlatformWindowManager.make_sequence(combo)
        return QtGui.QShortcut(sequence, parent, callback)

    @staticmethod
    def standard_shortcut(parent, standard_key: "QtGui.QKeySequence.StandardKey", callback) -> Optional["QtGui.QShortcut"]:  # type: ignore[name-defined]
        """Create a QShortcut from a Qt standard key (auto platform-aware)."""
        if QtGui is None:
            return None
        sequence = QtGui.QKeySequence(standard_key)
        return QtGui.QShortcut(sequence, parent, callback)

    @staticmethod
    def _replace_ctrl_token(combo: str, replacement: str) -> str:
        """Replace standalone 'Ctrl' tokens with a replacement while preserving other text.

        Uses basic tokenization around '+' to avoid replacing substrings like 'Control'.
        """
        parts = [p.strip() for p in combo.split('+')]
        mapped = [replacement if p.lower() == 'ctrl' else p for p in parts]
        return '+'.join(mapped)


