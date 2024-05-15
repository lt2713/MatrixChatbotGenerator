import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import os
from structures.transaction import Transaction


def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_label.config(text=file_path)


def submit():
    course_name = course_name_entry.get()
    selected_file = file_label.cget('text')
    year = year_entry.get()
    chatbot_name = chatbot_name_entry.get()
    messages_per_day = msg_per_day_selected.get()
    # Check inputs
    # Check course name not empty
    if not course_name:
        messagebox.showerror('Input Error', 'Course Name is mandatory.')
        return
    # Check Chatbot name not empty
    if not chatbot_name:
        messagebox.showerror('Input Error', 'Chatbot Name is mandatory.')
        return
    # Check File selected
    if selected_file == default_file_name:
        messagebox.showerror('Input Error', 'You need to select a file.')
        return
    # Check File has correct extension
    valid_extensions = ('.xml', '.qti')
    file_extension = os.path.splitext(selected_file)[1].lower()
    if file_extension not in valid_extensions:
        messagebox.showerror('Input Error', 'Only XML or QTI Files are valid.')
        return
    # Create new transaction
    transaction = Transaction(course_name, year, chatbot_name, messages_per_day, selected_file)
    transaction.print()


# main
root = tk.Tk()
# set window title
root.title('Create Chatbot from QTI')

# set window size
root.geometry("500x300")
root.grid_columnconfigure(0, weight=1, minsize=150)
root.grid_columnconfigure(1, weight=3, minsize=350)

# create course name input field
tk.Label(root, text='Course Name:').grid(row=0, column=0, padx=10, pady=5, sticky='w')
course_name_entry = tk.Entry(root, width=50)
course_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w',)

# create year input field
tk.Label(root, text='Course Year:').grid(row=1, column=0, padx=10, pady=5, sticky='w')
year_entry = tk.Entry(root, width=4)
year_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')

# create chatbot name input field
tk.Label(root, text='Chatbot Name').grid(row=2, column=0, padx=10, pady=5, sticky='w')
chatbot_name_entry = tk.Entry(root, width=50)
chatbot_name_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')

# create messages per day dropdown
tk.Label(root, text="Messages per day:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
options = ["1", "2", "3", "4"]
msg_per_day_selected = tk.StringVar()
msg_per_day_dropdown = ttk.Combobox(root, textvariable=msg_per_day_selected, values=options)
msg_per_day_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky='w')
msg_per_day_dropdown.current(0)  # Set default selection

# create select file button
default_file_name = "No file selected"
tk.Button(root, text='Select File', command=select_file).grid(row=4, column=0, padx=10, pady=20, sticky='w')
file_label = tk.Label(root, text=default_file_name)
file_label.grid(row=4, column=1, padx=10, pady=20, sticky='w')

# create submit button
tk.Button(root, text='Submit', command=submit).grid(row=5, column=0, columnspan=2, padx=10, pady=50)

root.mainloop()
