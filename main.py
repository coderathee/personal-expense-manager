import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime


# =========================================================
# DATABASE
# =========================================================

def create_database():
    connection = sqlite3.connect("expense_manager.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            date TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_transaction(transaction_type, amount, category):
    connection = sqlite3.connect("expense_manager.db")
    cursor = connection.cursor()

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO transactions
        (type, amount, category, date)
        VALUES (?, ?, ?, ?)
    """, (transaction_type, amount, category, date))

    connection.commit()
    connection.close()


def get_totals():
    connection = sqlite3.connect("expense_manager.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'Income'
    """)

    income = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'Expense'
    """)

    expense = cursor.fetchone()[0]

    connection.close()

    return income, expense


# =========================================================
# MAIN WINDOW
# =========================================================

window = tk.Tk()

window.title("Personal Expense Manager")
window.geometry("900x600")
window.resizable(False, False)


# =========================================================
# DISPLAY VARIABLES
# =========================================================

income_text = tk.StringVar(value="₹0")
expense_text = tk.StringVar(value="₹0")
balance_text = tk.StringVar(value="₹0")


# =========================================================
# UPDATE DASHBOARD
# =========================================================

def update_dashboard():

    income, expense = get_totals()

    balance = income - expense

    income_text.set(f"₹{income:.2f}")
    expense_text.set(f"₹{expense:.2f}")
    balance_text.set(f"₹{balance:.2f}")


# =========================================================
# ADD INCOME
# =========================================================

def add_income():

    income_window = tk.Toplevel(window)

    income_window.title("Add Income")
    income_window.geometry("350x220")
    income_window.resizable(False, False)

    tk.Label(
        income_window,
        text="Enter Income Amount",
        font=("Arial", 14, "bold")
    ).pack(pady=20)

    amount_entry = tk.Entry(
        income_window,
        font=("Arial", 14),
        width=20
    )

    amount_entry.pack()

    def save_income():

        try:

            amount = float(amount_entry.get())

            if amount <= 0:

                messagebox.showerror(
                    "Error",
                    "Amount must be greater than 0."
                )

                return

            save_transaction(
                "Income",
                amount,
                "Income"
            )

            update_dashboard()

            income_window.destroy()

            messagebox.showinfo(
                "Success",
                "Income saved successfully!"
            )

        except ValueError:

            messagebox.showerror(
                "Invalid Amount",
                "Please enter a valid number."
            )

    tk.Button(
        income_window,
        text="Save Income",
        width=15,
        command=save_income
    ).pack(pady=20)


# =========================================================
# ADD EXPENSE
# =========================================================

def add_expense():

    expense_window = tk.Toplevel(window)

    expense_window.title("Add Expense")
    expense_window.geometry("350x320")
    expense_window.resizable(False, False)

    tk.Label(
        expense_window,
        text="Enter Expense Amount",
        font=("Arial", 14, "bold")
    ).pack(pady=15)

    amount_entry = tk.Entry(
        expense_window,
        font=("Arial", 14),
        width=20
    )

    amount_entry.pack()

    tk.Label(
        expense_window,
        text="Select Category",
        font=("Arial", 12)
    ).pack(pady=15)

    category_var = tk.StringVar(
        value="Food"
    )

    categories = [
        "Food",
        "Travel",
        "Shopping",
        "Bills",
        "Entertainment",
        "Education",
        "Health",
        "Other"
    ]

    category_menu = tk.OptionMenu(
        expense_window,
        category_var,
        *categories
    )

    category_menu.pack()

    def save_expense():

        try:

            amount = float(
                amount_entry.get()
            )

            if amount <= 0:

                messagebox.showerror(
                    "Error",
                    "Amount must be greater than 0."
                )

                return

            category = category_var.get()

            save_transaction(
                "Expense",
                amount,
                category
            )

            update_dashboard()

            expense_window.destroy()

            messagebox.showinfo(
                "Success",
                "Expense saved successfully!"
            )

        except ValueError:

            messagebox.showerror(
                "Invalid Amount",
                "Please enter a valid number."
            )

    tk.Button(
        expense_window,
        text="Save Expense",
        width=15,
        command=save_expense
    ).pack(pady=20)


# =========================================================
# VIEW TRANSACTIONS
# =========================================================

def view_transactions():

    transaction_window = tk.Toplevel(window)

    transaction_window.title(
        "Transaction History"
    )

    transaction_window.geometry(
        "850x550"
    )

    transaction_window.resizable(
        False,
        False
    )

    tk.Label(
        transaction_window,
        text="Transaction History",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    table_frame = tk.Frame(
        transaction_window
    )

    table_frame.pack()

    headings = [
        "ID",
        "Type",
        "Amount",
        "Category",
        "Date"
    ]

    for column, heading in enumerate(headings):

        tk.Label(
            table_frame,
            text=heading,
            font=("Arial", 11, "bold"),
            width=16,
            borderwidth=1,
            relief="solid"
        ).grid(
            row=0,
            column=column
        )

    def load_transactions():

        for widget in table_frame.winfo_children():

            if widget.grid_info().get(
                "row",
                0
            ) != 0:

                widget.destroy()

        connection = sqlite3.connect(
            "expense_manager.db"
        )

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                type,
                amount,
                category,
                date
            FROM transactions
            ORDER BY id DESC
        """)

        transactions = cursor.fetchall()

        connection.close()

        for row, transaction in enumerate(
            transactions,
            start=1
        ):

            for column, value in enumerate(
                transaction
            ):

                if column == 2:

                    value = f"₹{value:.2f}"

                tk.Label(
                    table_frame,
                    text=value,
                    width=16,
                    borderwidth=1,
                    relief="solid"
                ).grid(
                    row=row,
                    column=column
                )

    # -----------------------------------------------------
    # DELETE TRANSACTION
    # -----------------------------------------------------

    def delete_transaction():

        delete_window = tk.Toplevel(
            transaction_window
        )

        delete_window.title(
            "Delete Transaction"
        )

        delete_window.geometry(
            "350x220"
        )

        delete_window.resizable(
            False,
            False
        )

        tk.Label(
            delete_window,
            text="Enter Transaction ID",
            font=("Arial", 14, "bold")
        ).pack(pady=20)

        id_entry = tk.Entry(
            delete_window,
            font=("Arial", 14),
            width=15
        )

        id_entry.pack()

        def confirm_delete():

            try:

                transaction_id = int(
                    id_entry.get()
                )

                connection = sqlite3.connect(
                    "expense_manager.db"
                )

                cursor = connection.cursor()

                cursor.execute(
                    """
                    SELECT *
                    FROM transactions
                    WHERE id = ?
                    """,
                    (transaction_id,)
                )

                transaction = cursor.fetchone()

                if transaction is None:

                    connection.close()

                    messagebox.showerror(
                        "Error",
                        "Transaction ID not found."
                    )

                    return

                cursor.execute(
                    """
                    DELETE FROM transactions
                    WHERE id = ?
                    """,
                    (transaction_id,)
                )

                connection.commit()

                connection.close()

                delete_window.destroy()

                load_transactions()

                update_dashboard()

                messagebox.showinfo(
                    "Success",
                    "Transaction deleted successfully!"
                )

            except ValueError:

                messagebox.showerror(
                    "Invalid ID",
                    "Please enter a valid transaction ID."
                )

        tk.Button(
            delete_window,
            text="Delete",
            width=15,
            command=confirm_delete
        ).pack(pady=20)

    tk.Button(
        transaction_window,
        text="Delete Transaction",
        width=20,
        height=2,
        command=delete_transaction
    ).pack(pady=25)

    load_transactions()


