import configparser
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from IHM_lib import *
from module_photos import *


### structure du fichier ini attendu :
# [Sommaire Module Photos]
# TEST = civils
# WOOP = Zooooooo
#
# [Module Photos - test]
# fichier_photos_entry = 1pdqZdiKec0alZNU5xUtcFUBaZpNH2v44ueQFY4S3Mxs
# dossier_photo_entry = 1Y4ONHyZtVkzAuo4EqbubZSrh8hjbJy_O
# input_entry = 1sApU23J6e4lFZ0OmDtghq40T1Iw5vMTY
# output_entry = 1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn
#
# [Module Photos - woop]
# fichier_photos_entry = fichier photos 2
# dossier_photo_entry = dossier photos 2
# input_entry = dossier inputs 2
# output_entry = dossier sortie 2


class GUIPhotos(ttk.Frame):
    def __init__(self, parent, api_drive, api_doc, api_sheets):
        super().__init__(parent)
        self.api_sheets = api_sheets
        self.dico_nom_id = {}
        self.configparser = configparser.ConfigParser()
        photo_window = self
        photo_window.winfo_toplevel().title("Module Photo")
        photo_window.grid_propagate(True)

        # ajout d'un labelframe pour la partie "insérer photos"
        inserphotos_labelframe = ttk.Labelframe(photo_window, text="Insérer des photos dans des fiches de personnages",
                                                width=700, name='inserphotos_labelframe')
        inserphotos_labelframe.grid(row=50, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))

        load_button = ttk.Button(inserphotos_labelframe, text="Charger fichier ini",
                                 command=lambda: action_bouton_charger(self))
        load_button.grid(row=1, column=0, columnspan=4, sticky='e', padx=(10, 10))

        # ajout d'un dropdown menu pour selectionner la configuration pré-enregistrée
        dropdown_label = ttk.Label(inserphotos_labelframe,
                                   text="réglage pré-enregistré dans le fichier de configuration : ")
        dropdown_label.grid(row=4, column=0, columnspan=2, sticky='w')

        # Create a StringVar to hold the selected value
        self.dropdown_selected_option = tk.StringVar()

        # Create the dropdown menu
        self.dropdown = ttk.Combobox(inserphotos_labelframe, textvariable=self.dropdown_selected_option)

        # Bind the selection event to the on_select function
        self.dropdown.bind("<<ComboboxSelected>>", lambda event: on_select(event, self.configparser, self,
                                                                           self.dropdown_selected_option.get()))
        self.dropdown.grid(row=4, column=2, columnspan=1, sticky='w', padx=(10, 10))

        rename_dropdown_button = ttk.Button(inserphotos_labelframe, text="\u270e",
                                            command=lambda: pop_up_renommer(self))
        rename_dropdown_button.grid(row=4, column=3, columnspan=1, sticky='w', padx=(10, 10))

        del_dropdown_button = ttk.Button(inserphotos_labelframe, text="\u274c",
                                         command=lambda: on_delete_click(self))
        del_dropdown_button.grid(row=4, column=4, columnspan=1, sticky='w', padx=(10, 10))

        add_dropdown_button = ttk.Button(inserphotos_labelframe, text="\u2795",
                                         command=lambda: on_add_click(self))
        add_dropdown_button.grid(row=4, column=5, columnspan=1, sticky='w', padx=(10, 10))

        # todo : refaire focntion d'enregistrement
        # todo : quand on a changé au moins un champ ou un onglet de dropdown et qu'on change de dropdown,
        #  demander si volonté d'enregistrer changement dans la configuration en cours
        #  - si oui confirmer, et rappeler d'enregistrer le fichier ini une fois toutes les modifications faites
        # todo : vérifier dans renommer / ajouter que le nom n'est pas déjà présent !!!

        current_file_label = ttk.Label(inserphotos_labelframe, text="Fichier avec référence photos / noms persos")
        current_file_label.grid(row=5, column=0, columnspan=2, sticky='w')
        self.fichier_photos_entry = GidEntry(inserphotos_labelframe, width=50)
        self.fichier_photos_entry.grid(column=2, row=5, columnspan=4, padx=(10, 10))

        # ajout d'un dropdown pour les onglets
        dropdown_onglet_label = ttk.Label(inserphotos_labelframe,
                                          text="Choix d l'onglet dans les fichier")
        dropdown_onglet_label.grid(row=6, column=0, columnspan=4, sticky='w')

        self.dropdown_onglet_selected_option = tk.StringVar()
        # Create the dropdown menu
        self.dropdown_onglet = ttk.Combobox(inserphotos_labelframe, textvariable=self.dropdown_onglet_selected_option)
        self.dropdown_onglet.grid(row=6, column=2, columnspan=1, sticky='w', padx=(10, 10))

        refresh_onglet_button = ttk.Button(inserphotos_labelframe, text="\u267B",
                                           command=lambda: maj_dropdown_onglets(self))
        refresh_onglet_button.grid(row=6, column=3, columnspan=1, sticky='e', padx=(10, 10))

        dossier_photo_labels = ttk.Label(inserphotos_labelframe, text="Dossier contenant les photos")
        dossier_photo_labels.grid(row=10, column=0, columnspan=2, sticky='w')
        self.dossier_photo_entry = GidEntry(inserphotos_labelframe, width=50)
        self.dossier_photo_entry.grid(column=2, row=10, columnspan=2, padx=(10, 10))

        output_labels = ttk.Label(inserphotos_labelframe, text="Dossier où créer le fichier de sortie")
        output_labels.grid(row=20, column=0, columnspan=2, sticky='w')
        self.output_entry = GidEntry(inserphotos_labelframe, width=50)
        self.output_entry.grid(column=2, row=20, columnspan=4, padx=(10, 10))

        input_labels = ttk.Label(inserphotos_labelframe, text="Dossier où lire les fiches à enrichir ")
        input_labels.grid(row=30, column=0, columnspan=2, sticky='w')
        self.input_entry = GidEntry(inserphotos_labelframe, width=50)
        self.input_entry.grid(column=2, row=30, columnspan=2, padx=(10, 10))

        offset_label = ttk.Label(inserphotos_labelframe, text="Décalage (si nécessaire)")
        offset_label.grid(row=40, column=0, columnspan=1, sticky='w')
        self.offset_entry = ttk.Entry(inserphotos_labelframe, width=15)
        self.offset_entry.grid(column=1, row=40, columnspan=1, padx=(10, 10))

        ok_button = ttk.Button(inserphotos_labelframe, text="OK",
                               command=lambda: copier_dossier_et_enrichir_photos(
                                   api_doc=api_doc,
                                   api_drive=api_drive,
                                   api_sheets=self.api_sheets,
                                   folder_id=self.dossier_photo_entry.get(),
                                   offset=int(self.offset_entry.get()),
                                   dossier_sources_fiches=[self.input_entry.get()],
                                   racine_sortie=self.output_entry.get(),
                                   nom_onglet=self.dropdown_onglet.get(),
                                   sheet_id=self.fichier_photos_entry.get()))
        ok_button.grid(row=40, column=30, columnspan=1, sticky='e', padx=(10, 10))

        save_button = ttk.Button(inserphotos_labelframe, text="Sauver fichier ini",
                                 command=lambda: sauver_fichier_ini_photos(self))
        save_button.grid(row=40, column=20, columnspan=1, sticky='e', padx=(10, 10))

    def set_configparser(self, config_parser):
        self.configparser = config_parser

    def set_dico_nom_id(self, dico_nom_id):
        self.dico_nom_id = dico_nom_id

    def get_apisheets(self):
        return self.api_sheets

    def get_configparser(self):
        return self.configparser

    def get_dico_nom_id(self):
        return self.dico_nom_id


