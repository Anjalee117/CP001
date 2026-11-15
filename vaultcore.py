import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


accounts = []
transactions = []
folder = Path(__file__).parent
accounts_file = folder / "accounts.csv"
transactions_file = folder / "transactions.csv"


def amount_value(value):
    try:
        return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        raise ValueError("Enter a valid amount.")


def minimum_balance(account_type):
    if account_type == "Savings":
        return Decimal("500.00")
    return Decimal("1000.00")


def save_data():
    with accounts_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["number", "name", "type", "balance", "active"])
        for account in accounts:
            writer.writerow([
                account["number"],
                account["name"],
                account["type"],
                account["balance"],
                account["active"],
            ])

    with transactions_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["account", "type", "amount", "balance", "date"])
        for item in transactions:
            writer.writerow([
                item["account"],
                item["type"],
                item["amount"],
                item["balance"],
                item["date"],
            ])


def load_data():
    accounts.clear()
    transactions.clear()

    if accounts_file.exists():
        with accounts_file.open("r", newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                accounts.append({
                    "number": row["number"],
                    "name": row["name"],
                    "type": row["type"],
                    "balance": Decimal(row["balance"]),
                    "active": row["active"].lower() == "true",
                })

    if transactions_file.exists():
        with transactions_file.open("r", newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                transactions.append({
                    "account": row["account"],
                    "type": row["type"],
                    "amount": Decimal(row["amount"]),
                    "balance": Decimal(row["balance"]),
                    "date": row["date"],
                })


def add_transaction(account, transaction_type, amount):
    transactions.append({
        "account": account["number"],
        "type": transaction_type,
        "amount": amount,
        "balance": account["balance"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


def next_account_number():
    highest = 1000
    for account in accounts:
        try:
            value = int(account["number"][2:])
            if value > highest:
                highest = value
        except ValueError:
            pass
    return "VA" + str(highest + 1)


def find_account(account_number):
    number = account_number.strip().upper()
    for account in accounts:
        if account["number"] == number:
            return account
    return None


def active_account(account_number):
    account = find_account(account_number)
    if account is None:
        raise ValueError("Account not found.")
    if not account["active"]:
        raise ValueError("This account is closed.")
    return account


def open_account(name, account_type, opening_deposit):
    clean_name = name.strip()
    clean_type = account_type.strip().title()

    if len(clean_name) < 2 or not all(
        part.replace("-", "").isalpha() for part in clean_name.split()
    ):
        raise ValueError("Enter a valid name.")
    if clean_type not in ("Savings", "Current"):
        raise ValueError("Account type must be Savings or Current.")

    deposit = amount_value(opening_deposit)
    required = minimum_balance(clean_type)
    if deposit < required:
        raise ValueError(
            clean_type + " account needs at least Rs. " + format(required, ".2f")
        )

    account = {
        "number": next_account_number(),
        "name": clean_name.title(),
        "type": clean_type,
        "balance": deposit,
        "active": True,
    }
    accounts.append(account)
    add_transaction(account, "OPEN", deposit)
    save_data()
    return account


def deposit_money(account_number, amount):
    account = active_account(account_number)
    value = amount_value(amount)
    if value <= 0:
        raise ValueError("Deposit amount must be greater than zero.")
    account["balance"] += value
    add_transaction(account, "DEPOSIT", value)
    save_data()
    return account


def withdraw_money(account_number, amount):
    account = active_account(account_number)
    value = amount_value(amount)
    if value <= 0:
        raise ValueError("Withdrawal amount must be greater than zero.")
    new_balance = account["balance"] - value
    required = minimum_balance(account["type"])
    if new_balance < required:
        raise ValueError(
            "Withdrawal rejected. Minimum balance is Rs. "
            + format(required, ".2f")
        )
    account["balance"] = new_balance
    add_transaction(account, "WITHDRAWAL", value)
    save_data()
    return account


def mini_statement(account_number):
    account = active_account(account_number)
    items = []
    for item in transactions:
        if item["account"] == account["number"]:
            items.append(item)
    return items[-5:]


def search_account(search_text):
    word = search_text.strip().lower()
    if word == "":
        raise ValueError("Enter an account number or name.")
    results = []
    for account in accounts:
        if account["active"] and (
            word in account["number"].lower()
            or word in account["name"].lower()
        ):
            results.append(account)
    return results


def close_account(account_number, final_withdrawal=False):
    account = active_account(account_number)
    if account["balance"] != Decimal("0.00"):
        if not final_withdrawal:
            raise ValueError(
                "Account balance is Rs. "
                + format(account["balance"], ".2f")
                + ". Complete final settlement before closing."
            )
        balance = account["balance"]
        account["balance"] = Decimal("0.00")
        add_transaction(account, "FINAL WITHDRAWAL", balance)
    if account["balance"] == Decimal("0.00"):
        account["active"] = False
        add_transaction(account, "CLOSE", Decimal("0.00"))
        save_data()
    return account


def apply_interest_to_savings(annual_rate):
    rate = amount_value(annual_rate)
    if rate <= 0 or rate > 100:
        raise ValueError("Rate must be above 0 and at most 100.")

    count = 0
    for account in accounts:
        if account["active"] and account["type"] == "Savings":
            interest = (account["balance"] * rate / Decimal("1200")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            account["balance"] += interest
            add_transaction(account, "INTEREST", interest)
            count += 1

    if count == 0:
        raise ValueError("No active Savings accounts found.")
    save_data()
    return count


def show_money(value):
    return "Rs. " + format(value, ",.2f")


def show_account(account):
    print(
        account["number"],
        "|",
        account["name"],
        "|",
        account["type"],
        "|",
        show_money(account["balance"]),
    )


def main():
    load_data()

    while True:
        print("\n========== VAULTCORE ==========")
        print("1. Open account")
        print("2. Deposit money")
        print("3. Withdraw money")
        print("4. Mini statement")
        print("5. Search account")
        print("6. Close account")
        print("7. Credit monthly interest")
        print("0. Exit")
        print("Savings minimum: Rs. 500.00")
        print("Current minimum: Rs. 1,000.00")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                account = open_account(
                    input("Name: "),
                    input("Account type (Savings/Current): "),
                    input("Opening deposit: "),
                )
                print("Account opened. Number:", account["number"])

            elif choice == "2":
                account = deposit_money(
                    input("Account number: "),
                    input("Deposit amount: "),
                )
                print("Deposit successful. Balance:", show_money(account["balance"]))

            elif choice == "3":
                account = withdraw_money(
                    input("Account number: "),
                    input("Withdrawal amount: "),
                )
                print("Withdrawal successful. Balance:", show_money(account["balance"]))

            elif choice == "4":
                number = input("Account number: ")
                items = mini_statement(number)
                print("Date                Type                 Amount        Balance")
                for item in items:
                    print(
                        f"{item['date']:19} "
                        f"{item['type']:20} "
                        f"{show_money(item['amount']):13} "
                        f"{show_money(item['balance'])}"
                    )

            elif choice == "5":
                results = search_account(input("Account number or name: "))
                if len(results) == 0:
                    print("No active account found.")
                for account in results:
                    show_account(account)

            elif choice == "6":
                number = input("Account number: ")
                account = active_account(number)
                if account["balance"] != Decimal("0.00"):
                    print(
                        "Current balance:",
                        show_money(account["balance"]),
                    )
                    answer = input(
                        "Withdraw the full balance as final settlement and close? (yes/no): "
                    ).strip().lower()
                    if answer != "yes":
                        raise ValueError("Account was not closed because balance is not zero.")
                    close_account(number, True)
                else:
                    close_account(number)
                print("Account closed successfully.")

            elif choice == "7":
                count = apply_interest_to_savings(
                    input("Annual interest rate (%): ")
                )
                print("Interest credited to", count, "Savings account(s).")

            elif choice == "0":
                print("Thank you for using VaultCore.")
                break

            else:
                print("Invalid option.")

        except ValueError as error:
            print("Error:", error)


if __name__ == "__main__":
    main()
