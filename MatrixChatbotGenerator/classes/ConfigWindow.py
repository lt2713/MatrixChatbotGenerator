import tkinter as tk
from tkinter import messagebox
import configparser
import os

# Determine the absolute path of the configuration file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.ini')


class ConfigWindow:

    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config = self.load_config()

        self.root = tk.Tk()
        self.root.title("Matrix Bot Configuration")

        tk.Label(self.root, text="Homeserver:").grid(row=0, column=0, padx=10, pady=5)
        self.homeserver_entry = tk.Entry( self.root, width=40)
        self.homeserver_entry.grid(row=0, column=1, padx=10, pady=5)
        self.homeserver_entry.insert(0,  self.config['Matrix'].get('homeserver', ''))

        tk.Label(self.root, text="User ID:").grid(row=1, column=0, padx=10, pady=5)
        self.user_id_entry = tk.Entry( self.root, width=40)
        self.user_id_entry.grid(row=1, column=1, padx=10, pady=5)
        self.user_id_entry.insert(0,  self.config['Matrix'].get('user_id', ''))

        tk.Label(self.root, text="Access Token:").grid(row=2, column=0, padx=10, pady=5)
        self.access_token_entry = tk.Entry( self.root, width=40)
        self.access_token_entry.grid(row=2, column=1, padx=10, pady=5)
        self.access_token_entry.insert(0,  self.config['Matrix'].get('access_token', ''))

        tk.Button(self.root, text="Cancel", command=self.root.destroy).grid(row=3, column=0, padx=10,
                                                                            pady=10, sticky='e')
        tk.Button(self.root, text="Save", command=self.on_save).grid(row=3, column=1, padx=10, pady=10, sticky='w')

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
        else:
            config['Matrix'] = {'homeserver': '', 'user_id': '', 'access_token': ''}
            with open(self.config_file, 'w') as configfile:
                config.write(configfile)
        return config

    def save_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def on_save(self):
        homeserver = self.homeserver_entry.get().strip()
        user_id = self.user_id_entry.get().strip()
        access_token = self.access_token_entry.get().strip()

        if not homeserver or not user_id or not access_token:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        self.config['Matrix']['homeserver'] = homeserver
        self.config['Matrix']['user_id'] = user_id
        self.config['Matrix']['access_token'] = access_token
        self.save_config()
        messagebox.showinfo("Success", "Configuration saved successfully.")
        self.root.destroy()

    def loop(self):
        try:
            self.root.mainloop()
        except Exception as e:
            print(f'An Error occurred in the config window: {e}')


if __name__ == '__main__':
    window = ConfigWindow()
    window.loop()


