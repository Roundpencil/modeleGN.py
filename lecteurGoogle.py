from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/documents.readonly
# https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/documents']
SCOPES = [
    'https://www.googleapis.com/auth/drive '
    'https://www.googleapis.com/auth/documents '
    'https://www.googleapis.com/auth/spreadsheets '
]

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'  # permet de mélanger l'ordre des tokens dans la déclaration


# crée deux lecteurs, api_doc et ApiDoc, pour pouvoir lire plus facilement les fichiers par la suite
def creer_lecteurs_google_apis():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
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
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')
    return text_run.get('content') if text_run else ''
    # if not text_run:
    #     return ''
    # return text_run.get('content')


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
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    text += read_structural_elements(cell.get('content')) + "¤¤¤"
                text += "¤¤"
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_structural_elements(toc.get('content'))
    return text


# renvoie un dictionnaire [label]["debut"/"fin"]
def identifier_sections_fiche(labelsATrouver, texte_document):
    texte_document = texte_document.lower()
    indexes = {
        label: {"debut": texte_document.find(label)}
        for label in labelsATrouver
    }
    # indexes = dict()
    # for label in labelsATrouver:
    #     indexes[label] = {"debut": texte_document.find(label)}
    # print("dictionnaire des labels : {0}".format(indexes))

    # maintenant, on aura besoin d'identifier pour chaque label où il se termine
    # pour cela on fait un dictionnaire ou la fin de chaque entrée est le début de la suivante
    # print("toutes les valeurs du tableau : {0}".format([x['debut'] for x in indexes.values()]))
    # on commence par extraire toutes les valeurs de début et les trier dans l'ordre
    tous_les_indexes = [x['debut'] for x in indexes.values()]
    tous_les_indexes.sort()
    # print("Tous les indexes : {0}".format(tous_les_indexes))
    # on crée une table qui associe à chaque début la section suivante
    table_debuts_fins_labels = {}
    for i in range(len(indexes)):
        try:
            table_debuts_fins_labels[tous_les_indexes[i]] = tous_les_indexes[i + 1] - 1
            # print("pour l'index {0}, j'ai le couple {1}:{2}".format(i, tous_les_indexes[i], tous_les_indexes[i+1]))
        except IndexError:
            table_debuts_fins_labels[tous_les_indexes[i]] = len(texte_document)
            break
    # enfin, on met à jour la table des labels pour avoir la fin à côté du début
    for label in labelsATrouver:
        indexes[label]["fin"] = table_debuts_fins_labels[indexes[label]["debut"]]
        # print("label {0} : [{1}:{2}]".format(label, indexes[label]["debut"], indexes[label]["fin"]))
    return indexes


def generer_liste_items(monGN, apiDrive, nom_fichier):
    # nom_fichier = nom_fichier

    # faire la requête pour lire tous les dossiers en entrée

    if len(nom_fichier) < 1:
        print("erreur, aucun mon_id dans l'input")
        return -1

    requete = "".join(f"'{mon_id}' in parents or " for mon_id in nom_fichier)

    requete = requete[:-3]
    print(f"requete = {requete}")

    # pour tenter de comprendre comment on spécifie le mimetype
    # requete = "mimeType == application/vnd.google-apps.document"

    try:
        # Call the Drive v3 API
        # results = api_doc.files().list(
        #     pageSize=100, q="'1toM693dBuKl8OPMDmCkDix0z6xX9syjA' in parents",
        #     fields="nextPageToken, files(mon_id, name, modifiedTime)").execute()
        results = apiDrive.files().list(
            pageSize=100, q=requete,
            fields="nextPageToken, files(id, name, modifiedTime, lastModifyingUser)").execute()

        items = results.get('files',
                            [])  # le q = trucs est l'identifiant du dossier drive qui contient toutes les intrigues
        print(f"j'ai trouvé {len(items)} items ")
        return items
    except HttpError as err:
        print(f'An error occurred: {err}')
        return None
