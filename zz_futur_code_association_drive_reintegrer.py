
# j'aimerais créer une fonction update_roles_from_drive qui fonctionne comme update_roles_from_csv, mais au lieu de lire un fichier dsv ouvre un document google sheets pour y lire les valeurs
# This content may violate our content policy. If you believe this to be in error, please submit your feedback — your input will aid our research in this area.

# Bien sûr! Pour lire les valeurs d'un document Google Sheets, vous pouvez utiliser l'API Google Sheets. Vous devrez d'abord installer l'API et créer des identifiants de développeur pour obtenir une clé d'accès.
# Une fois que vous avez accès à l'API, vous pouvez utiliser des méthodes pour lire les données d'une feuille de calcul spécifique. Par exemple, pour lire toutes les valeurs d'une feuille de calcul, vous pouvez utiliser la méthode get de la classe api_doc.spreadsheets() de l'API, en spécifiant l'ID de la feuille de calcul et la plage de cellules à lire.

# Voici un exemple de fonction "update_roles_from_drive" qui lira les valeurs d'un document Google Sheets pour mettre à jour les rôles d'une intrigue:

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

def update_roles_from_drive(intrigue, spreadsheet_id, credentials_path):
    # Charger les identifiants d'accès à l'API depuis le fichier json
    credentials = Credentials.from_authorized_user_info(info=json.load(open(credentials_path)))

    # Construire le api_doc Sheets
    sheets_service = build('sheets', 'v4', credentials=credentials)

    # Lire les valeurs de la feuille de calcul
    result = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='Roles!A:C').execute()
    values = result.get('values', [])

    for i, row in enumerate(values):
        if i == 0:
            # La première ligne contient les titres des colonnes, on l'ignore
            continue
        role_name, perso_name = row[:2]
        perso = GN.nomVersPersonnage(perso_name)
        if perso is None:
            print(f"Le personnage {perso_name} n'a pas été trouvé dans le GN, vérifiez la typo")
            continue
        role = intrigue.get_role_by_name(role_name)
        if role is None:
            print(f"Le role {role_name} n'a pas été trouvé dans l'intrigue {intrigue.nom}, vérifiez la typo")
            continue
        role.personnage = perso
        perso.roles.add(role)



# * ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


# et de la même manière, j'aimerais créer une focntion generate_drive_association qui focntionne comme generate_csv mais avec un document google sheet au lieu d'un csv

# Pour créer la fonction update_roles_from_drive, vous pouvez utiliser la bibliothèque Google Sheets API pour Python. Cette bibliothèque vous permettra de lire les valeurs d'un feuille de calcul Google Sheets en utilisant des requêtes HTTP. Voici un exemple de ce à quoi pourrait ressembler la fonction:

def update_roles_from_drive(gn, spreadsheet_id, sheet_name, verbal=True):
    # Utiliser la bibliothèque Google Sheets API pour ouvrir la feuille de calcul et obtenir les données
    result = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
    values = result.get('values', [])

    # Parcourir les lignes de données pour mettre à jour les rôles
    for row in values:
        role_name = row[0]
        personnage_name = row[1]

        # trouver le personnage correspondant dans le GN
        personnage = gn.nomVersPersonnage(personnage_name)

        if personnage is None:
            # Si le personnage n'a pas été trouvé, ajouter une erreur au journal d'erreurs
            gn.add_to_error_log(f"Le personnage {personnage_name} n'a pas été trouvé dans le GN")
            if verbal:
                print(f"Le personnage {personnage_name} n'a pas été trouvé dans le GN")
            continue

        # trouver le role correspondant dans les intrigues du GN
        role = None
        for intrigue in gn.intrigues.values():
            role = intrigue.getRoleByName(role_name)
            if role is not None:
                break
        if role is None:
            # Si le rôle n'a pas été trouvé, ajouter une erreur au journal d'erreurs
            gn.add_to_error_log(f"Le rôle {role_name} n'a pas été trouvé dans le GN")
            if verbal:
                print(f"Le rôle {role_name} n'a pas été trouvé dans le GN")
            continue

        # Associer le personnage au rôle
        role.perso = personnage
        personnage.roles.add(role)
    if verbal:
        print("Mise à jour des rôles depuis le drive terminée")


# * ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


# peux-tu me redonner le code de generate_drive_association ?

# Pour générer une association à partir d'un document Google Sheet, vous devrez utiliser les bibliothèques Google Sheets API et Google Drive API pour accéder aux données du document. Voici un exemple de code qui montre comment utiliser ces bibliothèques pour lire les données d'un feuille de calcul Google et les utiliser pour générer des associations:

import openai_secret_manager

# on importe les bibliothèques de Google Sheets et Drive
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def generate_drive_association(spreadsheet_id, sheet_name, gn: GN):
    """
    Génère les associations entre les personnages et les rôles à partir d'un document Google Sheet
    :param spreadsheet_id: L'ID du document Google Sheet
    :param sheet_name: Le nom de la feuille de calcul dans le document
    :param gn: L'objet GN sur lequel générer les associations
    """
    try:
        # On récupère les secrets pour l'accès à l'API google
        secrets = openai_secret_manager.get_secret("google")

        # On utilise les secrets pour construire un api_doc Sheets
        sheets_service = build('sheets', 'v4', credentials=secrets)

        # On utilise l'ID du document et le nom de la feuille pour accéder aux données
        result = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
        rows = result.get('values')

        # On parcourt les lignes du tableau pour créer les associations
        for row in rows:
            nom_personnage = row[0]
            nom_role = row[1]

            # On cherche les objets Personnage et Role correspondants
            personnage = gn.nomVersPersonnage(nom_personnage)
            role = gn.nomVersRole(nom_role)

            # On crée l'association entre le personnage et le rôle
            gn.associer_role_a_perso(role, personnage)

    except HttpError as error:
        print(f"An error occurred: {error}")

