import configparser
import logging
import os


import extraireTexteDeGoogleDoc
import lecteurGoogle
from modeleGN import *
import dateparser


# communication :
# todo :informer chalacta des factions,
#  des squelettes pnjs, des tableaux intrigues, des nouveaux tableaux de synthèse (objets / chrono / persos),
#  des nouveaux fichiers d'erruers, du tag questionnaire, balise info, tables des pjs et pnjs, nouvelle chrono

# bugs
# todo comprendre pourquoi pas de load de snyder
# todo : comprendre pouruqoi dans 49 un role pparait deux fois


# à faire - rapide


# à faire - plus long

# todo : ajouter deux sections "tableau relations" :
#  une qui conteint toutjours 4 colonnes
#  "X... Voit la relation avec... Comme... Et si non réciproque..."
#  dans les fiches de persos
#  dans les scènes : relations nécessaires (nouveau tag)
#  une qui contient toujours 2 colonnes multilatérale

# todo : une table des objets qui identifie les objets uniques, à la manières des PNJs

# todo : faire évoluer grille objets avec le code et le fait qu'on a trouvé un lien vers une fiche objet

# todo : gestion des évènement
#  lire les fiches > on lit le tableau > on met dans un dictionnaire > on utilise get pour prendre ce qui nous intéresse
#  les appeler à partir des intrigues dans un tableau 'scène nécessaure / onm évènement)
#  ne pas oublier qu'un évènement se rattache à un tringue, et donc à des roles, PAS DES PERSOS




# confort / logique
# todo : refaire version console

# todo : faire un menu qui crée le GN avec les options et crée tous les fichiers qui vont bien
#  dans un dossier magnet du drive fourni en entrée, et des questions sous la forme de "allez-vous utiliser...?"
#  pour déterminer les champs à créer

# todo sortir les erreurs sur les fichiers d'assocaitions factions


def charger_fichier_init(fichier_init: str):
    # init configuration
    config = configparser.ConfigParser()
    config.read(fichier_init)

    dict_config = {}
    try:
        # lecture des informations essentielles
        # dict_config['dossier_intrigues'] = [x.strip() for x in config.get('Essentiels', 'intrigues').split(',')]
        #
        dict_config['dossiers_intrigues'] = [config.get("Essentiels", key)
                                             for key in config.options("Essentiels")
                                             if key.startswith("id_dossier_intrigues")]

        dict_config['dossier_output'] = config.get('Essentiels', 'dossier_output_squelettes_pjs')

        dict_config['association_auto'] = config.getboolean('Essentiels', 'association_auto')

        dict_config['nom_fichier_sauvegarde'] = config.get('Essentiels', 'nom_fichier_sauvegarde')

        # lecture des informations optionnelles
        dict_config['dossiers_pjs'] = [config.get("Optionnels", key)
                                       for key in config.options("Optionnels")
                                       if key.startswith("id_dossier_pjs")]

        dict_config['dossiers_pnjs'] = [config.get("Optionnels", key)
                                        for key in config.options("Optionnels")
                                        if key.startswith("id_dossier_pnjs")]

        dict_config['id_factions'] = config.get('Optionnels', 'id_factions', fallback=None)

        dict_config['id_pjs_et_pnjs'] = config.get('Optionnels', 'id_pjs_et_pnjs', fallback=None)

        if dict_config['id_pjs_et_pnjs'] is None:
            logging.debug("Je suis en train de lire le fichier de config et je n'ai pas trouvé d'id pjpnj en ligne")
            dict_config['fichier_noms_pnjs'] = config.get('Optionnels', 'nom_fichier_pnjs', fallback=None)
            dict_config['liste_noms_pjs'] = [nom_p.strip()
                                             for nom_p in
                                             config.get('Optionnels', 'noms_persos', fallback=None).split(',')]

        texte_date_gn = config.get('Optionnels', 'date_gn', fallback=None)
        if texte_date_gn is not None:
            texte_date_gn = texte_date_gn.strip()
            logging.debug(f"texte_date_gn = {texte_date_gn} / {type(texte_date_gn)}")
            dict_config['date_gn'] = dateparser.parse(texte_date_gn, languages=['fr'])
            logging.debug(f"date_gn formattée = {dict_config['date_gn']}")
        logging.debug(f"pour ce GN, date_gn = {dict_config.get('date_gn', 'Pas de date lue')}")

        # création des champs dérivés
        # if dict_config['id_pjs_et_pnjs'] is not None:
        #     sheet_id = dict_config['id_pjs_et_pnjs']
        #     dict_config['liste_noms_pnjs'] = extraireTexteDeGoogleDoc.lire_gspread_pnj(api_sheets, sheet_id)
        #     dict_config['liste_noms_pjs'] = extraireTexteDeGoogleDoc.lire_gspread_pj(api_sheets, sheet_id)
        #
        # if dict_config.get('fichier_noms_pnjs', default=None) is not None:
        #     dict_config['liste_noms_pnjs'] = lire_fichier_pnjs(dict_config['fichier_noms_pnjs'])

    except configparser.Error as e:
        # Erreur lors de la lecture d'un paramètre dans le fichier de configuration
        print(f"Erreur lors de la lecture du fichier de configuration : {e}")
        return None
    return dict_config


