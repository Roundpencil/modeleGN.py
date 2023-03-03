import argparse
import configparser
import csv
import sys

import extraireTexteDeGoogleDoc
import lecteurGoogle
import modeleGN
from modeleGN import *
from MAGnet_lib import *



def main():
    sys.setrecursionlimit(5000)  # mis en place pour prévenir pickle de planter

    parser = argparse.ArgumentParser()

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("--intrigue", "-i", type=str, default="-01", help="si une seule intrigue doit être lue")
    group1.add_argument("--allintrigues", "-ai", action="store_true",
                        help="si on veut reparcourir toutes les intrigues")

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("--personnage", "-p", type=str, default="-01", help="si un seul personnage doit être lu")
    group2.add_argument("--allpjs", "-ap", action="store_true", help="si on veut reparcourir tous les pjs")

    parser.add_argument("--initfile", "-f", type=str, default="config.ini",
                        help="pour spécifier le fichier d'init à charger")
    parser.add_argument("--nofichiererreurs", "-nfe", action="store_true",
                        help="pour ne pas générer la table des intrigues")
    parser.add_argument("--notableintrigues", "-nti", action="store_true",
                        help="pour ne pas générer la table des intrigues")
    parser.add_argument("--noexportdrive", "-ned", action="store_true", help="pour ne pas provoquer l'export drive")
    parser.add_argument("--nochangelog", "-ncl", action="store_true",
                        help="pour ne pas provoquer la création des changelogs")
    parser.add_argument("--init", "-in", action="store_true", help="fait que la fonction self.load n'est pas appelée")
    parser.add_argument("--nosave", "-ns", action="store_true", help="fait que la focntion GN.save n'est pas appelée")
    parser.add_argument("--verbal", "-v", action="store_true", help="si on veut afficher toutes les erreurs")

    args = parser.parse_args()

    # init configuration
    config = configparser.ConfigParser()
    # config.read('config.ini')
    config.read(args.initfile)

    try:
        dossier_intrigues = config.get('dossiers', 'intrigues').split(',')

        dossier_pjs = [config.get("dossiers", key)
                       for key in config.options("dossiers") if key.startswith("base_persos")]

        id_factions = config.get('dossiers', 'id_factions')
        dossier_output_squelettes_pjs = config.get('dossiers', 'dossier_output_squelettes_pjs')

        noms_persos = [nom_p.strip()
                       for nom_p in config.get('pjs_a_importer', 'noms_persos').split(',')]

        nom_fichier_pnjs = config.get('pjs_a_importer', 'nom_fichier_pnjs')
        # print(nom_fichier_pnjs)
        association_auto = config.getboolean('globaux', 'association_auto')
        type_fiche = config.get('globaux', 'type_fiche')

        nom_fichier_sauvegarde = config.get('sauvegarde', 'nom_fichier_sauvegarde')
    except configparser.Error as e:
        # Erreur lors de la lecture d'un paramètre dans le fichier de configuration
        print("Erreur lors de la lecture du fichier de configuration : {}".format(e))
        return

    monGN = GN(folderIntriguesID=dossier_intrigues,
               folderPJID=dossier_pjs,
               id_factions=id_factions,
               dossier_outputs_drive=dossier_output_squelettes_pjs)

    # print(f"1 - pnj dans ce GN : {gn.liste_noms_pnjs()}")

    charger_PNJs(monGN, nom_fichier_pnjs)

    # print(f"2 - pnj dans ce GN : {gn.liste_noms_pnjs()}")

    try:
        if not args.init:
            monGN = GN.load(nom_fichier_sauvegarde)
            # print(f"Derniere version avant mise à jour : {gn.oldestUpdateIntrigue}")
            # gn.id_factions = "1lDKglitWeg6RsybhLgNsPUa-DqN5POPyOpIo2u9VvvA"
            # ajouter_champs_pour_gerer_456_colonnes(gn)
            monGN.dossier_outputs_drive = dossier_output_squelettes_pjs
    except:
        print(f"impossible d'ouvrir {nom_fichier_sauvegarde} : ré-lecture à zéro de toutes les infos")

    # print(f"3 - pnj dans ce GN : {gn.liste_noms_pnjs()}")
    apiDrive, apiDoc, apiSheets = lecteurGoogle.creer_lecteurs_google_apis()

    monGN.effacer_personnages_forces()

    # extraire_texte_de_google_doc.extraire_intrigues(gn, api_doc=api_doc, api_doc=api_doc, single_test="-01")
    # extraire_texte_de_google_doc.extraire_pjs(gn, api_doc=api_doc, api_doc=api_doc, single_test="-01")

    extraireTexteDeGoogleDoc.extraire_intrigues(monGN, api_drive=apiDrive, api_doc=apiDoc, singletest=args.intrigue,
                                                fast=(not args.allintrigues))
    extraireTexteDeGoogleDoc.extraire_pjs(monGN, api_drive=apiDrive, api_doc=apiDoc, singletest=args.perso,
                                          fast=(not args.allpjs))
    extraireTexteDeGoogleDoc.extraire_pjs(monGN, api_drive=apiDrive, api_doc=apiDoc, singletest=args.perso,
                                          fast=(not args.allpjs))

    extraireTexteDeGoogleDoc.extraire_factions(monGN, apiDoc=apiDoc)
    # extraire_texte_de_google_doc.lire_factions_depuis_fichier(gn, fichier_faction)

    monGN.forcer_import_pjs(noms_persos)
    monGN.rebuild_links(args.verbal)

    if not args.nosave:
        monGN.save(nom_fichier_sauvegarde)

    # todo: appel dans la foulée de dedupe PNJ pour faire le ménage?
    # todo : utiliser l'objet CSV pour générer les CSV

    # todo : passer la gestion des dates via un objet date time, et ajouter une variable avec la date du GN (0 par défaut)

    # todo : ajouter des fiches relations, qui décrivent l'évolution des relations entre les personnages,
    #  et qui devraient servir de base pour les lire

    # todo générer les relations lues dans un tableau des relations



    print("****************************")
    print("****************************")
    print("****************************")
    prefixeFichiers = str(datetime.date.today())
    print("*********toutesleserreurs*******************")
    if not args.nofichiererreurs:
        texte_erreurs = lister_erreurs(monGN, prefixeFichiers)
        ecrire_erreurs_dans_drive(texte_erreurs, apiDoc, apiDrive, dossier_output_squelettes_pjs)

    print("*********touslesquelettes*******************")
    if not args.noexportdrive:
        generer_squelettes_dans_drive(monGN, apiDoc, apiDrive, pj=True)
        generer_squelettes_dans_drive(monGN, apiDoc, apiDrive, pj=False)

    ecrire_squelettes_localement(monGN, prefixeFichiers)
    tousLesSquelettesPNJ(monGN, prefixeFichiers)
    print("*******dumpallscenes*********************")
    # dumpAllScenes(gn)

    print("*******changelog*********************")
    if not args.nochangelog:
        generer_tableau_changelog_sur_drive(monGN, apiDrive, apiSheets, dossier_output_squelettes_pjs)
        generer_changelog(monGN, prefixeFichiers, nb_jours=3)
        generer_changelog(monGN, prefixeFichiers, nb_jours=4)

    print("******* statut intrigues *********************")
    if not args.notableintrigues:
        creer_table_intrigues_sur_drive(monGN, apiSheets, apiDrive, dossier_output_squelettes_pjs)

    # ajouter_champs_modifie_par(gn, nom_fichier_sauvegarde)
    # trier_scenes(gn)
    # listerTrierPersos(gn)
    # #écrit toutes les scènes qui sont dans le GN, sans ordre particulier
    # dumpAllScenes(gn)

    ## pour avoir tous les objets du jeu :
    # generecsvobjets(gn)

    # squelettePerso(gn, "Kyle Talus")
    # listerRolesPerso(gn, "Greeta")
    # listerPNJs(gn)
    # genererCsvPNJs(gn, verbal=False)
    # genererCsvObjets(gn)

    # #lister les correspondaces entre les roles et les noms standards
    # mesroles = tousLesRoles(gn)
    # fuzzyWuzzyme(mesroles, noms_persos)

    # print(normaliserNomsPNJs(gn))
    # #génération d'un premier tableau de noms de PNJs à partir de ce qu'on lit dans les intrigues
    # nomsPNSnormalisés = normaliserNomsPNJs(gn)
    # print([ nomsPNSnormalisés[k][0] for k in nomsPNSnormalisés])
    # generer_liste_pnj_dedup(gn)

    # print(getAllRole(GN))

    # afficherLesPersos(gn)
    # afficherDatesScenes(gn)
    # genererCsvOrgaIntrigue(gn)
    # listerLesRoles(gn)

    # listerDatesIntrigues(gn)

    ## test de la fonction d'effaçage'
    # testEffacerIntrigue(gn)

    # print(" l'intrigue la plus ancienne est {0}, c'est {1}, maj : {2}".format(gn.idOldestUpdate, gn.intrigues[gn.idOldestUpdate], gn.oldestUpdate))

    # test de la focntion de rapprochement des PNJs
    # fuzzyWuzzyme(listerPNJs(gn), nomsPNJs)

    # #test de la focntion de lecture des PJs
    # dumpPersosLus(gn)
    # dumpSortedPersos(gn)

    # genererTableauIntrigues(gn)


