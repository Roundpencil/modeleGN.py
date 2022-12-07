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


def extrairePJs(monGN, apiDrive, apiDoc, singletest="-01"):
    folderid = monGN.folderIntriguesID

    #faire la requête pour lire tous les dossiers en entrée

    if len(folderid) < 1:
        print("erreur, aucun id dans l'input")
        return -1

    requete = ''
    for id in folderid:
        requete += f"'{id}' in parents or"
    requete = requete[:-3]
    print(f"requete = {requete}")

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

        if not items:
            print('No files found.')
            return

        for item in items:
            # print ("poung")

            # print ("ping")
            # Retrieve the documents contents from the Docs service.
            document = apiDoc.documents().get(documentId=item['id']).execute()
            # print ("pong")

            print('Titre document : {}'.format(document.get('title')))
            # print(document.get('title')[0:2])

            if not document.get('title')[0:2].isdigit():
                # print("... n'est pas un personnage")
                continue

            # print("... est un personnage !")

            # si contient "-01" fera toutes les intrigues, sinon seule celle qui est spécifiée
            if int(singletest) > 0:
                # Alors on se demandne si c'est la bonne
                if document.get('title')[0:2] != str(singletest):  # numéro de l'intrigue
                    # si ce n'est pas la bonne, pas la peine d'aller plus loin
                    continue
                else:
                    print("perso {0} trouvée".format(singletest))

            # du coup on traite

            # on vérifie d'abord s'il est nécessaire de traiter (dernière maj intrigue > derniere maj objet) :
            #   SI l'intrigue existe dans le GN ?
            if item['id'] in monGN.dictPJs.keys():
                #       SI la date de mise à jour du fichier n'est pas postérieure à la date de MAJ de l'intrigue
                # print("l'intrigue fait déjà partie du GN ! ")
                # print(f"Variable / type : monGN.intrigues[item['id']].lastChange / {type(monGN.intrigues[item['id']].lastChange)} / {monGN.intrigues[item['id']].lastChange}")
                # print(f"Variable / type : item['modifiedTime'] / {type(item['modifiedTime'])} / {item['modifiedTime']}")

                # on enlève les 5 derniers chars qui sont un point, les millisecondes et Z, pour formatter
                if monGN.dictPJs[item['id']].lastChange >= datetime.datetime.strptime(item['modifiedTime'][:-5],
                                                                                        '%Y-%m-%dT%H:%M:%S'):
                    print("et il n'a pas changé depuis le dernier passage")
                    # ALORS : Si c'est la même que la plus vielle mise à jour : on arrête
                    # si c'était la plus vieille du GN, pas la peine de continuer
                    if monGN..oldestUpdatedPJ == item['id']:
                        print("et d'ailleurs c'était le plus vieux > j'ai fini !")
                        break
                    else:
                        # sinon on passe au perso suivant (sauf si on est dans singletest)
                        if int(singletest) > 0:
                            print("stop !")
                            # alors si on est toujours là, c'est que c'était notre intrigue
                            # pas la peine d'aller plus loin
                            return
                        continue
                else:
                    print("il a changé depuis mon dernier passage : supprimons-la !")
                    # dans ce cas il faut la supprimer car on va tout réécrire
                    monGN.dictPJs[item['id']].clear()
                    del monGN.dictPJs[item['id']]

            print("et du coup, il est est temps de créer un nouveau fichier")
            # à ce stade, soit on sait qu'elle n'existait pas, soit on l'a effacée pour la réécrire
            contenuDocument = document.get('body').get('content')
            text = read_structural_elements(contenuDocument)
            #todo fonction de lecture de PJ

    except HttpError as err:
        print(f'An error occurred: {err}')
        # return #ajouté pour débugger
