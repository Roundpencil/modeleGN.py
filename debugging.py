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


##################### debugging factions

def voiture_balais_factions():
    factions = ['Course',
                'Daymio',
                'Cercle oblique',
                'Réseau freedom',
                'CDP',
                'Médecins',
                'Milice',
                'Empire',
                'tous les personnages joueurs']
    gn = GN.load('archive chalacta.mgn')

    scenes = gn.lister_toutes_les_scenes()
    a_corriger = set()

    for nom_faction in factions:
        for scene in scenes:
            score = process.extractOne(nom_faction, scene.nom_factions)
            if score and score[1] > 80:
                print(f"{score[0]}, {score[1]}")
                # alors on a un match
                a_corriger.add(scene)

    tri = Scene.trier_scenes(a_corriger)
    texte = '\n\n'.join([scene.str_pour_squelette() for scene in tri])
    dr, do, sh = lecteurGoogle.creer_lecteurs_google_apis()
    g_io.write_to_doc(do, '1xboOGtTJtnmOt6ITcEZ7NCcLTN6qhzGN9VaM5R4WobE', texte, 'titre')


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
    g_io.ecrire_table_google_sheets(api_sheets, output, mon_id, "persos Civils")



