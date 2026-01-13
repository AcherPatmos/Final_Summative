# student_menu.py
# Student menu for the Campus Resource Borrow & Return Management System.
# Students can:
# - View available resources
# - Borrow resources
# - Return resources
# - View their borrowing history

from datetime import date
from tabulate import tabulate
from system_manager import SystemManagerError, NotFoundError, ValidationError, ConflictError


def student_menu(system_manager, email_from_main: str):
    student_id = _get_or_create_student(system_manager, email_from_main)

    if student_id is None:
        print("\nReturning to main menu...")
        return

    student = system_manager.find_student(student_id)
    student_name = student["name"] if student else student_id  # fallback

    while True:
        print(f"\n{'=' * 60}")
        print(f"STUDENT MENU - Logged in as: {student_name}")
        print(f"{'=' * 60}")
        print("1) View available resources")
        print("2) Borrow a resource")
        print("3) Return a resource")
        print("4) View my borrowing history")
        print("0) Logout and return to main menu")
        print(f"{'=' * 60}")

        choice = input("\nChoose option: ").strip()

        if choice == "1":
            _view_available_resources(system_manager)
            if not _back_or_exit():
                break

        elif choice == "2":
            _borrow_resource(system_manager, student_id)
            if not _back_or_exit():
                break

        elif choice == "3":
            _return_resource(system_manager, student_id)
            if not _back_or_exit():
                break

        elif choice == "4":
            _view_my_history(system_manager, student_id)
            if not _back_or_exit():
                break

        elif choice == "0":
            print("\nLogging out...")
            break

        else:
            print("\nInvalid choice. Please try again.")


def _back_or_exit() -> bool:
    """
    Ask user whether to return to the student menu or exit.
    Returns True to continue menu, False to exit to main menu.
    """
    while True:
        print("\nWhat would you like to do next?")
        print("1) Go back to Student Menu")
        print("0) Exit to Main Menu")

        choice = input("\nChoose option: ").strip()

        if choice == "1":
            return True
        elif choice == "0":
            return False
        else:
            print("Invalid choice. Please try again.")


def _get_or_create_student(system_manager, email_from_main: str):
    """
    Uses the email already entered in main.py.
    1) Check if student exists in students.json (loaded into system_manager.students)
    2) If exists -> login and return student_id
    3) If not -> register (ask name), create ID, save, then login
    """
    print("\n" + "=" * 60)
    print("STUDENT LOGIN / REGISTRATION")
    print("=" * 60)

    email = email_from_main.strip().lower()

    # Check if student already exists by email
    existing_student = None
    for student in system_manager.students:
        if student.get("email", "").lower() == email:
            existing_student = student
            break

    if existing_student:
        print(f"\nWelcome back, {existing_student['name']}!")
        return existing_student["student_id"]

    # Student not found -> registration starts
    print("\nFirst time login detected. Let's create your account.")
    name = input("Enter your full name: ").strip()

    if not name:
        print("Name cannot be empty.")
        return None

    student_id = _generate_student_id(system_manager)

    try:
        system_manager.add_student(student_id, name, email)
        print(f"\nAccount created successfully!")
        print(f"Your Student ID is: {student_id}")
        return student_id
    except SystemManagerError as e:
        print(f"\nError creating account: {e}")
        return None


def _generate_student_id(system_manager):
    nums = []
    for student in system_manager.students:
        sid = str(student.get("student_id", ""))
        if sid.startswith("S") and sid[1:].isdigit():
            nums.append(int(sid[1:]))

    new_num = (max(nums) + 1) if nums else 1
    return "S" + str(new_num).zfill(3)


def _view_available_resources(system_manager):
    print("\n" + "=" * 60)
    print("AVAILABLE RESOURCES")
    print("=" * 60)

    try:
        available = system_manager.list_available_resources()

        if not available:
            print("\nNo resources available for borrowing at the moment.")
            print("Please check back later.")
            return

        table_data = []
        for resource in available:
            table_data.append([
                resource.get("resource_id", "N/A"),
                resource.get("name", "N/A"),
                resource.get("type", "N/A"),
                resource.get("quantity", 0),
            ])

        headers = ["Resource ID", "Name", "Category", "Quantity"]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    except SystemManagerError as e:
        print(f"\nError loading resources: {e}")


