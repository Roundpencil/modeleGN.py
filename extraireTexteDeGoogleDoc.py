from __future__ import print_function

from typing import Any

import fuzzywuzzy.process
from googleapiclient.errors import HttpError

import lecteurGoogle
from modeleGN import *

import dateparser


def extraire_intrigues(mon_gn, api_drive, api_doc, singletest="-01", verbal=False, fast=True):
    extraire_texte_de_google_doc(mon_gn, api_drive, api_doc, extraire_intrigue_de_texte, mon_gn.intrigues,
                                 mon_gn.dossiers_intrigues,
                                 singletest, verbal=verbal, fast=fast)


def extraire_pjs(mon_gn: GN, api_drive, api_doc, singletest="-01", verbal=False, fast=True):
    # print(f"je m'apprete à extraire les PJs depuis {gn.dossiers_pjs}")
    extraire_texte_de_google_doc(
        mon_gn, api_drive, api_doc, extraire_persos_de_texte, mon_gn.dictPJs, mon_gn.dossiers_pjs,
        singletest,
        verbal=verbal, fast=fast)


def extraire_pnjs(mon_gn: GN, api_drive, api_doc, singletest="-01", verbal=False, fast=True):
    # print(f"je m'apprête à extraire les PNJs depuis {gn.dossiers_pnjs}")
    if mon_gn.dossiers_pnjs is None or len(mon_gn.dossiers_pnjs) == 0:
        print("impossible de lire le dossier des PNJs : il n'existe pas")
        return
    extraire_texte_de_google_doc(mon_gn, api_drive, api_doc, extraire_persos_de_texte, mon_gn.dictPNJs,
                                 mon_gn.dossiers_pnjs,
                                 singletest,
                                 verbal=verbal, fast=fast)


def extraire_evenements(mon_gn: GN, apiDrive, apiDoc, singletest="-01", verbal=False, fast=True):
    # print(f"je m'apprete à extraire les PNJs depuis {gn.dossiers_pnjs}")
    if mon_gn.dossiers_evenements is None or len(mon_gn.dossiers_evenements) == 0:
        print(f"impossible de lire le dossier des évènements : il n'existe pas")
        return
    extraire_texte_de_google_doc(mon_gn, apiDrive, apiDoc, extraire_evenement_de_texte, mon_gn.dict_evenements,
                                 mon_gn.dossiers_evenements,
                                 singletest,
                                 verbal=verbal, fast=fast)


def extraire_texte_de_google_doc(mon_gn, apiDrive, apiDoc, fonction_extraction, dict_ids: dict, folder_array,
                                 single_test="-01", verbal=False, fast=True):
    items = lecteurGoogle.generer_liste_items(mon_gn, apiDrive=apiDrive, nom_fichier=folder_array)
    # print(f"folder = {folder_array}  items = {items}")

    if not items:
        print('No files found.')
        return

    # print(f"single_test : {type(single_test)} = {single_test}")
    if int(single_test) > 0:
        for item in items:
            try:
                # print ("poung")

                # print ("ping")
                # Retrieve the documents contents from the Docs api_doc.
                document = apiDoc.documents().get(documentId=item['id']).execute()

                print(f"Titre document : {document.get('title')}")

                # Alors on se demande si c'est le bon doc
                # if document.get('title')[0:3].strip() != str(single_test):  # numéro de l'intrigue
                #     # si ce n'est pas la bonne, pas la peine d'aller plus loin
                #     continue
                if ref_du_doc(document.get('title')) != int(single_test):
                    continue
                else:
                    print(f"j'ai trouvé le doc #{single_test} : {document.get('title')}")
                    # if item['id'] in gn.intrigues.keys():
                    #     gn.intrigues[item['id']].clear()
                    #     del gn.intrigues[item['id']]

                    objet_de_reference = None
                    if item['id'] in dict_ids.keys():
                        # dict_ids[item['id']].clear()
                        objet_de_reference = dict_ids.pop(item['id'])

                    nouvel_objet = extraire_objets_de_document(document, item, mon_gn, fonction_extraction,
                                                               saveLastChange=False, verbal=verbal)

                    if objet_de_reference is not None:
                        if isinstance(nouvel_objet, ConteneurDeScene):
                            nouvel_objet.updater_dates_maj_scenes(objet_de_reference)
                        objet_de_reference.clear()

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

                print(f"Titre document : {document.get('title')}")
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
                # if item['id'] in gn.intrigues .keys():
                if item['id'] in dict_ids.keys():

                    #       SI la date de mise à jour du fichier n'est pas postérieure à la date de MAJ de l'intrigue
                    # print("l'intrigue fait déjà partie du GN ! ")
                    # print(f"Variable / type : gn.intrigues[item['id']].lastChange /
                    # {type(gn.intrigues[item['id']].lastChange)} / {gn.intrigues[item['id']].lastChange}")
                    # print(f"Variable / type : item['modifiedTime'] / {type(item['modifiedTime'])} /
                    # {item['modifiedTime']}")

                    # on enlève les 5 derniers chars qui sont un point, les millisecondes et Z, pour formatter
                    # if gn.intrigues[item['id']].lastChange >=
                    # datetime.datetime.strptime(item['modifiedTime'][:-5], '%Y-%m-%dT%H:%M:%S'):
                    # if dict_ids[item['id']].lastProcessing >= item['modifiedTime']:
                    if fast and \
                            dict_ids[item['id']].lastProcessing >= datetime.datetime.strptime(
                        item['modifiedTime'][:-5], '%Y-%m-%dT%H:%M:%S'):

                        print(
                            f"et elle n'a pas changé (dernier changement : "
                            f"{datetime.datetime.strptime(item['modifiedTime'][:-5], '%Y-%m-%dT%H:%M:%S')}) "
                            f"depuis le dernier passage ({dict_ids[item['id']].lastProcessing})")
                        # ALORS : Si c'est la même que la plus vielle mise à jour : on arrête
                        # si c'était la plus vieille du GN, pas la peine de continuer

                        break
                        # on a trouvé une intrigue qui n'a pas bougé :
                        # toutes les suivantes qu'il nous remontera seront plus anciennes
                        # donc on arrête de parcourir
                    else:
                        # print("elle a changé depuis mon dernier passage : supprimons-la !")
                        # dans ce cas, il faut la supprimer, car on va tout réécrire
                        # gn.intrigues[item['id']].clear()
                        # del gn.intrigues[item['id']]

                        objet_de_reference = dict_ids.pop(item['id'])

                # puis, dans tous les cas, on la crée
                nouvel_objet = extraire_objets_de_document(document, item, mon_gn, fonction_extraction, verbal=verbal)
                if objet_de_reference is not None:
                    if isinstance(nouvel_objet, ConteneurDeScene):
                        nouvel_objet.updater_dates_maj_scenes(objet_de_reference)
                    objet_de_reference.clear()

            except HttpError as err:
                print(f'An error occurred: {err}')
                # return #ajouté pour débugger


