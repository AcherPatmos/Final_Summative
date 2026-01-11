"""
Campus Resource Borrow & Return Management System - Core Logic

This file contains the SystemManager class which controls the main rules of the system.
- It loads and saves data through FileManager
- It checks inputs and prevents invalid actions
- It manages students, resources, and borrowing transactions

"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional


# ----------------------------
# Custom Errors (so menus can show clear messages)
# ----------------------------
class SystemManagerError(Exception):
    """Base exception for predictable, user-friendly errors."""
    pass


class NotFoundError(SystemManagerError):
    """Raised when a student/resource/transaction cannot be found."""
    pass


class ValidationError(SystemManagerError):
    """Raised when user input is invalid (empty, wrong format, etc.)."""
    pass


class ConflictError(SystemManagerError):
    """Raised when an action is not allowed (duplicate, unavailable, etc.)."""
    pass


# ----------------------------
# Helper functions
# ----------------------------
def today_iso() -> str:
    """Return today's date as YYYY-MM-DD."""
    return date.today().isoformat()


def parse_iso(d: str) -> date:
    """Convert YYYY-MM-DD string into a date object (and validate format)."""
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception as e:
        raise ValidationError(f"Invalid date format '{d}'. Use YYYY-MM-DD.") from e


def iso_plus_days(start_iso: str, days: int) -> str:
    """Add days to a YYYY-MM-DD date string and return YYYY-MM-DD."""
    new_date = parse_iso(start_iso) + timedelta(days=days)
    return new_date.isoformat()


def require_nonempty(value: Any, field: str) -> str:
    """Ensure a value is not empty."""
    if value is None or not str(value).strip():
        raise ValidationError(f"{field} cannot be empty.")
    return str(value).strip()


def require_int_ge_0(value: Any, field: str) -> int:
    """Ensure a value is an integer >= 0."""
    try:
        iv = int(value)
    except Exception as e:
        raise ValidationError(f"{field} must be an integer.") from e

    if iv < 0:
        raise ValidationError(f"{field} must be >= 0.")
    return iv


# ----------------------------
# Role configuration (no dataclass)
# ----------------------------
class RoleConfig:
    """
    Controls role detection based on email domain.
    Example:
      student_domains=("alustudent.com",)
      staff_domains=("alu.edu",)
    """

    def __init__(
        self,
        student_domains: tuple = ("alustudent.com",),
        staff_domains: tuple = ("alueducation.com",),
    ):
        self.student_domains = student_domains
        self.staff_domains = staff_domains


