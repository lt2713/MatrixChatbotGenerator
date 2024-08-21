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
from ui.QuizzesWindow import QuizzesWindow
from ui.QuizbotInfoWindow import QuizbotInfoWindow
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
        self.root.title('Create Quizbot from QTI')

        # set window size
        self.root.geometry("500x300")
        self.root.grid_columnconfigure(0, weight=1, minsize=150)
        self.root.grid_columnconfigure(1, weight=3, minsize=350)

        # Create a frame to act as a custom menu bar
        menu_frame = tk.Frame(self.root, height=40, bg="#e6e6e6")
        menu_frame.grid(row=0, column=0, columnspan=2, sticky='ew')

        # Create a custom dropdown button for "Actions"
        actions_button = tk.Menubutton(menu_frame, text="Actions", bg="#e6e6e6", fg="black",
                                       relief="flat", padx=10, pady=3)
        actions_button.grid(row=0, column=0, padx=5, pady=3)

        actions_menu = tk.Menu(actions_button, tearoff=0, bg="#e6e6e6", fg="black", relief="flat")
        actions_button["menu"] = actions_menu
        actions_menu.add_command(label="Share Quizbot", command=self.show_quizbot_info)
        actions_menu.add_separator()
        actions_menu.add_command(label="Manage Quizzes", command=self.open_quizzes_window)

        # Create a custom dropdown button for "Options"
        options_button = tk.Menubutton(menu_frame, text="Settings", bg="#e6e6e6", fg="black",
                                       relief="flat", padx=10, pady=3)
        options_button.grid(row=0, column=1, padx=5, pady=3)

        options_menu = tk.Menu(options_button, tearoff=0, bg="#e6e6e6", fg="black", relief="flat")
        options_button["menu"] = options_menu

        options_menu.add_command(label="Configure", command=self.open_db_config)
        options_menu.add_separator()
        options_menu.add_command(label="Exit", command=self.root.quit)

        # Create chatbot name input field
        tk.Label(self.root, text='Quiz Name').grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.quiz_name_entry = tk.Entry(self.root, width=50)
        self.quiz_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        # Create messages per day dropdown
        tk.Label(self.root, text="Messages per day:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.msg_per_day_options = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        self.msg_per_day_selected = tk.StringVar()
        self.msg_per_day_dropdown = ttk.Combobox(self.root, textvariable=self.msg_per_day_selected,
                                                 values=self.msg_per_day_options)
        self.msg_per_day_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        self.msg_per_day_dropdown.current(0)  # Set default selection

        self.default_file_name = "No file selected"
        # Create select file button
        if self.fileselection:
            tk.Button(self.root, text='Select File', command=self.select_file)\
                .grid(row=3, column=0, padx=10, pady=20, sticky='w')
            self.file_label = tk.Label(self.root, text=self.default_file_name)
            self.file_label.grid(row=3, column=1, padx=10, pady=20, sticky='w')
        else:
            tk.Label(self.root, text='Exported Questions are used').grid(row=3, column=1, padx=10, sticky='w')

        # Create submit button
        tk.Button(self.root, text='Submit', command=self.submit).grid(row=4, column=0, columnspan=2, padx=10, pady=50)

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

    def open_quizzes_window(self):
        quizzes_window = QuizzesWindow(self.root)
        quizzes_window.loop()

    @staticmethod
    def open_db_config():
        config_window = ConfigWindow('Db')
        config_window.loop()

    @staticmethod
    def open_matrix_config():
        config_window = ConfigWindow('Matrix')
        config_window.loop()

    @staticmethod
    def show_quizbot_info():
        quizbot_info_window = QuizbotInfoWindow()
        quizbot_info_window.loop()

    def loop(self):
        try:
            self.root.mainloop()
        except Exception as e:
            print(f'An error occurred in the main window: {e}')


if __name__ == '__main__':
    ui = UserInterface()
    ui.loop()