def extraire_objets_de_document(document, item, mon_gn, fonctionExtraction, saveLastChange=True, verbal=False):
    # print("et du coup, il est temps de créer un nouveau fichier")
    # à ce stade, soit on sait qu'elle n'existait pas, soit on l'a effacée pour la réécrire
    contenu_document = document.get('body').get('content')
    text = lecteurGoogle.read_structural_elements(contenu_document)
    text = text.replace('\v', '\n')  # pour nettoyer les backspace verticaux qui se glissent

    # print(text) #test de la fonction récursive pour le texte
    # mon_objet = extraire_intrigue_de_texte(text, document.get('title'), item["id"], gn)
    last_file_edit = datetime.datetime.strptime(
        item['modifiedTime'][:-5],
        '%Y-%m-%dT%H:%M:%S')
    if verbal:
        print(f"clef présentes : {item['lastModifyingUser'].keys()}")

    try:
        derniere_modification_par = item['lastModifyingUser']['emailAddress']
    except Exception:
        derniere_modification_par = "Utilisateur inconnu"

    mon_objet = fonctionExtraction(text, document.get('title'), item["id"], last_file_edit, derniere_modification_par,
                                   mon_gn, verbal)
    # mon_objet.url = item["id"]
    # et on enregistre la date de dernière mise à jour de l'intrigue

    if mon_objet is not None and saveLastChange:
        mon_objet.lastProcessing = datetime.datetime.now()
    # print(f'url intrigue = {mon_objet.url}')
    # print(f"intrigue {mon_objet.nom}, date de modification : {item['modifiedTime']}")
    return mon_objet


