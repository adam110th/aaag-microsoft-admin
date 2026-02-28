"""Tests for src.core.utils."""

from __future__ import annotations

import json
import pathlib

from src.core.utils import parse_range_selection, sanitize_filename, save_json, write_with_lock_check


class TestWriteWithLockCheck:
    def test_writes_successfully(self, tmp_path: pathlib.Path) -> None:
        path = tmp_path / "test.txt"
        write_with_lock_check(path, lambda p: p.write_text("hello", encoding="utf-8"))
        assert path.read_text(encoding="utf-8") == "hello"

    def test_skip_on_q(self, tmp_path: pathlib.Path, monkeypatch) -> None:
        path = tmp_path / "locked.txt"

        call_count = 0

        def _failing_writer(p: pathlib.Path) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise PermissionError("locked")
            p.write_text("ok", encoding="utf-8")

        monkeypatch.setattr("builtins.input", lambda _prompt: "q")
        write_with_lock_check(path, _failing_writer)
        assert not path.exists()


class TestSaveJson:
    def test_writes_utf8_json(self, tmp_path: pathlib.Path) -> None:
        data = {"name": "Tes\u00f6rszeg", "count": 42}
        path = tmp_path / "out.json"
        save_json(data, path)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["name"] == "Tesörszeg"


class TestSanitizeFilename:
    def test_removes_bad_chars(self) -> None:
        assert sanitize_filename('file:with"bad<chars>') == "file_with_bad_chars_"

    def test_empty_becomes_unnamed(self) -> None:
        assert sanitize_filename("") == "_unnamed_"

    def test_strips_dots_and_spaces(self) -> None:
        assert sanitize_filename("...file...") == "file"


class TestParseRangeSelection:
    def test_single_values(self) -> None:
        assert parse_range_selection("1,3,5", 10) == [1, 3, 5]

    def test_ranges(self) -> None:
        assert parse_range_selection("5-8", 10) == [5, 6, 7, 8]

    def test_mixed(self) -> None:
        assert parse_range_selection("1,3,5-8", 10) == [1, 3, 5, 6, 7, 8]

    def test_out_of_bounds_ignored(self) -> None:
        assert parse_range_selection("0,5,11", 10) == [5]

    def test_empty_string(self) -> None:
        assert parse_range_selection("", 10) == []

    def test_invalid_values(self) -> None:
        assert parse_range_selection("abc,1,xyz", 10) == [1]

    def test_deduplication(self) -> None:
        assert parse_range_selection("1,1,1", 10) == [1]
