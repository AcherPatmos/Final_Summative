# Student menu for the Campus Resource Borrow & Return Management System.
# Students can:
# - View available resources
# - Borrow resources
# - Return resources
# - View their borrowing history

from datetime import date
from system_manager import SystemManagerError, NotFoundError, ValidationError, ConflictError


def student_menu(system_manager):
    # First, we need to get or create the student account
    student_id = _get_or_create_student(system_manager)

    if student_id is None:
        # User cancelled or error occurred
        print("\nReturning to main menu...")
        return
    while True:
        print(f"\n{'=' * 60}")  # for  visual separation in the console
        print(f"STUDENT MENU - Logged in as: {student_id}")
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

        elif choice == "2":
            _borrow_resource(system_manager, student_id)

        elif choice == "3":
            _return_resource(system_manager, student_id)

        elif choice == "4":
            _view_my_history(system_manager, student_id)

        elif choice == "0":
            print("\nLogging out...")
            break

        else:
            print("\n Invalid choice. Please try again.")


def _get_or_create_student(system_manager):
    # Get existing student or create new student account.
    #
    # This function handles the missing user registration feature.
    # When a student logs in with their email, we:
    # 1. Check if they already exist in the system
    # 2. If not, create a new account for them
    # 3. Return their student_id for use in the menu
    #
    # Returns:
    #     str: student_id if successful, None if cancelled

    print("\n" + "=" * 60)
    print("STUDENT LOGIN / REGISTRATION")
    print("=" * 60)

    # Get student email (already validated by main.py for role)
    email = input("Enter your student email: ").strip().lower()

    if not email:
        print("Email cannot be empty.")
        return None

    # Check if student already exists by searching for email
    existing_student = None
    for student in system_manager.students:
        if student.get("email", "").lower() == email:
            existing_student = student
            break

    if existing_student:
        # Student exists - welcome back!
        print(f"\n Welcome back, {existing_student['name']}!")
        return existing_student['student_id']

    # Student doesn't exist - create new account
    print("\n First time login detected. Let's create your account.")
    name = input("Enter your full name: ").strip()

    if not name:
        print(" Name cannot be empty.")
        return None

    # Generate new student ID
    student_id = _generate_student_id(system_manager)

    # Create the student account
    try:
        system_manager.add_student(student_id, name, email)
        print(f"\n Account created successfully!")
        print(f"Your Student ID is: {student_id}")
        return student_id
    except SystemManagerError as e:
        print(f"\n Error creating account: {e}")
        return None


def _generate_student_id(system_manager):
    # Generate a new unique student ID in format S001, S002, etc.
    #
    # This follows the same pattern as system_manager.next_transaction_id()
    #
    # Returns:
    #     str: New student ID like "S001"

    nums = []
    for student in system_manager.students:
        sid = str(student.get("student_id", ""))
        if sid.startswith("S") and sid[1:].isdigit():
            nums.append(int(sid[1:]))

    if nums:
        new_num = max(nums) + 1
    else:
        new_num = 1

    return "S" + str(new_num).zfill(3)


def _view_available_resources(system_manager):
    # Display all resources that are currently available (quantity > 0).
    #
    # Uses system_manager.list_available_resources()

    print("\n" + "=" * 60)
    print("AVAILABLE RESOURCES")
    print("=" * 60)

    try:
        available = system_manager.list_available_resources()

        if not available:
            print("\n No resources available for borrowing at the moment.")
            print("Please check back later.")
            return
            # Display in a nice formatted table
        print(f"\n{'ID':<12} {'Name':<30} {'Category':<20} {'Qty':<5}")
        print("-" * 70)

        for resource in available:
            resource_id = resource.get('resource_id', 'N/A')
            name = resource.get('name', 'N/A')
            rtype = resource.get('type', 'N/A')
            quantity = resource.get('quantity', 0)

            print(f"{resource_id:<12} {name:<30} {rtype:<20} {quantity:<5}")

            print("-" * 70)
            print(f"Total available resources: {len(available)}")

    except SystemManagerError as e:
        print(f"\n Error loading resources: {e}")


