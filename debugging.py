from googleapiclient.errors import HttpError

from MAGnet import *


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
