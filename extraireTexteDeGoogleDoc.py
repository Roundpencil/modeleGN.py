from __future__ import print_function

import re

import fuzzywuzzy.process
from fuzzywuzzy import process
from googleapiclient.errors import HttpError

import lecteurGoogle
import modeleGN
from modeleGN import *


def extraire_intrigues(monGN, apiDrive, apiDoc, singletest="-01", verbal=False, fast=True):
    extraireTexteDeGoogleDoc(monGN, apiDrive, apiDoc, extraireIntrigueDeTexte, monGN.intrigues, monGN.folderIntriguesID,
                             singletest, verbal=verbal, fast=fast)


def extraire_pjs(monGN, apiDrive, apiDoc, singletest="-01", verbal=False, fast=True):
    extraireTexteDeGoogleDoc(monGN, apiDrive, apiDoc, extrairePJDeTexte, monGN.dictPJs, monGN.folderPJID, singletest,
                             verbal=verbal, fast=fast)


def extraireTexteDeGoogleDoc(monGN, apiDrive, apiDoc, fonctionExtraction, dictIDs: dict, folderArray,
                             singletest="-01", verbal=False, fast=True):
    items = lecteurGoogle.genererListeItems(monGN, apiDrive=apiDrive, folderID=folderArray)

    if not items:
        print('No files found.')
        return

    # print(f"singletest : {type(singletest)} = {singletest}")
    if int(singletest) > 0:
        for item in items:
            try:
                # print ("poung")

                # print ("ping")
                # Retrieve the documents contents from the Docs api_doc.
                document = apiDoc.documents().get(documentId=item['id']).execute()

                print('Titre document : {}'.format(document.get('title')))

                # Alors on se demande si c'est le bon doc
                # if document.get('title')[0:3].strip() != str(singletest):  # numéro de l'intrigue
                #     # si ce n'est pas la bonne, pas la peine d'aller plus loin
                #     continue
                if ref_du_doc(document.get('title')) != int(singletest):
                    continue
                else:
                    print(f"j'ai trouvé le doc #{singletest} : {document.get('title')}")
                    # if item['id'] in mon_gn.intrigues.keys():
                    #     mon_gn.intrigues[item['id']].clear()
                    #     del mon_gn.intrigues[item['id']]

                    objet_de_reference = None
                    if item['id'] in dictIDs.keys():
                        dictIDs[item['id']].clear()
                        objet_de_reference = dictIDs.pop(item['id'])

                    nouvelObjet = extraireObjetsDeDocument(document, item, monGN, fonctionExtraction,
                                                           saveLastChange=False, verbal=verbal)
                    if objet_de_reference is not None:
                        nouvelObjet.updater_dates_maj_scenes(objet_de_reference)

                    break
                    # on a trouvé le bon doc, on arrête de chercher
            except HttpError as err:
                print(f'An error occurred: {err}')
                # return #ajouté pour débugger

    else:
        # dans ce cas, on lit tout, jusqu'à ce qu'on tombe sur une entrée qui n'a pas été modifiée
        for item in items:
            try:
                # print ("poung")

                # print ("ping")
                # Retrieve the documents contents from the Docs api_doc.
                document = apiDoc.documents().get(documentId=item['id']).execute()

                print('Titre document : {}'.format(document.get('title')))
                # print(document.get('title')[0:2])

                # if not document.get('title')[0:2].isdigit():
                #     # print("... n'est pas une intrigue")
                #     continue
                if ref_du_doc(document.get('title')) == -1:
                    continue

                # print("... est une intrigue !")

                objet_de_reference = None

                # on vérifie d'abord s'il est nécessaire de traiter (dernière maj intrigue > derniere maj objet) :
                #   SI l'intrigue existe dans le GN ?
                # if item['id'] in mon_gn.intrigues .keys():
                if item['id'] in dictIDs.keys():

                    #       SI la date de mise à jour du fichier n'est pas postérieure à la date de MAJ de l'intrigue
                    # print("l'intrigue fait déjà partie du GN ! ")
                    # print(f"Variable / type : mon_gn.intrigues[item['id']].lastChange / {type(mon_gn.intrigues[item['id']].lastChange)} / {mon_gn.intrigues[item['id']].lastChange}")
                    # print(f"Variable / type : item['modifiedTime'] / {type(item['modifiedTime'])} / {item['modifiedTime']}")

                    # on enlève les 5 derniers chars qui sont un point, les millisecondes et Z, pour formatter
                    # if mon_gn.intrigues[item['id']].lastChange >= datetime.datetime.strptime(item['modifiedTime'][:-5],
                    #                                                                         '%Y-%m-%dT%H:%M:%S'):
                    # if dictIDs[item['id']].lastProcessing >= item['modifiedTime']:
                    if fast and \
                            dictIDs[item['id']].lastProcessing >= datetime.datetime.strptime(
                        item['modifiedTime'][:-5],
                        '%Y-%m-%dT%H:%M:%S'):

                        print(
                            f"et elle n'a pas changé (dernier changement : {datetime.datetime.strptime(item['modifiedTime'][:-5], '%Y-%m-%dT%H:%M:%S')}) depuis le dernier passage ({dictIDs[item['id']].lastProcessing})")
                        # ALORS : Si c'est la même que la plus vielle mise à jour : on arrête
                        # si c'était la plus vieille du GN, pas la peine de continuer

                        break
                        # on a trouvé une intrigue qui n'a pas bougé :
                        # toutes les suivantes qu'il nous remontera seront plus anciennes
                        # donc on arrête de parcourir
                    else:
                        # print("elle a changé depuis mon dernier passage : supprimons-la !")
                        # dans ce cas, il faut la supprimer, car on va tout réécrire
                        # mon_gn.intrigues[item['id']].clear()
                        # del mon_gn.intrigues[item['id']]

                        objet_de_reference = dictIDs.pop(item['id'])

                # puis, dans tous les cas, on la crée
                nouvelObjet = extraireObjetsDeDocument(document, item, monGN, fonctionExtraction, verbal=verbal)
                if objet_de_reference is not None:
                    nouvelObjet.updater_dates_maj_scenes(objet_de_reference)
                    objet_de_reference.clear()

            except HttpError as err:
                print(f'An error occurred: {err}')
                # return #ajouté pour débugger


