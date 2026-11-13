
import json
import os
import calendar
from datetime import datetime, date


class WarrantySystem:
    def __init__(self):
        self.filename = "warranty_data.json"
        self.products = self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as file:
                    data = json.load(file)
                if isinstance(data, dict):
                    return data
            except (json.JSONDecodeError, OSError):
                print("Unable to read saved data.")
        return {}

    def save_data(self):
        with open(self.filename, "w") as file:
            json.dump(self.products, file, indent=4)

    def calculate_expiry(self, purchase, months):
        d = datetime.strptime(purchase, "%Y-%m-%d").date()
        month = d.month - 1 + months
        year = d.year + month // 12
        month = month % 12 + 1
        day = min(d.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def add_product(self):
        try:
            name = input("Product Name: ").strip()
            brand = input("Brand: ").strip()
            purchase = input("Purchase Date (YYYY-MM-DD): ")
            months = int(input("Warranty Months: "))

            if not name or not brand or months <= 0:
                print("Invalid product details.")
                return

            purchase_date = datetime.strptime(
                purchase, "%Y-%m-%d"
            ).date()

            if purchase_date > date.today():
                print("Purchase date cannot be in the future.")
                return

            expiry = self.calculate_expiry(purchase, months)
            pid = str(max(
                [int(x) for x in self.products.keys()] + [100]
            ) + 1)

            self.products[pid] = {
                "name": name,
                "brand": brand,
                "purchase": purchase,
                "months": months,
                "expiry": str(expiry),
                "services": []
            }

            self.save_data()
            print("Product Added Successfully!")
            print("Product ID:", pid)
            print("Warranty Expiry:", expiry)

        except (ValueError, OverflowError):
            print("Invalid date or warranty period.")

    def display_product(self, pid, p):
        days = (
            date.fromisoformat(p["expiry"]) - date.today()
        ).days

        if days < 0:
            status = "Expired"
        elif days <= 30:
            status = "Expiring Soon"
        else:
            status = "Active"

        print("\n---------------------------")
        print("Product ID:", pid)
        print("Product:", p["name"])
        print("Brand:", p["brand"])
        print("Purchase Date:", p["purchase"])
        print("Warranty Expiry:", p["expiry"])
        print("Warranty Status:", status)
        print("Days Remaining:", max(0, days))
        print("---------------------------")

    def view_products(self):
        if not self.products:
            print("No Products Available.")
            return

        for pid, p in self.products.items():
            self.display_product(pid, p)

    def search_product(self):
        keyword = input("Enter Product Name or ID: ").lower()
        found = False

        for pid, p in self.products.items():
            if keyword in p["name"].lower() or keyword == pid:
                self.display_product(pid, p)
                found = True

        if not found:
            print("Product Not Found.")

    def update_product(self):
        pid = input("Enter Product ID: ")

        if pid not in self.products:
            print("Product Not Found.")
            return

        p = self.products[pid]

        print("1. Update Product Name")
        print("2. Update Brand")
        print("3. Update Warranty Months")

        choice = input("Enter Choice: ")

        if choice == "1":
            name = input("New Product Name: ").strip()
            if not name:
                print("Name cannot be empty.")
                return
            p["name"] = name

        elif choice == "2":
            brand = input("New Brand: ").strip()
            if not brand:
                print("Brand cannot be empty.")
                return
            p["brand"] = brand

        elif choice == "3":
            try:
                months = int(input("New Warranty Months: "))
                if months <= 0:
                    print("Invalid warranty period.")
                    return

                expiry = self.calculate_expiry(
                    p["purchase"], months
                )
                p["months"] = months
                p["expiry"] = str(expiry)

            except (ValueError, OverflowError):
                print("Invalid warranty period.")
                return

        else:
            print("Invalid Choice.")
            return

        self.save_data()
        print("Product Updated Successfully!")

    def delete_product(self):
        pid = input("Enter Product ID: ")

        if pid in self.products:
            confirm = input("Confirm Delete (yes/no): ")
            if confirm.lower() == "yes":
                del self.products[pid]
                self.save_data()
                print("Product Deleted Successfully!")
            else:
                print("Deletion Cancelled.")
        else:
            print("Product Not Found.")

    def check_warranty(self):
        pid = input("Enter Product ID: ")

        if pid in self.products:
            self.display_product(pid, self.products[pid])
        else:
            print("Product Not Found.")

    def expiry_reminder(self):
        print("\n--- Warranty Expiry Reminders ---")
        found = False

        for pid, p in self.products.items():
            days = (
                date.fromisoformat(p["expiry"]) - date.today()
            ).days

            if 0 <= days <= 30:
                print(
                    pid, "-", p["name"],
                    "- Expires in", days, "days"
                )
                found = True

        if not found:
            print("No warranties expiring within 30 days.")

    def add_service(self):
        pid = input("Enter Product ID: ")

        if pid not in self.products:
            print("Product Not Found.")
            return

        service = input("Service Description: ").strip()

        if not service:
            print("Description cannot be empty.")
            return

        try:
            cost = float(input("Service Cost: "))

            if cost < 0:
                print("Invalid service cost.")
                return

        except ValueError:
            print("Invalid service cost.")
            return

        record = {
            "date": str(date.today()),
            "description": service,
            "cost": cost
        }

        self.products[pid]["services"].append(record)
        self.save_data()
        print("Service Record Added Successfully!")

    def view_services(self):
        pid = input("Enter Product ID: ")

        if pid not in self.products:
            print("Product Not Found.")
            return

        services = self.products[pid]["services"]

        if not services:
            print("No Service History Available.")
            return

        print("\n--- Service History ---")

        for s in services:
            print("Date:", s["date"])
            print("Service:", s["description"])
            print("Cost: Rs.", s["cost"])
            print("--------------------")

    def dashboard(self):
        total = len(self.products)
        active = 0
        expiring = 0
        expired = 0
        service_cost = 0

        for p in self.products.values():
            days = (
                date.fromisoformat(p["expiry"]) - date.today()
            ).days

            if days < 0:
                expired += 1
            elif days <= 30:
                expiring += 1
            else:
                active += 1

            for s in p["services"]:
                service_cost += s["cost"]

        print("\n===== WARRANTY DASHBOARD =====")
        print("Total Products:", total)
        print("Active Warranties:", active)
        print("Expiring Soon:", expiring)
        print("Expired Warranties:", expired)
        print("Total Service Cost: Rs.", service_cost)


system = WarrantySystem()

while True:
    print("\n===== SMART WARRANTY SYSTEM =====")
    print("1. Add Product")
    print("2. View Products")
    print("3. Search Product")
    print("4. Update Product")
    print("5. Delete Product")
    print("6. Check Warranty")
    print("7. Expiry Reminder")
    print("8. Add Service Record")
    print("9. View Service History")
    print("10. Dashboard")
    print("11. Exit")

    choice = input("Enter Your Choice: ")

    if choice == "1":
        system.add_product()

    elif choice == "2":
        system.view_products()

    elif choice == "3":
        system.search_product()

    elif choice == "4":
        system.update_product()

    elif choice == "5":
        system.delete_product()

    elif choice == "6":
        system.check_warranty()

    elif choice == "7":
        system.expiry_reminder()

    elif choice == "8":
        system.add_service()

    elif choice == "9":
        system.view_services()

    elif choice == "10":
        system.dashboard()

    elif choice == "11":
        print("Thank You for Using Smart Warranty System!")
        break

    else:
        print("Invalid Choice.")
