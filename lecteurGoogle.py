from __future__ import print_function

import logging
import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import credentials

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/documents.readonly
# https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/documents']
SCOPES = [
    'https://www.googleapis.com/auth/drive '
    'https://www.googleapis.com/auth/documents '
    'https://www.googleapis.com/auth/spreadsheets '
]

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'  # permet de mélanger l'ordre des tokens dans la déclaration

# les tailles des constantes sont faites pour avoir le matching avec les offset des google tables
# quand on voudra refaire des liens
DEBUT_TABLEAU = '\uE000' * 4
FIN_TABLEAU = '\uE001' * 2
SEPARATEUR_COLONNES = '\uE002' * 2
SEPARATEUR_LIGNES = '\uE003'
FIN_LIGNE = SEPARATEUR_COLONNES + SEPARATEUR_LIGNES
OFFSET_IMAGE = '\uE004'
# balises ajoutées dans le texte pour pouvoir reconstituer les styles
# source : https://developers.google.com/docs/api/reference/rest/v1/documents?hl=fr#paragraphstyle


# VALEURS_FORMATTAGE = {
#     'bold': ['<bold>', '</bold>'],
#     'underline': ['<underline>', '</underline>'],
#     'smallCaps': ['<smallCaps>', '</smallCaps>'],
#     'italic': ['<italic>', '</italic>'],
#     'strikethrough': ['<strikethrough>', '</strikethrough>'],
#     'backgroundColor': ['<backgroundColor>', '</backgroundColor>'],
#     # désactivé tant que je ne comprends pas comment définir les puces dans un batchupdate
#     # 'bullets': ['<bullets>', '</bullets>']
# }

CLEFS_FORMATTAGE = ['bold', 'underline', 'smallCaps', 'italic', 'strikethrough', 'backgroundColor', 'foregroundColor']


# DEBUT_TABLEAU = '¤¤d¤¤'
# FIN_TABLEAU = '¤¤f¤¤'
# SEPARATEUR_COLONNES = "¤¤c¤¤"
# SEPARATEUR_LIGNES = '¤¤l¤¤'
# FIN_LIGNE = SEPARATEUR_COLONNES + SEPARATEUR_LIGNES