def extraire_intrigue_de_texte(texteIntrigue, nomIntrigue, idUrl, lastFileEdit, derniere_modification_par, monGN,
                               verbal=False):
    # print("texte intrigue en entrée : ")
    # print(texteIntrigue.replace('\v', '\n'))
    # texteIntrigue = texteIntrigue.replace('\v', '\n')
    # print("*****************************")
    current_intrigue = Intrigue(nom=nomIntrigue, url=idUrl, derniere_edition_fichier=lastFileEdit)
    current_intrigue.modifie_par = derniere_modification_par
    monGN.intrigues[idUrl] = current_intrigue
    # noms_persos = gn.liste_noms_pjs()

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
    QUESTIONNAIRE = "questionnaire inscription"

    labels = [REFERENT, TODO, PITCH, PJS, PNJS, REROLLS, OBJETS, SCENESFX,
              TIMELINE, SCENES, RESOLUTION, NOTES, QUESTIONNAIRE]

    indexes = lecteurGoogle.identifier_sections_fiche(labels, texteIntrigue)

    # gestion de la section OrgaRéférent
    if indexes[REFERENT]["debut"] == -1:
        print("problème référent avec l'intrigue " + nomIntrigue)
    else:
        current_intrigue.orgaReferent = texteIntrigue[indexes[REFERENT]["debut"]:indexes[REFERENT]["fin"]].splitlines()[
                                            0][
                                        len(REFERENT) + len(" : "):].strip()
        # prendre la première ligne puis les caractères à partir du label
        # print("debut / fin orga référent : {0}/{1} pour {2}"
        # .format(indexDebutReferent, indexFinReferent, nomIntrigue))
        # print("Orga référent : " + currentIntrigue.orgaReferent)

    # gestion de la section à faire
    if indexes[TODO]["debut"] == -1:
        print("problème état de l'intrigue avec l'intrigue " + nomIntrigue)
    else:
        # currentIntrigue.questions_ouvertes = ''.join(
        #     texteIntrigue[indexes[TODO]["debut"]:indexes[TODO]["fin"]].splitlines()[1:])
        current_intrigue.questions_ouvertes = texteIntrigue[indexes[TODO]["debut"] + len(TODO):indexes[TODO]["fin"]]

    # gestion de la section Résumé
    current_intrigue.pitch = ''.join(
        texteIntrigue[indexes[PITCH]["debut"]:indexes[PITCH]["fin"]].splitlines(keepends=True)[1:])
    # print("section pitch trouvée : " + section)
    # print("pitch isolé after découpage : " + ''.join(section.splitlines(keepends=True)[1:]))
    # print("pitch lu dans l'intrigue après mise à jour : " + currentIntrigue.pitch)

    # gestion de la section PJ
    pjs = texteIntrigue[indexes[PJS]["debut"]:indexes[PJS]["fin"]].split("¤¤¤¤¤")
    nb_colonnes = len(pjs[0].split("¤¤¤"))
    if nb_colonnes == 4:
        lire_tableau_pj_chalacta(current_intrigue, pjs)
    elif nb_colonnes == 5:
        lire_tableau_pj_5_colonnes(current_intrigue, pjs)
    elif nb_colonnes == 6:
        lire_tableau_pj_6_colonnes(current_intrigue, pjs)
    else:
        current_intrigue.error_log.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                  "Tableau des personnages dans l'intrigue non standard",
                                                  ErreurManager.ORIGINES.SCENE)
        print("Erreur : tableau d'intrigue non standard")

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
            pnjAAjouter = Role(current_intrigue, nom=sections[0].strip(), description=sections[3].strip(),
                               pj=TypePerso.EST_PNJ_HORS_JEU, niveau_implication=sections[2].strip(),
                               perimetre_intervention=sections[1].strip())

            # print("Je suis en train de regarder {0} et son implication est {1}"
            # .format(pnjAAjouter.nom, sections[1].strip()))

            # cherche ensuite le niveau d'implication du pj
            if sections[1].strip().lower().find('perman') > -1:
                # print(pnjAAjouter.nom + " est permanent !!")
                pnjAAjouter.pj = TypePerso.EST_PNJ_PERMANENT
            elif sections[1].strip().lower().find('infiltr') > -1:
                pnjAAjouter.pj = TypePerso.EST_PNJ_INFILTRE
                # print(pnjAAjouter.nom + " est temporaire !!")
            # elif sections[1].strip().lower().find('temp') > -1:
            #     pnjAAjouter.pj = modeleGN.EST_PNJ_TEMPORAIRE
            #     # print(pnjAAjouter.nom + " est temporaire !!")
            elif len(sections[1].strip()) > 1:
                pnjAAjouter.pj = TypePerso.EST_PNJ_TEMPORAIRE
                # print(pnjAAjouter.nom + " est temporaire !!")

            # sinon PNJ hors-jeu est la valeur par défaut : ne rien faire

            # du coup, on peut l'ajouter aux intrigues
            current_intrigue.rolesContenus[pnjAAjouter.nom] = pnjAAjouter

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
            reRollAAjouter = Role(current_intrigue, nom=sections[0].strip(), description=sections[3].strip(),
                                  pj=TypePerso.EST_REROLL, type_intrigue=sections[2].strip(),
                                  niveau_implication=sections[1].strip())

            # du coup, on peut l'ajouter aux intrigues
            current_intrigue.rolesContenus[reRollAAjouter.nom] = reRollAAjouter

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
            mon_objet = None
            if len(sections) == 4:
                mon_objet = Objet(description=sections[0].strip(),
                                  specialEffect=sections[1].strip() if sections[1].strip().lower() != "non" else '',
                                  emplacementDebut=sections[2].strip(),
                                  fourniPar=sections[3].strip())
                # if sections[3].strip().lower() != "non":  # si on a mis non pour le RFID ca ne veut pas dire oui :)
                #     mon_objet.specialEffect = sections[1].strip()

            elif len(sections) == 3:
                mon_objet = Objet(description=sections[0].strip(),
                                  emplacementDebut=sections[1].strip(),
                                  fourniPar=sections[2].strip())
            elif len(sections) == 6:
                mon_objet = Objet(code=sections[0].strip(),
                                  description=sections[1].strip(),
                                  specialEffect=sections[2].strip() if sections[2].strip().lower() != "non" else '',
                                  emplacementDebut=sections[3].strip(),
                                  fourniPar=sections[4].strip())
            else:
                print(f"Erreur de format d'objet dans l'intrigue {current_intrigue.nom} : {sections}")

            if mon_objet is not None:
                current_intrigue.objets.add(mon_objet)
                mon_objet.inIntrigues.add(current_intrigue)

        # objets = texteIntrigue[indexes[OBJETS]["debut"]:indexes[OBJETS]["fin"]]
        # tab_objets, nb_colonnes = reconstituer_tableau(objets)
        # for ligne in tab_objets[1:]:
        #     mon_objet = None
        #     if nb_colonnes == 3:
        #         mon_objet = Objet(description=ligne[0].strip(), emplacementDebut=ligne[1].strip(),
        #                           fourniPar=ligne[2].strip())
        #     elif nb_colonnes == 4:
        #         mon_objet = Objet(description=ligne[0].strip(),
        #                           specialEffect=ligne[1].strip() if ligne[1].strip().lower() != "non" else '',
        #                           emplacementDebut=ligne[2].strip(),
        #                           fourniPar=ligne[3].strip())
        #         # if ligne[1].strip().lower() != "non":
        #         #     # si on a mis non pour le RFID ca ne veut pas dire oui :)
        #         #     mon_objet.specialEffect = ligne[1].strip()
        #     elif nb_colonnes == 6:
        #         mon_objet = Objet(code=ligne[0].strip(),
        #                           description=ligne[1].strip(),
        #                           specialEffect=ligne[2].strip() if ligne[2].strip().lower() != "non" else '',
        #                           emplacementDebut=ligne[3].strip(),
        #                           fourniPar=ligne[4].strip())
        #     else:
        #         print(f"Erreur de format d'objet dans l'intrigue {current_intrigue.nom} : {ligne}")
        #     if mon_objet is not None:
        #         current_intrigue.objets.add(mon_objet)
        #         mon_objet.inIntrigues.add(current_intrigue)

    # gestion de la section FX
    if indexes[SCENESFX]["debut"] > -1:
        current_intrigue.scenesEnJeu = ''.join(
            texteIntrigue[indexes[SCENESFX]["debut"]:indexes[SCENESFX]["fin"]].splitlines()[1:])

    # gestion de la section Questionnaire
    if indexes[QUESTIONNAIRE]["debut"] > -1:
        current_intrigue.questionnaire = ''.join(
            texteIntrigue[indexes[QUESTIONNAIRE]["debut"]:indexes[QUESTIONNAIRE]["fin"]].splitlines()[1:])

    # gestion de la section Timeline
    if indexes[TIMELINE]["debut"] > -1:
        current_intrigue.timeline = ''.join(
            texteIntrigue[indexes[TIMELINE]["debut"]:indexes[TIMELINE]["fin"]].splitlines()[1:])

    # gestion de la section Scènes
    if indexes[SCENES]["debut"] > -1:
        texteScenes = texteIntrigue[indexes[SCENES]["debut"] + len(SCENES):indexes[SCENES]["fin"]]
        texte2scenes(current_intrigue, nomIntrigue, texteScenes)

    # gestion de la section Résolution
    if indexes[RESOLUTION]["debut"] > -1:
        current_intrigue.resolution = ''.join(
            texteIntrigue[indexes[RESOLUTION]["debut"]:indexes[RESOLUTION]["fin"]].splitlines()[1:])

    # gestion de la section notes
    # print("debut/fin notes : {0}/{1}".format(indexes[NOTES]["debut"], indexes[NOTES]["fin"]))
    if indexes[NOTES]["debut"] > -1:
        current_intrigue.notes = ''.join(texteIntrigue[indexes[NOTES]["debut"]:indexes[NOTES]["fin"]].splitlines()[1:])

    # print("liste des persos : ")
    # for role in currentIntrigue.roles:
    #     print(role)

    return current_intrigue


