import configparser
import os

import extraireTexteDeGoogleDoc
import lecteurGoogle
from modeleGN import *


def charger_fichier_init(fichier_init: str):
    # init configuration
    config = configparser.ConfigParser()
    config.read(fichier_init)

    dict_config = dict()
    try:
        dict_config['dossier_intrigues'] = [x.strip() for x in config.get('dossiers', 'intrigues').split(',')]

        dict_config['dossier_pjs'] = [config.get("dossiers", key)
                                      for key in config.options("dossiers") if key.startswith("base_persos")]

        dict_config['id_factions'] = config.get('dossiers', 'id_factions')
        dict_config['dossier_output'] = config.get('dossiers', 'dossier_output_squelettes_pjs')

        dict_config['noms_persos'] = [nom_p.strip()
                                      for nom_p in config.get('pjs_a_importer', 'noms_persos').split(',')]

        # chargement des PNJs depuis le fichier spécifié dans le fichier de config
        dict_config['fichier_noms_pnjs'] = config.get('pjs_a_importer', 'nom_fichier_pnjs')
        dict_config['noms_pnjs'] = lire_fichier_pnjs(dict_config['fichier_noms_pnjs'])

        dict_config['association_auto'] = config.getboolean('globaux', 'association_auto')
        dict_config['type_fiche'] = config.get('globaux', 'type_fiche')

        dict_config['nom_fichier_sauvegarde'] = config.get('sauvegarde', 'nom_fichier_sauvegarde')

    except configparser.Error as e:
        # Erreur lors de la lecture d'un paramètre dans le fichier de configuration
        print("Erreur lors de la lecture du fichier de configuration : {}".format(e))
        return None
    return dict_config


def lire_fichier_pnjs(nom_fichier: str):
    to_return = []
    try:
        with open(nom_fichier, 'r') as f:
            for ligne in f:
                nom = ligne.strip()
                to_return.append(nom)
                # gn.dictPNJs[nom] = Personnage(nom=nom, forced=True, pj=EST_PNJ_HORS_JEU)
                # print(f"{gn.dictPNJs[nom]}")
    except FileNotFoundError:
        print(f"Le fichier {nom_fichier} - {os.getcwd()} n'a pas été trouvé.")
    return to_return


# todo : le bug est que l'intrigue est lue sans tableau des persos car nom=pj est none pendant tout ce temps ?

def lire_et_recharger_gn(mon_gn: GN, api_drive, api_doc, api_sheets, nom_fichier_sauvegarde: str,
                         dossier_output_squelettes_pjs: str,
                         noms_pjs=None, noms_pnjs=None,
                         fichier_erreurs: bool = True, export_drive: bool = True,
                         changelog: bool = True, table_intrigues: bool = True, table_objets: bool = True,
                         singletest_perso: str = "-01", singletest_intrigue: str = "-01",
                         fast_intrigues: bool = True, fast_persos: bool = True, verbal: bool = False):
    if api_doc is None or api_sheets is None or api_drive is None:
        api_drive, api_doc, api_sheets = lecteurGoogle.creer_lecteurs_google_apis()

    mon_gn.effacer_personnages_forces()

    extraireTexteDeGoogleDoc.extraire_intrigues(mon_gn,
                                                apiDrive=api_drive,
                                                apiDoc=api_doc,
                                                singletest=singletest_intrigue,
                                                fast=fast_intrigues)
    extraireTexteDeGoogleDoc.extraire_pjs(mon_gn,
                                          apiDrive=api_drive,
                                          apiDoc=api_doc,
                                          singletest=singletest_perso,
                                          fast=fast_persos)

    if noms_pjs:
        mon_gn.forcer_import_pjs(noms_pjs)
    if noms_pnjs:
        mon_gn.forcer_import_pnjs(noms_pnjs)

    extraireTexteDeGoogleDoc.extraire_factions(mon_gn, apiDoc=api_doc)
    print(f"mon_gn.factions = {mon_gn.factions}")

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

    print("******* statut intrigues *********************")
    if table_intrigues:
        creer_table_intrigues_sur_drive(mon_gn, api_sheets, api_drive, dossier_output_squelettes_pjs)

    print("*******changelog*********************")
    if changelog:
        generer_tableau_changelog_sur_drive(mon_gn, api_drive, api_sheets, dossier_output_squelettes_pjs)
        # genererChangeLog(mon_gn, prefixeFichiers, nbJours=3)
        # genererChangeLog(mon_gn, prefixeFichiers, nbJours=4)

    print("*********touslesquelettes*******************")
    if export_drive:
        generer_squelettes_dans_drive(mon_gn, api_doc, api_drive, pj=True)
        generer_squelettes_dans_drive(mon_gn, api_doc, api_drive, pj=False)

    ecrire_squelettes_localement(mon_gn, prefixeFichiers)
    ecrire_squelettes_localement(mon_gn, prefixeFichiers, pj=False)
    print("*******dumpallscenes*********************")
    # dumpAllScenes(mon_gn)

    print("******* table objets *********************")
    if table_objets:
        ecrire_table_objet_dans_drive(mon_gn, api_drive, api_sheets)

    print("******* fin de la génération  *********************")