def ajouterPersosSansFiche(monGN, nomspersos):
    monGN.forcer_import_pjs(nomspersos)

    print(f"fin de l'ajout des personnages sans fiche. j'ai {len(monGN.dictPJs.values())} personnages en tout")


def afficherLesPersos(monGN):
    for intrigue in monGN.intrigues:
        # print("propriétaire intrigue : {0} : {1}".format(intrigue.nom, intrigue.orga_referent))
        # for clef in intrigue.roles.keys():
        #     print(clef + " a pour nom complet : " + str(intrigue.roles[clef].nom))

        for role in intrigue.rolesContenus.values():
            print("pour le rôle " + role.nom)
            print("Personnage : " + role.personnage.nom)
            texteScenes = ""
            for scene in role.scenes:
                texteScenes += scene.titre + "; "
            print("scenes : " + texteScenes)


def afficherDatesScenes(monGN):
    for intrigue in monGN.intrigues:
        for scene in intrigue.scenes:
            print("scène : {0} / date : {1} > {2}".format(scene.titre, scene.date, scene.get_formatted_date()))


def genererCsvOrgaIntrigue(monGN):
    for intrigue in monGN.intrigues:
        print("{0};{1}".format(intrigue.nom, intrigue.orgaReferent))


def listerLesRoles(monGN):
    for intrigue in monGN.intrigues:
        print(f"intrigue : {intrigue.nom} - url : {intrigue.url}")
        for role in intrigue.rolesContenus.values():
            print(str(role))