def extraireObjetsDeDocument(document, item, monGN, fonctionExtraction, saveLastChange=True, verbal=False):
    # print("et du coup, il est temps de créer un nouveau fichier")
    # à ce stade, soit on sait qu'elle n'existait pas, soit on l'a effacée pour la réécrire
    contenuDocument = document.get('body').get('content')
    text = lecteurGoogle.read_structural_elements(contenuDocument)
    text = text.replace('\v', '\n')  # pour nettoyer les backspace verticaux qui se glissent

    # print(text) #test de la fonction récursive pour le texte
    # monObjet = extraireIntrigueDeTexte(text, document.get('title'), item["id"], mon_gn)
    lastFileEdit = datetime.datetime.strptime(
        item['modifiedTime'][:-5],
        '%Y-%m-%dT%H:%M:%S')
    print(f"clef présentes : {item['lastModifyingUser'].keys()}")
    try:
        derniere_modification_par = item['lastModifyingUser']['emailAddress']
    except:
        derniere_modification_par = "Utilisateur inconnu"

    monObjet = fonctionExtraction(text, document.get('title'), item["id"], lastFileEdit, derniere_modification_par,
                                  monGN, verbal)
    # monObjet.url = item["id"]
    # et on enregistre la date de dernière mise à jour de l'intrigue

    if monObjet is not None and saveLastChange:
        monObjet.lastProcessing = datetime.datetime.now()
    # print(f'url intrigue = {monObjet.url}')
    # print(f"intrigue {monObjet.nom}, date de modification : {item['modifiedTime']}")
    return monObjet