# def charger_PNJs(gn, chemin_fichier):
#     try:
#         with open(chemin_fichier, 'r') as f:
#             for ligne in f:
#                 nom = ligne.strip()
#                 gn.dictPNJs[nom] = Personnage(nom=nom, forced=True, pj=EST_PNJ_HORS_JEU)
#                 # print(f"{gn.dictPNJs[nom]}")
#     except FileNotFoundError:
#         print(f"Le fichier {chemin_fichier} n'a pas été trouvé.")

def lister_erreurs(mon_gn, prefixe, taille_min_log=1, verbal=False):
    logErreur = ""
    for intrigue in mon_gn.intrigues.values():
        if len(intrigue.errorLog) > taille_min_log:
            logErreur += f"Pour {intrigue.nom} : \n"
            logErreur += intrigue.errorLog + '\n'
            logErreur += suggerer_tableau_persos(mon_gn, intrigue)
            logErreur += "\n \n"
    if verbal:
        print(logErreur)
    if prefixe is not None:
        with open(prefixe + ' - problemes tableaux persos.txt', 'w', encoding="utf-8") as f:
            f.write(logErreur)
            f.close()
    return logErreur


def ecrire_erreurs_dans_drive(texte_erreurs, apiDoc, apiDrive, parent):
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- Listes des erreurs dans les tableaux des persos'
    id = extraireTexteDeGoogleDoc.add_doc(apiDrive, nom_fichier, parent)
    result = extraireTexteDeGoogleDoc.write_to_doc(apiDoc, id, texte_erreurs)
    if result:
        extraireTexteDeGoogleDoc.formatter_fichier_erreurs(apiDoc, id)


def suggerer_tableau_persos(mon_gn: GN, intrigue: Intrigue, verbal: bool = False):
    noms_persos = mon_gn.noms_pjs()
    noms_pnjs = mon_gn.noms_pnjs()
    noms_roles_dans_intrigue = [x.perso.nom for x in intrigue.rolesContenus.values()
                                if not x.issu_dune_faction and x.perso is not None]
    # print(f"noms roles dans intrigue {intrigue.nom} : {noms_roles_dans_intrigue}")
    # print("Tableau suggéré")
    # créer un set de tous les rôles de chaque scène de l'intrigue
    iwant = []
    for scene in intrigue.scenes:
        if scene.noms_roles_lus is not None:
            # comme on prend uniquement les roles lus, on exclut de facto les persos issus de faction
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
    # les scènes triées dans l'ordre de dernière modif
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


def ecrire_squelettes_localement(mon_gn: GN, prefixe=None, pj=True):
    squelettes_persos = squelettes_par_perso(mon_gn, pj)
    toutesScenes = "".join(squelettes_persos.values())

    if prefixe is not None:
        with open(prefixe + ' - squelettes.txt', 'w', encoding="utf-8") as f:
            f.write(toutesScenes)
            f.close()

    return toutesScenes


