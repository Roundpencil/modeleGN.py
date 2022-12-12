from __future__ import print_function

import datetime
import os.path
import re

import lecteurGoogle
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
    print("début extractions PJs")

    items = lecteurGoogle.genererListeItems(monGN, apiDrive=apiDrive, folderID=monGN.folderPJID)

    if not items:
        print('No files found.')
        return

    for item in items:
        try:
            # print ("poung")

            # print ("ping")
            # Retrieve the documents contents from the Docs service.
            document = apiDoc.documents().get(documentId=item['id']).execute()
            # print ("pong")

            print('Titre document : {}'.format(document.get('title')))
            # print(document.get('title')[0:2])


            # if not document.get('title')[0:2].isdigit():
            #     # print("... n'est pas un personnage")
            #     continue

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
                    if monGN.oldestUpdatedPJ == item['id']:
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
                    # print("il a changé depuis mon dernier passage : supprimons-le !")
                    # dans ce cas il faut la supprimer car on va tout réécrire
                    monGN.dictPJs[item['id']].clear()
                    del monGN.dictPJs[item['id']]

            # print("et du coup, il est est temps de créer un nouveau fichier")
            # à ce stade, soit on sait qu'elle n'existait pas, soit on l'a effacée pour la réécrire
            contenuDocument = document.get('body').get('content')
            text = lecteurGoogle.read_structural_elements(contenuDocument)

            monPJ = extrairePJDeTexte(text, document.get('title'), item["id"], monGN)
            # monIntrigue.url = item["id"]

            # print(f"j'ai ajouté : {monPJ.nom}")



            # print(f'url intrigue = {monIntrigue.url}')
            # print(f"intrigue {monIntrigue.nom}, date de modification : {item['modifiedTime']}")

            if int(singletest) > 0:
                print("stop !")
                # alors si on est toujours là, c'est que c'était notre PJ
                # pas la peine d'aller plus loin
                return
            # print("here we go again")

        except HttpError as err:
            print(f'An error occurred: {err}')
            # return #ajouté pour débugger