def lire_tableau_pj_chalacta(currentIntrigue, pjs):
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
                            type_intrigue=sections[2].strip(),
                            niveau_implication=sections[1].strip()
                            )
        currentIntrigue.rolesContenus[roleAAjouter.nom] = roleAAjouter


def lire_tableau_pj_5_colonnes(current_intrigue, pjs):
    for pj in pjs[1:]:  # on commence en 1 pour éviter de prendre la première ligne
        # print("taille du prochain PJ : " +str(len(pj)))
        if len(pj) < 18:  # dans ce cas, c'est qu'un a une ligne du tableau vide
            # print("pas assez de caractères je me suis arrêté")
            continue  # il y a de fortes chances que le PJ ne contienne que des renvois à la ligne
        sections = pj.split("¤¤¤")
        # print("j'ai trouvé " + str(len(sections)) + " sections")

        if len(sections) < 4:  # testé pour éviter de se taper les lignes vides après le tableau
            continue

        roleAAjouter = Role(current_intrigue,
                            nom=sections[0].split("http")[0].strip(),
                            description=sections[4].strip(),
                            type_intrigue=sections[3].strip(),
                            niveau_implication=sections[2].strip(),
                            pip_globaux=sections[1].strip()
                            )
        current_intrigue.rolesContenus[roleAAjouter.nom] = roleAAjouter


def lire_tableau_pj_6_colonnes(current_intrigue, pjs):
    for pj in pjs[1:]:  # on commence en 1 pour éviter de prendre la première ligne
        print("taille du prochain PJ : " + str(len(pj)))
        if len(pj) < 22:  # dans ce cas, c'est qu'un a une ligne du tableau vide
            # print("pas assez de caractères je me suis arrêté")
            continue  # il y a de fortes chances que le PJ ne contienne que des renvois à la ligne
        sections = pj.split("¤¤¤")
        # print("j'ai trouvé " + str(len(sections)) + " sections")

        if len(sections) < 6:  # testé pour éviter de se taper les lignes vides après le tableau
            continue

        roleAAjouter = Role(current_intrigue,
                            nom=sections[0].split("http")[0].strip(),
                            description=sections[5].strip(),
                            type_intrigue=sections[4].strip(),
                            niveau_implication=sections[3].strip(),
                            pipi=sections[1].strip(),
                            pipr=sections[2].strip()
                            )
        current_intrigue.rolesContenus[roleAAjouter.nom] = roleAAjouter