def _borrow_resource(system_manager, student_id):
    # Handle the borrowing process for a student.
    #
    # Uses system_manager.borrow_resource() which handles:
    # - Checking resource availability
    # - Reducing quantity
    # - Creating transaction
    # - Setting due date (3 days from now)

    print("\n" + "=" * 60)
    print("BORROW A RESOURCE")
    print("=" * 60)

    # First show what's available
    print("\nTip: View available resources (option 1) to see what you can borrow.")

    resource_id = input("\nEnter Resource ID to borrow (or 0 to cancel): ").strip()

    if resource_id == "0":
        print("Borrowing cancelled. Returning to main menu")
        return

    if not resource_id:
        print(" Resource ID cannot be empty.")
        return

    # Try to borrow the resource
    try:
        # Call borrow_resource method
        transaction = system_manager.borrow_resource(student_id, resource_id)

        # Success! Show the details
        print("\n Resource borrowed successfully!")
        print("-" * 60)
        print(f"Transaction ID: {transaction['transaction_id']}")
        print(f"Resource ID:    {transaction['resource_id']}")
        print(f"Borrow Date:    {transaction['borrow_date']}")
        print(f"Due Date:       {transaction['due_date']}")
        print("-" * 60)
        print(f"⚠  Please return by {transaction['due_date']} to avoid overdue status.")

    except NotFoundError as e:
        print(f"\n Not Found: {e}")
        print("Make sure you entered the correct Resource ID.")

    except ConflictError as e:
        print(f"\n Cannot Borrow: {e}")
        print("This might mean:")
        print("  - Resource is not available (quantity is 0)")
        print("  - You already have this resource borrowed")

    except ValidationError as e:
        print(f"\n Invalid Input: {e}")

    except SystemManagerError as e:
        print(f"\n Error: {e}")


def _return_resource(system_manager, student_id):
    # Handle the return process for a student.
    #
    # Students can return by entering either:
    # - Transaction ID (if they know it)
    # - Resource ID (system finds their active transaction)
    #
    # Uses system_manager.return_resource() or
    # system_manager.return_resource_by_student_resource()

    print("\n" + "=" * 60)
    print("RETURN A RESOURCE")
    print("=" * 60)

    # First, show what this student currently has borrowed
    print("\nYour currently borrowed items:")
    print("-" * 60)

    active_borrowings = []
    for tx in system_manager.transactions:
        if (tx.get('student_id') == student_id and
                tx.get('status') == 'borrowed'):
            active_borrowings.append(tx)

    if not active_borrowings:
        print(" You don't have any borrowed resources to return.")
        return

    # Display active borrowings
    print(f"\n{'Transaction ID':<15} {'Resource ID':<15} {'Borrow Date':<15} {'Due Date':<15}")
    print("-" * 60)

    for tx in active_borrowings:
        print(f"{tx['transaction_id']:<15} {tx['resource_id']:<15} "
              f"{tx['borrow_date']:<15} {tx['due_date']:<15}")

    print("-" * 60)

    # Get return method choice
    print("\nHow would you like to return?")
    print("1) By Resource ID (easier)")
    print("2) By Transaction ID (more precise)")
    print("0) Cancel")

    method = input("\nChoose method: ").strip()

    if method == "0":
        print("Return cancelled.")
        return

    elif method == "1":
        # Return by Resource ID
        resource_id = input("\nEnter Resource ID to return: ").strip()

        if not resource_id:
            print(" Resource ID cannot be empty.")
            return

        try:
            # Use the by_student_resource method your teammate built
            transaction = system_manager.return_resource_by_student_resource(
                student_id, resource_id
            )

            print("\n✅ Resource returned successfully!")
            print("-" * 60)
            print(f"Transaction ID: {transaction['transaction_id']}")
            print(f"Resource ID:    {transaction['resource_id']}")
            print(f"Return Date:    {transaction['return_date']}")
            print(f"Status:         {transaction['status']}")
            print("-" * 60)
            print("Thank you for returning on time!")

        except NotFoundError as e:
            print(f"\n Not Found: {e}")
            print("Make sure you borrowed this resource and haven't returned it yet.")

        except ConflictError as e:
            print(f"\n Error: {e}")

        except SystemManagerError as e:
            print(f"\n Error: {e}")

    elif method == "2":
        # Return by Transaction ID
        transaction_id = input("\nEnter Transaction ID to return: ").strip()

        if not transaction_id:
            print(" Transaction ID cannot be empty.")
            return

        try:
            transaction = system_manager.return_resource(transaction_id)

            print("\n Resource returned successfully!")
            print("-" * 60)
            print(f"Transaction ID: {transaction['transaction_id']}")
            print(f"Resource ID:    {transaction['resource_id']}")
            print(f"Return Date:    {transaction['return_date']}")
            print(f"Status:         {transaction['status']}")
            print("-" * 60)
            print("Thank you for returning on time!")

        except NotFoundError as e:
            print(f"\n Not Found: {e}")

        except ConflictError as e:
            print(f"\n Error: {e}")

        except SystemManagerError as e:
            print(f"\n Error: {e}")

    else:
        print(" Invalid choice.")


