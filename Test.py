import tkinter
from tkinter import ttk
from tkinter import messagebox

def create_window():
    extra_window = tkinter.Toplevel()
    extra_window.title("Create User Form")
    extra_window.geometry("350x320")
    extra_window.configure()
    
    ttk.Label(extra_window, text="Create User").grid(row=0, column=0, columnspan=2, pady=20)
    ttk.Label(extra_window, text="Email",).grid(row=1, column=0)
    ttk.Entry(extra_window).grid(row=1, column=1, pady=5)
    ttk.Label(extra_window, text="Username").grid(row=2, column=0)
    ttk.Entry(extra_window).grid(row=2, column=1, pady=5)
    ttk.Label(extra_window, text="Password").grid(row=3, column=0)
    ttk.Entry(extra_window, show="*").grid(row=3, column=1, pady=5)
    ttk.Label(extra_window, text="Confirm Password").grid(row=4, column=0)
    ttk.Entry(extra_window, show="*").grid(row=4, column=1, pady=5)
    ttk.Button(extra_window, text="Create").grid(row=5, column=0, columnspan=2, pady=20)

window = tkinter.Tk()
window.title("Login Form")
window.geometry("350x220")
window.configure(bg= "#333333")
#here i am creating a HCI screen for the user to login specifing title geometry and background colour

frame = tkinter.Frame(bg= "#333333")
#this allows the HCI to resize to the middle when expanded


#adding fuctionality to login button
    
#creating usability features
login_label = tkinter.Label(frame, text="Login", bg= "#333333", fg="#8c5630", font=("Aharoni", 20))
username_label = tkinter.Label(frame, text="Username", bg= "#333333", fg="#FFFFFF", font=("Aharoni", 12))
username_entry = tkinter.Entry(frame, font=("Aharoni", 12))
password_label = tkinter.Label(frame, text="Password", bg= "#333333", fg="#FFFFFF", font=("Aharoni", 12))
password_entry = tkinter.Entry(frame, show="*", font=("Aharoni", 12))
login_button = tkinter.Button(frame, text="Login", bg= "#8c5630", fg="#FFFFFF", font=("Aharoni", 12))
create_new_button = tkinter.Button(frame, text="Create New", bg= "#8c5630", fg="#FFFFFF", font=("Aharoni", 12), command= create_window)

#placing the widgets on the screen
login_label.grid(row=0, column=0, columnspan=2, pady=20)
username_label.grid(row=1, column=0)
username_entry.grid(row=1, column=1, pady=5)
password_label.grid(row=2, column=0)
password_entry.grid(row=2, column=1, pady=5)
login_button.grid(row=3, column=0, columnspan=2, pady=20)
create_new_button.grid(row=3, column=0)
frame.pack()

window.mainloop()