# =========================================================
# MONTHLY SUMMARY
# =========================================================

def monthly_summary():

    summary_window = tk.Toplevel(window)

    summary_window.title(
        "Monthly Expense Summary"
    )

    summary_window.geometry(
        "650x500"
    )

    summary_window.resizable(
        False,
        False
    )

    tk.Label(
        summary_window,
        text="Monthly Expense Summary",
        font=("Arial", 20, "bold")
    ).pack(pady=20)

    current_month = datetime.now().strftime(
        "%Y-%m"
    )

    connection = sqlite3.connect(
        "expense_manager.db"
    )

    cursor = connection.cursor()

    # Total monthly expense
    cursor.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'Expense'
        AND date LIKE ?
        """,
        (current_month + "%",)
    )

    monthly_expense = cursor.fetchone()[0]

    # Total monthly income
    cursor.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'Income'
        AND date LIKE ?
        """,
        (current_month + "%",)
    )

    monthly_income = cursor.fetchone()[0]

    # Category-wise expenses
    cursor.execute(
        """
        SELECT
            category,
            SUM(amount)
        FROM transactions
        WHERE type = 'Expense'
        AND date LIKE ?
        GROUP BY category
        ORDER BY SUM(amount) DESC
        """,
        (current_month + "%",)
    )

    categories = cursor.fetchall()

    connection.close()

    tk.Label(
        summary_window,
        text=f"Current Month: {current_month}",
        font=("Arial", 13)
    ).pack(pady=5)

    tk.Label(
        summary_window,
        text=f"Monthly Income: ₹{monthly_income:.2f}",
        font=("Arial", 14)
    ).pack(pady=5)

    tk.Label(
        summary_window,
        text=f"Monthly Expense: ₹{monthly_expense:.2f}",
        font=("Arial", 14)
    ).pack(pady=5)

    tk.Label(
        summary_window,
        text="Category-wise Expenses",
        font=("Arial", 15, "bold")
    ).pack(pady=20)

    for category, amount in categories:

        tk.Label(
            summary_window,
            text=f"{category}: ₹{amount:.2f}",
            font=("Arial", 12)
        ).pack(pady=3)


