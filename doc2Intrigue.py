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

folderid = "1toM693dBuKl8OPMDmCkDix0z6xX9syjA"  # le folder des intrigues de Chalacta


def extraireIntrigues(monGN, singletest="-01"):
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
            pageSize=100, q="'1toM693dBuKl8OPMDmCkDix0z6xX9syjA' in parents",
            fields="nextPageToken, files(id, name, modifiedTime)").execute()
        items = results.get('files',
                            [])  # le q = trucs est l'identifiant du dossier drive qui contient toutes les intrigues

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
                    # print("... n'est pas une intrigue")
                    continue

                # print("... est une intrigue !")

                # si contient "-01" fera toutes les intrigues, sinon seule celle qui est spécifiée
                if int(singletest) > 0:
                    # Alors on se demandne si c'est la bonne
                    if document.get('title')[0:2] != str(singletest):  # numéro de l'intrigue
                        # si ce n'est pas la bonne, pas la peine d'aller plus loin
                        continue
                    else:
                        print("intrigue {0} trouvée".format(singletest))

                # du coup on traite

                # on vérifie d'abord s'il est nécessaire de traiter (dernière maj intrigue > derniere maj objet) :
                #   SI l'intrigue existe dans le GN ?
                if item['id'] in monGN.intrigues.keys():
                    #       SI la date de mise à jour du fichier n'est pas postérieure à la date de MAJ de l'intrigue
                    # print("l'intrigue fait déjà partie du GN ! ")
                    print(f"Variable / type : monGN.intrigues[item['id']].lastChange / {type(monGN.intrigues[item['id']].lastChange)} / {monGN.intrigues[item['id']].lastChange}")
                    print(f"Variable / type : item['modifiedTime'] / {type(item['modifiedTime'])} / {item['modifiedTime']}")
                    if monGN.intrigues[item['id']].lastChange >= datetime.datetime.strptime(item['modifiedTime'][:-5], '%Y-%m-%dT%H:%M:%S'):
                        print ("et elle n'a pas changé depuis le dernier passage")
                        # ALORS : Si c'est la même que la plus vielle mise à jour : on arrête
                        #si c'était la plus vieille du GN, pas la peine de continuer
                        if monGN.idOldestUpdate == item['id']:
                            print("et d'ailleurs c'était la plus vieille > j'ai fini !")
                            break
                        else:
                            #sinon on passe à l'intrigue suivante (sauf si on est dans singletest)
                            if int(singletest) > 0:
                                print("stop !")
                                # alors si on est toujours là, c'est que c'était notre intrigue
                                # pas la peine d'aller plus loin
                                return
                            continue
                    else:
                        print("elle a changé depuis mon dernier passage : supprimons-la !")
                        #dans ce cas il faut la supprimer car on va tout réécrire
                        monGN.intrigues[item['id']].clear()
                        del monGN.intrigues[item['id']]

                print("et du coup, il est est temps de créer un nouveau fichier")
                # à ce stade, soit on sait qu'elle n'existait pas, soit on l'a effacée pour la réécrire
                contenuDocument = document.get('body').get('content')
                text = read_structural_elements(contenuDocument)

                # print(text) #test de la fonction récursive pour le texte
                monIntrigue = extraireIntrigueDeTexte(text, document.get('title'), item["id"], monGN)
                # monIntrigue.url = item["id"]

                # et on enregistre la date de dernière mise à jour de l'intrigue
                monIntrigue.lastChange = datetime.datetime.now()

                # print(f'url intrigue = {monIntrigue.url}')
                # print(f"intrigue {monIntrigue.nom}, date de modification : {item['modifiedTime']}")

                if int(singletest) > 0:
                    print("stop !")
                    # alors si on est toujours là, c'est que c'était notre intrigue
                    # pas la peine d'aller plus loin
                    return
                print("here we go again")

                # return #ajouté pour débugger
            except HttpError as err:
                print(err)
                # return #ajouté pour débugger
    except HttpError as error:
        print(f'An error occurred: {error}')


