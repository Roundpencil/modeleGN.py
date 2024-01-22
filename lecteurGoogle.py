from __future__ import print_function

import os.path
from enum import Enum

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import credentials

import logging

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

# balises ajoutées dans le texte pour pouvoir reconstituer les styles
# source : https://developers.google.com/docs/api/reference/rest/v1/documents?hl=fr#paragraphstyle
# class FORMATTAGE(Enum):
#     PREFIXE_GRAS_ON = '<bold>'
#     PREFIXE_GRAS_OFF = '</bold>'
#     PREFIXE_ITALIQUE_ON = '<italic>'
#     PREFIXE_ITALIQUE_OFF = '</italic>'
#     PREFIXE_SOULIGNE_ON = '<souligné>'
#     PREFIXE_SOULIGNE_OFF = '</souligné>'
#     PREFIXE_BARRE_ON = '<barré>'
#     PREFIXE_BARRE_OFF = '</barré>'
#     PREFIXE_SMALLCAPS_ON = '<small_caps>'
#     PREFIXE_SMALLCAPS_OFF = '</small_caps>'


# VALEURS_FORMATTAGE = [f.value for f in FORMATTAGE]
VALEURS_FORMATTAGE = {
    'bold': ['<bold>', '</bold>'],
    'underline': ['<underline>', '</underline>'],
    'smallCaps': ['<smallCaps>', '</smallCaps>'],
    'italic': ['<italic>', '</italic>'],
    'strikethrough': ['<strikethrough>', '</strikethrough>']
}


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
                print("Erreur lors du rafraichissement du token : ", e)
                raise e
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


def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement, including any hyperlinks.

    Args:
        element: a dict representing a ParagraphElement from a Google Doc.

    Returns:
        str: The text content of the element, with hyperlinks expanded.
    """
    content = ''
    text_run = element.get('textRun')

    if text_run:
        content = text_run.get('content', '')
        text_style = text_run.get('textStyle', {})
        hyperlink_info = text_style.get('link')

        # if hyperlink_info:
        #     url = f"{hyperlink_info.get('url')} "
        #     if url:
        #         content = ' '.join([content, url])

        if hyperlink_info := text_style.get('link'):
            url = f"{hyperlink_info.get('url')} "
            if url:
                content = ' '.join([content, url])

        for clef_formattage in VALEURS_FORMATTAGE:
            if text_style.get(clef_formattage):
                content = ''.join([VALEURS_FORMATTAGE[clef_formattage][0],
                                   content,
                                   VALEURS_FORMATTAGE[clef_formattage][1]])

        #             = {

    #         if text_style.get('bold'):
    #             content = ''.join([FORMATTAGE.PREFIXE_GRAS_ON, content, FORMATTAGE.PREFIXE_GRAS_OFF])
    #
    #         if text_style.get('italic'):
    #             content = ''.join([FORMATTAGE.PREFIXE_ITALIQUE_ON, content, FORMATTAGE.PREFIXE_ITALIQUE_OFF])
    #
    #         if text_style.get('underline'):
    #             content = ''.join([FORMATTAGE.PREFIXE_SOULIGNE_ON, content, FORMATTAGE.PREFIXE_SOULIGNE_OFF])
    #
    #         if text_style.get('strikethrough'):
    #             content = ''.join([FORMATTAGE.PREFIXE_BARRE_ON, content, FORMATTAGE.PREFIXE_BARRE_OFF])
    #
    #         if text_style.get('smallCaps'):
    #             content = ''.join([FORMATTAGE.PREFIXE_SMALLCAPS_ON, content, FORMATTAGE.PREFIXE_SMALLCAPS_OFF])

    return content


# def read_paragraph_element(element):
#     """Returns the text in the given ParagraphElement.
#
#         Args:
#             element: a ParagraphElement from a Google Doc.
#     """
#     text_run = element.get('textRun')
#     return text_run.get('content') if text_run else ''
#     # if not text_run:
#     #     return ''
#     # return text_run.get('content')