def on_select(event, config_parser, guiphoto, nom, verbal=False):
    field = guiphoto.dico_nom_id[nom]
    if verbal:
        print(f"nom : {nom} - field : {field}")
    config_2_fields(config_parser, guiphoto, field)


def sauver_fichier_ini_photos(guiphoto: GUIPhotos):
    # todo : réécrire cette fcontion pour coller à la structure sommaire _ ids psécifiques (cf intro)
    # bien noter que les noms sont enregistrés en minuscules

    # Open a file dialog to let the user select an existing file or write a new one
    ini_file_name = filedialog.asksaveasfilename(
        defaultextension=".ini",
        filetypes=[("INI files", "*.ini"), ("All files", "*.*")],
        title="Select or create an INI file"
    )

    # Check if a file was selected
    if ini_file_name:
        # Create a config parser object
        config = configparser.ConfigParser()

        # Check if the file exists
        if os.path.exists(ini_file_name):
            # Read the existing file
            config.read(ini_file_name)

        # Check if 'Settings' section exists, if not, add it
        if not config.has_section('Module Photos'):
            config.add_section('Module Photos')

        # Set the parameters in the section
        config.set('Module Photos', 'fichier_photos_entry', guiphoto.fichier_photos_entry.get())
        config.set('Module Photos', 'dossier_photo_entry', guiphoto.dossier_photo_entry.get())
        config.set('Module Photos', 'input_entry', guiphoto.input_entry.get())
        config.set('Module Photos', 'output_entry', guiphoto.output_entry.get())

        # Write the parameters to the ini file
        with open(ini_file_name, 'w') as configfile:
            config.write(configfile)

        print(f"Settings saved to {ini_file_name}")
    else:
        print("No file selected")