# crée deux lecteurs, api_doc et ApiDoc, pour pouvoir lire plus facilement les fichiers par la suite
def creer_lecteurs_google_apis():
    """
    Crée et renvoie des instances des services Google Drive, Docs et Sheets.

    Cette fonction gère l'authentification et la création des services Google.
    Elle utilise un fichier token.json pour stocker les tokens d'accès et de rafraîchissement de l'utilisateur.
    Si le fichier token.json n'existe pas ou si les tokens ne sont pas valides, la fonction guide l'utilisateur
    à travers le flux d'autorisation.

    En cas d'erreur lors de la création des services, la fonction imprime l'erreur et renvoie None pour chaque service.

    Returns:
        api_drive: Une instance du service Google Drive.
        lecteur_doc: Une instance du service Google Docs.
        lecteur_sheets: Une instance du service Google Sheets.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    # ServiceAccountCredentials.from_json_keyfile_dict(credentials.app_creds_dic, SCOPES)

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Erreur lors du rafraichissement du token : {e}, tentative de suppression")
                try:
                    os.remove('token.json')  # Delete the current token file
                    flow = InstalledAppFlow.from_client_config(
                        credentials.app_creds_dic,
                        SCOPES)

                    # flow = InstalledAppFlow.from_client_secrets_file(
                    #     'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e2:
                    print("Erreur lors de la seconde tentative de rafraichissement du token : ", e2)
                    # Handle the second refresh error as needed
                    raise e2
        else:
            flow = InstalledAppFlow.from_client_config(
                credentials.app_creds_dic,
                SCOPES)

            # flow = InstalledAppFlow.from_client_secrets_file(
            #     'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        api_drive = build('drive', 'v3', credentials=creds, static_discovery=False)
        lecteur_doc = build('docs', 'v1', credentials=creds, static_discovery=False)
        lecteur_sheets = build('sheets', 'v4', credentials=creds, static_discovery=False)

        # api_sheets = build('drive', 'v3', credentials=creds)
        # lecteur_doc = build('docs', 'v1', credentials=creds)
        # lecteur_sheets = build('sheets', 'v4', credentials=creds)

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None, None, None

    return api_drive, lecteur_doc, lecteur_sheets


def read_paragraph_element(element, extraire_formattage=True, verbal=False):
    """Returns the text in the given ParagraphElement, including any hyperlinks.

    Args:
        :param verbal: utilisé pour ajouter des messages de debugging pendant la fonction
        :param element: a dict representing a ParagraphElement from a Google Doc.
        :param extraire_formattage:

    Returns:
        str: The text content of the element, with hyperlinks expanded.
    """
    content = ''
    text_run = element.get('textRun')

    if text_run:
        content = text_run.get('content', '')
        if extraire_formattage:
            text_style = text_run.get('textStyle', {})

            if hyperlink_info := text_style.get('link'):
                url = f"{hyperlink_info.get('url')} "
                if url:
                    content = ' '.join([content, url])

            for clef_formattage in CLEFS_FORMATTAGE:
                if clef_formattage == 'backgroundColor':
                    background_color = text_style.get('backgroundColor', {}).get('color', {})
                    if background_color:  # Checks if backgroundColor is not empty
                        rgb_color = background_color.get('rgbColor', {})
                        if verbal:
                            print(f"RGB trouvé : {rgb_color}")
                        # Checks if the color is not transparent, blank, or white
                        if rgb_color:
                            r = rgb_color.get('red', 0)
                            g = rgb_color.get('green', 0)
                            b = rgb_color.get('blue', 0)
                            if (r, g, b) == (0, 0, 0):
                                continue
                            content = formatter_surligne(content, r, g, b)
                elif clef_formattage == 'foregroundColor':
                    foreground_color = text_style.get('foregroundColor', {}).get('color', {})
                    rgb_color = foreground_color.get('rgbColor', {})
                    if verbal:
                        print(f"RGB trouvé : {rgb_color}")
                    # Checks if the color is not transparent, blank, or white
                    if rgb_color:
                        r = rgb_color.get('red', 0)
                        g = rgb_color.get('green', 0)
                        b = rgb_color.get('blue', 0)
                        if (r, g, b) == (0, 0, 0):
                            continue
                        content = formatter_couleur(content, r, g, b)

                elif text_style.get(clef_formattage):
                    content = formatter_simple(content, clef_formattage)

    return content


def read_structural_elements(elements, extraire_formattage=True, verbal=False, chars_images=False):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            :param chars_images: pour remplacer les iméges par un caractère arbitraire (permet de conserver les indexes
            relatifs de toutes les portions de texte)
            :param verbal: pour afficher des messages de debuggage en cours d'exécution
            :param elements: a list of Structural Elements.
            :param extraire_formattage:
    """
    text = ''
    for value in elements:
        if verbal:
            print(f"Value du parcours de elements : {value}")

        if 'paragraph' in value:
            if bullets := (value.get('paragraph').get('bullet') and extraire_formattage):
                # désactivé tant que je ne comprends pas comment définir les puces dans un batchupdate
                # text += VALEURS_FORMATTAGE['bullets'][0]
                text += ' - '
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                if 'inlineObjectElement' in elem:
                    # if verbal:
                    #     print("inLineObjectElement détecté")
                    inline_object_id = elem.get('inlineObjectElement').get('inlineObjectId')
                    # You can retrieve the image URL or metadata from the inline object
                    if verbal:
                        print(f"Detected image with ID: {inline_object_id}")
                    if chars_images:
                        text += OFFSET_IMAGE
                text += read_paragraph_element(elem, extraire_formattage=extraire_formattage)
            # désactivé tant que je ne comprends pas comment définir les puces dans un batchupdate
            # if bullets:
            #     text += VALEURS_FORMATTAGE['bullets'][1]
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get('table')
            text += DEBUT_TABLEAU
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    a_ajouter = read_structural_elements(cell.get('content'),
                                                         extraire_formattage=extraire_formattage,
                                                         verbal=verbal,
                                                         chars_images=chars_images
                                                         ).strip() + SEPARATEUR_COLONNES
                    text += a_ajouter
                    if verbal:
                        print(repr(a_ajouter))
                text += SEPARATEUR_LIGNES
            text = text[:-1 * len(FIN_LIGNE)] + FIN_TABLEAU

        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_structural_elements(toc.get('content'),
                                             extraire_formattage=extraire_formattage,
                                             verbal=verbal,
                                             chars_images=chars_images
                                             )
    return text + '\n'


