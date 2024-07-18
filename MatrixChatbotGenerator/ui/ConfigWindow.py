import tkinter as tk
from tkinter import messagebox

from classes.ConfigManager import ConfigManager
from util.http_handler import HttpHandler


class ConfigWindow:

    def __init__(self, config_name):
        self.config_name = config_name if config_name else 'Db'
        self.cm = ConfigManager()
        self.config = self.cm.load_config(config_name)

        self.root = tk.Tk()
        if self.config_name == 'Db':
            self.root.title("Database Configuration")
        else:
            self.root.title("Matrix Bot Configuration")

        tk.Label(self.root, text="Server:").grid(row=0, column=0, padx=10, pady=5)
        self.server_entry = tk.Entry( self.root, width=40)
        self.server_entry.grid(row=0, column=1, padx=10, pady=5)
        self.server_entry.insert(0,  self.config[self.config_name].get('server', ''))

        tk.Label(self.root, text="User ID:").grid(row=1, column=0, padx=10, pady=5)
        self.user_id_entry = tk.Entry( self.root, width=40)
        self.user_id_entry.grid(row=1, column=1, padx=10, pady=5)
        self.user_id_entry.insert(0,  self.config[self.config_name].get('user_id', ''))

        tk.Label(self.root, text="Password:").grid(row=2, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(self.root, width=40, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)
        pw = ConfigManager.decrypt_password(self.config['Db']['password'])
        self.password_entry.insert(0, pw)

        tk.Button(self.root, text="Cancel", command=self.root.destroy).grid(row=4, column=0, padx=10,
                                                                            pady=10, sticky='e')
        tk.Button(self.root, text="Save", command=self.on_save).grid(row=4, column=1, padx=10, pady=10, sticky='w')

        if config_name == 'Db':
            tk.Button(self.root, text="Test Connection", command=self.test_connection).grid(row=3, column=1, padx=10,
                                                                                            pady=10, sticky='w')

    def on_save(self):
        server = self.server_entry.get().strip()
        user_id = self.user_id_entry.get().strip()
        password = self.password_entry.get().strip()

        if not server:
            self.show_message("error", "Error", "Server is required.")
            return

        encrypted_password = ConfigManager.encrypt_password(password)
        self.config[self.config_name]['server'] = server
        self.config[self.config_name]['user_id'] = user_id
        self.config[self.config_name]['password'] = encrypted_password
        ConfigManager.save_config(self.config)
        self.show_message("info", "Success", "Configuration saved successfully.")
        self.root.destroy()

    def loop(self):
        try:
            self.root.mainloop()
        except Exception as e:
            print(f'An Error occurred in the config window: {e}')

    def test_connection(self):
        if not self.server_entry.get().strip():
            self.show_message("error", "Error", "Server is required.")
            return
        hh = HttpHandler(self.server_entry.get().strip(), self.user_id_entry.get().strip(),
                         self.password_entry.get().strip())
        try:
            if hh.test_connection():
                self.show_message("info", "Success", "Connection successful!")
            else:
                self.show_message("error", "Error", f"Connection failed!")
        except Exception as e:
            self.show_message("error", "Error", f"Connection failed: {e}")

    def show_message(self, message_type, title, message):
        if message_type == "info":
            messagebox.showinfo(title, message, parent=self.root)
        elif message_type == "error":
            messagebox.showerror(title, message, parent=self.root)


if __name__ == '__main__':
    window = ConfigWindow('Db')
    window.loop()