def _borrow_resource(system_manager, student_id):
    print("\n" + "=" * 60)
    print("BORROW A RESOURCE")
    print("=" * 60)

    print("\nTip: View available resources (option 1) to see what you can borrow.")

    resource_id = input("\nEnter Resource ID to borrow (or 0 to cancel): ").strip()

    if resource_id == "0":
        print("Borrowing cancelled.")
        return

    if not resource_id:
        print("Resource ID cannot be empty.")
        return

    try:
        transaction = system_manager.borrow_resource(student_id, resource_id)

        print("\nResource borrowed successfully!")
        print("-" * 60)
        print(f"Transaction ID: {transaction['transaction_id']}")
        print(f"Resource ID:    {transaction['resource_id']}")
        print(f"Borrow Date:    {transaction['borrow_date']}")
        print(f"Due Date:       {transaction['due_date']}")
        print("-" * 60)
        print(f"Please return by {transaction['due_date']} to avoid overdue status.")

    except NotFoundError as e:
        print(f"\nNot Found: {e}")
        print("Make sure you entered the correct Resource ID.")

    except ConflictError as e:
        print(f"\nCannot Borrow: {e}")

    except ValidationError as e:
        print(f"\nInvalid Input: {e}")

    except SystemManagerError as e:
        print(f"\nError: {e}")


def _return_resource(system_manager, student_id):
    print("\n" + "=" * 60)
    print("RETURN A RESOURCE")
    print("=" * 60)

    active_borrowings = []
    for tx in system_manager.transactions:
        if tx.get("student_id") == student_id and tx.get("status") == "borrowed":
            active_borrowings.append(tx)

    if not active_borrowings:
        print("\nYou don't have any borrowed resources to return.")
        return

    table_data = []
    for tx in active_borrowings:
        table_data.append([
            tx.get("transaction_id", "N/A"),
            tx.get("resource_id", "N/A"),
            tx.get("borrow_date", "N/A"),
            tx.get("due_date", "N/A"),
        ])

    headers = ["Transaction ID", "Resource ID", "Borrow Date", "Due Date"]
    print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    print("\nHow would you like to return?")
    print("1) By Resource ID (easier)")
    print("2) By Transaction ID (more precise)")
    print("0) Cancel")

    method = input("\nChoose method: ").strip()

    if method == "0":
        print("Return cancelled.")
        return

    elif method == "1":
        resource_id = input("\nEnter Resource ID to return: ").strip()
        if not resource_id:
            print("Resource ID cannot be empty.")
            return

        try:
            transaction = system_manager.return_resource_by_student_resource(student_id, resource_id)
            print("\nResource returned successfully!")
            print("-" * 60)
            print(f"Transaction ID: {transaction['transaction_id']}")
            print(f"Resource ID:    {transaction['resource_id']}")
            print(f"Return Date:    {transaction['return_date']}")
            print(f"Status:         {transaction['status']}")
            print("-" * 60)

        except SystemManagerError as e:
            print(f"\nError: {e}")

    elif method == "2":
        transaction_id = input("\nEnter Transaction ID to return: ").strip()
        if not transaction_id:
            print("Transaction ID cannot be empty.")
            return

        try:
            transaction = system_manager.return_resource(transaction_id)
            print("\nResource returned successfully!")
            print("-" * 60)
            print(f"Transaction ID: {transaction['transaction_id']}")
            print(f"Resource ID:    {transaction['resource_id']}")
            print(f"Return Date:    {transaction['return_date']}")
            print(f"Status:         {transaction['status']}")
            print("-" * 60)

        except SystemManagerError as e:
            print(f"\nError: {e}")

    else:
        print("Invalid choice.")


def _view_my_history(system_manager, student_id):
    print("\n" + "=" * 60)
    print("MY BORROWING HISTORY")
    print("=" * 60)

    try:
        transactions = system_manager.list_transactions(student_id=student_id)

        if not transactions:
            print("\nNo borrowing history found.")
            return

        active = [tx for tx in transactions if tx.get("status") == "borrowed"]
        completed = [tx for tx in transactions if tx.get("status") in ["returned", "overdue"]]

        if active:
            print(f"\nCURRENTLY BORROWED ({len(active)}):")
            table_data = []
            today = date.today().isoformat()
            for tx in active:
                overdue_flag = system_manager.is_overdue(tx, today)
                status_display = "OVERDUE" if overdue_flag else "Borrowed"
                table_data.append([
                    tx.get("transaction_id", "N/A"),
                    tx.get("resource_id", "N/A"),
                    tx.get("borrow_date", "N/A"),
                    tx.get("due_date", "N/A"),
                    status_display,
                ])
            headers = ["Transaction ID", "Resource ID", "Borrow Date", "Due Date", "Status"]
            print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

        if completed:
            print(f"\nPAST TRANSACTIONS ({len(completed)}):")
            table_data = []
            for tx in completed:
                table_data.append([
                    tx.get("transaction_id", "N/A"),
                    tx.get("resource_id", "N/A"),
                    tx.get("borrow_date", "N/A"),
                    tx.get("return_date", "N/A"),
                    tx.get("status", "N/A"),
                ])
            headers = ["Transaction ID", "Resource ID", "Borrow Date", "Return Date", "Status"]
            print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

        print(f"\nTotal transactions: {len(transactions)}")
        print(f"Active borrowings:  {len(active)}")
        print(f"Completed returns:  {len(completed)}")

    except SystemManagerError as e:
        print(f"\nError loading history: {e}")