# =========================================================
# TITLE
# =========================================================

title = tk.Label(
    window,
    text="Personal Expense Manager",
    font=("Arial", 26, "bold")
)

title.pack(pady=30)


# =========================================================
# DASHBOARD
# =========================================================

dashboard = tk.Frame(window)

dashboard.pack(pady=20)


# Income box
income_frame = tk.Frame(
    dashboard,
    width=220,
    height=110,
    relief="solid",
    borderwidth=1
)

income_frame.grid(
    row=0,
    column=0,
    padx=15
)

income_frame.pack_propagate(False)

tk.Label(
    income_frame,
    text="Total Income",
    font=("Arial", 14, "bold")
).pack(pady=10)

tk.Label(
    income_frame,
    textvariable=income_text,
    font=("Arial", 20)
).pack()


# Expense box
expense_frame = tk.Frame(
    dashboard,
    width=220,
    height=110,
    relief="solid",
    borderwidth=1
)

expense_frame.grid(
    row=0,
    column=1,
    padx=15
)

expense_frame.pack_propagate(False)

tk.Label(
    expense_frame,
    text="Total Expense",
    font=("Arial", 14, "bold")
).pack(pady=10)

tk.Label(
    expense_frame,
    textvariable=expense_text,
    font=("Arial", 20)
).pack()


# Balance box
balance_frame = tk.Frame(
    dashboard,
    width=220,
    height=110,
    relief="solid",
    borderwidth=1
)

balance_frame.grid(
    row=0,
    column=2,
    padx=15
)

balance_frame.pack_propagate(False)

tk.Label(
    balance_frame,
    text="Balance",
    font=("Arial", 14, "bold")
).pack(pady=10)

tk.Label(
    balance_frame,
    textvariable=balance_text,
    font=("Arial", 20)
).pack()


# =========================================================
# BUTTONS
# =========================================================

button_frame = tk.Frame(window)

button_frame.pack(pady=35)


tk.Button(
    button_frame,
    text="Add Income",
    width=18,
    height=2,
    command=add_income
).grid(
    row=0,
    column=0,
    padx=8
)


tk.Button(
    button_frame,
    text="Add Expense",
    width=18,
    height=2,
    command=add_expense
).grid(
    row=0,
    column=1,
    padx=8
)


tk.Button(
    button_frame,
    text="View Transactions",
    width=18,
    height=2,
    command=view_transactions
).grid(
    row=0,
    column=2,
    padx=8
)


tk.Button(
    button_frame,
    text="Monthly Summary",
    width=18,
    height=2,
    command=monthly_summary
).grid(
    row=0,
    column=3,
    padx=8
)


# =========================================================
# START APPLICATION
# =========================================================

create_database()

update_dashboard()

window.mainloop()