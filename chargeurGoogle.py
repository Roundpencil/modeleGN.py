from __future__ import print_function

import os.path
import re

from modeleGN import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/documents.readonly']

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1' #permet de mélanger l'ordre des tokens dans la déclaration

folderid = "1toM693dBuKl8OPMDmCkDix0z6xX9syjA" #le folder des intrigues de Chalacta

def main():

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
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        results = service.files().list(
            pageSize = 100, q = "'1toM693dBuKl8OPMDmCkDix0z6xX9syjA' in parents", fields = "nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        for item in items:
            try:
                # print ("poung")

                lecteurDoc = build('docs', 'v1', credentials=creds)

                # print ("ping")
                # Retrieve the documents contents from the Docs service.
                document = lecteurDoc.documents().get(documentId=item['id']).execute()
                # print ("pong")

                # print('Titre document : {}'.format(document.get('title')))
                # print(document.get('title')[0:2])

                if document.get('title')[0:2] == "33": # alors on est dans les bonnes affaires de timagua, qui sert de pilote
                    print("intrigue timagua trouvée")
                    contenuDocument = document.get('body').get('content')
                    text = read_structural_elements(contenuDocument)

                    # print(text) #test de la focntion récursive pour le texte
                    extraireIntrigueDeTexte(text, document.get('title'))

                # return #ajouté pour débugger
            except HttpError as err:
                print(err)
                # return #ajouté pour débugger
    except HttpError as error:
        # Handle errors from drive API.
        print(f'An error occurred: {error}')

def extraireIntrigueDeTexte(texteIntrigue, nomIntrigue):
    currentIntrigue = Intrigue(nom=nomIntrigue)

    sections = texteIntrigue.split("###")
    # sections = re.findall(r'###.*', texteIntrigue, flags=re.DOTALL)
    # sections = re.findall(r'###.*', texteIntrigue, flags=re.MULTILINE|re.DOTALL)
    # sections = re.findall(r'###[.\n]?', texteIntrigue)
    print("Nous avons " + str(len(sections)) + " sections")

    for section in sections:
        # debutSection = section[0:10] #repplacer par une regexp pour être sur de choper toute la ligne
        # print("début de la section " + section[0:10])à
        # print("début de la section +1 " + section[0:11])
        # print("texte de la section : " + section)
        # print("texte de la section7_:_" + section[0:7])

        if section[0:6] == " Pitch":
        # if section[0:10] == '### Pitch':
        # if debutSection == "### Pitch":
            #choper le pitch
            currentIntrigue.pitch = ''.join(section.splitlines(keepends=True)[1:])
            # print("section pitch trouvée : " + section)
            # print("pitch isolé after découpage : " + ''.join(section.splitlines(keepends=True)[1:]))
            print("pitch lu dans l'intrigue après mise à jour : " + currentIntrigue.pitch)

        elif section[0:5] == " Todo":
            currentIntrigue.questions_ouvertes = ''.join(section.splitlines()[1:])

        elif section[0:6] == " Notes":
            currentIntrigue.questions_ouvertes = ''.join(section.splitlines()[1:])

        elif section[0:9] == " Scène : ":
            titreScene = section.splitlines()[0][9:].strip()
            sceneAAjouter = Scene(currentIntrigue, titreScene)
            print("titre de la scène ajoutée : " + sceneAAjouter.titre)

            balises = re.findall(r'##.*', section)
            for balise in balises:
                print("balise : " + balise)
                if balise[0:9] == '## Quand?':
                    sceneAAjouter.date = balise[10:].strip()
                    print("date de la scène : " + sceneAAjouter.date)
                elif balise[0:7] == '## Qui?':
                    roles = balise[8:].split(", ")
                    print("rôles trouvés : " + str(roles))
                    for nomRole in roles:
                        sceneAAjouter.addRole(currentIntrigue.getOrAddRole(nomRole))
                elif balise[0:11] == '## Niveau :':
                    sceneAAjouter.niveau = balise[12:].strip()

                elif balise[0:11] == '## Resumé :':
                    sceneAAjouter.resume = balise[12:0].strip()
                    pass
                else:
                    print("balise inconnue : " + balise)


            sceneAAjouter.description = ''.join(section.splitlines(keepends=True)[1+len(balises):])
            print("texte de la scene apres insertion : " + sceneAAjouter.description)

            pass
        elif section[0] == "\n":
            print("Marqueur de fin de section trouvé")
            pass
        else:
            print("Délimiteur de section inconnu : " + section.splitlines()[0])

    return currentIntrigue


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
                    text += read_structural_elements(cell.get('content'))
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_structural_elements(toc.get('content'))
    return text


if __name__ == '__main__':
    main()