def lire_fichier_pnjs(nom_fichier: str):
    to_return = []
    try:
        # with open(nom_fichier, 'r', encoding="utf-8") as f:
        with open(nom_fichier, 'r') as f:
            for ligne in f:
                nom = ligne.strip()
                to_return.append(nom)
    except FileNotFoundError:
        print(f"Le fichier {nom_fichier} - {os.getcwd()} n'a pas été trouvé.")
    logging.debug(f"après ajout du fichier des pnjs, le tableau contient = {to_return}")
    return to_return


def lire_et_recharger_gn(mon_gn: GN, api_drive, api_doc, api_sheets, nom_fichier_sauvegarde: str,
                         sans_chargement_fichier=False,
                         sauver_apres_operation=True,
                         liste_noms_pjs=None,  # noms_pnjs=None,
                         fichier_erreurs: bool = True,
                         generer_fichiers_pjs: bool = True,
                         generer_fichiers_pnjs: bool = True, pnjs_dedupliques: bool = True, aides_de_jeu: bool = True,
                         changelog: bool = True, table_intrigues: bool = True, table_objets: bool = True,
                         table_chrono: bool = True, table_persos: bool = True, table_pnjs: bool = True,
                         singletest_perso: str = "-01", singletest_intrigue: str = "-01",
                         fast_intrigues: bool = True, fast_persos: bool = True, verbal: bool = False):
    if api_doc is None or api_sheets is None or api_drive is None:
        api_drive, api_doc, api_sheets = lecteurGoogle.creer_lecteurs_google_apis()

    if sans_chargement_fichier:
        print("recréation d'un GN from scratch")
        new_gn = GN(
            mon_gn.dossiers_intrigues,
            mon_gn.dossier_outputs_drive,
            mon_gn.association_auto,
            mon_gn.dossiers_pjs,
            mon_gn.dossiers_pnjs,
            mon_gn.id_factions,
            fichier_pnjs=mon_gn.fichier_pnjs,
            id_pjs_et_pnjs=mon_gn.id_pjs_et_pnjs
        )
        mon_gn = new_gn
    else:
        mon_gn.effacer_personnages_forces()

    for perso in mon_gn.dictPJs.values():
        print(f"nom du personnage = {perso.nom} / {perso.forced}")
    print(f"noms persos = {mon_gn.noms_pjs()}")

    for perso in mon_gn.dictPNJs.values():
        print(f"nom du pnj = {perso.nom} / {perso.forced}")
    print(f"noms pnjs = {mon_gn.noms_pnjs()}")

    extraireTexteDeGoogleDoc.extraire_intrigues(mon_gn,
                                                api_drive=api_drive,
                                                api_doc=api_doc,
                                                singletest=singletest_intrigue,
                                                fast=fast_intrigues,
                                                verbal=verbal)
    extraireTexteDeGoogleDoc.extraire_pjs(mon_gn,
                                          api_drive=api_drive,
                                          api_doc=api_doc,
                                          singletest=singletest_perso,
                                          fast=fast_persos,
                                          verbal=verbal)

    extraireTexteDeGoogleDoc.extraire_pnjs(mon_gn,
                                           api_drive=api_drive,
                                           api_doc=api_doc,
                                           singletest=singletest_perso,
                                           fast=fast_persos,
                                           verbal=verbal)

    liste_orgas = None
    liste_noms_pnjs = None
    logging.debug(f"mon_gn.id_pjs_et_pnjs = {mon_gn.id_pjs_et_pnjs}")
    logging.debug(f"nom fichier pnj = {mon_gn.fichier_pnjs}")

    if (sheet_id := mon_gn.id_pjs_et_pnjs) is not None:
        # dans ce cas on a un tableau global avec toutes les données > on le lit
        # on met à jour les données pour les PNJs pour
        print(f"sheet_id = {sheet_id}, mon_gn.id_pjs_et_pnjs = {mon_gn.id_pjs_et_pnjs}")
        liste_noms_pnjs = extraireTexteDeGoogleDoc.lire_gspread_pnj(api_sheets, sheet_id)
        liste_noms_pjs, liste_orgas = extraireTexteDeGoogleDoc.lire_gspread_pj(api_sheets, sheet_id)
        print(f"liste_noms_pnjs = {liste_noms_pnjs}")
        print(f"liste_noms_pjs = {liste_noms_pjs}")
        print(f"liste_orgas = {liste_orgas}")
    elif (nom_fichier_pnjs := mon_gn.fichier_pnjs) is not None:
        liste_noms_pnjs = lire_fichier_pnjs(nom_fichier_pnjs)
        logging.debug(f"après ajout, liste nom = {liste_noms_pnjs}")

        # sinon on prend en compte les données envoyées en input, issues des balises du fichier init pour une création
        # et on utilise les focntion classiques d'injections si on trouve des trucs

    if liste_noms_pnjs is not None:
        print("début du forçage des PNJs")
        mon_gn.forcer_import_pnjs(liste_noms_pnjs, verbal=verbal)
        logging.debug("PNJs forcés ok")

    if liste_noms_pjs is not None:
        print("début du forçage des PJs")
        mon_gn.forcer_import_pjs(liste_noms_pjs, verbal=verbal, table_orgas_referent=liste_orgas)
        logging.debug("PJs forcés ok")

    extraireTexteDeGoogleDoc.extraire_factions(mon_gn, apiDoc=api_doc, verbal=verbal)
    # print(f"gn.factions = {gn.factions}")
    logging.debug("factions lues")

    mon_gn.rebuild_links(verbal)

    if sauver_apres_operation:
        mon_gn.save(nom_fichier_sauvegarde)

    print("****************************")
    print("****************************")
    print("****************************")
    prefixe_fichiers = str(datetime.date.today())
    print("*********toutesleserreurs*******************")
    if fichier_erreurs:
        texte_erreurs = lister_erreurs(mon_gn, prefixe_fichiers)
        ecrire_erreurs_dans_drive(texte_erreurs, api_doc, api_drive, mon_gn.dossier_outputs_drive)

    print("******* statut intrigues *********************")
    if table_intrigues:
        creer_table_intrigues_sur_drive(mon_gn, api_sheets, api_drive)

    print("*******changelog*********************")
    if changelog:
        generer_tableau_changelog_sur_drive(mon_gn, api_drive, api_sheets)
        # genererChangeLog(gn, prefixe_fichiers, nbJours=3)
        # genererChangeLog(gn, prefixe_fichiers, nbJours=4)

    print("*********touslesquelettes*******************")
    if generer_fichiers_pjs:
        generer_squelettes_dans_drive(mon_gn, api_doc, api_drive, pj=True)
    if generer_fichiers_pnjs:
        generer_squelettes_dans_drive(mon_gn, api_doc, api_drive, pj=False)

    ecrire_squelettes_localement(mon_gn, prefixe_fichiers)
    ecrire_squelettes_localement(mon_gn, prefixe_fichiers, pj=False)
    print("*******dumpallscenes*********************")
    # dumpAllScenes(gn)

    print("******* table objets *********************")
    if table_objets:
        ecrire_table_objet_dans_drive(mon_gn, api_drive, api_sheets)

    print("******* table planning *********************")
    if table_chrono:
        ecrire_table_chrono_dans_drive(mon_gn, api_drive, api_sheets)

    print("******* table persos *********************")
    if table_persos:
        ecrire_table_persos(mon_gn, api_drive, api_sheets)
    if table_pnjs:
        ecrire_table_pnj(mon_gn, api_drive, api_sheets)
    if pnjs_dedupliques:
        creer_table_pnj_dedupliquee_sur_drive(mon_gn, api_sheets, api_drive)


    print("******* aides de jeu *********************")
    if aides_de_jeu:
        ecrire_texte_info(mon_gn, api_doc, api_drive)

    print("******* fin de la génération  *********************")


