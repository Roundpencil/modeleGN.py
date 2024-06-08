import configparser

from IHM_lib import *
from module_photos import *

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import configparser
import os


class GUIPhotos(ttk.Frame):
    def __init__(self, parent, api_drive, api_doc, api_sheets):
        super().__init__(parent)
        photo_window = self
        photo_window.winfo_toplevel().title("Module Photo")
        photo_window.grid_propagate(True)

        # ajout d'un labelframe pour la partie "insérer photos"
        inserphotos_labelframe = ttk.Labelframe(photo_window, text="Insérer des photos dans des fiches de personnages",
                                                width=700, name='inserphotos_labelframe')
        inserphotos_labelframe.grid(row=50, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))

        load_button = ttk.Button(inserphotos_labelframe, text="Charger fichier ini",
                                 command=lambda: charger_fichier_photo(self))
        load_button.grid(row=1, column=0, columnspan=4, sticky='e', padx=(10, 10))

        current_file_label = ttk.Label(inserphotos_labelframe, text="Fichier avec référence photos / noms persos")
        current_file_label.grid(row=5, column=0, columnspan=2, sticky='w')
        self.fichier_photos_entry = GidEntry(inserphotos_labelframe, width=50)
        self.fichier_photos_entry.grid(column=2, row=5, columnspan=2, padx=(10, 10))

        dossier_photo_labels = ttk.Label(inserphotos_labelframe, text="Dossier contenant les photos")
        dossier_photo_labels.grid(row=10, column=0, columnspan=2, sticky='w')
        self.dossier_photo_entry = GidEntry(inserphotos_labelframe, width=50)
        self.dossier_photo_entry.grid(column=2, row=10, columnspan=2, padx=(10, 10))

        output_labels = ttk.Label(inserphotos_labelframe, text="Dossier où créer le fichier de sortie")
        output_labels.grid(row=20, column=0, columnspan=2, sticky='w')
        self.output_entry = GidEntry(inserphotos_labelframe, width=50)
        self.output_entry.grid(column=2, row=20, columnspan=2, padx=(10, 10))

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
                                   api_sheets=api_sheets,
                                   folder_id=self.dossier_photo_entry.get(),
                                   offset=self.offset_entry.get(),
                                   dossier_sources_fiches=self.input_entry.get(),
                                   racine_sortie=self.output_entry.get(),
                                   sheet_id=self.fichier_photos_entry.get()))
        ok_button.grid(row=40, column=30, columnspan=1, sticky='e', padx=(10, 10))

        save_button = ttk.Button(inserphotos_labelframe, text="Sauver fichier ini",
                                 command=lambda: sauver_fichier_ini_photos(self))
        save_button.grid(row=40, column=20, columnspan=1, sticky='e', padx=(10, 10))


# def sauver_fichier_ini_photos(fichier_photos_entry, dossier_photo_entry, input_entry, output_entry):
#     # Create a config parser object
#     config = configparser.ConfigParser()
#
#     # Add a section
#     config.add_section('Module Photo')
#
#     # Set the parameters in the section
#     config.set('Module Photo', 'fichier_photos_entry', fichier_photos_entry)
#     config.set('Module Photo', 'dossier_photo_entry', dossier_photo_entry)
#     config.set('Module Photo', 'input_entry', input_entry)
#     config.set('Module Photo', 'output_entry', output_entry)
#
#     # Write the parameters to the ini file
#     with open(ini_file_name, 'w') as configfile:
#         config.write(configfile)


def sauver_fichier_ini_photos(guiphoto: GUIPhotos):
    # Create a Tkinter root window
    # root = tk.Tk()
    # root.withdraw()  # Hide the root window

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


def charger_fichier_photo(guiphoto: GUIPhotos):
    file_path = filedialog.askopenfilename(filetypes=[("Fichiers INI", "*.ini")])

    if not file_path:
        messagebox.showerror("Erreur", "Aucun fichier sélectionné")
        return

    config_parser = configparser.ConfigParser()

    try:
        config_parser.read(file_path)
    except configparser.ParsingError as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du fichier .ini :\n{e}")
        return

    entrees = config_parser.items('Module Photo - Sommaire')
    dico_sortie = {nom_affiche: {'nom_section': 0,
                                 'fichier_photos_entry': 1,
                                 'dossier_photo_entry': 2,
                                 'input_entry': 3,
                                 'output_entry': 4,
                                 'onglet': 5} for nom_section, nom_affiche in entrees}

    guiphoto.fichier_photos_entry.insert(0, config_parser.get("Module Photos", 'fichier_photos_entry', fallback=""))
    guiphoto.dossier_photo_entry.insert(0, config_parser.get("Module Photos", 'dossier_photo_entry', fallback=""))
    guiphoto.input_entry.insert(0, config_parser.get("Module Photos", 'input_entry', fallback=""))
    guiphoto.output_entry.insert(0, config_parser.get("Module Photos", 'output_entry', fallback=""))
