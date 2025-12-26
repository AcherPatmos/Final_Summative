from datetime import date

def staff_menu(system_manager):
    while True:
        print("\nSTAFF MENU")
        print("1) Add resource")
        print("2) Update resource quantity")
        print("3) Remove resource")
        print("4) View all resources")
        print("5) View all transactions")
        print("6) View overdue transactions")
        print("0) Exit")

        choice = input("Choose option: ").strip()

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

        elif choice == "2":
            resource_id = input("Resource ID: ").strip()
            qty_str = input("New Quantity: ").strip()
            try:
                new_quantity = int(qty_str)
                system_manager.update_resource_quantity(resource_id, new_quantity)
                print("Quantity updated successfully.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            resource_id = input("Resource ID to remove: ").strip()
            try:
                system_manager.remove_resource(resource_id)
                print("Resource removed successfully.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "4":
            resources = system_manager.list_resources()
            if not resources:
                print("No resources found.")
            else:
                for r in resources:
                    # r can be a dict or Resource depending on SystemManager design
                    print(r)

        elif choice == "5":
            txs = system_manager.list_transactions()
            if not txs:
                print("No transactions found.")
            else:
                for t in txs:
                    print(t)

        elif choice == "6":
            today = date.today().isoformat()
            overdue = system_manager.list_overdue(today)
            if not overdue:
                print("No overdue resources.")
            else:
                for t in overdue:
                    print(t)

        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")
