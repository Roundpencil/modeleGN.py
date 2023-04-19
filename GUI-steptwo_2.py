import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import configparser

class ConfigEditor(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Configuration File Editor")
        self.grid()

        self.create_widgets()

    def create_widgets(self):
        self.load_button = tk.Button(self, text="Load Config", command=self.load_config)
        self.load_button.grid(row=0, column=0, pady=10)

        self.save_button = tk.Button(self, text="Save Config", command=self.save_config)
        self.save_button.grid(row=0, column=1, pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    def parse_config(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)

        return config

    def load_config(self):
        filename = askopenfilename(filetypes=[("Config Files", "*.ini"), ("All Files", "*.*")])

        if not filename:
            return

        self.config = self.parse_config(filename)

        for section in self.config.sections():
            section_frame = ttk.Frame(self.notebook)
            self.notebook.add(section_frame, text=section)

            for i, (key, value) in enumerate(self.config.items(section)):
                key_label = tk.Label(section_frame, text=key)
                key_label.grid(row=i, column=0, padx=(10, 0), pady=5, sticky="e")

                value_entry = tk.Entry(section_frame)
                value_entry.insert(0, value)
                value_entry.grid(row=i, column=1, padx=(0, 10), pady=5)

                if key.startswith("id_dossier"):
                    add_button = tk.Button(section_frame, text="Add", command=lambda f=section_frame, k=key: self.add_entry(f, k))
                    add_button.grid(row=i, column=2, padx=(0, 10), pady=5)

                    remove_button = tk.Button(section_frame, text="Remove", command=lambda f=section_frame, k=key: self.remove_entry(f, k))
                    remove_button.grid(row=i, column=3, padx=(0, 10), pady=5)

    def add_entry(self, section_frame, key):
        key_label = tk.Label(section_frame, text=key)
        key_label.grid(row=len(section_frame.grid_slaves()), column=0, padx=(10, 0), pady=5, sticky="e")

        value_entry = tk.Entry(section_frame)
        value_entry.grid(row=len(section_frame.grid_slaves()), column=1, padx=(0, 10), pady=5)

    def remove_entry(self, section_frame, key):
        matching_widgets = [w for w in section_frame.grid_slaves() if w.cget("text") == key]
        if matching_widgets:
            last_widget = matching_widgets[-1]
            row = last_widget.grid_info()['row']
            for w in section_frame.grid_slaves():
                if w.grid_info()['row'] == row:
                    w.grid_forget()

    def save_config(self):
        filename = asksaveasfilename(defaultextension=".ini", filetypes=[("Config Files", "*.ini"), ("All Files", "*.*")])

        if not filename:
            return

        new_config = configparser.ConfigParser()

        for section_index in range(self.notebook.index("end")):
            section_frame = self.notebook.nametowidget(self.notebook.tabs()[section_index])
            section_name = self.notebook.tab(section_index, "text")
            new_config.add_section(section_name)

            entries = {}
            for widget in section_frame.grid_slaves():
                if isinstance(widget, tk.Entry):
                    row = widget.grid_info()['row']
                    column = widget.grid_info()['column']
                    if column == 1:
                        entries[row] = widget.get()
                elif isinstance(widget, tk.Label) and widget.grid_info()['column'] == 0:
                    row = widget.grid_info()['row']
                    key = widget.cget("text")
                    new_config.set(section_name, key, entries[row])

        with open(filename, "w") as configfile:
            new_config.write(configfile)

root = tk.Tk()
app = ConfigEditor(master=root)
app.mainloop()
