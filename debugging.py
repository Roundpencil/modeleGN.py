from googleapiclient.errors import HttpError

import lecteurGoogle
from MAGnet import *
from lecteurGoogle import creer_lecteurs_google_apis

import re


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

# from googleapiclient.discovery import build
# from google.oauth2 import service_account

# # Chemin vers votre fichier de clés d'authentification service account JSON
# SERVICE_ACCOUNT_FILE = 'path/to/service.json'
#
# # ID du Google Drive contenant l'image et du Google Doc à modifier
# GOOGLE_DRIVE_IMAGE_ID = 'votre_id_image'
# GOOGLE_DOC_ID = 'votre_id_document_google_doc'
#
# SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']


def inserer_image_dans_google_doc(image_id, doc_id, position, drive_service, docs_service):
    # Obtenir l'URL de l'image depuis Google Drive
    image_file = drive_service.files().get(fileId=image_id, fields='webViewLink').execute()
    image_url = image_file.get('webViewLink')

    # Créer une requête pour insérer l'image dans le Google Doc
    request = [
        {
            'insertInlineImage': {
                'location': {
                    'index': position,
                },
                'uri': image_url,
                'objectSize': {
                    'height': {
                        'magnitude': 50,
                        'unit': 'PT'
                    },
                    'width': {
                        'magnitude': 50,
                        'unit': 'PT'
                    }
                }
            }
        }
    ]

    # # Exécuter la requête
    # result = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    # print(f'Image insérée avec succès : {result}')
    return request


def lister_images_dans_dossier(folder_id, drive_service):
    images_dict = {}

    # Définir la requête pour rechercher des fichiers d'images dans le dossier spécifié
    query = f"'{folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png') and trashed = false"
    response = drive_service.files().list(q=query,
                                          spaces='drive',
                                          fields='files(id, name)',
                                          orderBy='createdTime').execute()

    # Extraire le nom de fichier sans extension et l'ID, et les ajouter au dictionnaire
    for file in response.get('files', []):
        # Supprimer l'extension du fichier pour obtenir le nom de l'image
        file_name_without_extension = '.'.join(file.get('name').split('.')[:-1]).strip()
        images_dict[file_name_without_extension] = file.get('id')

    return images_dict



def trouver_clefs_plus_longues_et_positions(dictionnaire, texte):
    # Dictionnaire pour stocker les positions et les clés correspondantes
    positions_et_clefs = {}

    # Parcourir chaque clé du dictionnaire
    for cle in dictionnaire:
        # Chercher la première apparition de la clé dans le texte
        position = texte.find(cle)
        # Si la clé est trouvée dans le texte (position != -1)
        if position != -1:
            # Si une clé correspond déjà à cette position, comparer leurs longueurs
            if position in positions_et_clefs:
                cle_existante = positions_et_clefs[position]
                # Conserver la clé la plus longue
                if len(cle) > len(cle_existante):
                    positions_et_clefs[position] = cle
            else:
                # Ajouter la clé et sa position si aucune clé n'est encore associée à cette position
                positions_et_clefs[position] = cle

    # Transformer le dictionnaire en liste de listes comme spécifié
    resultats = [[cle, pos] for pos, cle in positions_et_clefs.items()]
    return resultats


############# seconde tentative

def trouver_mots(liste_mots, texte):
    # Prétraiter le texte pour le découper en mots tout en gardant les indices de chaque mot
    mots_texte = re.finditer(r'\b\w+\b', texte)
    mots_indices = {mot.group().lower(): [] for mot in
                    mots_texte}  # Initialiser un dictionnaire pour garder les indices

    # Réinitialiser l'itérateur pour parcourir à nouveau
    mots_texte = re.finditer(r'\b\w+\b', texte)
    for mot in mots_texte:
        mot_inf = mot.group().lower()  # Convertir en minuscules pour la comparaison
        if mot_inf in mots_indices:
            mots_indices[mot_inf].append(mot.start())  # Enregistrer l'indice de début de chaque mot

    # Créer la liste de listes à retourner
    resultats = []
    for mot in liste_mots:
        mot_inf = mot.lower()  # Comparaison insensible à la casse
        if mot_inf in mots_indices:
            for indice in mots_indices[mot_inf]:
                resultats.append([indice, mot])

    return resultats