def extraireIntrigueDeTexte(texteIntrigue, nomIntrigue, idUrl, monGN):

    # print("texte intrigue en entrée : ")
    # print(texteIntrigue)
    # print("*****************************")
    currentIntrigue = Intrigue(nom=nomIntrigue, url=idUrl)
    monGN.intrigues[idUrl] = currentIntrigue
    nomspersos = monGN.getNomsPersos()

    texteIntrigueLow = texteIntrigue.lower()  # on passe en minuscule pour mieux trouver les chaines

    # on fait un dict du début de chaque label
    REFERENT = "orga référent"
    TODO = "etat de l’intrigue"
    PITCH = "résumé de l’intrigue"
    PJS = "personnages impliqués"
    PNJS = "pnjs impliqués"
    REROLLS = "rerolls possibles"
    OBJETS = "objets liés"
    SCENESFX = "scènes nécessaires et fx"
    TIMELINE = "chronologie des événements"
    SCENES = "détail de l’intrigue"
    RESOLUTION = "résolution de l’intrigue"
    NOTES = "notes supplémentaires"

    labels = [REFERENT, TODO, PITCH, PJS, PNJS, REROLLS, OBJETS, SCENESFX,
              TIMELINE, SCENES, RESOLUTION, NOTES]

    indexes = dict()
    for label in labels:
        indexes[label] = {"debut": texteIntrigueLow.find(label)}
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
            tableDebutsFinsLabels[tousLesIndexes[i]] = len(texteIntrigueLow)
            break

    # enfin on met à jour la table des labels pour avoir la fin à côté du début
    for label in labels:
        indexes[label]["fin"] = tableDebutsFinsLabels[indexes[label]["debut"]]
        # print("label {0} : [{1}:{2}]".format(label, indexes[label]["debut"], indexes[label]["fin"]))

    # gestion de la section OrgaRéférent
    if indexes[REFERENT]["debut"] == -1:
        print("problème référent avec l'intrigue " + nomIntrigue)
    else:
        currentIntrigue.orgaReferent = texteIntrigue[indexes[REFERENT]["debut"]:indexes[REFERENT]["fin"]].splitlines()[
                                           0][
                                       len(REFERENT) + len(" : "):]
        # prendre la première ligne puis les caractères à partir du label
        # print("debut / fin orga référent : {0}/{1} pour {2}".format(indexDebutReferent, indexFinReferent, nomIntrigue))
        # print("Orga référent : " + currentIntrigue.orgaReferent)

    # gestion de la section à faire
    currentIntrigue.questions_ouvertes = ''.join(
        texteIntrigue[indexes[TODO]["debut"]:indexes[TODO]["fin"]].splitlines()[1:])

    # gestion de la section Résumé
    currentIntrigue.pitch = ''.join(
        texteIntrigue[indexes[PITCH]["debut"]:indexes[PITCH]["fin"]].splitlines(keepends=True)[1:])
    # print("section pitch trouvée : " + section)
    # print("pitch isolé after découpage : " + ''.join(section.splitlines(keepends=True)[1:]))
    # print("pitch lu dans l'intrigue après mise à jour : " + currentIntrigue.pitch)

    # gestion de la section PJ
    pjs = texteIntrigue[indexes[PJS]["debut"]:indexes[PJS]["fin"]].split("#####")
    for pj in pjs[1:]:  # on commence en 1 pour éviter de prendre la première ligne
        # print("taille du prochain PJ : " +str(len(pj)))
        if len(pj) < 14:  # dans ce cas c'est qu'un a une ligne du tableau vide
            # print("pas assez de caractères je me suis arrêté")
            continue  # il y a de fortes chances que le PJ ne contienne que des renvois à la ligne
        sections = pj.split("###")
        # print("j'ai trouvé " + str(len(sections)) + " sections")

        if len(sections) < 4:
            continue
        # print("perso découpé avant ajout : " + str(sections))
        nomNormalise = process.extractOne(str(sections[0]).strip(), nomspersos)
        # print("nom normalisé pour " + str(sections[0].strip()) + " : " + nomNormalise[0] + " - " + str(nomNormalise[1]))
        if nomNormalise[1] < 70:
            print("WARNING : indice de confiance faible ({0}) pour l'association du personnage {1}, trouvé dans le "
                  "tableau, avec le personnage {2} dans l'intrigue {3}".format(nomNormalise[1],
                                                                               str(sections[0]).strip(),
                                                                               nomNormalise[0], nomIntrigue))

        pjAAjouter = Role(currentIntrigue, nom=sections[0].strip())
        pjAAjouter.description = sections[3].strip()
        pjAAjouter.typeIntrigue = sections[2].strip()
        pjAAjouter.niveauImplication = sections[1].strip()
        check = currentIntrigue.associerRoleAPerso(pjAAjouter, monGN.personnages[nomNormalise[0]])

        if check == 0:  # dans ce cas, ce personnage n'était pas déjà associé à un rôle dans l'intrigue
            currentIntrigue.roles[pjAAjouter.nom] = pjAAjouter
        else:
            print("Erreur : impossible d'associer le personnage {0} au rôle {1} dans l'intrigue {2} : il est déjà "
                  "associé à un rôle".format(nomNormalise[0], sections[0].strip(), currentIntrigue))
            # print("taille du nombre de roles dans l'intrigue {0}".format(len(currentIntrigue.roles)))
        # print("check pour {0} = {1}".format(pjAAjouter.nom, check))

    # gestion de la section PNJs
    if indexes[PNJS]["debut"] > -1:
        pnjs = texteIntrigue[indexes[PNJS]["debut"]:indexes[PNJS]["fin"]].split('#####')
        # faire un tableau avec une ligne par PNJ
        for pnj in pnjs[1:]:  # on enlève la première ligne qui contient les titres
            if len(pnj) < 14:
                # dans ce cas c'est une ligne vide
                continue
            sections = pnj.split("###")
            # 0 Nom duPNJ et / ou fonction:
            # 1 Intervention:(Permanente ou Temporaire)
            # 2 Type d’implication: (Active, Passive, Info,ou Objet)
            # 3 Résumé de l’implication
            pnjAAjouter = Role(currentIntrigue, nom=sections[0].strip(), niveauImplication=sections[2].strip(),
                               description=sections[3].strip(), pj=modeleGN.EST_PNJ_HORS_JEU)

            # print("Je suis en train de regarder {0} et son implication est {1}".format(pnjAAjouter.nom, sections[1].strip()))

            # cherche ensuite le niveau d'implication du pj
            if sections[1].strip().lower().find('perman') > -1:
                # print(pnjAAjouter.nom + " est permanent !!")
                pnjAAjouter.pj = modeleGN.EST_PNJ_PERMANENT
            elif sections[1].strip().lower().find('temp') > -1:
                pnjAAjouter.pj = modeleGN.EST_PNJ_TEMPORAIRE
                # print(pnjAAjouter.nom + " est temporaire !!")
            elif sections[1].strip().lower().find('infiltr') > -1:
                pnjAAjouter.pj = modeleGN.EST_PNJ_INFILTRE
                # print(pnjAAjouter.nom + " est temporaire !!")

            # sinon PNJ hors jeu est la valeur par défaut : ne rien faire

            # du coup on peut l'ajouter aux intrigues
            currentIntrigue.roles[pnjAAjouter.nom] = pnjAAjouter

    # à ce stade là on a et les PJs et les PNJs > on peut générer le tableau de reférence des noms dans l'intrigue
    nomsRoles = currentIntrigue.getNomsRoles()

    # gestion de la section Rerolls
    if indexes[REROLLS]["debut"] > -1:
        rerolls = texteIntrigue[indexes[REROLLS]["debut"]:indexes[REROLLS]["fin"]].split('#####')
        # faire un tableau avec une ligne par Reroll
        for reroll in rerolls[1:]:  # on enlève la première ligne qui contient les titres
            if len(reroll) < 14:
                # dans ce cas c'est une ligne vide
                continue
            sections = reroll.split("###")
            # même sections que les PJs
            reRollAAjouter = Role(currentIntrigue, nom=sections[0].strip(), description=sections[3].strip(),
                                  niveauImplication=sections[1].strip(), typeIntrigue=sections[2].strip(),
                                  pj=modeleGN.EST_REROLL)

            # du coup on peut l'ajouter aux intrigues
            currentIntrigue.roles[reRollAAjouter.nom] = reRollAAjouter

    # gestion de la section Objets
    # todo : objets
    #   dans la gestion des objets faire la difference entre les objets à 3 et 4 colonnes (avec ou sans RFID)

    # gestion de la section FX
    if indexes[SCENESFX]["debut"] > -1:
        currentIntrigue.scenesEnJeu = ''.join(
            texteIntrigue[indexes[SCENESFX]["debut"]:indexes[SCENESFX]["fin"]].splitlines()[1:])

    # gestion de la section Timeline
    if indexes[TIMELINE]["debut"] > -1:
        currentIntrigue.timeline = ''.join(
            texteIntrigue[indexes[TIMELINE]["debut"]:indexes[TIMELINE]["fin"]].splitlines()[1:])

    # gestion de la section Scènes
    if indexes[SCENES]["debut"] > -1:
        scenes = texteIntrigue[indexes[SCENES]["debut"] + len(SCENES):indexes[SCENES]["fin"]].split("###")

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
    if indexes[RESOLUTION]["debut"] > -1:
        currentIntrigue.resolution = ''.join(
            texteIntrigue[indexes[RESOLUTION]["debut"]:indexes[RESOLUTION]["fin"]].splitlines()[1:])

    # gestion de la section notes
    # print("debut/fin notes : {0}/{1}".format(indexes[NOTES]["debut"], indexes[NOTES]["fin"]))
    if indexes[NOTES]["debut"] > -1:
        currentIntrigue.notes = ''.join(texteIntrigue[indexes[NOTES]["debut"]:indexes[NOTES]["fin"]].splitlines()[1:])

    # print("liste des persos : ")
    # for role in currentIntrigue.roles:
    #     print(role)

    return currentIntrigue


