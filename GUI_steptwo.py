import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import configparser
import re


class ConfigEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Configuration File Editor")

        # Top frame for file selection
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)

        self.load_button = tk.Button(self.top_frame, text="Load Config", command=self.load_config)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.top_frame, text="Save Config", command=self.save_config, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Main frame for notebook
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.config = configparser.ConfigParser()

    def parse_config(self, file_content):
        config_data = {}
        section = None

        for line in file_content.splitlines():
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            match = re.match(r'\[(.+)\]', line)
            if match:
                section = match.group(1)
                config_data[section] = []
            else:
                key, value = line.split("=", 1)
                config_data[section].append((key.strip(), value.strip()))

        return config_data

    def load_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("Configuration Files", "*.conf"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as f:
                file_content = f.read()

            config_data = self.parse_config(file_content)

            # Clear notebook
            for tab in self.notebook.tabs():
                self.notebook.forget(tab)

            for section, items in config_data.items():
                frame = ttk.Frame(self.notebook)
                self.notebook.add(frame, text=section)

                for idx, (key, value) in enumerate(items):
                    key_label = ttk.Label(frame, text=key)
                    key_label.grid(row=idx, column=0, padx=5, pady=5, sticky=tk.W)

                    value_entry = ttk.Entry(frame)
                    value_entry.insert(0, value)
                    value_entry.grid(row=idx, column=1, padx=5, pady=5, sticky=tk.W)

            self.save_button.config(state=tk.NORMAL)

    def save_config(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".conf", filetypes=[("Configuration Files", "*.conf"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as f:
                for idx, tab_id in enumerate(self.notebook.tabs()):
                    section = self.notebook.tab(tab_id, "text")
                    frame = self.notebook.nametowidget(tab_id)

                    f.write(f"[{section}]\n")

                    for entry_row in frame.grid_slaves():
                        if entry_row.grid_info()['column'] == 0:
                            continue

                        value = frame.grid_slaves(row=entry_row.grid_info()['row'], column=1)[0].get()
                        key = frame.grid_slaves(row=entry_row, column=0)[0].cget("text")
                        f.write(f"{key} = {value}\n")
                        f.write("\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()
