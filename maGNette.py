import argparse
import configparser
import csv
import sys

import extraireTexteDeGoogleDoc
import lecteurGoogle
import modeleGN
from modeleGN import *


def main():
    sys.setrecursionlimit(5000)  # mis en place pour prévenir pickle de planter

    parser = argparse.ArgumentParser()

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("-intrigue", type=str, default="-01", help="si une seule intrigue doit être lue")
    group1.add_argument("-allintrigues", action="store_true", help="si on veut reparcourir toutes les intrigues")

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("-perso", type=str, default="-01", help="si un seul perso doit être lu")
    group2.add_argument("-allpjs", action="store_true", help="si on veut reparcourir tous les pjs")

    parser.add_argument("-initfile", type=str, default="config.init", help="pour spécifier le fichier d'init à charger")
    parser.add_argument("-nofichiererreurs", action="store_true", help="pour ne pas générer la table des intrigues")
    parser.add_argument("-notableintrigues", action="store_true", help="pour ne pas générer la table des intrigues")
    parser.add_argument("-noexportdrive", action="store_true", help="pour ne pas provoquer l'export drive")
    parser.add_argument("-nochangelog", action="store_true", help="pour ne pas provoquer la création des changelogs")
    parser.add_argument("-init", action="store_true", help="fait que la fonction gn.load n'est pas appelée")
    parser.add_argument("-nosave", action="store_true", help="fait que la focntion GN.save n'est pas appelée")
    parser.add_argument("-verbal", action="store_true", help="si on veut afficher toutes les erreurs")

    args = parser.parse_args()

    # init configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

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
               fichier_factions=id_factions,
               dossier_outputs_drive=dossier_output_squelettes_pjs)

    # print(f"1 - pnj dans ce GN : {mon_gn.noms_pnjs()}")

    charger_PNJs(monGN, nom_fichier_pnjs)

    # print(f"2 - pnj dans ce GN : {mon_gn.noms_pnjs()}")

    try:
        if not args.init:
            monGN = GN.load(nom_fichier_sauvegarde)
            # print(f"Derniere version avant mise à jour : {mon_gn.oldestUpdateIntrigue}")
            # mon_gn.fichier_factions = "1lDKglitWeg6RsybhLgNsPUa-DqN5POPyOpIo2u9VvvA"
            monGN.dossier_outputs_drive = dossier_output_squelettes_pjs
    except:
        print(f"impossible d'ouvrir {nom_fichier_sauvegarde} : ré-lecture à zéro de toutes les infos")

    # print(f"3 - pnj dans ce GN : {mon_gn.noms_pnjs()}")

    apiDrive, apiDoc, apiSheets = lecteurGoogle.creer_lecteurs_google_apis()

    monGN.effacer_personnages_forces()

    # extraireTexteDeGoogleDoc.extraireIntrigues(mon_gn, api_doc=api_doc, api_doc=api_doc, singletest="-01")
    # extraireTexteDeGoogleDoc.extrairePJs(mon_gn, api_doc=api_doc, api_doc=api_doc, singletest="-01")

    extraireTexteDeGoogleDoc.extraireIntrigues(monGN, apiDrive=apiDrive, apiDoc=apiDoc, singletest=args.intrigue,
                                               fast=(not args.allintrigues))
    extraireTexteDeGoogleDoc.extrairePJs(monGN, apiDrive=apiDrive, apiDoc=apiDoc, singletest=args.perso,
                                         fast=(not args.allpjs))
    extraireTexteDeGoogleDoc.extraire_factions(monGN, apiDoc=apiDoc)
    # extraireTexteDeGoogleDoc.lire_factions_depuis_fichier(mon_gn, fichier_faction)

    monGN.forcerImportPersos(noms_persos)
    monGN.rebuildLinks(args.verbal)

    if not args.nosave:
        monGN.save(nom_fichier_sauvegarde)

    # todo: appel dans la foulée de dedupe PNJ pour faire le ménage?
    # todo : utiliser l'objet CSV pour générer les CSV

    # todo : passer la gestion des dates via un objet date time, et ajouter une variable avec la date du GN (0 par défaut)

    # todo : ajouter des fiches relations, qui décrivent l'évolution des relations entre les personnages,
    #  et qui devraient servir de base pour les lire

    # todo générer les relations lues dans un tableau des relations

    # todo : coder la lecture de la balise faction dans une scène,
    #  qui ajouter des dummy roles dans la scène quand ils sont lus?
    #  qu'il faudra nettoyer avant chaque association dans cleanupall
    #  qui forcera lors de l'association l'ajout de la scène au personnage? comment gérer les rôles?

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

    tousLesSquelettesPerso(monGN, prefixeFichiers)
    tousLesSquelettesPNJ(monGN, prefixeFichiers)
    print("*******dumpallscenes*********************")
    # dumpAllScenes(mon_gn)

    print("*******changelog*********************")
    if not args.nochangelog:
        generer_tableau_changelog_sur_drive(monGN, apiDrive, apiSheets, dossier_output_squelettes_pjs)
        genererChangeLog(monGN, prefixeFichiers, nbJours=3)
        genererChangeLog(monGN, prefixeFichiers, nbJours=4)

    print("******* statut intrigues *********************")
    if not args.notableintrigues:
        creer_table_intrigues_sur_drive(monGN, apiSheets, apiDrive, dossier_output_squelettes_pjs)

    # ajouter_champs_modifie_par(mon_gn, nom_fichier_sauvegarde)
    # trierScenes(mon_gn)
    # listerTrierPersos(mon_gn)
    # #écrit toutes les scènes qui sont dans le GN, sans ordre particulier
    # dumpAllScenes(mon_gn)

    ## pour avoir tous les objets du jeu :
    # generecsvobjets(mon_gn)

    # squelettePerso(mon_gn, "Kyle Talus")
    # listerRolesPerso(mon_gn, "Greeta")
    # listerPNJs(mon_gn)
    # genererCsvPNJs(mon_gn, verbal=False)
    # genererCsvObjets(mon_gn)

    # #lister les correspondaces entre les roles et les noms standards
    # mesroles = tousLesRoles(mon_gn)
    # fuzzyWuzzyme(mesroles, noms_persos)

    # print(normaliserNomsPNJs(mon_gn))
    # #génération d'un premier tableau de noms de PNJs à partir de ce qu'on lit dans les intrigues
    # nomsPNSnormalisés = normaliserNomsPNJs(mon_gn)
    # print([ nomsPNSnormalisés[k][0] for k in nomsPNSnormalisés])
    # dedupePNJs(mon_gn)

    # print(getAllRole(GN))

    # afficherLesPersos(mon_gn)
    # afficherDatesScenes(mon_gn)
    # genererCsvOrgaIntrigue(mon_gn)
    # listerLesRoles(mon_gn)

    # listerDatesIntrigues(mon_gn)

    ## test de la fonction d'effaçage'
    # testEffacerIntrigue(mon_gn)

    # print(" l'intrigue la plus ancienne est {0}, c'est {1}, maj : {2}".format(mon_gn.idOldestUpdate, mon_gn.intrigues[mon_gn.idOldestUpdate], mon_gn.oldestUpdate))

    # test de la focntion de rapprochement des PNJs
    # fuzzyWuzzyme(listerPNJs(mon_gn), nomsPNJs)

    # #test de la focntion de lecture des PJs
    # dumpPersosLus(mon_gn)
    # dumpSortedPersos(mon_gn)

    # genererTableauIntrigues(mon_gn)


