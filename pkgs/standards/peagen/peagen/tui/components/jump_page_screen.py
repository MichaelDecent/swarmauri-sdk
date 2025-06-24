from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class JumpPageScreen(ModalScreen[int | None]):
    """Prompt the user for a page number."""

    def __init__(self, current: int, total: int) -> None:
        super().__init__()
        self.current = current
        self.total = total

    def compose(self) -> ComposeResult:  # pragma: no cover - UI code
        prompt = f"Jump to page (1-{self.total})"
        with Vertical(id="jump_page_box"):
            yield Label(prompt)
            yield Input(
                value=str(self.current), id="jump_page_input", placeholder="page"
            )
            with Horizontal():
                yield Button("Go", id="submit", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            page_str = self.query_one("#jump_page_input", Input).value
            try:
                page = int(page_str)
            except Exception:
                page = None
            self.dismiss(page)
        elif event.button.id == "cancel":
            self.dismiss(None)
