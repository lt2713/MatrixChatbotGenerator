import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import os
import threading

from structures.quiz import Quiz
from classes.QTIParser import QTIParser
from classes.ChatbotGenerator import ChatbotGenerator
from ui.ConfigWindow import ConfigWindow
from util.http_handler import HttpHandler


class UserInterface:
    def __init__(self, questions=None):
        self.fileselection = not questions
        if not self.fileselection:
            self.questions = questions

        self.hh = HttpHandler()
        # MatrixChatbotGenerator
        self.root = tk.Tk()
        # set window title
        self.root.title('Create Chatbot from QTI')

        # set window size
        self.root.geometry("500x300")
        self.root.grid_columnconfigure(0, weight=1, minsize=150)
        self.root.grid_columnconfigure(1, weight=3, minsize=350)

        # create menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        # create file menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Edit Db Config", command=self.open_db_config)
        file_menu.add_command(label="Manage Quizzes", command=self.manage_quizzes)
        # file_menu.add_command(label="Edit Matrix Config", command=self.open_matrix_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # create chatbot name input field
        tk.Label(self.root, text='Quiz Name').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.quiz_name_entry = tk.Entry(self.root, width=50)
        self.quiz_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')

        # create messages per day dropdown
        tk.Label(self.root, text="Messages per day:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.msg_per_day_options = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        self.msg_per_day_selected = tk.StringVar()
        self.msg_per_day_dropdown = ttk.Combobox(self.root, textvariable=self.msg_per_day_selected,
                                                 values=self.msg_per_day_options)
        self.msg_per_day_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        self.msg_per_day_dropdown.current(0)  # Set default selection

        self.default_file_name = "No file selected"
        # create select file button
        if self.fileselection:
            tk.Button(self.root, text='Select File', command=self.select_file)\
                .grid(row=2, column=0, padx=10, pady=20, sticky='w')
            self.file_label = tk.Label(self.root, text=self.default_file_name)
            self.file_label.grid(row=2, column=1, padx=10, pady=20, sticky='w')
        else:
            tk.Label(self.root, text='Exported Questions are used').grid(row=2, column=1, padx=10, sticky='w')

        # create submit button
        tk.Button(self.root, text='Submit', command=self.submit).grid(row=3, column=0, columnspan=2, padx=10, pady=50)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_label.config(text=file_path)

    def submit(self):
        quiz_name = self.quiz_name_entry.get()
        if self.fileselection:
            selected_file = self.file_label.cget('text')
        else:
            selected_file = None
        messages_per_day = self.msg_per_day_selected.get()
        # Check inputs
        # Check quiz name not empty
        if not quiz_name:
            messagebox.showerror('Input Error', 'Quiz Name is mandatory.')
            return

        # Check File selected
        if self.fileselection:
            if selected_file == self.default_file_name:
                messagebox.showerror('Input Error', 'You need to select a file.')
                return
            # Check File has correct extension
            valid_extensions = ('.xml', '.qti')
            file_extension = os.path.splitext(selected_file)[1].lower()
            if file_extension not in valid_extensions:
                messagebox.showerror('Input Error', 'Only XML or QTI Files are valid.')
                return

        # Create new transaction
        if self.fileselection:
            qtiparser = QTIParser(selected_file)
            self.questions = qtiparser.get_questions()
        quiz = Quiz(quiz_name, messages_per_day, selected_file, self.questions)
        cg = ChatbotGenerator(quiz)

        progress_window = tk.Toplevel(self.root)
        progress_window.title("Progress")
        progress_window.geometry("400x100")
        progress_label = tk.Label(progress_window, text="Uploading Quiz...")
        progress_label.pack(pady=10)
        progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
        progress_bar.pack(pady=10)

        def update_progress(value):
            progress_bar["value"] = value
            progress_window.update_idletasks()

        def run_generator():
            if cg.start(update_progress):
                messagebox.showinfo('Success!', f'Quiz {quiz.name} was created containing '
                                                f'{quiz.get_number_of_questions()} questions.')
                self.clear_screen()
            else:
                messagebox.showerror('Error!', cg.get_message())
            progress_window.destroy()

        threading.Thread(target=run_generator).start()

    def clear_screen(self):
        if self.fileselection:
            self.file_label.config(text=self.default_file_name)
        self.quiz_name_entry.delete(0, tk.END)
        self.msg_per_day_dropdown.current(0)
        self.quiz_name_entry.focus_set()

    def manage_quizzes(self):
        self.quizzes_window = tk.Toplevel(self.root)
        self.quizzes_window.title("Manage Quizzes")
        self.quizzes_window.geometry("600x400")

        # Table headings
        headings = ["Quiz Name", "Messages Per Day", "Subscribers", "Actions"]
        for col, heading in enumerate(headings):
            tk.Label(self.quizzes_window, text=heading).grid(row=0, column=col)

        # Fetch quizzes and display them
        self.display_quizzes()

    def display_quizzes(self):
        for widget in self.quizzes_window.winfo_children():
            widget.destroy()

        headings = ["Quiz Name", "Messages Per Day", "Subscribers", "Actions"]
        for col, heading in enumerate(headings):
            tk.Label(self.quizzes_window, text=heading).grid(row=0, column=col)

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

    def edit_quiz(self, quiz):
        self.edit_window = tk.Toplevel(self.quizzes_window)
        # Open a new window to edit the quiz details
        self.edit_window.title(f"Edit Quiz: {quiz['name']}")
        self.edit_window.geometry("400x200")

        tk.Label(self.edit_window, text='Quiz Name').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        quiz_name_entry = tk.Entry(self.edit_window, width=50)
        quiz_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        quiz_name_entry.insert(0, quiz['name'])

        tk.Label(self.edit_window, text="Messages per day:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        msg_per_day_selected = tk.StringVar()
        msg_per_day_dropdown = ttk.Combobox(self.edit_window, textvariable=msg_per_day_selected,
                                            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        msg_per_day_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        msg_per_day_dropdown.set(quiz['messages_per_day'])

        save_button = tk.Button(self.edit_window, text="Save",
                                command=lambda: self.save_quiz_changes(quiz['id'], quiz_name_entry.get(),
                                                                       msg_per_day_selected.get()))
        save_button.grid(row=2, column=0, columnspan=2, pady=10)

    def save_quiz_changes(self, quiz_id, new_name, new_messages_per_day):
        data = {
            'name': new_name,
            'messages_per_day': new_messages_per_day
        }
        response = self.hh.put(f'/quizzes/{quiz_id}', data)
        if response.status_code == 200:
            messagebox.showinfo('Success!', 'Quiz updated successfully.')
            self.edit_window.destroy()
            self.display_quizzes()  # Refresh the quiz list
            self.quizzes_window.lift()
            self.quizzes_window.focus_force()
        else:
            messagebox.showerror('Error', 'Failed to update quiz.')

    def delete_quiz(self, quiz):
        response = self.hh.delete(f'/quizzes/{quiz["id"]}')
        if response.status_code == 200:
            messagebox.showinfo('Success!', 'Quiz deleted successfully.')
            self.display_quizzes()
            self.quizzes_window.lift()
            self.quizzes_window.focus_force()
        else:
            messagebox.showerror('Error', 'Failed to delete quiz.')

    @staticmethod
    def open_db_config():
        config_window = ConfigWindow('Db')
        config_window.loop()

    @staticmethod
    def open_matrix_config():
        config_window = ConfigWindow('Matrix')
        config_window.loop()

    def loop(self):
        try:
            self.root.mainloop()
        except Exception as e:
            print(f'An error occurred in the main window: {e}')


if __name__ == '__main__':
    ui = UserInterface()
    ui.loop()
