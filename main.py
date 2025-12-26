# main.py
"""
Entry point for the Campus Resource Borrow & Return Management System.

Flow:
1) Initialize FileManager + SystemManager
2) Load existing data from JSON
3) Ask user for email (role is determined automatically)
4) Route user to Staff menu or Student menu
5) Allow user to return to role selection or exit

Note:
- main.py should NOT contain business logic (borrow/return/add/remove).
- It only coordinates menus and the SystemManager.
"""

from __future__ import annotations

from file_manager import FileManager, FileManagerError, FileCorruptionError
from system_manager import SystemManager, SystemManagerError, ValidationError, RoleConfig

# These menu functions will be implemented by Patmos.
# Keep these imports as-is so integration is straightforward.
try:
    from staff_menu import staff_menu
except Exception:
    staff_menu = None  # type: ignore

try:
    from student_menu import student_menu
except Exception:
    student_menu = None  # type: ignore


def _print_header() -> None:
    print("=" * 60)
    print("Campus Resource Borrow & Return Management System")
    print("=" * 60)


def _prompt_email() -> str:
    return input("\nEnter your campus email (or 0 to exit): ").strip()


def _prompt_continue() -> None:
    input("\nPress Enter to continue...")


def main() -> None:
    _print_header()

    # If you want a dedicated folder: data_dir="data"
    try:
        fm = FileManager(
            students_file="students.json",
            resources_file="resources.json",
            transactions_file="transactions.json",
            data_dir=None,
        )
    except (FileManagerError, OSError) as e:
        print(f"\nStartup error (FileManager): {e}")
        return

    # Configure your campus domains here:
    # Example:
    #   student_domains=("student.campus.edu",)
    #   staff_domains=("campus.edu",)
    role_config = RoleConfig(
        student_domains=("student.campus.edu",),
        staff_domains=("campus.edu",),
    )

    sm = SystemManager(file_manager=fm, due_days=3, role_config=role_config)

    try:
        sm.load_all()
    except FileCorruptionError as e:
        print("\nData file error:")
        print(e)
        print("\nFix the corrupted JSON file (or delete it to reset) and run again.")
        return
    except FileManagerError as e:
        print(f"\nCould not load data: {e}")
        return

    # Main loop: ask for email -> route -> return here
    while True:
        email = _prompt_email()

        if email == "0":
            print("\nGoodbye.")
            break

        try:
            role = sm.determine_role(email)
        except ValidationError as e:
            print(f"\nInvalid email: {e}")
            _prompt_continue()
            continue
        except SystemManagerError as e:
            print(f"\nError: {e}")
            _prompt_continue()
            continue

        # Route to the correct menu
        if role == "staff":
            if staff_menu is None:
                print("\nStaff menu is not available yet (staff_menu.py not found).")
                _prompt_continue()
                continue
            print("\nRole detected: STAFF")
            staff_menu(sm)  # type: ignore

        elif role == "student":
            if student_menu is None:
                print("\nStudent menu is not available yet (student_menu.py not found).")
                _prompt_continue()
                continue
            print("\nRole detected: STUDENT")
            student_menu(sm)  # type: ignore

        else:
            # Should never happen because determine_role only returns student/staff
            print("\nRole could not be determined.")
            _prompt_continue()


if __name__ == "__main__":
    main()