def listerDatesIntrigues(monGN):
    for intrigue in monGN.intrigues.values():
        print("{0} - {1} - {2}".format(intrigue.nom, intrigue.lastProcessing, intrigue.url))


# def listerRolesPerso(gn, nomPerso):
#     nomPerso = process.extractOne(nomPerso, noms_persos)[0]
#     for personnage in gn.dictPJs.values():
#         if personnage.nom == nomPerso:
#             # print(f"{nomPerso} trouvé")
#             for role in personnage.rolesContenus:
#                 print(role)
#             break


# def ecrire_squelettes_localement(gn, prefixe=None):
#     toutesScenes = ""
#     for personnage in gn.dictPJs.values():
#         toutesScenes += f"Début du squelette pour {personnage.nom} (Orga Référent : {personnage.orga_referent}) : \n"
#         toutesScenes += f"résumé de la bio : \n"
#         for item in personnage.description:
#             toutesScenes += f"{item} \n"
#         toutesScenes += f"Psychologie : "
#         for item in personnage.concept:
#             toutesScenes += f"{item} \n"
#         toutesScenes += f"Motivations et objectifs : \n"
#         for item in personnage.driver:
#             toutesScenes += f"{item} \n"
#         toutesScenes += f"Chronologie : \n "
#         for item in personnage.dates_clefs:
#             toutesScenes += f"{item} \n"
#         toutesScenes += "\n *** Scenes associées : *** \n"
#
#         mesScenes = []
#         for role in personnage.roles:
#             for scene in role.scenes:
#                 # print(f"{scene.titre} trouvée")
#                 mesScenes.append(scene)
#
#         # for scene in personnage.scenes:
#         #     mesScenes.append(scene)
#
#         # print(f"{nomPerso} trouvé")
#         mesScenes = Scene.trier_scenes(mesScenes)
#         for scene in mesScenes:
#             # print(scene)
#             toutesScenes += str(scene) + '\n'
#         toutesScenes += '****************************************************** \n'
#
#         # print('****************************************************** \n')
#     # print(toutesScenes)
#     if prefixe is not None:
#         with open(prefixe + ' - squelettes.txt', 'w', encoding="utf-8") as f:
#             f.write(toutesScenes)
#             f.close()
#
#     return toutesScenes