def extraireIntrigueDeTexte(texteIntrigue, nomIntrigue, idUrl, lastFileEdit, derniere_modification_par, monGN,
                            verbal=False):
    # print("texte intrigue en entrée : ")
    # print(texteIntrigue.replace('\v', '\n'))
    # texteIntrigue = texteIntrigue.replace('\v', '\n')
    # print("*****************************")
    currentIntrigue = Intrigue(nom=nomIntrigue, url=idUrl, derniere_edition_fichier=lastFileEdit)
    currentIntrigue.modifie_par = derniere_modification_par
    monGN.intrigues[idUrl] = currentIntrigue
    # noms_persos = mon_gn.noms_pjs()

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

    indexes = lecteurGoogle.identifierSectionsFiche(labels, texteIntrigue)

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
    if indexes[TODO]["debut"] == -1:
        print("problème état de l'intrigue avec l'intrigue " + nomIntrigue)
    else:
        # currentIntrigue.questions_ouvertes = ''.join(
        #     texteIntrigue[indexes[TODO]["debut"]:indexes[TODO]["fin"]].splitlines()[1:])
        currentIntrigue.questions_ouvertes = texteIntrigue[indexes[TODO]["debut"] + len(TODO):indexes[TODO]["fin"]]

    # gestion de la section Résumé
    currentIntrigue.pitch = ''.join(
        texteIntrigue[indexes[PITCH]["debut"]:indexes[PITCH]["fin"]].splitlines(keepends=True)[1:])
    # print("section pitch trouvée : " + section)
    # print("pitch isolé after découpage : " + ''.join(section.splitlines(keepends=True)[1:]))
    # print("pitch lu dans l'intrigue après mise à jour : " + currentIntrigue.pitch)

    # gestion de la section PJ
    pjs = texteIntrigue[indexes[PJS]["debut"]:indexes[PJS]["fin"]].split("¤¤¤¤¤")
    for pj in pjs[1:]:  # on commence en 1 pour éviter de prendre la première ligne
        # print("taille du prochain PJ : " +str(len(pj)))
        if len(pj) < 14:  # dans ce cas, c'est qu'un a une ligne du tableau vide
            # print("pas assez de caractères je me suis arrêté")
            continue  # il y a de fortes chances que le PJ ne contienne que des renvois à la ligne
        sections = pj.split("¤¤¤")
        # print("j'ai trouvé " + str(len(sections)) + " sections")

        if len(sections) < 4:  # testé pour éviter de se taper les lignes vides après le tableau
            continue

        # déplacé dans l'objet GN à faire tourner en fin de traitement, notamment si changement des Persos depuis le
        # dernier run
        # print("perso découpé avant ajout : " + str(sections)) nomNormalise = process.extractOne(str(
        # sections[0]).strip(), noms_persos) # print("nom normalisé pour " + str(sections[0].strip()) + " : " +
        # nomNormalise[0] + " - " + str(nomNormalise[1])) if nomNormalise[1] < 70: print("WARNING : indice de
        # confiance faible ({0}) pour l'association du personnage {1}, trouvé dans le " "tableau, avec le personnage
        # {2} dans l'intrigue {3}".format(nomNormalise[1], str(sections[0]).strip(), nomNormalise[0], nomIntrigue))

        roleAAjouter = Role(currentIntrigue,
                            nom=sections[0].split("http")[0].strip(),
                            description=sections[3].strip(),
                            typeIntrigue=sections[2].strip(),
                            niveauImplication=sections[1].strip()
                            )
        currentIntrigue.rolesContenus[roleAAjouter.nom] = roleAAjouter

    # gestion de la section PNJs
    if indexes[PNJS]["debut"] > -1:
        # print(f'bloc PNJs = {texteIntrigue[indexes[PNJS]["debut"]:indexes[PNJS]["fin"]]}')
        # print(f"dans l'intrigue {currentIntrigue.nom}")

        pnjs = texteIntrigue[indexes[PNJS]["debut"]:indexes[PNJS]["fin"]].split('¤¤¤¤¤')
        # faire un tableau avec une ligne par PNJ
        for pnj in pnjs[1:]:  # on enlève la première ligne qui contient les titres
            # print(f"section pnj en cours de lecture : {pnj}")
            # print(f"taille = {len(pnj)}")
            if len(pnj) < 14:
                # dans ce cas, c'est une ligne vide
                # print(f"pnj {pnj}  est vide")
                continue
            sections = pnj.split("¤¤¤")
            # 0 Nom duPNJ et / ou fonction :
            # 1 Intervention:(Permanente ou Temporaire)
            # 2 Type d’implication: (Active, Passive, Info, ou Objet)
            # 3 Résumé de l’implication
            pnjAAjouter = Role(currentIntrigue, nom=sections[0].strip(), description=sections[3].strip(),
                               pj=modeleGN.EST_PNJ_HORS_JEU, niveauImplication=sections[2].strip(),
                               perimetreIntervention=sections[1].strip())

            # print("Je suis en train de regarder {0} et son implication est {1}".format(pnjAAjouter.nom, sections[1].strip()))

            # cherche ensuite le niveau d'implication du pj
            if sections[1].strip().lower().find('perman') > -1:
                # print(pnjAAjouter.nom + " est permanent !!")
                pnjAAjouter.pj = modeleGN.EST_PNJ_PERMANENT
            elif sections[1].strip().lower().find('infiltr') > -1:
                pnjAAjouter.pj = modeleGN.EST_PNJ_INFILTRE
                # print(pnjAAjouter.nom + " est temporaire !!")
            # elif sections[1].strip().lower().find('temp') > -1:
            #     pnjAAjouter.pj = modeleGN.EST_PNJ_TEMPORAIRE
            #     # print(pnjAAjouter.nom + " est temporaire !!")
            elif len(sections[1].strip()) > 1:
                pnjAAjouter.pj = modeleGN.EST_PNJ_TEMPORAIRE
                # print(pnjAAjouter.nom + " est temporaire !!")

            # sinon PNJ hors-jeu est la valeur par défaut : ne rien faire

            # du coup, on peut l'ajouter aux intrigues
            currentIntrigue.rolesContenus[pnjAAjouter.nom] = pnjAAjouter

    # gestion de la section Rerolls
    if indexes[REROLLS]["debut"] > -1:
        rerolls = texteIntrigue[indexes[REROLLS]["debut"]:indexes[REROLLS]["fin"]].split('¤¤¤¤¤')
        # faire un tableau avec une ligne par Reroll
        for reroll in rerolls[1:]:  # on enlève la première ligne qui contient les titres
            if len(reroll) < 14:
                # dans ce cas, c'est une ligne vide
                continue
            sections = reroll.split("¤¤¤")
            # même sections que les PJs
            reRollAAjouter = Role(currentIntrigue, nom=sections[0].strip(), description=sections[3].strip(),
                                  pj=modeleGN.EST_REROLL, typeIntrigue=sections[2].strip(),
                                  niveauImplication=sections[1].strip())

            # du coup, on peut l'ajouter aux intrigues
            currentIntrigue.rolesContenus[reRollAAjouter.nom] = reRollAAjouter

    # gestion de la section Objets
    if indexes[OBJETS]["debut"] > -1:
        objets = texteIntrigue[indexes[OBJETS]["debut"]:indexes[OBJETS]["fin"]].split('¤¤¤¤¤')
        # faire un tableau avec une ligne par objet
        for objet in objets[1:]:  # on enlève la première ligne qui contient les titres
            if len(objet) < 14:
                # dans ce cas, c'est une ligne vide
                continue
            sections = objet.split("¤¤¤")
            # vérifier si nous sommes avec un objet RFID (4 colonnes) ou sans (3 colonnes)
            monObjet = None
            if len(sections) == 4:
                monObjet = Objet(description=sections[0].strip(), emplacementDebut=sections[2].strip(),
                                 fourniPar=sections[3].strip())
                if sections[3].strip().lower() != "non":  # si on a mis non pour le RFID ca ne veut pas dire oui :)
                    monObjet.specialEffect = sections[3].strip()

            elif len(sections) == 3:
                monObjet = Objet(description=sections[0].strip(), emplacementDebut=sections[1].strip(),
                                 fourniPar=sections[2].strip())
            else:
                print(f"Erreur de format d'objet dans l'intrigue {currentIntrigue.nom} : {sections}")

            if monObjet is not None:
                currentIntrigue.objets.add(monObjet)
                monObjet.inIntrigues.add(currentIntrigue)

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
        texteScenes = texteIntrigue[indexes[SCENES]["debut"] + len(SCENES):indexes[SCENES]["fin"]]
        texte2scenes(currentIntrigue, nomIntrigue, texteScenes)

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