# Ce code utilise l'ID du document et le nom de la feuille pour accéder aux données du document et parcourt les lignes pour générer des associations en utilisant la fonction self.associer_role_a_perso . N'oubliez pas d'ajouter les bibliothèques google-api-python-client et google-auth-httplib2 pour utiliser ces fonctions


def generer_csv_association(roles_dict, filename):
    # Ouvrir un fichier CSV en mode écriture
    with open(filename, 'w', newline='') as csvfile:
        # Créer un objet CSV writer
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Écrire les en-têtes de colonnes
        writer.writerow(['nom', 'description', 'pipr', 'pipi', 'sexe', 'personnage'])
        # Pour chaque rôle dans le dictionnaire de rôles
        for role in roles_dict.values():
            # Récupérer les valeurs de chaque champ
            nom = role.nom
            description = role.description
            pipr = role.pipr
            pipi = role.pipi
            sexe = role.genre
            personnage = role.personnage if role.personnage else ""
            # Écrire les valeurs dans le fichier CSV
            writer.writerow([nom, description, pipr, pipi, sexe, personnage])
    print("Fichier CSV généré avec succès: {}".format(filename))


def lire_association_roles_depuis_csv(roles_list, filename):
    try:
        # Ouvrir le fichier CSV en mode lecture
        with open(filename, 'r', newline='') as csvfile:
            # Créer un objet CSV reader
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            # Vérifier les en-têtes de colonnes
            headers = next(reader)
            if headers != ['nom', 'description', 'pipr', 'pipi', 'sexe', 'personnage']:
                raise ValueError("Le fichier CSV ne contient pas les bonnes entêtes de colonnes")
            # Pour chaque ligne du fichier CSV
            for row in reader:
                nom = row[0]
                personnage = row[5]

                # et mettre à jour les paramètres du GN en fcontion de ceux du programme > ca se joue à quel niveau?
                # qu'est-ce qui est propriété de quoi? peut-on changer d'association en cours de vie de self?

                # Trouver le rôle correspondant dans la liste de rôles
                role = next((role for role in roles_list if role.nom == nom), None)
                if role:
                    # Mettre à jour le champ personnage de ce rôle
                    role.perso = personnage
            print("Les informations de personnages ont été mises à jour.")
    except FileNotFoundError:
        print(f"Le fichier {filename} n'existe pas.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier: {e}")

##        ***********************************


