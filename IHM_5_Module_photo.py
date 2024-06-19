import configparser
import os
import tkinter as tk
import webbrowser
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font

import google_io
from IHM_lib import *
from modeleGN import GN
from module_photos import *

# structure du fichier ini attendu :
# [Module Photos - test]
# fichier_photos_noms = 1pdqZdiKec0alZNU5xUtcFUBaZpNH2v44ueQFY4S3Mxs
# dossier_photos = 1Y4ONHyZtVkzAuo4EqbubZSrh8hjbJy_O
# dossier_contenant_fiches = 1sApU23J6e4lFZ0OmDtghq40T1Iw5vMTY
# dossier_sortie = 1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn
#
# [Module Photos - woop]
# fichier_photos_noms = fichier photos 2
# dossier_photos = dossier photos 2
# dossier_contenant_fiches = dossier inputs 2
# dossier_sortie = dossier sortie 2

PREFIXESECTION = 'Module Photos - '


class GUIPhotos(ttk.Frame):
    def __init__(self, parent, api_drive, api_doc, api_sheets):
        super().__init__(parent)
        self.api_sheets = api_sheets
        self.configparser = configparser.ConfigParser()
        self.dico_nom_session_joueurs = {}
        photo_window = self
        photo_window.winfo_toplevel().title("Module Photo")
        photo_window.grid_propagate(True)

        # ajout d'un labelframe pour la partie "Créer fichier référence"
        creerfichier_labelframe = ttk.Labelframe(photo_window, text="Créer un fichier perso/photos",
                                                 width=700, name='creerfichier_labelframe')
        creerfichier_labelframe.grid(row=10, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))

        def on_radiobutton_change():
            if file_option.get() == "mgn":
                magnet_button.config(state="normal")
                sheet_entry.config(state="disabled")
                sheet_button.config(state="disabled")
                if not len(mgn_file_label['text']) or not len(session_var.get()):
                    create_file_button.config(state="disabled")
                else:
                    create_file_button.config(state="normal")
            elif file_option.get() == "sheet":
                magnet_button.config(state="disabled")
                sheet_entry.config(state="normal")
                sheet_button.config(state="normal")
                if not len(session_var.get()):
                    create_file_button.config(state="disabled")
                else:
                    create_file_button.config(state="normal")
            else:
                magnet_button.config(state="disabled")
                sheet_entry.config(state="disabled")
                sheet_button.config(state="disabled")
                create_file_button.config(state="normal")

        def on_format_change(valeur, valeurs_activant_separateur: list[str], valeurs_activant_sessions: list[str]):
            if valeur in valeurs_activant_separateur:
                separator_entry.config(state="normal")
            else:
                separator_entry.config(state="disabled")

            if valeur in valeurs_activant_sessions:
                session_dropdown.config(state="readonly")
            else:
                session_dropdown.config(state="disabled")

        # Create the labelframe
        creerfichier_labelframe = ttk.Labelframe(photo_window, text="Créer un fichier perso/photos",
                                                 width=700, name='creerfichier_labelframe')
        creerfichier_labelframe.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))

        # # Configure the grid layout for the main window
        # photo_window.grid_rowconfigure(0, weight=1)
        # photo_window.grid_columnconfigure(0, weight=1)
        # photo_window.grid_rowconfigure(1, weight=1)
        # photo_window.grid_rowconfigure(2, weight=1)
        # photo_window.grid_rowconfigure(3, weight=1)

        # # Configure the grid layout for the labelframe
        # for i in range(0, 40, 10):
        #     creerfichier_labelframe.grid_rowconfigure(i, weight=1)
        # creerfichier_labelframe.grid_columnconfigure(0, weight=1)

        # First section: "Où sont mes fichiers de personnage"
        question_label = ttk.Label(creerfichier_labelframe, text="Source pour la liste des personnages : ")
        question_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=5)

        # Radiobuttons
        file_option = tk.StringVar(value="none")
        radiobutton_mgn = ttk.Radiobutton(creerfichier_labelframe, text="Fichier Mgn", variable=file_option,
                                          value="mgn", command=on_radiobutton_change)
        radiobutton_mgn.grid(row=10, column=0, sticky="w", pady=5)

        radiobutton_sheet = ttk.Radiobutton(creerfichier_labelframe, text="Sheet dédiée", variable=file_option,
                                            value="sheet", command=on_radiobutton_change)
        radiobutton_sheet.grid(row=20, column=0, sticky="w", pady=5)

        radiobutton_none = ttk.Radiobutton(creerfichier_labelframe,
                                           text="Je ne souhaite pas utiliser de fichiers de personnages "
                                                "(je crée uniquement un fichier à partir des photos)",
                                           variable=file_option, value="none", command=on_radiobutton_change)
        radiobutton_none.grid(row=30, column=0, columnspan=4, sticky="w", pady=5)

        # Button for "charger fichier Magnet"
        def charger_fichier_mgn(display_label):
            config_file = filedialog.askopenfilename(initialdir=".", title="Select file",
                                                     filetypes=(('fichiers MAGnet', '*.mgn'),
                                                                ("all files", "*.*")))
            display_label.config(text=config_file)
            create_file_button.config(state="normal")
            # todo : prendre en compte le format des noms, et donc les sessions dans la génération du fichier !
            #  si fichier MGN : extraire les données du fichier lors du loading
            #  si fichier sheet : utiliser un bouton rafraichir
            # todo : incorporer le chargement des choses dans dico_nom_sessions_joueur
            # todo : code à réintégrer pour le loading
            #     gn = GN.load(mgn_file_label['text'])
            #     noms_persos = gn.noms_personnages()
            # elif file_option.get() == "sheet":


        magnet_button = ttk.Button(creerfichier_labelframe, text="Charger fichier Magnet", state="disabled",
                                   command=lambda: charger_fichier_mgn(mgn_file_label))
        magnet_button.grid(row=10, column=3, padx=10, pady=5, sticky="nsew")

        mgn_file_label = ttk.Label(creerfichier_labelframe, text="")
        mgn_file_label.grid(row=10, column=1, columnspan=2, sticky="nsew", pady=5)

        # Text entry for "sheet dédiée"
        sheet_entry = GidEntry(creerfichier_labelframe, state="disabled")
        sheet_entry.grid(row=20, column=1, padx=10, pady=5, columnspan=2, sticky='we')

        # sheet button
        def charger_sheet_noms():
            self.dico_nom_session_joueurs.clear()
            id_sheet = sheet_entry.get()
            pjs, pnjs = google_io.lire_gspread_pj_pnjs(api_sheets, id_sheet)
            noms_persos = []
            if pjs:
                for perso in pjs:
                    nom_perso = perso["Nom"]
                    if not nom_perso in self.dico_nom_session_joueurs:
                        self.dico_nom_session_joueurs[nom_perso] = {session: interprete for session in perso if session.startwith("Interprète")}
                noms_persos += [ for perso in pjs]
            if pnjs:
                noms_persos += [perso["Nom"] for perso in pnjs]
            # todo : finir l'écriture de cette focntion

            messagebox.showinfo("MAGnet - Module Photos",
                                "Fichier Chargé avec succès [aucune opération réalisée en vrai, c'est un placeholder]")

        sheet_button = ttk.Button(creerfichier_labelframe, text="Charger sheet", state="disabled",
                                  command=lambda: charger_sheet_noms())
        sheet_button.grid(row=20, column=3, padx=10, pady=5, sticky="nsew")

        # Second section: "Emplacement du dossier Photo"
        photo_folder_label = ttk.Label(creerfichier_labelframe, text="Emplacement du dossier Photo")
        photo_folder_label.grid(row=40, column=0, sticky="w", pady=5)

        # Entry for the second section
        photo_folder_entry = GidEntry(creerfichier_labelframe)
        photo_folder_entry.grid(row=40, column=1, padx=10, pady=5, columnspan=3, sticky='we')

        # Third section: "Format du nom des photos"
        format_label = ttk.Label(creerfichier_labelframe, text="Format du nom des photos")
        format_label.grid(row=50, column=0, sticky="w", pady=5)

        # Dropdown menu for the third section
        format_options = [
            "Juste le nom des personnages",
            "Juste le nom des joueurs et joueuse",
            "Joueurs [séparateur] Personnage",
            "Personnage [séparateur] Joueurs"
        ]
        format_var = tk.StringVar(value=format_options[0])
        format_dropdown = ttk.Combobox(creerfichier_labelframe, textvariable=format_var, values=format_options,
                                       state='readonly', width=30)
        # state='disabled', width=30)
        format_dropdown.grid(row=50, column=1, padx=10, pady=5)
        format_dropdown.bind("<<ComboboxSelected>>",
                             lambda event: on_format_change(format_var.get(), format_options[2:4], format_options[1:4]))
        # format_var.trace("w", on_format_change)

        # Label for the separator
        separator_label = ttk.Label(creerfichier_labelframe, text="Séparateur :")
        separator_label.grid(row=51, column=1, sticky="w", padx=10)

        # Entry for the separator
        separator_entry = ttk.Entry(creerfichier_labelframe, state="disabled")
        separator_entry.grid(row=51, column=2, padx=10, pady=5, sticky="w")

        # Label for the session
        session_label = ttk.Label(creerfichier_labelframe, text="Session :")
        session_label.grid(row=52, column=1, sticky="w", padx=10)

        # dropdown for the session
        session_var = tk.StringVar()
        session_dropdown = ttk.Combobox(creerfichier_labelframe, textvariable=session_var, values=[],
                                        # state='readonly', width=30)
                                        state='disabled', width=30)
        session_dropdown.grid(row=52, column=2, padx=10, pady=5)

        # Fourth section: "Dossier où créer le fichier de sortie"
        output_folder_label = ttk.Label(creerfichier_labelframe, text="Dossier où créer le fichier de sortie")
        output_folder_label.grid(row=60, column=0, sticky="w", pady=5)

        # Entry for the output folder
        output_folder_entry = GidEntry(creerfichier_labelframe)
        output_folder_entry.grid(row=60, column=1, padx=10, pady=5, columnspan=3, sticky='we')

        output_file_name_label = ttk.Label(creerfichier_labelframe, text="Nom du fichier à créer")
        output_file_name_label.grid(row=65, column=0, sticky="w", pady=5)

        # Entry for the output folder
        output_file_name_entry = ttk.Entry(creerfichier_labelframe)
        output_file_name_entry.grid(row=65, column=1, padx=10, pady=5, columnspan=3, sticky='we')

        # Button to create the file
        def creer_fichier_dans_drive():
            # on crée le nom des persos en fonction du radiobutton
            if file_option.get() == "mgn" or file_option.get() == "sheet":
                # format_options = [
                #     "Juste le nom des personnages",
                #     "Juste le nom des joueurs et joueuse",
                #     "Joueurs [séparateur] Personnage",
                #     "Personnage [séparateur] Joueurs"
                # ]

                if not self.dico_nom_session_joueurs:
                    messagebox.showerror("Impossible de générer le fichier",
                                         "Merci de charger au moins un fichier source (mgn ou google sheet) "
                                         "pour les noms")

                if format_dropdown.get() == format_options[0]:
                    noms_persos = list(self.dico_nom_session_joueurs.keys())
                else:
                    session = session_var.get()
                    if format_dropdown.get() == format_options[1]:
                        noms_persos = [self.dico_nom_session_joueurs[perso][session]
                                       for perso in self.dico_nom_session_joueurs]
                    elif format_dropdown.get() == format_options[2]:
                        separateur = separator_entry.get()
                        noms_persos = [f"{self.dico_nom_session_joueurs[nom_perso].get(session, '')}" \
                                       f"{separateur}" \
                                       f"{nom_perso}"
                                       for nom_perso in self.dico_nom_session_joueurs]
                    elif format_dropdown.get() == format_options[3]:
                        separateur = separator_entry.get()
                        noms_persos = [f"{nom_perso}" \
                                       f"{separateur}" \
                                       f"{self.dico_nom_session_joueurs[nom_perso].get(session, '')}"
                                       for nom_perso in self.dico_nom_session_joueurs]
                    else:
                        messagebox.showerror("Probleme lors de la génératon du fichier",
                                             "Merci de choisir le formattage du nom des photos")
                        return
            else:
                noms_persos = []

            print(noms_persos)

            id_sheet, erreur = ecrire_tableau_photos_noms(api_drive, self.api_sheets,
                                                          folder_source_images=photo_folder_entry.get(),
                                                          noms_persos=noms_persos,
                                                          dossier_output=output_folder_entry.get(verbal=True),
                                                          nom_fichier=output_file_name_entry.get())
            if erreur:
                messagebox.showerror("Une erreur est survenue", erreur)
                return

            messagebox.showinfo("Génération terminée", "Le fichier a bien été généré \n"
                                                       "Reste à faire manuellement : \n"
                                                       " - Vérifier les associations automatiques réalisées \n"
                                                       " - Déplacer les noms insécables dans la bonne colonne, "
                                                       "si nécessaire \n"
                                                       " - Ajouter les alias sécables et insécables \n"
                                                       " - Ajouter des lignes pour les noms qui doivent apparaître "
                                                       "sans photos")

            address = g_io.id_2_sheet_address(id_sheet)

            def open_link(event):
                webbrowser.open_new(address)

            prez_output_label['text'] = "Fichier créé : "
            output_label.config(text=address)

            output_label.bind("<Button-1>", open_link)
            save_ini_button.config(state="normal")

        create_file_button = ttk.Button(creerfichier_labelframe, text="Créer fichier Photos / Noms",
                                        command=lambda: creer_fichier_dans_drive())
        create_file_button.grid(row=80, column=0, columnspan=1, pady=10)

        # Label for the ini file name
        prez_output_label = ttk.Label(creerfichier_labelframe)
        prez_output_label.grid(row=80, column=1, columnspan=1, sticky="w", pady=5)

        # Entry for the ini file name
        output_label = ttk.Label(creerfichier_labelframe, foreground="blue", cursor="hand2")
        output_label.grid(row=80, column=2, padx=10, pady=5, columnspan=2, sticky='we')

        # bouton pour sauvegarder configuration dans fichier ini
        def initiate_ini_file(verbal=False):
            self.configparser = configparser.ConfigParser()
            nom_section = "Module Photos - Configuration par défaut"
            self.configparser.add_section(nom_section)
            if verbal:
                print(f"label : {output_label['text']}, dossier : {photo_folder_entry.get(process=False)}")
            self.configparser.set(nom_section, 'fichier_photos_noms', output_label['text'])
            self.configparser.set(nom_section, 'dossier_photos', photo_folder_entry.get(process=False))
            if verbal:
                print("contenu du configparser qui vient d'être créé : ")
                for section in self.configparser:
                    for key, value in self.configparser.items(section):
                        print(f"{section}: {key}: {value}")
                    # for key in self.configparser[section]:
                    #     print(f"{section}: {key}: {self.configparser[section][key]}")

            sauver_fichier_ini_photos(self)

        save_ini_button = ttk.Button(creerfichier_labelframe, text="Sauvegarder le fichier de configuration...",
                                     command=lambda: initiate_ini_file(), state='disabled')
        save_ini_button.grid(row=90, column=0, columnspan=2, pady=10)

        ################################################
        # ajout d'un labelframe pour la partie "insérer photos"
        inserphotos_labelframe = ttk.Labelframe(photo_window, text="Insérer des photos dans des fiches de personnages",
                                                width=700, name='inserphotos_labelframe')
        inserphotos_labelframe.grid(row=50, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))
        inserphotos_labelframe.grid_propagate(True)

        load_button = ttk.Button(inserphotos_labelframe, text="Charger fichier ini",
                                 command=lambda: action_bouton_charger(self))
        load_button.grid(row=10, column=0, columnspan=4, sticky='w', padx=(10, 10))

        # ajout d'un dropdown menu pour selectionner la configuration pré-enregistrée
        dropdown_label = ttk.Label(inserphotos_labelframe,
                                   text="Réglage pré-enregistré : ")
        dropdown_label.grid(row=40, column=0, columnspan=1, sticky='w')

        # Create a StringVar to hold the selected value
        self.dropdown_selected_option = tk.StringVar()
        # self.previous_dropdown_field = None
        self.previous_dropdown_section = None

        # Create the dropdown menu
        self.dropdown = ttk.Combobox(inserphotos_labelframe, textvariable=self.dropdown_selected_option,
                                     state='readonly')

        # Bind the selection event to the on_select function
        self.dropdown.bind("<<ComboboxSelected>>", lambda event: on_select(self))
        self.dropdown.grid(row=40, column=1, columnspan=4, sticky='nsew', padx=(10, 10))

        rename_dropdown_button = ttk.Button(inserphotos_labelframe, text="\u270e",
                                            command=lambda: pop_up_renommer(self))
        rename_dropdown_button.grid(row=45, column=1, columnspan=1, sticky='w', padx=(10, 10))
        ToolTip(rename_dropdown_button, "Renommer la configuration en cours")

        del_dropdown_button = ttk.Button(inserphotos_labelframe, text="\u274c",
                                         command=lambda: on_delete_click(self))
        del_dropdown_button.grid(row=45, column=2, columnspan=1, sticky='w', padx=(10, 10))
        ToolTip(del_dropdown_button, "Supprimer la configuration en cours")

        add_dropdown_button = ttk.Button(inserphotos_labelframe, text="\u2795",
                                         command=lambda: on_add_click(self))
        add_dropdown_button.grid(row=45, column=3, columnspan=1, sticky='w', padx=(10, 10))
        ToolTip(add_dropdown_button, "Ajouter une nouvelle configuration")

        copy_dropdown_button = ttk.Button(inserphotos_labelframe, text="\u2398",
                                          command=lambda: on_copy_click(self))
        copy_dropdown_button.grid(row=45, column=4, columnspan=1, sticky='w', padx=(10, 10))
        ToolTip(copy_dropdown_button, "Dupliquer la configuration en cours")

        # todo : proposer une architecture qui permet à la fois
        #  de stoquer un configparser dans le GN et d'être rétrocompatible
        # todo : rajouter un champ pour dire qu'on ne veut mettre que les photos des PJs ?

        current_file_label = ttk.Label(inserphotos_labelframe, text="Fichier avec référence photos / noms persos")
        current_file_label.grid(row=50, column=0, columnspan=1, sticky='w')
        self.fichier_photos_entry = GidEntry(inserphotos_labelframe, width=50)
        self.fichier_photos_entry.grid(column=1, row=50, columnspan=4, sticky='nsew', padx=(10, 10))

        # ajout d'un dropdown pour les onglets
        dropdown_onglet_label = ttk.Label(inserphotos_labelframe,
                                          text="Choix de l'onglet dans les fichier")
        dropdown_onglet_label.grid(row=60, column=0, columnspan=4, sticky='w')

        self.dropdown_onglet_selected_option = tk.StringVar()
        # Create the dropdown menu
        self.dropdown_onglet = ttk.Combobox(inserphotos_labelframe, textvariable=self.dropdown_onglet_selected_option,
                                            state='readonly')
        self.dropdown_onglet.grid(row=60, column=1, columnspan=3, sticky='nsew', padx=(10, 10))

        refresh_onglet_button = ttk.Button(inserphotos_labelframe, text="\u267B",
                                           command=lambda: maj_dropdown_onglets(self))
        refresh_onglet_button.grid(row=60, column=4, columnspan=1, sticky='w', padx=(10, 10))
        ToolTip(refresh_onglet_button, "Rafraichir le nom des onglets")

        dossier_photo_labels = ttk.Label(inserphotos_labelframe, text="Dossier contenant les photos")
        dossier_photo_labels.grid(row=100, column=0, sticky='w')
        self.dossier_photo_entry = GidEntry(inserphotos_labelframe, width=50)
        self.dossier_photo_entry.grid(column=1, row=100, columnspan=4, padx=(10, 10), sticky='nsew')

        output_labels = ttk.Label(inserphotos_labelframe, text="Dossier où créer les fichiers de sortie")
        output_labels.grid(row=200, column=0, columnspan=1, sticky='w')
        self.output_entry = GidEntry(inserphotos_labelframe, width=50)
        self.output_entry.grid(column=1, row=200, columnspan=4, padx=(10, 10), sticky='nsew')

        input_labels = ttk.Label(inserphotos_labelframe, text="Dossier où lire les fiches à enrichir ")
        input_labels.grid(row=300, column=0, columnspan=1, sticky='w')
        self.input_entry = GidEntry(inserphotos_labelframe, width=50)
        self.input_entry.grid(column=1, row=300, columnspan=4, padx=(10, 10), sticky='nsew')

        offset_label = ttk.Label(inserphotos_labelframe, text="Décalage (si nécessaire)")
        offset_label.grid(row=400, column=0, columnspan=1, sticky='w')
        self.offset_entry = ttk.Entry(inserphotos_labelframe, width=15)
        self.offset_entry.grid(column=1, row=400, columnspan=1, padx=(10, 10))

        def inserer_photos_erreurs():
            texte_erreurs = copier_dossier_et_enrichir_photos(
                api_doc=api_doc,
                api_drive=api_drive,
                api_sheets=self.api_sheets,
                folder_id=self.dossier_photo_entry.get(),
                offset=int(self.offset_entry.get()),
                dossier_sources_fiches=[self.input_entry.get()],
                racine_sortie=self.output_entry.get(),
                nom_onglet=self.dropdown_onglet.get(),
                sheet_id=self.fichier_photos_entry.get())
            if len(texte_erreurs) == 0:
                messagebox.showinfo("Opération terminée", "L'opération s'est déroulée avec succès")
            else:
                messagebox.showerror("Une ou plusieurs erreurs sont survenues", '\n'.join(texte_erreurs))

        ok_button = ttk.Button(inserphotos_labelframe, text="OK", command=lambda: inserer_photos_erreurs())
        ok_button.grid(row=400, column=4, columnspan=1, sticky='e', padx=(10, 10))

        save_button = ttk.Button(inserphotos_labelframe, text="Sauver fichier ini",
                                 command=lambda: sauver_fichier_ini_photos(self))
        save_button.grid(row=400, column=3, columnspan=1, sticky='e', padx=(10, 10))

        self.has_changed_label = ttk.Label(inserphotos_labelframe)
        self.has_changed_label.grid(row=410, column=0, columnspan=4, sticky='nsew')

        #######
        # on ajoute un modlule pour changer de mode
        def switch_mode():
            if selected_mode.get() == 1:
                inserphotos_labelframe.grid()
                creerfichier_labelframe.grid_remove()
            else:
                creerfichier_labelframe.grid()
                inserphotos_labelframe.grid_remove()

        # Initially hide the second LabelFrame

        creerfichier_labelframe.grid_remove()

        # Create an IntVar to hold the value of the selected mode
        selected_mode = tk.IntVar(value=1)

        # Create the radiobuttons
        radio_mode1 = ttk.Radiobutton(photo_window, text="Insérer des photos", variable=selected_mode, value=1,
                                      command=switch_mode)
        radio_mode1.grid(row=0, column=1, sticky=tk.W, pady=5)

        radio_mode2 = ttk.Radiobutton(photo_window, text="Créer fichier Photos/noms", variable=selected_mode, value=2,
                                      command=switch_mode)
        radio_mode2.grid(row=0, column=2, sticky=tk.W, pady=5)

    def set_configparser(self, config_parser):
        self.configparser = config_parser

    def get_apisheets(self):
        return self.api_sheets

    def get_configparser(self):
        return self.configparser

    def set_dropdown_value_from_nom_section(self, nom_section):
        self.dropdown_selected_option.set(nom_section)
        self.previous_dropdown_section = nom_section

    def get_previous_dropdown_section(self):
        return self.previous_dropdown_section

    def has_changed(self):
        # Define the font with italic style
        italic_font = font.Font(family="Helvetica", size=8, slant="italic")

        # Update the label's text and font
        self.has_changed_label.config(text="Les réglages prédéfinis ont changé, "
                                           "n'oubliez pas de sauvegarder si vous souhaiter les conserver",
                                      font=italic_font)

    def cancel_change(self):
        self.has_changed_label.config(text="")