def ajouterPersosSansFiche(monGN, nomspersos):
    monGN.forcerImportPersos(nomspersos)

    print(f"fin de l'ajout des personnages sans fiche. j'ai {len(monGN.dictPJs.values())} personnages en tout")


def afficherLesPersos(monGN):
    for intrigue in monGN.intrigues:
        # print("propriétaire intrigue : {0} : {1}".format(intrigue.nom, intrigue.orgaReferent))
        # for clef in intrigue.roles.keys():
        #     print(clef + " a pour nom complet : " + str(intrigue.roles[clef].nom))

        for role in intrigue.rolesContenus.values():
            print("pour le rôle " + role.nom)
            print("Personnage : " + role.perso.nom)
            texteScenes = ""
            for scene in role.scenes:
                texteScenes += scene.titre + "; "
            print("scenes : " + texteScenes)


def afficherDatesScenes(monGN):
    for intrigue in monGN.intrigues:
        for scene in intrigue.scenes:
            print("scène : {0} / date : {1} > {2}".format(scene.titre, scene.date, scene.getFormattedDate()))


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


# def listerRolesPerso(monGN, nomPerso):
#     nomPerso = process.extractOne(nomPerso, noms_persos)[0]
#     for perso in monGN.dictPJs.values():
#         if perso.nom == nomPerso:
#             # print(f"{nomPerso} trouvé")
#             for role in perso.rolesContenus:
#                 print(role)
#             break