def lister_erreurs(mon_gn, prefixe, taille_min_log=0, verbal=False):
    log_erreur = ""
    # intrigues_triees = list(mon_gn.intrigues.values())
    # intrigues_triees = sorted(intrigues_triees,  key= lambda x:x.orga_referent)
    intrigues_triees = sorted(mon_gn.intrigues.values(), key=lambda x: x.orgaReferent)
    # for intrigue in gn.intrigues.values():

    current_orga = "ceci est un placeholder"
    for intrigue in intrigues_triees:
        if current_orga != intrigue.orgaReferent:
            current_orga = intrigue.orgaReferent
            log_erreur += f"{current_orga} voici les intrigues avec des soucis dans leurs tableaux de persos \n"
        if intrigue.error_log.nb_erreurs() > taille_min_log:
            # print(f"poy! {intrigue.error_log}")
            log_erreur += f"Pour {intrigue.nom} : \n" \
                          f"{intrigue.error_log} \n"
            log_erreur += suggerer_tableau_persos(mon_gn, intrigue)
            log_erreur += "\n \n"
    if verbal:
        print(log_erreur)
    if prefixe is not None:
        with open(f'{prefixe} - problèmes tableaux persos.txt', 'w', encoding="utf-8") as f:
            f.write(log_erreur)
            f.close()
    return log_erreur


def ecrire_erreurs_dans_drive(texte_erreurs, apiDoc, apiDrive, parent):
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- Listes des erreurs dans les tableaux des persos'
    mon_id = extraireTexteDeGoogleDoc.add_doc(apiDrive, nom_fichier, parent)
    if result := extraireTexteDeGoogleDoc.write_to_doc(
            apiDoc, mon_id, texte_erreurs
    ):
        extraireTexteDeGoogleDoc.formatter_fichier_erreurs(apiDoc, mon_id)
    # result = extraireTexteDeGoogleDoc.write_to_doc(apiDoc, mon_id, texte_erreurs)
    # if result:
    #     extraireTexteDeGoogleDoc.formatter_fichier_erreurs(apiDoc, mon_id)


def suggerer_tableau_persos(mon_gn: GN, intrigue: Intrigue, verbal: bool = False):
    noms_persos = mon_gn.noms_pjs()
    noms_pnjs = mon_gn.noms_pnjs()
    noms_roles_dans_tableau_intrigue = [x.personnage.nom for x in intrigue.rolesContenus.values()
                                        if not x.issu_dune_faction and x.personnage is not None]
    # print(f"noms roles dans intrigue {intrigue.nom} : {noms_roles_dans_tableau_intrigue}")
    # print("Tableau suggéré")
    # créer un set de tous les rôles de chaque scène de l'intrigue
    tous_les_noms_lus_dans_scenes = []
    for scene in intrigue.scenes:
        if scene.noms_roles_lus is not None:
            # comme on prend uniquement les roles lus, on exclut de facto les persos issus de faction
            tous_les_noms_lus_dans_scenes += scene.noms_roles_lus
    tous_les_noms_lus_dans_scenes = [x.strip() for x in tous_les_noms_lus_dans_scenes]
    tous_les_noms_lus_dans_scenes = set(tous_les_noms_lus_dans_scenes)

    tableau_sortie = []
    to_print = "Tableau suggéré : \n"

    # pour chaque nom dans une scène, trouver le personnage correspondant
    for nom in tous_les_noms_lus_dans_scenes:
        # print(str(nom))
        score_pj = process.extractOne(str(nom), noms_persos)
        score_pnj = process.extractOne(str(nom), noms_pnjs)
        if score_pj[0] in noms_roles_dans_tableau_intrigue or score_pnj[0] in noms_roles_dans_tableau_intrigue:
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
        to_print += f"{e[0]} {e[1]} \n"

    if verbal:
        print(to_print)

    return to_print