def squelettes_persos_en_kit(monGN):
    squelettes_persos = {}
    for perso in monGN.dictPJs.values():
        texte_intro = ""
        texte_intro += f"Début du squelette pour {perso.nom} (Orga Référent : {perso.orgaReferent}) : \n"
        texte_intro += f"résumé de la bio : \n"
        for item in perso.description:
            texte_intro += f"{item} \n"
        texte_intro += f"Psychologie : "
        for item in perso.concept:
            texte_intro += f"{item} \n"
        texte_intro += f"Motivations et objectifs : \n"
        for item in perso.driver:
            texte_intro += f"{item} \n"
        texte_intro += f"Chronologie : \n "
        for item in perso.datesClefs:
            texte_intro += f"{item} \n"
        texte_intro += "\n *** Scenes associées : *** \n"

        mes_scenes = []
        for role in perso.roles:
            for scene in role.scenes:
                # print(f"{scene.titre} trouvée")
                mes_scenes.append(scene)

        mes_scenes = Scene.trier_scenes(mes_scenes)
        # for scene in mesScenes:
        #     # print(scene)
        #     texte_intro += str(scene) + '\n'
        texte_intro += '****************************************************** \n'
        # squelettes_persos[personnage.nom] = dict()
        # squelettes_persos[personnage.nom]['intro'] = texte_intro
        # squelettes_persos[personnage.nom]['scenes'] = mes_scenes

        squelettes_persos[perso.nom] = {'intro': texte_intro, 'scenes': mes_scenes}
    return squelettes_persos


def reverse_generer_squelettes_dans_drive(mon_GN: GN, api_doc, api_drive):
    d = squelettes_persos_en_kit(mon_GN)
    for nom_perso in d:
        # créer le fichier et récupérer l'ID
        nom_fichier = f'{nom_perso} - squelette au {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}'
        id = extraireTexteDeGoogleDoc.add_doc(api_drive, nom_fichier, mon_GN.dossier_outputs_drive)

        # ajouter le texte de l'intro
        texte_intro = d[nom_perso]["intro"]
        extraireTexteDeGoogleDoc.write_to_doc(api_doc, id, texte_intro, titre=False)

        # ajouter toutes les scènes
        for scene in d[nom_perso]["scenes"]:
            description_scene = scene.dict_text()

            # ajouter le titre
            extraireTexteDeGoogleDoc.write_to_doc(api_doc, id, description_scene["titre"], titre=True)
            # ajouter les entetes
            extraireTexteDeGoogleDoc.write_to_doc(api_doc, id, description_scene["en-tete"], titre=False)
            # ajouter le texte
            extraireTexteDeGoogleDoc.write_to_doc(api_doc, id, description_scene["corps"], titre=True)


def tousLesSquelettesPNJ(monGN: GN, prefixe):
    toutesScenes = ""
    for perso in monGN.dictPNJs.values():
        toutesScenes += f"Début du squelette pour {perso.nom} (Orga Référent : {perso.orgaReferent}) : \n"
        toutesScenes += f"résumé de la bio : \n {perso.description} \n"
        toutesScenes += f"Psychologie : \n {perso.concept} \n"
        toutesScenes += f"Motivations et objectifs : \n {perso.driver} \n"
        toutesScenes += f"Chronologie : \n {perso.datesClefs} \n"
        toutesScenes += "\nScenes associées : \n"

        mesScenes = []
        for role in perso.roles:
            for scene in role.scenes:
                # print(f"{scene.titre} trouvée")
                mesScenes.append(scene)

        # for scene in personnage.scenes:
        #     mesScenes.append(scene)

        # print(f"{nomPerso} trouvé")
        mesScenes = Scene.trier_scenes(mesScenes)
        for scene in mesScenes:
            # print(scene)
            toutesScenes += str(scene) + '\n'
        toutesScenes += '****************************************************** \n'

        # print('****************************************************** \n')
    # print(toutesScenes)
    if prefixe is not None:
        with open(prefixe + ' - squelettes PNJs.txt', 'w', encoding="utf-8") as f:
            f.write(toutesScenes)
            f.close()

    return toutesScenes





