import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class GNConfigurator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GN Configurator")
        self.geometry("600x400")

        self.id_dossier_intrigues_entries = []
        self.id_dossier_pjs_entries = []
        self.id_dossier_evenements_entries = []
        self.row_intrigue = 100
        self.row_pj = 200
        self.row_evenement = 300
        self.row_boutons = 400

        self.create_widgets()

    def create_widgets(self):
        mainframe = ttk.Frame(self)
        mainframe.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.create_subframe_with_entries("ID Dossier Intrigues", mainframe, self.id_dossier_intrigues_entries, self.row_intrigue)
        self.create_subframe_with_entries("ID Dossier PJs", mainframe, self.id_dossier_pjs_entries, self.row_pj)
        self.create_subframe_with_entries("ID Dossier Evenements", mainframe, self.id_dossier_evenements_entries, self.row_evenement)

        create_button = ttk.Button(mainframe, text="Créer fichier .ini", command=self.create_ini_file)
        create_button.grid(row=self.row_boutons, column=0, sticky=tk.E)

        cancel_button = ttk.Button(mainframe, text="Annuler", command=self.quit)
        cancel_button.grid(row=self.row_boutons, column=1, sticky=tk.W)

    # def create_subframe_with_entries(self, label_text, frame, entry_list, row):
    #     subframe = ttk.Frame(frame)
    #     subframe.grid(row=row, column=0, columnspan=2, sticky=tk.W)
    #
    #     label = ttk.Label(subframe, text=label_text)
    #     label.pack(side=tk.LEFT)
    #
    #     add_button = ttk.Button(subframe, text="+", command=lambda: self.add_entry_with_suffix(subframe, entry_list))
    #     add_button.pack(side=tk.RIGHT)
    #
    #     remove_button = ttk.Button(subframe, text="-", command=lambda: self.remove_entry(entry_list))
    #     remove_button.pack(side=tk.RIGHT)
    #
    #     self.add_entry_with_suffix(subframe, entry_list)
    def create_subframe_with_entries(self, label_text, frame, entry_list, row):
        subframe = ttk.Frame(frame)
        subframe.grid(row=row, column=0, columnspan=2, sticky=tk.W)

        label = ttk.Label(subframe, text=label_text)
        label.grid(row=0, column=0, sticky=tk.W)

        add_button = ttk.Button(subframe, text="+", command=lambda: self.add_entry_with_suffix(subframe, entry_list))
        add_button.grid(row=0, column=2, sticky=tk.E)

        remove_button = ttk.Button(subframe, text="-", command=lambda: self.remove_entry(entry_list))
        remove_button.grid(row=0, column=1, sticky=tk.E)

        self.add_entry_with_suffix(subframe, entry_list)

    def add_entry_with_suffix(self, frame, entry_list):
        max_row = max_row = max([slave.grid_info()["row"] for slave in frame.grid_slaves()] + [0])

        entry_frame = ttk.Frame(frame)
        entry_frame.grid(row=max_row+1, sticky=tk.EW)

        # entry_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        entry = ttk.Entry(entry_frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        suffix_entry = ttk.Entry(entry_frame, width=10)
        suffix_entry.pack(side=tk.LEFT)

        entry_list.append((entry, suffix_entry))
    # def add_entry_with_suffix(self, frame, entry_list):
    #     # Trouver la première ligne vide, sinon utiliser la ligne suivante après la dernière ligne
    #     empty_rows = [slave.grid_info()["row"] for slave in frame.grid_slaves() if not slave.grid_slaves()]
    #     if empty_rows:
    #         next_row = min(empty_rows)
    #     else:
    #         next_row = max([slave.grid_info()["row"] for slave in frame.grid_slaves()] + [0]) + 1
    #
    #     entry_frame = ttk.Frame(frame)
    #     entry_frame.grid(row=next_row, sticky=tk.EW)
    #
    #     entry = ttk.Entry(entry_frame)
    #     entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    #     suffix_entry = ttk.Entry(entry_frame, width=10)
    #     suffix_entry.pack(side=tk.LEFT)
    #
    #     entry_list.append((entry, suffix_entry))

    def remove_entry(self, entry_list):
        if len(entry_list) > 1:
            entry, suffix_entry = entry_list.pop()
            # entry.grid_forget()
            # suffix_entry.grid_forget()
            entry.destroy()
            suffix_entry.destroy()

    def create_ini_file(self):
        file = filedialog.asksaveasfile(mode="w", defaultextension=".ini", filetypes=[("Fichiers INI", "*.ini")])

        if file:
            file.write("[Essentiels]\n")
            for i, (entry, suffix_entry) in enumerate(self.id_dossier_intrigues_entries, start=1):
                if i == 1:
                    key = "id_dossier_intrigues"
                else:
                    key = f"id_dossier_intrigues_{suffix_entry.get()}"
                file.write(f"{key} = {entry.get()}\n")

            for i, (entry, suffix_entry) in enumerate(self.id_dossier_pjs_entries, start=1):
                if i == 1:
                    key = "id_dossier_pjs"
                else:
                    key = f"id_dossier_pjs_{suffix_entry.get()}"
                file.write(f"{key} = {entry.get()}\n")
            for i, (entry, suffix_entry) in enumerate(self.id_dossier_evenements_entries, start=1):
                if i == 1:
                    key = "id_dossier_evenements"
                else:
                    key = f"id_dossier_evenements_{suffix_entry.get()}"
                file.write(f"{key} = {entry.get()}\n")

            file.close()
            self.quit()

if __name__ == '__main__':
    app = GNConfigurator()
    app.mainloop()