def texte2scenes(conteneur: ConteneurDeScene, nomConteneur, texteScenes, tableauRolesExistant=True):
    noms_roles = None
    if tableauRolesExistant:
        # à ce stade là on a et les PJs et les PNJs > on peut générer le tableau de référence des noms dans l'intrigue
        noms_roles = conteneur.get_noms_roles()
        # print(f"pour {currentIntrigue.nom}, noms_roles =  {noms_roles}")

    # print(f"Texte section scène : {texteScenes}")
    scenes = texteScenes.split("###")
    for scene in scenes:
        # print("taille de la scène : " + str(len(scene)))
        if len(scene) < 10:
            continue

        titre_scene = scene.splitlines()[0].strip()
        scene_a_ajouter = conteneur.ajouter_scene(titre_scene)
        scene_a_ajouter.modifie_par = conteneur.modifie_par
        # print("titre de la scène ajoutée : " + scene_a_ajouter.titre)

        balises = re.findall(r'##.*', scene)
        for balise in balises:
            # print("balise : " + balise)
            if balise[0:9].lower() == '## quand?':
                extraire_date_scene(balise[10:], scene_a_ajouter)
            elif balise[0:10].lower() == '## quand ?':
                extraire_date_scene(balise[11:], scene_a_ajouter)
                # scene_a_ajouter.date = balise[11:].strip()
                # # print("date de la scène : " + scene_a_ajouter.date)
            elif balise[0:9].lower() == '## il y a':
                extraire_il_y_a_scene(balise[10:], scene_a_ajouter)
            elif balise[0:9].lower() == '## date :':
                extraire_date_absolue(balise[10:], scene_a_ajouter)
            elif balise[0:8].lower() == '## date?':
                extraire_date_absolue(balise[9:], scene_a_ajouter)
            elif balise[0:7].lower() == '## qui?':
                extraire_qui_scene(balise[8:], conteneur, noms_roles, scene_a_ajouter)

            elif balise[0:8].lower() == '## qui ?':
                extraire_qui_scene(balise[9:], conteneur, noms_roles, scene_a_ajouter)

            elif balise[0:11].lower() == '## niveau :':
                scene_a_ajouter.niveau = balise[12:].strip()

            elif balise[0:11].lower() == '## résumé :':
                scene_a_ajouter.resume = balise[12:].strip()

            elif balise[0:10].lower() == '## résumé:':
                scene_a_ajouter.resume = balise[11:].strip()

            elif balise[0:13].lower() == '## factions :':
                scene_a_ajouter.nom_factions.add([f.strip() for f in balise[14:].split(',')])

            elif balise[0:12].lower() == '## faction :':
                noms_factions = [f.strip() for f in balise[13:].split(',')]
                for f in noms_factions:
                    scene_a_ajouter.nom_factions.add(f)

            elif balise[0:12].lower() == '## factions:':
                scene_a_ajouter.nom_factions.add([f.strip() for f in balise[13:].split(',')])

            elif balise[0:11].lower() == '## faction:':
                scene_a_ajouter.nom_factions.add([f.strip() for f in balise[12:].split(',')])

            else:
                texte_erreur = "balise inconnue : " + balise + " dans le conteneur " + nomConteneur
                print(texte_erreur)
                scene_a_ajouter.description += balise
                conteneur.error_log.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                   texte_erreur,
                                                   ErreurManager.ORIGINES.SCENE)

        scene_a_ajouter.description = ''.join(scene.splitlines(keepends=True)[1 + len(balises):])
        # print("texte de la scene apres insertion : " + scene_a_ajouter.description)