def action_bouton_charger(gui_photo: GUIPhotos):
    if not (config_parser := charger_fichier_config()):
        return -1

    gui_photo.set_configparser(config_parser)

    upgrader_valeurs_dropdown(gui_photo)

    return 0


def charger_fichier_config():
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers INI", "*.ini")])

    if not file_path:
        messagebox.showerror("Erreur", "Aucun fichier sélectionné")
        return

    config_parser = configparser.ConfigParser()

    try:
        config_parser.read(file_path)
        return config_parser
    except configparser.ParsingError as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du fichier .ini :\n{e}")
        return None


def upgrader_valeurs_dropdown(gui_photo: GUIPhotos):
    config_parser = gui_photo.get_configparser()
    entrees = config_parser.items('Sommaire Module Photos')

    dico_nom_id = {nom_a_afficher: code for code, nom_a_afficher in entrees}
    tous_les_noms = list(dico_nom_id.keys())
    gui_photo.dropdown['values'] = tous_les_noms
    if len(tous_les_noms):
        gui_photo.dropdown_selected_option.set(tous_les_noms[0])

    config_2_fields(config_parser=config_parser, gui_photo=gui_photo, field=dico_nom_id[tous_les_noms[0]])

    gui_photo.set_dico_nom_id(dico_nom_id)
    return dico_nom_id


def config_2_fields(config_parser: configparser.ConfigParser, gui_photo: GUIPhotos, field: str):
    field = field.lower()

    gui_photo.fichier_photos_entry.delete(0, 'end')
    gui_photo.dossier_photo_entry.delete(0, 'end')
    gui_photo.input_entry.delete(0, 'end')
    gui_photo.output_entry.delete(0, 'end')
    gui_photo.offset_entry.delete(0, 'end')

    gui_photo.fichier_photos_entry.insert(0, config_parser.get(f"Module Photos - {field}", 'fichier_photos_entry',
                                                               fallback=""))
    valeur_dropdown_onglet = config_parser.get(f"Module Photos - {field}", 'onglet',
                                               fallback="")
    maj_dropdown_onglets(gui_photo, valeur_dropdown_onglet)
    gui_photo.dossier_photo_entry.insert(0, config_parser.get(f"Module Photos - {field}", 'dossier_photo_entry',
                                                              fallback=""))
    gui_photo.input_entry.insert(0, config_parser.get(f"Module Photos - {field}", 'input_entry', fallback=""))
    gui_photo.output_entry.insert(0, config_parser.get(f"Module Photos - {field}", 'output_entry', fallback=""))
    gui_photo.offset_entry.insert(0, config_parser.get(f"Module Photos - {field}", 'offset', fallback=0))

    valeur_dropdown = config_parser.get(f"Sommaire Module Photos", field)
    gui_photo.dropdown.set(valeur_dropdown)