# # renvoie un dictionnaire [label]["debut"/"fin"]
# def identifier_sections_fiche(labels_a_trouver, texte_document):
#     texte_document = texte_document.lower()
#     indexes = {
#         label: {"debut": texte_document.find(label)}
#         for label in labels_a_trouver
#     }
#     # indexes = dict()
#     # for label in labelsATrouver:
#     #     indexes[label] = {"debut": texte_document.find(label)}
#     # print("dictionnaire des labels : {0}".format(indexes))
#
#     # maintenant, on aura besoin d'identifier pour chaque label où il se termine
#     # pour cela on fait un dictionnaire ou la fin de chaque entrée est le début de la suivante
#     # print("toutes les valeurs du tableau : {0}".format([x['debut'] for x in indexes.values()]))
#     # on commence par extraire toutes les valeurs de début et les trier dans l'ordre
#     tous_les_indexes = [x['debut'] for x in indexes.values()]
#     tous_les_indexes.sort()
#     # print("Tous les indexes : {0}".format(tous_les_indexes))
#     # on crée une table qui associe à chaque début la section suivante
#     table_debuts_fins_labels = {}
#     for i in range(len(indexes)):
#         try:
#             # table_debuts_fins_labels[tous_les_indexes[i]] = tous_les_indexes[i + 1] - 1
#             table_debuts_fins_labels[tous_les_indexes[i]] = tous_les_indexes[i + 1]
#             # print("pour l'index {0}, j'ai le couple {1}:{2}".format(i, tous_les_indexes[i], tous_les_indexes[i+1]))
#         except IndexError:
#             table_debuts_fins_labels[tous_les_indexes[i]] = len(texte_document)
#             break
#     # enfin, on met à jour la table des labels pour avoir la fin à côté du début
#     for label in labels_a_trouver:
#         indexes[label]["fin"] = table_debuts_fins_labels[indexes[label]["debut"]]
#         # print("label {0} : [{1}:{2}]".format(label, indexes[label]["debut"], indexes[label]["fin"]))
#     return indexes


def text_2_dict_sections(noms_sections, texte_formatte, verbal=False):
    erreurs: list[str] = []
    if verbal:
        print(f"Je suis en train de lire les sections d'un fichier, dont le texte brut est \n {texte_formatte}")
    sections = {}
    texte_pur = retirer_balises_formattage(texte_formatte)

    lignes_texte_pur = texte_pur.split('\n')
    lignes_texte_formatte = texte_formatte.split('\n')
    current_key = None
    current_brut = []
    current_formatte = []

    for ligne_texte_pur, ligne_texte_formatte in zip(lignes_texte_pur, lignes_texte_formatte):
        if any(ligne_texte_pur.lower().strip().startswith(key) for key in noms_sections):
            if current_key:
                if current_key in sections:
                    message_erreur = f"Erreur, la section {current_key} est présente deux fois dans le fichier source"
                    print(message_erreur)
                    erreurs.append(message_erreur)
                sections[current_key] = {
                    'brut': '\n'.join(current_brut),
                    'formatté': '\n'.join(current_formatte)
                }
            # print(f"DEBUG : ligne où une clef a été trouvée : {ligne_texte_pur}")
            current_key = next(
                section for section in noms_sections if ligne_texte_pur.strip().lower().startswith(section))
            current_brut = [ligne_texte_pur.strip()]
            current_formatte = [ligne_texte_formatte.strip()]
        else:
            current_brut.append(ligne_texte_pur.strip())
            current_formatte.append(ligne_texte_formatte.strip())

    # on ajoute la dernière clef
    if current_key:
        if current_key in sections:
            message_erreur = f"Erreur, la section {current_key} est présente deux fois dans le fichier source"
            print(message_erreur)
            erreurs.append(message_erreur)
        sections[current_key] = {
            'brut': '\n'.join(current_brut),
            'formatté': '\n'.join(current_formatte)
        }

    if verbal:
        print(f"A la fin de mes passages section valait {sections}")
    return sections, erreurs


