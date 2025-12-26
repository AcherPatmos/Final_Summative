# file_manager.py
"""
FileManager handles ONLY reading and writing JSON files.

Responsibilities:
- Load students/resources/transactions from JSON
- Save students/resources/transactions to JSON
- Handle missing files (create them as empty lists)
- Handle empty files safely
- Prevent corruption by validating that loaded data is a list

This file is designed to match SystemManager's expectations:
  load_students() -> list[dict]
  load_resources() -> list[dict]
  load_transactions() -> list[dict]
  save_students(list[dict]) -> None
  save_resources(list[dict]) -> None
  save_transactions(list[dict]) -> None
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional


class FileManagerError(Exception):
    """Base exception for file-related predictable errors."""
    pass


class FileCorruptionError(FileManagerError):
    """Raised when a JSON file exists but cannot be parsed safely."""
    pass


class FileManager:
    def __init__(
        self,
        students_file: str = "students.json",
        resources_file: str = "resources.json",
        transactions_file: str = "transactions.json",
        data_dir: Optional[str] = None,
    ):
        """
        If data_dir is provided, files will be stored inside that directory.
        Example: data_dir="data" -> data/students.json etc.
        """
        self.data_dir = data_dir
        self.students_file = self._resolve_path(students_file)
        self.resources_file = self._resolve_path(resources_file)
        self.transactions_file = self._resolve_path(transactions_file)

        # Ensure directory exists (if using data_dir)
        if self.data_dir:
            os.makedirs(self.data_dir, exist_ok=True)

        # Ensure files exist
        self._ensure_file(self.students_file)
        self._ensure_file(self.resources_file)
        self._ensure_file(self.transactions_file)

    # ----------------------------
    # Public load methods
    # ----------------------------
    def load_students(self) -> List[Dict[str, Any]]:
        return self._load_list(self.students_file)

    def load_resources(self) -> List[Dict[str, Any]]:
        return self._load_list(self.resources_file)

    def load_transactions(self) -> List[Dict[str, Any]]:
        return self._load_list(self.transactions_file)

    # ----------------------------
    # Public save methods
    # ----------------------------
    def save_students(self, students: List[Dict[str, Any]]) -> None:
        self._save_list(self.students_file, students)

    def save_resources(self, resources: List[Dict[str, Any]]) -> None:
        self._save_list(self.resources_file, resources)

    def save_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        self._save_list(self.transactions_file, transactions)

    # ----------------------------
    # Internal helpers
    # ----------------------------
    def _resolve_path(self, filename: str) -> str:
        filename = str(filename).strip()
        if not filename:
            raise ValueError("Filename cannot be empty.")
        return os.path.join(self.data_dir, filename) if self.data_dir else filename

    def _ensure_file(self, path: str) -> None:
        """
        Create file if missing. Initialize with empty list [].
        """
        if not os.path.exists(path):
            # Create parent dirs if needed
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write("[]")

    def _load_list(self, path: str) -> List[Dict[str, Any]]:
        """
        Loads a JSON file expected to contain a list of dicts.
        - Missing file: creates and returns []
        - Empty file: returns []
        - Invalid JSON: raises FileCorruptionError
        - Wrong root type (not list): raises FileCorruptionError
        """
        self._ensure_file(path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                if raw == "":
                    # Empty file treated as empty list (then repaired)
                    self._save_list(path, [])
                    return []

                data = json.loads(raw)

        except json.JSONDecodeError as e:
            raise FileCorruptionError(
                f"File '{path}' contains invalid JSON. Please fix or delete the file."
            ) from e
        except OSError as e:
            raise FileManagerError(f"Could not read file '{path}'.") from e

        if data is None:
            return []

        if not isinstance(data, list):
            raise FileCorruptionError(
                f"File '{path}' must contain a JSON list (e.g., [])."
            )

        # Ensure each entry is a dict (soft validation)
        cleaned: List[Dict[str, Any]] = []
        for i, item in enumerate(data):
            if isinstance(item, dict):
                cleaned.append(item)
            else:
                raise FileCorruptionError(
                    f"File '{path}' contains a non-object entry at index {i}. "
                    "Expected each list item to be a JSON object (dictionary)."
                )

        return cleaned

    def _save_list(self, path: str, data: List[Dict[str, Any]]) -> None:
        """
        Saves a list of dicts to JSON with safe writing:
        - Writes to a temp file first
        - Then replaces the original file
        """
        if data is None:
            data = []

        if not isinstance(data, list):
            raise FileManagerError("Data to save must be a list.")

        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise FileManagerError(
                    f"Data to save must be a list of dictionaries. Bad entry at index {i}."
                )

        tmp_path = f"{path}.tmp"

        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic-ish replace (works well on most OS)
            os.replace(tmp_path, path)

        except OSError as e:
            # Attempt cleanup
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            raise FileManagerError(f"Could not write file '{path}'.") from e
