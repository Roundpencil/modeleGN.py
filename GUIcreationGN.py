import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class GNConfigurator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.mode_association_var = tk.StringVar()
        self.title("GN Configurator")
        self.geometry("600x400")

        self.id_dossier_intrigues_entries = []
        self.id_dossier_pjs_entries = []
        self.id_dossier_evenements_entries = []
        self.id_dossier_objets_entries = []
        self.row_intrigue = 100
        self.row_optionnels = 200
        self.row_pj = 201
        self.row_evenement = 300
        self.row_boutons = 400
        self.row_objets = 500
        self.row_factions = 501
        self.row_date = 502


        self.taille_label = 20
        self.taille_entry = 30

        self.create_widgets()

    def create_widgets(self):
        mainframe = ttk.Frame(self)
        mainframe.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(mainframe, text="Essentiels").grid(row=0, column=0, sticky=tk.W)

        self.create_subframe_with_entries("ID Dossier Intrigues", mainframe, self.id_dossier_intrigues_entries, self.row_intrigue)

        ttk.Label(mainframe, text="Mode Association").grid(row=3, column=0, sticky=tk.W)
        self.mode_association_var.set("0 - Automatique")
        mode_association_combo = ttk.Combobox(mainframe, textvariable=self.mode_association_var,
                                              values=["0 - Automatique", "1 - Manuel via fiches"])
        mode_association_combo.grid(row=3, column=1, sticky=tk.W)

        ttk.Label(mainframe, text="Nom Fichier Sauvegarde").grid(row=4, column=0, sticky=tk.W)
        self.nom_fichier_sauvegarde_entry = ttk.Entry(mainframe)
        self.nom_fichier_sauvegarde_entry.grid(row=4, column=1, sticky=tk.W)

        ttk.Label(mainframe, text="Optionnels").grid(row=self.row_optionnels, column=0, sticky=tk.W)


        self.create_subframe_with_entries("ID Dossier PJs", mainframe, self.id_dossier_pjs_entries, self.row_pj)
        self.create_subframe_with_entries("ID Dossier Evenements", mainframe, self.id_dossier_evenements_entries, self.row_evenement)
        self.create_subframe_with_entries("ID Dossier Objets", mainframe, self.id_dossier_objets_entries, self.row_objets)

        ttk.Label(mainframe, text="Date GN").grid(row=self.row_date, column=0, sticky=tk.W)
        self.date_gn_entry = ttk.Entry(mainframe)
        self.date_gn_entry.grid(row=self.row_date, column=1, sticky=tk.W)


        create_button = ttk.Button(mainframe, text="Créer fichier .ini", command=self.create_ini_file)
        create_button.grid(row=self.row_boutons, column=0, sticky=tk.E)

        cancel_button = ttk.Button(mainframe, text="Annuler", command=self.quit)
        cancel_button.grid(row=self.row_boutons, column=1, sticky=tk.W)

#todo : ajouter fichier pj_pnj
    #todo : ajouter id factions
    #todo : ajuster les lignes et colonnes
    #todo : ajouter une case à cocher si choix d'une date
    #todo : vérifier quand on fait le fichier de config que si un champ est vide on n'en fait rien

    def create_subframe_with_entries(self, label_text, frame, entry_list, row):
        subframe = ttk.Frame(frame)
        subframe.grid(row=row, column=0, columnspan=2, sticky=tk.W)

        label = ttk.Label(subframe, text=label_text, width=self.taille_label)
        label.grid(row=0, column=0, sticky=tk.W)

        label = ttk.Label(subframe, text="Nom", width=self.taille_entry)
        label.grid(row=0, column=1, sticky=tk.W)

        label = ttk.Label(subframe, text="ID Google Drive", width=self.taille_entry)
        label.grid(row=0, column=2, sticky=tk.W)

        add_button = ttk.Button(subframe, text="+", command=lambda: self.add_entry_with_suffix(subframe, entry_list))
        add_button.grid(row=0, column=4, sticky=tk.E)

        remove_button = ttk.Button(subframe, text="-", command=lambda: self.remove_entry(entry_list))
        remove_button.grid(row=0, column=3, sticky=tk.E)

        self.add_entry_with_suffix(subframe, entry_list)

    def add_entry_with_suffix(self, frame, entry_list):
        max_row = max_row = max([slave.grid_info()["row"] for slave in frame.grid_slaves()] + [0])

        entry_frame = ttk.Frame(frame)
        entry_frame.grid(row=max_row+1, column=1, columnspan=2, sticky=tk.EW)

        # entry_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        entry = ttk.Entry(entry_frame, width=self.taille_entry)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        suffix_entry = ttk.Entry(entry_frame, width=self.taille_entry)
        suffix_entry.pack(side=tk.LEFT)

        entry_list.append((entry, suffix_entry))

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