def tousLesSquelettesPerso(monGN, prefixe=None):
    toutesScenes = ""
    for perso in monGN.dictPJs.values():
        toutesScenes += f"Début du squelette pour {perso.nom} (Orga Référent : {perso.orgaReferent}) : \n"
        toutesScenes += f"résumé de la bio : \n"
        for item in perso.description:
            toutesScenes += f"{item} \n"
        toutesScenes += f"Psychologie : "
        for item in perso.concept:
            toutesScenes += f"{item} \n"
        toutesScenes += f"Motivations et objectifs : \n"
        for item in perso.driver:
            toutesScenes += f"{item} \n"
        toutesScenes += f"Chronologie : \n "
        for item in perso.datesClefs:
            toutesScenes += f"{item} \n"
        toutesScenes += "\n *** Scenes associées : *** \n"

        mesScenes = []
        for role in perso.roles:
            for scene in role.scenes:
                # print(f"{scene.titre} trouvée")
                mesScenes.append(scene)

        # for scene in perso.scenes:
        #     mesScenes.append(scene)

        # print(f"{nomPerso} trouvé")
        mesScenes = Scene.trierScenes(mesScenes)
        for scene in mesScenes:
            # print(scene)
            toutesScenes += str(scene) + '\n'
        toutesScenes += '****************************************************** \n'

        # print('****************************************************** \n')
    # print(toutesScenes)
    if prefixe is not None:
        with open(prefixe + ' - squelettes.txt', 'w', encoding="utf-8") as f:
            f.write(toutesScenes)
            f.close()

    return toutesScenes


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

        mes_scenes = Scene.trierScenes(mes_scenes)
        # for scene in mesScenes:
        #     # print(scene)
        #     texte_intro += str(scene) + '\n'
        texte_intro += '****************************************************** \n'
        # squelettes_persos[perso.nom] = dict()
        # squelettes_persos[perso.nom]['intro'] = texte_intro
        # squelettes_persos[perso.nom]['scenes'] = mes_scenes

        squelettes_persos[perso.nom] = {'intro': texte_intro, 'scenes': mes_scenes}
    return squelettes_persos


def squelettes_par_perso(monGN, pj=True):
    squelettes_persos = {}
    if pj:
        liste_persos_source = monGN.dictPJs.values()
    else:
        liste_persos_source = monGN.dictPNJs.values()

    for perso in liste_persos_source:
        # for perso in mon_gn.dictPJs.values():
        texte_perso = ""
        texte_perso += f"Début du squelette pour {perso.nom} (Orga Référent : {perso.orgaReferent}) : \n"
        texte_perso += f"résumé de la bio : \n"
        for item in perso.description:
            texte_perso += f"{item} \n"
        texte_perso += f"Psychologie : "
        for item in perso.concept:
            texte_perso += f"{item} \n"
        texte_perso += f"Motivations et objectifs : \n"
        for item in perso.driver:
            texte_perso += f"{item} \n"
        texte_perso += f"Chronologie : \n "
        for item in perso.datesClefs:
            texte_perso += f"{item} \n"
        texte_perso += "\n *** Scenes associées : *** \n"

        mes_scenes = []
        for role in perso.roles:
            for scene in role.scenes:
                # print(f"{scene.titre} trouvée")
                mes_scenes.append(scene)

        mes_scenes = Scene.trierScenes(mes_scenes)
        for scene in mes_scenes:
            # print(scene)
            texte_perso += str(scene) + '\n'
        texte_perso += '****************************************************** \n'
        squelettes_persos[perso.nom] = texte_perso

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


