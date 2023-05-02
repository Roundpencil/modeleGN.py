import configparser
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from tkinter import ttk

import IHM_4_editer_config
import google_io as g_io
import lecteurGoogle

# addresse_fiche_intrigue = "https://docs.google.com/document/d/1TeZ6FQafiHyRAJb61wSI6NKTAXHioSI5RmKkgxkqU10"
# addresse_fiche_perso = "https://docs.google.com/document/d/1ZfbzOmGkbVEPzn_u1h6M6JZBZyMcYKgMcqL55k996uw"
# addresse_fiche_evenement = "https://docs.google.com/document/d/1EkEhr6ZwqbpQIZFJxwYC3nt3QA1Fu3L3OezzgMPgMxg/edit"
# addresse_fiche_objet = "https://docs.google.com/document/d/1zUwBTLSwDDt4Pu5T-_JikkzrUVPj9Cdx5O2_iKPNrnM"
# addresse_fichier_pj_pnj = "https://docs.google.com/spreadsheets/d/1eMcP6yyQOX6RmFzkzFB-9BuOOB7ClnjYDwpnZFX5jpU"
# addresse_fichier_factions = \
#     "https://docs.google.com/document/d/1Y4LjLqmdyyZF7KzOLzufHsj4Ufl2npd-UW5cb_EWwhk/edit?usp=sharing"

addresse_fiche_intrigue = "1TeZ6FQafiHyRAJb61wSI6NKTAXHioSI5RmKkgxkqU10"
addresse_fiche_perso = "1ZfbzOmGkbVEPzn_u1h6M6JZBZyMcYKgMcqL55k996uw"
addresse_fiche_evenement = "1EkEhr6ZwqbpQIZFJxwYC3nt3QA1Fu3L3OezzgMPgMxg"
addresse_fiche_objet = "1zUwBTLSwDDt4Pu5T-_JikkzrUVPj9Cdx5O2_iKPNrnM"
addresse_fichier_pj_pnj = "1eMcP6yyQOX6RmFzkzFB-9BuOOB7ClnjYDwpnZFX5jpU"
addresse_fichier_factions = "1Y4LjLqmdyyZF7KzOLzufHsj4Ufl2npd-UW5cb_EWwhk"

