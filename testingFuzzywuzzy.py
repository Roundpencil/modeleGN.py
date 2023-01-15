import argparse
import configparser
import csv

from fuzzywuzzy import process, fuzz

import extraireTexteDeGoogleDoc
import modeleGN
from modeleGN import *
import lecteurGoogle
import sys

from googleapiclient.errors import HttpError


def main():
    sys.setrecursionlimit(5000)  # mis en place pour prévenir pickle de planter

    parser = argparse.ArgumentParser()
    parser.add_argument("-init", action="store_true", help="fait que la fonction gn.load n'est pas appelée")
    parser.add_argument("-nosave", action="store_true", help="fait que la focntion GN.save n'est pas appelée")
    parser.add_argument("-intrigue", type=str, default="-01", help="si une seule intrigue doit être lue")
    parser.add_argument("-perso", type=str, default="-01", help="si un seul perso doit être lu")
    parser.add_argument("-verbal", action="store_true", help="si on veut afficher toutes les erreurs")
    args = parser.parse_args()

    # init configuration
    config = configparser.ConfigParser()
    config.read('config.ini')


    try:
        dossier_intrigues = config.get('dossiers', 'intrigues').split(',')

        dossier_pjs = [config.get("dossiers", key)
                       for key in config.options("dossiers") if key.startswith("base_persos_")]

        fichier_factions = config.get('dossiers', 'fichier_faction')
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

    # print(f"1 - pnj dans ce GN : {monGN.noms_pnjs()}")

    charger_PNJs(monGN, nom_fichier_pnjs)

    # print(f"2 - pnj dans ce GN : {monGN.noms_pnjs()}")

    if not args.init:
        monGN = GN.load(nom_fichier_sauvegarde)
        # print(f"Derniere version avant mise à jour : {monGN.oldestUpdateIntrigue}")
        # monGN.fichier_factions = "1lDKglitWeg6RsybhLgNsPUa-DqN5POPyOpIo2u9VvvA"
        monGN.dossier_outputs_drive = dossier_output_squelettes_pjs

    # print(f"3 - pnj dans ce GN : {monGN.noms_pnjs()}")

    apiDrive, apiDoc = lecteurGoogle.creer_lecteurs_google_apis()

    monGN.effacer_personnages_forces()

    # extraireTexteDeGoogleDoc.extraireIntrigues(monGN, apiDrive=apiDrive, api_drive=api_drive, singletest="-01")
    # extraireTexteDeGoogleDoc.extrairePJs(monGN, apiDrive=apiDrive, api_drive=api_drive, singletest="-01")

    extraireTexteDeGoogleDoc.extraireIntrigues(monGN, apiDrive=apiDrive, apiDoc=apiDoc, singletest=args.intrigue)
    extraireTexteDeGoogleDoc.extrairePJs(monGN, apiDrive=apiDrive, apiDoc=apiDoc, singletest=args.perso)
    extraireTexteDeGoogleDoc.extraire_factions(monGN, apiDoc=apiDoc)
    # extraireTexteDeGoogleDoc.lire_factions_depuis_fichier(monGN, fichier_faction)


    monGN.forcerImportPersos(noms_persos)
    monGN.rebuildLinks(args.verbal)

    if not args.nosave:
        monGN.save(nom_fichier_sauvegarde)

    # todo : une focntion qui force la lecture sans tout refaire
    #  principe : sauter la boucle
    #  et l'option qui va avec dans l'appel au programme


    # todo: appel dans la foulée de dedupe PNJ pour faire le ménage?
    # todo : utiliser l'objet CSV pour générer les CSV

    # todo : passer la gestion des dates via un objet date time, et ajouter une variable avec la date du GN (0 par défaut)

    # todo : ajouter des fiches relations, qui décrivent l'évolution des relations entre les personnages,
    #  et qui devraient servir de base pour les lire

    # todo générer les relations lues dans un tableau des relations

    # todo : tester et débugger la fonction de mise à jour des fiches
    #  Mettre à jour la version de change log > un fichier par jour PRECISEMMENT
    #  Se concentrer sur les scènes / afficher les scènes concernées en premier / uniquement ?

    # todo : coder la lecture de la balise faction dans une scène,
    #  qui ajouter des dummy roles dans la scène quand ils sont lus?
    #  qu'il faudra nettoyer avant chaque association dans cleanupall
    #  qui forcera lors de l'association l'ajout de la scène au personnage? comment gérer les rôles?

    print("****************************")
    print("****************************")
    print("****************************")
    prefixeFichiers = str(datetime.date.today())
    print("*********toutesleserreurs*******************")
    lister_erreurs(monGN, prefixeFichiers)

    print("*********touslesquelettes*******************")
    generer_squelettes_dans_drive(monGN, apiDoc, apiDrive)
    tousLesSquelettesPerso(monGN, prefixeFichiers)
    tousLesSquelettesPNJ(monGN, prefixeFichiers)
    print("*******dumpallscenes*********************")
    # dumpAllScenes(monGN)

    print("*******changelog*********************")
    genererChangeLog(monGN, prefixeFichiers, nbJours=3)
    genererChangeLog(monGN, prefixeFichiers, nbJours=4)

    # trierScenes(monGN)
    # listerTrierPersos(monGN)
    # #écrit toutes les scènes qui sont dans le GN, sans ordre particulier
    # dumpAllScenes(monGN)

    ## pour avoir tous les objets du jeu :
    # generecsvobjets(monGN)

    # squelettePerso(monGN, "Kyle Talus")
    # listerRolesPerso(monGN, "Greeta")
    # listerPNJs(monGN)
    genererCsvPNJs(monGN, verbal=False)
    # genererCsvObjets(monGN)

    # #lister les correspondaces entre les roles et les noms standards
    # mesroles = tousLesRoles(monGN)
    # fuzzyWuzzyme(mesroles, noms_persos)

    # print(normaliserNomsPNJs(monGN))
    # #génération d'un premier tableau de noms de PNJs à partir de ce qu'on lit dans les intrigues
    # nomsPNSnormalisés = normaliserNomsPNJs(monGN)
    # print([ nomsPNSnormalisés[k][0] for k in nomsPNSnormalisés])
    # dedupePNJs(monGN)

    # print(getAllRole(GN))

    # afficherLesPersos(monGN)
    # afficherDatesScenes(monGN)
    # genererCsvOrgaIntrigue(monGN)
    # listerLesRoles(monGN)

    # listerDatesIntrigues(monGN)

    ## test de la fonction d'effaçage'
    # testEffacerIntrigue(monGN)

    # print(" l'intrigue la plus ancienne est {0}, c'est {1}, maj : {2}".format(monGN.idOldestUpdate, monGN.intrigues[monGN.idOldestUpdate], monGN.oldestUpdate))

    # test de la focntion de rapprochement des PNJs
    # fuzzyWuzzyme(listerPNJs(monGN), nomsPNJs)

    # #test de la focntion de lecture des PJs
    # dumpPersosLus(monGN)
    # dumpSortedPersos(monGN)

    # genererTableauIntrigues(monGN)


