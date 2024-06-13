import tkinter as tk
from tkinter import messagebox
from ui.QuizWindow import QuizWindow


class QuizzesWindow:
    def __init__(self, root, http_handler):
        self.root = root
        self.hh = http_handler

        self.quizzes_window = tk.Toplevel(self.root)
        self.quizzes_window.title("Manage Quizzes")
        self.quizzes_window.geometry("600x400")

        # Table headings
        headings = ["Quiz Name", "Messages Per Day", "Subscribers", "Actions"]
        for col, heading in enumerate(headings):
            tk.Label(self.quizzes_window, text=heading).grid(row=0, column=col)

    def manage_quizzes(self):
        # Fetch quizzes and display them
        self.display_quizzes()

    def display_quizzes(self):
        for widget in self.quizzes_window.winfo_children():
            widget.destroy()

        headings = ["Quiz Name", "Messages Per Day", "Subscribers", "Actions"]
        for col, heading in enumerate(headings):
            tk.Label(self.quizzes_window, text=heading).grid(row=0, column=col)

        self.fill_list()

    def fill_list(self):
        response = self.hh.get('/quizzes')
        quizzes = response.json()

        for row, quiz in enumerate(quizzes, start=1):
            tk.Label(self.quizzes_window, text=quiz['name']).grid(row=row, column=0)
            tk.Label(self.quizzes_window, text=quiz['messages_per_day']).grid(row=row, column=1)
            tk.Label(self.quizzes_window, text=quiz['subscribers']).grid(row=row, column=2)

            edit_button = tk.Button(self.quizzes_window, text="Edit", command=lambda q=quiz: self.edit_quiz(q))
            edit_button.grid(row=row, column=3)

            delete_button = tk.Button(self.quizzes_window, text="Delete", command=lambda q=quiz: self.delete_quiz(q))
            delete_button.grid(row=row, column=4)

    def delete_quiz(self, quiz):
        response = self.hh.delete(f'/quizzes/{quiz["id"]}')
        if response.status_code == 200:
            self.show_message('info', 'Success!', 'Quiz deleted successfully.')
            self.display_quizzes()
            self.quizzes_window.lift()
            self.quizzes_window.focus_force()
        else:
            self.show_message('error', 'Error', 'Failed to delete quiz.')

    def edit_quiz(self, quiz):
        qw = QuizWindow(self.quizzes_window, self.hh, quiz)
        qw.loop()

    def show_message(self, message_type, title, message):
        if message_type == "info":
            messagebox.showinfo(title, message, parent=self.root)
        elif message_type == "error":
            messagebox.showerror(title, message, parent=self.root)
