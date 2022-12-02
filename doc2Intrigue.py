from __future__ import print_function

import os.path
import re

from modeleGN import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from fuzzywuzzy import process

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/documents.readonly']

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1' #permet de mélanger l'ordre des tokens dans la déclaration

folderid = "1toM693dBuKl8OPMDmCkDix0z6xX9syjA" #le folder des intrigues de Chalacta

def extraireIntrigues(monGN):

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

                print('Titre document : {}'.format(document.get('title')))
                # print(document.get('title')[0:2])

                if not document.get('title')[0:2].isdigit():
                    print("... n'est pas une intrigue")
                    continue

                print("... est une intrigue !")

                singletest = "81"
                if int(singletest) > 0:
                    #pour tester sur une intrigue en particulier
                    if document.get('title')[0:2] == str(singletest): #numéro de l'intrigue
                        print("intrigue {0} trouvée".format(singletest))
                        contenuDocument = document.get('body').get('content')
                        text = read_structural_elements(contenuDocument)

                        # print(text) #test de la focntion récursive pour le texte
                        extraireIntrigueDeTexte(text, document.get('title'), monGN)
                        return
                else:
                    #pour tester en live...
                    # print("*** intrigue en cours : " + document.get('title'))
                    contenuDocument = document.get('body').get('content')
                    text = read_structural_elements(contenuDocument)
                    extraireIntrigueDeTexte(text, document.get('title'), monGN)


                # return #ajouté pour débugger
            except HttpError as err:
                print(err)
                # return #ajouté pour débugger
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