def extrairePJDeTexte(textePJ, nomDoc, idUrl, monGN):
    if len(textePJ) < 800:
        print(f"fiche {nomDoc} avec {len(textePJ)} caractères est vide")
        return #dans ce cas c'est qu'on est en train de lite un template, qui fait 792 cars

    nomPJ = re.sub(r"^\d+\s*-", '', nomDoc).strip()
    # print(f"nomDoc =_{nomDoc}_ nomPJ =_{nomPJ}_")
    # print(f"Personnage en cours d'importation : {nomPJ} avec {len(textePJ)} caractères")
    currentPJ = Personnage(nom=nomPJ, url=idUrl)
    monGN.dictPJs[idUrl] = currentPJ

    textePJLow = textePJ.lower()  # on passe en minuscule pour mieux trouver les chaines

    REFERENT = "orga référent"
    JOUEURV1 = "joueur v1"
    JOUEURV2 = "joueur v2"
    JOUEUSE1 = "joueuse v1"
    JOUEUSE2 = "joueuse v2"
    PITCH = "pitch perso"
    COSTUME = "indications costumes"
    FACTION1 = "faction principale"
    FACTION2 = "faction secondaire"
    BIO = "bio résumée"
    PSYCHO = "psychologie"
    MOTIVATIONS = "motivations et objectifs"
    CHRONOLOGIE = "chronologie "
    INTRIGUES = "intrigues"
    RELATIONS = "relations avec les autres persos"

    labels = [REFERENT, JOUEURV1, JOUEURV2, PITCH, COSTUME, FACTION1, FACTION2,
              BIO, PSYCHO, MOTIVATIONS, CHRONOLOGIE, RELATIONS, INTRIGUES, JOUEUSE1, JOUEUSE2]

    indexes = lecteurGoogle.identifierSectionsFiche(labels, textePJ)

    if indexes[REFERENT]["debut"] == -1:
        print("pas de référént avec le perso " + nomPJ)
    else:
        currentPJ.orgaReferent = textePJ[indexes[REFERENT]["debut"]:indexes[REFERENT]["fin"]].splitlines()[
                                     0][
                                 len(REFERENT) + len(" : "):]

    if indexes[JOUEURV1]["debut"] == -1:
        print("Pas de joueur 1 avec le perso " + nomPJ)
    else:
        currentPJ.joueurs['V1'] = textePJ[indexes[JOUEURV1]["debut"]:indexes[JOUEURV1]["fin"]].splitlines()[
                                      0][
                                  len(JOUEURV1) + len(" : "):]

    if indexes[JOUEURV2]["debut"] == -1:
        print("Pas de joueur 2 avec le perso " + nomPJ)
    else:
        currentPJ.joueurs['V2'] = textePJ[indexes[JOUEURV2]["debut"]:indexes[JOUEURV2]["fin"]].splitlines()[
                                      0][
                                  len(JOUEURV1) + len(" : "):]

    if indexes[JOUEUSE1]["debut"] == -1:
        print("Pas de joueuse 1 avec le perso " + nomPJ)
    else:
        currentPJ.joueurs['V1'] = textePJ[indexes[JOUEUSE1]["debut"]:indexes[JOUEUSE1]["fin"]].splitlines()[
                                      0][
                                  len(JOUEURV1) + len(" : "):]

    if indexes[JOUEUSE2]["debut"] == -1:
        print("Pas de joueuse 2 avec le perso " + nomPJ)
    else:
        currentPJ.joueurs['V2'] = textePJ[indexes[JOUEUSE2]["debut"]:indexes[JOUEUSE2]["fin"]].splitlines()[
                                      0][
                                  len(JOUEURV1) + len(" : "):]

    if indexes[PITCH]["debut"] == -1:
        print("Pas de pitch  avec le perso " + nomPJ)
    else:
        currentPJ.pitch = textePJ[indexes[PITCH]["debut"]:indexes[PITCH]["fin"]].splitlines()[1:]

    if indexes[COSTUME]["debut"] == -1:
        print("Pas d'indication costume avec le perso " + nomPJ)
    else:
        currentPJ.indicationsCostume = textePJ[indexes[COSTUME]["debut"] + len(COSTUME) + len(" : "):
                                               indexes[COSTUME]["fin"]]

    if indexes[FACTION1]["debut"] == -1:
        print("Pas de faction 1 avec le perso " + nomPJ)
    else:
        currentPJ.factions.append(textePJ[indexes[FACTION1]["debut"]:indexes[FACTION1]["fin"]].splitlines()[
                                     0][
                                 len(FACTION1) + len(" : "):])

    if indexes[FACTION2]["debut"] == -1:
        print("Pas de faction 2 avec le perso " + nomPJ)
    else:
        currentPJ.factions.append(textePJ[indexes[FACTION2]["debut"]:indexes[FACTION2]["fin"]].splitlines()[
                                     0][
                                 len(FACTION2) + len(" : "):])

    if indexes[BIO]["debut"] == -1:
        print("Pas de BIO avec le perso " + nomPJ)
    else:
        currentPJ.description = textePJ[indexes[BIO]["debut"]:
                                         indexes[BIO]["fin"]].splitlines()[1:]

    if indexes[PSYCHO]["debut"] == -1:
        print("Pas de psycho avec le perso " + nomPJ)
    else:
        currentPJ.concept = textePJ[indexes[PSYCHO]["debut"]:
                                         indexes[PSYCHO]["fin"]].splitlines()[1:]

    if indexes[MOTIVATIONS]["debut"] == -1:
        print("Pas de motivations avec le perso " + nomPJ)
    else:
        currentPJ.driver = textePJ[indexes[MOTIVATIONS]["debut"]:indexes[MOTIVATIONS]["fin"]].splitlines()[
                                     0][
                                 len(MOTIVATIONS) + len(" : "):]

    #rajouter les scènes en jeu après le tableau
    bottomText = textePJ.split("#####")[-1]
    currentPJ.textesAnnexes = bottomText

    # et on enregistre la date de dernière mise à jour de l'intrigue
    currentPJ.lastChange = datetime.datetime.now()

    return currentPJ