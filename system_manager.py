# system_manager.py
"""
Campus Resource Borrow & Return Management System - Core Logic

SystemManager is the "brain" of the program:
- Loads/saves JSON via FileManager
- Validates rules
- Manages Students, Resources, and BorrowTransactions
- Provides a clean public API for menus (staff_menu.py, student_menu.py)

Design choice: SystemManager works with plain dictionaries internally.
This makes JSON persistence simple and avoids tight coupling to model classes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional


class SystemManagerError(Exception):
    """Base exception for predictable, user-friendly errors."""
    pass


class NotFoundError(SystemManagerError):
    pass


class ValidationError(SystemManagerError):
    pass


class ConflictError(SystemManagerError):
    pass


def _today_iso() -> str:
    return date.today().isoformat()


def _parse_iso(d: str) -> date:
    # Expect YYYY-MM-DD
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception as e:
        raise ValidationError(f"Invalid date format '{d}'. Use YYYY-MM-DD.") from e


def _iso_plus_days(start_iso: str, days: int) -> str:
    return (_parse_iso(start_iso) + timedelta(days=days)).isoformat()


def _require_nonempty(value: str, field: str) -> str:
    if value is None or not str(value).strip():
        raise ValidationError(f"{field} cannot be empty.")
    return str(value).strip()


def _require_int_ge_0(value: Any, field: str) -> int:
    try:
        iv = int(value)
    except Exception as e:
        raise ValidationError(f"{field} must be an integer.") from e
    if iv < 0:
        raise ValidationError(f"{field} must be >= 0.")
    return iv


@dataclass
class RoleConfig:
    """
    Controls how role detection works from email.
    Example:
      student_domains=("student.campus.edu",)
      staff_domains=("campus.edu",)
    """
    student_domains: tuple = ("student.campus.edu",)
    staff_domains: tuple = ("campus.edu",)


class SystemManager:
    def __init__(
        self,
        file_manager,
        due_days: int = 3,
        role_config: Optional[RoleConfig] = None,
    ):
        """
        file_manager must provide:
          - load_students() -> list[dict]
          - load_resources() -> list[dict]
          - load_transactions() -> list[dict]
          - save_students(list[dict]) -> None
          - save_resources(list[dict]) -> None
          - save_transactions(list[dict]) -> None
        """
        self.file_manager = file_manager
        self.due_days = due_days
        self.role_config = role_config or RoleConfig()

        # Internal storage (lists of dicts)
        self.students: List[Dict[str, Any]] = []
        self.resources: List[Dict[str, Any]] = []
        self.transactions: List[Dict[str, Any]] = []

    # ----------------------------
    # Loading / Saving
    # ----------------------------
    def load_all(self) -> None:
        self.students = self.file_manager.load_students() or []
        self.resources = self.file_manager.load_resources() or []
        self.transactions = self.file_manager.load_transactions() or []

        # Normalize keys (in case older files used different names)
        for r in self.resources:
            if "resource_id" not in r and "item_id" in r:
                r["resource_id"] = r.pop("item_id")
            if "type" not in r and "rtype" in r:
                r["type"] = r.pop("rtype")

    def save_all(self) -> None:
        self.file_manager.save_students(self.students)
        self.file_manager.save_resources(self.resources)
        self.file_manager.save_transactions(self.transactions)

    # ----------------------------
    # Role detection
    # ----------------------------
    def determine_role(self, email: str) -> str:
        email = _require_nonempty(email, "email").lower()
        if "@" not in email:
            raise ValidationError("Email must contain '@'.")

        domain = email.split("@", 1)[1]
        if any(domain.endswith(d) for d in self.role_config.student_domains):
            return "student"
        if any(domain.endswith(d) for d in self.role_config.staff_domains):
            return "staff"

        raise ValidationError(
            "Email domain not recognized for student/staff. "
            "Use the correct campus email."
        )

    # ----------------------------
    # Find helpers
    # ----------------------------
    def _find_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        student_id = _require_nonempty(student_id, "student_id")
        return next((s for s in self.students if s.get("student_id") == student_id), None)

    def _find_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resource_id = _require_nonempty(resource_id, "resource_id")
        return next((r for r in self.resources if r.get("resource_id") == resource_id), None)

    def _find_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        transaction_id = _require_nonempty(transaction_id, "transaction_id")
        return next((t for t in self.transactions if t.get("transaction_id") == transaction_id), None)

    def _active_transactions_for_resource(self, resource_id: str) -> List[Dict[str, Any]]:
        return [
            t for t in self.transactions
            if t.get("resource_id") == resource_id and t.get("status") == "borrowed"
        ]

    def _active_transactions_for_student_resource(self, student_id: str, resource_id: str) -> List[Dict[str, Any]]:
        return [
            t for t in self.transactions
            if t.get("student_id") == student_id
            and t.get("resource_id") == resource_id
            and t.get("status") == "borrowed"
        ]

    # ----------------------------
    # ID generation
    # ----------------------------
    def _next_transaction_id(self) -> str:
        # T001, T002...
        existing_nums = []
        for t in self.transactions:
            tid = str(t.get("transaction_id", ""))
            if tid.startswith("T") and tid[1:].isdigit():
                existing_nums.append(int(tid[1:]))
        nxt = (max(existing_nums) + 1) if existing_nums else 1
        return f"T{nxt:03d}"

    # ----------------------------
    # Students
    # ----------------------------
    def add_student(self, student_id: str, name: str, email: str) -> None:
        student_id = _require_nonempty(student_id, "student_id")
        name = _require_nonempty(name, "name")
        email = _require_nonempty(email, "email")

        if self._find_student(student_id):
            raise ConflictError(f"Student ID '{student_id}' already exists.")

        self.students.append(
            {"student_id": student_id, "name": name, "email": email}
        )
        self.file_manager.save_students(self.students)

    # ----------------------------
    # Resources (Staff)
    # ----------------------------
    def add_resource(self, resource_id: str, name: str, rtype: str, quantity: Any) -> None:
        resource_id = _require_nonempty(resource_id, "resource_id")
        name = _require_nonempty(name, "name")
        rtype = _require_nonempty(rtype, "type")
        qty = _require_int_ge_0(quantity, "quantity")

        if self._find_resource(resource_id):
            raise ConflictError(f"Resource ID '{resource_id}' already exists.")

        self.resources.append(
            {"resource_id": resource_id, "name": name, "type": rtype, "quantity": qty}
        )
        self.file_manager.save_resources(self.resources)

    def update_resource_quantity(self, resource_id: str, new_quantity: Any) -> None:
        r = self._find_resource(resource_id)
        if not r:
            raise NotFoundError(f"Resource '{resource_id}' not found.")

        qty = _require_int_ge_0(new_quantity, "new_quantity")
        r["quantity"] = qty
        self.file_manager.save_resources(self.resources)

    def remove_resource(self, resource_id: str) -> None:
        r = self._find_resource(resource_id)
        if not r:
            raise NotFoundError(f"Resource '{resource_id}' not found.")

        # Block removal if currently borrowed (active transactions exist)
        active = self._active_transactions_for_resource(resource_id)
        if active:
            raise ConflictError("Cannot remove resource: it is currently borrowed.")

        self.resources = [x for x in self.resources if x.get("resource_id") != resource_id]
        self.file_manager.save_resources(self.resources)

    def list_resources(self) -> List[Dict[str, Any]]:
        # Return shallow copies to avoid accidental mutation in menus
        return [dict(r) for r in self.resources]

    def list_available_resources(self) -> List[Dict[str, Any]]:
        return [dict(r) for r in self.resources if int(r.get("quantity", 0)) > 0]

    # ----------------------------
    # Borrowing / Returning (Student)
    # ----------------------------
    def borrow_resource(self, student_id: str, resource_id: str, borrow_date: Optional[str] = None) -> Dict[str, Any]:
        student_id = _require_nonempty(student_id, "student_id")
        resource_id = _require_nonempty(resource_id, "resource_id")

        s = self._find_student(student_id)
        if not s:
            raise NotFoundError(f"Student '{student_id}' not found.")

        r = self._find_resource(resource_id)
        if not r:
            raise NotFoundError(f"Resource '{resource_id}' not found.")

        available_qty = int(r.get("quantity", 0))
        if available_qty <= 0:
            raise ConflictError("Resource is not available (quantity is 0).")

        # Optional policy: prevent borrowing same resource if already active
        active_same = self._active_transactions_for_student_resource(student_id, resource_id)
        if active_same:
            raise ConflictError("Student already has this resource borrowed and not returned.")

        bdate = borrow_date.strip() if borrow_date else _today_iso()
        # Validate date format
        _parse_iso(bdate)

        ddate = _iso_plus_days(bdate, self.due_days)
        tid = self._next_transaction_id()

        tx = {
            "transaction_id": tid,
            "student_id": student_id,
            "resource_id": resource_id,
            "borrow_date": bdate,
            "due_date": ddate,
            "return_date": None,
            "status": "borrowed",
        }

        # Update resource quantity + save
        r["quantity"] = available_qty - 1
        self.transactions.append(tx)

        self.file_manager.save_resources(self.resources)
        self.file_manager.save_transactions(self.transactions)

        return dict(tx)

    def return_resource(self, transaction_id: str, return_date: Optional[str] = None) -> Dict[str, Any]:
        tx = self._find_transaction(transaction_id)
        if not tx:
            raise NotFoundError(f"Transaction '{transaction_id}' not found.")

        if tx.get("status") != "borrowed":
            raise ConflictError("This transaction is already returned (or not active).")

        r = self._find_resource(tx.get("resource_id", ""))
        if not r:
            raise NotFoundError("Resource for this transaction no longer exists.")

        rdate = return_date.strip() if return_date else _today_iso()
        _parse_iso(rdate)

        tx["return_date"] = rdate
        tx["status"] = "returned"

        # Increase quantity
        r["quantity"] = int(r.get("quantity", 0)) + 1

        self.file_manager.save_resources(self.resources)
        self.file_manager.save_transactions(self.transactions)

        return dict(tx)

    # Convenience return method if your team insists on (student_id, resource_id)
    def return_resource_by_student_resource(self, student_id: str, resource_id: str, return_date: Optional[str] = None) -> Dict[str, Any]:
        student_id = _require_nonempty(student_id, "student_id")
        resource_id = _require_nonempty(resource_id, "resource_id")

        active = self._active_transactions_for_student_resource(student_id, resource_id)
        if not active:
            raise NotFoundError("No active borrowed transaction found for this student and resource.")
        if len(active) > 1:
            raise ConflictError("Multiple active transactions found; return using transaction_id instead.")

        return self.return_resource(active[0]["transaction_id"], return_date=return_date)

    # ----------------------------
    # Transactions / Reports (Staff)
    # ----------------------------
    def list_transactions(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if student_id:
            student_id = _require_nonempty(student_id, "student_id")
            return [dict(t) for t in self.transactions if t.get("student_id") == student_id]
        return [dict(t) for t in self.transactions]

    def is_overdue(self, tx: Dict[str, Any], current_date: str) -> bool:
        if tx.get("status") != "borrowed":
            return False
        due = _parse_iso(tx.get("due_date", ""))
        cur = _parse_iso(current_date)
        return cur > due

    def list_overdue(self, current_date: Optional[str] = None) -> List[Dict[str, Any]]:
        cdate = current_date.strip() if current_date else _today_iso()
        _parse_iso(cdate)
        return [dict(t) for t in self.transactions if self.is_overdue(t, cdate)]