def maj_dropdown_onglets(gui_photos: GUIPhotos, valeur=None):
    current_valeur = gui_photos.dropdown_onglet_selected_option.get()
    try:
        # Call the Sheets API to get the spreadsheet metadata
        api_sheets = gui_photos.get_apisheets()
        sheet_id = gui_photos.fichier_photos_entry.get()
        spreadsheet = api_sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()

        # Extract the sheet names
        sheet_names = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
    except Exception as e:
        sheet_names = []

    gui_photos.dropdown_onglet['values'] = sheet_names
    if valeur and len(sheet_names):
        gui_photos.dropdown_onglet_selected_option.set(valeur)
    elif current_valeur in sheet_names:
        gui_photos.dropdown_onglet_selected_option.set(current_valeur)
    elif len(sheet_names):
        gui_photos.dropdown_onglet_selected_option.set(sheet_names[0])


def pop_up_renommer(gui_photo: GUIPhotos):
    ancien_nom = gui_photo.dropdown.get()

    # Fonction appelée lors du clic sur le bouton pour afficher la pop-up
    def on_confirm():
        # Récupération du texte entré par l'utilisateur
        result = entry.get()
        popup.destroy()
        # Affichage du résultat dans la console pour l'exemple
        print("Valeur confirmée :", result)
        nouveau_nom = result
        config_parser = gui_photo.get_configparser()
        dico_nom_id = gui_photo.get_dico_nom_id()
        clef = dico_nom_id[ancien_nom]
        config_parser.set("Sommaire Module Photos", clef, nouveau_nom)
        upgrader_valeurs_dropdown(gui_photo)
        config_2_fields(config_parser, gui_photo, clef)

    def on_cancel():
        # Fermeture de la pop-up et retour de None
        popup.destroy()
        # Affichage de None dans la console pour l'exemple
        print("Action annulée, retour de None")

    # Création de la pop-up
    popup = tk.Toplevel(gui_photo)
    popup.title("Renommer la configuration pré-enregistrée")

    # Message d'instruction
    label = tk.Label(popup, text="Entrez une nouvelle valeur :")
    label.pack(pady=10)

    # Champ de texte avec valeur par défaut
    entry = tk.Entry(popup, width=40)
    entry.insert(0, ancien_nom)
    entry.pack(pady=5)

    # Boutons Confirmer et Annuler
    button_frame = tk.Frame(popup)
    button_frame.pack(pady=10)

    confirm_button = tk.Button(button_frame, text="Confirmer", command=on_confirm)
    confirm_button.pack(side="left", padx=5)

    cancel_button = tk.Button(button_frame, text="Annuler", command=on_cancel)
    cancel_button.pack(side="right", padx=5)


def on_delete_click(gui_photo: GUIPhotos):
    # Afficher une boîte de dialogue pour confirmer la suppression
    response = messagebox.askyesno("Confirmation de suppression",
                                   "Voulez-vous vraiment supprimer ce réglage pré-enregistré?")
    if response:  # Si l'utilisateur clique sur "Oui"
        config = gui_photo.get_configparser()
        wording_to_remove = gui_photo.dropdown.get()
        clef_to_remove = gui_photo.get_dico_nom_id()[wording_to_remove]
        config.remove_option("Sommaire Module Photos", clef_to_remove)
        if config.has_section(f"Module Photos - {clef_to_remove}"):
            config.remove_section(f"Module Photos - {clef_to_remove}")
        upgrader_valeurs_dropdown(gui_photo)