#
# # Exemple d'utilisation
# liste_mots = ['Python', 'est', 'un', 'langage']
# texte = "Python est un langage de programmation. Python est utilisé dans divers domaines."
#
# liste_mots = ['Dal Joval Drasnov', 'le parrain', 'Dal', 'JOvall']
# texte = "Dal JOvall Drasnov est un parrain de la mafia. Dal a deux enfants : Jerima et Saryth"
#
# print(trouver_mots(liste_mots, texte))
#

def base_nom_prenom(nom_secable):
    base_nettoyee = nom_secable.strip()
    if not base_nettoyee:
        return []

    to_return = [base_nettoyee]
    nom_prenom = base_nettoyee.split()
    if len(nom_prenom) > 1:
        to_return.append(nom_prenom[0].strip())
        to_return.append(''.join(nom_prenom[1:]).strip())
    return to_return


def lire_table_photos(api_sheets, sheet_id, sheet_name='Feuille 1', separateur=';'):
    result = api_sheets.spreadsheets().values().get(spreadsheetId=sheet_id, range=sheet_name,
                                                    majorDimension="ROWS").execute()
    values = result.get('values', [])
    print(values)
    to_return = {}
    for value in values[1:]:
        value = value + [''] * (5-len(value))
        photo, nom_secable, nom_insecable, alias_secable, alias_insecable = value
        photo = photo.strip()
        to_return[photo] = []
        if nom_secable:
            a_ajouter = base_nom_prenom(nom_secable)
            to_return[photo].extend(a_ajouter)

        if nom_insecable := nom_insecable.strip():
            to_return[photo].append(nom_insecable)

        if alias_secable := alias_secable.strip() :
            tous_mes_alias = alias_secable.split(separateur)
            for alias in tous_mes_alias:
                a_ajouter = base_nom_prenom(alias_secable)
                to_return[photo].extend(a_ajouter)

        if alias_insecable := alias_insecable.strip():
            a_ajouter = alias_insecable.split(separateur)
            for alias in a_ajouter:
                to_return[photo].append(alias.strip())

    return to_return

##### test lire photos
api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()
sheet_id = '1WhevQB9MMcYbjGF1nHscCzShFF7Qlt53WkaHHlNpao4'
r = lire_table_photos(api_sheets, sheet_id, separateur=';')
print(r)

###### test inclusion image ancien code

# def test_inclusion_images():
#     api_drive, api_doc, _ = creer_lecteurs_google_apis()
#     # donner un dossier source image, un fichier texte
#     dossier_image = '169GWiwLFVcbaZsJZvtPGo-q8gfol1gDX'
#     item_id = '1syyJGdBK2Kkar5UgWNsRWyiU1_plAQfEFeZFX9XWnbo'
#
#     #lire le texte d'origine
#     document = api_doc.documents().get(documentId=item_id).execute()
#     contenu_document = document.get('body').get('content')
#     texte_avec_format = lecteurGoogle.read_structural_elements(contenu_document)
#     texte_avec_format = texte_avec_format.replace('\v', '\n')  # pour nettoyer les backspace verticaux qui se glissent
#     print(texte_avec_format)
#
#     # lister toutes les photos du dossier source
#     dic_photos = lister_images_dans_dossier(dossier_image, api_drive)
#     print(dic_photos)
#
#     dic_photos = prendre_en_compte_prenoms_dans_dico_images(dic_photos)
#     print(dic_photos)
#
#     #trouver les emplacements des clefs
#     liste_clef_pos = trouver_clefs_plus_longues_et_positions(dic_photos, texte_avec_format)
#     print(liste_clef_pos)
#
#     #créer la requete
#     for clef, position in liste_clef_pos:
#         img_id = dic_photos[clef]
#         request = inserer_image_dans_google_doc(image_id=img_id, doc_id=item_id,
#                                                 position=position, drive_service=api_drive, docs_service=api_doc)
#         print(request)
#
#     # créer un nouveau document pour accueillir la fiche enrichie
#
#     # exporter la fiche enrichie dans le document
#
#
# test_inclusion_images()
