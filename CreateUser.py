import tkinter
from tkinter import ttk
from tkinter import messagebox
import sqlite3

# Create a SQLite database connection and cursor
conn = sqlite3.connect("user_database.db")
cursor = conn.cursor()

# Create a table for user information if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()

window = tkinter.Tk()
window.title("Create User Form")
window.geometry("350x320")
window.configure(bg="#333333")

frame = tkinter.Frame(bg="#333333")


def check_password(password):
    l, u, d = 0, 0, 0
    if len(password) >= 8:
        for i in password:
            # Counting lowercase alphabets
            if i.islower():
                l += 1
            # Counting uppercase alphabets
            if i.isupper():
                u += 1
            # Counting digits
            if i.isdigit():
                d += 1

        if l >= 1 and u >= 1 and d >= 1 and l + u + d == len(password):
            return "Valid password"
        else:
            messagebox.showerror(title="Credentials Error", message="Invalid password")


def insert_user(email, username, password):
    # Insert user data into the 'users' table
    cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))
    conn.commit()


def create():
    if "@hfed.net" in email_entry.get():
        if username_entry.get() != "":
            if check_password(password_entry.get()) == "Valid password":
                if password_entry.get() == confirm_password_entry.get():
                    # Insert user data into the database
                    insert_user(email_entry.get(), username_entry.get(), password_entry.get())

                    messagebox.showinfo(title="Welcome", message="Creation Successful")
                    window.destroy()
                else:
                    messagebox.showerror(title="Credentials Error", message="Password must be the same")
            else:
                messagebox.showerror(title="Credentials Error",
                                     message="Password must contain upper and lower case characters and numbers")
        else:
            messagebox.showerror(title="Credentials Error", message="Must enter username")
    else:
        messagebox.showerror(title="Credentials Error", message="Email must contain @hfed.net domain")


# Creating usability features
login_label = tkinter.Label(frame, text="Create User", bg="#333333", fg="#8c5630", font=("Aharoni", 20))
email_label = tkinter.Label(frame, text="Email", bg="#333333", fg="#FFFFFF", font=("Aharoni", 12))
email_entry = tkinter.Entry(frame, font=("Aharoni", 12))
username_label = tkinter.Label(frame, text="Username", bg="#333333", fg="#FFFFFF", font=("Aharoni", 12))
username_entry = tkinter.Entry(frame, font=("Aharoni", 12))
password_label = tkinter.Label(frame, text="Password", bg="#333333", fg="#FFFFFF", font=("Aharoni", 12))
password_entry = tkinter.Entry(frame, show="*", font=("Aharoni", 12))
confirm_password_label = tkinter.Label(frame, text="Confirm Password", bg="#333333", fg="#FFFFFF", font=("Aharoni", 12))
confirm_password_entry = tkinter.Entry(frame, show="*", font=("Aharoni", 12))
create_user_button = tkinter.Button(frame, text="Create", bg="#8c5630", fg="#FFFFFF", font=("Aharoni", 12),
                                    command=create)

# Placing the widgets on the screen
login_label.grid(row=0, column=0, columnspan=2, pady=20)
email_label.grid(row=1, column=0)
email_entry.grid(row=1, column=1, pady=5)
username_label.grid(row=2, column=0)
username_entry.grid(row=2, column=1, pady=5)
password_label.grid(row=3, column=0)
password_entry.grid(row=3, column=1, pady=5)
confirm_password_label.grid(row=4, column=0)
confirm_password_entry.grid(row=4, column=1, pady=5)
create_user_button.grid(row=5, column=0, columnspan=2, pady=20)
frame.pack()

window.mainloop()