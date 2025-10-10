import tkinter, sqlite3, ChessMain, webbrowser
from tkinter import ttk
from tkinter import messagebox

with sqlite3.connect("user_database.db") as conn:
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
window.title("Login Form")
window.geometry("350x260")
window.configure(bg="#333333")

frame = tkinter.Frame(bg="#333333")

def open_link():
    #webbrowser.open("https://asq.org/customer-services/faq/login")
    help_window = tkinter.Toplevel(window)
    help_window.title("Login Help")
    help_window.geometry('350x250')
    help_window.configure()
    frame_help = tkinter.Frame(help_window)
    
    tkinter.Label(frame_help, text="How to create a user", font=("Aharoni", 20)).grid(row=0, column=0)
    ttk.Label(frame_help, text='Enter you school email ending in @hfed.net, \n then enter you chosen username, \n this must be unique, next you create a password \n and enter it in the password box \n and re enter it in the confirm password box. \n Lastly you click create. Welcome!', font=("Aharoni", 12)).grid(row=1, column=0)
    frame_help.pack()

def help_link():
    webbrowser.open("https://www.chess.com/learn-how-to-play-chess")

def help_tool():
    chess_window = tkinter.Tk()
    chess_window.title("How to play")
    chess_window.geometry("350x260")
    chess_window.configure(bg="#333333")

    frame = tkinter.Frame(bg="#333333")
    question_button = tkinter.Button(frame, text="Tutorial", bg="#8c5630", fg="#FFFFFF", font=("Aharoni", 12), command=help_link)
    play_button = tkinter.Button(frame, text="No thanks", bg="#8c5630", fg="#FFFFFF", font=("Aharoni", 12), command= chess_window.destroy)
    question_button.pack()
    play_button.pack()
    frame.pack()

def login():
    entered_username = username_entry.get()
    entered_password = password_entry.get()

    cursor.execute("SELECT * FROM users WHERE username=?", (entered_username,))
    user = cursor.fetchone()

    if user and user[3] == entered_password:  # user[3] is the password field in the database
        messagebox.showinfo(title="Welcome", message="Login Successful")
        window.destroy()
        help_tool()
        ChessMain.main()
    else:
        messagebox.showerror(title="Login Error", message="Invalid username or password")

def create_user():
    window_create_user = tkinter.Toplevel(window)
    window_create_user.title("Create User Form")
    window_create_user.geometry("350x320")
    window_create_user.configure()

    frame_create_user = tkinter.Frame(window_create_user)

    def check_password(password):
        l, u, d = 0, 0, 0
        if len(password) >= 8:
            for i in password:
                if i.islower():
                    l += 1
                if i.isupper():
                    u += 1
                if i.isdigit():
                    d += 1

            if l >= 1 and u >= 1 and d >= 1 and l + u + d == len(password):
                return "Valid password"
            else:
                messagebox.showerror(title="Credentials Error", message="Invalid password")

    def insert_user(email, username, password):
        cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))
        conn.commit()

    def create():
        if "@hfed.net" in email_entry.get():
            if username_entry.get() != "":
                if check_password(password_entry.get()) == "Valid password":
                    if password_entry.get() == confirm_password_entry.get():
                        cursor.execute("SELECT * FROM users WHERE username=? OR email=?", (username_entry.get(), email_entry.get()))
                        existing_user = cursor.fetchone()

                        if existing_user:
                            messagebox.showerror(title="Credentials Error", message="Username or email already exists")
                        else:
                            insert_user(email_entry.get(), username_entry.get(), password_entry.get())
                            messagebox.showinfo(title="Welcome", message="Creation Successful")
                            window_create_user.destroy()
                    else:
                        messagebox.showerror(title="Credentials Error", message="Password must be the same")
                else:
                    messagebox.showerror(title="Credentials Error", message="Password must contain upper and lower case characters and numbers")
            else:
                messagebox.showerror(title="Credentials Error", message="Must enter username")
        else:
            messagebox.showerror(title="Credentials Error", message="Email must contain @hfed.net domain")

    login_label = tkinter.Label(frame_create_user, text="Create User", font=("Aharoni", 20))
    email_label = tkinter.Label(frame_create_user, text="Email", font=("Aharoni", 12))
    email_entry = tkinter.Entry(frame_create_user, font=("Aharoni", 12))
    username_label = tkinter.Label(frame_create_user, text="Username", font=("Aharoni", 12))
    username_entry = tkinter.Entry(frame_create_user, font=("Aharoni", 12))
    password_label = tkinter.Label(frame_create_user, text="Password", font=("Aharoni", 12))
    password_entry = tkinter.Entry(frame_create_user, show="*", font=("Aharoni", 12))
    confirm_password_label = tkinter.Label(frame_create_user, text="Confirm Password", font=("Aharoni", 12))
    confirm_password_entry = tkinter.Entry(frame_create_user, show="*", font=("Aharoni", 12))
    create_user_button = tkinter.Button(frame_create_user, text="Create", font=("Aharoni", 12), command=create)
    question_button = tkinter.Button(frame_create_user, text="Help", font=("Aharoni", 12), command=open_link)

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
    question_button.grid(row=5, column=1, columnspan=2, pady=20)
    frame_create_user.pack()


login_label = tkinter.Label(frame, text="Login", bg="#333333", fg="#8c5630", font=("Aharoni", 20))
username_label = tkinter.Label(frame, text="Username", bg="#333333", fg="#FFFFFF", font=("Aharoni", 12))
username_entry = tkinter.Entry(frame, font=("Aharoni", 12))
password_label = tkinter.Label(frame, text="Password", bg="#333333", fg="#FFFFFF", font=("Aharoni", 12))
password_entry = tkinter.Entry(frame, show="*", font=("Aharoni", 12))
login_button = tkinter.Button(frame, text="Login", bg="#8c5630", fg="#FFFFFF", font=("Aharoni", 12), command=login)
create_new_button = tkinter.Button(frame, text="Create New", bg="#8c5630", fg="#FFFFFF", font=("Aharoni", 12), command=create_user)
question_button = tkinter.Button(frame, text="Help", bg="#8c5630", fg="#FFFFFF", font=("Aharoni", 12), command=open_link)

login_label.grid(row=0, column=0, columnspan=2, pady=20)
username_label.grid(row=1, column=0)
username_entry.grid(row=1, column=1, pady=5)
password_label.grid(row=2, column=0)
password_entry.grid(row=2, column=1, pady=5)
login_button.grid(row=3, column=0, columnspan=2, pady=20)
create_new_button.grid(row=3, column=0)
question_button.grid(row=4, column=0, columnspan=2)
frame.pack()

window.mainloop()