# def squelettePerso(gn, nomPerso):
#     mesScenes = []
#     nomPerso = process.extractOne(nomPerso, noms_persos)[0]
#     for personnage in gn.dictPJs.values():
#         if personnage.nom == nomPerso:
#             # print(f"{nomPerso} trouvé")
#             for role in personnage.rolesContenus:
#                 for scene in role.scenes:
#                     # print(f"{scene.titre} trouvée")
#                     mesScenes.append(scene)
#             break
#
#     # print(f"{nomPerso} trouvé")
#     mesScenes = Scene.trier_scenes(mesScenes)
#     for scene in mesScenes:
#         print(scene)


def listerPNJs(monGN):
    toReturn = []
    for intrigue in monGN.intrigues.values():
        for role in intrigue.rolesContenus.values():
            if role.est_un_pnj():
                print(role)
                toReturn.append(role.nom)
    return toReturn


# def genererCsvPNJs(gn: GN, verbal=False):
#     liste_noms_pnjs = gn.liste_noms_pnjs()
#     output = "nom PNJ;description;type_pj;niveau implication;details intervention;intrigue;" \
#              "nom dans l'intrigue;indice de confiance normalisation\n"
#     for intrigue in gn.intrigues.values():
#         for role in intrigue.rolesContenus.values():
#             if role.est_un_pnj():
#                 nompnj = role.nom.replace('\n', chr(10))
#                 description = role.description.replace('\n', "***")
#                 niveau_implication = role.niveau_implication.replace('\n', chr(10))
#                 perimetre_intervention = role.perimetre_intervention.replace('\n', chr(10))
#                 score = process.extractOne(nompnj, liste_noms_pnjs)
#                 typeDansGN = gn.dictPNJs[score[0]].pj
#                 output += f"{score[0]};" \
#                           f"{description};" \
#                           f"{string_type_pj(typeDansGN)};" \
#                           f"{niveau_implication};" \
#                           f"{perimetre_intervention};" \
#                           f"{intrigue.nom}; " \
#                           f"{nompnj}; " \
#                           f"{score[1]}" \
#                           "\n"
#     if verbal:
#         print(output)


def genererCsvObjets(monGN):
    print("description;Avec FX?;FX;Débute Où?;fourni par Qui?;utilisé où?")
    for intrigue in monGN.intrigues.values():
        for objet in intrigue.objets:
            description = objet.description.replace('\n', "***")
            avecfx = objet.rfid
            fx = objet.specialEffect.replace('\n', "***")
            debuteou = objet.emplacementDebut.replace('\n', "***")
            fournipar = objet.fourniParJoueur.replace('\n', "***")
            utiliseou = [x.nom for x in objet.inIntrigues]
            print(f"{description};"
                  f"{avecfx};"
                  f"{fx};"
                  f"{debuteou};"
                  f"{fournipar};"
                  f"{utiliseou}")


def tousLesRoles(monGN):
    tousLesRoles = []
    print(f"dernière modification GN : {monGN.oldestUpdate}/{monGN.intrigues[monGN.oldestUpdatedIntrigue]}")
    for intrigue in monGN.intrigues.values():
        tousLesRoles.extend(
            role.nom
            for role in intrigue.rolesContenus.values()
            if not modeleGN.est_un_pnj(role.pj)
            and role.pj != TypePerso.EST_REROLL
        )
        # for role in intrigue.rolesContenus.values():
        #     if not modeleGN.est_un_pnj(role.pj) and role.pj != TypePerso.EST_REROLL:
        #         tousLesRoles.append(role.nom)
        # # print(f"date dernière MAJ {intrigue.dateModification}")

            # print(f"date dernière MAJ {intrigue.dateModification}")
    return tousLesRoles


def fuzzyWuzzyme(input, choices):
    # input.sort()
    toReturn = []
    input = set(input)
    for element in input:
        # scores = process.extract(element, choices, limit=5)
        scores = process.extractOne(element, choices)
        toReturn.append([element, scores[0], scores[1]])
    toReturn.sort(key=lambda x: x[2])

    for element in toReturn:
        print(f"fuzzy : {element}")


def normaliserNomsPNJs(monGN):
    nomsPNJs = []
    nomsNormalises = dict()
    for intrigue in monGN.intrigues.values():
        for role in intrigue.rolesContenus.values():
            if role.est_un_pnj():
                nomsPNJs.append(role.nom)
    nomsPNJs = list(set(nomsPNJs))
    print("Nom D'origine ;Meilleur choix;Confiance")
    for i in range(len(nomsPNJs)):
        choices = process.extract(nomsPNJs[i], nomsPNJs, limit=2)
        print(f"{choices[0][0]};{choices[1][0]};{choices[1][1]}")

        # le premier choix sera toujours de 100, vu qu'il se sera trouvé lui-même
        # si le second choix est > 90 il y a de fortes chances qu'on ait le même personnage
        # sinon on ne prend pas de risques et on garde le meme personnage
        if choices[1][1] > 90:
            nomsNormalises[nomsPNJs[i]] = [choices[1][0], choices[1][1]]
        else:
            nomsNormalises[nomsPNJs[i]] = [choices[0][0], choices[0][1]]

    return nomsNormalises