# def pop_up_renommer(gui_photo: GUIPhotos):
#     ancien_nom = gui_photo.dropdown.get()
# 
#     # Fonction appelée lors du clic sur le bouton pour afficher la pop-up
#     def on_confirm():
#         # Récupération du texte entré par l'utilisateur
#         result = entry.get()
#         popup.destroy()
#         # Affichage du résultat dans la console pour l'exemple
#         print("Valeur confirmée :", result)
#         nouveau_nom = result
#         config_parser = gui_photo.get_configparser()
#         dico_nom_id = gui_photo.get_dico_nom_id()
#         clef = dico_nom_id[ancien_nom]
#         config_parser.set("Sommaire Module Photos", clef, nouveau_nom)
#         upgrader_valeurs_dropdown(gui_photo)
#         config_2_fields(config_parser, gui_photo, clef)
# 
#     def on_cancel():
#         # Fermeture de la pop-up et retour de None
#         popup.destroy()
#         # Affichage de None dans la console pour l'exemple
#         print("Action annulée, retour de None")
# 
#     # Création de la pop-up
#     popup = tk.Toplevel(gui_photo)
#     popup.title("Renommer la configuration pré-enregistrée")
# 
#     # Message d'instruction
#     label = tk.Label(popup, text="Entrez une nouvelle valeur :")
#     label.pack(pady=10)
# 
#     # Champ de texte avec valeur par défaut
#     entry = tk.Entry(popup, width=40)
#     entry.insert(0, ancien_nom)
#     entry.pack(pady=5)
# 
#     # Boutons Confirmer et Annuler
#     button_frame = tk.Frame(popup)
#     button_frame.pack(pady=10)
# 
#     confirm_button = tk.Button(button_frame, text="Confirmer", command=on_confirm)
#     confirm_button.pack(side="left", padx=5)
# 
#     cancel_button = tk.Button(button_frame, text="Annuler", command=on_cancel)
#     cancel_button.pack(side="right", padx=5)


def on_add_click(gui_photo: GUIPhotos):
    # Fonction appelée lors du clic sur le bouton pour afficher la pop-up
    def on_confirm():
        # Récupération du texte entré par l'utilisateur
        result = entry.get()
        popup.destroy()
        # Affichage du résultat dans la console pour l'exemple
        print("valeur ajoutée :", result)
        nouveau_nom = result
        config_parser = gui_photo.get_configparser()

        config_parser.set("Sommaire Module Photos", nouveau_nom, nouveau_nom)
        config_parser.set("Sommaire Module Photos", nouveau_nom, nouveau_nom)

        upgrader_valeurs_dropdown(gui_photo)
        config_2_fields(config_parser, gui_photo, nouveau_nom)

    def on_cancel():
        # Fermeture de la pop-up et retour de None
        popup.destroy()
        # Affichage de None dans la console pour l'exemple
        print("Action annulée, retour de None")

    # Création de la pop-up
    popup = tk.Toplevel(gui_photo)
    popup.title("Ajouter une configuration pré-enregistrée")

    # Message d'instruction
    label = tk.Label(popup, text="Entrez une nouvelle valeur :")
    label.pack(pady=10)

    # Champ de texte avec valeur par défaut
    entry = tk.Entry(popup, width=40)
    entry.pack(pady=5)

    # Boutons Confirmer et Annuler
    button_frame = tk.Frame(popup)
    button_frame.pack(pady=10)

    confirm_button = tk.Button(button_frame, text="Confirmer", command=on_confirm)
    confirm_button.pack(side="left", padx=5)

    cancel_button = tk.Button(button_frame, text="Annuler", command=on_cancel)
    cancel_button.pack(side="right", padx=5)
