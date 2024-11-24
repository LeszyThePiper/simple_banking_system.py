import sqlite3
import random


# Database initialization
def initialize_database():
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS card (
            id INTEGER PRIMARY KEY,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn, cur


# Function to generate a card number following the Luhn Algorithm
def generate_card_number():
    bin_number = "400000"  # Bank Identification Number (BIN)
    account_identifier = f"{random.randint(0, 999999999):09}"  # 9-digit unique Account Identifier
    incomplete_card_number = bin_number + account_identifier
    checksum = luhn_checksum(incomplete_card_number)
    return incomplete_card_number + str(checksum)


# Function to calculate the checksum for the Luhn algorithm
def luhn_checksum(number):
    digits = [int(d) for d in number]
    for i in range(len(digits) - 1, -1, -2):  # Double every second digit from the right
        digits[i] *= 2
        if digits[i] > 9:  # Subtract 9 if the result is greater than 9
            digits[i] -= 9
    total = sum(digits)
    return (10 - total % 10) % 10  # Return the checksum digit


# Function to generate a random 4-digit PIN
def generate_pin():
    return f"{random.randint(0, 9999):04}"


# Check if card number is valid and exists
def validate_card(cur, card_number):
    if luhn_checksum(card_number[:-1]) != int(card_number[-1]):
        return "invalid_luhn"
    cur.execute("SELECT * FROM card WHERE number = ?", (card_number,))
    return "exists" if cur.fetchone() else "not_found"


# Main banking system logic
def main():
    conn, cur = initialize_database()

    while True:
        # Display the main menu
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        choice = input()

        if choice == "1":  # Create a new account
            card_number = generate_card_number()
            pin = generate_pin()
            cur.execute("INSERT INTO card (number, pin) VALUES (?, ?)", (card_number, pin))
            conn.commit()  # Commit after insertion
            print("\nYour card has been created")
            print(f"Your card number:\n{card_number}")
            print(f"Your card PIN:\n{pin}\n")

        elif choice == "2":  # Log into an existing account
            print("\nEnter your card number:")
            entered_card = input()
            print("Enter your PIN:")
            entered_pin = input()

            cur.execute("SELECT * FROM card WHERE number = ? AND pin = ?", (entered_card, entered_pin))
            account = cur.fetchone()

            if account:
                print("\nYou have successfully logged in!\n")
                while True:
                    # Account menu
                    print("1. Balance")
                    print("2. Add income")
                    print("3. Do transfer")
                    print("4. Close account")
                    print("5. Log out")
                    print("0. Exit")
                    sub_choice = input()

                    if sub_choice == "1":  # Check account balance
                        cur.execute("SELECT balance FROM card WHERE number = ?", (entered_card,))
                        balance = cur.fetchone()[0]
                        print(f"\nBalance: {balance}\n")
                    elif sub_choice == "2":  # Add income
                        print("\nEnter income:")
                        income = int(input())
                        cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (income, entered_card))
                        conn.commit()  # Commit after updating balance
                        print("Income was added!\n")
                    elif sub_choice == "3":  # Do transfer
                        print("\nTransfer")
                        print("Enter card number:")
                        receiver_card = input()

                        if receiver_card == entered_card:
                            print("You can't transfer money to the same account!\n")
                        else:
                            card_status = validate_card(cur, receiver_card)
                            if card_status == "invalid_luhn":
                                print("Probably you made a mistake in the card number. Please try again!\n")
                            elif card_status == "not_found":
                                print("Such a card does not exist.\n")
                            else:
                                print("Enter how much money you want to transfer:")
                                amount = int(input())
                                cur.execute("SELECT balance FROM card WHERE number = ?", (entered_card,))
                                current_balance = cur.fetchone()[0]
                                if current_balance < amount:
                                    print("Not enough money!\n")
                                else:
                                    cur.execute("UPDATE card SET balance = balance - ? WHERE number = ?",
                                                (amount, entered_card))
                                    cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?",
                                                (amount, receiver_card))
                                    conn.commit()  # Commit after the transfer
                                    print("Success!\n")
                    elif sub_choice == "4":  # Close account
                        cur.execute("DELETE FROM card WHERE number = ?", (entered_card,))
                        conn.commit()  # Commit after deleting the account
                        print("\nThe account has been closed!\n")
                        break
                    elif sub_choice == "5":  # Log out of the account
                        print("\nYou have successfully logged out!\n")
                        break
                    elif sub_choice == "0":  # Exit the program
                        print("\nBye!")
                        conn.close()
                        return
                    else:
                        print("\nInvalid option. Try again.\n")
            else:
                print("\nWrong card number or PIN!\n")

        elif choice == "0":  # Exit the program
            print("\nBye!")
            conn.close()
            break

        else:
            print("\nInvalid option. Try again.\n")


if __name__ == "__main__":
    main()
