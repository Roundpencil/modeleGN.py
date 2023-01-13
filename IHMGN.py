import tkinter as tk

# Variable globale pour stocker les valeurs des paramètres
settings_values = {}

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Paramètres")

    # Champ de texte pour entrer un nom
    name_label = tk.Label(settings_window, text="Nom")
    name_label.pack()
    name_entry = tk.Entry(settings_window)
    name_entry.pack()

    # Bouton radio pour choisir le genre
    gender_label = tk.Label(settings_window, text="Genre")
    gender_label.pack()
    gender_var = tk.StringVar()
    male_radio = tk.Radiobutton(settings_window, text="Homme", variable=gender_var, value="homme")
    male_radio.pack()
    female_radio = tk.Radiobutton(settings_window, text="Femme", variable=gender_var, value="femme")
    female_radio.pack()

    # Bouton pour sauvegarder les paramètres
    save_button = tk.Button(settings_window, text="OK", command=lambda: save_settings(settings_window))
    save_button.pack()
    cancel_button= tk.Button(settings_window, text="Annuler", command=lambda: cancel_settings(settings_window))
    cancel_button.pack()

    def save_settings(settings_window):
        # Récupération des valeurs des widgets
        settings_values["name"] = name_entry.get()
        settings_values["gender"] = gender_var.get()
        # Fermeture de la fenêtre
        settings_window.destroy()
        return settings_values

    def cancel_settings(settings_window):
        settings_window.destroy()
        return None


def open_new_gn():
    new_gn_window = tk.Toplevel(root)
    new_gn_window.title("Créer nouveau GN")

    # Champ de texte pour entrer le nom du nouveau GN
    gn_name_label = tk.Label(new_gn_window, text="Nom du GN")
    gn_name_label.pack()
    gn_name_entry = tk.Entry(new_gn_window)
    gn_name_entry.pack()

    # Bouton radio pour choisir le nombre de joueurs
    players_label = tk.Label(new_gn_window, text="Nombre de joueurs")
    players_label.pack()
    players_var = tk.StringVar()
    few_players_radiobutton = tk.Radiobutton(new_gn_window, text="Peu", variable=players_var, value="peu")
    few_players_radiobutton.pack()
    many_players_radiobutton = tk.Radiobutton(new_gn_window, text="Beaucoup", variable=players_var, value="beaucoup")
    many_players_radiobutton.pack()

    # Bouton pour créer le nouveau GN
    create_button = tk.Button(new_gn_window, text="Créer", command=create_gn)
    create_button.pack()


def lire_intrigues():
    # code pour lire les intrigues
    message_text.insert(tk.END, "lire_intrigues\n")

def lire_persos():
    # code pour lire les persos
    message_text.insert(tk.END, "lire_persos\n")

def forcer_ajout_pjs():
    # code pour forcer l'ajout des PJs
    message_text.insert(tk.END, "forcer_ajout_pjs\n")

def forcer_ajout_PNJs():
    # code pour forcer l'ajout des PNJs
    message_text.insert(tk.END, "forcer_ajout_PNJs\n")

def generer_liste_PNJs_uniques():
    # code pour générer une liste de PNJs uniques
    message_text.insert(tk.END, "generer_liste_PNJs_uniques\n")

def generer_squelette():
    # code pour générer les squelette
    message_text.insert(tk.END, "generer_squelette\n")

def generer_recap_soucis():
    # code pour générer un récap des soucis
    message_text.insert(tk.END, "generer_recap_soucis\n")

def generer_changelog_3j():
    # code pour générer un changelog à 3j
    message_text.insert(tk.END, "generer_changelog_3j\n")

def generer_changelog_4j():
    # code pour générer un changelog à 4j
    message_text.insert(tk.END, "generer_changelog_4j\n")

root = tk.Tk()
root.title("Mon programme")

# Ajout d'une zone de message
message_frame = tk.Frame(root)
message_frame.pack()

message_text = tk.Text(message_frame, height=10, width=50)
message_text.pack()

# Ajout des boutons dans une grille
button_frame = tk.Frame(root)
button_frame.pack()

# Bouton paramètres
settings_button = tk.Button(button_frame, text="Paramètres", command=open_settings)
settings_button.config(width=20)
settings_button.grid(row=0, column=0)

# Bouton Créer nouveau GN
new_gn_button = tk.Button(button_frame, text="Créer nouveau GN", command=open_new_gn)
new_gn_button.config(width=20)
new_gn_button.grid(row=0, column=1)

# Bouton lire les intrigues
intrigues_button = tk.Button(button_frame, text="Lire les intrigues", command=lire_intrigues)
intrigues_button.config(width=20)
intrigues_button.grid(row=1, column=0)

# Bouton lire les persos
persos_button = tk.Button(button_frame, text="Lire les persos", command=lire_persos)
persos_button.config(width=20)
persos_button.grid(row=1, column=1)

# Bouton forcer l'ajout des PJs
ajout_pjs_button = tk.Button(button_frame, text="Forcer l'ajout des PJs", command=forcer_ajout_pjs)
ajout_pjs_button.config(width=20)
ajout_pjs_button.grid(row=2, column=0)

# Bouton forcer l'ajout des PNJs
ajout_pnjs_button = tk.Button(button_frame, text="Forcer l'ajout des PNJs", command=forcer_ajout_PNJs)
ajout_pnjs_button.config(width=20)
ajout_pnjs_button.grid(row=2, column=1)

# Bouton générer liste PNJs uniques
liste_pnjs_button = tk.Button(button_frame, text="Générer liste PNJs uniques", command=generer_liste_PNJs_uniques)
liste_pnjs_button.config(width=20)
liste_pnjs_button.grid(row=3, column=0)

# Bouton générer les squelette
squelette_button = tk.Button(button_frame, text="Générer les squelette", command=generer_squelette)
squelette_button.config(width=20)
squelette_button.grid(row=3, column=1)

# Bouton générer un récap des soucis
recap_soucis_button = tk.Button(button_frame, text="Générer un récap des soucis", command=generer_recap_soucis)
recap_soucis_button.config(width=20)
recap_soucis_button.grid(row=4, column=0)

# Bouton générer un changelog à 3j
changelog_3j_button = tk.Button(button_frame, text="Générer un changelog à 3j", command=generer_changelog_3j)
changelog_3j_button.config(width=20)
changelog_3j_button.grid(row=4, column=1)

# Bouton générer un changelog à 4j
changelog_4j_button = tk.Button(button_frame, text="Générer un changelog à 4j", command=generer_changelog_4j)
changelog_4j_button.config(width=20)
changelog_4j_button.grid(row=5, column=0)

root.mainloop()