def extraire_qui_scene(liste_noms, conteneur, noms_roles, scene_a_ajouter, verbal=True, seuil=80):
    roles = liste_noms.split(",")
    scene_a_ajouter.noms_roles_lus = roles
    # print("rôles trouvés en lecture brute : " + str(roles))

    # dans ce cas, on prend les noms du tableau, qui fon fois, et on s'en sert pour identifier
    # les noms de la scène
    for nom_du_role in roles:
        if len(nom_du_role) < 2:
            continue
        # SI NomsRoles est None, ca veut dire qu'on travaille sans tableau de référence des rôles
        # > on les crée sans se poser de questions
        if noms_roles is None:
            # print("Je suis entrée dans une situation ou il n'y avait pas de référence des noms")

            # on cherche s'il existe déjà un rôle avec ce nom dans le conteneur
            # roleAAjouter = None
            nom_du_role = nom_du_role.strip()
            if nom_du_role in conteneur.rolesContenus:
                # print(f"nom trouvé dans le contenu : {nom_du_role}")
                role_a_ajouter = conteneur.rolesContenus[nom_du_role]
            else:
                # print(f"nouveau role créé dans le contenu : {nom_du_role}")
                role_a_ajouter = Role(conteneur, nom=nom_du_role)
                conteneur.rolesContenus[role_a_ajouter.nom] = role_a_ajouter

            role_a_ajouter.ajouter_a_scene(scene_a_ajouter)

            # print(f"le rôle {roleAAjouter.nom} est associé aux scènes {[s.titre for s in roleAAjouter.scenes]}")

            # print(f"après opération d'ajout de role, les roles contienntn {conteneur.rolesContenus} ")

        else:
            # Sinon, il faut normaliser et extraire les rôles
            # pour chaque nom de la liste : retrouver le nom le plus proche dans la liste des noms du GN
            score = process.extractOne(nom_du_role.strip(), noms_roles)
            # print("nom normalisé du personnage {0} trouvé dans une scène de {1} : {2}".format(nom_du_role.strip(),
            #                                                                                   conteneur.nom,
            #                                                                                   score))

            # si on a trouvé quelqu'un MAIs qu'on est <80% >> afficher un warning : on s'est peut-être trompé de perso!
            if score is not None:
                if score[1] < seuil:
                    warning_text = f"Association Scene ({score[1]}) - nom dans scène : {nom_du_role} " \
                                   f"> Role : {score[0]} dans {conteneur.nom}/{scene_a_ajouter.titre}"
                    conteneur.add_to_error_log(ErreurManager.NIVEAUX.WARNING,
                                               warning_text,
                                               ErreurManager.ORIGINES.SCENE)
                    if verbal:
                        print(warning_text)

                # trouver le rôle à ajouter à la scène en lisant l'intrigue
                mon_role = conteneur.rolesContenus[score[0]]
                mon_role.ajouter_a_scene(scene_a_ajouter)
            else:
                texte_erreur = f"Erreur, process renvoie None pour nom scène : " \
                               f"{nom_du_role} dans {scene_a_ajouter.titre}"
                if verbal:
                    print(texte_erreur)
                conteneur.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                           texte_erreur,
                                           ErreurManager.ORIGINES.SCENE)


def extraire_date_scene(balise_date, scene_a_ajouter):
    # réécrite pour merger les fonctions il y a et quand :

    # est-ce que la date est écrite au format quand ? il y a ?
    if balise_date.strip().lower()[0:6] == 'il y a':
        # print(f" 'quand il y a' trouvée : {balise_date}")
        return extraire_il_y_a_scene(balise_date.strip()[7:], scene_a_ajouter)
    else:
        scene_a_ajouter.date = balise_date.strip()
    # print("date de la scène : " + scene_a_ajouter.date)


def extraire_il_y_a_scene(baliseDate, scene_a_ajouter):
    # print("balise date : " + balise_date)
    # trouver s'il y a un nombre a[ns]
    date_en_jours = calculer_jours_il_y_a(baliseDate)
    # print(f"dans extraire il y a scene : {date_en_jours} avant de mettre à jour")

    scene_a_ajouter.date = date_en_jours
    # print(f"et après mise à jour de la scène : {scene_a_ajouter.date}")


def extraire_date_absolue(texte_brut: str, scene_a_ajouter: Scene):
    if texte_brut.endswith("h"):
        texte_brut += "00"
    scene_a_ajouter.date_absolue = dateparser.parse(texte_brut, languages=['fr'])


def calculer_jours_il_y_a(balise_date):
    # print(f"balise date il y a en entrée {balise_date}")
    balise_date = balise_date.lower()
    try:
        ma_date = balise_date
        # print(f"ma date avant stripping : {ma_date}")
        # print(balise_date.strip().lower()[0:6])
        # #si il y a un "il y a" dans la balise, il faut le virer
        # if balise_date.strip().lower()[0:6] == 'il y a':
        #     ma_date = balise_date[7:]
        # print(f"ma date après stripping : {balise_date} > {ma_date}")

        ans = re.search(r"\d+\s*a", ma_date)

        # trouver s'il y a un nombres* m[ois]
        mois = re.search('\d+\s*m', ma_date)

        # trouver s'il y a un nombre* s[emaines]
        semaines = re.search('\d+\s*s', ma_date)

        # trouver s'il y a un nombres* j[ours]
        jours = re.search('\d+\s*j', ma_date)

        # print(f"{balise_date} =  {ans} ans/ {jours} jours/ {mois} mois/ {semaines} semaines")

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

        # print(f"{ma_date} > ans/jours/mois = {ans}/{mois}/{jours}")

        date_en_jours = -1 * (float(ans) * 365 + float(mois) * 30.5 + float(semaines) * 7 + float(jours))
        # print(f"balise date il y a en sortie {date_en_jours}")

        return date_en_jours
    except ValueError:
        print(f"Erreur avec la date {balise_date}")
        return balise_date.strip()


