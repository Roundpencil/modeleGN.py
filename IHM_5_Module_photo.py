import configparser
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font

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
        self.previous_dropdown_field = None

        # Create the dropdown menu
        self.dropdown = ttk.Combobox(inserphotos_labelframe, textvariable=self.dropdown_selected_option)

        # Bind the selection event to the on_select function
        self.dropdown.bind("<<ComboboxSelected>>", lambda event: on_select(self))
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

        # todo : ajouter une focntion qui contrôle que les paramètres sont legit avant de lacer les choses (cf. générer)

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

        self.has_changed_label = ttk.Label(inserphotos_labelframe)
        self.has_changed_label.grid(row=41, column=0, columnspan=4, sticky='nsew')

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

    def set_dropdown_value_from_field(self, field):
        valeur_dropdown = self.configparser.get(f"Sommaire Module Photos", field)
        self.dropdown_selected_option.set(valeur_dropdown)
        self.previous_dropdown_field = field

    def get_previous_dropdown_field(self):
        return self.previous_dropdown_field

    def has_changed(self):
        # Define the font with italic style
        italic_font = font.Font(family="Helvetica", size=12, slant="italic")

        # Update the label's text and font
        self.has_changed_label.config(text="Les réglages prédéfinis ont changé, "
                                           "n'oubliez pas de sauvegarder si vous souhaiter les conserver",
                                      font=italic_font)

    def cancel_change(self):
        self.has_changed_label.config(text="")


def on_select(gui_photo, verbal=False):
    field_2_config(gui_photo, gui_photo.get_previous_dropdown_field())

    nom = gui_photo.dropdown_selected_option.get()
    field = gui_photo.dico_nom_id[nom]
    if verbal:
        print(f"nom : {nom} - field : {field}")
    config_2_fields(gui_photo, field)


def sauver_fichier_ini_photos(gui_photo: GUIPhotos):
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
        config_read = configparser.ConfigParser()

        # Check if the file exists
        if os.path.exists(ini_file_name):
            # Read the existing file
            config_read.read(ini_file_name)

        config_to_write = gui_photo.get_configparser()

        # Create a new ConfigParser object to store the filtered config_read
        merged_config = configparser.ConfigParser()

        # Copy everything from config_read except specified sections
        for section in config_read.sections():
            if section != "Sommaire Module Photos" and not section.startswith("Module Photos -"):
                merged_config.add_section(section)
                for option in config_read.options(section):
                    merged_config.set(section, option, config_read.get(section, option))

        # Add everything from config_to_write into merged_config
        for section in config_to_write.sections():
            if not merged_config.has_section(section):
                merged_config.add_section(section)
            for option in config_to_write.options(section):
                merged_config.set(section, option, config_to_write.get(section, option))

        # Write the parameters to the ini file
        with open(ini_file_name, 'w') as configfile:
            merged_config.write(configfile)
        gui_photo.cancel_change()
        messagebox.showinfo("Confirmation", "Modifications bien enregistrées")
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
        gui_photo.set_dropdown_value_from_field(dico_nom_id[tous_les_noms[0]])

    config_2_fields(gui_photo=gui_photo, field=dico_nom_id[tous_les_noms[0]])

    gui_photo.set_dico_nom_id(dico_nom_id)
    return dico_nom_id


def config_2_fields(gui_photo: GUIPhotos, field: str):
    field = field.lower()
    config_parser = gui_photo.get_configparser()

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

    gui_photo.set_dropdown_value_from_field(field)


def field_2_config(gui_photo, field, verbal=True):
    field = field.lower()
    if verbal:
        print(field)
    config_parser = gui_photo.get_configparser()

    # Retrieve the values from the Tkinter fields
    fichier_photos_value = gui_photo.fichier_photos_entry.get()
    dossier_photo_value = gui_photo.dossier_photo_entry.get()
    input_value = gui_photo.input_entry.get()
    output_value = gui_photo.output_entry.get()
    offset_value = gui_photo.offset_entry.get()
    onglet_value = gui_photo.dropdown_onglet.get()  # Assuming you have a dropdown for 'onglet'

    # Set the values into the config_parser
    section = f"Module Photos - {field}"
    if not config_parser.has_section(section):
        config_parser.add_section(section)

    # config_parser.set(section, 'fichier_photos_entry', fichier_photos_value)
    # config_parser.set(section, 'dossier_photo_entry', dossier_photo_value)
    # config_parser.set(section, 'input_entry', input_value)
    # config_parser.set(section, 'output_entry', output_value)
    # config_parser.set(section, 'offset', offset_value)
    # config_parser.set(section, 'onglet', onglet_value)

    has_changed = False

    if config_parser.get(section, 'fichier_photos_entry', fallback=None) != fichier_photos_value:
        config_parser.set(section, 'fichier_photos_entry', fichier_photos_value)
        has_changed = True

    if config_parser.get(section, 'dossier_photo_entry', fallback=None) != dossier_photo_value:
        config_parser.set(section, 'dossier_photo_entry', dossier_photo_value)
        has_changed = True

    if config_parser.get(section, 'input_entry', fallback=None) != input_value:
        config_parser.set(section, 'input_entry', input_value)
        has_changed = True

    if config_parser.get(section, 'output_entry', fallback=None) != output_value:
        config_parser.set(section, 'output_entry', output_value)
        has_changed = True

    if config_parser.get(section, 'offset', fallback=None) != offset_value:
        config_parser.set(section, 'offset', offset_value)
        has_changed = True

    if config_parser.get(section, 'onglet', fallback=None) != onglet_value:
        config_parser.set(section, 'onglet', onglet_value)
        has_changed = True

    if has_changed:
        gui_photo.has_changed()

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

        if nouveau_nom_deja_pris(gui_photo, nouveau_nom):
            messagebox.showerror("Erreur", "Ce nom correspond déjà à un réglage préenregistré")
            pop_up_renommer(gui_photo)
        else:
            config_parser = gui_photo.get_configparser()
            dico_nom_id = gui_photo.get_dico_nom_id()
            clef = dico_nom_id[ancien_nom]
            config_parser.set("Sommaire Module Photos", clef, nouveau_nom)
            upgrader_valeurs_dropdown(gui_photo)
            config_2_fields(gui_photo, clef)

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


def nouveau_nom_deja_pris(gui_photo, nouveau_nom):
    return nouveau_nom in gui_photo.dico_nom_id


def on_add_click(gui_photo: GUIPhotos):
    # Fonction appelée lors du clic sur le bouton pour afficher la pop-up
    def on_confirm():
        # Récupération du texte entré par l'utilisateur
        result = entry.get()
        popup.destroy()
        # Affichage du résultat dans la console pour l'exemple
        print("valeur ajoutée :", result)
        nouveau_nom = result

        if nouveau_nom_deja_pris(gui_photo, nouveau_nom):
            messagebox.showerror("Erreur", "Ce nom correspond déjà à un réglage préenregistré")
            on_add_click(gui_photo)
        else:
            config_parser = gui_photo.get_configparser()
            if not config_parser.has_section("Sommaire Module Photos"):
                config_parser.add_section("Sommaire Module Photos")
            config_parser.set("Sommaire Module Photos", nouveau_nom, nouveau_nom)

            upgrader_valeurs_dropdown(gui_photo)
            config_2_fields(gui_photo, nouveau_nom)

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