def texte2scenes(conteneur: ConteneurDeScene, nomConteneur, texteScenes, tableauRolesExistant=True):
    nomsRoles = None
    if tableauRolesExistant:
        # à ce stade là on a et les PJs et les PNJs > on peut générer le tableau de reférence des noms dans l'intrigue
        nomsRoles = conteneur.getNomsRoles()
        # print(f"pour {currentIntrigue.nom}, nomsRoles =  {nomsRoles}")

    # print(f"Texte section scène : {texteScenes}")
    scenes = texteScenes.split("###")
    for scene in scenes:
        # print("taille de la scène : " + str(len(scene)))
        if len(scene) < 10:
            continue

        titreScene = scene.splitlines()[0].strip()
        sceneAAjouter = conteneur.addScene(titreScene)
        sceneAAjouter.modifie_par = conteneur.modifie_par
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
                extraireQuiScene(balise[8:], conteneur, nomsRoles, sceneAAjouter)

            elif balise[0:8].lower() == '## qui ?':
                extraireQuiScene(balise[9:], conteneur, nomsRoles, sceneAAjouter)

            elif balise[0:11].lower() == '## niveau :':
                sceneAAjouter.niveau = balise[12:].strip()

            elif balise[0:11].lower() == '## résumé :':
                sceneAAjouter.resume = balise[12:].strip()

            elif balise[0:10].lower() == '## résumé:':
                sceneAAjouter.resume = balise[11:].strip()

            else:
                print("balise inconnue : " + balise + " dans le conteneur " + nomConteneur)
                sceneAAjouter.description += balise

        sceneAAjouter.description = ''.join(scene.splitlines(keepends=True)[1 + len(balises):])
        # print("texte de la scene apres insertion : " + sceneAAjouter.description)


def extraireQuiScene(listeNoms, conteneur, nomsRoles, sceneAAjouter, verbal=True, seuil=80):
    roles = listeNoms.split(",")
    sceneAAjouter.noms_roles_lus = roles
    # print("rôles trouvés en lecture brute : " + str(roles))

    # dans ce cas, on prend les noms du tableau, qui fon fois, et on s'en sert pour identifier
    # les noms de la scène
    for nomRole in roles:
        if len(nomRole) < 2:
            continue
        # SI NomsRoles est None, ca veut dire qu'on travaille sans tableau de référence des rôles > on les crée sans se poser de questions
        if nomsRoles is None:
            # print("Je suis entrée dans une situation ou il n'y avait pas de référence des noms")

            # on cherche s'il existe déjà un rôle avec ce nom dans le conteneur
            roleAAjouter = None
            nomRole = nomRole.strip()
            if nomRole in conteneur.rolesContenus:
                # print(f"nom trouvé dans le contenu : {nomRole}")
                roleAAjouter = conteneur.rolesContenus[nomRole]
            else:
                # print(f"nouveau role créé dans le contenu : {nomRole}")
                roleAAjouter = Role(conteneur, nom=nomRole)
                conteneur.rolesContenus[roleAAjouter.nom] = roleAAjouter

            roleAAjouter.ajouterAScene(sceneAAjouter)

            # print(f"le rôle {roleAAjouter.nom} est associé aux scènes {[s.titre for s in roleAAjouter.scenes]}")

            # print(f"après opération d'ajout de role, les roles contienntn {conteneur.rolesContenus} ")


        else:
            # Sinon, il faut normaliser et extraire les rôles
            # pour chaque nom de la liste : retrouver le nom le plus proche dans la liste des noms du GN
            score = process.extractOne(nomRole.strip(), nomsRoles)
            # print("nom normalisé du personnage {0} trouvé dans une scène de {1} : {2}".format(nomRole.strip(), currentIntrigue.nom, score))

            # si on a trouvé quelqu'un MAIs qu'on est <80% >> afficher un warning : on s'est peut-être trompé de perso!
            if score is not None:
                if score[1] < seuil:
                    warningText = f"Warning association Scene ({score[1]}) - nom dans scène : {nomRole} > Role : {score[0]} dans {conteneur.nom}/{sceneAAjouter.titre}"
                    conteneur.addToErrorLog(warningText)
                    if verbal:
                        print(warningText)

                # trouver le rôle à ajouter à la scène en lisant l'intrigue
                monRole = conteneur.rolesContenus[score[0]]
                monRole.ajouterAScene(sceneAAjouter)
            else:
                texteErreur = f"Erreur, process renvoie None pour nom scène : {nomRole} dans {sceneAAjouter.titre}"
                if verbal:
                    print(texteErreur)
                conteneur.errorLog += texteErreur + '\n'


