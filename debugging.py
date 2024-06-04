from googleapiclient.errors import HttpError

from MAGnet import *


def kalitt_debug():
    nom_perso = 'Brance'
    nom_gn = 'archive chalacta.mgn'
    debug_perso_gn(nom_gn, nom_perso)


def debug_perso_gn(nom_gn, nom_perso):
    gn: GN = GN.load(nom_gn)
    noms = [perso.nom for perso in gn.personnages.values()]
    # print(noms)
    kalitt = next(perso for perso in gn.personnages.values() if nom_perso in perso.nom)
    texte_kalitt = generer_squelette_perso(gn, kalitt)
    # print(texte_kalitt)
    api_drive, api_doc, sheet = lecteurGoogle.creer_lecteurs_google_apis()
    nom_fichier = 'test export requete'
    texte = generer_squelette_perso(gn, kalitt)
    parent = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn'
    mon_id = g_io.creer_google_doc(api_drive, nom_fichier, parent)
    g_io.write_to_doc(
        api_doc, mon_id, texte, verbal=True
    )


# kalitt_debug()

# debug_perso_gn('Demo.mgn', 'Corwin')

def remove_permission_for_email_recursive(api_drive, folder_id, email_address):
    """
    Recursively remove permissions for a specific email address from all files and files within subfolders
    in a given folder.

    Parameters:
        api_drive: Initialized Google Drive API service instance.
        folder_id: The ID of the folder whose files' permissions are to be modified.
        email_address: The email address whose permissions are to be removed.
    """
    try:
        page_token = None
        while True:
            # Query to search for all files and folders in the specified folder, handling pagination with page_token
            query = f"'{folder_id}' in parents"
            response = api_drive.files().list(q=query,
                                              pageSize=1000,  # Consider using a smaller pageSize for large directories
                                              fields="nextPageToken, files(id, name, mimeType)",
                                              pageToken=page_token).execute()
            items = response.get('files', [])

            if not items:
                print("No more files or folders found.")
                break

            for item in items:
                # Check if the item is a folder; if so, recurse
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    print(f"Entering folder: {item['name']} ({item['id']})")
                    remove_permission_for_email_recursive(api_drive, item['id'], email_address)
                else:
                    # Process files to remove permissions
                    permissions = api_drive.permissions().list(fileId=item['id'],
                                                               fields="permissions(id, emailAddress)").execute()
                    for permission in permissions.get('permissions', []):
                        if permission.get('emailAddress') == email_address:
                            api_drive.permissions().delete(fileId=item['id'], permissionId=permission['id']).execute()
                            print(f"Removed permission for {email_address} from file: {item['name']}")

            page_token = response.get('nextPageToken')
            if not page_token:
                break
    except HttpError as error:
        print(f'An error occurred: {error}')


#     """
#     Recursively remove permissions for a specific email address from all files and files within subfolders
#     in a given folder.
#
#     Parameters:
#         api_drive: Initialized Google Drive API service instance.
#         folder_id: The ID of the folder whose files' permissions are to be modified.
#         email_address: The email address whose permissions are to be removed.
#     """
#     try:
#         # Query to search for all files and folders in the specified folder
#         query = f"'{folder_id}' in parents"
#         response = api_drive.files().list(q=query, pageSize=700, fields="files(id, name, mimeType)").execute()
#         items = response.get('files', [])
#
#
#         if not items:
#             print("No files or folders found.")
#             return
#
#         for item in items:
#             # Check if the item is a folder; if so, recurse
#             if item['mimeType'] == 'application/vnd.google-apps.folder':
#                 print(f"Entering folder: {item['name']} ({item['id']})")
#                 remove_permission_for_email_recursive(api_drive, item['id'], email_address)
#             else:
#                 # Process files to remove permissions
#                 permissions = api_drive.permissions().list(fileId=item['id'],
#                                                            fields="permissions(id, emailAddress)").execute()
#                 for permission in permissions.get('permissions', []):
#                     if permission.get('emailAddress') == email_address:
#                         api_drive.permissions().delete(fileId=item['id'], permissionId=permission['id']).execute()
#                         print(f"Removed permission for {email_address} from file: {item['name']}")
#     except HttpError as error:
#         print(f'An error occurred: {error}')


def compter_contenu_dossier_drive(folder_id: str, api_drive):
    files = extraire_tous_items_dossier(api_drive, folder_id)

    print(f"Total number of files in the folder: {len(files)}")
    # Now `files` contains all files within the specified folder