def retirer_balises_formattage(text, verbal=False):
    # to_return = text
    # for balise in CLEFS_FORMATTAGE:
    #     if verbal:
    #         print(f'je suis en train de supprimer la balise {balise} \n'
    #               f'texte avant : {to_return}')
    #     to_return = supprimer_balises(text, balise)
    #     if verbal:
    #         print(f'texte après : {to_return}')
    # if verbal:
    #     print(f'Après retirage des balises, le texte vaut : {to_return}')
    # return to_return

    # Create a pattern that matches any of the provided tags
    pattern = fr'</?({"|".join(CLEFS_FORMATTAGE)})(:[^>]+)?>'

    # Replace all occurrences of the pattern with an empty string
    result = re.sub(pattern, '', text)

    return result


# def supprimer_balises(input_string, clef):
#     # Modify pattern to handle opening and closing tags with or without arguments
#     pattern = fr'</?{clef}(:[^>]+)?>'
#
#     # Replace all occurrences of the pattern with an empty string
#     result = re.sub(pattern, '', input_string, flags=re.DOTALL)
#
#     return result

# def generer_liste_items(api_drive, nom_fichier):
#     # nom_fichier = nom_fichier
#
#     # faire la requête pour lire tous les dossiers en entrée
#
#     if len(nom_fichier) < 1:
#         print("erreur, aucun mon_id dans l'input")
#         return -1
#
#     requete = "".join(f"'{mon_id}' in parents or " for mon_id in nom_fichier)
#
#     requete = requete[:-3]
#     logging.debug(f"requete = {requete}")
#
#     # pour tenter de comprendre comment on spécifie le mimetype
#     # requete = "mimeType == application/vnd.google-apps.document"
#
#     try:
#         # Call the Drive v3 API
#         results = api_drive.files().list(
#             pageSize=200, q=requete,
#             fields="nextPageToken, files(id, name, modifiedTime, lastModifyingUser)").execute()
#
#         items = results.get('files',
#                             [])  # le q = trucs est l'identifiant du dossier drive qui contient toutes les intrigues
#         print(f"j'ai trouvé {len(items)} items ")
#         return items
#     except HttpError as err:
#         print(f'An error occurred: {err}')
#         return None
def generer_liste_items(api_drive, nom_fichier):
    if len(nom_fichier) < 1:
        print("erreur, aucun mon_id dans l'input")
        return -1

    requete = "".join(f"'{mon_id}' in parents or " for mon_id in nom_fichier)
    requete = requete[:-3]
    logging.debug(f"requete = {requete}")

    items = []  # Initialise une liste vide pour stocker les résultats
    page_token = None  # Initialise le token de page pour la pagination

    try:
        while True:
            # Appel de l'API avec gestion de la pagination
            results = api_drive.files().list(
                pageSize=200,
                q=requete,
                fields="nextPageToken, files(id, name, modifiedTime, lastModifyingUser)",
                pageToken=page_token  # Utilise le token de page actuel
            ).execute()

            # Ajoute les fichiers de cette page à la liste des items
            items.extend(results.get('files', []))

            # Met à jour le token de page avec le prochain, s'il existe
            page_token = results.get('nextPageToken', None)
            if page_token is None:
                break  # Si aucun token de page suivant, fin de la boucle

        print(f"j'ai trouvé {len(items)} items")
        return items
    except HttpError as err:
        print(f'An error occurred: {err}')
        return None


def formatter_tableau_pour_export(tableau: list):
    to_return = DEBUT_TABLEAU

    for ligne in tableau:
        for cellule in ligne:
            to_return += f'{cellule}{SEPARATEUR_COLONNES}'
            # a_inserer = cellule if len(cellule) else ' '
            # to_return += f'{a_inserer}{SEPARATEUR_COLONNES}'
        to_return += SEPARATEUR_LIGNES

    # on enlève le dernier FIN LIGNE pour le remplacer par un FIN TABLEAU
    return to_return[:-1 * len(FIN_LIGNE)] + FIN_TABLEAU


def formatter_gras(nom):
    return formatter_simple(nom, 'bold')


def formatter_souligne(text):
    return formatter_simple(text, "underline")


def formatter_simple(text, clef):
    return f"<{clef}>{text}</{clef}>"


def formatter_surligne(text, r, g, b):
    clef_complete = f"backgroundColor:{r}/{g}/{b}"
    return f"<{clef_complete}>{text}</{clef_complete}>"


def formatter_couleur(content, r, g, b):
    clef_complete = f"foregroundColor:{r}/{g}/{b}"
    return f"<{clef_complete}>{content}</{clef_complete}>"