def extraire_persos_de_texte(texte_persos, nom_doc, id_url, last_file_edit, derniere_modification_par, mon_gn,
                             verbal=False, pj: TypePerso = TypePerso.EST_PJ):
    print(f"Lecture de {nom_doc}")
    if len(texte_persos) < 800:
        print(f"fiche {nom_doc} avec {len(texte_persos)} caractères est vide")
        return  # dans ce cas c'est qu'on est en train de lite un template, qui fait 792 cars

    nom_perso_en_cours = re.sub(r"^\d+\s*-", '', nom_doc).strip()
    # print(f"nomDoc =_{nomDoc}_ nomPJ =_{nomPJ}_")
    # print(f"Personnage en cours d'importation : {nomPJ} avec {len(textePJ)} caractères")
    perso_en_cours = Personnage(nom=nom_perso_en_cours, url=id_url, derniere_edition_fichier=last_file_edit, pj=pj)
    perso_en_cours.modifie_par = derniere_modification_par
    mon_gn.dictPJs[id_url] = perso_en_cours

    texte_persos_low = texte_persos.lower()  # on passe en minuscule pour mieux trouver les chaines

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

    indexes = lecteurGoogle.identifier_sections_fiche(labels, texte_persos_low)

    # print(f"indexes : {indexes}")

    if indexes[REFERENT]["debut"] == -1:
        print("pas de référent avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.orgaReferent = texte_persos[indexes[REFERENT]["debut"]:indexes[REFERENT]["fin"]].splitlines()[
                                          0][
                                      len(REFERENT) + len(" : "):]

    if indexes[JOUEURV1]["debut"] == -1:
        if verbal:
            print("Pas de joueur 1 avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.joueurs['V1'] = texte_persos[indexes[JOUEURV1]["debut"]:indexes[JOUEURV1]["fin"]].splitlines()[
                                           0][
                                       len(JOUEURV1) + len(" : "):]

    if indexes[JOUEURV2]["debut"] == -1:
        if verbal:
            print("Pas de joueur 2 avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.joueurs['V2'] = texte_persos[indexes[JOUEURV2]["debut"]:indexes[JOUEURV2]["fin"]].splitlines()[
                                           0][
                                       len(JOUEURV1) + len(" : "):]

    if indexes[JOUEUSE1]["debut"] == -1:
        if verbal:
            print("Pas de joueuse 1 avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.joueurs['V1'] = texte_persos[indexes[JOUEUSE1]["debut"]:indexes[JOUEUSE1]["fin"]].splitlines()[
                                           0][
                                       len(JOUEURV1) + len(" : "):]

    if indexes[JOUEUSE2]["debut"] == -1:
        if verbal:
            print("Pas de joueuse 2 avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.joueurs['V2'] = texte_persos[indexes[JOUEUSE2]["debut"]:indexes[JOUEUSE2]["fin"]].splitlines()[
                                           0][
                                       len(JOUEURV1) + len(" : "):]

    if indexes[PITCH]["debut"] == -1:
        if verbal:
            print("Pas de pitch  avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.pitch = texte_persos[indexes[PITCH]["debut"]:indexes[PITCH]["fin"]].splitlines()[1:]

    if indexes[COSTUME]["debut"] == -1:
        if verbal:
            print("Pas d'indication costume avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.indicationsCostume = texte_persos[indexes[COSTUME]["debut"] + len(COSTUME) + len(" : "):
                                                         indexes[COSTUME]["fin"]]

    if indexes[FACTION1]["debut"] == -1:
        if verbal:
            print("Pas de faction 1 avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.factions.append(texte_persos[indexes[FACTION1]["debut"]:indexes[FACTION1]["fin"]].splitlines()[
                                           0][
                                       len(FACTION1) + len(" : "):])

    if indexes[FACTION2]["debut"] == -1:
        if verbal:
            print("Pas de faction 2 avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.factions.append(texte_persos[indexes[FACTION2]["debut"]:indexes[FACTION2]["fin"]].splitlines()[
                                           0][
                                       len(FACTION2) + len(" : "):])

    if indexes[BIO]["debut"] == -1:
        if verbal:
            print("Pas de BIO avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.description = texte_persos[indexes[BIO]["debut"]:
                                                  indexes[BIO]["fin"]].splitlines()[1:]

    if indexes[PSYCHO]["debut"] == -1:
        if verbal:
            print("Pas de psycho avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.concept = texte_persos[indexes[PSYCHO]["debut"]:
                                              indexes[PSYCHO]["fin"]].splitlines()[1:]

    if indexes[MOTIVATIONS]["debut"] == -1:
        if verbal:
            print("Pas de motivations avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.driver = texte_persos[indexes[MOTIVATIONS]["debut"]:indexes[MOTIVATIONS]["fin"]].splitlines()[1:]

    if indexes[CHRONOLOGIE]["debut"] == -1:
        if verbal:
            print("Pas de chronologie avec le perso " + nom_perso_en_cours)
    else:
        perso_en_cours.datesClefs = texte_persos[
                                    indexes[CHRONOLOGIE]["debut"]:indexes[CHRONOLOGIE]["fin"]].splitlines()[1:]

    if indexes[SCENES]["debut"] == -1:
        if verbal:
            print("Pas de scènes dans le perso " + nom_perso_en_cours)
    else:
        # print(f"début balise scène : {indexes[SCENES]['debut']}, fin balise scènes : {indexes[SCENES]['fin']} ")
        texte_scenes = texte_persos[indexes[SCENES]["debut"] + len(SCENES):indexes[SCENES]["fin"]]

        # print(f"ping j'ai trouvé la balise scènes, elle contient : {texteScenes}")
        texte2scenes(perso_en_cours, nom_perso_en_cours, texte_scenes, False)
        # for scene in perso_en_cours.scenes:
        #     print(f"Scene présente : {scene}")
        # print(f"rôles contenus dans {nomPJ} : {perso_en_cours.rolesContenus}")

    # rajouter les scènes en jeu après le tableau
    bottom_text = texte_persos.split("#####")[-1]
    perso_en_cours.textesAnnexes = bottom_text

    # et on enregistre la date de dernière mise à jour de l'intrigue
    perso_en_cours.lastProcessing = datetime.datetime.now()

    # print(f"perso à la fin de l'importation {perso_en_cours}")
    return perso_en_cours


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
        contenu_document = document.get('body').get('content')
        text = lecteurGoogle.read_structural_elements(contenu_document)
        text = text.replace('\v', '\n')  # pour nettoyer les backspace verticaux qui se glissent

    except HttpError as err:
        print(f'An error occurred: {err}')
        return

    if verbal:
        print(f"texte = {text}")

    # à ce stade, j'ai lu les factions et je peux dépouiller
    # print(f"clefs dictionnaire : {mon_GN.dictPJs.keys()}")
    lines = text.splitlines()
    noms_persos = list(mon_GN.noms_pjs()) + list(mon_GN.noms_pnjs())
    # on crée un dictionnaire qui permettra de retrouver les id en fonction des noms
    temp_dict_pjs = {mon_GN.dictPJs[x].nom: x for x in mon_GN.dictPJs}
    temp_dict_pnjs = {mon_GN.dictPNJs[x].nom: x for x in mon_GN.dictPNJs}

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
                # print(f"score durant lecture faction pour {perso_name} = {score}")
                if verbal:
                    # print(f"pour le nom {perso_name} lu dans la faction {current_faction.nom}, j'ai {score}")
                    pass
                if temp_dict_pjs.get(score[0]):
                    personnages_a_ajouter = mon_GN.dictPJs[temp_dict_pjs.get(score[0])]
                else:
                    personnages_a_ajouter = mon_GN.dictPNJs[temp_dict_pnjs.get(score[0])]

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
        if doc.get('isWriting'):
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
        if len(requests) != 0:
            # execute the requests
            result = service.documents().batchUpdate(documentId=file_id, body={'requests': requests}).execute()
            return result
        else:
            return None
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
        if verbal:
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


def ecrire_table_google_sheets(api_sheets, table, spreadsheet_id, feuille=None):
    ma_range = 'A1'
    if feuille is not None:
        try:
            ma_range = f'{feuille}!A1'
            api_sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": feuille
                            }
                        }
                    }
                ]
            }).execute()
        except HttpError as error:
            print(f'An error occurred: {error}')

    # def ecrire_table_google_sheets(api_doc, df, spreadsheet_id):
    try:
        body = {'range': ma_range,
                'values': table,
                'majorDimension': 'ROWS'
                }

        # print(f"api_doc = {api_doc}")

        # result = api_sheets.spreadsheets().values().update(
        #     spreadsheetId=spreadsheet_id, range='A1',
        #     valueInputOption='RAW', body=body).execute()

        result = api_sheets.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=ma_range,
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
                elif text.startswith("Info"):
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
                                            'blue': 1.0,
                                            'green': 0.0,
                                            'red': 0.0
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
                elif text.endswith("voici les intrigues avec des soucis dans leurs tableaux de persos \n"):
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

        if len(requests) != 0:
            # Envoie toutes les requêtes en une seule fois pour mettre à jour le document
            result = api_doc.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
        else:
            return None

    except:
        result = None

    return result