def generecsvobjets(monGn):
    for intrigue in monGn.intrigues.values():
        for objet in intrigue.objets:
            print(
                f"{intrigue.nom};{intrigue.orgaReferent};{objet.description};{objet.fourniParJoueur};{objet.fourniParJoueur};{objet.rfid};{objet.specialEffect};")


def dumpPersosLus(monGN):
    for pj in monGN.dictPJs.values():
        # if pj.url != "":
        print(pj)


# def dumpSortedPersos(gn):
#     tousLesPersos = [x.nom for x in gn.dictPJs.values()]
#     tousLesPersos.sort()
#     print(tousLesPersos)
#     print(len(tousLesPersos))
#     print(len(noms_persos))


def dumpAllScenes(monGN):
    for intrigue in monGN.intrigues.values():
        print(f"{str(intrigue)}")
        print(f" a {len(intrigue.scenes)} scenes")

        mesScenes = dict()
        for scene in intrigue.scenes:
            print(f"titre / longdigit : {scene.titre} / {scene.getLongdigitsDate()}")
            mesScenes[str(scene.getLongdigitsDate())] = scene
        print(f"toutes les scènes : {mesScenes}")

        for key in sorted([str(x) for x in mesScenes.keys()], reverse=True):
            print(mesScenes[key])


def trierScenes(monGN):
    # for intrigue in gn.intrigues.values():
    #     print(f"{str(intrigue)}")
    #     print(f" a {len(intrigue.scenes)} scenes")
    #     scenesTriees = sorted(intrigue.scenes, key=lambda scene: scene.getLongdigitsDate(), reverse=True)
    #     for s in scenesTriees:
    #         print(s)

    for intrigue in monGN.intrigues.values():
        print()
        print()
        print(f"intrigue {intrigue.nom} : ")
        triee = intrigue.get_scenes_triees()
        for scene in triee:
            print(scene)


def listerTrierPersos(monGN):
    touspj = []
    for pj in monGN.dictPJs.values():
        touspj.append(pj.nom)
    touspj.sort()
    for pj in touspj:
        print(pj)


def genererTableauIntrigues(monGN):
    print("Intrigue; Orga Référent")
    toPrint = monGN.intrigues.values()
    toPrint = sorted(toPrint, key=lambda x: x.nom)
    for intrigue in toPrint:
        print(f"{intrigue.nom};{intrigue.orgaReferent.strip()};")




    # rolesSansScenes = []
    # for role in intrigue.roles.values():
    #     if len(role.scenes()) < 1:
    #         rolesSansScenes.append(role)
    #
    # if len(rolesSansScenes) > 0:
    #     print("Roles sans Scènes : ")
    #     for role in rolesSansScenes:
    #         print(role.nom)


