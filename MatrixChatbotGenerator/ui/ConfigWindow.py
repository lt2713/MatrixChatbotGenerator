import tkinter as tk
from tkinter import messagebox
import configparser
import os

import requests
from requests.auth import HTTPBasicAuth

from classes.ConfigManager import ConfigManager


class ConfigWindow:

    def __init__(self, config_name):
        self.config_name = config_name if config_name else 'Db'
        self.cm = ConfigManager()
        self.config = self.cm.load_config(config_name)

        self.root = tk.Tk()
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

        tk.Button(self.root, text="Cancel", command=self.root.destroy).grid(row=3, column=0, padx=10,
                                                                            pady=10, sticky='e')
        tk.Button(self.root, text="Save", command=self.on_save).grid(row=3, column=1, padx=10, pady=10, sticky='w')

        if config_name == 'Db':
            tk.Button(self.root, text="Test Connection", command=self.test_connection).grid(row=4, column=1, padx=10,
                                                                                        pady=10, sticky='w')

    def on_save(self):
        server = self.server_entry.get().strip()
        user_id = self.user_id_entry.get().strip()
        password = self.password_entry.get().strip()

        if not server or not user_id or not password:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        encrypted_password = ConfigManager.encrypt_password(password)
        self.config[self.config_name]['server'] = server
        self.config[self.config_name]['user_id'] = user_id
        self.config[self.config_name]['password'] = encrypted_password
        ConfigManager.save_config(self.config)
        messagebox.showinfo("Success", "Configuration saved successfully.")
        self.root.destroy()

    def loop(self):
        try:
            self.root.mainloop()
        except Exception as e:
            print(f'An Error occurred in the config window: {e}')

    def test_connection(self):
        server = self.server_entry.get().strip()
        user_id = self.user_id_entry.get().strip()
        password = self.password_entry.get().strip()

        if not server or not user_id or not password:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            response = requests.get(f'{server}/helloworld', auth=HTTPBasicAuth(user_id, password))
            if response.status_code == 200:
                messagebox.showinfo("Success", "Connection successful!")
            else:
                messagebox.showerror("Error", f"Connection failed: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")


if __name__ == '__main__':
    window = ConfigWindow('Db')
    window.loop()