def extraireIntrigueDeTexte(texteIntrigue, nomIntrigue, monGN):
    #todo : une fois qu'il y aura un objet GN serialisé, ajouter pour chaque intrigue une date de dernière mise à jour pour croiser avec le fichier > si mise à jour : réécriture de toute la scène, sinon passer la mise à jour

    # print("texte intrigue en entrée : ")
    # print(texteIntrigue)
    # print("*****************************")

    labelOrgaReferent = "orga référent"
    labelTodo = "etat de l’intrigue"
    labelResume = "résumé de l’intrigue"
    labelPJs = "personnages impliqués"
    labelPNJs = "pnjs impliqués"
    labelRerolls = "rerolls possibles"
    labelObjets = "objets liés"
    labelFX = "scènes nécessaires et FX"
    labelTimeline = "chronologie des événements"
    labelScenes = "détail de l’intrigue"
    labelResolution = "résolution de l’intrigue"
    labelNotes = "notes supplémentaires"

    currentIntrigue = Intrigue(nom=nomIntrigue)
    monGN.intrigues.add(currentIntrigue)
    nomspersos = monGN.getNomsPersos()

    texteIntrigueLow = texteIntrigue.lower()

    indexDebutReferent = texteIntrigueLow.find(labelOrgaReferent)
    indexDebutTodo = texteIntrigueLow.find(labelTodo)
    indexDebutResume = texteIntrigueLow.find(labelResume)
    indexDebutPjs = texteIntrigueLow.find(labelPJs)
    indexDebutPNJs = texteIntrigueLow.find(labelPNJs)
    indexDebutRerolls = texteIntrigueLow.find(labelRerolls)
    indexDebutObjets = texteIntrigueLow.find(labelObjets)
    indexDebutFX = texteIntrigueLow.find(labelFX)
    indexDebutTimeline = texteIntrigueLow.find(labelTimeline)
    indexDebutScenes = texteIntrigueLow.find(labelScenes)
    indexdebutResolution = texteIntrigueLow.find(labelResolution)
    indexDebutNotes = texteIntrigueLow.find(labelNotes)


    #todo : mettre en place un failsafe en cas de disparition d'un tag?
    #ou bien mettre toutes les valeurs dans un tableau et ré-identifier les sections en focntion de ce qu'on a?

    indexFinReferent = indexDebutTodo - 1
    indexFinTodo = indexDebutResume - 1
    indexFinResume = indexDebutPjs - 1
    indexFinPjs = indexDebutPNJs - 1
    indexFinPNJs = indexDebutRerolls - 1
    indexFinRerolls = indexDebutObjets - 1
    indexFinObjets = indexDebutFX - 1
    indexFinFX = indexDebutTimeline - 1
    indexFinTimeline = indexDebutScenes - 1
    indexFinScenes = indexdebutResolution - 1
    indexFinResolution = indexDebutNotes - 1
    indexFinNotes = len(texteIntrigue)

    #gestion de la section OrgaRéférent
    if indexDebutReferent == -1:
        print("problème référent avec l'intrigue " + nomIntrigue)
    else:
        currentIntrigue.orgaReferent = texteIntrigue[indexDebutReferent:indexFinReferent].splitlines()[0][len(labelOrgaReferent) + len(" : "):] #prendre la première ligne puis les caractères à partir du label
        # print("debut / fin orga référent : {0}/{1} pour {2}".format(indexDebutReferent, indexFinReferent, nomIntrigue))
        # print("Orga référent : " + currentIntrigue.orgaReferent)

    #gestion de la section à faire
    currentIntrigue.questions_ouvertes = ''.join(texteIntrigue[indexDebutTodo:indexFinTodo].splitlines()[1:])

    #gestion de la section Résumé
    currentIntrigue.pitch = ''.join(texteIntrigue[indexDebutResume:indexFinResume].splitlines(keepends=True)[1:])
    # print("section pitch trouvée : " + section)
    # print("pitch isolé after découpage : " + ''.join(section.splitlines(keepends=True)[1:]))
    # print("pitch lu dans l'intrigue après mise à jour : " + currentIntrigue.pitch)

    #gestion de la section PJ
    pjs = texteIntrigue[indexDebutPjs:indexFinPjs].split("#####")
    for pj in pjs[1:]: #on commence en 1 pour éviter de prendre la première ligne
        # print("taille du prochain PJ : " +str(len(pj)))
        if len(pj) < 14: # dans ce cas c'est qu'un a une ligne du tableau vide
            # print("pas assez de caractères je me suis arrêté")
            continue #il y a de fortes chances que le PJ ne contienne que des renvois à la ligne
        sections = pj.split("###")
        # print("j'ai trouvé " + str(len(sections)) + " sections")

        if len(sections) < 4:
            continue
        # print("perso découpé avant ajout : " + str(sections))
        nomNormalise = process.extractOne(str(sections[0]).strip(), nomspersos)
        # print("nom normalisé pour " + str(sections[0].strip()) + " : " + nomNormalise[0] + " - " + str(nomNormalise[1]))
        if nomNormalise[1] < 70:
            print("WARNING : indice de confiance faible ({0}) pour l'association du personnage {1}, trouvé dans le "
                  "tableau, avec le personnage {2} dans l'intrigue {3}".format(nomNormalise[1],str(sections[0]).strip(), nomNormalise[0], nomIntrigue))

        pjAAjouter = Role(currentIntrigue, nom=sections[0].strip())
        pjAAjouter.description = sections[3].strip()
        pjAAjouter.typeIntrigue = sections[2].strip()
        pjAAjouter.niveauImplication = sections[1].strip()
        check = currentIntrigue.associerRoleAPerso(pjAAjouter, monGN.personnages[nomNormalise[0]])

        if check == 0: #dans ce cas, ce personnage n'était pas déjà associé à un rôle dans l'intrigue
            currentIntrigue.roles[pjAAjouter.nom] = pjAAjouter
        else:
            print("Erreur : impossible d'associer le personnage {0} au rôle {1} dans l'intrigue {2} : il est déjà "
                  "associé à un rôle".format(nomNormalise[0], roleAAssocier.nom, currentIntrigue))
            # print("taille du nombre de roles dans l'intrigue {0}".format(len(currentIntrigue.roles)))
        # print("check pour {0} = {1}".format(pjAAjouter.nom, check))


    #gestion de la section PNJs
    #todo : gérer la section PNJ

    #à ce stade là on a et les PJs et les PNJs > on peut générer le tableau de reférence des noms dans l'intrigue
    nomsRoles = currentIntrigue.getNomsRoles()

    # gestion de la section Rerolls
    # todo : rerolls

    # gestion de la section Objets
    # todo : objets
    # todo dans la gestion des objets faire la difference entre les objets à 3 et 4 colonnes (avec ou sans RFID)

    # gestion de la section FX
    # todo : FX et scenes en jeu

    # gestion de la section Timeline
    # todo : timeline

    # gestion de la section Scènes
    scenes = texteIntrigue[indexDebutScenes + len(labelScenes):indexFinScenes].split("###")

    for scene in scenes:
        # print("taille de la scène : " + str(len(scene)))
        if len(scene) < 10:
            continue

        titreScene = scene.splitlines()[0].strip()
        sceneAAjouter = currentIntrigue.addScene(titreScene)
        # print("titre de la scène ajoutée : " + sceneAAjouter.titre)

        balises = re.findall(r'##.*', scene)
        for balise in balises:
            # print("balise : " + balise)
            if balise[0:9].lower() == '## quand?':
                extraireDateScene(balise[10:], sceneAAjouter)
            elif balise[0:10].lower() == '## quand ?':
                extraireDateScene(balise[11:], sceneAAjouter)
                # sceneAAjouter.date = balise[11:].strip()
                # # print("date de la scène : " + sceneAAjouter.date)
            elif balise[0:9].lower() == '## il y a':
                extraireIlYAScene(balise[10:], sceneAAjouter)
            elif balise[0:7].lower() == '## qui?':
                extraireQuiScene(balise[8:], currentIntrigue, nomsRoles, sceneAAjouter)

            elif balise[0:8].lower() == '## qui ?':
                extraireQuiScene(balise[9:], currentIntrigue, nomsRoles, sceneAAjouter)

            elif balise[0:11].lower() == '## niveau :':
                        sceneAAjouter.niveau = balise[12:].strip()

            elif balise[0:11].lower() == '## resumé :':
                sceneAAjouter.resume = balise[12:].strip()

            else:
                print("balise inconnue : " + balise + " dans l'intrigue " + nomIntrigue)

        sceneAAjouter.description = ''.join(scene.splitlines(keepends=True)[1 + len(balises):])
        # print("texte de la scene apres insertion : " + sceneAAjouter.description)

    # gestion de la section Résolution
    currentIntrigue.resolution = ''.join(texteIntrigue[indexdebutResolution:indexFinResolution].splitlines()[1:])

    # gestion de la section notes
    currentIntrigue.notes = ''.join(texteIntrigue[indexDebutNotes:indexFinNotes].splitlines()[1:])

    # print("liste des persos : ")
    # for role in currentIntrigue.roles:
    #     print(role)

    return currentIntrigue