def generer_squelettes_dans_drive(mon_GN: GN, api_doc, api_drive, pj=True):
    parent = mon_GN.dossier_outputs_drive
    if pj:
        pj_pnj = "PJ"
    else:
        pj_pnj = "PNJ"
    nom_dossier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Squelettes {pj_pnj}'
    nouveau_dossier = extraireTexteDeGoogleDoc.creer_dossier(api_drive, parent, nom_dossier)

    d = squelettes_par_perso(mon_GN, pj=pj)
    for nom_perso in d:
        # créer le fichier et récupérer l'ID
        nom_fichier = f'{nom_perso} - squelette au {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}'
        texte = d[nom_perso]

        extraireTexteDeGoogleDoc.inserer_squelettes_dans_drive(nouveau_dossier, api_doc, api_drive, texte, nom_fichier)


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

        # for scene in perso.scenes:
        #     mesScenes.append(scene)

        # print(f"{nomPerso} trouvé")
        mesScenes = Scene.trierScenes(mesScenes)
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


def genererChangeLog(monGN, prefixe, nbJours=1, verbal=False):
    dateReference = datetime.date.today() - datetime.timedelta(days=nbJours)

    # on crée un tableau avec tous lse changements :
    # [orga referent | perso | titre intrigue | url intrigue | date changement intrigue]
    # structure souhaitée :
    # orga referent / persos / titre intrigue/ url intrigue | date changement intrigue

    restitution = dict()
    for intrigue in monGN.intrigues.values():
        if intrigue.lastFileEdit.date() > dateReference:
            for role in intrigue.rolesContenus.values():
                if role.perso is not None and modeleGN.estUnPJ(role.perso.pj):
                    referent = role.perso.orgaReferent.strip()

                    if len(referent) < 3:
                        referent = "Orga sans nom"

                    # print(f"je m'apprête à ajouter une ligne pour {referent} : {role.perso.nom} dans {intrigue.nom}")
                    nomPerso = role.perso.nom
                    nomIntrigue = intrigue.nom

                    # on vérifie que le référent et le persos existent, sinon on initialise
                    if referent not in restitution:
                        restitution[referent] = dict()
                    if nomPerso not in restitution[referent]:
                        # restitution[referent][nomPerso] = dict()
                        restitution[referent][nomPerso] = []
                    # if nomIntrigue not in restitution[referent][nomPerso]:
                    #     restitution[referent][nomPerso][nomIntrigue] = \
                    #         [intrigue.lastProcessing.strftime("%d/%m/%Y à %H:%M:%S"),
                    #          intrigue.getFullUrl()]
                    # # on utilise nomintrigue comem clef, car sinon, comme on rentre par les roles on va multiplier les entrées

                    # et maintenant on remplit la liste
                    restitution[referent][nomPerso].append([intrigue.nom,
                                                            intrigue.getFullUrl(),
                                                            intrigue.lastFileEdit.strftime("%d/%m/%Y à %H:%M:%S")])

                    # print(restitution)
                    # restitution.append([role.perso.orgaReferent,
                    #                     role.perso.nom,
                    #                     intrigue.titre,
                    #                     intrigue.getFullUrl(),
                    #                     intrigue.lastProcessing])
    # print(restitution)
    texte = ""
    for nomOrga in restitution:
        texte += f"{nomOrga}, ces personnages sont dans des intrigues qui ont été modifiées depuis {dateReference} : \n"
        for perso in restitution[nomOrga]:
            texte += f"\t pour {perso} : \n "
            for element in restitution[nomOrga][perso]:
                # texte += f"\t\t l'intrigue {restitution[nomOrga][perso][0]} \n " \
                #          f"\t\t a été modifiée le {restitution[nomOrga][perso][2]} \n" \
                #          f"\t\t (url : {restitution[nomOrga][perso][1]}) \n"
                texte += f"\t\t l'intrigue {element[0]} \n " \
                         f"\t\t a été modifiée le {element[2]} \n" \
                         f"\t\t (url : {element[1]}) \n\n"

    if verbal:
        print(texte)

    if prefixe is not None:
        with open(prefixe + ' - changements - ' + str(nbJours) + 'j.txt', 'w', encoding="utf-8") as f:
            f.write(texte)
            f.close()

    return texte