def extraire_tous_items_dossier(api_drive, folder_id):
    query = f"'{folder_id}' in parents"
    files = []
    page_token = None
    while True:
        response = api_drive.files().list(q=query,
                                          pageSize=1000,  # Adjust based on your needs
                                          fields="nextPageToken, files(id, name)",
                                          pageToken=page_token).execute()
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return files


#
######### RETIRER LES DROITS
# Initialize your Google Drive API service
# api_drive, _, _ = creer_lecteurs_google_apis()
# root_folder_id = '1_oKXTTD7BtKSI_EWqTjUJ-2jrT_W_e8j'  # le fichier archive
# # root_folder_id = '1CjJPn5Srbka1gqMNt7oAG7pmX-qvgGKN'  # fichier simple de test
# email_address = 'emeric.montagnese@gmail.com'
# remove_permission_for_email_recursive(api_drive, root_folder_id, email_address)


# ### COMPTER LES FICHIERS
# api_drive, _, _ = creer_lecteurs_google_apis()
# root_folder_id = '1_oKXTTD7BtKSI_EWqTjUJ-2jrT_W_e8j'  # le fichier archive
# compter_contenu_dossier_drive(root_folder_id, api_drive)


######################### travail sur l'insertion d'images automatiques ###############################################

def verifier_acces_image(image_id, api_drive):
    try:
        # Récupérer les métadonnées de l'image
        file_metadata = api_drive.files().get(fileId=image_id, fields='id, name, owners, permissions').execute()

        # Afficher les informations de base de l'image
        print(f"Nom de l'image: {file_metadata.get('name')}")
        print("Propriétaires :")
        for owner in file_metadata.get('owners', []):
            print(f"- {owner.get('emailAddress')}")

        # Vérifier si des permissions sont listées (indique que vous avez accès à voir les permissions)
        if 'permissions' in file_metadata:
            print("Permissions :")
            for perm in file_metadata['permissions']:
                print(
                    f"- Type : {perm.get('type')}, Rôle : {perm.get('role')}, Email : {perm.get('emailAddress', 'N/A')}")
        else:
            print("Permissions : Non listées (vous n'avez peut-être pas le droit de voir les permissions)")

        return True  # Accès vérifié
    except Exception as e:
        print(f"Erreur lors de la vérification de l'accès : {e}")
        return False  # Accès non vérifié


# # Remplacez 'Votre_Image_ID' par l'ID de votre image
# api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()
# verifier_acces_image('1dd4-_fgHjIiUMjXtRFZsaZPwZmuonc6T', api_drive)
#
#
# # ID de votre document Google Docs
# document_id = '1iF6aE93CO-e77jRh9CHEEyh7ZYazNSb5kwOKQrmyeg4'
#
# # URL de l'image à insérer
# image_id ='1dd4-_fgHjIiUMjXtRFZsaZPwZmuonc6T'
# image_url = f'https://drive.google.com/uc?export=view&id={image_id}'

# drive_service.files().get(fileId=imageId, fields="webContentLink")

# Requête pour insérer l'image
# requests = [
#     {
#         'insertInlineImage': {
#             'location': {'index': 1},
#             'uri': image_url,
#             'objectSize': {
#                 'height': {'magnitude': 50, 'unit': 'PT'},
#                 'width': {'magnitude': 50, 'unit': 'PT'}
#             }
#         }
#     }
# ]


# # Exécuter la requête
# try:
#     result = api_doc.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
#     print("L'image a été insérée avec succès.")
# except Exception as e:
#     print(f"Erreur lors de l'insertion de l'image : {e}")


def lister_images_avec_extension_dans_dossier(folder_id, drive_service, extension='png'):
    images_dict = {}

    # Définir la requête pour rechercher des fichiers d'images dans le dossier spécifié
    query = f"'{folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png') and trashed = false"
    page_token = None  # Initialiser le token de pagination à None

    while True:  # Commencer une boucle pour gérer la pagination
        response = drive_service.files().list(q=query,
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              orderBy='createdTime',
                                              pageToken=page_token).execute()  # Ajouter pageToken à la requête

        # Extraire le nom de fichier sans extension et l'ID, et les ajouter au dictionnaire
        for file in response.get('files', []):
            # Supprimer l'extension du fichier pour obtenir le nom de l'image
            name = file.get('name')
            extension = name.split('.')[-1].strip()
            if extension == extension:
                print(name)

        page_token = response.get('nextPageToken')  # Récupérer le nextPageToken de la réponse

        if not page_token:  # Si il n'y a pas de nextPageToken, c'est la fin des résultats
            break  # Sortir de la boucle


