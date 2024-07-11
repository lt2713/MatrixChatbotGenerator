import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from ui.QuizWindow import QuizWindow


class QuizzesWindow:
    def __init__(self, root, http_handler):
        self.root = root
        self.hh = http_handler

        self.quizzes_window = tk.Toplevel(self.root)
        self.quizzes_window.title("Manage Quizzes")
        self.quizzes_window.geometry("700x400")

        # Create a frame for the table and scrollbar
        self.frame = tk.Frame(self.quizzes_window)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for the scrollbar
        self.canvas = tk.Canvas(self.frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        self.scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas
        self.table_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        # Bind the canvas to the scrollbar
        self.table_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Table headings
        self.headings = ["Quiz Name", "Messages Per Day", "Questions", "Subscribers"]
        self.create_headings()

        response = self.hh.get('/quizzes')
        self.quizzes = response.json()

        self.refresh()  # Initial fetch and display of quizzes

    def create_headings(self):
        for col, heading in enumerate(self.headings):
            tk.Label(self.table_frame, text=heading, padx=15, pady=5,
                     font=('Arial', 9)).grid(row=0, column=col, sticky='ew')
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(len(self.headings) - 1, weight=1)
        ttk.Separator(self.table_frame, orient='horizontal').grid(row=1, column=0, columnspan=len(self.headings)+2,
                                                                  sticky='ew', pady=(0, 10))

    def display_quizzes(self):
        # Clear the existing widgets except the headings
        for widget in self.table_frame.winfo_children():
            if widget.grid_info()["row"] > 1:  # Skip heading row
                widget.destroy()

        self.fill_list()

    def fill_list(self):
        for row, quiz in enumerate(self.quizzes, start=2):
            tk.Label(self.table_frame, text=quiz['name'], padx=10, pady=5).grid(row=row, column=0, sticky='ew')
            tk.Label(self.table_frame, text=quiz['messages_per_day'], padx=10, pady=5).grid(row=row, column=1,
                                                                                            sticky='ew')
            tk.Label(self.table_frame, text=quiz['questions'], padx=10, pady=5).grid(row=row, column=2, sticky='ew')
            tk.Label(self.table_frame, text=quiz['subscribers'], padx=10, pady=5).grid(row=row, column=3, sticky='ew')

            edit_button = tk.Button(self.table_frame, text="Edit", command=lambda q=quiz: self.edit_quiz(q))
            edit_button.grid(row=row, column=4, padx=10, pady=5, sticky='ew')

            delete_button = tk.Button(self.table_frame, text="Delete", command=lambda q=quiz: self.confirm_delete(q))
            delete_button.grid(row=row, column=5, padx=10, pady=5, sticky='ew')

    def confirm_delete(self, quiz):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the quiz '{quiz['name']}'?")
        if confirm:
            self.delete_quiz(quiz)

    def delete_quiz(self, quiz):
        response = self.hh.delete(f'/quizzes/{quiz["id"]}')
        if response.status_code == 200:
            self.show_message('info', 'Success!', 'Quiz deleted successfully.')
            self.refresh()
        else:
            self.show_message('error', 'Error', 'Failed to delete quiz.')

    def refresh(self):
        response = self.hh.get('/quizzes')
        self.quizzes = response.json()
        self.display_quizzes()

    def edit_quiz(self, quiz):
        qw = QuizWindow(self.quizzes_window, self.hh, quiz)
        self.quizzes_window.wait_window(qw.root)
        self.refresh()  # Refresh the list after the edit window is closed

    def show_message(self, message_type, title, message):
        if message_type == "info":
            messagebox.showinfo(title, message, parent=self.root)
        elif message_type == "error":
            messagebox.showerror(title, message, parent=self.root)

    def loop(self):
        self.quizzes_window.mainloop()