def ajouterPersosSansFiche(monGN, nomspersos):
    monGN.forcerImportPersos(nomspersos)

    print(f"fin de l'ajout des personnages sans fiche. j'ai {len(monGN.dictPJs.values())} personnages en tout")


def testEffacerIntrigue(monGN):
    listerRolesPerso(monGN, "Kyle Talus")
    monGN.intrigues["1p5ndWGUb3uCJ1iSSkPpHrDAzwY8iBdK8Lf9CLpP9Diw"].clear()
    del monGN.intrigues["1p5ndWGUb3uCJ1iSSkPpHrDAzwY8iBdK8Lf9CLpP9Diw"]
    print("J'ai effacé l'intrigue Rox et Rouky")
    listerRolesPerso(monGN, "Kyle Talus")


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


def listerRolesPerso(monGN, nomPerso):
    nomPerso = process.extractOne(nomPerso, noms_persos)[0]
    for perso in monGN.dictPJs.values():
        if perso.nom == nomPerso:
            # print(f"{nomPerso} trouvé")
            for role in perso.rolesContenus:
                print(role)
            break



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


def squelettes_par_perso(monGN):
    squelettes_persos = {}
    for perso in monGN.dictPJs.values():
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

def reverse_generer_squelettes_dans_drive(mon_GN:GN, api_doc, api_drive):
    d = squelettes_persos_en_kit(mon_GN)
    for nom_perso in d:
        # créer le fichier et récupérer l'ID
        nom_fichier = f'{nom_perso} - squelette au {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}'
        id = extraireTexteDeGoogleDoc.add_doc(api_drive, nom_fichier, mon_GN.dossier_outputs_drive)

        #ajouter le texte de l'intro
        texte_intro = d[nom_perso]["intro"]
        extraireTexteDeGoogleDoc.write_to_doc(api_doc, id, texte_intro, titre=False)

        #ajouter toutes les scènes
        for scene in d[nom_perso]["scenes"]:
            description_scene = scene.dict_text()

            #ajouter le titre
            extraireTexteDeGoogleDoc.write_to_doc(api_doc, id, description_scene["titre"], titre=True)
            # ajouter les entetes
            extraireTexteDeGoogleDoc.write_to_doc(api_doc, id, description_scene["en-tete"], titre=False)
            # ajouter le texte
            extraireTexteDeGoogleDoc.write_to_doc(api_doc, id, description_scene["corps"], titre=True)