# def squelettePerso(monGN, nomPerso):
#     mesScenes = []
#     nomPerso = process.extractOne(nomPerso, noms_persos)[0]
#     for perso in monGN.dictPJs.values():
#         if perso.nom == nomPerso:
#             # print(f"{nomPerso} trouvé")
#             for role in perso.rolesContenus:
#                 for scene in role.scenes:
#                     # print(f"{scene.titre} trouvée")
#                     mesScenes.append(scene)
#             break
#
#     # print(f"{nomPerso} trouvé")
#     mesScenes = Scene.trierScenes(mesScenes)
#     for scene in mesScenes:
#         print(scene)


def listerPNJs(monGN):
    toReturn = []
    for intrigue in monGN.intrigues.values():
        for role in intrigue.rolesContenus.values():
            if role.estUnPNJ():
                print(role)
                toReturn.append(role.nom)
    return toReturn


def genererCsvPNJs(monGN: GN, verbal=False):
    noms_pnjs = monGN.noms_pnjs()
    output = "nom PNJ;description;typePJ;niveau implication;details intervention;intrigue;" \
             "nom dans l'intrigue;indice de confiance normalisation\n"
    for intrigue in monGN.intrigues.values():
        for role in intrigue.rolesContenus.values():
            if role.estUnPNJ():
                nompnj = role.nom.replace('\n', chr(10))
                description = role.description.replace('\n', "***")
                niveauImplication = role.niveauImplication.replace('\n', chr(10))
                perimetreIntervention = role.perimetreIntervention.replace('\n', chr(10))
                score = process.extractOne(nompnj, noms_pnjs)
                typeDansGN = monGN.dictPNJs[score[0]].pj
                output += f"{score[0]};" \
                          f"{description};" \
                          f"{stringTypePJ(typeDansGN)};" \
                          f"{niveauImplication};" \
                          f"{perimetreIntervention};" \
                          f"{intrigue.nom}; " \
                          f"{nompnj}; " \
                          f"{score[1]}" \
                          "\n"
    if verbal:
        print(output)


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
        for role in intrigue.rolesContenus.values():
            if not modeleGN.estUnPNJ(role.pj) and role.pj != EST_REROLL:
                tousLesRoles.append(role.nom)
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
            if role.estUnPNJ():
                nomsPNJs.append(role.nom)
    nomsPNJs = list(set(nomsPNJs))
    print("Nom D'origine ;Meilleur choix;Confiance")
    for i in range(len(nomsPNJs)):
        choices = process.extract(nomsPNJs[i], nomsPNJs, limit=2)
        print(f"{choices[0][0]};{choices[1][0]};{choices[1][1]}")

        # le premier choix sera toujours de 100, vu qu'il se sera trouvé lui-même
        # si le second choix est > 90 il y a de fortes chances qu'on ait le même perso
        # sinon on ne prend pas de risques et on garde le meme perso
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


# def dumpSortedPersos(monGN):
#     tousLesPersos = [x.nom for x in monGN.dictPJs.values()]
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
    # for intrigue in mon_gn.intrigues.values():
    #     print(f"{str(intrigue)}")
    #     print(f" a {len(intrigue.scenes)} scenes")
    #     scenesTriees = sorted(intrigue.scenes, key=lambda scene: scene.getLongdigitsDate(), reverse=True)
    #     for s in scenesTriees:
    #         print(s)

    for intrigue in monGN.intrigues.values():
        print()
        print()
        print(f"intrigue {intrigue.nom} : ")
        triee = intrigue.getScenesTriees()
        for scene in triee:
            print(scene)


