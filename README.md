# VaultCore

VaultCore is a simple console banking project made in Python. It was created
for the CP-001 Core Banking Transaction Engine problem.

The project is kept in one Python file so it is easy to run and understand.

## Requirements

- Python 3.10 or newer
- Command Prompt, PowerShell or a terminal
- No extra Python packages are needed

## How to run

Extract the ZIP file and open a terminal inside the `VaultCore` folder.

Run this command:

```text
python vaultcore.py
```

If `python` does not work on Windows, try:

```text
py vaultcore.py
```

## Features

1. Open a Savings or Current account with an automatic account number.
2. Deposit and withdraw money.
3. Show the last five transactions of an account.
4. Search for an account using its number or customer name.
5. Close an account after completing the final balance settlement.
6. Credit monthly interest to all active Savings accounts.
7. Save and load account and transaction details using CSV files.

## Minimum balance

- Savings account: Rs. 500
- Current account: Rs. 1,000

A normal withdrawal is rejected if it takes the account below its minimum
balance. During account closure, the remaining balance can be withdrawn as a
final settlement. The account is closed only after its balance becomes zero.

## Saved files

The first successful banking operation creates these files automatically:

- `accounts.csv`
- `transactions.csv`

These files keep the account details and transaction history. The program loads
them again when it starts. Do not change their column names manually.

## Project file

- `vaultcore.py` contains the complete program, menu, banking rules and CSV
  handling.

## Interest calculation

Monthly interest is calculated using:

```text
interest = balance * annual rate / 1200
```

Interest is given only to active Savings accounts.

## Notes

This is a beginner-level educational project. It is not real banking software.
It does not include login security, encryption, online payments or a database.