def extraireQuiScene(listeNoms, currentIntrigue, nomsRoles, sceneAAjouter):
    roles = listeNoms.split(",")
    # print("rôles trouvés en lecture brute : " + str(roles))

    #dans ce cas, on prend les noms du tableau, qui fon fois, et on s'en sert pour identifier
    # les noms de la scène
    for nomRole in roles:
        #pour chaque nom de la liste : retrouver le nom le plus proche dans la liste des noms du GN
        nomNormalise = process.extractOne(nomRole.strip(), nomsRoles)
        # print("nom normalisé du personnage {0} trouvé dans une scène de {1} : {2}".format(nomRole.strip(), currentIntrigue.nom, nomNormalise))

        #si on a trouvé quelqu'un MAIs qu'on est <80% >> afficher un warning : on s'tes peut etre trompé de perso
        if nomNormalise is not None and nomNormalise[1] < 80:
            print("Warning, lors de l'association des rôles dans la scene {0}, problème avec le nom "
                  "déclaré {1} : indice de correspondance : {2}".format(sceneAAjouter.titre, nomRole, nomNormalise))

        #trouver le rôle à ajouter à la scène en lisant l'intrigue
        monRole = currentIntrigue.roles[nomNormalise[0]]

        monRole.ajouterAScene(sceneAAjouter)


def reconstruireTableauRolesFromScenes(texteSectionScenes, listeNoms):
    #extraire toutes les balises "qui"
    #standardiser les noms trouvés et les concaténer
    #supprimer les doublons
    #todo : reconstruire les noms des tableaux d'intrigue

def extraireDateScene(baliseDate, sceneAAjouter):
    sceneAAjouter.date = baliseDate.strip()
    # print("date de la scène : " + sceneAAjouter.date)

def extraireIlYAScene(baliseDate, sceneAAjouter):
    #trouver s'il y a un nombres* a[ns]
    ans = re.search(r"\d*\s*[a]", baliseDate).group(0)[:-1]  #enlever le dernier char car c'est le marqueur de temps
    #trouver s'il y a un nombres* m[ois]
    mois = re.search('\d*\s*[m]', baliseDate).group(0)[:-1]
    #trouver s'il y a un nombres* j[ours]
    jours = re.search('\d*\s*[j]', baliseDate).group(0)[:-1]
    sceneAAjouter.date = -1 * (float(ans) * 365 + float(mois) * 30.5 + float(jours))

    pass


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
                    text += read_structural_elements(cell.get('content')) + "###"
                text += "##"
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_structural_elements(toc.get('content'))
    return text


if __name__ == '__main__':
    main()