# def reconstituer_tableau(texte_lu, separateur_ligne="¤¤¤¤¤", separateur_colonne="¤¤¤"):
#     first_hash_index = texte_lu.find(separateur_ligne)
#     last_hash_index = texte_lu.rfind(separateur_ligne)
#     if first_hash_index == -1 or last_hash_index == -1:
#         return None
#
#     texte_tableau = texte_lu[first_hash_index:last_hash_index + 1]
#     lignes = texte_tableau.split(separateur_ligne)
#     to_return = []
#     for ligne in lignes[1:]:
#         to_return.append(ligne.split(separateur_colonne))
#
#     return to_return

def reconstituer_tableau(texte_lu: str, separateur_ligne="¤¤¤¤¤", separateur_colonne="¤¤¤"):
    first_hash_index = texte_lu.find(separateur_ligne)
    last_hash_index = texte_lu.rfind(separateur_ligne)
    if first_hash_index == -1 or last_hash_index == -1:
        return None, None

    texte_tableau = texte_lu[first_hash_index:last_hash_index + 1]
    lignes = texte_tableau.split(separateur_ligne)
    to_return = []
    for ligne in lignes[1:]:
        to_return.append(ligne.split(separateur_colonne))

    num_columns = len(to_return[0]) if to_return else None
    return to_return, num_columns


def extraire_evenement_de_texte(texte_evenement, nom_evenement, id_url, lastFileEdit, derniere_modification_par, monGN,
                                verbal=False):
    # Créer un nouvel évènement

    # lire les sections dans le fichier

    # pour chaque section, l'attribuer directement
    # ou bien utiliser la lecture de tableau pour la traiter (potentiellement via un dictionnaire)
    pass