def listerTrierPersos(monGN):
    touspj = []
    for pj in monGN.dictPJs.values():
        touspj.append(pj.nom)
    touspj.sort()
    for pj in touspj:
        print(pj)


def lister_erreurs(monGN, prefixe, tailleMinLog=1, verbal=False):
    logErreur = ""
    for intrigue in monGN.intrigues.values():
        if len(intrigue.errorLog) > tailleMinLog:
            logErreur += f"Pour {intrigue.nom} : \n"
            logErreur += intrigue.errorLog + '\n'
            logErreur += suggerer_tableau_persos(monGN, intrigue)
            logErreur += "\n \n"
    if verbal:
        print(logErreur)
    with open(prefixe + ' - problemes tableaux persos.txt', 'w', encoding="utf-8") as f:
        f.write(logErreur)
        f.close()
    return logErreur


def genererTableauIntrigues(monGN):
    print("Intrigue; Orga Référent")
    toPrint = monGN.intrigues.values()
    toPrint = sorted(toPrint, key=lambda x: x.nom)
    for intrigue in toPrint:
        print(f"{intrigue.nom};{intrigue.orgaReferent.strip()};")


def suggerer_tableau_persos(mon_gn: GN, intrigue: Intrigue, verbal: bool = False):
    noms_persos = mon_gn.noms_pjs()
    noms_pnjs = mon_gn.noms_pnjs()
    noms_roles_dans_intrigue = [x.perso.nom for x in intrigue.rolesContenus.values() if x.perso is not None]
    # print("Tableau suggéré")
    # créer un set de tous les rôles de chaque scène de l'intrigue
    iwant = []
    for scene in intrigue.scenes:
        if scene.noms_roles_lus is not None:
            iwant += scene.noms_roles_lus
    iwant = [x.strip() for x in iwant]
    iwant = set(iwant)

    tableau_sortie = []
    toPrint = "Tableau suggéré : \n"

    # pour chaque nom dans une scène, trouver le perso correspondant
    for nom in iwant:
        # print(str(nom))
        score_pj = process.extractOne(str(nom), noms_persos)
        score_pnj = process.extractOne(str(nom), noms_pnjs)
        if score_pj[0] in noms_roles_dans_intrigue or score_pnj[0] in noms_roles_dans_intrigue:
            prefixe = "[OK]"
        else:
            prefixe = "[XX]"

        if score_pj[1] > score_pnj[1]:
            meilleur_nom = f"{score_pj[0]} pour {nom} ({score_pj[1]} % de certitude)"
        else:
            meilleur_nom = f"{score_pnj[0]} pour {nom} ({score_pnj[1]} % de certitude)"

        tableau_sortie.append([prefixe, meilleur_nom])
        tableau_sortie = sorted(tableau_sortie)

    for e in tableau_sortie:
        toPrint += f"{e[0]} {e[1]} \n"

    if verbal:
        print(toPrint)

    return toPrint


def dedupePNJs(monGN):
    nomsPNJs = []
    nomsNormalises = dict()
    for intrigue in monGN.intrigues.values():
        for role in intrigue.rolesContenus.values():
            if role.estUnPNJ():
                nomsPNJs.append(role.nom)
    nomsPNJs = list(set(nomsPNJs))
    extract = process.dedupe(nomsPNJs, threshold=89)
    for v in extract:
        print(v)

    # rolesSansScenes = []
    # for role in intrigue.roles.values():
    #     if len(role.scenes()) < 1:
    #         rolesSansScenes.append(role)
    #
    # if len(rolesSansScenes) > 0:
    #     print("Roles sans Scènes : ")
    #     for role in rolesSansScenes:
    #         print(role.nom)