def extraireDateScene(baliseDate, sceneAAjouter):
    # réécrite pour merger les fontions il y a et quand :

    # est-ce que la date est écrite au format quand ? il y a ?
    if baliseDate.strip().lower()[0:6] == 'il y a':
        # print(f" 'quand il y a' trouvée : {baliseDate}")
        return extraireIlYAScene(baliseDate.strip()[7:], sceneAAjouter)
    else:
        sceneAAjouter.date = baliseDate.strip()
    # print("date de la scène : " + sceneAAjouter.date)


def extraireIlYAScene(baliseDate, sceneAAjouter):
    # print("balise date : " + baliseDate)
    # trouver s'il y a un nombres a[ns]
    dateEnJours = calculerJoursIlYA(baliseDate)

    sceneAAjouter.date = dateEnJours


def calculerJoursIlYA(baliseDate):
    baliseDate = baliseDate.lower()
    try:
        maDate = baliseDate
        # print(f"ma date avant stripping : {maDate}")
        # print(baliseDate.strip().lower()[0:6])
        # #si il y a un "il y a" dans la balise, il faut le virer
        # if baliseDate.strip().lower()[0:6] == 'il y a':
        #     maDate = baliseDate[7:]
        # print(f"ma date après stripping : {baliseDate} > {maDate}")

        ans = re.search(r"\d+\s*a", maDate)

        # trouver s'il y a un nombres* m[ois]
        mois = re.search('\d+\s*m', maDate)

        # trouver s'il y a un nombres* s[emaines]
        semaines = re.search('\d+\s*s', maDate)

        # trouver s'il y a un nombres* j[ours]
        jours = re.search('\d+\s*j', maDate)

        # print(f"{baliseDate} =  {ans} ans/ {jours} jours/ {mois} mois/ {semaines} semaines")

        # travailler ce qu'on a trouvé comme valeurs
        if ans is None:
            ans = 0
        else:
            ans = ans.group(0)[:-1]  # enlever le dernier char car c'est le marqueur de temps

        if mois is None:
            mois = 0
        else:
            mois = mois.group(0)[:-1]

        if semaines is None:
            semaines = 0
        else:
            semaines = semaines.group(0)[:-1]
        if jours is None:
            jours = 0
        else:
            jours = jours.group(0)[:-1]

        # print(f"{maDate} > ans/jours/mois = {ans}/{mois}/{jours}")

        dateEnJours = -1 * (float(ans) * 365 + float(mois) * 30.5 + float(semaines) * 7 + float(jours))
        return dateEnJours
    except ValueError:
        print(f"Erreur avec la date {baliseDate}")
        return baliseDate.strip()