def on_select(gui_photo, verbal=False):
    # field_2_config(gui_photo, gui_photo.get_previous_dropdown_field())
    field_2_config(gui_photo, gui_photo.get_previous_dropdown_section())

    nom_section = gui_photo.dropdown_selected_option.get()
    # field = gui_photo.dico_nom_id[nom]
    if verbal:
        print(f"nom : {nom_section} - nom section : {nom_section}")
    config_2_fields(gui_photo, nom_section)


def sauver_fichier_ini_photos(gui_photo: GUIPhotos, verbal=False):
    # bien noter que les noms sont enregistrés en minuscules

    # Open a file dialog to let the user select an existing file or write a new one
    ini_file_name = filedialog.asksaveasfilename(
        defaultextension=".ini",
        filetypes=[("INI files", "*.ini"), ("All files", "*.*")],
        title="Select or create an INI file"
    )

    if verbal:
        print("contenu du configarser reçu en entrée : ")
        for section in (cp := gui_photo.configparser):
            for key, value in cp.items(section):
                print(f"{section}: {key}: {value}")

    # Check if a file was selected
    if ini_file_name:
        # Create a config parser object
        config_read = configparser.ConfigParser()

        # Check if the file exists
        if os.path.exists(ini_file_name):
            # Read the existing file
            config_read.read(ini_file_name)
            if verbal:
                print("contenu du configarser lu dans le fichier : ")
                for section in config_read:
                    for key, value in config_read.items(section):
                        print(f"{section}: {key}: {value}")

        config_to_write = gui_photo.get_configparser()

        # Create a new ConfigParser object to store the filtered config_read
        merged_config = configparser.ConfigParser()

        # Copy everything from config_read except specified sections
        for section in config_read.sections():
            # if section != "Sommaire Module Photos" and not section.startswith("Module Photos -"):
            if not section.startswith(PREFIXESECTION):
                merged_config.add_section(section)
                for option in config_read.options(section):
                    merged_config.set(section, option, config_read.get(section, option))

        # Add everything from config_to_write into merged_config
        for section in config_to_write.sections():
            if not merged_config.has_section(section):
                merged_config.add_section(section)
            for option in config_to_write.options(section):
                merged_config.set(section, option, config_to_write.get(section, option))

        if verbal:
            print("contenu du configarser mergé: ")
            for section in merged_config:
                for key, value in merged_config.items(section):
                    print(f"{section}: {key}: {value}")

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

    gui_photo.cancel_change()
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


