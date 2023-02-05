import configparser
import os

import extraireTexteDeGoogleDoc
import lecteurGoogle
from modeleGN import *
import dateparser

# communication :
# todo :informer chalacta des factions,
#  des squelettes pnjs, des tableaux intrigues, des nouveaux tableaux de synthèse (objets / chrono / persos),
#  des nouveaux fichiers d'erruers, du tag questionnaire

# bugs
# todo comprendre pourquoi pas de load de snyder
# todo vérifier le focntionnement de la balise questionnaire perso



# à faire
# todo : gestion des évènement
#  lire les fiches > on lit le tableau > on met dans un dictionnaire > on utilise get pour prendre ce qui nous intéresse
#  les appeler à partir des intrigues dans un tableau 'scène nécessaure / onm évènement)

# todo : ajouter une section "tableau relations" qui conteint toutjours 4 colonnes
#  "X... Voit la relation avec... Comme... Et si non réciproque..."
#  dans les fiches de persos
#  dans les scènes : relations nécessaires (nouveau tag)

# refaire tableau objet 6 colonnes
# refaire une focntion de mise à jour globale qui met à jour les dates, les objets

# confort / logique
# todo : refaire version console
# todo : webisation des pjs et PNJs > créer une sheet avec le nom des pjs sur un onglet, et le nom des PNJ sur l'autre

# todo : faire un menu qui crée le GN avec les options et crée tous les fichiers qui vont bien
#  dans un dossier magnet du drive fourni en entrée, et des questions sous la forme de "allez-vous utiliser...?"
#  pour déterminer les champs à créer

# todo : permettre d'utiliser un tableau récap comme dans l'exemple de sandrine avec une balise tableau récap ?


def charger_fichier_init(fichier_init: str):
    # init configuration
    config = configparser.ConfigParser()
    config.read(fichier_init)

    dict_config = dict()
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

        dict_config['id_factions'] = config.get('Optionnels', 'id_factions')

        dict_config['fichier_noms_pnjs'] = config.get('Optionnels', 'nom_fichier_pnjs')

        dict_config['liste_noms_pjs'] = [nom_p.strip()
                                         for nom_p in config.get('Optionnels', 'noms_persos').split(',')]

        texte_date_gn = config.get('Optionnels', 'date_gn').strip()
        if texte_date_gn is not None :
            print(f"texte_date_gn = {texte_date_gn} / {type(texte_date_gn)}")
            dict_config['date_gn'] = dateparser.parse(texte_date_gn, languages=['fr'])
            print(f"date_gn formattée = {dict_config['date_gn']}")
        print(f"pour ce GN, date_gn = {dict_config['date_gn']}")

        # création des champs dérivés
        dict_config['liste_noms_pnjs'] = lire_fichier_pnjs(dict_config['fichier_noms_pnjs'])

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
    except FileNotFoundError:
        print(f"Le fichier {nom_fichier} - {os.getcwd()} n'a pas été trouvé.")
    return to_return


def lire_et_recharger_gn(mon_gn: GN, api_drive, api_doc, api_sheets, nom_fichier_sauvegarde: str,
                         sans_chargement_fichier=False,
                         sauver_apres_operation=True,
                         noms_pjs=None, noms_pnjs=None,
                         fichier_erreurs: bool = True,
                         generer_fichiers_pjs: bool = True,
                         generer_fichiers_pnjs: bool = True,
                         changelog: bool = True, table_intrigues: bool = True, table_objets: bool = True,
                         table_chrono: bool = True, table_persos: bool = True,
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
            mon_gn.id_factions
        )
        mon_gn = new_gn
    else:
        mon_gn.effacer_personnages_forces()

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

    if noms_pjs:
        mon_gn.forcer_import_pjs(noms_pjs, verbal=verbal)
        print("début du forçage des PJs")
        mon_gn.forcer_import_pnjs(noms_pnjs, verbal=verbal)
    if noms_pnjs:
        print("début du forçage des PNJs")
        mon_gn.forcer_import_pnjs(noms_pnjs, verbal=verbal)

    extraireTexteDeGoogleDoc.extraire_factions(mon_gn, apiDoc=api_doc, verbal=verbal)
    # print(f"mon_gn.factions = {mon_gn.factions}")

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
        # genererChangeLog(mon_gn, prefixe_fichiers, nbJours=3)
        # genererChangeLog(mon_gn, prefixe_fichiers, nbJours=4)

    print("*********touslesquelettes*******************")
    if generer_fichiers_pjs:
        generer_squelettes_dans_drive(mon_gn, api_doc, api_drive, pj=True)
    if generer_fichiers_pnjs:
        generer_squelettes_dans_drive(mon_gn, api_doc, api_drive, pj=False)

    ecrire_squelettes_localement(mon_gn, prefixe_fichiers)
    ecrire_squelettes_localement(mon_gn, prefixe_fichiers, pj=False)
    print("*******dumpallscenes*********************")
    # dumpAllScenes(mon_gn)

    print("******* table objets *********************")
    if table_objets:
        ecrire_table_objet_dans_drive(mon_gn, api_drive, api_sheets)

    print("******* table planning *********************")
    if table_chrono:
        ecrire_table_chrono_dans_drive(mon_gn, api_drive, api_sheets)

    print("******* table persos *********************")
    if table_persos:
        ecrire_table_persos(mon_gn, api_drive, api_sheets)
    print("******* fin de la génération  *********************")