def _view_my_history(system_manager, student_id):

    # Display complete borrowing history for the current student.
    #
    # Shows both active borrowings and past returns.
    # Uses system_manager.list_transactions(student_id)
    #
    # Args:
    #     system_manager: SystemManager instance
    #     student_id: Current student's ID

    print("\n" + "=" * 60)
    print("MY BORROWING HISTORY")
    print("=" * 60)

    try:
        # Get all transactions for this student
        transactions = system_manager.list_transactions(student_id=student_id)

        if not transactions:
            print("\n No borrowing history found.")
            print("You haven't borrowed any resources yet.")
            return

        # Separate active and completed
        active = [tx for tx in transactions if tx.get('status') == 'borrowed']
        completed = [tx for tx in transactions if tx.get('status') in ['returned', 'overdue']]

        # Show active borrowings
        if active:
            print(f"\n CURRENTLY BORROWED ({len(active)}):")
            print("-" * 80)
            print(f"{'Trans ID':<12} {'Resource ID':<15} {'Borrowed':<12} {'Due Date':<12} {'Status':<10}")
            print("-" * 80)

            for tx in active:
                # Check if overdue
                today = date.today().isoformat()
                is_overdue = system_manager.is_overdue(tx, today)
                status_display = " OVERDUE" if is_overdue else "Borrowed"

                print(f"{tx['transaction_id']:<12} {tx['resource_id']:<15} "
                      f"{tx['borrow_date']:<12} {tx['due_date']:<12} {status_display:<10}")

            print("-" * 80)

        # Show completed transactions
        if completed:
            print(f"\n PAST TRANSACTIONS ({len(completed)}):")
            print("-" * 90)
            print(f"{'Trans ID':<12} {'Resource ID':<15} {'Borrowed':<12} {'Returned':<12} {'Status':<10}")
            print("-" * 90)

            for tx in completed:
                return_date = tx.get('return_date', 'N/A')
                status = tx.get('status', 'N/A')

                print(f"{tx['transaction_id']:<12} {tx['resource_id']:<15} "
                      f"{tx['borrow_date']:<12} {return_date:<12} {status:<10}")

            print("-" * 90)

        # Summary
        print(f"\nTotal transactions: {len(transactions)}")
        print(f"Active borrowings:  {len(active)}")
        print(f"Completed returns:  {len(completed)}")

    except SystemManagerError as e:
        print(f"\n Error loading history: {e}")