def tableau_intrigues_persos():
    gn = GN.load('archive chalacta.mgn')

    dico = {perso: [] for perso in gn.personnages.values()}
    for intrigue in gn.intrigues.values():
        for role in intrigue.rolesContenus.values():
            if perso := role.personnage:
                dico[perso].append(intrigue)

    intrigues = list(gn.intrigues.values())

    # output = [[''] + [intrigue.nom for intrigue in intrigues]]
    # for perso in dico:
    #     if 'pierre' not in perso.orga_referent.lower():
    #         continue
    #     to_add = [perso.nom]
    #     for intrigue in dico[perso]:
    #         for i in intrigues:
    #             to_add.append(1 if i == intrigue else 0)
    #     output.append(to_add)

    output = []
    mes_persos = [perso for perso in gn.personnages.values() if 'pierre' in perso.orga_referent.lower()]
    output.append([''] + [perso.nom for perso in mes_persos])

    for intrigue in intrigues:
        to_add = [intrigue.nom]
        for perso in mes_persos:
            to_add.append(1 if intrigue in dico[perso] else 0)
        output.append(to_add)
    _, _, api_sheets = lecteurGoogle.creer_lecteurs_google_apis()
    mon_id = '1HeJI-ECICzVvMzzefku721Vk6Hggc8cF9WClnCGDTUM'
    g_io.write_to_sheet(api_sheets, output, mon_id, "persos Civils")


from googleapiclient.errors import HttpError


def list_docs_and_create_sheet(drive_service, sheets_service, folder_id, output_folder_id):
    try:
        # Query to search for Google Docs in the specified folder
        # query = f"'{folder_id}' in parents"
        # # query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document'"
        # print(f"query = {query}")
        # results = drive_service.files().list(q=query, fields="files(id, name, modifiedTime)").execute()
        # files = results.get('files', [])
        results = drive_service.files().list(
            pageSize=100,
            q=f"'{folder_id}' in parents", fields="nextPageToken, files(id, name, modifiedTime)").execute()
        files = results.get('files', [])

        print(f"file = {files}")

        # Create a new Google Sheet in the specified output folder
        spreadsheet_body = {
            'properties': {
                'title': 'Google Docs List'
            },
            'sheets': [{
                'properties': {
                    'title': 'Docs'
                }
            }]
        }
        sheet = sheets_service.spreadsheets().create(body=spreadsheet_body, fields='spreadsheetId').execute()
        spreadsheet_id = sheet.get('spreadsheetId')

        # Prepare the data for the Google Sheet
        values = [["File ID", "Name", "Last Change"]]
        values.extend([[file['id'], file['name'], file['modifiedTime']] for file in files])

        # Write data to the Google Sheet
        data_body = {
            'values': values
        }
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Docs!A1',
            valueInputOption='USER_ENTERED',
            body=data_body
        ).execute()

        print("ping pre")
        # # Move the created sheet to the desired folder
        # drive_service.files().update(
        #     fileId=spreadsheet_id,
        #     addParents=output_folder_id,
        #     removeParents=sheet['spreadsheetId'],
        #     fields='id, parents'
        # ).execute()
        file_id = g_io.creer_google_sheet(drive_service, "liste Charles", output_folder_id)
        g_io.write_to_sheet(sheets_service, values, file_id, feuille="tout")

        print("ping post")

        print(f"Spreadsheet created with ID: {spreadsheet_id}")
        return spreadsheet_id

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


def lister_fichiers_objets_charles():
    dr, _, sh = lecteurGoogle.creer_lecteurs_google_apis()
    folder_id = '1KC6lFBPAz2BF-iFKbXXcRtXBa-RYdn65'
    output = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn'
    list_docs_and_create_sheet(dr, sh, folder_id, output)