def extrairePJDeTexte(textePJ, nomDoc, idUrl, lastFileEdit, derniere_modification_par, monGN, verbal=False):
    print(f"Lecture de {nomDoc}")
    if len(textePJ) < 800:
        print(f"fiche {nomDoc} avec {len(textePJ)} caractères est vide")
        return  # dans ce cas c'est qu'on est en train de lite un template, qui fait 792 cars

    nomPJ = re.sub(r"^\d+\s*-", '', nomDoc).strip()
    # print(f"nomDoc =_{nomDoc}_ nomPJ =_{nomPJ}_")
    # print(f"Personnage en cours d'importation : {nomPJ} avec {len(textePJ)} caractères")
    currentPJ = Personnage(nom=nomPJ, url=idUrl, derniere_edition_fichier=lastFileEdit)
    currentPJ.modifie_par = derniere_modification_par
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
    CHRONOLOGIE = "chronologie"
    INTRIGUES = "intrigues"
    RELATIONS = "relations avec les autres persos"
    SCENES = "scènes"

    labels = [REFERENT, JOUEURV1, JOUEURV2, PITCH, COSTUME, FACTION1, FACTION2,
              BIO, PSYCHO, MOTIVATIONS, CHRONOLOGIE, RELATIONS, INTRIGUES, JOUEUSE1, JOUEUSE2, SCENES]

    indexes = lecteurGoogle.identifierSectionsFiche(labels, textePJ)

    # print(f"indexes : {indexes}")

    if indexes[REFERENT]["debut"] == -1:
        print("pas de référent avec le perso " + nomPJ)
    else:
        currentPJ.orgaReferent = textePJ[indexes[REFERENT]["debut"]:indexes[REFERENT]["fin"]].splitlines()[
                                     0][
                                 len(REFERENT) + len(" : "):]

    if indexes[JOUEURV1]["debut"] == -1:
        if verbal:
            print("Pas de joueur 1 avec le perso " + nomPJ)
    else:
        currentPJ.joueurs['V1'] = textePJ[indexes[JOUEURV1]["debut"]:indexes[JOUEURV1]["fin"]].splitlines()[
                                      0][
                                  len(JOUEURV1) + len(" : "):]

    if indexes[JOUEURV2]["debut"] == -1:
        if verbal:
            print("Pas de joueur 2 avec le perso " + nomPJ)
    else:
        currentPJ.joueurs['V2'] = textePJ[indexes[JOUEURV2]["debut"]:indexes[JOUEURV2]["fin"]].splitlines()[
                                      0][
                                  len(JOUEURV1) + len(" : "):]

    if indexes[JOUEUSE1]["debut"] == -1:
        if verbal:
            print("Pas de joueuse 1 avec le perso " + nomPJ)
    else:
        currentPJ.joueurs['V1'] = textePJ[indexes[JOUEUSE1]["debut"]:indexes[JOUEUSE1]["fin"]].splitlines()[
                                      0][
                                  len(JOUEURV1) + len(" : "):]

    if indexes[JOUEUSE2]["debut"] == -1:
        if verbal:
            print("Pas de joueuse 2 avec le perso " + nomPJ)
    else:
        currentPJ.joueurs['V2'] = textePJ[indexes[JOUEUSE2]["debut"]:indexes[JOUEUSE2]["fin"]].splitlines()[
                                      0][
                                  len(JOUEURV1) + len(" : "):]

    if indexes[PITCH]["debut"] == -1:
        if verbal:
            print("Pas de pitch  avec le perso " + nomPJ)
    else:
        currentPJ.pitch = textePJ[indexes[PITCH]["debut"]:indexes[PITCH]["fin"]].splitlines()[1:]

    if indexes[COSTUME]["debut"] == -1:
        if verbal:
            print("Pas d'indication costume avec le perso " + nomPJ)
    else:
        currentPJ.indicationsCostume = textePJ[indexes[COSTUME]["debut"] + len(COSTUME) + len(" : "):
                                               indexes[COSTUME]["fin"]]

    if indexes[FACTION1]["debut"] == -1:
        if verbal:
            print("Pas de faction 1 avec le perso " + nomPJ)
    else:
        currentPJ.factions.append(textePJ[indexes[FACTION1]["debut"]:indexes[FACTION1]["fin"]].splitlines()[
                                      0][
                                  len(FACTION1) + len(" : "):])

    if indexes[FACTION2]["debut"] == -1:
        if verbal:
            print("Pas de faction 2 avec le perso " + nomPJ)
    else:
        currentPJ.factions.append(textePJ[indexes[FACTION2]["debut"]:indexes[FACTION2]["fin"]].splitlines()[
                                      0][
                                  len(FACTION2) + len(" : "):])

    if indexes[BIO]["debut"] == -1:
        if verbal:
            print("Pas de BIO avec le perso " + nomPJ)
    else:
        currentPJ.description = textePJ[indexes[BIO]["debut"]:
                                        indexes[BIO]["fin"]].splitlines()[1:]

    if indexes[PSYCHO]["debut"] == -1:
        if verbal:
            print("Pas de psycho avec le perso " + nomPJ)
    else:
        currentPJ.concept = textePJ[indexes[PSYCHO]["debut"]:
                                    indexes[PSYCHO]["fin"]].splitlines()[1:]

    if indexes[MOTIVATIONS]["debut"] == -1:
        if verbal:
            print("Pas de motivations avec le perso " + nomPJ)
    else:
        currentPJ.driver = textePJ[indexes[MOTIVATIONS]["debut"]:indexes[MOTIVATIONS]["fin"]].splitlines()[1:]

    if indexes[CHRONOLOGIE]["debut"] == -1:
        if verbal:
            print("Pas de chronologie avec le perso " + nomPJ)
    else:
        currentPJ.datesClefs = textePJ[indexes[CHRONOLOGIE]["debut"]:indexes[CHRONOLOGIE]["fin"]].splitlines()[1:]

    if indexes[SCENES]["debut"] == -1:
        if verbal:
            print("Pas de scènes dans le perso " + nomPJ)
    else:
        # print(f"début balise scène : {indexes[SCENES]['debut']}, fin balise scènes : {indexes[SCENES]['fin']} ")
        texteScenes = textePJ[indexes[SCENES]["debut"] + len(SCENES):indexes[SCENES]["fin"]]

        # print(f"ping j'ai trouvé la balise scènes, elle contient : {texteScenes}")
        texte2scenes(currentPJ, nomPJ, texteScenes, False)
        # for scene in currentPJ.scenes:
        #     print(f"Scene présente : {scene}")
        # print(f"rôles contenus dans {nomPJ} : {currentPJ.rolesContenus}")

    # rajouter les scènes en jeu après le tableau
    bottomText = textePJ.split("#####")[-1]
    currentPJ.textesAnnexes = bottomText

    # et on enregistre la date de dernière mise à jour de l'intrigue
    currentPJ.lastProcessing = datetime.datetime.now()

    return currentPJ


def ref_du_doc(s):
    match = re.match(r'^(\d+)\s*-.*$', s)
    if match:
        return int(match.group(1))
    else:
        return -1


