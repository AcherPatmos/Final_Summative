# staff_menu.py

from datetime import date


# -------------------------------------------------
# Helper function: print transactions in table form
# -------------------------------------------------
def print_transactions_table(transactions):
    if not transactions:
        print("No transactions found.")
        return

    print("\n{:<8} {:<8} {:<10} {:<12} {:<12} {:<12} {:<10}".format(
        "T_ID", "STUD_ID", "RES_ID", "BORROW", "DUE", "RETURN", "STATUS"
    ))
    print("-" * 75)

    for t in transactions:
        print("{:<8} {:<8} {:<10} {:<12} {:<12} {:<12} {:<10}".format(
            t["transaction_id"],
            t["student_id"],
            t["resource_id"],
            t["borrow_date"],
            t["due_date"],
            t["return_date"] if t["return_date"] else "-",
            t["status"]
        ))


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
            resource_id = input("Resource ID: ").strip()
            name = input("Name: ").strip()
            rtype = input("Type/Category: ").strip()
            qty_str = input("Quantity: ").strip()

            try:
                quantity = int(qty_str)
                system_manager.add_resource(resource_id, name, rtype, quantity)
                print("Resource added successfully.")
            except Exception as e:
                print(f"Error: {e}")

        # ----------------------------
        # Update resource quantity
        # ----------------------------
        elif choice == "2":
            resource_id = input("Resource ID: ").strip()
            qty_str = input("New Quantity: ").strip()

            try:
                new_quantity = int(qty_str)
                system_manager.update_resource_quantity(resource_id, new_quantity)
                print("Quantity updated successfully.")
            except Exception as e:
                print(f"Error: {e}")

        # ----------------------------
        # Remove resource
        # ----------------------------
        elif choice == "3":
            resource_id = input("Resource ID to remove: ").strip()

            try:
                system_manager.remove_resource(resource_id)
                print("Resource removed successfully.")
            except Exception as e:
                print(f"Error: {e}")

        # ----------------------------
        # View all resources
        # ----------------------------
        elif choice == "4":
            resources = system_manager.list_resources()
            if not resources:
                print("No resources found.")
            else:
                print("\nResources:")
                for r in resources:
                    print(
                        f"- ID: {r['resource_id']} | "
                        f"Name: {r['name']} | "
                        f"Type: {r['type']} | "
                        f"Quantity: {r['quantity']}"
                    )

        # ----------------------------
        # View all transactions (TABLE)
        # ----------------------------
        elif choice == "5":
            transactions = system_manager.list_transactions()
            print_transactions_table(transactions)

        # ----------------------------
        # View overdue transactions (TABLE)
        # ----------------------------
        elif choice == "6":
            today = date.today().isoformat()
            overdue = system_manager.list_overdue(today)
            print_transactions_table(overdue)

        # ----------------------------
        # Exit
        # ----------------------------
        elif choice == "0":
            print("Logging out...")
            break

        else:
            print("Invalid choice. Try again.")