def extraireQuiScene(listeNoms, currentIntrigue, nomsRoles, sceneAAjouter):
    roles = listeNoms.split(",")
    # print("rôles trouvés en lecture brute : " + str(roles))

    # dans ce cas, on prend les noms du tableau, qui fon fois, et on s'en sert pour identifier
    # les noms de la scène
    for nomRole in roles:
        # pour chaque nom de la liste : retrouver le nom le plus proche dans la liste des noms du GN
        nomNormalise = process.extractOne(nomRole.strip(), nomsRoles)
        # print("nom normalisé du personnage {0} trouvé dans une scène de {1} : {2}".format(nomRole.strip(), currentIntrigue.nom, nomNormalise))

        # si on a trouvé quelqu'un MAIs qu'on est <80% >> afficher un warning : on s'tes peut etre trompé de perso
        if nomNormalise is not None and nomNormalise[1] < 80:
            print("Warning, lors de l'association des rôles dans la scene {0}, problème avec le nom "
                  "déclaré {1} : indice de correspondance : {2}".format(sceneAAjouter.titre, nomRole, nomNormalise))

        # trouver le rôle à ajouter à la scène en lisant l'intrigue
        # warning: un truc plante parfois ici mais je ne sais pas encore quoi ni pourquoi (process renvoie None)
        monRole = currentIntrigue.roles[nomNormalise[0]]

        monRole.ajouterAScene(sceneAAjouter)


def extraireDateScene(baliseDate, sceneAAjouter):
    sceneAAjouter.date = baliseDate.strip()
    # print("date de la scène : " + sceneAAjouter.date)


def extraireIlYAScene(baliseDate, sceneAAjouter):
    # print("balise date : " + baliseDate)
    # trouver s'il y a un nombres* a[ns]
    ans = re.search(r"\d*\s*a", baliseDate)
    if ans is None:
        ans = 0
    else:
        ans = ans.group(0)[:-1]  # enlever le dernier char car c'est le marqueur de temps

    # trouver s'il y a un nombres* m[ois]
    mois = re.search('\d*\s*m', baliseDate)
    if mois is None:
        mois = 0
    else:
        mois = mois.group(0)[:-1]

    # trouver s'il y a un nombres* j[ours]
    jours = re.search('\d*\s*j', baliseDate)
    if jours is None:
        jours = 0
    else:
        jours = jours.group(0)[:-1]

    sceneAAjouter.date = -1 * (float(ans) * 365 + float(mois) * 30.5 + float(jours))


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