def lister_erreurs(mon_gn, prefixe, taille_min_log=0, verbal=False):
    log_erreur = ""
    intrigues_triees = [intrigue for intrigue in mon_gn.intrigues.values()]
    # intrigues_triees = sorted(intrigues_triees,  key= lambda x:x.orgaReferent)
    intrigues_triees = sorted(mon_gn.intrigues.values(), key=lambda x: x.orgaReferent)
    # for intrigue in mon_gn.intrigues.values():

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
        with open(prefixe + ' - problèmes tableaux persos.txt', 'w', encoding="utf-8") as f:
            f.write(log_erreur)
            f.close()
    return log_erreur


def ecrire_erreurs_dans_drive(texte_erreurs, apiDoc, apiDrive, parent):
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- Listes des erreurs dans les tableaux des persos'
    mon_id = extraireTexteDeGoogleDoc.add_doc(apiDrive, nom_fichier, parent)
    result = extraireTexteDeGoogleDoc.write_to_doc(apiDoc, mon_id, texte_erreurs)
    if result:
        extraireTexteDeGoogleDoc.formatter_fichier_erreurs(apiDoc, mon_id)


def suggerer_tableau_persos(mon_gn: GN, intrigue: Intrigue, verbal: bool = False):
    noms_persos = mon_gn.noms_pjs()
    noms_pnjs = mon_gn.noms_pnjs()
    noms_roles_dans_tableau_intrigue = [x.perso.nom for x in intrigue.rolesContenus.values()
                                        if not x.issu_dune_faction and x.perso is not None]
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

    # pour chaque nom dans une scène, trouver le perso correspondant
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
    dict_orgas_persos = dict()
    tableau_scene_orgas = []
    tous_les_conteneurs = list(mon_gn.dictPJs.values()) + list(mon_gn.intrigues.values())
    toutes_les_scenes = []
    for conteneur in tous_les_conteneurs:
        for scene in conteneur.scenes:
            toutes_les_scenes.append(scene)

    toutes_les_scenes = sorted(toutes_les_scenes, key=lambda s: s.derniere_mise_a_jour, reverse=True)

    # print(f"taille de toutes les scènes = {len(toutes_les_scenes)}"
    #       f"taille de tous les conteneurs = {len(tous_les_conteneurs)}")

    for ma_scene in toutes_les_scenes:
        for role in ma_scene.roles:
            if role.est_un_pnj():
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
            if role.est_un_pnj():
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
    dossier_output = mon_gn.dossier_outputs_drive
    mon_id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, dossier_output)
    extraireTexteDeGoogleDoc.exporter_changelog(tableau_scene_orgas, mon_id, dict_orgas_persos, api_sheets)


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
                                intrigue.getFullUrl()])

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Etat des intrigues'
    dossier_export = mon_gn.dossier_outputs_drive
    mon_id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, dossier_export)
    # extraire_texte_de_google_doc.exporter_table_intrigue(api_doc, nom_fichier, dossier_export, df)
    # extraire_texte_de_google_doc.ecrire_table_google_sheets(api_sheets, df, mon_id)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table_intrigues, mon_id)


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