def creer_synthese_actions_en_jeu_par_pnjs():
    gn = GN.load('archive chalacta.mgn')
    dico = {}
    toutes_interventions = []
    # for evenement in gn.evenements.values():
    for evenement in gn.lister_tous_les_conteneurs_evenements_unitaires():
        toutes_interventions.extend(evenement.interventions)

    for intervention in toutes_interventions:
        intervenants = intervention.liste_intervenants
        for intervenant in intervenants:
            clef = intervenant.str_avec_perso()
            if clef not in dico:
                dico[clef] = []
            dico[clef].append(intervention)

    to_R = ""

    for intervenant in dico:
        to_R += f"{intervenant} \n : "
        tableau = [["Jour", "Heure", "Description", "Provenance"]]
        dico[intervenant] = sorted(dico[intervenant], key=lambda x: [x.jour_formatte(), x.heure_debut_formattee()])

        for element in dico[intervenant]:
            tableau.append([element.jour_formatte(), element.heure_debut_formattee(), element.description,
                            element.evenement.nom_evenement])
        to_R += lecteurGoogle.formatter_tableau_pour_export(tableau)
        to_R += '\n\n\n'

    dr, do, sh = lecteurGoogle.creer_lecteurs_google_apis()
    id = '1Nly0HQGziW6wAMFh13v9f0jG_jIjE3lEAZVrpwFtKNg'
    g_io.write_to_doc(
        do, id, to_R, verbal=True
    )


######################################################################
#### reboot création table PNJ >>> ce code marche



# def recurrer_table_evenementiel(colonnes_ok, table_test, current_solutions, verbal=1):
#     for i in range(len(table_test)):
#         colonnes_figes = colonnes_ok + table_test[:i]
#         colonne_a_fusionner = table_test[i]
#         colonnes_a_tester = table_test[i + 1:]
#         if verbal:
#             print(f"{'  ' * verbal} colonnes figées : {colonnes_figes}")
#             print(f"{'  ' * verbal} colonne a fusionner {colonne_a_fusionner}")
#             print(f"{'  ' * verbal} colonne a tester {colonnes_a_tester}")
#
#         for j in range(len(colonnes_a_tester)):
#             current_colonne = colonnes_a_tester[j]
#             colonne_fusionnee = fusionner_colonnes(colonne_a_fusionner, current_colonne, verbal)
#             if colonne_fusionnee:
#                 # new_fixed = colonnes_figes + [colonne_fusionnee] + colonnes_a_tester[j + 1:]
#                 # recurrer_table_evenementiel(new_fixed, colonnes_a_tester[j+1:], current_solutions)
#                 nouvelle_table = colonnes_a_tester[:j] + [colonne_fusionnee] + colonnes_a_tester[j + 1:]
#                 recurrer_table_evenementiel(colonnes_figes, nouvelle_table,
#                                             current_solutions, verbal + 1 if verbal else 0)
#         if verbal:
#             print(f"{'  ' * verbal} Solution ajoutée : {colonnes_figes + [colonne_a_fusionner] + colonnes_a_tester}")
#         current_solutions.append(colonnes_figes + [colonne_a_fusionner] + colonnes_a_tester)


# def recurrer_table_evenementiel_optim(colonnes_ok, table_test, current_solutions, verbal=1):
#     # on trie les colonnes dans l'ordre de la plus grande à la plus petite en taille
#     # on arrete quand on a une solurtion moins optim
#     # on entre dans la récursion là ou on s'tait arrété
#
#     for i in range(len(table_test)):
#         colonnes_figes = colonnes_ok + table_test[:i]
#         colonne_a_fusionner = table_test[i]
#         colonnes_a_tester = table_test[i + 1:]
#         if verbal:
#             print(f"{'  ' * verbal} colonnes figées : {colonnes_figes}")
#             print(f"{'  ' * verbal} colonne a fusionner {colonne_a_fusionner}")
#             print(f"{'  ' * verbal} colonne a tester {colonnes_a_tester}")
#
#         for j in range(len(colonnes_a_tester)):
#             current_colonne = colonnes_a_tester[j]
#             colonne_fusionnee = fusionner_colonnes(colonne_a_fusionner, current_colonne, verbal)
#             if colonne_fusionnee:
#                 # new_fixed = colonnes_figes + [colonne_fusionnee] + colonnes_a_tester[j + 1:]
#                 # recurrer_table_evenementiel(new_fixed, colonnes_a_tester[j+1:], current_solutions)
#                 nouvelle_table = colonnes_a_tester[:j] + [colonne_fusionnee] + colonnes_a_tester[j + 1:]
#                 recurrer_table_evenementiel(colonnes_figes, nouvelle_table,
#                                             current_solutions, verbal + 1 if verbal else 0)
#         if verbal:
#             print(f"{'  ' * verbal} Solution ajoutée : {colonnes_figes + [colonne_a_fusionner] + colonnes_a_tester}")
#         current_solutions.append(colonnes_figes + [colonne_a_fusionner] + colonnes_a_tester)