def read_structural_elements(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """
    text = ''
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text += read_paragraph_element(elem)
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get('table')
            text += DEBUT_TABLEAU
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    text += read_structural_elements(cell.get('content')) + SEPARATEUR_COLONNES
                text += SEPARATEUR_LIGNES
            text = text[:-1 * len(FIN_LIGNE)] + FIN_TABLEAU

        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_structural_elements(toc.get('content'))
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
                    print(f"Erreur, la section {current_key} est présente deux fois dans le fichier source")
                sections[current_key] = {
                    'brut': '\n'.join(current_brut),
                    'formatté': '\n'.join(current_formatte)
                }
            # print(f"DEBUG : ligne où une clef a été trouvée : {ligne_texte_pur}")
            current_key = next(section for section in noms_sections if ligne_texte_pur.strip().lower().startswith(section))
            current_brut = [ligne_texte_pur.strip()]
            current_formatte = [ligne_texte_formatte.strip()]
        else:
            current_brut.append(ligne_texte_pur.strip())
            current_formatte.append(ligne_texte_formatte.strip())
        #
        # # Check if the line starts with a keyword
        # for key in noms_sections:
        #     if verbal:
        #         print(f"Je suis en train de vérifier la clef {key} pour la chaine {ligne_texte_pur.lower().strip()}")
        #     if ligne_texte_pur.lower().strip().startswith(key):
        #         if current_key:
        #             sections[current_key] = {
        #                 'brut': '\n'.join(current_brut),
        #                 'formatté': '\n'.join(current_formatte)
        #             }
        #         current_key = key
        #         current_brut = [ligne_texte_pur.strip()]
        #         current_formatte = [ligne_texte_formatte.strip()]
        #         break
        #
        #     # else:  # This else belongs to the for-loop
        #     #     if current_key:
        #     #         current_brut.append(ligne_texte_pur.strip())
        #     #         current_formatte.append(ligne_texte_formatte.strip())
        #     #     break
        # if len(current_brut) > 1:
        #     current_brut.append(ligne_texte_pur.strip())
        #     current_formatte.append(ligne_texte_formatte.strip())

    # on ajoute la dernière clef
    if current_key:
        if current_key in sections:
            print(f"Erreur, la section {current_key} est présente deux fois dans le fichier source")
        sections[current_key] = {
            'brut': '\n'.join(current_brut),
            'formatté': '\n'.join(current_formatte)
        }

    if verbal:
        print(f"A la fin de mes passages section valait {sections}")
    return sections


def retirer_balises_formattage(text, verbal=False):
    to_return = text
    for couple_balises in VALEURS_FORMATTAGE.values():
        for balise in couple_balises:
            if verbal:
                print(f'je suis en train de supprimer la balise {balise} \n'
                      f'texte avant : {to_return}')
            to_return = to_return.replace(balise, '')
            if verbal:
                print(f'texte après : {to_return}')
    if verbal:
        print(f'Après retirage des balises, le texte vaut : {to_return}')
    return to_return


def generer_liste_items(api_drive, nom_fichier):
    # nom_fichier = nom_fichier

    # faire la requête pour lire tous les dossiers en entrée

    if len(nom_fichier) < 1:
        print("erreur, aucun mon_id dans l'input")
        return -1

    requete = "".join(f"'{mon_id}' in parents or " for mon_id in nom_fichier)

    requete = requete[:-3]
    logging.debug(f"requete = {requete}")

    # pour tenter de comprendre comment on spécifie le mimetype
    # requete = "mimeType == application/vnd.google-apps.document"

    try:
        # Call the Drive v3 API
        results = api_drive.files().list(
            pageSize=200, q=requete,
            fields="nextPageToken, files(id, name, modifiedTime, lastModifyingUser)").execute()

        items = results.get('files',
                            [])  # le q = trucs est l'identifiant du dossier drive qui contient toutes les intrigues
        print(f"j'ai trouvé {len(items)} items ")
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
