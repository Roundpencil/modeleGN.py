
import tkinter as tk
from tkinter import ttk
import tkinter as tk
from tkinter import ttk

class WizzardGN(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.winfo_toplevel().title("Création d'un nouveau GN...")
        self.winfo_toplevel().geometry("665x535")

        # (previous widget definitions remain the same)
        # Mode association
        mode_association_label = tk.Label(self, text="Mode association:")
        mode_association_label.grid(column=0, row=0, sticky=tk.W)
        self.mode_association_var = tk.StringVar()
        self.mode_association_var.set("0 - Automatique")
        mode_association_options = ["0 - Automatique", "1 - Manuel via fiches"]
        mode_association_dropdown = ttk.Combobox(self, textvariable=self.mode_association_var,
                                                 values=mode_association_options, state="readonly")
        mode_association_dropdown.grid(column=1, row=0)

        # Nom fichier de sauvegarde
        nom_fichier_sauvegarde_label = tk.Label(self, text="Nom fichier de sauvegarde :")
        nom_fichier_sauvegarde_label.grid(column=0, row=10, sticky=tk.W, columnspan=2)
        self.nom_fichier_sauvegarde_entry = tk.Entry(self, width=50)
        self.nom_fichier_sauvegarde_entry.grid(column=2, row=10, columnspan=2)

        # Création fichiers
        # creation_fichiers_label = tk.Label(self, text="Création fichiers:")
        # creation_fichiers_label.grid(column=0, row=20, sticky=tk.W, pady=(10, 3))
        # self.creation_fichiers_var = tk.StringVar()
        # self.creation_fichiers_var.set(0)
        # creation_fichiers_options = [("Créer automatiquement les fichiers", 0), ("Saisir des IDs existants", 1)]
        # for text, value in creation_fichiers_options:
        #     tk.Radiobutton(self, text=text, variable=self.creation_fichiers_var, value=value).grid(column=0 + value, row=30,
        #                                                                                                 sticky=tk.W)

        creation_fichiers_label = tk.Label(self, text="Création fichiers:")
        creation_fichiers_label.grid(column=0, row=20, sticky=tk.W, pady=(10, 3))
        self.creation_fichiers_var = tk.StringVar()
        self.creation_fichiers_var.set(0)
        creation_fichiers_options = [("Saisir des IDs existants", 0),
                                     ("Créer automatiquement les fichiers dans le dossier : ", 1)]
        for text, value in creation_fichiers_options:
            tk.Radiobutton(self, text=text, variable=self.creation_fichiers_var, value=value,
                           command=self.toggle_creation_fichiers_entry).grid(column=0, row=30 + value, sticky=tk.W,
                                                                             columnspan=2)

        # Entry for Creation fichiers
        self.creation_fichiers_entry = tk.Entry(self, state="normal")
        self.creation_fichiers_entry.grid(column=2, row=31, columnspan=2, sticky=tk.EW)
        self.creation_fichiers_entry['state'] = 'disabled'

        # # Mode de saisie des personnages
        # mode_saisie_personnages_label = tk.Label(self, text="Mode de saisie des personnages:")
        # mode_saisie_personnages_label.grid(column=0, row=40, sticky=tk.W, pady=(10, 3))
        # self.mode_saisie_personnages_var = tk.StringVar()
        # self.mode_saisie_personnages_var.set(2)
        # mode_saisie_personnages_options = [("Via fiches Persos", 0), ("Via liste des PJs et PNJs", 1), ("Les deux", 2)]
        # for text, value in mode_saisie_personnages_options:
        #     tk.Radiobutton(self, text=text, variable=self.mode_saisie_personnages_var, value=value).grid(column=0 + value,
        #                                                                                                       row=50,
        #                                                                                                       sticky=tk.W)

        # Utiliser un fichier des PJs et des PNJs
        self.utilisation_fichier_pjs_pnjs_var = tk.BooleanVar(value=False)
        utilisation_fichier_pjs_pnjs_checkbox = tk.Checkbutton(self,
                                                               text="Utiliser un fichier des PJs et des PNJs",
                                                               variable=self.utilisation_fichier_pjs_pnjs_var)
        utilisation_fichier_pjs_pnjs_checkbox.grid(column=0, row=40, sticky=tk.W, pady=(10, 3),
                                                   columnspan=2)

        # Utiliser un fichier faction
        self.utilisation_fichier_factions_var = tk.BooleanVar(value=False)
        utilisation_fichier_factions_checkbox = tk.Checkbutton(self, text="Utiliser un fichier factions",
                                                               variable=self.utilisation_fichier_factions_var)
        utilisation_fichier_factions_checkbox.grid(column=0, row=50, sticky=tk.W, pady=(10, 3),
                                                   columnspan=2)

        # Nombre de dossiers Intrigues
        nombre_dossiers_intrigues_label = tk.Label(self, text="Nombre de dossiers Intrigues:")
        nombre_dossiers_intrigues_label.grid(column=0, row=65, sticky=tk.W, pady=(10, 3))
        nombre_dossiers_intrigues_spinbox = tk.Spinbox(self, from_=1, to=100, width=5)
        nombre_dossiers_intrigues_spinbox.grid(column=1, row=65, pady=(10, 3))

        # Nombre de dossiers Evenements
        nombre_dossiers_evenements_label = tk.Label(self, text="Nombre de dossiers Evenements:")
        nombre_dossiers_evenements_label.grid(column=0, row=70, sticky=tk.W, pady=(10, 3))
        nombre_dossiers_evenements_spinbox = tk.Spinbox(self, from_=0, to=100, width=5)
        nombre_dossiers_evenements_spinbox.grid(column=1, row=70, pady=(10, 3))

        # Nombre de dossiers Objet
        nombre_dossiers_objet_label = tk.Label(self, text="Nombre de dossiers Objet:")
        nombre_dossiers_objet_label.grid(column=0, row=80, sticky=tk.W, pady=(10, 3))
        nombre_dossiers_objet_spinbox = tk.Spinbox(self, from_=0, to=100, width=5)
        nombre_dossiers_objet_spinbox.grid(column=1, row=80, pady=(10, 3))

        # Nombre de dossiers PJs
        nombre_dossiers_pjs_label = tk.Label(self, text="Nombre de dossiers PJs:")
        nombre_dossiers_pjs_label.grid(column=0, row=90, sticky=tk.W, pady=(10, 3))
        nombre_dossiers_pjs_spinbox = tk.Spinbox(self, from_=0, to=100, width=5)
        nombre_dossiers_pjs_spinbox.grid(column=1, row=90, pady=(10, 3))

        # Nombre de dossiers PNJs
        nombre_dossiers_pnjs_label = tk.Label(self, text="Nombre de dossiers PNJs:")
        nombre_dossiers_pnjs_label.grid(column=0, row=100, sticky=tk.W, pady=(10, 3))
        nombre_dossiers_pnjs_spinbox = tk.Spinbox(self, from_=0, to=100, width=5)
        nombre_dossiers_pnjs_spinbox.grid(column=1, row=100, pady=(10, 3))

        # Date GN en Français (vide si non utilisée) with checkbox
        self.date_gn_checkbox_var = tk.BooleanVar(value=False)

        date_gn_checkbox = tk.Checkbutton(self, text="Date GN en Français (vide si non utilisée):",
                                          variable=self.date_gn_checkbox_var, command=self.toggle_date_gn_entry)
        date_gn_checkbox.grid(column=0, row=110, columnspan=2, sticky=tk.W, pady=(10, 3))
        self.date_gn_entry = tk.Entry(self)
        self.date_gn_entry.grid(column=2, row=110, pady=(10, 3), sticky=tk.W)

        # OK and Annuler buttons
        ok_button = tk.Button(self, text="OK", command=self.on_ok_click)
        ok_button.grid(column=0, row=120, pady=10)
        annuler_button = tk.Button(self, text="Annuler", command=self.on_annuler_click)
        annuler_button.grid(column=1, row=120, pady=10)

    def toggle_creation_fichiers_entry(self):
        if self.creation_fichiers_var.get() == "0":
            self.creation_fichiers_entry.config(state='disabled')
        else:
            self.creation_fichiers_entry.config(state='normal')

    def toggle_date_gn_entry(self):
        if self.date_gn_checkbox_var.get():
            # self.date_gn_entry.delete(0, 'end')
            self.date_gn_entry.config(state='normal')
        else:
            self.date_gn_entry.config(state ='disabled')

    def on_ok_click(self):
        # Collect values from the widgets and create a dictionary
        params = {
            "mode_association": self.mode_association_var.get(),
            "nom_fichier_sauvegarde": self.nom_fichier_sauvegarde_entry.get(),
            "creation_fichiers": self.creation_fichiers_var.get(),
            "mode_saisie_personnages": self.mode_saisie_personnages_var.get(),
            "utilisation_dossier_evenements": self.utilisation_dossier_evenements_var.get(),
            "utilisation_fichier_factions": self.utilisation_fichier_factions_var.get(),
            "date_gn": self.date_gn_entry.get()
        }
        print(params)
        # Generate file based on the params dictionary
        # ...
        self.destroy()

    def on_annuler_click(self):
        self.destroy()

#
# class WizzardGN(ttk.Frame):
#     def __init__(self, parent):
#     # global fenetre_wizard, mode_association_var, nom_fichier_sauvegarde_entry, creation_fichiers_var, mode_saisie_personnages_var, utilisation_dossier_evenements_var, utilisation_fichier_factions_var, date_gn_entry
#         super().__init__(parent)
#         fenetre_wizard = self
#         fenetre_wizard.winfo_toplevel().title("Création d'un nouveau GN...")
#         fenetre_wizard.winfo_toplevel().geometry("665x535")
#
#         # (previous widget definitions remain the same)
#         # Mode association
#         mode_association_label = tk.Label(fenetre_wizard, text="Mode association:")
#         mode_association_label.grid(column=0, row=0, sticky=tk.W)
#         mode_association_var = tk.StringVar()
#         mode_association_var.set("0 - Automatique")
#         mode_association_options = ["0 - Automatique", "1 - Manuel via fiches"]
#         mode_association_dropdown = ttk.Combobox(fenetre_wizard, textvariable=mode_association_var,
#                                                  values=mode_association_options, state="readonly")
#         mode_association_dropdown.grid(column=1, row=0)
#
#         # Nom fichier de sauvegarde
#         nom_fichier_sauvegarde_label = tk.Label(fenetre_wizard, text="Nom fichier de sauvegarde :")
#         nom_fichier_sauvegarde_label.grid(column=0, row=10, sticky=tk.W)
#         nom_fichier_sauvegarde_entry = tk.Entry(fenetre_wizard, width=50)
#         nom_fichier_sauvegarde_entry.grid(column=0, row=11, columnspan=3)
#
#         # Création fichiers
#         creation_fichiers_label = tk.Label(fenetre_wizard, text="Création fichiers:")
#         creation_fichiers_label.grid(column=0, row=20, sticky=tk.W, pady=(10, 3))
#         creation_fichiers_var = tk.StringVar()
#         creation_fichiers_var.set(0)
#         creation_fichiers_options = [("Créer automatiquement les fichiers", 0), ("Saisir des IDs existants", 1)]
#         for text, value in creation_fichiers_options:
#             tk.Radiobutton(fenetre_wizard, text=text, variable=creation_fichiers_var, value=value).grid(column=0 + value, row=30,
#                                                                                                         sticky=tk.W)
#
#         # Mode de saisie des personnages
#         mode_saisie_personnages_label = tk.Label(fenetre_wizard, text="Mode de saisie des personnages:")
#         mode_saisie_personnages_label.grid(column=0, row=40, sticky=tk.W, pady=(10, 3))
#         mode_saisie_personnages_var = tk.StringVar()
#         mode_saisie_personnages_var.set(2)
#         mode_saisie_personnages_options = [("Via fiches Persos", 0), ("Via liste des PJs et PNJs", 1), ("Les deux", 2)]
#         for text, value in mode_saisie_personnages_options:
#             tk.Radiobutton(fenetre_wizard, text=text, variable=mode_saisie_personnages_var, value=value).grid(column=0 + value,
#                                                                                                               row=50,
#                                                                                                               sticky=tk.W)
#
#         # Nombre de dossiers Evenements
#         nombre_dossiers_evenements_label = tk.Label(fenetre_wizard, text="Nombre de dossiers Evenements:")
#         nombre_dossiers_evenements_label.grid(column=0, row=70, sticky=tk.W, pady=(10, 3))
#         nombre_dossiers_evenements_spinbox = tk.Spinbox(fenetre_wizard, from_=0, to=100, width=5)
#         nombre_dossiers_evenements_spinbox.grid(column=1, row=70, pady=(10, 3))
#
#         # Nombre de dossiers Objet
#         nombre_dossiers_objet_label = tk.Label(fenetre_wizard, text="Nombre de dossiers Objet:")
#         nombre_dossiers_objet_label.grid(column=0, row=80, sticky=tk.W, pady=(10, 3))
#         nombre_dossiers_objet_spinbox = tk.Spinbox(fenetre_wizard, from_=0, to=100, width=5)
#         nombre_dossiers_objet_spinbox.grid(column=1, row=80, pady=(10, 3))
#
#         # Nombre de dossiers PJs
#         nombre_dossiers_pjs_label = tk.Label(fenetre_wizard, text="Nombre de dossiers PJs:")
#         nombre_dossiers_pjs_label.grid(column=0, row=90, sticky=tk.W, pady=(10, 3))
#         nombre_dossiers_pjs_spinbox = tk.Spinbox(fenetre_wizard, from_=0, to=100, width=5)
#         nombre_dossiers_pjs_spinbox.grid(column=1, row=90, pady=(10, 3))
#
#         # Nombre de dossiers PNJs
#         nombre_dossiers_pnjs_label = tk.Label(fenetre_wizard, text="Nombre de dossiers PNJs:")
#         nombre_dossiers_pnjs_label.grid(column=0, row=100, sticky=tk.W, pady=(10, 3))
#         nombre_dossiers_pnjs_spinbox = tk.Spinbox(fenetre_wizard, from_=0, to=100, width=5)
#         nombre_dossiers_pnjs_spinbox.grid(column=1, row=100, pady=(10, 3))
#
#         # Date GN en Français (vide si non utilisée) with checkbox
#         date_gn_checkbox_var = tk.BooleanVar(value=False)
#
#         date_gn_checkbox = tk.Checkbutton(fenetre_wizard, text="Date GN en Français (vide si non utilisée):",
#                                           variable=date_gn_checkbox_var, command=self.toggle_date_gn_entry)
#         date_gn_checkbox.grid(column=0, row=110, sticky=tk.W, pady=(10, 3))
#         date_gn_entry = tk.Entry(fenetre_wizard)
#         date_gn_entry.grid(column=1, row=110, pady=(10, 3))
#
#         # OK and Annuler buttons
#         ok_button = tk.Button(fenetre_wizard, text="OK", command=on_ok_click)
#         ok_button.grid(column=0, row=120, pady=10)
#         annuler_button = tk.Button(fenetre_wizard, text="Annuler", command=self.on_annuler_click)
#         annuler_button.grid(column=1, row=120, pady=10)
#
#
#     def toggle_date_gn_entry():
#         if date_gn_checkbox_var.get():
#             date_gn_entry.delete(0, 'end')
#             date_gn_entry.config(state ='disabled')
#         else:
#             date_gn_entry.config(state='normal')
#
#
#     def on_ok_click():
#         # Collect values from the widgets and create a dictionary
#         params = {
#             "mode_association": mode_association_var.get(),
#             "nom_fichier_sauvegarde": nom_fichier_sauvegarde_entry.get(),
#             "creation_fichiers": creation_fichiers_var.get(),
#             "mode_saisie_personnages": mode_saisie_personnages_var.get(),
#             "utilisation_dossier_evenements": utilisation_dossier_evenements_var.get(),
#             "utilisation_fichier_factions": utilisation_fichier_factions_var.get(),
#             "date_gn": date_gn_entry.get()
#         }
#         print(params)
#         # Generate file based on the params dictionary
#         # ...
#         fenetre_wizard.destroy()
#
#
#     def on_annuler_click():
#         fenetre_wizard.destroy()
#
#
#
if __name__ == "__main__":
    root = tk.Tk()
    wiz = WizzardGN(root)
    wiz.grid(column=0, row=0)
    wiz.mainloop()


