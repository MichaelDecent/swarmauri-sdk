import pytest
import asyncio

from peagen.tui.app import QueueDashboardApp


class DummyTable:
    def __init__(self, key):
        self.key = key
        self.cursor_row = 0
        self.cursor_column = 0
        self.rows: list[tuple[tuple[str, ...], str | None]] = []

    def get_row_key(self, row):
        return self.key

    def clear(self):
        self.rows.clear()

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def cursor_coordinate(self):
        return (self.cursor_row, self.cursor_column)

    @cursor_coordinate.setter
    def cursor_coordinate(self, coord):
        self.cursor_row, self.cursor_column = coord

    def add_row(self, *values, key=None):
        self.rows.append((values, key))


class DummyTableNoGetRowKey:
    """Simulate DataTable without ``get_row_key``."""

    def __init__(self):
        from textual._two_way_dict import TwoWayDict

        self.cursor_row = 0
        self.cursor_column = 0
        self.rows: list[tuple[tuple[str, ...], str | None]] = []
        self._row_locations = TwoWayDict({})

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def cursor_coordinate(self):
        return (self.cursor_row, self.cursor_column)

    @cursor_coordinate.setter
    def cursor_coordinate(self, coord):
        self.cursor_row, self.cursor_column = coord

    def add_row(self, *values, key=None):
        index = len(self.rows)
        self.rows.append((values, key))
        if key is not None:
            self._row_locations[key] = index

    def clear(self):
        from textual._two_way_dict import TwoWayDict

        self.rows.clear()
        self._row_locations = TwoWayDict({})


@pytest.mark.unit
def test_default_collapsed(monkeypatch):
    parent = {"id": "p1", "result": {"children": ["c1"]}}
    child = {"id": "c1"}
    app = QueueDashboardApp()
    app.backend.tasks = [parent, child]
    app.client.tasks = {}
    app.tasks_table = DummyTable("p1")
    monkeypatch.setattr(app, "call_later", lambda func, *args, **kwargs: func(*args, **kwargs))
    monkeypatch.setattr(app, "trigger_data_processing", lambda debounce=True: asyncio.run(app.async_process_and_update_data()))

    asyncio.run(app.async_process_and_update_data())

    assert "p1" in app.collapsed


@pytest.mark.unit
def test_toggle_children_updates_table(monkeypatch):
    parent = {"id": "p1", "result": {"children": ["c1"]}}
    child = {"id": "c1"}
    app = QueueDashboardApp()
    app.backend.tasks = [parent, child]
    app.client.tasks = {}
    app.tasks_table = DummyTableNoGetRowKey()
    monkeypatch.setattr(app, "call_later", lambda func, *args, **kwargs: func(*args, **kwargs))
    monkeypatch.setattr(app, "trigger_data_processing", lambda debounce=True: asyncio.run(app.async_process_and_update_data()))

    asyncio.run(app.async_process_and_update_data())

    # Initially collapsed: prefix shows '+'
    assert app.tasks_table.rows
    assert app.tasks_table.rows[0][0][0].startswith("+ ")
    assert "p1" in app.collapsed

    app.action_toggle_children()
    asyncio.run(app.async_process_and_update_data())

    # Expanded: prefix switches to '-'
    assert app.tasks_table.rows[0][0][0].startswith("- ")
    assert "p1" not in app.collapsed

    app.action_toggle_children()
    asyncio.run(app.async_process_and_update_data())

    # Collapsed again: prefix resets to '+'
    assert app.tasks_table.rows[0][0][0].startswith("+ ")
    assert "p1" in app.collapsed
