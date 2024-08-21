import os
import tkinter as tk
from tkinter import messagebox


class QuizbotInfoWindow:

    def __init__(self):
        # Load environment variables
        self.matrix_host = os.getenv('MATRIX_HOST', 'Unknown Host')
        self.matrix_user = os.getenv('MATRIX_USER', 'Unknown User')
        self.matrix_link = f"https://matrix.to/#/{self.matrix_user}"

        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("Quizbot Information")

        # Display MATRIX_HOST
        tk.Label(self.root, text="Matrix Homeserver:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.host_value = tk.Entry(self.root, width=50)
        self.host_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.host_value.insert(0, self.matrix_host)
        self.host_value.config(state='readonly')  # Make the entry read-only

        # Display MATRIX_USER
        tk.Label(self.root, text="Quizbot User:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.user_value = tk.Entry(self.root, width=50)
        self.user_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.user_value.insert(0, self.matrix_user)
        self.user_value.config(state='readonly')

        # Display the generated Matrix link
        tk.Label(self.root, text="Direct Link:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.link_value = tk.Entry(self.root, width=50)
        self.link_value.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.link_value.insert(0, self.matrix_link)
        self.link_value.config(state='readonly')

        # Copy link to clipboard button
        tk.Button(self.root, text="Copy Link", command=self.copy_to_clipboard).grid(row=3, column=0, columnspan=2,
                                                                                    pady=10)

    def copy_to_clipboard(self):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.matrix_link)
            self.show_message("info", "Copied", "Link copied to clipboard!")
        except Exception as e:
            self.show_message("error", "Error", f"Failed to copy link: {e}")

    def show_message(self, message_type, title, message):
        if message_type == "info":
            messagebox.showinfo(title, message, parent=self.root)
        elif message_type == "error":
            messagebox.showerror(title, message, parent=self.root)

    def loop(self):
        try:
            self.root.mainloop()
        except Exception as e:
            print(f'An Error occurred in the Matrix User Window: {e}')


if __name__ == '__main__':
    window = QuizbotInfoWindow()
    window.loop()