def charger_PNJs(gn, chemin_fichier):
    try:
        with open(chemin_fichier, 'r') as f:
            for ligne in f:
                nom = ligne.strip()
                gn.dictPNJs[nom] = Personnage(nom=nom, forced=True, pj=EST_PNJ_HORS_JEU)
                # print(f"{gn.dictPNJs[nom]}")
    except FileNotFoundError:
        print(f"Le fichier {chemin_fichier} n'a pas été trouvé.")


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


def generer_tableau_changelog_sur_drive(mon_gn: GN, api_drive, api_sheets, dossier_output: str):
    dict_orgas_persos = dict()
    tableau_scene_orgas = []
    tous_les_conteneurs = list(mon_gn.dictPJs.values()) + list(mon_gn.intrigues.values())
    toutes_les_scenes = []
    for conteneur in tous_les_conteneurs:
        for scene in conteneur.scenes:
            toutes_les_scenes.append(scene)

    toutes_les_scenes = sorted(toutes_les_scenes, key=lambda scene: scene.derniere_mise_a_jour, reverse=True)

    # print(f"taille de toutes les scènes = {len(toutes_les_scenes)}"
    #       f"taille de tous les conteneurs = {len(tous_les_conteneurs)}")

    for ma_scene in toutes_les_scenes:
        for role in ma_scene.roles:
            if role.estUnPNJ():
                continue
            if role.perso is None:
                continue
            if len(role.perso.orgaReferent) < 3:
                orga_referent = "Orga sans nom"
            else:
                orga_referent = role.perso.orgaReferent.strip()
            if orga_referent not in dict_orgas_persos:
                # dict_orgas_persos[role.perso.orgaReferent].append(role.perso.nom)
                dict_orgas_persos[orga_referent] = set()
            # else:
            #     # dict_orgas_persos[role.perso.orgaReferent] = [role.perso.nom]
            dict_orgas_persos[orga_referent].add(role.perso.nom)

    # à ce stade là on a :
    # les scènes triées dans l'ordre de dernière modif #todo : créer la méthode)
    # tous les orgas dans un set
    for ma_scene in toutes_les_scenes:
        dict_scene = dict()
        dict_scene['nom_scene'] = ma_scene.titre
        dict_scene['date'] = ma_scene.derniere_mise_a_jour.strftime("%Y-%m-%d %H:%M:%S")
        dict_scene['qui'] = ma_scene.modifie_par
        dict_scene['document'] = ma_scene.conteneur.getFullUrl()
        dict_orgas = dict()
        # dict_scene['dict_orgas'] = dict_orgas
        for role in ma_scene.roles:
            if role.estUnPNJ():
                continue
            if role.perso is None:
                continue
            orga_referent = role.perso.orgaReferent.strip()
            if len(orga_referent) < 3:
                orga_referent = "Orga sans nom"
            if orga_referent not in dict_orgas:
                dict_orgas[orga_referent] = [role.perso.nom]
            else:
                dict_orgas[orga_referent] += [role.perso.nom]
        tableau_scene_orgas.append([dict_scene, dict_orgas])

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Changelog'

    id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, dossier_output)
    extraireTexteDeGoogleDoc.exporter_changelog(tableau_scene_orgas, id, dict_orgas_persos, api_sheets)


def creer_table_intrigues_sur_drive(mon_gn: GN, api_sheets, api_drive, dossier_export):
    table_intrigues = [
        ["nom intrigue", "nombre de scenes", "dernière édition", "modifié par", "Orga referent", "statut", "Problèmes",
         "url"]]
    for intrigue in mon_gn.intrigues.values():
        table_intrigues.append([intrigue.nom,
                                len(intrigue.scenes),
                                intrigue.lastFileEdit.strftime("%Y-%m-%d %H:%M:%S"),
                                intrigue.modifie_par,
                                intrigue.orgaReferent,
                                intrigue.questions_ouvertes,
                                len(intrigue.errorLog.splitlines()),
                                intrigue.getFullUrl()])

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Etat des intrigues'
    id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, dossier_export)
    # extraireTexteDeGoogleDoc.exporter_table_intrigue(api_doc, nom_fichier, dossier_export, df)
    # extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, df, id)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table_intrigues, id)