def generer_liste_pnj_dedup(monGN, threshold=89, verbal=False):
    nomsPNJs = []
    # nomsNormalises = dict()
    for intrigue in monGN.intrigues.values():
        for role in intrigue.rolesContenus.values():
            if role.estUnPNJ():
                nomsPNJs.append(role.nom)
    nomsPNJs = list(set(nomsPNJs))
    extract = process.dedupe(nomsPNJs, threshold=threshold)
    extract = sorted(extract)
    if verbal:
        for v in extract:
            print(v)
    to_return = '\n'.join(extract)
    return to_return


def ecrire_liste_pnj_dedup_localement(mon_gn: GN, prefixe: str, threshold=89, verbal=False):
    to_print = generer_liste_pnj_dedup(mon_gn, threshold, verbal)
    if prefixe is not None:
        with open(prefixe + ' - liste_pnjs_dedupliqués.txt', 'w', encoding="utf-8") as f:
            f.write(to_print)
            f.close()


def generer_changelog(monGN, prefixe, nbJours=1, verbal=False):
    dateReference = datetime.date.today() - datetime.timedelta(days=nbJours)

    # on crée un tableau avec tous lse changements :
    # [orga referent | perso | titre intrigue | url intrigue | date changement intrigue]
    # structure souhaitée :
    # orga referent / persos / titre intrigue/ url intrigue | date changement intrigue

    restitution = dict()
    for intrigue in monGN.intrigues.values():
        if intrigue.lastFileEdit.date() > dateReference:
            for role in intrigue.rolesContenus.values():
                if role.perso is not None and estUnPJ(role.perso.pj):
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


def ecrire_fichier_config(dict_config: dict, nom_fichier: str):
    config = configparser.ConfigParser()

    # Create the sections
    config['dossiers'] = {'intrigues': ",".join(dict_config['dossier_intrigues']),
                          'id_factions': dict_config['id_factions'],
                          'dossier_output_squelettes_pjs': dict_config['dossier_output']}

    nb_fichiers_persos = 1
    for perso in dict_config['dossier_pjs']:
        config['dossiers']['base_persos_' + str(nb_fichiers_persos)] = perso
        nb_fichiers_persos += 1

    config['globaux'] = {'association_auto': dict_config['association_auto'],
                         'type_fiche': dict_config['type_fiche']}

    config['sauvegarde'] = {'nom_fichier_sauvegarde': dict_config['nom_fichier_sauvegarde']}

    config['pjs_a_importer'] = {'noms_persos': ",".join(dict_config['noms_persos']),
                                'nom_fichier_pnjs': dict_config['fichier_noms_pnjs']}

    # Write the config file
    with open(nom_fichier, 'w') as configfile:
        config.write(configfile)


def generer_table_objets(monGN):
    to_return = [['description', 'Avec FX?', 'FX', 'Débute Où?', 'fourni par Qui?', 'utilisé où?']]

    for intrigue in monGN.intrigues.values():
        for objet in intrigue.objets:
            description = objet.description.replace('\n', "***")
            avecfx = objet.rfid
            fx = objet.specialEffect.replace('\n', "***")
            debuteou = objet.emplacementDebut.replace('\n', "***")
            fournipar = objet.fourniParJoueur.replace('\n', "***")
            utiliseou = [x.nom for x in objet.inIntrigues]
            to_return.append([f"{description}",
                              f"{avecfx}",
                              f"{fx}",
                              f"{debuteou}",
                              f"{fournipar}",
                              f"{utiliseou}"]
                             )
    return to_return


def ecrire_table_objet_dans_drive(mon_gn: GN, api_drive, api_sheets):
    parent = mon_gn.dossier_outputs_drive
    table = generer_table_objets(mon_gn)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- Table des objets'
    id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, parent)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table, id)