# à voir ce qu'on fait de cette fonction
def lire_factions_depuis_fichier(mon_GN: GN, fichier: str):
    try:
        with open(fichier, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Fichier introuvable : {fichier}")
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
                try:
                    current_faction.ajouter_personnage(perso_name)
                except Exception as e:
                    print(f"Impossible d'ajouter le personnage {perso_name} : {e}")


def split_text_reverse(text: str, taille_chunk: int):
    lines = text.split("\n")[::-1]
    for i in range(len(lines) - 1, -1, -1 * taille_chunk):
        yield "\n".join(lines[i - 1000 if i - taille_chunk >= 0 else 0:i])


def ajouter_champs_modifie_par(mon_gn: GN, nom_fichier=None):
    for conteneur in list(mon_gn.intrigues.values()) + list(mon_gn.dictPJs.values()):
        conteneur.modifie_par = ""
        for scene in conteneur.scenes:
            scene.modifie_par = ""

    if nom_fichier is not None:
        mon_gn.save(nom_fichier)
        print(f"fichier sauvegardé sous {nom_fichier}")


# ***************** début de l'ajout des fonctions pour faire tourner la GUI ***********************************


# def charger_fichier_init(fichier_init: str):
#     # init configuration
#     config = configparser.ConfigParser()
#     config.read(fichier_init)
#     resultat_ok = False
#     dict_config = dict()
#     try:
#         dossier_intrigues = config.get('dossiers', 'intrigues').split(',')
#
#         dossiers_pjs = [config.get("dossiers", key)
#                        for key in config.options("dossiers") if key.startswith("base_persos")]
#
#         id_factions = config.get('dossiers', 'id_factions')
#         dossier_output_squelettes_pjs = config.get('dossiers', 'dossier_output_squelettes_pjs')
#
#         noms_persos = [nom_p.strip()
#                        for nom_p in config.get('pjs_a_importer', 'noms_persos').split(',')]
#
#         nom_fichier_pnjs = config.get('pjs_a_importer', 'nom_fichier_pnjs')
#         # print(nom_fichier_pnjs)
#         association_auto = config.getboolean('globaux', 'association_auto')
#         type_fiche = config.get('globaux', 'type_fiche')
#
#         nom_fichier_sauvegarde = config.get('sauvegarde', 'nom_fichier_sauvegarde')
#         resultat_ok = True
#     except configparser.Error as e:
#         # Erreur lors de la lecture d'un paramètre dans le fichier de configuration
#         print("Erreur lors de la lecture du fichier de configuration : {}".format(e))
#         return
#     return dossier_intrigues, dossiers_pjs, id_factions, dossier_output_squelettes_pjs, \
#            noms_persos, nom_fichier_pnjs, association_auto, type_fiche, nom_fichier_sauvegarde, resultat_ok

# def charger_PNJs(self, chemin_fichier):
#     try:
#         with open(chemin_fichier, 'r') as f:
#             for ligne in f:
#                 nom = ligne.strip()
#                 self.dictPNJs[nom] = Personnage(nom=nom, forced=True, pj=EST_PNJ_HORS_JEU)
#                 # print(f"{self.dictPNJs[nom]}")
#     except FileNotFoundError:
#         print(f"Le fichier {chemin_fichier} n'a pas été trouvé.")

def ajouter_champs_pour_gerer_faction(gn:GN):
    for intrigue in gn.intrigues.values():
        for scene in intrigue.scenes:
            scene.nom_factions = set()
            yop = vars(scene)
            print(f"yop = {yop}")
        for role in intrigue.rolesContenus.values():
            role.issu_dune_faction = False


def ajouter_champs_pour_gerer_456_colonnes(gn:GN):
    for intrigue in gn.intrigues.values():
        for role in intrigue.rolesContenus.values():
            role.pip_globaux = 0
            role.pip_total = 0



if __name__ == '__main__':
    main()


def convertir_erreur_manager(gn:GN):
    print(gn.dictPJs)

    for obj in list(gn.dictPJs.values())+list(gn.dictPNJs.values())+list(gn.intrigues.values()):
        tmp = obj.error_log
        obj.error_log = ErreurManager()
        for erreur in tmp.erreurs:
            niveau = 0
            origine = 0
            for n in ErreurManager.NIVEAUX:
                if n == erreur.niveau:
                    niveau = n
            for o in ErreurManager.ORIGINES:
                if o == erreur.origine:
                    origine = n

            obj.error_log.ajouter_erreur(niveau, erreur.texte, origine)
        print(f"{obj.nom} a été mis à jour")
    # def convertir_erreur_manager(liste_anciens_erreur_manager):
    #     nouveaux_erreur_manager = []
    #     for ancien_erreur_manager in liste_anciens_erreur_manager:
    #         nouveau_erreur_manager = ErreurManagerV2()
    #         nouveau_erreur_manager.erreurs = [ErreurManagerV2.ErreurAssociation(
    #             erreur.niveau,
    #             erreur.texte,
    #             erreur.origine
    #         ) for erreur in ancien_erreur_manager.erreurs]
    #         nouveaux_erreur_manager.append(nouveau_erreur_manager)
    #         print(f"{obj.nom} a été mis à jour")
    #     return nouveaux_erreur_manager



def lister_rerolls(gn:GN):
    for conteneur in list(gn.dictPJs.values()) \
                     + list(gn.dictPNJs.values()) \
                     + list(gn.intrigues.values()):
        for scene in conteneur.scenes:
            for role in scene.roles:
                if role.pj == TypePerso.EST_REROLL:
                    print(f"{role.nom} est un reroll")