def generer_tableau_changelog_sur_drive(mon_gn: GN, api_drive, api_sheets):
    dict_orgas_persos = {}
    tableau_scene_orgas = []
    # tous_les_conteneurs = list(mon_gn.dictPJs.values()) + list(mon_gn.intrigues.values())
    # toutes_les_scenes = []
    # for conteneur in tous_les_conteneurs:
    #     for scene in conteneur.scenes:
    #         toutes_les_scenes.append(scene)
    toutes_les_scenes = mon_gn.lister_toutes_les_scenes()

    toutes_les_scenes = sorted(toutes_les_scenes, key=lambda s: s.derniere_mise_a_jour, reverse=True)

    # print(f"taille de toutes les scènes = {len(toutes_les_scenes)}"
    #       f"taille de tous les conteneurs = {len(tous_les_conteneurs)}")

    for ma_scene in toutes_les_scenes:
        for role in ma_scene.roles:
            if role.est_un_pnj():
                continue
            if role.personnage is None:
                continue
            if len(role.personnage.orgaReferent) < 3:
                orga_referent = "Orga sans nom"
            else:
                orga_referent = role.personnage.orgaReferent.strip()
            if orga_referent not in dict_orgas_persos:
                # dict_orgas_persos[role.personnage.orga_referent].append(role.personnage.nom)
                dict_orgas_persos[orga_referent] = set()
            # else:
            #     # dict_orgas_persos[role.personnage.orga_referent] = [role.personnage.nom]
            dict_orgas_persos[orga_referent].add(role.personnage.nom)

    # à ce stade là on a :
    # les scènes triées dans l'ordre de dernière modif
    # tous les orgas dans un set
    for ma_scene in toutes_les_scenes:
        dict_scene = dict()
        dict_scene['nom_scene'] = ma_scene.titre
        dict_scene['date'] = ma_scene.derniere_mise_a_jour.strftime("%Y-%m-%d %H:%M:%S")
        dict_scene['qui'] = ma_scene.modifie_par
        dict_scene['document'] = ma_scene.conteneur.get_full_url()
        dict_orgas = dict()
        # dict_scene['dict_orgas'] = dict_orgas
        for role in ma_scene.roles:
            if role.est_un_pnj():
                continue
            if role.personnage is None:
                continue
            orga_referent = role.personnage.orgaReferent.strip()
            if len(orga_referent) < 3:
                orga_referent = "Orga sans nom"
            if orga_referent not in dict_orgas:
                dict_orgas[orga_referent] = [role.personnage.nom]
            else:
                dict_orgas[orga_referent] += [role.personnage.nom]
        tableau_scene_orgas.append([dict_scene, dict_orgas])

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Changelog'
    dossier_output = mon_gn.dossier_outputs_drive
    mon_id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, dossier_output)
    extraireTexteDeGoogleDoc.exporter_changelog(tableau_scene_orgas, mon_id, dict_orgas_persos, api_sheets)
    extraireTexteDeGoogleDoc.supprimer_feuille_1(api_sheets, mon_id)


def creer_table_intrigues_sur_drive(mon_gn: GN, api_sheets, api_drive):
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
                                intrigue.error_log.nb_erreurs(),
                                intrigue.get_full_url()])

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Etat des intrigues'
    dossier_export = mon_gn.dossier_outputs_drive
    mon_id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, dossier_export)
    # extraire_texte_de_google_doc.exporter_table_intrigue(api_doc, nom_fichier, dossier_export, df)
    # extraire_texte_de_google_doc.ecrire_table_google_sheets(api_sheets, df, mon_id)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table_intrigues, mon_id)


def creer_table_pnj_dedupliquee_sur_drive(mon_gn: GN, api_sheets, api_drive):
    table_pnj = [["Nom"]]
    for nom in generer_liste_pnj_dedup(mon_gn):
        table_pnj.append([nom])

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Suggestion liste PNJs dédupliqués'
    dossier_export = mon_gn.dossier_outputs_drive
    mon_id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, dossier_export)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table_pnj, mon_id)


def generer_squelettes_dans_drive(mon_GN: GN, api_doc, api_drive, pj=True):
    parent = mon_GN.dossier_outputs_drive
    pj_pnj = "PJ" if pj else "PNJ"
    nom_dossier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Squelettes {pj_pnj}'
    nouveau_dossier = extraireTexteDeGoogleDoc.creer_dossier(api_drive, parent, nom_dossier)

    d = squelettes_par_perso(mon_GN, pj=pj)
    for nom_perso in d:
        # créer le fichier et récupérer l'ID
        nom_fichier = f'{nom_perso} - squelette au {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}'
        texte = d[nom_perso]

        extraireTexteDeGoogleDoc.inserer_squelettes_dans_drive(nouveau_dossier, api_doc, api_drive, texte, nom_fichier)