def extraire_factions(mon_GN: GN, apiDoc, verbal=False):
    if not hasattr(mon_GN, 'factions'):
        mon_GN.factions = dict()

    if not hasattr(mon_GN, 'id_factions'):
        mon_GN.id_factions = None

    if mon_GN.id_factions is None:
        return -1

    try:
        document = apiDoc.documents().get(documentId=mon_GN.id_factions).execute()
        contenuDocument = document.get('body').get('content')
        text = lecteurGoogle.read_structural_elements(contenuDocument)
        text = text.replace('\v', '\n')  # pour nettoyer les backspace verticaux qui se glissent

    except HttpError as err:
        print(f'An error occurred: {err}')
        return

    # à ce stade, j'ai lu les factions et je peux dépouiller
    # print(f"clefs dictionnaire : {mon_GN.dictPJs.keys()}")
    lines = text.splitlines()
    noms_persos = list(mon_GN.noms_pjs()) + list(mon_GN.noms_pnjs())
    temp_dict = {mon_GN.dictPJs[x].nom: x for x in mon_GN.dictPJs}
    current_faction = None
    for line in lines:
        if line.startswith("### "):
            faction_name = line.replace("### ", "")
            faction_name = faction_name.strip()
            current_faction = Faction(faction_name)
            mon_GN.factions[faction_name] = current_faction
        elif line.startswith("## "):
            line = line.replace("## ", "")
            personnages_names = line.strip().split(",")
            for perso_name in personnages_names:
                perso_name = perso_name.strip()
                score = fuzzywuzzy.process.extractOne(perso_name, noms_persos)
                if verbal:
                    print(f"pour le nom {perso_name} lu dans la faction {current_faction.nom}, j'ai {score}")
                if temp_dict.get(score[0]):
                    personnages_a_ajouter = mon_GN.dictPJs[temp_dict.get(score[0])]
                else:
                    personnages_a_ajouter = mon_GN.dictPNJs[score[0]]

                current_faction.personnages.add(personnages_a_ajouter)
    return 0


def inserer_squelettes_dans_drive(parent_id: str, api_doc, api_drive, text: str, nom_fichier, titre=False):
    id = add_doc(api_drive, nom_fichier, parent_id)
    write_to_doc(api_doc, id, text, titre=titre)
    formatter_titres_scenes_dans_squelettes(api_doc, id)


def check_if_doc_exists(service, file_id):
    try:
        # check if the file exists
        service.files().get(fileId=file_id).execute()
        return True
    except HttpError as error:
        if error.resp.status == 404:
            print(F'File not found: {file_id}')
        else:
            print(F'An error occurred: {error}')
        return False


def is_document_being_edited(service, file_id):
    try:
        # get the document
        doc = service.documents().get(documentId=file_id).execute()
        # check if the document is being edited
        if doc.get('isWriting') == True:
            print("Document is currently being edited")
            return True
        else:
            print("Document is not currently being edited")
            return False
    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def add_doc(service, nom_fichier, parent):
    try:
        # create the metadata for the new document
        file_metadata = {
            'name': nom_fichier,
            'parents': [parent],
            'mimeType': 'application/vnd.google-apps.document'
        }

        # create the document
        file = service.files().create(body=file_metadata, fields='id').execute()
        print(F'File ID pour {nom_fichier}: {file.get("id")}')
        return file.get("id")

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None


def write_to_doc(service, file_id, text, titre=False):
    try:
        requests = [{
            'insertText': {
                'location': {
                    'index': 1
                },
                'text': text
            }
        }]
        # Execute the request.
        result = service.documents().batchUpdate(documentId=file_id, body={'requests': requests}).execute()
        return result
    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def formatter_titres_scenes_dans_squelettes(service, file_id):
    try:
        # get the document
        doc = service.documents().get(documentId=file_id).execute()

        # initialize the request list
        requests = []

        # loop through the paragraphs of the document
        for para in doc.get('body').get('content'):
            # check if the paragraph is a text run and starts with "titre scène"
            if 'paragraph' in para and para.get('paragraph').get('elements')[0].get('textRun').get(
                    'content').startswith("titre scène"):
                # create the update request
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': para.get('startIndex'),
                            'endIndex': para.get('endIndex')
                        },
                        'textStyle': {
                            'bold': True,
                            'fontSize': {
                                'magnitude': 12,
                                'unit': 'PT'
                            }
                        },
                        'fields': 'bold,fontSize'
                    }
                })
        # execute the requests
        result = service.documents().batchUpdate(documentId=file_id, body={'requests': requests}).execute()
        return result
    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def creer_dossier(service_drive, id_dossier_parent, nom_dossier):
    try:
        # Création de l'objet dossier
        nouveau_dossier = {'name': nom_dossier, 'parents': [id_dossier_parent],
                           'mimeType': 'application/vnd.google-apps.folder'}
        # Ajout du nouveau dossier
        dossier_cree = service_drive.files().create(body=nouveau_dossier, fields='id').execute()
        # Récupération de l'id du nouveau dossier
        id_dossier = dossier_cree.get('id')
        return id_dossier
    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def creer_google_sheet(api_drive, nom_sheet: str, parent_folder_id: str):
    # Create a new document
    body = {
        'name': nom_sheet,
        'parents': [parent_folder_id],
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    new_doc = api_drive.files().create(body=body).execute()
    return new_doc.get("id")


# tableau_scene_orgas, id, dict_orgas_persos, api_sheets
def exporter_changelog(tableau_scenes_orgas, spreadsheet_id, dict_orgas_persos, service, verbal=False):
    # create the "tous" worksheet
    tous_worksheet = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": "tous"
                    }
                }
            }
        ]
    }).execute()
    tous_worksheet_id = tous_worksheet['replies'][0]['addSheet']['properties']['sheetId']

    # create a worksheet for each value in dict_orgas_persos
    for orga in dict_orgas_persos:
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": orga
                        }
                    }
                }
            ]
        }).execute()

    # write data to the "tous" worksheet
    values = [["nom_scene", "date", "qui", "document"] + list(dict_orgas_persos.keys())]
    if verbal:
        print(f"en-tetes = {values}")

    for scene_orgas in tableau_scenes_orgas:
        dict_scene, dict_orgas = scene_orgas
        row = [dict_scene["nom_scene"], dict_scene["date"], dict_scene["qui"], dict_scene["document"]]

        for orga in dict_orgas_persos:
            if orga in dict_orgas:
                nom_persos = ", ".join([perso for perso in dict_orgas[orga]])
                row.append(nom_persos)
            else:
                row.append("")
        values.append(row)

    body = {
        'range': 'tous!A1',
        'values': values,
        'majorDimension': 'ROWS'
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range='tous!A1',
        valueInputOption='RAW', body=body).execute()

    # write data to the worksheets for each value in dict_orgas_persos
    for orga in dict_orgas_persos:
        print(f"fiche orga en cours de création = {orga}")

        # persos = []
        # for orga_set in dict_orgas_persos.values():
        #     persos.extend(orga_set)
        persos = [p for p in dict_orgas_persos[orga]]
        values = [["nom_scene", "date", "qui", "document"] + persos]
        if verbal:
            print(f"en-tetes = {values}")
        for scene_orgas in tableau_scenes_orgas:
            dict_scene, dict_orgas = scene_orgas
            row = [dict_scene["nom_scene"], dict_scene["date"], dict_scene["qui"], dict_scene["document"]]

            for perso in dict_orgas_persos[orga]:
                if orga not in dict_orgas or perso not in dict_orgas[orga]:
                    row.append("")
                else:
                    row.append("x")
            values.append(row)
        body = {
            'range': f'{orga}!A1',
            'values': values,
            'majorDimension': 'ROWS'
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=f'{orga}!A1',
            valueInputOption='RAW', body=body).execute()