def generer_squelettes_dans_drive(mon_GN:GN, api_doc, api_drive):
    parent = mon_GN.dossier_outputs_drive
    nom_dossier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Squelettes PJ'
    nouveau_dossier = extraireTexteDeGoogleDoc.creer_dossier(api_drive, parent, nom_dossier)

    d = squelettes_par_perso(mon_GN)
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


def squelettePerso(monGN, nomPerso):
    mesScenes = []
    nomPerso = process.extractOne(nomPerso, noms_persos)[0]
    for perso in monGN.dictPJs.values():
        if perso.nom == nomPerso:
            # print(f"{nomPerso} trouvé")
            for role in perso.rolesContenus:
                for scene in role.scenes:
                    # print(f"{scene.titre} trouvée")
                    mesScenes.append(scene)
            break

    # print(f"{nomPerso} trouvé")
    mesScenes = Scene.trierScenes(mesScenes)
    for scene in mesScenes:
        print(scene)


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


def dumpSortedPersos(monGN):
    tousLesPersos = [x.nom for x in monGN.dictPJs.values()]
    tousLesPersos.sort()
    print(tousLesPersos)
    print(len(tousLesPersos))
    print(len(noms_persos))


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
    # for intrigue in monGN.intrigues.values():
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
            logErreur += f"pour {intrigue.nom} : \n"
            logErreur += intrigue.errorLog + '\n'
            logErreur += suggerer_tableau_persos(monGN, intrigue)
            logErreur += "\n \n"
    if verbal:
        print(logErreur)
    with open(prefixe + ' - problemes tableaux persos.txt', 'w', encoding="utf-8") as f:
        f.write(logErreur)
        f.close()


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


def generer_csv_association(roles_dict, filename):
    # Ouvrir un fichier CSV en mode écriture
    with open(filename, 'w', newline='') as csvfile:
        # Créer un objet CSV writer
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Écrire les en-têtes de colonnes
        writer.writerow(['nom', 'description', 'pipr', 'pipi', 'sexe', 'personnage'])
        # Pour chaque rôle dans le dictionnaire de rôles
        for role in roles_dict.values():
            # Récupérer les valeurs de chaque champ
            nom = role.nom
            description = role.description
            pipr = role.pipr
            pipi = role.pipi
            sexe = role.sexe
            personnage = role.perso if role.perso else ""
            # Écrire les valeurs dans le fichier CSV
            writer.writerow([nom, description, pipr, pipi, sexe, personnage])
    print("Fichier CSV généré avec succès: {}".format(filename))



def lire_association_roles_depuis_csv(roles_list, filename):
    try:
        # Ouvrir le fichier CSV en mode lecture
        with open(filename, 'r', newline='') as csvfile:
            # Créer un objet CSV reader
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            # Vérifier les en-têtes de colonnes
            headers = next(reader)
            if headers != ['nom', 'description', 'pipr', 'pipi', 'sexe', 'personnage']:
                raise ValueError("Le fichier CSV ne contient pas les bonnes entêtes de colonnes")
            # Pour chaque ligne du fichier CSV
            for row in reader:
                nom = row[0]
                personnage = row[5]

                # et mettre à jour les paramètres du GN en fcontion de ceux du programme > ca se joue à quel niveau?
                # qu'est-ce qui est propriété de quoi? peut-on changer d'association en cours de vie de gn?

                # Trouver le rôle correspondant dans la liste de rôles
                role = next((role for role in roles_list if role.nom == nom), None)
                if role:
                    # Mettre à jour le champ perso de ce rôle
                    role.perso = personnage
            print("Les informations de personnages ont été mises à jour.")
    except FileNotFoundError:
        print(f"Le fichier {filename} n'existe pas.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier: {e}")

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

main()