def squelettes_par_perso(mon_gn, pj=True):
    squelettes_persos = {}
    if pj:
        liste_persos_source = mon_gn.dictPJs.values()
    else:
        liste_persos_source = mon_gn.dictPNJs.values()

    for perso in liste_persos_source:
        print(f"génération du texte des persos : personnage en cours de lecture : {perso.nom}")
        # for personnage in gn.dictPJs.values():
        texte_perso = ""
        texte_perso += f"Début du squelette pour {perso.nom} (Orga Référent : {perso.orgaReferent}) : \n"
        texte_perso += f"résumé de la bio : \n"
        for item in perso.description:
            texte_perso += f"{item} \n"
        texte_perso += f"Psychologie : \n"
        for item in perso.concept:
            texte_perso += f"{item} \n"
        texte_perso += f"Motivations et objectifs : \n"
        print(f"driver avant insertion {perso.driver}")
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

        mes_scenes = Scene.trier_scenes(mes_scenes, date_gn=mon_gn.date_gn)
        for scene in mes_scenes:
            # print(scene)
            texte_perso += scene.str_pour_squelette(mon_gn.date_gn) + '\n'
        texte_perso += '****************************************************** \n'
        squelettes_persos[perso.nom] = texte_perso

    return squelettes_persos


def ecrire_squelettes_localement(mon_gn: GN, prefixe=None, pj=True):
    squelettes_persos = squelettes_par_perso(mon_gn, pj)
    toutes_scenes = "".join(squelettes_persos.values())

    if prefixe is not None:
        with open(prefixe + ' - squelettes.txt', 'w', encoding="utf-8") as f:
            f.write(toutes_scenes)
            f.close()

    return toutes_scenes


def generer_liste_pnj_dedup(monGN, threshold=89, verbal=False):
    noms_pnjs = []
    # nomsNormalises = dict()
    for intrigue in monGN.intrigues.values():
        for role in intrigue.rolesContenus.values():
            if role.est_un_pnj():
                noms_pnjs.append(role.nom)
    noms_pnjs = list(set(noms_pnjs))
    extract = process.dedupe(noms_pnjs, threshold=threshold)
    extract = sorted(extract)

    logging.debug(f"liste des pnjs dédup : {extract}")

    if verbal:
        for v in extract:
            print(v)
    return extract


def ecrire_liste_pnj_dedup_localement(mon_gn: GN, prefixe: str, threshold=89, verbal=False):
    to_print = '\n'.join(generer_liste_pnj_dedup(mon_gn, threshold, verbal))
    if prefixe is not None:
        with open(f"{prefixe} - liste_pnjs_dedupliqués.txt", 'w', encoding="utf-8") as f:
            f.write(to_print)
            f.close()


def generer_changelog(monGN, prefixe, nbJours=1, verbal=False):
    date_reference = datetime.date.today() - datetime.timedelta(days=nbJours)

    # on crée un tableau avec tous lse changements :
    # [orga referent | personnage | titre intrigue | url intrigue | date changement intrigue]
    # structure souhaitée :
    # orga referent / persos / titre intrigue/ url intrigue | date changement intrigue

    restitution = dict()
    for intrigue in monGN.intrigues.values():
        if intrigue.lastFileEdit.date() > date_reference:
            for role in intrigue.rolesContenus.values():
                if role.personnage is not None and est_un_pj(role.personnage.pj):
                    referent = role.personnage.orgaReferent.strip()

                    if len(referent) < 3:
                        referent = "Orga sans nom"

                    # print(f"je m'apprête à ajouter une ligne pour {referent} : {role.personnage.nom} dans {intrigue.nom}")
                    nom_perso = role.personnage.nom
                    # nomIntrigue = intrigue.nom

                    # on vérifie que le référent et le personnage existent, sinon on initialise
                    if referent not in restitution:
                        restitution[referent] = dict()
                    if nom_perso not in restitution[referent]:
                        # restitution[referent][nom_perso] = dict()
                        restitution[referent][nom_perso] = []
                    # if nomIntrigue not in restitution[referent][nom_perso]:
                    #     restitution[referent][nom_perso][nomIntrigue] = \
                    #         [intrigue.lastProcessing.strftime("%d/%m/%Y à %H:%M:%S"),
                    #          intrigue.get_full_url()]
                    # # on utilise nomintrigue comem clef,
                    # # car sinon, comme on rentre par les roles on va multiplier les entrées

                    # et maintenant on remplit la liste
                    restitution[referent][nom_perso].append([intrigue.nom,
                                                             intrigue.get_full_url(),
                                                             intrigue.lastFileEdit.strftime("%d/%m/%Y à %H:%M:%S")])

                    # print(restitution)
                    # restitution.append([role.personnage.orga_referent,
                    #                     role.personnage.nom,
                    #                     intrigue.titre,
                    #                     intrigue.get_full_url(),
                    #                     intrigue.lastProcessing])
    # print(restitution)
    texte = ""
    for nomOrga in restitution:
        texte += f"{nomOrga}, ces personnages sont dans des intrigues qui ont été modifiées " \
                 f"depuis {date_reference} : \n"
        for perso in restitution[nomOrga]:
            texte += f"\t pour {perso} : \n "
            for element in restitution[nomOrga][perso]:
                # texte += f"\t\t l'intrigue {restitution[nomOrga][personnage][0]} \n " \
                #          f"\t\t a été modifiée le {restitution[nomOrga][personnage][2]} \n" \
                #          f"\t\t (url : {restitution[nomOrga][personnage][1]}) \n"
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
    for perso in dict_config['dossiers_pjs']:
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
    to_return = [['code', 'description', 'Avec FX?', 'FX', 'Débute Où?', 'fourni par Qui?', 'utilisé où?',
                  'fiche objet trouvée?']]

    for intrigue in monGN.intrigues.values():
        for objet in intrigue.objets:
            code = objet.code.replace('\n', '\v')
            description = objet.description.replace('\n', '\v')
            avecfx = objet.avec_fx()
            fx = objet.specialEffect.replace('\n', '\v')
            debuteou = objet.emplacementDebut.replace('\n', '\v')
            fournipar = objet.fourniParJoueur.replace('\n', '\v')
            # code = objet.code.replace('\n', "***")
            # description = objet.description.replace('\n', "***")
            # avecfx = objet.avec_fx()
            # fx = objet.specialEffect.replace('\n', "***")
            # debuteou = objet.emplacementDebut.replace('\n', "***")
            # fournipar = objet.fourniParJoueur.replace('\n', "***")
            utiliseou = [x.nom for x in objet.inIntrigues]
            to_return.append([f"{code}",
                              f"{description}",
                              f"{avecfx}",
                              f"{fx}",
                              f"{debuteou}",
                              f"{fournipar}",
                              f"{utiliseou}",
                              "fonction non développée"]
                             )
    return to_return