def upgrader_valeurs_dropdown(gui_photo: GUIPhotos, nom_section: str = None):
    config_parser = gui_photo.get_configparser()
    tous_les_noms = tous_les_noms_de_sections(config_parser)
    gui_photo.dropdown['values'] = tous_les_noms
    if nom_section and nom_section in tous_les_noms:
        gui_photo.set_dropdown_value_from_nom_section(nom_section)
        config_2_fields(gui_photo=gui_photo, nom_section=nom_section)
    elif len(tous_les_noms):
        gui_photo.set_dropdown_value_from_nom_section(tous_les_noms[0])
        config_2_fields(gui_photo=gui_photo, nom_section=tous_les_noms[0])


def tous_les_noms_de_sections(config_parser):
    tous_les_noms = [nom_section[len(PREFIXESECTION):] for nom_section in config_parser.sections()]
    return tous_les_noms


def config_2_fields(gui_photo: GUIPhotos, nom_section: str):
    # nom_section = nom_section.lower()
    config_parser = gui_photo.get_configparser()

    gui_photo.fichier_photos_entry.delete(0, 'end')
    gui_photo.dossier_photo_entry.delete(0, 'end')
    gui_photo.input_entry.delete(0, 'end')
    gui_photo.output_entry.delete(0, 'end')
    gui_photo.offset_entry.delete(0, 'end')

    gui_photo.fichier_photos_entry.insert(0, config_parser.get(f"{PREFIXESECTION}{nom_section}", 'fichier_photos_noms',
                                                               fallback=""))
    valeur_dropdown_onglet = config_parser.get(f"{PREFIXESECTION}{nom_section}", 'onglet',
                                               fallback="")
    maj_dropdown_onglets(gui_photo, valeur_dropdown_onglet)
    gui_photo.dossier_photo_entry.insert(0, config_parser.get(f"{PREFIXESECTION}{nom_section}", 'dossier_photos',
                                                              fallback=""))
    gui_photo.input_entry.insert(0, config_parser.get(f"{PREFIXESECTION}{nom_section}", 'dossier_contenant_fiches',
                                                      fallback=""))
    gui_photo.output_entry.insert(0, config_parser.get(f"{PREFIXESECTION}{nom_section}", 'dossier_sortie', fallback=""))
    gui_photo.offset_entry.insert(0, config_parser.get(f"{PREFIXESECTION}{nom_section}", 'offset', fallback=0))

    gui_photo.set_dropdown_value_from_nom_section(nom_section)