def ecrire_erreurs_dans_drive(texte_erreurs, apiDoc, apiDrive, parent):
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- Listes des erreurs dans les tableaux des persos'
    id = extraireTexteDeGoogleDoc.add_doc(apiDrive, nom_fichier, parent)
    result = extraireTexteDeGoogleDoc.write_to_doc(apiDoc, id, texte_erreurs)
    if result:
        extraireTexteDeGoogleDoc.formatter_fichier_erreurs(apiDoc, id)


# ***************** début de l'ajout des fonctions pour faire tourner la GUI ***********************************

def lire_et_recharger_gn(mon_gn: GN, api_drive, api_doc, api_sheets, noms_persos,
                         nom_fichier_sauvegarde: str, dossier_output_squelettes_pjs: str,
                         fichier_erreurs: bool = True, export_drive: bool = True,
                         changelog: bool = True, table_intrigues: bool = True,
                         singletest_perso: str = "-01", singletest_intrigue: str = "-01",
                         fast_intrigues: bool = True, fast_persos: bool = True, verbal: bool = False):
    if api_doc is None or api_sheets is None or api_drive is None:
        api_drive, api_doc, api_sheets = lecteurGoogle.creer_lecteurs_google_apis()

    mon_gn.effacer_personnages_forces()

    extraireTexteDeGoogleDoc.extraireIntrigues(mon_gn,
                                               apiDrive=api_drive,
                                               apiDoc=api_doc,
                                               singletest=singletest_intrigue,
                                               fast=fast_intrigues)
    extraireTexteDeGoogleDoc.extrairePJs(mon_gn,
                                         apiDrive=api_drive,
                                         apiDoc=api_doc,
                                         singletest=singletest_perso,
                                         fast=fast_persos)
    extraireTexteDeGoogleDoc.extraire_factions(mon_gn, apiDoc=api_doc)

    mon_gn.forcerImportPersos(noms_persos)
    mon_gn.rebuildLinks(verbal)

    mon_gn.save(nom_fichier_sauvegarde)

    print("****************************")
    print("****************************")
    print("****************************")
    prefixeFichiers = str(datetime.date.today())
    print("*********toutesleserreurs*******************")
    if fichier_erreurs:
        texte_erreurs = lister_erreurs(mon_gn, prefixeFichiers)
        ecrire_erreurs_dans_drive(texte_erreurs, api_doc, api_drive, dossier_output_squelettes_pjs)

    print("*********touslesquelettes*******************")
    if export_drive:
        generer_squelettes_dans_drive(mon_gn, api_doc, api_drive, pj=True)
        generer_squelettes_dans_drive(mon_gn, api_doc, api_drive, pj=False)

    tousLesSquelettesPerso(mon_gn, prefixeFichiers)
    tousLesSquelettesPNJ(mon_gn, prefixeFichiers)
    print("*******dumpallscenes*********************")
    # dumpAllScenes(mon_gn)

    print("*******changelog*********************")
    if changelog:
        generer_tableau_changelog_sur_drive(mon_gn, api_drive, api_sheets, dossier_output_squelettes_pjs)
        genererChangeLog(mon_gn, prefixeFichiers, nbJours=3)
        genererChangeLog(mon_gn, prefixeFichiers, nbJours=4)

    print("******* statut intrigues *********************")
    if table_intrigues:
        creer_table_intrigues_sur_drive(mon_gn, api_sheets, api_drive, dossier_output_squelettes_pjs)


def charger_fichier_init(fichier_init: str):
    # init configuration
    config = configparser.ConfigParser()
    config.read(fichier_init)
    resultat_ok = False
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
        resultat_ok = True
    except configparser.Error as e:
        # Erreur lors de la lecture d'un paramètre dans le fichier de configuration
        print("Erreur lors de la lecture du fichier de configuration : {}".format(e))
        return
    return dossier_intrigues, dossier_pjs, id_factions, dossier_output_squelettes_pjs, \
           noms_persos, nom_fichier_pnjs, association_auto, type_fiche, nom_fichier_sauvegarde, resultat_ok


if __name__ == '__main__':
    main()