def ecrire_table_objet_dans_drive(mon_gn: GN, api_drive, api_sheets):
    parent = mon_gn.dossier_outputs_drive
    table = generer_table_objets(mon_gn)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- Table des objets'
    mon_id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, parent)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table, mon_id)


def generer_table_chrono_condensee_raw(gn: GN):
    # pour chaque personnage, construire un tableau contenant, dans l'ordre chronologique,
    # toutes les scènes du personnage avec le texte "il y a..., titrescène"
    tableau_sortie = []
    for perso in list(gn.dictPJs.values()) + list(gn.dictPNJs.values()):
        mes_scenes = []
        for role in perso.roles:
            for scene in role.scenes:
                # print(f"{scene.titre} trouvée")
                mes_scenes.append(scene)
        mes_scenes = Scene.trier_scenes(mes_scenes, date_gn=gn.date_gn)

        # créer des lignes [date][évènement]
        # ma_ligne = [personnage.nom] + [[s.get_formatted_date(date_gn=gn.date_gn), s.titre] for s in mes_scenes]
        ma_ligne = [perso.nom] + mes_scenes
        tableau_sortie.append(ma_ligne)

    return tableau_sortie


def generer_table_chrono_condensee(tableau_raw, date_gn):
    # tableau_formatte = []
    # for ligne in tableau_raw:
    #     tableau_formatte += [ligne[0]] + [[f"{event[0]} - {event[1]}"] for event in ligne[1:]]
    #
    # # mettre tous les noms dans une matrice et remplir les moins longs par ""
    # # find the length of the longest list
    # max_len = max(len(lst) for lst in tableau_formatte)
    # print(f"tableau formatté = {tableau_formatte}")
    #
    # # pad the shorter lists with zeros
    # matrice = [lst + [""] * (max_len - len(lst)) for lst in tableau_formatte]
    #
    # # transpose the list of lists
    # to_return = [list(row) for row in zip(*matrice)]
    # return to_return

    # Get the maximum number of events among all stories
    max_len = max(len(story) - 1 for story in tableau_raw)

    # Initialize the matrix with the first row being the story titles
    matrix = [[story[0] for story in tableau_raw]]

    # Iterate over the range of events
    for i in range(max_len):
        # Initialize a row for the current event
        row = []

        # Iterate over all stories
        for story in tableau_raw:
            # If the current story has an event for the current date, add the formatted date and event
            if i + 1 < len(story):
                # date, event = story[i + 1]
                # row.append(f"{date} - {event}")
                date = story[i + 1].get_formatted_date(date_gn=date_gn)
                event = f"{story[i + 1].titre} \n ({story[i + 1].conteneur.nom})"
                # event = story[i + 1].titre
                row.append(f"{date} - {event}")
            # Otherwise, add an empty string
            else:
                row.append("")
        # Add the current row to the matrix
        matrix.append(row)

    return matrix