def ecrire_table_google_sheets(service, table, spreadsheet_id):
    # def ecrire_table_google_sheets(api_doc, df, spreadsheet_id):
    try:
        body = {
            'range': 'A1',
            'values': table,
            'majorDimension': 'ROWS'
        }
        # print(f"api_doc = {api_doc}")

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range='A1',
            valueInputOption='RAW', body=body).execute()

    except HttpError as error:
        print(f'An error occurred: {error}')
        result = None
    return result


def formatter_fichier_erreurs(api_doc, doc_id):
    # Récupère le contenu complet du document
    try:
        doc = api_doc.documents().get(documentId=doc_id).execute()
        requests = []

        # Parcours toutes les lignes du document pour trouver les lignes qui commencent par "Pour"
        for line in doc.get('body').get('content'):
            if 'paragraph' in line:
                # Récupère le contenu de la ligne
                text = line.get('paragraph').get('elements')[0].get('textRun').get('content')
                if text.startswith("Pour "):
                    # Si la ligne commence par "Pour ", on ajoute une requête pour mettre le texte en gras
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': line.get('startIndex'),
                                'endIndex': line.get('endIndex')
                            },
                            'textStyle': {
                                'bold': True,
                                'fontSize': {
                                    'magnitude': 12,
                                    'unit': 'PT'
                                }
                            },
                            'fields': 'bold, fontSize'
                        }
                    })
                elif text.startswith("Erreur"):
                    # Si la ligne commence par "Erreur", on ajoute une requête pour mettre le texte en rouge
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': line.get('startIndex'),
                                'endIndex': line.get('endIndex')
                            },
                            'textStyle': {
                                'foregroundColor': {
                                    'color': {
                                        'rgbColor': {
                                            'blue': 0.0,
                                            'green': 0.0,
                                            'red': 1.0
                                        }
                                    }
                                }
                            },
                            'fields': 'foregroundColor'
                        }
                    })
                elif text.startswith("Warning"):
                    # Si la ligne commence par "Warning", on ajoute une requête pour mettre le texte en orange
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': line.get('startIndex'),
                                'endIndex': line.get('endIndex')
                            },
                            'textStyle': {
                                'foregroundColor': {
                                    'color': {
                                        'rgbColor': {
                                            'blue': 0.0,
                                            'green': 0.5,
                                            'red': 1.0
                                        }
                                    }
                                }
                            },
                            'fields': 'foregroundColor'
                        }
                    })
                elif text.startswith("[XX]"):
                    # Si la ligne commence par "[XX]", on ajoute une requête pour mettre le texte en vert
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': line.get('startIndex'),
                                'endIndex': line.get('endIndex')
                            },
                            'textStyle': {
                                'foregroundColor': {
                                    'color': {
                                        'rgbColor': {
                                            'blue': 0.0,
                                            'green': 0.5,
                                            'red': 1.0
                                        }
                                    }
                                }
                            },
                            'fields': 'foregroundColor'
                        }
                    })
                elif text.startswith("[OK]"):
                    # Si la ligne commence par "[OK]", on ajoute une requête pour mettre le texte en vert
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': line.get('startIndex'),
                                'endIndex': line.get('endIndex')
                            },
                            'textStyle': {
                                'foregroundColor': {
                                    'color': {
                                        'rgbColor': {
                                            'blue': 0.035,
                                            'green': 0.224,
                                            'red': 0.027
                                        }
                                    }
                                }
                            },
                            'fields': 'foregroundColor'
                        }
                    })

        # Envoie toutes les requêtes en une seule fois pour mettre à jour le document
        result = api_doc.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    except:
        result = None

    return result



