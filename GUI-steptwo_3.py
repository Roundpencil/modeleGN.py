import tkinter as tk
from tkinter import ttk
from configparser import ConfigParser


class ConfigEditor(tk.Tk):
    def __init__(self, config_file):
        super().__init__()

        self.row = 0
        self.title("Configuration Editor")
        self.geometry("600x400")
        self.columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew")

        self.config_file = config_file
        self.config = ConfigParser()
        self.load_config()

    def load_config(self):
        self.config.read(self.config_file)
        self.display_config(self.config)

    def display_config(self, config):
        self.notebook.destroy()

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew")

        section_frames = {}

        for section in config.sections():
            dossier_type = section.split("_")[0]
            if dossier_type not in section_frames:
                frame = ttk.Frame(self.notebook)
                section_frames[dossier_type] = frame
                self.notebook.add(frame, text=dossier_type)

            frame = section_frames[dossier_type]
            frame.columnconfigure(1, weight=1)

            section_label = tk.Label(frame, text=section, font=("Helvetica", 12, "bold"))
            section_label.grid(row=self.row, column=0, columnspan=2, pady=(10, 0))

            self.row += 1

            for key, value in config.items(section):
                key_label = tk.Label(frame, text=key)
                key_label.grid(row=self.row, column=0, sticky="w")

                value_entry = tk.Entry(frame)
                value_entry.insert(tk.END, value)
                value_entry.grid(row=self.row, column=1, sticky="ew")

                self.row += 1

            self.row = 0

if __name__ == "__main__":
    config_file = "sample_config.ini"
    app = ConfigEditor(config_file)
    app.mainloop()