def generer_table_chrono_complete(table_raw, date_gn):
    # # Find all unique dates across all stories
    # all_dates = set()
    # for story in table_raw:
    #     all_dates |= set([event[0] for event in story[1:]])
    # all_dates = sorted(list(all_dates), key=extraireTexteDeGoogleDoc.calculer_jours_il_y_a)

    # Find all unique dates across all stories
    # all_scenes = set()
    # for story in table_raw:
    #     all_dates |= set([scene for scene in story[1:]])
    # all_dates = sorted(list(all_dates), key=lambda scene: scene.clef_tri(date_gn))

    all_scenes = []
    for ligne in table_raw:
        all_scenes += list(ligne[1:])
        # all_scenes += [scene for scene in ligne[1:]]
    all_scenes = Scene.trier_scenes(all_scenes, date_gn=date_gn)

    # all_date = set()
    # for scene in all_scenes:
    #     print(f"clef-formatted-titre = {scene.clef_tri(date_gn)} / {scene.get_formatted_date(date_gn=date_gn)} / {scene.titre}")
    #     all_date.add(scene.get_formatted_date(date_gn=date_gn))

    dates = []
    seen = set()
    for scene in all_scenes:
        date = scene.get_formatted_date(date_gn=date_gn)
        if date not in seen:
            seen.add(date)
            dates.append(date)
    #
    # for date in dates:
    #     print(f"date triée (normalement) = {date}")

    # all_dates = []
    # for scene in all_scenes:
    #     all_dates.append(scene.get_formatted_date(date_gn=date_gn))
    # all_dates = set(all_dates)

    # Create a dictionary mapping dates to indices
    date_to_index = {date: i for i, date in enumerate(dates)}
    print(f"date_to_index = {date_to_index}")
    # Initialize the matrix with empty values
    num_stories = len(table_raw)
    num_dates = len(dates)
    # matrix = [['' for j in range(num_stories + 1)] for i in range(num_dates + 1)]
    matrix = [['' for _ in range(num_stories + 1)] for _ in range(num_dates + 1)]

    # Populate the first row with story titles
    for j, story in enumerate(table_raw):
        matrix[0][j + 1] = story[0]

    # Populate the first column with dates
    for i, date in enumerate(dates):
        matrix[i + 1][0] = date

    # Fill in the events
    for j, story in enumerate(table_raw):
        for event in story[1:]:
            i = date_to_index[event.get_formatted_date(date_gn=date_gn)]
            matrix[i + 1][j + 1] = '\n'.join([matrix[i + 1][j + 1], f"{event.titre} \n ({event.conteneur.nom})"])

    return matrix

def generer_table_chrono_scenes(mon_gn: GN):
    # Dates	Horaires	Episodes / Intrigues	Titre	Evênement	PJ concernés	PNJ concernés
    toutes_scenes = Scene.trier_scenes(mon_gn.lister_toutes_les_scenes())
    to_return = [['Date', 'Intrigue', 'Scène', 'PJs concernés', 'PNJ, concernés']]

    # for scene in toutes_scenes:
    #     logging.debug(f"scene = {scene.titre} *******************************************")
    #     for role in scene.roles:
    #         logging.debug(f"\t role = {role.nom} est issu d'une faction : {role.issu_dune_faction}")
    #         logging.debug(f"\t \t personnage = {role.personnage}")
    #         logging.debug(f"\t \t \t nom personnage = {role.personnage.nom}")

    for scene in toutes_scenes:
        to_return.append([
            scene.get_formatted_date(mon_gn.date_gn),
            scene.conteneur.nom,
            scene.titre,
            ', '.join([role.personnage.nom for role in scene.roles if role is not None and role.est_un_pj()]),
            ', '.join([role.personnage.nom for role in scene.roles if role is not None and role.est_un_pnj()]),
        ])
    return to_return


def ecrire_table_chrono_dans_drive(mon_gn: GN, api_drive, api_sheets):
    parent = mon_gn.dossier_outputs_drive
    table_raw = generer_table_chrono_condensee_raw(mon_gn)
    table_simple = generer_table_chrono_condensee(table_raw, mon_gn.date_gn)
    table_complete = generer_table_chrono_complete(table_raw, mon_gn.date_gn)
    table_chrono_scenes = generer_table_chrono_scenes(mon_gn)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- synthèse chrono'
    file_id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, parent)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table_simple, file_id, feuille="condensée")
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table_complete, file_id, feuille="étendue")
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table_chrono_scenes, file_id,
                                                        feuille="toutes les scènes")
    extraireTexteDeGoogleDoc.supprimer_feuille_1(api_sheets, file_id)


def generer_tableau_recap_persos(gn: GN):
    # to_return = []
    to_return = [["Nom Perso", "Orga Référent", "Points", "Intrigues"]]
    for perso in gn.dictPJs.values():
        table_perso = [perso.nom]
        table_perso += [perso.orgaReferent]
        table_perso += [perso.sommer_pip()]
        for role in perso.roles:
            table_perso += [role.conteneur.nom]
        to_return.append(table_perso)
    return to_return


def ecrire_table_persos(mon_gn: GN, api_drive, api_sheets):
    parent = mon_gn.dossier_outputs_drive
    table = generer_tableau_recap_persos(mon_gn)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- synthèse des intrigues par personnage'
    file_id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, parent)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table, file_id)


def generer_table_pnjs_etendue(gn: GN, verbal=False):
    table_pnj = [["nom PNJ", "description",
                  "type_pj",
                  "niveau implication",
                  "details intervention",
                  "intrigue", "nom dans l'intrigue"]]


    # print("ping table pnj")
    # print(f"pnjs contenus : {gn.dictPNJs.keys()}")

    for pnj in gn.dictPNJs.values():
    #     print(f"{pnj.nom}")
    #     for role in pnj.roles:
    #         print(f"table pnj : pnj en cours d'ajout : {pnj.nom}")
    #         print(f"{pnj.nom}")
    #         print(f"{role.description}")
    #         print(f"{pnj.string_type_pj()}")
    #         print(f"{role.niveauImplication}")
    #         print(f"{role.perimetre_intervention}")
    #         print(f"{role.conteneur.nom}")
    #         print(f"{role.nom}")

        table_pnj.extend(
            [
                pnj.nom,
                role.description,
                pnj.string_type_pj(),
                role.niveauImplication,
                role.perimetre_intervention,
                role.conteneur.nom,
                role.nom
            ]
            for role in pnj.roles
        )
    if verbal:
        print(table_pnj)

    return table_pnj


