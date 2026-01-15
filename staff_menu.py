# staff_menu.py

from datetime import date
from tabulate import tabulate

from system_manager import SystemManagerError, ValidationError, NotFoundError, ConflictError


# -------------------------------------------------
# Helper function: print transactions in table form (TABULATE)
# -------------------------------------------------
def print_transactions_table(transactions):
    """
    Display transactions in a clean table using tabulate.
    """
    if not transactions:
        print("\nNo transactions found.")
        return

    table_data = []
    for t in transactions:
        table_data.append([
            t.get("transaction_id", "N/A"),
            t.get("student_id", "N/A"),
            t.get("resource_id", "N/A"),
            t.get("borrow_date", "N/A"),
            t.get("due_date", "N/A"),
            t.get("return_date") if t.get("return_date") else "-",
            t.get("status", "N/A"),
        ])

    headers = [
        "Transaction ID",
        "Student ID",
        "Resource ID",
        "Borrow Date",
        "Due Date",
        "Return Date",
        "Status"
    ]

    print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


# -------------------------------------------------
# Helper function: print resources in table form (TABULATE)
# -------------------------------------------------
def print_resources_table(resources):
    """
    Display resources in a clean table using tabulate.
    """
    if not resources:
        print("\nNo resources found.")
        return

    table_data = []
    for r in resources:
        table_data.append([
            r.get("resource_id", "N/A"),
            r.get("name", "N/A"),
            r.get("type", "N/A"),
            r.get("quantity", 0),
        ])

    headers = ["Resource ID", "Name", "Category", "Quantity"]
    print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


# -------------------------------------------------
# Helper function: ask whether to go back or exit
# -------------------------------------------------
def back_to_menu_or_exit():
    """
    After completing an action, ask staff whether to:
    1) go back to the staff menu
    0) exit to the main menu

    Returns:
        True  -> show staff menu again
        False -> exit staff menu and return to main.py
    """
    while True:
        print("\nWhat would you like to do next?")
        print("1) Go back to Staff Menu")
        print("0) Exit to Main Menu")

        choice = input("Choose option: ").strip()

        if choice == "1":
            return True
        elif choice == "0":
            return False
        else:
            print("Invalid choice. Please try again.")


# -------------------------------------------------
# Staff Menu
# -------------------------------------------------
def staff_menu(system_manager):
    while True:
        print("\n==============================")
        print("          STAFF MENU")
        print("==============================")
        print("1) Add resource")
        print("2) Update resource quantity")
        print("3) Remove resource")
        print("4) View all resources")
        print("5) View all transactions")
        print("6) View overdue transactions")
        print("0) Exit")

        choice = input("Choose option: ").strip()

        # ----------------------------
        # Add resource
        # ----------------------------
        if choice == "1":
            # Check ID first before asking for other details
            resource_id = input("Resource ID: ").strip()

            # Validate immediately
            if not resource_id:
                print(" Error: Resource ID cannot be empty.")
                continue

            # Check for duplicates BEFORE asking for other details
            try:
                existing = system_manager.find_resource(resource_id)
                if existing:
                    print(f"\n Error: Resource ID '{resource_id}' already exists!")
                    print(f" Existing resource: {existing['name']} ({existing['type']}, qty: {existing['quantity']})")
                    print("  Please use a different Resource ID.\n")
                    continue  # Go back to menu without asking for other fields
            except Exception as e:
                print(f" Error checking resource: {e}")
                continue

            # Only ask for other details if ID is unique
            print("Resource ID is available.")
            name = input("Name: ").strip()
            rtype = input("Type/Category: ").strip()
            qty_str = input("Quantity: ").strip()

            try:
                quantity = int(qty_str)
                system_manager.add_resource(resource_id, name, rtype, quantity)
                print("\n Resource added successfully!")

            except ValueError:
                print("\nInvalid quantity. Please enter a number.")

            except ConflictError as e:
                print(f"\nCannot add resource: {e}")

            except ValidationError as e:
                print(f"\nInvalid input: {e}")

            except SystemManagerError as e:
                print(f"\nError: {e}")

            if not back_to_menu_or_exit():
                break

        # ----------------------------
        # Update resource quantity
        # ----------------------------
        elif choice == "2":
            resource_id = input("Resource ID: ").strip()
            qty_str = input("New Quantity: ").strip()

            try:
                new_quantity = int(qty_str)
                system_manager.update_resource_quantity(resource_id, new_quantity)
                print("\nQuantity updated successfully.")

            except ValueError:
                print("\nInvalid quantity. Please enter a number.")

            except NotFoundError as e:
                print(f"\nResource not found: {e}")

            except ValidationError as e:
                print(f"\nInvalid input: {e}")

            except SystemManagerError as e:
                print(f"\nError: {e}")

            if not back_to_menu_or_exit():
                break

        # ----------------------------
        # Remove resource
        # ----------------------------
        elif choice == "3":
            resource_id = input("Resource ID to remove: ").strip()

            try:
                system_manager.remove_resource(resource_id)
                print("\nResource removed successfully.")

            except NotFoundError as e:
                print(f"\nResource not found: {e}")

            except ConflictError as e:
                print(f"\nCannot remove resource: {e}")

            except ValidationError as e:
                print(f"\nInvalid input: {e}")

            except SystemManagerError as e:
                print(f"\nError: {e}")

            if not back_to_menu_or_exit():
                break

        # ----------------------------
        # View all resources
        # ----------------------------
        elif choice == "4":
            try:
                resources = system_manager.list_resources()
                print_resources_table(resources)

            except SystemManagerError as e:
                print(f"\nError: {e}")

            if not back_to_menu_or_exit():
                break

        # ----------------------------
        # View all transactions
        # ----------------------------
        elif choice == "5":
            try:
                transactions = system_manager.list_transactions()
                print_transactions_table(transactions)

            except SystemManagerError as e:
                print(f"\nError: {e}")

            if not back_to_menu_or_exit():
                break

        # ----------------------------
        # View overdue transactions
        # ----------------------------
        elif choice == "6":
            try:
                today = date.today().isoformat()
                overdue = system_manager.list_overdue(today)
                print_transactions_table(overdue)

            except SystemManagerError as e:
                print(f"\nError: {e}")

            if not back_to_menu_or_exit():
                break

        # ----------------------------
        # Exit
        # ----------------------------
        elif choice == "0":
            print("\nLogging out...")
            break

        else:
            print("\nInvalid choice. Try again.")
