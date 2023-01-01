from __future__ import print_function

import datetime
import os.path
import re

import modeleGN
from modeleGN import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from fuzzywuzzy import process

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/documents.readonly']

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'  # permet de mélanger l'ordre des tokens dans la déclaration


# crée deux lecteurs, apiDrive et ApiDoc, pour pouvoir lire plus facilement les fichiers par la suite
def creerLecteursGoogleAPIs():
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
        apiDrive = build('drive', 'v3', credentials=creds)
        lecteurDoc = build('docs', 'v1', credentials=creds)

    except HttpError as error:
        print(f'An error occurred: {error}')

    return apiDrive, lecteurDoc


def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')
    if not text_run:
        return ''
    return text_run.get('content')


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
def identifierSectionsFiche(labelsATrouver, texteDocument):
    texteDocument = texteDocument.lower()
    # on passe en minuscule pour mieux trouver les chaines

    indexes = dict()
    for label in labelsATrouver:
        indexes[label] = {"debut": texteDocument.find(label)}
        # on complètera la seconde dimension (fin) plus bas avec la fin de la séquence
    # print("dictionnaire des labels : {0}".format(indexes))
    # maintenant, on aura besoin d'identifier pour chaque label où il se termine
    # pour cela on fait un dictionnaire ou la fin de chaque entrée est le début de la suivante
    # print("toutes les valeurs du tableau : {0}".format([x['debut'] for x in indexes.values()]))
    # on commence par extraire toutes les valeurs de début et les trier dans l'ordre
    tousLesIndexes = [x['debut'] for x in indexes.values()]
    tousLesIndexes.sort()
    # print("Tous les indexes : {0}".format(tousLesIndexes))
    # on crée une table qui associe à chaque début la section suivante
    tableDebutsFinsLabels = dict()
    for i in range(len(indexes)):
        try:
            tableDebutsFinsLabels[tousLesIndexes[i]] = tousLesIndexes[i + 1] - 1
            # print("pour l'index {0}, j'ai le couple {1}:{2}".format(i, tousLesIndexes[i], tousLesIndexes[i+1]))
        except IndexError:
            tableDebutsFinsLabels[tousLesIndexes[i]] = len(texteDocument)
            break
    # enfin on met à jour la table des labels pour avoir la fin à côté du début
    for label in labelsATrouver:
        indexes[label]["fin"] = tableDebutsFinsLabels[indexes[label]["debut"]]
        # print("label {0} : [{1}:{2}]".format(label, indexes[label]["debut"], indexes[label]["fin"]))
    return indexes


def genererListeItems(monGN, apiDrive, folderID):
    folderid = folderID

    # faire la requête pour lire tous les dossiers en entrée

    if len(folderid) < 1:
        print("erreur, aucun id dans l'input")
        return -1

    requete = ""
    for id in folderid:
        requete += f"'{id}' in parents or"
    requete = requete[:-3]
    print(f"requete = {requete}")

    ## pour tentere de comprendre comment on spécifie le mimetype
    # requete = "mimeType == application/vnd.google-apps.document"

    try:
        # Call the Drive v3 API
        # results = apiDrive.files().list(
        #     pageSize=100, q="'1toM693dBuKl8OPMDmCkDix0z6xX9syjA' in parents",
        #     fields="nextPageToken, files(id, name, modifiedTime)").execute()
        results = apiDrive.files().list(
            pageSize=100, q=requete,
            fields="nextPageToken, files(id, name, modifiedTime)").execute()

        items = results.get('files',
                            [])  # le q = trucs est l'identifiant du dossier drive qui contient toutes les intrigues
        print((f"j'ai trouvé {len(items)} items "))
        return items
    except HttpError as err:
        print(f'An error occurred: {err}')
        return None