# invariant :
# - j'ai une solution en cours d'ellaboration
# - j'ai une colonne à teste
# - j'ai une colonne contre lquelle la tester
# SI mes dex colonnes sont fusionnables,
#   je récurrentre entre un monde et j'ai fusionnée et un monde ou je n'iapas fusionné
#       et je passe à la colonne suivante
# SINON
#       je passe à la suivante

# def recurrer_table_evenementiel_v2(colonnes_source):
#     # hypotèse : il existe une combianison ABC  SSI AB, AC et BC sont des solutions possibles
#     # hypothèse 2 : il existe une combinaison ABCD SSI ABC est possible et AD, BC, et CD sont possibles
#     # et ainsi de suite
#     # ainsi, je jeps réduire la recherche de solutions en prenant les paires et en cherchant toutes les combianaisons possibles
#     # ensuite, je prends toutes les paires de plus haut niveau et je redescende en décomposant mon problème
#
#     # invariant : j'ai une table de niveau N
#     # SI il existe une table de niveau N+1 avec au moins un élément ALORS jer cherche une table de niveau N+2
#     # SINON  j'ai fini de trouver mes  solutions
#
#     # initialisation : création table niveau 2
#     niveau = 2
#     tables = {niveau: []}
#     table_n2 = tables[2]
#     dictionnaire_combinaisons = {}
#     nb_col_source = len(colonnes_source)
#     range_source = range(nb_col_source)
#
#     for i in range_source:
#         for j in range(i + 1, len(colonnes_source)):
#             if resultat := fusionner_colonnes(colonnes_source[i], colonnes_source[j], 0):
#                 dictionnaire_combinaisons[(i, j)] = resultat
#                 table_n2.append({i, j})
#
#     print(f"niveau = {niveau}, len = {len(tables[niveau])}")
#     while len(tables[niveau]) > 0:
#         print(f"niveau = {niveau}, len = {len(tables[niveau])}")
#         # sinon, on calcule la table de niveau N+1
#         tables_n_precedent = tables[niveau]
#         niveau += 1
#         tables[niveau] = []
#         # pour chaque élément qui a une solution A0...aN-1 au niveau N-1
#         for solution_n_precedent in tables_n_precedent:
#             max_n_precedent = max(solution_n_precedent)
#             elements_a_tester = [x for x in range(max_n_precedent + 1, nb_col_source) if x not in solution_n_precedent]
#             # pour chaque élément B du set de base qui est différent des composantes de la solution (éléments à tester)
#             for element_a_tester in elements_a_tester:
#                 ajout_ok = True
#                 for element_solution_prececent in solution_n_precedent:
#
#                     # je cherche si (A0, B) ... (An, B) sont toutes des solutions valables
#                     set_a_tester = {element_a_tester, element_solution_prececent}
#                     if set_a_tester not in tables[2]:
#                         ajout_ok = False
#                         break
#
#                 #           SIOUI : ALORS il existe une solution (A0, ..., AN, B)
#                 if ajout_ok:
#                     tables[niveau].append(solution_n_precedent | {element_a_tester})
#             #               j'enregistre que la solution existe dans la table[niveau] sous forme de set
#             #               j'enregistre qu'à la clef de cette solution correspond la solution
#             #               >> pas la peine, certaines solutions ne seront jamais calculées !!!
#     del tables[niveau]
#
#     return tables
#
#
# def fournir_solutions(donnee_test):
#     solution = []
#     colonnes_ok = []
#     recurrer_table_evenementiel(colonnes_ok, donnee_test, solution)
#     return solution


# donnee_test = [
#     ['event1', 'event2', None, 'event4', ''],
#     [None, 'collision', 'event3', None, 'event5'],
#     [None, None, 'fill 1a', None, 'fill 1b'],
#     ['', '', 'fill2', '', ''],
#     ['', '', '', '', 'fill3']
# ]
#
#
# def tester_recursion():
#     donnee_test = [
#         ['event1', 'event2', None, 'event4', ''],
#         [None, 'collision', 'event3', None, 'event5'],
#         [None, None, 'fill 1a', None, 'fill 1b'],
#         ['', '', 'fill2', '', ''],
#         ['', '', '', '', 'fill3']
#     ]
#
#     # donnee_test = [
#     #     ['event1', 'event2', None, 'event4', ''],
#     #     ['poy', 'poy',None, None, 'fill 1b'],
#     #     ['', '', 'fill2', '', ''],
#     # ]
#     return fournir_solutions(donnee_test)


# ******** fonction pour commencer à intégrer les évènements en ignorant les doublons ***********************