#
#         # # Create the buttons
#         # # self.create_gn_button = tk.Button(self.master, text="Créer nouveau GN", command=self.create_new_gn)
#         # # self.create_gn_button.grid(row=0, column=0, sticky="nsew")
#         #
#         # self.regen_button = tk.Button(self.master, text="Régénérer", command=self.regen)
#         # self.regen_button.grid(row=1, column=0, sticky="nsew")
#         #
#         # # self.diagnostic_button = tk.Button(self.master, text="Mode diagnostic", command=self.diagnostic_mode)
#         # # self.diagnostic_button.grid(row=2, column=0, sticky="nsew")
#         #
#         # # self.config_button = tk.Button(self.master, text="Changer fichier de configuration",
#         # #                                command=self.change_config_file)
#         # # self.config_button.grid(row=3, column=0, sticky="nsew")
#         # #
#         # # self.edit_config_button = tk.Button(self.master, text="Modifier  fichier de configuration",
#         # #                                     command=self.modify_config)
#         # # self.edit_config_button.grid(row=4, column=0, sticky="nsew")
#         #
#         # # Create the label
#         # # self.current_file_label = tk.Label(self.master, text="Fichier ini actuel : Aucun")
#         # # self.current_file_label.grid(row=5, column=0, columnspan=2, sticky='w')
#         # # self.lire_fichier_config()
#
# # def updateur_de_boutons_disponibles(self, state, boutons):
# #     # self.ok_button.config(state=state)
# #     # self.diagnostic_button.config(state=state)
# #     # self.edit_config_button.config(state=state)
# #     pass
#
#
#
#
#     def create_new_gn(self):
#         new_gn_window = tk.Toplevel(self.master)
#         new_gn_window.title("Créer nouveau GN")
#         new_gn_window.geometry("450x270")
#
#         intrigues_label = tk.Label(new_gn_window, text="Intrigues")
#         intrigues_label.grid(row=0, column=0)
#         intrigues_entry = tk.Entry(new_gn_window)
#         intrigues_entry.grid(row=0, column=1)
#
#         base_persos_gn_label = tk.Label(new_gn_window, text="Base persos GN")
#         base_persos_gn_label.grid(row=1, column=0)
#         base_persos_gn_entry = tk.Entry(new_gn_window)
#         base_persos_gn_entry.grid(row=1, column=1)
#
#         # fichier_faction_label = tk.Label(new_gn_window, text="Fichier faction")
#         # fichier_faction_label.grid(row=2, column=0)
#         # fichier_faction_entry = tk.Entry(new_gn_window)
#         # fichier_faction_entry.grid(row=2, column=1)
#
#         id_factions_label = tk.Label(new_gn_window, text="ID factions")
#         id_factions_label.grid(row=3, column=0)
#         id_factions_entry = tk.Entry(new_gn_window)
#         id_factions_entry.grid(row=3, column=1)
#
#         dossier_output_squelettes_pjs_label = tk.Label(new_gn_window, text="Dossier output")
#         dossier_output_squelettes_pjs_label.grid(row=4, column=0)
#         dossier_output_squelettes_pjs_entry = tk.Entry(new_gn_window)
#         dossier_output_squelettes_pjs_entry.grid(row=4, column=1)
#
#         association_auto_label = tk.Label(new_gn_window, text="Association auto")
#         association_auto_label.grid(row=5, column=0)
#         association_auto_var = tk.IntVar()
#         association_auto_yes = tk.Radiobutton(new_gn_window, text="Oui", variable=association_auto_var, value=1)
#         association_auto_yes.grid(row=5, column=1)
#         association_auto_no = tk.Radiobutton(new_gn_window, text="Non", variable=association_auto_var, value=0)
#         association_auto_no.grid(row=5, column=2)
#
#         type_fiche_label = tk.Label(new_gn_window, text="Type de fiche")
#         type_fiche_label.grid(row=6, column=0)
#         type_fiche_var = tk.StringVar(new_gn_window)
#         type_fiche_var.set("Chalacta")
#         type_fiche_dropdown = tk.OptionMenu(new_gn_window, type_fiche_var, "Chalacta", "Modèle 7 colonnes")
#         type_fiche_dropdown.grid(row=6, column=1)
#
#         nom_fichier_sauvegarde_label = tk.Label(new_gn_window, text="Nom fichier sauvegarde")
#         nom_fichier_sauvegarde_label.grid(row=7, column=0)
#         nom_fichier_sauvegarde_entry = tk.Entry(new_gn_window)
#         nom_fichier_sauvegarde_entry.grid(row=7, column=1)
#
#         noms_persos_label = tk.Label(new_gn_window, text="Noms persos")
#         noms_persos_label.grid(row=8, column=0)
#         noms_persos_entry = tk.Entry(new_gn_window)
#         noms_persos_entry.grid(row=8, column=1)
#
#         nom_fichier_pnjs_label = tk.Label(new_gn_window, text="Nom fichier PNJs")
#
#         nom_fichier_pnjs_label.grid(row=9, column=0)
#         nom_fichier_pnjs_entry = tk.Entry(new_gn_window)
#         nom_fichier_pnjs_entry.grid(row=9, column=1)
#
#         submit_button = tk.Button(new_gn_window, text="Valider",
#                                   command=lambda: self.submit_new_gn(intrigues_entry.get(), base_persos_gn_entry.get(),
#                                                                      id_factions_entry.get(),
#                                                                      dossier_output_squelettes_pjs_entry.get(),
#                                                                      association_auto_var.get(), type_fiche_var.get(),
#                                                                      nom_fichier_sauvegarde_entry.get(),
#                                                                      noms_persos_entry.get(),
#                                                                      nom_fichier_pnjs_entry.get(),
#                                                                      new_gn_window))
#         submit_button.grid(row=10, column=0)
#
#     def submit_new_gn(self, intrigues, base_persos_gn, id_factions, dossier_output_squelettes_pjs,
#                       association_auto, type_fiche, nom_fichier_sauvegarde, noms_persos, nom_fichier_pnjs, window):
#         # Do something with the user's input
#         # print(f"Intrigues: {intrigues}")
#         # print(f"Base persos GN: {base_persos_gn}")
#         # print(f"ID factions: {id_factions}")
#         # print(f"Dossier output squelettes PJs: {dossier_output_squelettes_pjs}")
#         # print(f"Association auto: {association_auto}")
#         # print(f"Type de fiche: {type_fiche}")
#         # print(f"Nom fichier sauvegarde: {nom_fichier_sauvegarde}")
#         # print(f"Noms persos: {noms_persos}")
#         # print(f"Nom fichier PNJs: {nom_fichier_pnjs}")
#
#         # Create a dictionary with the entered values
#         dict_config = {"dossier_intrigues": intrigues.split(','),
#                        "dossiers_pjs": base_persos_gn.split(','),
#                        "id_factions": id_factions,
#                        "dossier_output": dossier_output_squelettes_pjs,
#                        "association_auto": association_auto,
#                        "type_fiche": type_fiche,
#                        "nom_fichier_sauvegarde": nom_fichier_sauvegarde,
#                        "noms_persos": noms_persos.split(","),
#                        "fichier_noms_pnjs": nom_fichier_pnjs}
#
#         nom_fichier = f"{nom_fichier_sauvegarde}.ini"
#         ecrire_fichier_config(dict_config, nom_fichier)
#         self.lire_fichier_config(nom_fichier)
#         # Do something with the config_dict, like saving it to a file
#         # for key in dict_config:
#         #     print(f"{key}:{dict_config[key]} type : {type(dict_config[key])}")
#
#         # Close the configuration window
#         window.destroy()
#
#     def diagnostic_mode(self):
#         diagnostic_window = tk.Toplevel(self.master)
#
#         # recharger_gn_button = tk.Button(diagnostic_window, text="Recharger GN", command=lambda: print("Recharger GN"))
#         # recharger_gn_button.grid(row=0, column=0, sticky="nsew")
#         #
#         # relire_intrigues_button = tk.Button(diagnostic_window, text="Relire toutes les intrigues",
#         #                                     command=lambda: extraireTexteDeGoogleDoc.extraire_intrigues(
#         #                                         self.self, self.api_sheets, self.api_doc, fast=False)
#         #                                     )
#         # relire_intrigues_button.grid(row=1, column=0, sticky="nsew")
#         #
#         # relire_persos_button = tk.Button(diagnostic_window, text="Relire tous les personnages",
#         #                                  command=lambda: extraireTexteDeGoogleDoc.extraire_pjs(
#         #                                      self.self, self.api_sheets, self.api_doc, fast=False)
#         #                                  )
#         # relire_persos_button.grid(row=2, column=0, sticky="nsew")
#         #
#         # relire_perso_spec_button = tk.Button(diagnostic_window, text="Relire un personnage spécifique",
#         #                                      command=lambda: print("Relire un personnage spécique"))
#         # relire_perso_spec_button.grid(row=3, column=0, sticky="nsew")
#         #
#         # relire_intrigue_spec_button = tk.Button(diagnostic_window, text="Relire une intrigue spécifique",
#         #                                         command=lambda: print("Relire une intrigue spécifique"))
#         # relire_intrigue_spec_button.grid(row=4, column=0, sticky="nsew")
#         #
#         # effacer_persos_force_button = tk.Button(diagnostic_window, text="Effacer les personnages forcés",
#         #                                         command=lambda: self.self.effacer_personnages_forces())
#         # effacer_persos_force_button.grid(row=5, column=0, sticky="nsew")
#
#         importer_persos_config_button = tk.Button(diagnostic_window,
#                                                   text="Importer les personnages du fichier de configuration",
#                                                   command=lambda: self.gn.forcer_import_pjs(
#                                                       self.dict_config['liste_noms_pjs'])
#                                                   )
#         importer_persos_config_button.grid(row=6, column=0, sticky="nsew")
#
#         importer_pnjs_button = tk.Button(diagnostic_window, text="Ré-importer les PNJs d'après le fichier",
#                                          command=lambda: self.gn.forcer_import_pnjs(
#                                              lire_fichier_pnjs(self.dict_config['fichier_noms_pnjs']))
#                                          )
#         importer_pnjs_button.grid(row=7, column=0, sticky="nsew")
#
#         sauvegarder_gn_button = tk.Button(diagnostic_window, text="Sauvegarder le GN",
#                                           command=lambda: self.gn.save(self.dict_config['nom_fichier_sauvegarde'])
#                                           )
#         sauvegarder_gn_button.grid(row=8, column=0, sticky="nsew")
#
#         generer_liste_ref_pnj_button = tk.Button(diagnostic_window,
#                                                  text="Générer liste de référence des PNJs dédupliqués",
#                                                  command=lambda: ecrire_liste_pnj_dedup_localement(
#                                                      self.gn, str(datetime.date.today()))
#                                                  )
#         generer_liste_ref_pnj_button.grid(row=9, column=0, sticky="nsew")
#
#         generer_fichier_association_button = tk.Button(diagnostic_window, text="Générer le fichier d'association",
#                                                        command=lambda: print("Générer le fichier d'association"))
#         generer_fichier_association_button.grid(row=10, column=0, sticky="nsew")
#
#         lire_fichier_association_button = tk.Button(diagnostic_window, text="Lire le fichier d'associations",
#                                                     command=lambda: print("Lire le fichier d'associations"))
#         lire_fichier_association_button.grid(row=11, column=0, sticky="nsew")
#
#         # generer_changelog_drive_button = tk.Button(diagnostic_window, text="Générer changelog dans Drive",
#         #                                            command=lambda: generer_tableau_changelog_sur_drive(
#         #                                                self.self, self.api_sheets, self.apiSheets)
#         #                                            )
#         # generer_changelog_drive_button.grid(row=12, column=0, sticky="nsew")
#
#         generer_changelog_local_button = tk.Button(diagnostic_window, text="Générer changelog localement",
#                                                    command=lambda: generer_changelog(
#                                                        self.gn, str(datetime.date.today()))
#                                                    )
#         generer_changelog_local_button.grid(row=13, column=0, sticky="nsew")
#
#         # generer_erreurs_local_button = tk.Button(diagnostic_window, text="Générer fichier des erreurs localement",
#         #                                          command=lambda: lister_erreurs(self.gn, str(datetime.date.today())))
#         # generer_erreurs_local_button.grid(row=14, column=0, sticky="nsew")
#
#         # generer_erreurs_drive_button = tk.Button(diagnostic_window, text="Générer fichier des erreurs sur Drive",
#         #                                          command=lambda:
#         #                                          ecrire_erreurs_dans_drive(
#         #                                              lister_erreurs(self.self, None),
#         #                                              self.api_doc, self.api_sheets,
#         #                                              self.dict_config['dossier_output']))
#         # generer_erreurs_drive_button.grid(row=15, column=0, sticky="nsew")
#         #
#         # generer_table_intrigues_drive_button = tk.Button(diagnostic_window,
#         #                                                  text="Générer table des intrigues sur Drive",
#         #                                                  command=lambda: creer_table_intrigues_sur_drive(
#         #                                                      self.self, self.apiSheets, self.api_sheets)
#         #                                                  )
#         # generer_table_intrigues_drive_button.grid(row=16, column=0, sticky="nsew")
#
#         generer_table_intrigues_local_button = tk.Button(diagnostic_window,
#                                                          text="Générer table des intrigues localement",
#                                                          command=lambda: print(
#                                                              "Générer table des intrigues localement"))
#         generer_table_intrigues_local_button.grid(row=17, column=0, sticky="nsew")
#
#         # generer_fiches_pj_drive_button = tk.Button(diagnostic_window, text="Générer fiches PJ dans Drive",
#         #                                            command=lambda: generer_squelettes_dans_drive(
#         #                                                self.self, self.api_doc, self.api_sheets, True)
#         #                                            )
#         # generer_fiches_pj_drive_button.grid(row=18, column=0, sticky="nsew")
#         #
#         # generer_fiches_pnj_drive_button = tk.Button(diagnostic_window, text="Générer fiches PNJ dans Drive",
#         #                                             command=lambda: lambda: generer_squelettes_dans_drive(
#         #                                                 self.self, self.api_doc, self.api_sheets, False)
#         #                                             )
#         # generer_fiches_pnj_drive_button.grid(row=19, column=0, sticky="nsew")
#
#         generer_fiches_pj_local_button = tk.Button(diagnostic_window, text="Générer fiches PJ localement",
#                                                    command=lambda: ecrire_squelettes_localement(
#                                                        self.gn, str(datetime.date.today()), pj=True)
#                                                    )
#         generer_fiches_pj_local_button.grid(row=20, column=0, sticky="nsew")
#
#         generer_fiches_pnj_local_button = tk.Button(diagnostic_window, text="Générer fiches PNJ localement",
#                                                     command=lambda: ecrire_squelettes_localement(
#                                                         self.gn, str(datetime.date.today()), pj=False)
#                                                     )
#         generer_fiches_pnj_local_button.grid(row=21, column=0, sticky="nsew")
#
#         generer_table_pnj_local_button = tk.Button(diagnostic_window, text="Générer table des PNJs localement",
#                                                    command=lambda: print("Générer table des PNJs localement"))
#         generer_table_pnj_local_button.grid(row=22, column=0, sticky="nsew")
#
#         forcer_update_gn_button = tk.Button(diagnostic_window, text="Vérifier le modèle",
#                                             command=lambda: mettre_a_jour_champs(self.gn))
#         forcer_update_gn_button.grid(row=23, column=0, sticky="nsew")
#
#         # relire_factions_button = tk.Button(diagnostic_window, text="Relire les factions",
#         #                                    command=lambda: print("Relire les factions"))
#         # relire_factions_button.grid(row=23, column=0, sticky="nsew")
#
#         def modify_config(self):
#             config_window = tk.Toplevel(self.master)
#             # for key in self.dict_config:
#             #     print(f"{key}:{self.dict_config[key]} type : {type(self.dict_config[key])}")
#
#             tk.Label(config_window, text="Intrigues").grid(row=0, column=0)
#             intrigues_entry = tk.Entry(config_window)
#             intrigues_entry.insert(0, ",".join(self.dict_config['dossier_intrigues']))
#             intrigues_entry.grid(row=0, column=1)
#
#             tk.Label(config_window, text="Base persos self").grid(row=1, column=0)
#             base_persos_gn_entry = tk.Entry(config_window)
#             base_persos_gn_entry.insert(0, ",".join(self.dict_config['dossiers_pjs']))
#             base_persos_gn_entry.grid(row=1, column=1)
#
#             tk.Label(config_window, text="Id factions").grid(row=3, column=0)
#             id_factions_entry = tk.Entry(config_window)
#             id_factions_entry.insert(0, self.dict_config['id_factions'])
#             id_factions_entry.grid(row=3, column=1)
#
#             tk.Label(config_window, text="Dossier output").grid(row=4, column=0)
#             dossier_output_squelettes_pjs_entry = tk.Entry(config_window)
#             dossier_output_squelettes_pjs_entry.insert(0, self.dict_config['dossier_output'])
#             dossier_output_squelettes_pjs_entry.grid(row=4, column=1)
#
#             tk.Label(config_window, text="Association auto").grid(row=5, column=0)
#             association_auto_var = tk.StringVar(value=self.dict_config['association_auto'])
#             association_auto_yes = tk.Radiobutton(config_window, text="Oui", variable=association_auto_var, value="oui")
#             association_auto_yes.grid(row=5, column=1)
#             association_auto_no = tk.Radiobutton(config_window, text="Non", variable=association_auto_var, value="non")
#             association_auto_no.grid(row=5, column=2)
#
#             tk.Label(config_window, text="Type fiche").grid(row=6, column=0)
#             type_fiche_var = tk.StringVar(value=self.dict_config['type_fiche'])
#             type_fiche_chalacta = tk.Radiobutton(config_window, text="Chalacta / modele 7 colonnes",
#                                                  variable=type_fiche_var, value="Chalacta / modele 7 colonnes")
#             type_fiche_chalacta.grid(row=6, column=1)
#             type_fiche_autre = tk.Radiobutton(config_window, text="Autre", variable=type_fiche_var, value="autre")
#             type_fiche_autre.grid(row=6, column=2)
#
#             tk.Label(config_window, text="Nom fichier sauvegarde").grid(row=7, column=0)
#             nom_fichier_sauvegarde_entry = tk.Entry(config_window)
#             nom_fichier_sauvegarde_entry.insert(0, self.dict_config['nom_fichier_sauvegarde'])
#             nom_fichier_sauvegarde_entry.grid(row=7, column=1)
#
#             tk.Label(config_window, text="Noms persos").grid(row=8, column=0)
#
#             noms_persos_entry = tk.Entry(config_window)
#             noms_persos_entry.insert(0, ",".join(self.dict_config['liste_noms_pjs']))
#             noms_persos_entry.grid(row=8, column=1)
#
#             tk.Label(config_window, text="Nom fichier pnjs").grid(row=9, column=0)
#             nom_fichier_pnjs_entry = tk.Entry(config_window)
#             nom_fichier_pnjs_entry.insert(0, self.dict_config['fichier_noms_pnjs'])
#             nom_fichier_pnjs_entry.grid(row=9, column=1)
#
#             ok_button = tk.Button(config_window, text="Valider", command=lambda: self.validate_config(
#                 intrigues_entry.get(), base_persos_gn_entry.get(), id_factions_entry.get(),
#                 dossier_output_squelettes_pjs_entry.get(),
#                 association_auto_var.get(), type_fiche_var.get(), nom_fichier_sauvegarde_entry.get(),
#                 noms_persos_entry.get(),
#                 nom_fichier_pnjs_entry.get(), config_window)
#                                   )
#
#             ok_button.grid(row=11, column=0)
#             cancel_button = tk.Button(config_window, text="Annuler", command=config_window.destroy)
#             cancel_button.grid(row=11, column=1)
#
#         def validate_config(self, intrigues, base_persos_gn, id_factions, dossier_output_squelettes_pjs,
#                             association_auto, type_fiche, nom_fichier_sauvegarde, noms_persos, nom_fichier_pnjs,
#                             config_window):
#             # Create a dictionary with the entered values
#             dict_config = {"dossier_intrigues": intrigues.split(','),
#                            "dossiers_pjs": base_persos_gn.split(','),
#                            "id_factions": id_factions,
#                            "dossier_output": dossier_output_squelettes_pjs,
#                            "association_auto": association_auto,
#                            "type_fiche": type_fiche,
#                            "nom_fichier_sauvegarde": nom_fichier_sauvegarde,
#                            "noms_persos": noms_persos.split(","),
#                            "fichier_noms_pnjs": nom_fichier_pnjs}
#
#             nom_fichier = f"{nom_fichier_sauvegarde}.ini"
#             ecrire_fichier_config(dict_config, nom_fichier)
#             self.lire_fichier_config(nom_fichier)
#             # Do something with the config_dict, like saving it to a file
#             # for key in dict_config:
#             #     print(f"{key}:{dict_config[key]} type : {type(dict_config[key])}")
#
#             # Close the configuration window
#             config_window.destroy()
#
#         # def regen(self):
#         #     regen_window = tk.Toplevel(self.master)
#         #     regen_window.geometry("675x475")  # chaque nouvelle ligne fait +25 de hauteur
#         #
#         #     lecture_label = tk.Label(regen_window, text="Options de lecture")
#         #     lecture_label.grid(row=50, column=0, columnspan=2)
#         #
#         #     forcer_update_gn_button = tk.Button(regen_window, text="adapter le GN aux \n dernières maj de Magnet",
#         #                                         command=lambda: mettre_a_jour_champs(self.gn))
#         #     forcer_update_gn_button.grid(row=50, column=3, rowspan=2)  # , sticky="nsew"
#         #
#         #     # Intrigues
#         #     var_fast_intrigue = tk.BooleanVar(value=True)
#         #     var_fast_fiches_pjs = tk.BooleanVar(value=True)
#         #     var_fast_fiches_pnjs = tk.BooleanVar(value=True)
#         #     var_fast_evenements = tk.BooleanVar(value=True)
#         #     var_fast_objets = tk.BooleanVar(value=True)
#         #
#         #     # ajouter le bouton et le label ini a la première ligne
#         #     self.config_button = tk.Button(regen_window, text="Changer fichier de configuration",
#         #                                    command=self.change_config_file)
#         #     self.config_button.grid(row=0, column=0)  # , sticky="nsew"
#         #
#         #     # Create the label
#         #     self.current_file_label = tk.Label(regen_window, text="Fichier ini actuel : Aucun")
#         #     self.current_file_label.grid(row=0, column=1, columnspan=3, sticky='w')
#         #     self.lire_fichier_config()
#         #
#         #     # Intrigue Line
#         #     tk.Label(regen_window, text="Intrigue").grid(row=51, column=0)
#         #     tk.Radiobutton(regen_window, text="Rapide", variable=var_fast_intrigue, value=True).grid(row=51, column=1)
#         #     tk.Radiobutton(regen_window, text="Complet", variable=var_fast_intrigue, value=False).grid(row=51, column=2)
#         #
#         #     # Fiches PJs Line
#         #     tk.Label(regen_window, text="Fiches PJs").grid(row=52, column=0)
#         #     tk.Radiobutton(regen_window, text="Rapide", variable=var_fast_fiches_pjs, value=True).grid(row=52, column=1)
#         #     tk.Radiobutton(regen_window, text="Complet", variable=var_fast_fiches_pjs, value=False).grid(row=52, column=2)
#         #
#         #     # Fiches PNJs Line
#         #     ttk.Label(regen_window, text="Fiches PNJs").grid(row=53, column=0)
#         #     tk.Radiobutton(regen_window, text="Rapide", variable=var_fast_fiches_pnjs, value=True).grid(row=53, column=1)
#         #     tk.Radiobutton(regen_window, text="Complet", variable=var_fast_fiches_pnjs, value=False).grid(row=53, column=2)
#         #
#         #     # Evenements Line
#         #     ttk.Label(regen_window, text="Evenements").grid(row=54, column=0)
#         #     tk.Radiobutton(regen_window, text="Rapide", variable=var_fast_evenements, value=True).grid(row=54, column=1)
#         #     tk.Radiobutton(regen_window, text="Complet", variable=var_fast_evenements, value=False).grid(row=54, column=2)
#         #
#         #     # Objets Line
#         #     ttk.Label(regen_window, text="Objets").grid(row=55, column=0)
#         #     tk.Radiobutton(regen_window, text="Rapide", variable=var_fast_objets, value=True).grid(row=55, column=1)
#         #     tk.Radiobutton(regen_window, text="Complet", variable=var_fast_objets, value=False).grid(row=55, column=2)
#         #
#         #     repartir_de_0_var = tk.BooleanVar()
#         #     repartir_de_0_var.set(False)
#         #     charger_fichier_check = tk.Checkbutton(regen_window, text="Repartir de 0",
#         #                                            variable=repartir_de_0_var)
#         #     charger_fichier_check.grid(row=104, column=0)
#         #
#         #     sauver_apres_operation_var = tk.BooleanVar()
#         #     sauver_apres_operation_var.set(True)
#         #     sauver_apres_operation_check = tk.Checkbutton(regen_window, text="Sauver après opération",
#         #                                                   variable=sauver_apres_operation_var)
#         #     sauver_apres_operation_check.grid(row=104, column=1)
#         #
#         #     generer_label = ttk.Label(regen_window, text="Générer...")
#         #     generer_label.grid(row=105, column=0, columnspan=2)
#         #
#         #     master_state = tk.BooleanVar()
#         #     master_state.set(True)
#         #     master_checkbox = tk.Checkbutton(regen_window, text="cocher / décocher tout", variable=master_state,
#         #                                      command=lambda: update_checkboxes(master_state))
#         #     master_checkbox.grid(sticky="W", row=105, column=2)
#         #
#         #     def update_checkboxes(etat_a_forcer):
#         #         args = [generer_fichiers_pj_var,
#         #                 generer_fichiers_pj_var,
#         #                 generer_fichiers_pnjs_var,
#         #                 fichier_erreurs_intrigues_var,
#         #                 fichier_erreurs_evenements_var,
#         #                 changelog_var,
#         #                 table_intrigues_var,
#         #                 table_objets_var,
#         #                 table_chrono_var,
#         #                 table_persos_var,
#         #                 table_pnjs_var,
#         #                 aide_de_jeu_var,
#         #                 table_commentaires_var,
#         #                 table_evenements_var,
#         #                 table_relations_var
#         #                 ]
#         #
#         #         for checkbox in args:
#         #             checkbox.set(etat_a_forcer.get())
#         #
#         #     generer_fichiers_pj_var = tk.BooleanVar()
#         #     generer_fichiers_pj_var.set(True)
#         #     generer_fichiers_drive_check = tk.Checkbutton(regen_window, text="Squelettes PJs",
#         #                                                   variable=generer_fichiers_pj_var)
#         #     generer_fichiers_drive_check.grid(sticky="W", row=106, column=0)
#         #
#         #     generer_fichiers_pnjs_var = tk.BooleanVar()
#         #     generer_fichiers_pnjs_var.set(True)
#         #     generer_fichiers_pnjs_check = tk.Checkbutton(regen_window, text="Squelettes PNJs",
#         #                                                  variable=generer_fichiers_pnjs_var)
#         #     generer_fichiers_pnjs_check.grid(sticky="W", row=106, column=1)
#         #
#         #     fichier_erreurs_intrigues_var = tk.BooleanVar()
#         #     fichier_erreurs_intrigues_var.set(True)
#         #     fichier_erreurs_check = tk.Checkbutton(regen_window, text="Fichier erreurs intrigues",
#         #                                            variable=fichier_erreurs_intrigues_var)
#         #     fichier_erreurs_check.grid(sticky="W", row=106, column=2)
#         #
#         #     changelog_var = tk.BooleanVar()
#         #     changelog_var.set(True)
#         #     changelog_check = tk.Checkbutton(regen_window, text="Changelog",
#         #                                      variable=changelog_var)
#         #     changelog_check.grid(sticky="W", row=106, column=3)
#         #
#         #     table_intrigues_var = tk.BooleanVar()
#         #     table_intrigues_var.set(True)
#         #     table_intrigues_check = tk.Checkbutton(regen_window, text="Table des intrigues",
#         #                                            variable=table_intrigues_var)
#         #     table_intrigues_check.grid(sticky="W", row=107, column=0)
#         #
#         #     table_objets_var = tk.BooleanVar()
#         #     table_objets_var.set(True)
#         #     table_objets_check = tk.Checkbutton(regen_window, text="Table des objets",
#         #                                         variable=table_objets_var)
#         #     table_objets_check.grid(sticky="W", row=107, column=1)
#         #
#         #     table_chrono_var = tk.BooleanVar()
#         #     table_chrono_var.set(True)
#         #     table_chrono_check = tk.Checkbutton(regen_window, text="Chronologie des persos",
#         #                                         variable=table_chrono_var)
#         #     table_chrono_check.grid(sticky="W", row=107, column=2)
#         #
#         #     table_persos_var = tk.BooleanVar()
#         #     table_persos_var.set(True)
#         #     table_persos_check = tk.Checkbutton(regen_window, text="Table des persos",
#         #                                         variable=table_persos_var)
#         #     table_persos_check.grid(sticky="W", row=107, column=3)
#         #
#         #     table_pnjs_var = tk.BooleanVar()
#         #     table_pnjs_var.set(True)
#         #     table_pnjs_check = tk.Checkbutton(regen_window, text="Table des pnjs",
#         #                                       variable=table_pnjs_var)
#         #     table_pnjs_check.grid(sticky="W", row=108, column=0)
#         #
#         #     aide_de_jeu_var = tk.BooleanVar()
#         #     aide_de_jeu_var.set(True)
#         #     aide_de_jeu_check = tk.Checkbutton(regen_window, text="Inputs aides de jeu",
#         #                                        variable=aide_de_jeu_var)
#         #     aide_de_jeu_check.grid(sticky="W", row=108, column=1)
#         #
#         #     table_commentaires_var = tk.BooleanVar()
#         #     table_commentaires_var.set(True)
#         #     table_commentaires_check = tk.Checkbutton(regen_window, text="Extraire les commentaires",
#         #                                               variable=table_commentaires_var)
#         #     table_commentaires_check.grid(sticky="W", row=108, column=2)
#         #
#         #     table_relations_var = tk.BooleanVar()
#         #     table_relations_var.set(True)
#         #     table_relations_check = tk.Checkbutton(regen_window, text="Table des relations",
#         #                                            variable=table_relations_var)
#         #     table_relations_check.grid(sticky="W", row=108, column=3)
#         #
#         #     table_evenements_var = tk.BooleanVar()
#         #     table_evenements_var.set(True)
#         #     table_evenements_check = tk.Checkbutton(regen_window, text="Table des évènements",
#         #                                             variable=table_evenements_var)
#         #     table_evenements_check.grid(sticky="W", row=109, column=0)
#         #
#         #     fichier_erreurs_evenements_var = tk.BooleanVar()
#         #     fichier_erreurs_evenements_var.set(True)
#         #     fichier_erreurs_evenements_check = tk.Checkbutton(regen_window, text="Fichier erreurs évènements",
#         #                                                       variable=fichier_erreurs_evenements_var)
#         #     fichier_erreurs_evenements_check.grid(sticky="W", row=109, column=1)
#         #
#         #     # Buttons
#         #     cancel_button = tk.Button(regen_window, text="Annuler", command=regen_window.destroy)
#         #     cancel_button.grid(row=200, column=0)
#         #
#         #     verbal_var = tk.BooleanVar()
#         #     verbal_var.set(False)
#         #     verbal_check = tk.Checkbutton(regen_window, text='Mode "bavard"',
#         #                                   variable=verbal_var)
#         #     verbal_check.grid(row=200, column=2)
#         #
#         #     # ajout des méthodes nécessaires pour gérer le thread
#         #     progress = Progressbar(regen_window, orient='horizontal', length=580, mode='determinate')
#         #     progress.grid(row=301, column=0, columnspan=4)
#         #
#         #     def faire_evoluer_barre(evolution: float):
#         #         print(f"debug : la valeur de la barre est de {progress['value']}, "
#         #               f"j'ai reçu une demande de l'augmenter de {evolution} ")
#         #         if evolution == -100:
#         #             progress['value'] = 0
#         #         elif progress['value'] < 100:
#         #             progress['value'] += evolution
#         #         else:
#         #             print(f"Erreur : la barre atteindrait {progress['value'] + evolution}")
#         #
#         #     t_lambda_regen = lambda: lire_et_recharger_gn(mon_gn=self.gn,
#         #                                                   api_drive=self.apiDrive,
#         #                                                   api_doc=self.apiDoc,
#         #                                                   api_sheets=self.apiSheets,
#         #                                                   aides_de_jeu=aide_de_jeu_var.get(),
#         #                                                   liste_noms_pjs=self.dict_config.get(
#         #                                                       'liste_noms_pjs'),
#         #                                                   # noms_pnjs=self.dict_config.get('liste_noms_pnjs'),
#         #                                                   nom_fichier_sauvegarde=self.dict_config[
#         #                                                       'nom_fichier_sauvegarde'],
#         #                                                   fichier_erreurs_intrigues=fichier_erreurs_intrigues_var.get(),
#         #                                                   fichier_erreurs_evenements=fichier_erreurs_evenements_var.get(),
#         #                                                   generer_fichiers_pjs=generer_fichiers_pj_var.get(),
#         #                                                   generer_fichiers_pnjs=generer_fichiers_pnjs_var.get(),
#         #                                                   changelog=changelog_var.get(),
#         #                                                   table_intrigues=table_intrigues_var.get(),
#         #                                                   table_objets=table_objets_var.get(),
#         #                                                   table_chrono=table_chrono_var.get(),
#         #                                                   table_persos=table_persos_var.get(),
#         #                                                   table_pnjs=table_pnjs_var.get(),
#         #                                                   table_commentaires=table_commentaires_var.get(),
#         #                                                   fast_intrigues=var_fast_intrigue.get(),
#         #                                                   fast_persos=var_fast_fiches_pjs.get(),
#         #                                                   fast_pnjs=var_fast_fiches_pnjs.get(),
#         #                                                   fast_evenements=var_fast_evenements.get(),
#         #                                                   fast_objets=var_fast_objets.get(),
#         #                                                   sans_chargement_fichier=repartir_de_0_var.get(),
#         #                                                   sauver_apres_operation=sauver_apres_operation_var.get(),
#         #                                                   verbal=verbal_var.get(),
#         #                                                   table_relations=table_relations_var.get(),
#         #                                                   table_evenements=table_evenements_var.get(),
#         #                                                   visualisation=faire_evoluer_barre
#         #                                                   )
#         #
#         #     ok_button = tk.Button(regen_window, text="OK",
#         #                           command=lambda: threading.Thread(target=t_lambda_regen).start()
#         #                           )
#         #
#         #     ok_button.grid(row=200, column=1)
#         #
#         #     lecture_label = ttk.Label(regen_window, text="\n Progression de la régénération... \n")
#         #     lecture_label.grid(row=300, column=1, columnspan=2)
#
#         # def regen_intrigue_select(self, value):
#         #     if value in ["Rapide", "Complet"]:
#         #         self.intrigue_specifique_entry.config(state='disabled')
#         #     elif value == "Spécifique":
#         #         self.intrigue_specifique_entry.config(state='normal')
#         #
#         # def regen_personnages_select(self, value):
#         #     if value in ["Rapide", "Complet"]:
#         #         self.personnages_specifique_entry.config(state='disabled')
#         #     elif value == "Spécifique":
#         #         self.personnages_specifique_entry.config(state='normal')
#
#         # def process_regen(self, intrigues_value, personnages_value, sans_chargement_fichier_value,
#         #                   sauver_apres_operation_value, fichier_erreur_intrigues_var, fichier_erreur_evenements_var,
#         #                   generer_fichiers_pjs_var, changelog_var,
#         #                   table_chrono_var, table_persos_var, table_pnj_var,
#         #                   table_commentaires_var,
#         #                   table_intrigues_var, table_objets_var,
#         #                   generer_fichiers_pnjs_var, verbal_var, aide_de_jeu_var, table_evenements_var,
#         #                   table_relations_var
#         #                   ):
#         #
#         #     # if intrigues_value == "Spécifique":
#         #     #     intrigue_specifique = self.intrigue_specifique_entry.get()
#         #     # else:
#         #     #     intrigue_specifique = ""
#         #     # if personnages_value == "Spécifique":
#         #     #     personnages_specifique = self.personnages_specifique_entry.get()
#         #     # else:
#         #     #     personnages_specifique = ""
#         #     # # Call the existing method that process the result with the input values:
#         #     # # print(f"{intrigues_value}, {intrigue_specifique}, {personnages_value}, {personnages_specifique}, "
#         #     # #       f"{charger_fichier_value}, {sauver_apres_operation_value}, {generer_fichiers_drive_value}")
#         #     #
#         #     # if intrigues_value != "Spécifique":
#         #     #     intrigue_specifique = "-01"
#         #     # if personnages_value != "Spécifique":
#         #     #     personnages_specifique = "-01"
#         #
#         #     lire_et_recharger_gn(mon_gn=self.gn,
#         #                          api_drive=self.apiDrive,
#         #                          api_doc=self.apiDoc,
#         #                          api_sheets=self.apiSheets,
#         #                          aides_de_jeu=aide_de_jeu_var,
#         #                          liste_noms_pjs=self.dict_config.get('liste_noms_pjs'),
#         #                          # noms_pnjs=self.dict_config.get('liste_noms_pnjs'),
#         #                          nom_fichier_sauvegarde=self.dict_config['nom_fichier_sauvegarde'],
#         #                          fichier_erreurs_intrigues=fichier_erreur_intrigues_var,
#         #                          fichier_erreurs_evenements=fichier_erreur_evenements_var,
#         #                          generer_fichiers_pjs=generer_fichiers_pjs_var,
#         #                          generer_fichiers_pnjs=generer_fichiers_pnjs_var,
#         #                          changelog=changelog_var,
#         #                          table_intrigues=table_intrigues_var,
#         #                          table_objets=table_objets_var,
#         #                          table_chrono=table_chrono_var,
#         #                          table_persos=table_persos_var,
#         #                          table_pnjs=table_pnj_var,
#         #                          table_commentaires=table_commentaires_var,
#         #                          fast_intrigues=(intrigues_value == "Rapide"),
#         #                          fast_persos=(personnages_value == "Rapide"),
#         #                          singletest_perso=personnages_specifique,
#         #                          singletest_intrigue=intrigue_specifique,
#         #                          sans_chargement_fichier=sans_chargement_fichier_value,
#         #                          sauver_apres_operation=sauver_apres_operation_value,
#         #                          verbal=verbal_var,
#         #                          table_relations=table_relations_var,
#         #                          table_evenements=table_evenements_var)