def squelettes_par_perso(mon_gn, pj=True):
    squelettes_persos = {}
    if pj:
        liste_persos_source = mon_gn.dictPJs.values()
    else:
        liste_persos_source = mon_gn.dictPNJs.values()

    for perso in liste_persos_source:
        print(f"génération du texte des persos : perso en cours de lecture : {perso.nom}")
        # for perso in mon_gn.dictPJs.values():
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
    date_reference = datetime.date.today() - datetime.timedelta(days=nbJours)

    # on crée un tableau avec tous lse changements :
    # [orga referent | perso | titre intrigue | url intrigue | date changement intrigue]
    # structure souhaitée :
    # orga referent / persos / titre intrigue/ url intrigue | date changement intrigue

    restitution = dict()
    for intrigue in monGN.intrigues.values():
        if intrigue.lastFileEdit.date() > date_reference:
            for role in intrigue.rolesContenus.values():
                if role.perso is not None and est_un_pj(role.perso.pj):
                    referent = role.perso.orgaReferent.strip()

                    if len(referent) < 3:
                        referent = "Orga sans nom"

                    # print(f"je m'apprête à ajouter une ligne pour {referent} : {role.perso.nom} dans {intrigue.nom}")
                    nom_perso = role.perso.nom
                    # nomIntrigue = intrigue.nom

                    # on vérifie que le référent et le perso existent, sinon on initialise
                    if referent not in restitution:
                        restitution[referent] = dict()
                    if nom_perso not in restitution[referent]:
                        # restitution[referent][nom_perso] = dict()
                        restitution[referent][nom_perso] = []
                    # if nomIntrigue not in restitution[referent][nom_perso]:
                    #     restitution[referent][nom_perso][nomIntrigue] = \
                    #         [intrigue.lastProcessing.strftime("%d/%m/%Y à %H:%M:%S"),
                    #          intrigue.getFullUrl()]
                    # # on utilise nomintrigue comem clef,
                    # # car sinon, comme on rentre par les roles on va multiplier les entrées

                    # et maintenant on remplit la liste
                    restitution[referent][nom_perso].append([intrigue.nom,
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
        texte += f"{nomOrga}, ces personnages sont dans des intrigues qui ont été modifiées " \
                 f"depuis {date_reference} : \n"
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
        # ma_ligne = [perso.nom] + [[s.get_formatted_date(date_gn=gn.date_gn), s.titre] for s in mes_scenes]
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
                event = story[i + 1].titre
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
    all_dates = set()
    for story in table_raw:
        all_dates |= set([scene for scene in story[1:]])
    all_dates = sorted(list(all_dates), key=lambda scene: scene.clef_tri(date_gn))


    # Create a dictionary mapping dates to indices
    date_to_index = {scene.get_formatted_date(date_gn=date_gn): i for i, scene in enumerate(all_dates)}

    # Initialize the matrix with empty values
    num_stories = len(table_raw)
    num_dates = len(all_dates)
    # matrix = [['' for j in range(num_stories + 1)] for i in range(num_dates + 1)]
    matrix = [['' for _ in range(num_stories + 1)] for _ in range(num_dates + 1)]

    # Populate the first row with story titles
    for j, story in enumerate(table_raw):
        matrix[0][j + 1] = story[0]

    # Populate the first column with dates
    for i, scene in enumerate(all_dates):
        matrix[i + 1][0] = scene.get_formatted_date(date_gn=date_gn)

    # Fill in the events
    for j, story in enumerate(table_raw):
        for event in story[1:]:
            i = date_to_index[event.get_formatted_date(date_gn=date_gn)]
            matrix[i + 1][j + 1] = '\n'.join([matrix[i + 1][j + 1], event.titre])

    return matrix


def ecrire_table_chrono_dans_drive(mon_gn: GN, api_drive, api_sheets):
    parent = mon_gn.dossier_outputs_drive
    table_raw = generer_table_chrono_condensee_raw(mon_gn)
    table_simple = generer_table_chrono_condensee(table_raw, mon_gn.date_gn)
    table_complete = generer_table_chrono_complete(table_raw, mon_gn.date_gn)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- synthèse chrono'
    file_id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, parent)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table_simple, file_id, feuille="condensée")
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table_complete, file_id, feuille="étendue")


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
                  f'- synthèse des intrigues par perso'
    file_id = extraireTexteDeGoogleDoc.creer_google_sheet(api_drive, nom_fichier, parent)
    extraireTexteDeGoogleDoc.ecrire_table_google_sheets(api_sheets, table, file_id)


def mettre_a_jour_champs(gn: GN):
    # #mise à jour des errors logs
    # for conteneur in list(gn.dictPJs.values()) + list(gn.dictPNJs.values()) + list(gn.intrigues.values()):
    #     conteneur.error_log.clear()
    #     print(f"pour le conteneur {conteneur}, errorlog = {conteneur.error_log}")

    # mise à jour des formats de date
    if not hasattr(gn, 'date_gn'):
        gn.date_gn = None
    for conteneur in list(gn.dictPJs.values()) \
                     + list(gn.dictPNJs.values()) \
                     + list(gn.intrigues.values()):
        for scene in conteneur.scenes:
            if not hasattr(scene, 'date_absolue'):
                scene.date_absolue = None
            print(f"la scène {scene.titre}, dateba absolue = {scene.date_absolue}")
