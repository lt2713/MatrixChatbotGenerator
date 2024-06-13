import tkinter as tk
from tkinter import ttk, messagebox


class QuizWindow:
    def __init__(self, root, http_handler, quiz):
        self.root = root
        self.hh = http_handler

        self.edit_window = tk.Toplevel(self.root)
        # Open a new window to edit the quiz details
        self.edit_window.title(f"Edit Quiz: {quiz['name']}")
        self.edit_window.geometry("400x200")

        tk.Label(self.edit_window, text='Quiz Name').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.quiz_name_entry = tk.Entry(self.edit_window, width=50)
        self.quiz_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        self.quiz_name_entry.insert(0, quiz['name'])

        tk.Label(self.edit_window, text="Messages per day:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.msg_per_day_selected = tk.StringVar()
        self.msg_per_day_dropdown = ttk.Combobox(self.edit_window, textvariable=self.msg_per_day_selected,
                                            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.msg_per_day_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        self.msg_per_day_dropdown.set(quiz['messages_per_day'])

        self.save_button = tk.Button(self.edit_window, text="Save",
                                command=lambda: self.save_quiz_changes(quiz['id'], self.quiz_name_entry.get(),
                                                                       self.msg_per_day_selected.get()))
        self.save_button.grid(row=2, column=0, columnspan=2, pady=10)

    def save_quiz_changes(self, quiz_id, new_name, new_messages_per_day):
        data = {
            'name': new_name,
            'messages_per_day': new_messages_per_day
        }
        response = self.hh.put(f'/quizzes/{quiz_id}', data)
        if response.status_code == 200:
            self.show_message('info', 'Success!', 'Quiz updated successfully.')
            self.edit_window.destroy()
        else:
            self.show_message('error', 'Error', 'Failed to update quiz.')

    def show_message(self, message_type, title, message):
        if message_type == "info":
            messagebox.showinfo(title, message, parent=self.root)
        elif message_type == "error":
            messagebox.showerror(title, message, parent=self.root)

    def loop(self):
        self.edit_window.mainloop()
