import configparser

from IHM_lib import *
from module_photos import *


class GUIPhotos(ttk.Frame):
    def __init__(self, parent, api_drive, api_doc, api_sheets):
        super().__init__(parent)
        photo_window = self
        photo_window.winfo_toplevel().title("Module Photo")
        photo_window.grid_propagate(True)

        # ajout d'un labelframe pour la partie "insérer photos"
        inserphotos_labelframe = ttk.Labelframe(photo_window, text="Insérer des photos dans des fiches de personnages",
                                                width=700, name='inserphotos_labelframe')
        inserphotos_labelframe.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))

        current_file_label = ttk.Label(inserphotos_labelframe, text="Fichier avec référence photos / noms persos")
        current_file_label.grid(row=0, column=0, columnspan=2, sticky='w')
        self.fichier_photos_entry = GidEntry(inserphotos_labelframe, width=50)
        self.fichier_photos_entry.grid(column=2, row=0, columnspan=2, padx=(10, 10))

        dossier_photo_labels = ttk.Label(inserphotos_labelframe, text="Dossier contenant les photos")
        dossier_photo_labels.grid(row=1, column=0, columnspan=2, sticky='w')
        self.dossier_photo_entry = GidEntry(inserphotos_labelframe, width=50)
        self.dossier_photo_entry.grid(column=2, row=1, columnspan=2, padx=(10, 10))

        output_labels = ttk.Label(inserphotos_labelframe, text="Dossier où créer le fichier de sortie")
        output_labels.grid(row=2, column=0, columnspan=2, sticky='w')
        self.output_entry = GidEntry(inserphotos_labelframe, width=50)
        self.output_entry.grid(column=2, row=2, columnspan=2, padx=(10, 10))

        input_labels = ttk.Label(inserphotos_labelframe, text="Dossier où lire les fiches à enrichir ")
        input_labels.grid(row=3, column=0, columnspan=2, sticky='w')
        self.input_entry = GidEntry(inserphotos_labelframe, width=50)
        self.input_entry.grid(column=2, row=3, columnspan=2, padx=(10, 10))

        offset_label = ttk.Label(inserphotos_labelframe, text="Décalage (si nécessaire)")
        offset_label.grid(row=4, column=0, columnspan=1, sticky='w')
        self.offset_entry = ttk.Entry(inserphotos_labelframe, width=15)
        self.offset_entry.grid(column=1, row=4, columnspan=1, padx=(10, 10))

        ok_button = ttk.Button(inserphotos_labelframe, text="OK",
                               command=lambda: print("go"))
        ok_button.grid(row=4, column=2, columnspan=2, sticky='e', padx=(10, 10))
        ok_button.config(command=lambda: copier_dossier_et_enrichir_photos(
            api_doc=api_doc,
            api_drive=api_drive,
            api_sheets=api_sheets,
            folder_id=self.dossier_photo_entry.get(),
            offset=self.offset_entry.get(),
            dossier_sources_fiches=self.input_entry.get(),
            racine_sortie=self.output_entry.get(),
            sheet_id=self.fichier_photos_entry.get()))


def sauver_fichier_ini_photos(fichier_photos_entry, dossier_photo_entry, input_entry, output_entry):
    # Create a config parser object
    config = configparser.ConfigParser()

    # Add a section
    config.add_section('Module Photo')

    # Set the parameters in the section
    config.set('Module Photo', 'fichier_photos_entry', fichier_photos_entry)
    config.set('Module Photo', 'dossier_photo_entry', dossier_photo_entry)
    config.set('Module Photo', 'input_entry', input_entry)
    config.set('Module Photo', 'output_entry', output_entry)

    # Write the parameters to the ini file
    with open(ini_file_name, 'w') as configfile:
        config.write(configfile)