def generer_table_pnjs_simple(gn: GN, verbal=False):
    table_pnj = [["nom PNJ",
                  "type_pj",
                  "intrigues"]]

    logging.debug(f"pnjs contenus : {gn.dictPNJs.keys()}")

    table_pnj.extend(
        [
            pnj.nom,
            pnj.string_type_pj(),
            pnj.toutes_les_apparitions(),
        ]
        for pnj in gn.dictPNJs.values()
    )

    if verbal:
        for pnj in gn.dictPNJs.values():
            print(f"{pnj.nom}")
            for role in pnj.roles:
                print(f"table pnj : pnj en cours d'ajout : {pnj.nom}")
                print(f"{pnj.nom}")
                print(f"{role.description}")
                print(f"{pnj.string_type_pj()}")
                print(f"{role.niveauImplication}")
                print(f"{role.perimetre_intervention}")
                print(f"{role.conteneur.nom}")
                print(f"{role.nom}")

    if verbal:
        print(table_pnj)

    return table_pnj


def ecrire_table_pnj(mon_gn: GN, api_drive, api_sheets):
    parent = mon_gn.dossier_outputs_drive
    table_etendue = generer_table_pnjs_etendue(mon_gn)
    table_simple = generer_table_pnjs_simple(mon_gn)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- table des PNJs'
    file_id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, parent)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table_simple, file_id)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table_etendue, file_id, feuille="détaillée")


def generer_textes_infos(gn: GN):
    # on crée un dictionnaire avec toutes les scènes par infos
    dict_infos = {}
    for scene in gn.lister_toutes_les_scenes():
        for info in scene.infos:
            if info in dict_infos:
                dict_infos[info].append(scene)
            else:
                dict_infos[info] = [scene]

    # on met toutes les scènes dans une string
    to_return = ""
    for info in dict_infos:
        to_return += f"Scènes associées à {info} : \n"
        for scene in dict_infos[info]:
            to_return += scene.str_pour_squelette() + '\n'
        to_return += '***************************** \n'
    return to_return


def ecrire_texte_info(mon_GN: GN, api_doc, api_drive):
    parent = mon_GN.dossier_outputs_drive

    texte = generer_textes_infos(mon_GN)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- données pour aides de jeu'
    mon_id = extraireTexteDeGoogleDoc.add_doc(api_drive, nom_fichier, parent)
    extraireTexteDeGoogleDoc.write_to_doc(
        api_doc, mon_id, texte
    )


def mettre_a_jour_champs(gn: GN):
    # #mise à jour des errors logs
    # for conteneur in list(gn.dictPJs.values()) + list(gn.dictPNJs.values()) + list(gn.intrigues.values()):
    #     conteneur.error_log.clear()
    #     print(f"pour le conteneur {conteneur}, errorlog = {conteneur.error_log}")

    # mise à jour des formats de date et des factions
    if not hasattr(gn, 'date_gn'):
        gn.date_gn = None
    if not hasattr(gn, 'factions'):
        gn.factions = {}
    if not hasattr(gn, 'id_factions'):
        gn.id_factions = None
    if hasattr(gn, 'liste_noms_pjs'):
        delattr(gn, 'liste_noms_pjs')
    if hasattr(gn, 'liste_noms_pnjs'):
        delattr(gn, 'liste_noms_pnjs')
    if not hasattr(gn, 'id_pjs_et_pnjs'):
        gn.id_pjs_et_pnjs = None
    if not hasattr(gn, 'fichier_pnjs'):
        gn.fichier_pnjs = None

    for conteneur in list(gn.dictPJs.values()) \
                     + list(gn.dictPNJs.values()) \
                     + list(gn.intrigues.values()):
        for scene in conteneur.scenes:
            if not hasattr(scene, 'date_absolue'):
                scene.date_absolue = None
            # print(f"la scène {scene.titre}, dateba absolue = {scene.date_absolue}")

    for intrigue in gn.intrigues.values():
        for objet in intrigue.objets:
            if not hasattr(objet, 'code'):
                objet.code = ""
            if hasattr(objet, 'rfid'):
                delattr(objet, 'rfid')

    for conteneur in list(gn.dictPJs.values()) \
                     + list(gn.dictPNJs.values()) \
                     + list(gn.intrigues.values()):
        for role in conteneur.rolesContenus.values():
            print(f"clefs (2) pour {role.nom} = {vars(role).keys()}")
            if hasattr(role, 'perimetreIntervention'):
                if not hasattr(role, 'perimetre_intervention'):
                    role.perimetre_intervention = role.perimetreIntervention
                delattr(role, 'perimetreIntervention')
                print(f"PerimetreIntervention supprimé pour {role.nom}")

            if hasattr(role, 'perimetre_Intervention'):
                if not hasattr(role, 'perimetre_intervention'):
                    role.perimetre_intervention = role.perimetre_Intervention
                delattr(role, 'perimetre_Intervention')

    for scene in gn.lister_toutes_les_scenes():
        if not hasattr(scene, 'infos'):
            scene.infos = set()
