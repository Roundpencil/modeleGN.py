import sys
import tkinter as tk
from tkinter import filedialog
from MAGnet_lib import *
from modeleGN import GN


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("MAGnet")
        self.master.geometry("220x150")
        # self.grid()
        # self.create_widgets()
        self.gn = None
        self.dict_config = None
        self.apiDrive = None
        self.apiDoc = None
        self.apiSheets = None

        # Create the buttons
        self.create_gn_button = tk.Button(self.master, text="Créer nouveau GN", command=self.create_new_gn)
        self.create_gn_button.grid(row=0, column=0, sticky="nsew")

        self.regen_button = tk.Button(self.master, text="Régénérer", command=self.regen)
        self.regen_button.grid(row=1, column=0, sticky="nsew")

        self.diagnostic_button = tk.Button(self.master, text="Mode diagnostic", command=self.diagnostic_mode)
        self.diagnostic_button.grid(row=2, column=0, sticky="nsew")

        self.config_button = tk.Button(self.master, text="Changer fichier de configuration",
                                       command=self.change_config_file)
        self.config_button.grid(row=3, column=0, sticky="nsew")

        self.edit_config_button = tk.Button(self.master, text="Modifier  fichier de configuration",
                                            command=self.modify_config)
        self.edit_config_button.grid(row=4, column=0, sticky="nsew")

        # Create the label
        self.current_file_label = tk.Label(self.master, text="Fichier ini actuel : Aucun")
        self.current_file_label.grid(row=5, column=0, columnspan=2, sticky='w')
        self.lire_fichier_config()

    def update_button_state(self):
        if not self.dict_config:
            self.regen_button.config(state="disabled")
            self.diagnostic_button.config(state="disabled")
            self.edit_config_button.config(state="disabled")

        else:
            self.regen_button.config(state="normal")
            self.diagnostic_button.config(state="normal")
            self.edit_config_button.config(state="normal")

    # def create_widgets(self):
    #     self.new_gn_button = tk.Button(self, text="Créer nouveau GN", command=self.create_new_gn)
    #     self.new_gn_button.grid(row=0, column=0)
    #
    #     self.update_button = tk.Button(self, text="Générer fiches mises à jour", command=self.regen)
    #     self.update_button.grid(row=0, column=1)
    #
    #     self.diagnostic_button = tk.Button(self, text="Mode diagnostic", command=self.diagnostic_mode)
    #     self.diagnostic_button.grid(row=0, column=2)
    #
    #     self.config_file_button = tk.Button(self, text="Changer fichier de configuration",
    #                                         command=self.change_config_file)
    #     self.config_file_button.grid(row=1, column=0)
    #
    #     self.current_file_label = tk.Label(self, text="Fichier ini actuel")
    #     self.current_file_label.grid(row=1, column=1)

    def create_new_gn(self):
        new_gn_window = tk.Toplevel(self.master)
        new_gn_window.title("Créer nouveau GN")
        new_gn_window.geometry("450x270")

        intrigues_label = tk.Label(new_gn_window, text="Intrigues")
        intrigues_label.grid(row=0, column=0)
        intrigues_entry = tk.Entry(new_gn_window)
        intrigues_entry.grid(row=0, column=1)

        base_persos_gn_label = tk.Label(new_gn_window, text="Base persos GN")
        base_persos_gn_label.grid(row=1, column=0)
        base_persos_gn_entry = tk.Entry(new_gn_window)
        base_persos_gn_entry.grid(row=1, column=1)

        # fichier_faction_label = tk.Label(new_gn_window, text="Fichier faction")
        # fichier_faction_label.grid(row=2, column=0)
        # fichier_faction_entry = tk.Entry(new_gn_window)
        # fichier_faction_entry.grid(row=2, column=1)

        id_factions_label = tk.Label(new_gn_window, text="ID factions")
        id_factions_label.grid(row=3, column=0)
        id_factions_entry = tk.Entry(new_gn_window)
        id_factions_entry.grid(row=3, column=1)

        dossier_output_squelettes_pjs_label = tk.Label(new_gn_window, text="Dossier output")
        dossier_output_squelettes_pjs_label.grid(row=4, column=0)
        dossier_output_squelettes_pjs_entry = tk.Entry(new_gn_window)
        dossier_output_squelettes_pjs_entry.grid(row=4, column=1)

        association_auto_label = tk.Label(new_gn_window, text="Association auto")
        association_auto_label.grid(row=5, column=0)
        association_auto_var = tk.IntVar()
        association_auto_yes = tk.Radiobutton(new_gn_window, text="Oui", variable=association_auto_var, value=1)
        association_auto_yes.grid(row=5, column=1)
        association_auto_no = tk.Radiobutton(new_gn_window, text="Non", variable=association_auto_var, value=0)
        association_auto_no.grid(row=5, column=2)

        type_fiche_label = tk.Label(new_gn_window, text="Type de fiche")
        type_fiche_label.grid(row=6, column=0)
        type_fiche_var = tk.StringVar(new_gn_window)
        type_fiche_var.set("Chalacta")
        type_fiche_dropdown = tk.OptionMenu(new_gn_window, type_fiche_var, "Chalacta", "Modèle 7 colonnes")
        type_fiche_dropdown.grid(row=6, column=1)

        nom_fichier_sauvegarde_label = tk.Label(new_gn_window, text="Nom fichier sauvegarde")
        nom_fichier_sauvegarde_label.grid(row=7, column=0)
        nom_fichier_sauvegarde_entry = tk.Entry(new_gn_window)
        nom_fichier_sauvegarde_entry.grid(row=7, column=1)

        noms_persos_label = tk.Label(new_gn_window, text="Noms persos")
        noms_persos_label.grid(row=8, column=0)
        noms_persos_entry = tk.Entry(new_gn_window)
        noms_persos_entry.grid(row=8, column=1)

        nom_fichier_pnjs_label = tk.Label(new_gn_window, text="Nom fichier PNJs")

        nom_fichier_pnjs_label.grid(row=9, column=0)
        nom_fichier_pnjs_entry = tk.Entry(new_gn_window)
        nom_fichier_pnjs_entry.grid(row=9, column=1)

        submit_button = tk.Button(new_gn_window, text="Valider",
                                  command=lambda: self.submit_new_gn(intrigues_entry.get(), base_persos_gn_entry.get(),
                                                                     id_factions_entry.get(),
                                                                     dossier_output_squelettes_pjs_entry.get(),
                                                                     association_auto_var.get(), type_fiche_var.get(),
                                                                     nom_fichier_sauvegarde_entry.get(),
                                                                     noms_persos_entry.get(),
                                                                     nom_fichier_pnjs_entry.get(),
                                                                     new_gn_window))
        submit_button.grid(row=10, column=0)

    def submit_new_gn(self, intrigues, base_persos_gn, id_factions, dossier_output_squelettes_pjs,
                      association_auto, type_fiche, nom_fichier_sauvegarde, noms_persos, nom_fichier_pnjs, window):
        # Do something with the user's input
        print(f"Intrigues: {intrigues}")
        print(f"Base persos GN: {base_persos_gn}")
        print(f"ID factions: {id_factions}")
        print(f"Dossier output squelettes PJs: {dossier_output_squelettes_pjs}")
        print(f"Association auto: {association_auto}")
        print(f"Type de fiche: {type_fiche}")
        print(f"Nom fichier sauvegarde: {nom_fichier_sauvegarde}")
        print(f"Noms persos: {noms_persos}")
        print(f"Nom fichier PNJs: {nom_fichier_pnjs}")
        window.destroy()

    def diagnostic_mode(self):
        diagnostic_window = tk.Toplevel(self.master)

        recharger_gn_button = tk.Button(diagnostic_window, text="Recharger GN", command=lambda: print("Recharger GN"))
        recharger_gn_button.grid(row=0, column=0, sticky="nsew")

        relire_intrigues_button = tk.Button(diagnostic_window, text="Relire toutes les intrigues",
                                            command=lambda: extraireTexteDeGoogleDoc.extraire_intrigues(
                                                self.gn, self.apiDrive, self.apiDoc, fast=False)
                                            )
        relire_intrigues_button.grid(row=1, column=0, sticky="nsew")

        relire_persos_button = tk.Button(diagnostic_window, text="Relire tous les personnages",
                                         command=lambda: extraireTexteDeGoogleDoc.extraire_pjs(
                                             self.gn, self.apiDrive, self.apiDoc, fast=False)
                                         )
        relire_persos_button.grid(row=2, column=0, sticky="nsew")

        relire_perso_spec_button = tk.Button(diagnostic_window, text="Relire un personnage spécifique",
                                             command=lambda: print("Relire un personnage spécique"))
        relire_perso_spec_button.grid(row=3, column=0, sticky="nsew")

        relire_intrigue_spec_button = tk.Button(diagnostic_window, text="Relire une intrigue spécifique",
                                                command=lambda: print("Relire une intrigue spécifique"))
        relire_intrigue_spec_button.grid(row=4, column=0, sticky="nsew")

        effacer_persos_force_button = tk.Button(diagnostic_window, text="Effacer les personnages forcés",
                                                command=lambda: self.gn.effacer_personnages_forces())
        effacer_persos_force_button.grid(row=5, column=0, sticky="nsew")

        importer_persos_config_button = tk.Button(diagnostic_window,
                                                  text="Importer les personnages du fichier de configuration",
                                                  command=lambda: self.gn.forcer_import_pjs(
                                                      self.dict_config['noms_persos'])
                                                  )
        importer_persos_config_button.grid(row=6, column=0, sticky="nsew")

        importer_pnjs_button = tk.Button(diagnostic_window, text="Ré-importer les PNJs d'après le fichier",
                                         command=lambda: self.gn.forcer_import_pnjs(
                                             lire_fichier_pnjs(self.dict_config['fichier_noms_pnjs']))
                                         )
        importer_pnjs_button.grid(row=7, column=0, sticky="nsew")

        sauvegarder_gn_button = tk.Button(diagnostic_window, text="Sauvegarder le GN",
                                          command=lambda: self.gn.save(self.dict_config['nom_fichier_sauvegarde'])
                                          )
        sauvegarder_gn_button.grid(row=8, column=0, sticky="nsew")

        generer_liste_ref_pnj_button = tk.Button(diagnostic_window,
                                                 text="Générer liste de référence des PNJs dédupliqués",
                                                 command=lambda: ecrire_liste_pnj_dedup_localement(
                                                     self.gn, str(datetime.date.today()))
                                                 )
        generer_liste_ref_pnj_button.grid(row=9, column=0, sticky="nsew")

        generer_fichier_association_button = tk.Button(diagnostic_window, text="Générer le fichier d'association",
                                                       command=lambda: print("Générer le fichier d'association"))
        generer_fichier_association_button.grid(row=10, column=0, sticky="nsew")

        lire_fichier_association_button = tk.Button(diagnostic_window, text="Lire le fichier d'associations",
                                                    command=lambda: print("Lire le fichier d'associations"))
        lire_fichier_association_button.grid(row=11, column=0, sticky="nsew")

        generer_changelog_drive_button = tk.Button(diagnostic_window, text="Générer changelog dans Drive",
                                                   command=lambda: generer_tableau_changelog_sur_drive(
                                                       self.gn, self.apiDrive, self.apiSheets,
                                                       self.dict_config['dossier_output'])
                                                   )
        generer_changelog_drive_button.grid(row=12, column=0, sticky="nsew")

        generer_changelog_local_button = tk.Button(diagnostic_window, text="Générer changelog localement",
                                                   command=lambda: genererChangeLog(
                                                       self.gn, str(datetime.date.today()))
                                                   )
        generer_changelog_local_button.grid(row=13, column=0, sticky="nsew")

        generer_erreurs_local_button = tk.Button(diagnostic_window, text="Générer fichier des erreurs localement",
                                                 command=lambda: lister_erreurs(self.gn, str(datetime.date.today())))
        generer_erreurs_local_button.grid(row=14, column=0, sticky="nsew")

        generer_erreurs_drive_button = tk.Button(diagnostic_window, text="Générer fichier des erreurs sur Drive",
                                                 command=lambda:
                                                 ecrire_erreurs_dans_drive(
                                                     lister_erreurs(self.gn, None),
                                                     self.apiDoc, self.apiDrive, self.dict_config['dossier_output']))
        generer_erreurs_drive_button.grid(row=15, column=0, sticky="nsew")

        generer_table_intrigues_drive_button = tk.Button(diagnostic_window,
                                                         text="Générer table des intrigues sur Drive",
                                                         command=lambda: creer_table_intrigues_sur_drive(
                                                             self.gn, self.apiSheets, self.apiDrive,
                                                             self.dict_config['dossier_output'])
                                                         )
        generer_table_intrigues_drive_button.grid(row=16, column=0, sticky="nsew")

        generer_table_intrigues_local_button = tk.Button(diagnostic_window,
                                                         text="Générer table des intrigues localement",
                                                         command=lambda: print(
                                                             "Générer table des intrigues localement"))
        generer_table_intrigues_local_button.grid(row=17, column=0, sticky="nsew")

        generer_fiches_pj_drive_button = tk.Button(diagnostic_window, text="Générer fiches PJ dans Drive",
                                                   command=lambda: generer_squelettes_dans_drive(
                                                       self.gn, self.apiDoc, self.apiDrive, True)
                                                   )
        generer_fiches_pj_drive_button.grid(row=18, column=0, sticky="nsew")

        generer_fiches_pnj_drive_button = tk.Button(diagnostic_window, text="Générer fiches PNJ dans Drive",
                                                    command=lambda: lambda: generer_squelettes_dans_drive(
                                                        self.gn, self.apiDoc, self.apiDrive, False)
                                                    )
        generer_fiches_pnj_drive_button.grid(row=19, column=0, sticky="nsew")

        generer_fiches_pj_local_button = tk.Button(diagnostic_window, text="Générer fiches PJ localement",
                                                   command=lambda: ecrire_squelettes_localement(
                                                       self.gn, str(datetime.date.today()), pj=True)
                                                   )
        generer_fiches_pj_local_button.grid(row=20, column=0, sticky="nsew")

        generer_fiches_pnj_local_button = tk.Button(diagnostic_window, text="Générer fiches PNJ localement",
                                                    command=lambda: ecrire_squelettes_localement(
                                                        self.gn, str(datetime.date.today()), pj=False)
                                                    )
        generer_fiches_pnj_local_button.grid(row=21, column=0, sticky="nsew")

        generer_table_pnj_local_button = tk.Button(diagnostic_window, text="Générer table des PNJs localement",
                                                   command=lambda: print("Générer table des PNJs localement"))
        generer_table_pnj_local_button.grid(row=22, column=0, sticky="nsew")

        relire_factions_button = tk.Button(diagnostic_window, text="Relire les factions",
                                           command=lambda: print("Relire les factions"))
        relire_factions_button.grid(row=23, column=0, sticky="nsew")
        # diagnostic_window = tk.Toplevel(self.master)
        # diagnostic_window.title("Mode diagnostic")
        # diagnostic_window.geometry("400x400")
        #
        # # Create the 3x3 button grid
        # for i in range(3):
        #     for j in range(3):
        #         button = tk.Button(diagnostic_window)
        #         button.grid(row=i, column=j)

    def change_config_file(self):
        config_file = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                 filetypes=(("ini files", "*.ini"), ("all files", "*.*")))
        self.lire_fichier_config(config_file)

    def lire_fichier_config(self, config_file: str = 'config.ini'):
        try:
            self.dict_config = charger_fichier_init(config_file)
            # print("ping")
            self.update_button_state()
            self.current_file_label.config(text=config_file)
            try:
                self.gn = GN.load(self.dict_config['nom_fichier_sauvegarde'])
            except Exception as f:
                print(f"le gn {self.dict_config['nom_fichier_sauvegarde']} n'existe pas, j'en crée un nouveau")
                self.gn = GN(self.dict_config["intrigues"], self.dict_config["dossier_pj"],
                             self.dict_config["dossier_output_squelettes_pjs"],
                             self.dict_config["id_factions"])
            if self.apiDoc is None or self.apiSheets is None or self.apiDrive is None:
                self.apiDrive, self.apiDoc, self.apiSheets = lecteurGoogle.creer_lecteurs_google_apis()

        except Exception as e:
            print(f"une erreur est survenue pendant la lecture du fichier ini : {e}")
            self.dict_config = None
            self.update_button_state()

    def modify_config(self):
        config_window = tk.Toplevel(self.master)
        # for key in self.dict_config:
        #     print(f"{key}:{self.dict_config[key]} type : {type(self.dict_config[key])}")

        tk.Label(config_window, text="Intrigues").grid(row=0, column=0)
        intrigues_entry = tk.Entry(config_window)
        intrigues_entry.insert(0, ",".join(self.dict_config['dossier_intrigues']))
        intrigues_entry.grid(row=0, column=1)

        tk.Label(config_window, text="Base persos gn").grid(row=1, column=0)
        base_persos_gn_entry = tk.Entry(config_window)
        base_persos_gn_entry.insert(0, ",".join(self.dict_config['dossier_pjs']))
        base_persos_gn_entry.grid(row=1, column=1)

        tk.Label(config_window, text="Id factions").grid(row=3, column=0)
        id_factions_entry = tk.Entry(config_window)
        id_factions_entry.insert(0, self.dict_config['id_factions'])
        id_factions_entry.grid(row=3, column=1)

        tk.Label(config_window, text="Dossier output").grid(row=4, column=0)
        dossier_output_squelettes_pjs_entry = tk.Entry(config_window)
        dossier_output_squelettes_pjs_entry.insert(0, self.dict_config['dossier_output'])
        dossier_output_squelettes_pjs_entry.grid(row=4, column=1)

        tk.Label(config_window, text="Association auto").grid(row=5, column=0)
        association_auto_var = tk.StringVar(value=self.dict_config['association_auto'])
        association_auto_yes = tk.Radiobutton(config_window, text="Oui", variable=association_auto_var, value="oui")
        association_auto_yes.grid(row=5, column=1)
        association_auto_no = tk.Radiobutton(config_window, text="Non", variable=association_auto_var, value="non")
        association_auto_no.grid(row=5, column=2)

        tk.Label(config_window, text="Type fiche").grid(row=6, column=0)
        type_fiche_var = tk.StringVar(value=self.dict_config['type_fiche'])
        type_fiche_chalacta = tk.Radiobutton(config_window, text="Chalacta / modele 7 colonnes",
                                             variable=type_fiche_var, value="Chalacta / modele 7 colonnes")
        type_fiche_chalacta.grid(row=6, column=1)
        type_fiche_autre = tk.Radiobutton(config_window, text="Autre", variable=type_fiche_var, value="autre")
        type_fiche_autre.grid(row=6, column=2)

        tk.Label(config_window, text="Nom fichier sauvegarde").grid(row=7, column=0)
        nom_fichier_sauvegarde_entry = tk.Entry(config_window)
        nom_fichier_sauvegarde_entry.insert(0, self.dict_config['nom_fichier_sauvegarde'])
        nom_fichier_sauvegarde_entry.grid(row=7, column=1)

        tk.Label(config_window, text="Noms persos").grid(row=8, column=0)

        noms_persos_entry = tk.Entry(config_window)
        noms_persos_entry.insert(0, ",".join(self.dict_config['noms_persos']))
        noms_persos_entry.grid(row=8, column=1)

        tk.Label(config_window, text="Nom fichier pnjs").grid(row=9, column=0)
        nom_fichier_pnjs_entry = tk.Entry(config_window)
        nom_fichier_pnjs_entry.insert(0, self.dict_config['fichier_noms_pnjs'])
        nom_fichier_pnjs_entry.grid(row=9, column=1)

        ok_button = tk.Button(config_window, text="Valider", command=lambda: self.validate_config(
            intrigues_entry.get(), base_persos_gn_entry.get(), id_factions_entry.get(),
            dossier_output_squelettes_pjs_entry.get(),
            association_auto_var.get(), type_fiche_var.get(), nom_fichier_sauvegarde_entry.get(),
            noms_persos_entry.get(),
            nom_fichier_pnjs_entry.get(), config_window)
                              )

        ok_button.grid(row=11, column=0)
        cancel_button = tk.Button(config_window, text="Annuler", command=config_window.destroy)
        cancel_button.grid(row=11, column=1)

    def validate_config(self, intrigues, base_persos_gn, id_factions, dossier_output_squelettes_pjs,
                        association_auto, type_fiche, nom_fichier_sauvegarde, noms_persos, nom_fichier_pnjs,
                        config_window):

        # Create a dictionary with the entered values
        dict_config = {"dossier_intrigues": intrigues.split(','),
                       "dossier_pjs": base_persos_gn.split(',') ,
                       "id_factions": id_factions,
                       "dossier_output": dossier_output_squelettes_pjs,
                       "association_auto": association_auto,
                       "type_fiche": type_fiche,
                       "nom_fichier_sauvegarde": nom_fichier_sauvegarde,
                       "noms_persos": noms_persos.split(","),
                       "fichier_noms_pnjs": nom_fichier_pnjs}

        nom_fichier = nom_fichier_sauvegarde + ".ini"
        ecrire_fichier_config(dict_config, nom_fichier)
        self.lire_fichier_config(nom_fichier)
        # Do something with the config_dict, like saving it to a file
        # for key in dict_config:
        #     print(f"{key}:{dict_config[key]} type : {type(dict_config[key])}")

        # Close the configuration window
        config_window.destroy()

    def regen(self):
        regen_window = tk.Toplevel(self.master)
        regen_window.geometry("600x150")  # adjust the size of the window

        # Intrigues
        intrigues_label = tk.Label(regen_window, text="Intrigues")
        intrigues_label.grid(row=0, column=0, columnspan=2)

        intrigues_var = tk.StringVar(regen_window)
        intrigues_var.set("Rapide")

        intrigues_rapide = tk.Radiobutton(regen_window, text="Rapide", variable=intrigues_var, value="Rapide",
                                          command=lambda: self.regen_intrigue_select("Rapide"))
        intrigues_rapide.grid(row=1, column=0)
        intrigues_complet = tk.Radiobutton(regen_window, text="Complet", variable=intrigues_var, value="Complet",
                                           command=lambda: self.regen_intrigue_select("Complet"))
        intrigues_complet.grid(row=1, column=1)
        intrigues_specifique = tk.Radiobutton(regen_window, text="Spécifique", variable=intrigues_var,
                                              value="Spécifique",
                                              command=lambda: self.regen_intrigue_select("Spécifique"))
        intrigues_specifique.grid(row=1, column=2)

        self.intrigue_specifique_entry = tk.Entry(regen_window)
        self.intrigue_specifique_entry.grid(row=1, column=3)
        self.intrigue_specifique_entry.config(state='disabled')

        # Personnages
        personnages_label = tk.Label(regen_window, text="Personnages")
        personnages_label.grid(row=2, column=0, columnspan=2)

        personnages_var = tk.StringVar(regen_window)
        personnages_var.set("Rapide")

        personnages_rapide = tk.Radiobutton(regen_window, text="Rapide", variable=personnages_var, value="Rapide",
                                            command=lambda: self.regen_personnages_select("Rapide"))
        personnages_rapide.grid(row=3, column=0)
        personnages_complet = tk.Radiobutton(regen_window, text="Complet", variable=personnages_var, value="Complet",
                                             command=lambda: self.regen_personnages_select("Complet"))
        personnages_complet.grid(row=3, column=1)
        personnages_specifique = tk.Radiobutton(regen_window, text="Spécifique", variable=personnages_var,
                                                value="Spécifique",
                                                command=lambda: self.regen_personnages_select("Spécifique"))
        personnages_specifique.grid(row=3, column=2)

        self.personnages_specifique_entry = tk.Entry(regen_window)
        self.personnages_specifique_entry.grid(row=3, column=3)
        self.personnages_specifique_entry.config(state='disabled')

        charger_fichier_var = tk.BooleanVar()
        charger_fichier_var.set(True)
        charger_fichier_check = tk.Checkbutton(regen_window, text="Charger depuis fichier",
                                               variable=charger_fichier_var)
        charger_fichier_check.grid(row=4, column=0)

        sauver_apres_operation_var = tk.BooleanVar()
        sauver_apres_operation_var.set(True)
        sauver_apres_operation_check = tk.Checkbutton(regen_window, text="Sauver après opération",
                                                      variable=sauver_apres_operation_var)
        sauver_apres_operation_check.grid(row=4, column=1)

        generer_fichiers_drive_var = tk.BooleanVar()
        generer_fichiers_drive_var.set(True)
        generer_fichiers_drive_check = tk.Checkbutton(regen_window, text="Générer fichiers Drive",
                                                      variable=generer_fichiers_drive_var)
        generer_fichiers_drive_check.grid(row=4, column=2)

        # Buttons
        cancel_button = tk.Button(regen_window, text="Annuler", command=regen_window.destroy)
        cancel_button.grid(row=5, column=0)

        ok_button = tk.Button(regen_window, text="OK",
                              command=lambda: self.process_regen(intrigues_var.get(), personnages_var.get(),
                                                                 charger_fichier_var.get(),
                                                                 sauver_apres_operation_var.get(),
                                                                 generer_fichiers_drive_var.get()))
        ok_button.grid(row=5, column=1)

    # def regen(self):
    #     regen_window = tk.Toplevel(self.master)
    #     regen_window.title("Régénération")
    #     regen_window.geometry("500x500")
    #
    #     # Intrigues
    #     intrigues_label = tk.Label(regen_window, text="Intrigues :")
    #     intrigues_label.grid(row=0, column=0)
    #
    #     intrigues_var = tk.StringVar(regen_window)
    #     intrigues_var.set("Rapide")
    #
    #     intrigues_rapide = tk.Radiobutton(regen_window, text="Rapide", variable=intrigues_var, value="Rapide",
    #                                       command=lambda: self.regen_intrigue_select("Rapide"))
    #     intrigues_rapide.grid(row=0, column=1)
    #     intrigues_complet = tk.Radiobutton(regen_window, text="Complet", variable=intrigues_var, value="Complet",
    #                                        command=lambda: self.regen_intrigue_select("Complet"))
    #     intrigues_complet.grid(row=0, column=2)
    #     intrigues_specifique = tk.Radiobutton(regen_window, text="Spécifique", variable=intrigues_var, value="Spécifique",
    #                                           command=lambda: self.regen_intrigue_select("Spécifique"))
    #     intrigues_specifique.grid(row=0, column=3)
    #
    #     self.intrigue_specifique_entry = tk.Entry(regen_window)
    #     self.intrigue_specifique_entry.grid(row=1, column=1, columnspan=3)
    #     self.intrigue_specifique_entry.config(state='disabled')
    #
    #     # Personnages
    #     personnages_label = tk.Label(regen_window, text="Personnages :")
    #     personnages_label.grid(row=2, column=0)
    #
    #     personnages_var = tk.StringVar(regen_window)
    #
    #
    #     personnages_var.set("Rapide")
    #
    #     personnages_rapide = tk.Radiobutton(regen_window, text="Rapide", variable=personnages_var, value="Rapide",
    #                                         command=lambda: self.regen_personnages_select("Rapide"))
    #     personnages_rapide.grid(row=2, column=1)
    #     personnages_complet = tk.Radiobutton(regen_window, text="Complet", variable=personnages_var, value="Complet",
    #                                          command=lambda: self.regen_personnages_select("Complet"))
    #     personnages_complet.grid(row=2, column=2)
    #     personnages_specifique = tk.Radiobutton(regen_window, text="Spécifique", variable=personnages_var, value="Spécifique",
    #                                             command=lambda: self.regen_personnages_select("Spécifique"))
    #     personnages_specifique.grid(row=2, column=3)
    #
    #     self.personnages_specifique_entry = tk.Entry(regen_window)
    #     self.personnages_specifique_entry.grid(row=3, column=1, columnspan=3)
    #     self.personnages_specifique_entry.config(state='disabled')
    #
    #     # Checkboxes
    #     charger_fichier_var = tk.IntVar(value=1)
    #     charger_fichier_checkbox = tk.Checkbutton(regen_window, text="Charger depuis fichier", variable=charger_fichier_var)
    #     charger_fichier_checkbox.grid(row=4, column=0)
    #
    #     sauver_apres_operation_var = tk.IntVar(value=1)
    #     sauver_apres_operation_checkbox = tk.Checkbutton(regen_window, text="Sauver après opération",
    #                                                      variable=sauver_apres_operation_var)
    #     sauver_apres_operation_checkbox.grid(row=4, column=1)
    #
    #     generer_fichiers_drive_var = tk.IntVar(value=1)
    #     generer_fichiers_drive_checkbox = tk.Checkbutton(regen_window, text="Générer fichiers Drive",
    #                                                      variable=generer_fichiers_drive_var)
    #     generer_fichiers_drive_checkbox.grid(row=4, column=2)
    #
    #     # Buttons
    #     cancel_button = tk.Button(regen_window, text="Annuler", command=regen_window.destroy)
    #     cancel_button.grid(row=5, column=0)
    #
    #     ok_button = tk.Button(regen_window, text="OK",
    #                           command=lambda: self.process_regen(intrigues_var.get(), personnages_var.get(),
    #                                                              charger_fichier_var.get(), sauver_apres_operation_var.get(),
    #                                                              generer_fichiers_drive_var.get()))
    #     ok_button.grid(row=5, column=1)

    def regen_intrigue_select(self, value):
        if value == "Rapide" or value == "Complet":
            self.intrigue_specifique_entry.config(state='disabled')
        elif value == "Spécifique":
            self.intrigue_specifique_entry.config(state='normal')

    def regen_personnages_select(self, value):
        if value == "Rapide" or value == "Complet":
            self.personnages_specifique_entry.config(state='disabled')
        elif value == "Spécifique":
            self.personnages_specifique_entry.config(state='normal')

    def process_regen(self, intrigues_value, personnages_value, charger_fichier_value, sauver_apres_operation_value,
                      generer_fichiers_drive_value):
        if intrigues_value == "Spécifique":
            intrigue_specifique = self.intrigue_specifique_entry.get()
        else:
            intrigue_specifique = ""
        if personnages_value == "Spécifique":
            personnages_specifique = self.personnages_specifique_entry.get()
        else:
            personnages_specifique = ""
        # Call the existing method that process the result with the input values:
        print(f"{intrigues_value}, {intrigue_specifique}, {personnages_value}, {personnages_specifique}, "
              f"{charger_fichier_value}, {sauver_apres_operation_value}, {generer_fichiers_drive_value}")

        if intrigues_value != "Spécifique":
            intrigue_specifique = "-01"
        if personnages_value != "Spécifique":
            personnages_specifique = "-01"

        lire_et_recharger_gn(self.gn, self.apiDrive, self.apiDoc, self.apiSheets,
                             self.dict_config['nom_fichier_sauvegarde'],
                             self.dict_config['dossier_output'],
                             noms_pjs=self.dict_config['noms_persos'],
                             noms_pnjs=self.dict_config['noms_pnjs'],
                             fichier_erreurs=True, export_drive=generer_fichiers_drive_value, changelog=True,
                             table_intrigues=True, fast_intrigues=(intrigues_value == "Rapide"),
                             fast_persos=(personnages_value == "Rapide"),
                             singletest_perso=personnages_specifique, singletest_intrigue=intrigue_specifique)


# todo : à tester
# ajouter les options actuellement forcées à true


#                               self.dict_config['dossier_intrigues'] = dossier_intrigues
# self.dict_config['dossier_pjs'] = dossier_pjs
# self.dict_config['id_factions'] = id_factions
# self.dict_config['dossier_output_squelettes_pjs'] = dossier_output_squelettes_pjs
# self.dict_config['noms_persos'] = noms_persos
# self.dict_config['nom_fichier_pnjs'] = nom_fichier_pnjs
# self.dict_config['association_auto'] = association_auto
# self.dict_config['type_fiche'] = type_fiche
# self.dict_config['nom_fichier_sauvegarde'] = nom_fichier_sauvegarde

def main():
    sys.setrecursionlimit(5000)  # mis en place pour prévenir pickle de planter
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


if __name__ == '__main__':
    main()
