import sqlite3

# Connect to database
connection = sqlite3.connect("expense_manager.db")

# Create cursor
cursor = connection.cursor()

# Create transactions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT,
    date TEXT NOT NULL
)
""")

# Save changes
connection.commit()

# Close connection
connection.close()

print("Database created successfully!")