def field_2_config(gui_photo, field, verbal=True):
    # field = field.lower()
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
    section = f"{PREFIXESECTION}{field}"
    if not config_parser.has_section(section):
        config_parser.add_section(section)

    has_changed = False

    if config_parser.get(section, 'fichier_photos_noms', fallback=None) != fichier_photos_value:
        config_parser.set(section, 'fichier_photos_noms', fichier_photos_value)
        has_changed = True

    if config_parser.get(section, 'dossier_photos', fallback=None) != dossier_photo_value:
        config_parser.set(section, 'dossier_photos', dossier_photo_value)
        has_changed = True

    if config_parser.get(section, 'dossier_contenant_fiches', fallback=None) != input_value:
        config_parser.set(section, 'dossier_contenant_fiches', input_value)
        has_changed = True

    if config_parser.get(section, 'dossier_sortie', fallback=None) != output_value:
        config_parser.set(section, 'dossier_sortie', output_value)
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
    except Exception:
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
            config = gui_photo.get_configparser()

            ancienne_section = f"{PREFIXESECTION}{ancien_nom}"
            nouvelle_section = f"{PREFIXESECTION}{nouveau_nom}"

            config.add_section(nouvelle_section)
            for item in config.items(ancienne_section):
                config.set(nouvelle_section, item[0], item[1])

            config.remove_section(ancienne_section)

            upgrader_valeurs_dropdown(gui_photo, nouveau_nom)

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
        section_to_remove = f"{PREFIXESECTION}{wording_to_remove}"
        if config.has_section(section_to_remove):
            config.remove_section(section_to_remove)
        upgrader_valeurs_dropdown(gui_photo)


def nouveau_nom_deja_pris(gui_photo, nouveau_nom):
    tous_les_noms = tous_les_noms_de_sections(gui_photo.get_configparser())
    return nouveau_nom in tous_les_noms


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
            config_parser.add_section(f"{PREFIXESECTION}{nouveau_nom}")
            upgrader_valeurs_dropdown(gui_photo, nouveau_nom)

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


def on_copy_click(gui_photo: GUIPhotos):
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
            config = gui_photo.get_configparser()

            ancienne_section = f"{PREFIXESECTION}{ancien_nom}"
            nouvelle_section = f"{PREFIXESECTION}{nouveau_nom}"

            config.add_section(nouvelle_section)
            for item in config.items(ancienne_section):
                config.set(nouvelle_section, item[0], item[1])

            upgrader_valeurs_dropdown(gui_photo, nouveau_nom)

    def on_cancel():
        # Fermeture de la pop-up et retour de None
        popup.destroy()
        # Affichage de None dans la console pour l'exemple
        print("Action annulée, retour de None")

    # Création de la pop-up
    popup = tk.Toplevel(gui_photo)
    popup.title("Copier la configuration actuelle")

    # Message d'instruction
    label = tk.Label(popup, text="Nom de la copie : ")
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


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
