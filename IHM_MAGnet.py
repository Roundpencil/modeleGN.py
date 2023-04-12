import threading
import tkinter as tk
import traceback
import webbrowser
from tkinter import filedialog, ttk, messagebox
from tkinter.ttk import Progressbar

from MAGnet_lib import *
from modeleGN import GN


class Application(tk.Frame):
    def __init__(self,
                 mode_leger=True,
                 master=None):
        super().__init__(master)

        self.maj_versions = None
        self.url_derniere_version = None
        self.derniere_version = None
        self.master = master
        self.master.title("MAGnet, la moulinette")
        # self.master.geometry("450x150")
        # self.grid()
        # self.create_widgets()
        self.gn = None
        self.dict_config = None
        self.apiDrive = None
        self.apiDoc = None
        self.apiSheets = None

        # reprise de l'ancien code de regen
        regen_window = self.master
        # regen_window.geometry("665x535")  # chaque nouvelle ligne fait +25 de hauteur
        regen_window.grid_propagate(1)

        # ajouter le bouton et le label ini a la première ligne
        # ajout d'un labelframe pour le fichier ini
        ini_labelframe = ttk.Labelframe(regen_window, text="Sélection du GN à lire", width=700)
        ini_labelframe.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))

        config_button = ttk.Button(ini_labelframe, text="Changer fichier de configuration")
        config_button.grid(row=0, column=0, pady=(10, 10), padx=(10, 10))

        # v_config_button = ttk.Button(ini_labelframe, text="Vérifier le fichier de configuration")
        # v_config_button.grid(row=1, column=0, pady=(10, 10), padx=(10, 10))
        # v_config_button(command=lambda: self.verifier_config_et_afficher_popup())

        v_config_button = ttk.Button(ini_labelframe, text="Vérifier le fichier de configuration",
                                     command=lambda: self.verifier_config_et_afficher_popup(current_file_label))
        v_config_button.grid(row=1, column=0, pady=(10, 10), padx=(10, 10))

        # Create the label
        current_file_label = ttk.Label(ini_labelframe, text="Fichier ini actuel : Aucun")
        current_file_label.grid(row=0, column=1, columnspan=3, sticky='w')

        # ajout d'un labelframe pour les fonctions du mode diagnostic
        diagnostic_labelframe = ttk.Labelframe(regen_window, text="Outils diagnostic", width=700)
        # diagnostic_labelframe.grid(row=50, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))

        lecture_label = ttk.Label(diagnostic_labelframe, text="Options de lecture")
        lecture_label.grid(row=50, column=0, columnspan=3)

        forcer_update_gn_button = ttk.Button(diagnostic_labelframe, text="Vérifier le modèle \nde la sauvegarde",
                                             command=lambda: mettre_a_jour_champs(self.gn))
        forcer_update_gn_button.grid(row=50, column=3, rowspan=2, columnspan=2,
                                     sticky="ne")  # , sticky="nsew"

        verbal_var = tk.BooleanVar()
        verbal_var.set(False)
        verbal_check = ttk.Checkbutton(diagnostic_labelframe, text='Mode "bavard"',
                                       variable=verbal_var)
        verbal_check.grid(row=53, column=3, rowspan=2, columnspan=2, padx=(150, 10),
                          sticky="nw")

        # Intrigues
        var_fast_intrigue = tk.BooleanVar(value=True)
        var_fast_fiches_pjs = tk.BooleanVar(value=True)
        var_fast_fiches_pnjs = tk.BooleanVar(value=True)
        var_fast_evenements = tk.BooleanVar(value=True)
        var_fast_objets = tk.BooleanVar(value=True)

        # Intrigue Line
        ttk.Label(diagnostic_labelframe, text="Intrigue").grid(row=51, column=0)
        ttk.Radiobutton(diagnostic_labelframe, text="Rapide", variable=var_fast_intrigue, value=True).grid(row=51,
                                                                                                           column=1)
        ttk.Radiobutton(diagnostic_labelframe, text="Complet", variable=var_fast_intrigue, value=False).grid(row=51,
                                                                                                             column=2)

        # Fiches PJs Line
        ttk.Label(diagnostic_labelframe, text="Fiches PJs").grid(row=52, column=0)
        ttk.Radiobutton(diagnostic_labelframe, text="Rapide", variable=var_fast_fiches_pjs, value=True).grid(row=52,
                                                                                                             column=1)
        ttk.Radiobutton(diagnostic_labelframe, text="Complet", variable=var_fast_fiches_pjs, value=False).grid(row=52,
                                                                                                               column=2)

        # Fiches PNJs Line
        ttk.Label(diagnostic_labelframe, text="Fiches PNJs").grid(row=53, column=0)
        ttk.Radiobutton(diagnostic_labelframe, text="Rapide", variable=var_fast_fiches_pnjs, value=True).grid(row=53,
                                                                                                              column=1)
        ttk.Radiobutton(diagnostic_labelframe, text="Complet", variable=var_fast_fiches_pnjs, value=False).grid(row=53,
                                                                                                                column=2)

        # Evenements Line
        ttk.Label(diagnostic_labelframe, text="Evenements").grid(row=54, column=0)
        ttk.Radiobutton(diagnostic_labelframe, text="Rapide", variable=var_fast_evenements, value=True).grid(row=54,
                                                                                                             column=1)
        ttk.Radiobutton(diagnostic_labelframe, text="Complet", variable=var_fast_evenements, value=False).grid(row=54,
                                                                                                               column=2)

        # Objets Line
        ttk.Label(diagnostic_labelframe, text="Objets").grid(row=55, column=0)
        ttk.Radiobutton(diagnostic_labelframe, text="Rapide", variable=var_fast_objets, value=True).grid(row=55,
                                                                                                         column=1)
        ttk.Radiobutton(diagnostic_labelframe, text="Complet", variable=var_fast_objets, value=False).grid(row=55,
                                                                                                           column=2)

        repartir_de_0_var = tk.BooleanVar()
        repartir_de_0_var.set(False)
        charger_fichier_check = ttk.Checkbutton(diagnostic_labelframe, text="Tout effacer",
                                                variable=repartir_de_0_var)
        charger_fichier_check.grid(row=104, column=0, pady=(0, 10))

        sauver_apres_operation_var = tk.BooleanVar()
        sauver_apres_operation_var.set(True)
        sauver_apres_operation_check = ttk.Checkbutton(diagnostic_labelframe, text="Sauver après opération",
                                                       variable=sauver_apres_operation_var)
        sauver_apres_operation_check.grid(row=104, column=1, pady=(0, 10))

        # ajouter un bouton pour afficher ou pas les options du mode diagnostic au dessus
        switch_diag_var = tk.BooleanVar()

        def gerer_frame_diag():
            if switch_diag_var.get():
                # Show the diagnostic_labelframe
                diagnostic_labelframe.grid(row=50, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))
                # regen_window.geometry("675x735")
            else:
                # Hide the diagnostic_labelframe
                diagnostic_labelframe.grid_forget()
                # regen_window.geometry("675x510")

        switch_diag_var = tk.BooleanVar()
        switch_diag_var.set(False)
        if mode_leger:
            switch_diag = ttk.Checkbutton(regen_window, text="Afficher outils diagnostic",
                                          variable=switch_diag_var, onvalue=1, command=gerer_frame_diag)
        else:
            switch_diag = ttk.Checkbutton(regen_window, text="Afficher outils diagnostic",
                                          variable=switch_diag_var, onvalue=1, style="Switch",
                                          command=gerer_frame_diag)

        switch_diag.grid(row=999, column=0, padx=(10, 0))

        manuel_button = ttk.Button(regen_window, text="Afficher le manuel en ligne",
                                   command=lambda: webbrowser.open_new("https://docs.google.com/document/d"
                                                                       "/1U1D5byuXXv6_dHo13fcn9ka50pYYHzMlNGtH3gfE1Sc")
                                   )

        manuel_button.grid(row=999, column=3, pady=(0, 10))

        # début de la zone génération
        generer_labelframe = ttk.Labelframe(regen_window, text="Options de génération", width=700)
        generer_labelframe.grid(row=100, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))

        master_state = tk.BooleanVar()
        master_state.set(True)
        master_checkbox = ttk.Checkbutton(generer_labelframe, text="Cocher / Décocher tout", variable=master_state,
                                          command=lambda: update_checkboxes(master_state))
        master_checkbox.grid(row=105, column=0, columnspan=4)

        def update_checkboxes(etat_a_forcer):
            args = [generer_fichiers_pj_var,
                    generer_fichiers_pj_var,
                    generer_fichiers_pnjs_var,
                    fichier_erreurs_intrigues_var,
                    fichier_erreurs_evenements_var,
                    changelog_var,
                    table_intrigues_var,
                    table_objets_var,
                    table_chrono_var,
                    table_persos_var,
                    table_pnjs_var,
                    aide_de_jeu_var,
                    table_commentaires_var,
                    table_evenements_var,
                    table_relations_var,
                    fichier_questionnaire_inscription_var
                    ]

            for checkbox in args:
                checkbox.set(etat_a_forcer.get())

        generer_fichiers_pj_var = tk.BooleanVar()
        generer_fichiers_pj_var.set(True)
        generer_fichiers_drive_check = ttk.Checkbutton(generer_labelframe, text="Squelettes PJs",
                                                       variable=generer_fichiers_pj_var)
        generer_fichiers_drive_check.grid(sticky="W", row=106, column=0)

        generer_fichiers_pnjs_var = tk.BooleanVar()
        generer_fichiers_pnjs_var.set(True)
        generer_fichiers_pnjs_check = ttk.Checkbutton(generer_labelframe, text="Squelettes PNJs",
                                                      variable=generer_fichiers_pnjs_var)
        generer_fichiers_pnjs_check.grid(sticky="W", row=106, column=1)

        fichier_erreurs_intrigues_var = tk.BooleanVar()
        fichier_erreurs_intrigues_var.set(True)
        fichier_erreurs_check = ttk.Checkbutton(generer_labelframe, text="Fichier erreurs intrigues",
                                                variable=fichier_erreurs_intrigues_var)
        fichier_erreurs_check.grid(sticky="W", row=106, column=2)

        changelog_var = tk.BooleanVar()
        changelog_var.set(True)
        changelog_check = ttk.Checkbutton(generer_labelframe, text="Changelog",
                                          variable=changelog_var)
        changelog_check.grid(sticky="W", row=106, column=3)

        table_intrigues_var = tk.BooleanVar()
        table_intrigues_var.set(True)
        table_intrigues_check = ttk.Checkbutton(generer_labelframe, text="Table des intrigues",
                                                variable=table_intrigues_var)
        table_intrigues_check.grid(sticky="W", row=107, column=0)

        table_objets_var = tk.BooleanVar()
        table_objets_var.set(True)
        table_objets_check = ttk.Checkbutton(generer_labelframe, text="Table des objets",
                                             variable=table_objets_var)
        table_objets_check.grid(sticky="W", row=107, column=1)

        table_chrono_var = tk.BooleanVar()
        table_chrono_var.set(True)
        table_chrono_check = ttk.Checkbutton(generer_labelframe, text="Chronologie des persos",
                                             variable=table_chrono_var)
        table_chrono_check.grid(sticky="W", row=107, column=2)

        table_persos_var = tk.BooleanVar()
        table_persos_var.set(True)
        table_persos_check = ttk.Checkbutton(generer_labelframe, text="Table des persos",
                                             variable=table_persos_var)
        table_persos_check.grid(sticky="W", row=107, column=3)

        table_pnjs_var = tk.BooleanVar()
        table_pnjs_var.set(True)
        table_pnjs_check = ttk.Checkbutton(generer_labelframe, text="Table des pnjs",
                                           variable=table_pnjs_var)
        table_pnjs_check.grid(sticky="W", row=108, column=0)

        aide_de_jeu_var = tk.BooleanVar()
        aide_de_jeu_var.set(True)
        aide_de_jeu_check = ttk.Checkbutton(generer_labelframe, text="Inputs aides de jeu",
                                            variable=aide_de_jeu_var)
        aide_de_jeu_check.grid(sticky="W", row=108, column=1)

        table_commentaires_var = tk.BooleanVar()
        table_commentaires_var.set(True)
        table_commentaires_check = ttk.Checkbutton(generer_labelframe, text="Extraire les commentaires",
                                                   variable=table_commentaires_var)
        table_commentaires_check.grid(sticky="W", row=108, column=2)

        table_relations_var = tk.BooleanVar()
        table_relations_var.set(True)
        table_relations_check = ttk.Checkbutton(generer_labelframe, text="Table des relations",
                                                variable=table_relations_var)
        table_relations_check.grid(sticky="W", row=108, column=3)

        table_evenements_var = tk.BooleanVar()
        table_evenements_var.set(True)
        table_evenements_check = ttk.Checkbutton(generer_labelframe, text="Table des évènements",
                                                 variable=table_evenements_var)
        table_evenements_check.grid(sticky="W", row=109, column=0)

        fichier_erreurs_evenements_var = tk.BooleanVar()
        fichier_erreurs_evenements_var.set(True)
        fichier_erreurs_evenements_check = ttk.Checkbutton(generer_labelframe, text="Fichier erreurs évènements",
                                                           variable=fichier_erreurs_evenements_var)
        fichier_erreurs_evenements_check.grid(sticky="W", row=109, column=1)

        fichier_questionnaire_inscription_var = tk.BooleanVar()
        fichier_questionnaire_inscription_var.set(True)
        fichier_questionnaire_inscription_check = ttk.Checkbutton(generer_labelframe,
                                                                  text="Fichier questionnaire inscription",
                                                                  variable=fichier_questionnaire_inscription_var)
        fichier_questionnaire_inscription_check.grid(sticky="W", row=109, column=2)

        # Buttons
        cancel_button = ttk.Button(generer_labelframe, text="Quitter", command=regen_window.destroy)
        cancel_button.grid(row=200, column=0, pady=(0, 10))

        # ajout des méthodes nécessaires pour gérer le thread
        progression_labelframe = ttk.Labelframe(regen_window, text="Progression de la génération")
        progression_labelframe.grid(row=300, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(10, 10))

        # lecture_label = ttk.Label(progression_labelframe, text="\n Progression de la régénération... \n")
        # lecture_label.grid(row=300, sticky="nsew")

        progress = Progressbar(progression_labelframe, orient='horizontal', length=580, mode='determinate')
        progress.grid(row=301, pady=(25, 10), padx=(25, 10), sticky="ew")

        message_label = ttk.Label(progression_labelframe, text="\n\n\n\n\n", anchor="w")
        message_label.grid(row=302, rowspan=5, padx=(10, 10), sticky="nsew")

        def faire_evoluer_barre(evolution: float):
            # print(f"debug : la valeur de la barre est de {progress['value']}, "
            #       f"j'ai reçu une demande de l'augmenter de {evolution} ")
            if evolution == -100:
                progress['value'] = 0
            elif evolution == 1000:
                progress['value'] = 100
            else:
                progress['value'] += evolution

        def afficher_message_statut(message: str, end='\n'):
            # print(f"debug : on m'a demandé d'afficher {message}")
            current_text = message_label['text']
            # print(f"debug : avant, j'avais le texte suivant :  {current_text}")
            updated_text = current_text + message
            updated_text = '\n'.join(updated_text.splitlines()[-5:]) + end
            # print(f"debug : et à ce stade, on a le texte suivant : {updated_text}")
            message_label['text'] = updated_text

        def t_lancer_regeneration():
            lire_et_recharger_gn(mon_gn=self.gn,
                                 api_drive=self.apiDrive,
                                 api_doc=self.apiDoc,
                                 api_sheets=self.apiSheets,
                                 aides_de_jeu=aide_de_jeu_var.get(),
                                 liste_noms_pjs=self.dict_config.get(
                                     'liste_noms_pjs'),
                                 # noms_pnjs=self.dict_config.get('liste_noms_pnjs'),
                                 nom_fichier_sauvegarde=self.dict_config[
                                     'nom_fichier_sauvegarde'],
                                 fichier_erreurs_intrigues=fichier_erreurs_intrigues_var.get(),
                                 fichier_erreurs_evenements=fichier_erreurs_evenements_var.get(),
                                 generer_fichiers_pjs=generer_fichiers_pj_var.get(),
                                 generer_fichiers_pnjs=generer_fichiers_pnjs_var.get(),
                                 changelog=changelog_var.get(),
                                 table_intrigues=table_intrigues_var.get(),
                                 table_objets=table_objets_var.get(),
                                 table_chrono=table_chrono_var.get(),
                                 table_persos=table_persos_var.get(),
                                 table_pnjs=table_pnjs_var.get(),
                                 table_commentaires=table_commentaires_var.get(),
                                 fast_intrigues=var_fast_intrigue.get(),
                                 fast_persos=var_fast_fiches_pjs.get(),
                                 fast_pnjs=var_fast_fiches_pnjs.get(),
                                 fast_evenements=var_fast_evenements.get(),
                                 fast_objets=var_fast_objets.get(),
                                 sans_chargement_fichier=repartir_de_0_var.get(),
                                 sauver_apres_operation=sauver_apres_operation_var.get(),
                                 verbal=verbal_var.get(),
                                 table_relations=table_relations_var.get(),
                                 table_evenements=table_evenements_var.get(),
                                 table_questionnaire=fichier_questionnaire_inscription_var.get(),
                                 visualisation=faire_evoluer_barre,
                                 m_print=afficher_message_statut
                                 )

        ok_button = ttk.Button(generer_labelframe, text="OK",
                               command=lambda: threading.Thread(target=t_lancer_regeneration).start()
                               )

        ok_button.grid(row=200, column=1, pady=(0, 10))
        boutons = [ok_button, forcer_update_gn_button]
        config_button.config(command=lambda: self.change_config_file(boutons, current_file_label))

        fichier_defaut = fichier_ini_defaut()

        if fichier_defaut:
            self.lire_fichier_config(boutons, current_file_label, config_file=fichier_defaut)
        else:
            self.lire_fichier_config(boutons, current_file_label)

    def updater_boutons_disponibles(self, on: bool, boutons: list):
        to_set = "normal" if on else "disabled"
        for bouton in boutons:
            bouton.config(state=to_set)

    def change_config_file(self, boutons: list, display_label):
        config_file = filedialog.askopenfilename(initialdir=".", title="Select file",
                                                 filetypes=(("ini files", "*.ini"), ("all files", "*.*")))
        self.lire_fichier_config(boutons, display_label, config_file)

    def lire_fichier_config(self, boutons: list, display_label, config_file: str = 'config.ini'):
        try:
            self.dict_config = charger_fichier_init(config_file)
            if self.dict_config is None:
                texte_erreur = "Erreur lors de la lecture du fichier de configuration \n" \
                               "Merci de le vérifier avant de le recharger"
                messagebox.showinfo("Fichier de configuration non valide", texte_erreur)
                self.updater_boutons_disponibles(False, boutons)
                return
            print(f"debug : dict config = {self.dict_config}")
            self.updater_boutons_disponibles(True, boutons)
            display_label.config(text=config_file)
            try:
                self.gn = GN.load(self.dict_config['nom_fichier_sauvegarde'])
                self.gn.injecter_config(dossiers_evenements=self.dict_config['dossiers_evenements'],
                                        dossiers_intrigues=self.dict_config['dossiers_intrigues'],
                                        dossier_output=self.dict_config['dossier_output'],
                                        mode_association=self.dict_config['mode_association'],
                                        dossiers_pj=self.dict_config.get('dossiers_pjs'),
                                        dossiers_pnj=self.dict_config.get('dossiers_pnjs'),
                                        id_factions=self.dict_config.get('id_factions'),
                                        dossiers_objets=self.dict_config.get('dossiers_objets'),
                                        date_gn=self.dict_config.get('date_gn'),
                                        id_pjs_et_pnjs=self.dict_config.get('id_pjs_et_pnjs'),
                                        fichier_pnjs=self.dict_config.get('fichier_noms_pnjs')
                                        )
                # print(f"après injection, nous avons : "
                #       f"dossiers_intrigues={self.dict_config['dossiers_intrigues'],}"
                #       f"dossier_output= {self.dict_config['dossier_output']},"
                #       f"association_auto= {self.dict_config['association_auto']},"
                #       f"dossiers_pj= {self.dict_config.get('dossiers_pjs')},"
                #       f"dossiers_pnj= {self.dict_config.get('dossiers_pnjs')},"
                #       f"id_factions= {self.dict_config.get('id_factions')}")

            except Exception as f:
                print(traceback.format_exc())
                print(f"une erreur est survenue qui a conduit à re-créer un self : {f}")
                print(f"le self {self.dict_config['nom_fichier_sauvegarde']} n'existe pas, j'en crée un nouveau")
                self.gn = GN(dossiers_intrigues=self.dict_config['dossiers_intrigues'],
                             dossier_output=self.dict_config['dossier_output'],
                             mode_association=self.dict_config['mode_association'],
                             dossiers_pj=self.dict_config.get('dossiers_pjs'),
                             dossiers_pnj=self.dict_config.get('dossiers_pjs'),
                             id_factions=self.dict_config.get('id_factions'),
                             id_pjs_et_pnjs=self.dict_config.get('id_pjs_et_pnjs'),
                             dossiers_evenements=self.dict_config.get('dossiers_evenements')
                             )
            if self.apiDoc is None or self.apiSheets is None or self.apiDrive is None:
                self.apiDrive, self.apiDoc, self.apiSheets = lecteurGoogle.creer_lecteurs_google_apis()

            if not self.derniere_version:
                self.derniere_version, self.maj_versions, self.url_derniere_version = \
                    verifier_derniere_version(self.apiDoc)
                if not self.derniere_version:
                    # if not the latest version, show a popup with options to download or wait
                    response = messagebox.askquestion("Un nouvelle version est disponible !",
                                                      f"souhaitez-vous télécharger la mise à jour ? \n "
                                                      f"{self.maj_versions}",
                                                      icon="warning")
                    if response == "yes":
                        # if "Download" button clicked, open the latest version URL in the web browser
                        webbrowser.open_new(self.url_derniere_version)


        except Exception as e:
            if "Token has been expired or revoked." in str(e):
                # if token has been expired or revoked, show a popup with a specific error message
                messagebox.showerror("Expirations des droits",
                                     "Le fichier token.json a expiré. \n"
                                     "Pas de panique ! \n\n"
                                     "1. Supprimez-le \n"
                                     "2. Rechargez le fichier de paramètres \n"
                                     "3. Suivez les instructions sur la page web google qui s'affiche "
                                     "pour vous ré-authentifier \n\n"
                                     "Pour plus d'informations sur cette erreur liée à google, consulter le manuel")
                print(f"une erreur RefreshError est survenue pendant la lecture du fichier ini : {e}")

            elif "The OAuth client was deleted." in str(e):
                # if OAuth client was deleted, show a popup with a specific error message
                messagebox.showerror("Cette version de MAGnet a expiré",
                                     "Cette version de MAGnet a expiré. '\n'"
                                     "pour continuer à l'utiliser, merci de télécharger la dernière version")

            else:
                # if other RefreshError is raised, show a popup with a generic error message
                messagebox.showerror("Error", "Erreur inattendue.")
                logging.debug(f"Erreur inattendue dans la lecture du fichier de configuration : {e}")

            traceback.print_exc()
            self.dict_config = None
            self.updater_boutons_disponibles(False, boutons)


        except Exception as e:
            print(f"une erreur est survenue pendant la lecture du fichier ini : {e}")
            traceback.print_exc()
            self.dict_config = None
            self.updater_boutons_disponibles(False, boutons)

    def afficher_resultats(self, resultats, test_global_reussi):
        root = tk.Tk()

        if test_global_reussi:
            root.title("Tests Réussis")
            # root.iconbitmap("success_icon.ico")  # Remplacez par le chemin vers l'icône de succès
        else:
            root.title("Tests Échoués")
            # root.iconbitmap("failure_icon.ico")  # Remplacez par le chemin vers l'icône d'échec

        tree = ttk.Treeview(root, columns=("Paramètre", "Nom du fichier lu", "Résultat du test"))

        tree.heading("#0", text="")
        tree.column("#0", width=0, minwidth=0, stretch=tk.NO)

        tree.heading("Paramètre", text="Nom du paramètre")
        tree.column("Paramètre", anchor=tk.W)

        tree.heading("Nom du fichier lu", text="Nom du fichier lu")
        tree.column("Nom du fichier lu", anchor=tk.W)

        tree.heading("Résultat du test", text="Résultat du test")
        tree.column("Résultat du test", anchor=tk.W)

        for res in resultats:
            tree.insert('', tk.END, values=(res[0], res[1], res[2]))

        tree.pack(padx=10, pady=10)

        root.mainloop()

    def verifier_config_et_afficher_popup(self, current_file_label):
        if self.dict_config:
        # if config_dict := charger_fichier_init(str(current_file_label)):
            resultats, test_reussi = extraireTexteDeGoogleDoc.verifier_fichier_config(self.dict_config,
                                                                                      self.apiDrive,
                                                                                      self.apiDoc,
                                                                                      self.apiSheets)
            print(resultats)
            self.afficher_resultats(resultats, test_reussi)
        else:
            messagebox.showerror("Erreur", "Erreur lors du chargement du fichier de configuration.")