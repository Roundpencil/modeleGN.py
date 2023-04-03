import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class GNConfigurator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GN Configurator")
        self.geometry("800x600")

        self.id_dossier_intrigues_entries = []
        self.id_dossier_pjs_entries = []
        self.id_dossier_pnjs_entries = []
        self.id_dossier_evenements_entries = []
        self.id_dossier_objets_entries = []
        self.id_factions_entries = []

        self.create_widgets()

    def create_widgets(self):
        mainframe = ttk.Frame(self)
        mainframe.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(mainframe, text="Essentiels").grid(row=0, column=0, sticky=tk.W)

        self.create_subframe_with_entries("ID Dossier Intrigues", mainframe, self.id_dossier_intrigues_entries, 1)
        self.create_subframe_with_entries("ID Dossier PJs", mainframe, self.id_dossier_pjs_entries, 2)

        ttk.Label(mainframe, text="Mode Association").grid(row=3, column=0, sticky=tk.W)
        self.mode_association_var = tk.StringVar()
        self.mode_association_var.set("0 - Automatique")
        mode_association_combo = ttk.Combobox(mainframe, textvariable=self.mode_association_var,
                                              values=["0 - Automatique", "1 - Manuel via fiches"])
        mode_association_combo.grid(row=3, column=1, sticky=tk.W)

        ttk.Label(mainframe, text="Nom Fichier Sauvegarde").grid(row=4, column=0, sticky=tk.W)
        self.nom_fichier_sauvegarde_entry = ttk.Entry(mainframe)
        self.nom_fichier_sauvegarde_entry.grid(row=4, column=1, sticky=tk.W)

        ttk.Label(mainframe, text="Optionnels").grid(row=5, column=0, sticky=tk.W)

        self.create_subframe_with_entries("ID Dossier PNJs", mainframe, self.id_dossier_pnjs_entries, 6)
        self.create_subframe_with_entries("ID Dossier Evenements", mainframe, self.id_dossier_evenements_entries, 7)
        self.create_subframe_with_entries("ID Dossier Objets", mainframe, self.id_dossier_objets_entries, 8)
        self.create_subframe_with_entries("ID Factions", mainframe, self.id_factions_entries, 9)

        ttk.Label(mainframe, text="Date GN").grid(row=10, column=0, sticky=tk.W)
        self.date_gn_entry = ttk.Entry(mainframe)
        self.date_gn_entry.grid(row=10, column=1, sticky=tk.W)

        create_button = ttk.Button(mainframe, text="Créer fichier .ini", command=self.create_ini_file)
        create_button.grid(row=11, column=0, sticky=tk.E)

        cancel_button = ttk.Button(mainframe, text="Annuler", command=self.quit)
        cancel_button.grid(row=11, column=1, sticky=tk.W)

    def create_subframe_with_entries(self, label_text, frame, entry_list, row):
        subframe = ttk.Frame(frame)
        subframe.grid(row=row, column=0, columnspan=2, sticky=tk.W)

        label = ttk.Label(subframe, text=label_text)
        label.pack(side=tk.LEFT)
        add_button = ttk.Button(subframe, text="+", command=lambda: self.add_entry_with_suffix(subframe, entry_list))
        add_button.pack(side=tk.RIGHT)
        entry = ttk.Entry(subframe)
        entry.pack(side=tk.RIGHT)

        suffix_entry = ttk.Entry(subframe, width=5)
        suffix_entry.pack(side=tk.RIGHT)

        entry_list.append((entry, suffix_entry))

    def add_entry_with_suffix(self, frame, entry_list):
        entry = ttk.Entry(frame)
        entry.pack(side=tk.BOTTOM)

        suffix_entry = ttk.Entry(frame, width=5)
        suffix_entry.pack(side=tk.BOTTOM)

        entry_list.append((entry, suffix_entry))

    def create_ini_file(self):
        file_name = filedialog.asksaveasfilename(defaultextension=".ini",
                                                 filetypes=[("INI files", "*.ini"), ("All files", "*.*")])

        if file_name:
            with open(file_name, "w") as file:
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

                file.write(f"mode_association = {self.mode_association_var.get()}\n")
                file.write(f"nom_fichier_sauvegarde = {self.nom_fichier_sauvegarde_entry.get()}\n")

                file.write("[Optionnels]\n")

                for i, (entry, suffix_entry) in enumerate(self.id_dossier_pnjs_entries, start=1):
                    if i == 1:
                        key = "id_dossier_pnjs"
                    else:
                        key = f"id_dossier_pnjs_{suffix_entry.get()}"
                    file.write(f"{key} = {entry.get()}\n")

                for i, (entry, suffix_entry) in enumerate(self.id_dossier_evenements_entries, start=1):
                    if i == 1:
                        key = "id_dossier_evenements"
                    else:
                        key = f"id_dossier_evenements_{suffix_entry.get()}"
                    file.write(f"{key} = {entry.get()}\n")

                for i, (entry, suffix_entry) in enumerate(self.id_dossier_objets_entries, start=1):
                    if i == 1:
                        key = "id_dossier_objets"
                    else:
                        key = f"id_dossier_objets_{suffix_entry.get()}"
                    file.write(f"{key} = {entry.get()}\n")

                for i, (entry, suffix_entry) in enumerate(self.id_factions_entries, start=1):
                    if i == 1:
                        key = "id_factions"
                    else:
                        key = f"id_factions_{suffix_entry.get()}"
                    file.write(f"{key} = {entry.get()}\n")

                file.write(f"date_gn = {self.date_gn_entry.get()}\n")

            self.quit()

if __name__ == '__main__':
    app = GNConfigurator()
    app.mainloop()