# ----------------------------
# System Manager
# ----------------------------
class SystemManager:
    def __init__(self, file_manager, due_days: int = 3, role_config: Optional[RoleConfig] = None):
        self.file_manager = file_manager
        self.due_days = due_days
        self.role_config = role_config if role_config is not None else RoleConfig()

        # In-memory data
        self.students: List[Dict[str, Any]] = []
        self.resources: List[Dict[str, Any]] = []
        self.transactions: List[Dict[str, Any]] = []

    # ----------------------------
    # Load / Save
    # ----------------------------
    def load_all(self) -> None:
        self.students = self.file_manager.load_students() or []
        self.resources = self.file_manager.load_resources() or []
        self.transactions = self.file_manager.load_transactions() or []

        # normalize old keys (optional safety)
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
        email = require_nonempty(email, "email").lower()

        if "@" not in email:
            raise ValidationError("Email must contain '@'.")

        domain = email.split("@", 1)[1]

        for d in self.role_config.student_domains:
            if domain.endswith(d):
                return "student"

        for d in self.role_config.staff_domains:
            if domain.endswith(d):
                return "staff"

        raise ValidationError("Email domain not recognized for student/staff. Use the correct campus email.")

    # ----------------------------
    # Find helpers
    # ----------------------------
    def find_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        student_id = require_nonempty(student_id, "student_id")
        for s in self.students:
            if s.get("student_id") == student_id:
                return s
        return None

    def find_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resource_id = require_nonempty(resource_id, "resource_id")
        for r in self.resources:
            if r.get("resource_id") == resource_id:
                return r
        return None

    def find_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        transaction_id = require_nonempty(transaction_id, "transaction_id")
        for t in self.transactions:
            if t.get("transaction_id") == transaction_id:
                return t
        return None

    def active_transactions_for_resource(self, resource_id: str) -> List[Dict[str, Any]]:
        active = []
        for t in self.transactions:
            if t.get("resource_id") == resource_id and t.get("status") == "borrowed":
                active.append(t)
        return active

    def active_transactions_for_student_resource(self, student_id: str, resource_id: str) -> List[Dict[str, Any]]:
        active = []
        for t in self.transactions:
            if (
                t.get("student_id") == student_id
                and t.get("resource_id") == resource_id
                and t.get("status") == "borrowed"
            ):
                active.append(t)
        return active

    # ----------------------------
    # ID generation
    # ----------------------------
    def next_transaction_id(self) -> str:
        nums = []
        for t in self.transactions:
            tid = str(t.get("transaction_id", ""))
            if tid.startswith("T") and tid[1:].isdigit():
                nums.append(int(tid[1:]))

        if nums:
            new_num = max(nums) + 1
        else:
            new_num = 1

        return "T" + str(new_num).zfill(3)

    # ----------------------------
    # Students
    # ----------------------------
    def add_student(self, student_id: str, name: str, email: str) -> None:
        student_id = require_nonempty(student_id, "student_id")
        name = require_nonempty(name, "name")
        email = require_nonempty(email, "email")

        if self.find_student(student_id) is not None:
            raise ConflictError(f"Student ID '{student_id}' already exists.")

        self.students.append({"student_id": student_id, "name": name, "email": email})
        self.file_manager.save_students(self.students)

    # ----------------------------
    # Resources (Staff)
    # ----------------------------
    def add_resource(self, resource_id: str, name: str, rtype: str, quantity: Any) -> None:
        resource_id = require_nonempty(resource_id, "resource_id")
        name = require_nonempty(name, "name")
        rtype = require_nonempty(rtype, "type")
        qty = require_int_ge_0(quantity, "quantity")

        if self.find_resource(resource_id) is not None:
            raise ConflictError(f"Resource ID '{resource_id}' already exists.")

        self.resources.append({"resource_id": resource_id, "name": name, "type": rtype, "quantity": qty})
        self.file_manager.save_resources(self.resources)

    def update_resource_quantity(self, resource_id: str, new_quantity: Any) -> None:
        r = self.find_resource(resource_id)
        if r is None:
            raise NotFoundError(f"Resource '{resource_id}' not found.")

        qty = require_int_ge_0(new_quantity, "new_quantity")
        r["quantity"] = qty
        self.file_manager.save_resources(self.resources)

    def remove_resource(self, resource_id: str) -> None:
        r = self.find_resource(resource_id)
        if r is None:
            raise NotFoundError(f"Resource '{resource_id}' not found.")

        active = self.active_transactions_for_resource(resource_id)
        if active:
            raise ConflictError("Cannot remove resource: it is currently borrowed.")

        new_list = []
        for x in self.resources:
            if x.get("resource_id") != resource_id:
                new_list.append(x)

        self.resources = new_list
        self.file_manager.save_resources(self.resources)

    def list_resources(self) -> List[Dict[str, Any]]:
        result = []
        for r in self.resources:
            result.append(dict(r))  # copy
        return result

    def list_available_resources(self) -> List[Dict[str, Any]]:
        result = []
        for r in self.resources:
            if int(r.get("quantity", 0)) > 0:
                result.append(dict(r))  # copy
        return result

    # ----------------------------
    # Borrowing / Returning (Student)
    # ----------------------------
    def borrow_resource(self, student_id: str, resource_id: str, borrow_date: Optional[str] = None) -> Dict[str, Any]:
        student_id = require_nonempty(student_id, "student_id")
        resource_id = require_nonempty(resource_id, "resource_id")

        s = self.find_student(student_id)
        if s is None:
            raise NotFoundError(f"Student '{student_id}' not found.")

        r = self.find_resource(resource_id)
        if r is None:
            raise NotFoundError(f"Resource '{resource_id}' not found.")

        qty = int(r.get("quantity", 0))
        if qty <= 0:
            raise ConflictError("Resource is not available (quantity is 0).")

        # prevent borrowing same resource twice without returning
        active_same = self.active_transactions_for_student_resource(student_id, resource_id)
        if active_same:
            raise ConflictError("Student already has this resource borrowed and not returned.")

        if borrow_date is None:
            bdate = today_iso()
        else:
            bdate = borrow_date.strip()

        parse_iso(bdate)  # validate format
        ddate = iso_plus_days(bdate, self.due_days)

        tid = self.next_transaction_id()

        tx = {
            "transaction_id": tid,
            "student_id": student_id,
            "resource_id": resource_id,
            "borrow_date": bdate,
            "due_date": ddate,
            "return_date": None,
            "status": "borrowed",
        }

        # update quantity and save
        r["quantity"] = qty - 1
        self.transactions.append(tx)

        self.file_manager.save_resources(self.resources)
        self.file_manager.save_transactions(self.transactions)

        return dict(tx)

    def return_resource(self, transaction_id: str, return_date: Optional[str] = None) -> Dict[str, Any]:
        transaction_id = require_nonempty(transaction_id, "transaction_id")

        tx = self.find_transaction(transaction_id)
        if tx is None:
            raise NotFoundError(f"Transaction '{transaction_id}' not found.")

        if tx.get("status") != "borrowed":
            raise ConflictError("This transaction is already returned (or not active).")

        rid = tx.get("resource_id", "")
        r = self.find_resource(rid)
        if r is None:
            raise NotFoundError("Resource for this transaction no longer exists.")

        if return_date is None:
            rdate = today_iso()
        else:
            rdate = return_date.strip()

        parse_iso(rdate)  # validate

        tx["return_date"] = rdate
        tx["status"] = "returned"

        r["quantity"] = int(r.get("quantity", 0)) + 1

        self.file_manager.save_resources(self.resources)
        self.file_manager.save_transactions(self.transactions)

        return dict(tx)

    def return_resource_by_student_resource(self, student_id: str, resource_id: str, return_date: Optional[str] = None) -> Dict[str, Any]:
        student_id = require_nonempty(student_id, "student_id")
        resource_id = require_nonempty(resource_id, "resource_id")

        active = self.active_transactions_for_student_resource(student_id, resource_id)
        if not active:
            raise NotFoundError("No active borrowed transaction found for this student and resource.")

        if len(active) > 1:
            raise ConflictError("Multiple active transactions found; return using transaction_id instead.")

        return self.return_resource(active[0]["transaction_id"], return_date=return_date)

    # ----------------------------
    # Transactions / Reports (Staff)
    # ----------------------------
    def list_transactions(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if student_id is None:
            return [dict(t) for t in self.transactions]

        student_id = require_nonempty(student_id, "student_id")
        result = []
        for t in self.transactions:
            if t.get("student_id") == student_id:
                result.append(dict(t))
        return result

    def is_overdue(self, tx: Dict[str, Any], current_date: str) -> bool:
        if tx.get("status") != "borrowed":
            return False

        due = parse_iso(tx.get("due_date", ""))
        cur = parse_iso(current_date)
        return cur > due

    def list_overdue(self, current_date: Optional[str] = None) -> List[Dict[str, Any]]:
        if current_date is None:
            cdate = today_iso()
        else:
            cdate = current_date.strip()

        parse_iso(cdate)  # validate

        result = []
        for t in self.transactions:
            if self.is_overdue(t, cdate):
                result.append(dict(t))
        return result