class WizzardGN(ttk.Frame):
    def __init__(self, parent, api_drive):
        super().__init__(parent)
        self.api_drive = api_drive
        self.winfo_toplevel().title("Création d'un nouveau GN...")
        self.grid_propagate(True)
        # self.winfo_toplevel().geometry("665x535")

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
        nom_fichier_sauvegarde_label.grid(column=0, row=10, sticky=tk.W, columnspan=1)
        self.nom_fichier_sauvegarde_entry = tk.Entry(self, width=50)
        self.nom_fichier_sauvegarde_entry.grid(column=1, row=10, columnspan=2, padx=(0, 10))

        # Création fichiers

        # creation_fichiers_label = tk.Label(self, text="Création fichiers:")
        # creation_fichiers_label.grid(column=0, row=20, sticky=tk.W, pady=(10, 3))
        self.creation_fichiers_var = tk.StringVar()
        self.creation_fichiers_var.set(0)
        creation_fichiers_options = [("Saisir des IDs existants pour les dossiers", 0),
                                     ("Créer automatiquement les fichiers dans le dossier : ", 1)]
        for text, value in creation_fichiers_options:
            tk.Radiobutton(self, text=text, variable=self.creation_fichiers_var, value=value,
                           command=self.toggle_creation_fichiers_entry).grid(column=0, row=50 + value, sticky=tk.W,
                                                                             columnspan=2)

        # Entry for Creation fichiers
        self.creation_fichiers_entry = tk.Entry(self, state="normal")
        self.creation_fichiers_entry.grid(column=1, row=52, columnspan=3, sticky=tk.EW, padx=(10,10))
        self.creation_fichiers_entry['state'] = 'disabled'

        # # Mode de saisie des personnages

        # Utiliser un fichier des PJs et des PNJs
        self.utilisation_fichier_pjs_pnjs_var = tk.BooleanVar(value=False)
        utilisation_fichier_pjs_pnjs_checkbox = tk.Checkbutton(self,
                                                               text="Utiliser un fichier des PJs et des PNJs",
                                                               variable=self.utilisation_fichier_pjs_pnjs_var)
        utilisation_fichier_pjs_pnjs_checkbox.grid(column=0, row=30, sticky=tk.W, pady=(10, 3),
                                                   columnspan=2)

        # Utiliser un fichier faction
        self.utilisation_fichier_factions_var = tk.BooleanVar(value=False)
        utilisation_fichier_factions_checkbox = tk.Checkbutton(self, text="Utiliser un fichier factions",
                                                               variable=self.utilisation_fichier_factions_var)
        utilisation_fichier_factions_checkbox.grid(column=0, row=40, sticky=tk.W, pady=(10, 3),
                                                   columnspan=2)

        # Nombre de dossiers Intrigues
        nombre_dossiers_intrigues_label = tk.Label(self, text="Nombre de dossiers Intrigues:")
        nombre_dossiers_intrigues_label.grid(column=0, row=65, sticky=tk.W, pady=(10, 3))
        self.nombre_dossiers_intrigues_spinbox = tk.Spinbox(self, from_=1, to=100, width=5)
        self.nombre_dossiers_intrigues_spinbox.grid(column=1, row=65, pady=(10, 3))

        # Nombre de dossiers Evenements
        nombre_dossiers_evenements_label = tk.Label(self, text="Nombre de dossiers Evenements:")
        nombre_dossiers_evenements_label.grid(column=0, row=70, sticky=tk.W, pady=(10, 3))
        self.nombre_dossiers_evenements_spinbox = tk.Spinbox(self, from_=0, to=100, width=5)
        self.nombre_dossiers_evenements_spinbox.grid(column=1, row=70, pady=(10, 3))

        # Nombre de dossiers Objet
        nombre_dossiers_objet_label = tk.Label(self, text="Nombre de dossiers Objet:")
        nombre_dossiers_objet_label.grid(column=0, row=80, sticky=tk.W, pady=(10, 3))
        self.nombre_dossiers_objet_spinbox = tk.Spinbox(self, from_=0, to=100, width=5)
        self.nombre_dossiers_objet_spinbox.grid(column=1, row=80, pady=(10, 3))

        # Nombre de dossiers PJs
        nombre_dossiers_pjs_label = tk.Label(self, text="Nombre de dossiers PJs:")
        nombre_dossiers_pjs_label.grid(column=0, row=90, sticky=tk.W, pady=(10, 3))
        self.nombre_dossiers_pjs_spinbox = tk.Spinbox(self, from_=0, to=100, width=5)
        self.nombre_dossiers_pjs_spinbox.grid(column=1, row=90, pady=(10, 3))

        # Nombre de dossiers PNJs
        nombre_dossiers_pnjs_label = tk.Label(self, text="Nombre de dossiers PNJs:")
        nombre_dossiers_pnjs_label.grid(column=0, row=100, sticky=tk.W, pady=(10, 3))
        self.nombre_dossiers_pnjs_spinbox = tk.Spinbox(self, from_=0, to=100, width=5)
        self.nombre_dossiers_pnjs_spinbox.grid(column=1, row=100, pady=(10, 3))

        # Date GN en Français (vide si non utilisée) with checkbox
        self.date_gn_checkbox_var = tk.BooleanVar(value=False)

        date_gn_checkbox = tk.Checkbutton(self, text="Date GN en Français (vide si non utilisée):",
                                          variable=self.date_gn_checkbox_var, command=self.toggle_date_gn_entry)
        date_gn_checkbox.grid(column=0, row=110, columnspan=2, sticky=tk.W, pady=(10, 3))
        self.date_gn_entry = tk.Entry(self)
        self.date_gn_entry.grid(column=2, row=110, pady=(10, 3), sticky=tk.W)
        self.date_gn_entry['state'] = 'disabled'

        # OK and Annuler buttons
        ok_button = tk.Button(self, text="Suivant >", command=self.on_ok_click)
        ok_button.grid(column=0, row=120, pady=10)
        # annuler_button = tk.Button(self, text="Annuler", command=self.on_annuler_click)
        # annuler_button.grid(column=1, row=120, pady=10)

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
            self.date_gn_entry.config(state='disabled')

    def on_ok_click(self):
        creer_fichier = self.creation_fichiers_var.get() == '1'
        nom_parent = self.creation_fichiers_entry.get()

        if creer_fichier:
            nom_parent, nom_valide = g_io.extraire_id_google_si_possible(nom_parent)
            if not nom_valide:
                messagebox.showerror("Erreur", "Le nom du dossier spécifié pour créer les fichiers n'est pas valide")
                return

            # vérifier qu'il y a un fichier de sauvegarde >> popup sinon
            # print(f"nom fichier sauvegarde = {self.nom_fichier_sauvegarde_entry.get()} / "
            #       f"{self.nom_fichier_sauvegarde_entry['text']}")
            if len(self.nom_fichier_sauvegarde_entry.get()) == 0:
                messagebox.showerror("Erreur", "Vous avez demandé à ce que tout soit créé automatiquement "
                                               "mais aucun nom de fichier de sauvegarde n'a été fourni")
                return

            # si création d'un fichier, vérifier que le dossier parent existe,
            # sinon pop up d'erreur et on quitte

            ok, erreur = g_io.verifier_acces_fichier(self.api_drive, nom_parent)
            if not ok:
                messagebox.showerror("Erreur", f"Impossible de créer les fichiers \n {erreur}")
                return

        dict_essentiels = {}
        dict_optionnels = {}

        nb_intrigues = int(self.nombre_dossiers_intrigues_spinbox.get())
        # print(f"nib i = {nb_intrigues}")
        for i in range(nb_intrigues):
            if creer_fichier:
                current_dossier = g_io.creer_dossier(self.api_drive, nom_parent, f"Intrigues {i + 1}")
                dict_essentiels[f"id_dossier_intrigues_{i + 1}"] = current_dossier
                g_io.copier_fichier_vers_dossier(self.api_drive, addresse_fiche_intrigue, current_dossier)
            else:
                dict_essentiels[f"id_dossier_intrigues_{i + 1}"] = ""

        if creer_fichier:
            dict_essentiels['dossier_output_squelettes_pjs'] = g_io.creer_dossier(self.api_drive, nom_parent, "Output")
        else:
            dict_essentiels['dossier_output_squelettes_pjs'] = ""
        dict_essentiels['mode_association'] = self.mode_association_var.get()
        dict_essentiels['nom_fichier_sauvegarde'] = self.nom_fichier_sauvegarde_entry.get()

        nb_evenements = int(self.nombre_dossiers_evenements_spinbox.get())
        for i in range(nb_evenements):
            current_dossier = ""
            if creer_fichier:
                current_dossier = g_io.creer_dossier(self.api_drive, nom_parent, f"Evènements {i + 1}")
                g_io.copier_fichier_vers_dossier(self.api_drive, addresse_fiche_evenement, current_dossier)
            dict_optionnels[f"id_dossier_evenements_{i + 1}"] = current_dossier

        nb_objets = int(self.nombre_dossiers_objet_spinbox.get())
        for i in range(nb_objets):
            current_dossier = ""
            if creer_fichier:
                current_dossier = g_io.creer_dossier(self.api_drive, nom_parent, f"Objets {i + 1}")
                g_io.copier_fichier_vers_dossier(self.api_drive, addresse_fiche_objet, current_dossier)
            dict_optionnels[f"id_dossier_objets_{i + 1}"] = current_dossier

        nb_pjs = int(self.nombre_dossiers_pjs_spinbox.get())
        for i in range(nb_pjs):
            current_dossier = ""
            if creer_fichier:
                current_dossier = g_io.creer_dossier(self.api_drive, nom_parent, f"Fiches PJs {i + 1}")
                g_io.copier_fichier_vers_dossier(self.api_drive, addresse_fiche_perso, current_dossier)
            dict_optionnels[f"id_dossier_pjs_{i + 1}"] = current_dossier

        nb_pnjs = int(self.nombre_dossiers_pnjs_spinbox.get())
        for i in range(nb_pnjs):
            current_dossier = ""
            if creer_fichier:
                current_dossier = g_io.creer_dossier(self.api_drive, nom_parent, f"Fiches PNJs {i + 1}")
                g_io.copier_fichier_vers_dossier(self.api_drive, addresse_fiche_perso, current_dossier)
            dict_optionnels[f"id_dossier_pnjs_{i + 1}"] = current_dossier

        if self.utilisation_fichier_factions_var.get():
            id_factions = ""
            if creer_fichier:
                id_factions = g_io.copier_fichier_vers_dossier(self.api_drive, addresse_fichier_factions, nom_parent)
            dict_optionnels["id_factions"] = id_factions

        if self.utilisation_fichier_pjs_pnjs_var.get():
            id_pjpnj = ""
            if creer_fichier:
                id_pjpnj = g_io.copier_fichier_vers_dossier(self.api_drive, addresse_fichier_pj_pnj, nom_parent)
            dict_optionnels["id_pjs_et_pnjs"] = id_pjpnj

        if self.date_gn_checkbox_var.get():
            dict_optionnels["date_gn"] = self.date_gn_entry.get()

        print(dict_essentiels)
        print(dict_optionnels)
        # créer un configparser et mettre les dictionnaires dedans
        config = configparser.ConfigParser()
        config.add_section('Essentiels')
        for param in dict_essentiels:
            config.set("Essentiels", param, dict_essentiels[param])
        config.add_section('Optionnels')
        for param in dict_optionnels:
            config.set("Optionnels", param, dict_optionnels[param])

        if creer_fichier:
            if file_path := filedialog.asksaveasfilename(
                    defaultextension=".ini",
                    filetypes=[("INI files", "*.ini"), ("All files", "*.*")],
                    title="Choisissez un fichier pour enregistrer la configuration",
            ):
                nom_fichier_ini = file_path
                with open(nom_fichier_ini, "w") as config_file:
                    config.write(config_file)
            messagebox.showinfo("Enregistrement réussi", "Le fichier de paramètre a bien été créé et enregistré \n"
                                                         "Les répertoires ont été créés \n"
                                                         "Le fichiers exemple ont été générés"
                                )

        else:
            # ungrid me et mettre à la place un step two, chargé à partir du configparser créé
            self.grid_forget()
            nxt = IHM_4_editer_config.FenetreEditionConfig(self.winfo_toplevel(), api_drive=self.api_drive, config_parser=config)
            nxt.grid(row=0, column=0)

    def on_annuler_click(self):
        # self.destroy()
        self.grid_forget()


if __name__ == "__main__":
    dr, do, sh = lecteurGoogle.creer_lecteurs_google_apis()
    root = tk.Tk()
    wiz = WizzardGN(root, dr)
    wiz.grid(column=0, row=0)
    wiz.mainloop()
