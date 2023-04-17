import tkinter as tk
from tkinter import ttk


def on_ok_click():
    # Collect values from the widgets and create a dictionary
    params = {
        "mode_association": mode_association_var.get(),
        "nom_fichier_sauvegarde": nom_fichier_sauvegarde_entry.get(),
        "creation_fichiers": creation_fichiers_var.get(),
        "mode_saisie_personnages": mode_saisie_personnages_var.get(),
        "utilisation_dossier_evenements": utilisation_dossier_evenements_var.get(),
        "utilisation_fichier_factions": utilisation_fichier_factions_var.get(),
        "date_gn": date_gn_entry.get()
    }
    print(params)
    # Generate file based on the params dictionary
    # ...
    root.destroy()


def on_annuler_click():
    root.destroy()


def display_panel():
    global root, mode_association_var, nom_fichier_sauvegarde_entry, creation_fichiers_var, mode_saisie_personnages_var, utilisation_dossier_evenements_var, utilisation_fichier_factions_var, date_gn_entry

    root = tk.Tk()
    root.title("Paramètres")
    root.geometry("665x535")

    # Mode association
    mode_association_label = tk.Label(root, text="Mode association:")
    mode_association_label.grid(column=0, row=0, sticky=tk.W)
    mode_association_var = tk.StringVar()
    mode_association_var.set("0 - Automatique")
    mode_association_options = ["0 - Automatique", "1 - Manuel via fiches"]
    mode_association_dropdown = ttk.Combobox(root, textvariable=mode_association_var,
                                             values=mode_association_options, state="readonly")
    mode_association_dropdown.grid(column=1, row=0)

    # Nom fichier de sauvegarde
    nom_fichier_sauvegarde_label = tk.Label(root, text="Nom fichier de sauvegarde :")
    nom_fichier_sauvegarde_label.grid(column=0, row=10, sticky=tk.W)
    nom_fichier_sauvegarde_entry = tk.Entry(root, width=50)
    nom_fichier_sauvegarde_entry.grid(column=0, row=11, columnspan=3)

    # Création fichiers
    creation_fichiers_label = tk.Label(root, text="Création fichiers:")
    creation_fichiers_label.grid(column=0, row=20, sticky=tk.W, pady=(10, 3))
    creation_fichiers_var = tk.StringVar()
    creation_fichiers_var.set(0)
    creation_fichiers_options = [("Créer automatiquement les fichiers", 0), ("Saisir des IDs existants", 1)]
    for text, value in creation_fichiers_options:
        tk.Radiobutton(root, text=text, variable=creation_fichiers_var, value=value).grid(column=0 + value, row=30,
                                                                                          sticky=tk.W)

    # Mode de saisie des personnages
    mode_saisie_personnages_label = tk.Label(root, text="Mode de saisie des personnages:")
    mode_saisie_personnages_label.grid(column=0, row=40, sticky=tk.W, pady=(10, 3))
    mode_saisie_personnages_var = tk.StringVar()
    mode_saisie_personnages_var.set(2)
    mode_saisie_personnages_options = [("Via fiches Persos", 0), ("Via liste des PJs et PNJs", 1), ("Les deux", 2)]
    for text, value in mode_saisie_personnages_options:
        tk.Radiobutton(root, text=text, variable=mode_saisie_personnages_var, value=value).grid(column=0 + value,
                                                                                                row=50,
                                                                                                sticky=tk.W)

    # Utilisation d'un dossier évènements
    utilisation_dossier_evenements_var = tk.BooleanVar(value=True)
    utilisation_dossier_evenements_cb = tk.Checkbutton(root, text="Utilisation d'un dossier évènements",
                                                       variable=utilisation_dossier_evenements_var)
    utilisation_dossier_evenements_cb.grid(column=0, row=70, sticky=tk.W, columnspan=2, pady=(10, 3))

    # Utilisation    d    'un fichier Factions
    utilisation_fichier_factions_var = tk.BooleanVar(value=True)
    utilisation_fichier_factions_cb = tk.Checkbutton(root, text="Utilisation d'un fichier Factions",
                                                     variable=utilisation_fichier_factions_var)
    utilisation_fichier_factions_cb.grid(column=0, row=80, sticky=tk.W, columnspan=2, pady=(10, 3))

    # date    GN(vide    si    non    utilisée)
    date_gn_label = tk.Label(root, text="Date GN en Français (vide si non utilisée):")
    date_gn_label.grid(column=0, row=90, sticky=tk.W, pady=(10, 3))
    date_gn_entry = tk.Entry(root)
    date_gn_entry.grid(column=1, row=90, pady=(10, 3))

    # OK and Annuler    buttons
    ok_button = tk.Button(root, text="OK", command=on_ok_click)
    ok_button.grid(column=0, row=100, pady=10)
    annuler_button = tk.Button(root, text="Annuler", command=on_annuler_click)
    annuler_button.grid(column=1, row=100, pady=10)

    root.mainloop()


if __name__ == "__main__":
    display_panel()
