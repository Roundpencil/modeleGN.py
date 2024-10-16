import csv
import os
import traceback

import createur_planning_evenementiel as cpe
import google_io as g_io
from modeleGN import *


# communication :
# A venir (prochaine version)
# Suppression du besoin de télécharger le fichier mgn : l’interface proposera à l’utilisateur une liste des GNs
# auxquel il a accès et réalisera toutes les opérations.
# Optimisation de la gestion des factions
#
# Nouveaux paramètres pour optimiser la généraition du planning :
# -Ajout d’un paramètre nb_aides  > si spécifié, tentative de forcer ce nombre d'aides lors de la génération du planning
# -Ajout d’un paramètre pas_evenement pour déterminer l’unité de temps entre deux évènements
# (aujourd’hui calculé automatiquement) (plus grand pas > plus grand tableau >
# plus grande durée de génération du planning)
# -Ajout d’un nouvel onglet dans les fichiers de casting
# (joueurs venant aider pour faire PNJ) pour personnaliser les planning PNJs
# -Ajout d’un paramètre sessions_à_generer pour savoir quels casting on affiche,
# et quels planning sont à générer si volonté de ne pas tout générer
# -Ajout d’un paramètre pour prendre en compte le nombre de PNJs si celui-ci est connu

# interfaces de constructions

# tester

# bugs

# à faire - rapide
# todo :
#  nouveau paramètre : NB_aides  > si spécifié, tentative de forcer ce nombre d'aides en amont du calcul si ok > utiliser respecter nb aides
#  nouveau paramètre : pas_evenement pour forcer taille pas. Dire dans le manuel plus grand pas > plus grand tableau > plus grande longueur de solveur
#  nouvel onglet dans les fichiers de castings : aides par sessions (plutot que de prendre les pré-affectation) et les utiliser
#  nouveau paramètre à ajouter : sessions_à_generer pour savoir quels casting on affiche, et quel génération on fait

# todo : vérifier qu'on peut choisir de 'nutiliser MAGnet que pour les évènements

# Module Photo
# todo : permettre de marcher avec un mgn pour qu'il n'y ait qu'un seul fichier pour les utilisateurs MAGnet
# todo : proposer une architecture qui permet à la fois de stoquer un configparser dans le GN et d'être rétrocompatible
# todo : rajouter un champ pour dire qu'on ne veut mettre que les photos des PJs ?

# utilité du code
# todo : regarder s'il faut supprimer perimetre_intervention dans Role, qui fait doublon avec le type de personnage
# todo : changer tous les paramètres de MAGnet_lib par une classe ou un dictionnaire pour accelérer le design
#   vérifier l'usage de la GUI 3 qui utilise can write

# à faire - plus long
# todo : faire quelque part une liste de tous les dossiers ou se trouvent des *.mng
#  vérifier auxquels a acces l'utilisateur quand il lance le programme, puis lui proposer de télécahrger les siens.
#  objectifs : se passer et du fichier de config, et de la nécessité de télécharger un mgn
#  quand on vérifie la validité du dict config du fichier GN, en profiter pour le loader et séparer les fcontions selon si on a utilisé .ini ou .mgn
#  problème desécurté à craquer

# todo : renommer Evmenet en FicheEvemenet et Intervention en Evenement

# confort / logique
# todo : refaire version console


def print_progress(v: float):
    print(f"La génération a progressé de {v}%")


def lire_fichier_pnjs(nom_fichier: str):
    to_return = []
    try:
        with open(nom_fichier, 'r', encoding="utf-8") as f:
            # with open(nom_fichier, 'r') as f:
            for ligne in f:
                nom = ligne.strip()
                # to_return.append(nom)
                to_return.append({"Nom": nom})
    except FileNotFoundError:
        print(f"Le fichier {nom_fichier} - {os.getcwd()} n'a pas été trouvé.")
    except Exception as e:
        logging.debug(
            f"Une erreur inattendue est survenue lors de la lecture du fichier {nom_fichier} - {os.getcwd()}: {str(e)}")
    logging.debug(f"après ajout du fichier des pnjs, le tableau contient = {to_return}")
    return to_return


def lire_et_recharger_gn(fichier_gn: str,
                         # mon_gn: GN,
                         api_drive, api_doc, api_sheets,
                         # nom_fichier_sauvegarde: str,
                         sans_chargement_fichier=False,
                         sauver_apres_operation=True,
                         # liste_noms_pjs=None,  # noms_pnjs=None,
                         fichier_erreurs_intrigues: bool = True, fichier_erreurs_evenements: bool = True,
                         generer_fichiers_pjs: bool = True,
                         generer_fichiers_pnjs: bool = True, aides_de_jeu: bool = True,
                         changelog: bool = True, table_intrigues: bool = True, table_objets: bool = True,
                         table_chrono: bool = True, table_persos: bool = True, table_pnjs: bool = True,
                         table_commentaires: bool = True, table_relations: bool = True, table_evenements: bool = True,
                         table_questionnaire: bool = True, resume_par_perso=True, solveur_planning=True,
                         singletest_perso: str = "-01", singletest_intrigue: str = "-01",
                         fast_intrigues: bool = True, fast_persos: bool = True, fast_pnjs=True, fast_evenements=True,
                         fast_objets=True,
                         verbal: bool = False, visualisation=print_progress, m_print=print):
    visualisation(-100)
    pas_visualisation = 50 / 7.0

    test_ok = False
    # Verification des fichiers d'entrée et chargement du fichier de config
    if fichier_gn.endswith('.ini'):
        test_ok, _, dict_config = g_io.verifier_fichier_gn_et_fournir_dict_config(fichier_gn, api_drive)
    elif fichier_gn.endswith('.mgn'):
        mon_gn = GN.load(fichier_gn, m_print=m_print)
        if mon_gn is None:
            return
        dict_config = mon_gn.dict_config
        test_ok, _ = g_io.verifier_dict_config(dict_config, api_drive)

    if not test_ok:
        m_print("Erreur dans le fichier de configuration")
        m_print("Vérifiez les erreurs et recommencez")
        return

    m_print("Configuration du GN ok")
    visualisation(pas_visualisation)

    # commencer le traitement
    if sans_chargement_fichier:
        m_print("recréation d'un GN from scratch")
        new_gn = GN(dict_config=dict_config)
        mon_gn = new_gn
    else:
        # si c'ets un fichier ini qui a été founi en entrée, on update le GN, sinon on garde la config
        if fichier_gn.endswith('.mgn'):
            # mon_gn = GN.load(fichier_gn) # le fichier a déjà été chargé
            mon_gn = g_io.charger_gn_from_gn(mon_gn, api_drive, m_print=m_print,
                                             updater_dict_config=None)
        else:
            mon_gn = g_io.charger_gn_from_dict(dict_config, api_drive, m_print=m_print,
                                               updater_dict_config=dict_config,
                                               last_save_connu=None)
            if mon_gn is None:
                return

        mon_gn.effacer_personnages_forces()

    for perso in mon_gn.personnages.values():
        logging.debug(f"nom du personnage = {perso.nom} / {perso.forced}")
    logging.debug(f"noms pjs dans le GN  = {mon_gn.noms_pjs()}")

    logging.debug(f"noms pnjs = {mon_gn.noms_pnjs()}")

    ids_lus = g_io.extraire_intrigues(mon_gn,
                                      api_drive=api_drive,
                                      api_doc=api_doc,
                                      singletest=singletest_intrigue,
                                      fast=fast_intrigues,
                                      verbal=verbal,
                                      m_print=m_print,
                                      visualisation=visualisation,
                                      taille_visualisation=pas_visualisation)
    retirer_intrigues_supprimees(mon_gn, ids_lus)
    # visualisation(pas_visualisation)
    m_print("****** fin de la lecture des intrigues  *********")
    ids_persos = []
    if mon_gn.get_dossiers_pjs():
        ids_lus = g_io.extraire_pjs(mon_gn,
                                    api_drive=api_drive,
                                    api_doc=api_doc,
                                    singletest=singletest_perso,
                                    fast=fast_persos,
                                    verbal=verbal,
                                    m_print=m_print,
                                    visualisation=visualisation,
                                    taille_visualisation=pas_visualisation)
        ids_persos += ids_lus
        # visualisation(pas_visualisation)
        m_print("****** fin de la lecture des pjs  *********")

    if mon_gn.get_dossiers_pnjs():
        ids_lus = g_io.extraire_pnjs(mon_gn,
                                     api_drive=api_drive,
                                     api_doc=api_doc,
                                     singletest=singletest_perso,
                                     fast=fast_pnjs,
                                     verbal=verbal,
                                     m_print=m_print,
                                     visualisation=visualisation,
                                     taille_visualisation=pas_visualisation)
        ids_persos += ids_lus
        # visualisation(pas_visualisation)
        m_print("****** fin de la lecture des pnjs *********")
    retirer_persos_supprimees(mon_gn, ids_persos)

    if mon_gn.get_dossiers_evenements():
        ids_lus = g_io.extraire_evenements(mon_gn,
                                           api_drive=api_drive,
                                           api_doc=api_doc,
                                           fast=fast_evenements,
                                           m_print=m_print,
                                           visualisation=visualisation,
                                           taille_visualisation=pas_visualisation
                                           )

        retirer_fiches_evenements_supprimes(mon_gn, ids_lus)
        # visualisation(pas_visualisation)
        m_print("****** fin de la lecture des évènements *********")

    if mon_gn.get_dossiers_objets():
        ids_lus = g_io.extraire_objets(mon_gn,
                                       api_drive=api_drive,
                                       api_doc=api_doc,
                                       fast=fast_objets,
                                       m_print=m_print,
                                       visualisation=visualisation,
                                       taille_visualisation=pas_visualisation
                                       )
        retirer_objets_supprimes(mon_gn, ids_lus)
        # visualisation(pas_visualisation)
        m_print("****** fin de la lecture des objets *********")

    m_print("****** fin de la lecture du drive *********")
    # liste_orgas = None
    # liste_noms_pnjs = None
    pnjs_lus = None
    pjs_lus = None
    logging.debug(f"mon_gn.id_pjs_et_pnjs = {mon_gn.get_id_pjs_et_pnjs()}")
    logging.debug(f"nom fichier pnj = {mon_gn.get_fichier_pnjs()}")

    # # debuggage
    # if sauver_apres_operation:
    #     mon_gn.save(nom_fichier_sauvegarde)

    m_print("****** reconstruction du GN : lecture des PJs et PNJs *********")

    if (sheet_id := mon_gn.get_id_pjs_et_pnjs()) is not None:
        # dans ce cas on a un tableau global avec toutes les données > on le lit
        # on met à jour les données pour les PNJs pour
        logging.debug(f"sheet_id = {sheet_id}, mon_gn.id_pjs_et_pnjs = {mon_gn.get_id_pjs_et_pnjs()}")
        pjs_lus, pnjs_lus = g_io.lire_gspread_pj_pnjs(api_sheets, sheet_id)
        # logging.debug(f"liste_noms_pnjs = {pjs_lus}")
        # logging.debug(f"liste_noms_pjs = {pnjs_lus}")
        # logging.debug(f"liste_orgas = {liste_orgas}")
    else:
        if (nom_fichier_pnjs := mon_gn.get_fichier_pnjs()) is not None:
            logging.debug("Pas d'id_pj_et_pnj, mais un fichier PNJs")
            pnjs_lus = lire_fichier_pnjs(nom_fichier_pnjs)
            logging.debug(f"après lecture, liste nom = {pnjs_lus}")
        if (liste_noms_pjs := mon_gn.get_liste_noms_pjs()) is not None:
            logging.debug("Pas d'id_pj_et_pnj, mais une liste de pjs")
            logging.debug(f"liste noms pjs = {liste_noms_pjs}")
            pjs_lus = [{"Nom": nom.strip()} for nom in liste_noms_pjs.split(',')]
            logging.debug(f"dictionnaire pjs injectés : {pjs_lus}")

        # sinon on prend en compte les données envoyées en input, issues des balises du fichier init pour une création
        # et on utilise les focntion classiques d'injections si on trouve des trucs

    if pnjs_lus is not None:
        logging.debug("début du forçage des PNJs")
        mon_gn.forcer_import_pnjs(pnjs_lus, verbal=verbal)
        logging.debug("PNJs forcés ok")

    if pjs_lus is not None:
        logging.debug("début du forçage des PJs")
        mon_gn.forcer_import_pjs(pjs_lus, verbal=verbal)
        logging.debug("PJs forcés ok")

    m_print("****** reconstruction du GN : reconstruction des factions (si applicable) *********")
    g_io.extraire_factions(mon_gn, api_doc=api_doc, verbal=verbal)
    # print(f"gn.factions = {gn.factions}")
    logging.debug("factions lues")

    visualisation(pas_visualisation)

    # # ajouté pour debug SUPPRIMER IMPERATIVEMENT
    # mon_gn.save(nom_fichier_sauvegarde)

    m_print(
        "* reconstruction du GN : mise à jour de tous les liens entre persos, intrigues, scenes objets et évènements *")
    mon_gn.rebuild_links(verbal)

    if sauver_apres_operation:
        # mon_gn.save(nom_fichier_sauvegarde)
        # mon_gn.save()
        g_io.sauvegarder_et_uploader_gn(mon_gn, api_drive)

    # visualisation(25)

    # pas_visualisation = 25.0 / 14.0
    m_print("*******************************************")
    m_print("*******************************************")
    # prefixe_fichiers = str(datetime.date.today())

    dict_methodes = {
        'fichier_erreurs_intrigues':
            lambda: ecrire_erreurs_intrigues_dans_drive(mon_gn, api_doc, api_drive, m_print=m_print),
        'fichier_erreurs_evenements':
            lambda: ecrire_erreurs_evenements_dans_drive(mon_gn, api_doc, api_drive,
                                                         mon_gn.get_dossier_outputs_drive(), m_print=m_print),
        'table_intrigues':
            lambda: creer_table_intrigues_sur_drive(mon_gn, api_sheets, api_drive, m_print=m_print),
        'changelog':
            lambda: generer_tableau_changelog_sur_drive(mon_gn, api_drive, api_sheets, m_print=m_print),
        'table_objets':
            lambda: ecrire_table_objet_dans_drive(mon_gn, api_drive, api_sheets, m_print=m_print),
        'table_chrono':
        # lambda: ecrire_table_chrono_dans_drive(mon_gn, api_drive, api_sheets),
            lambda: ecrire_table_chrono_dans_drive(mon_gn, api_drive, api_sheets, m_print=m_print),
        'table_persos':
            lambda: ecrire_table_persos(mon_gn, api_drive, api_sheets, m_print=m_print),
        'table_pnjs':
            lambda: ecrire_table_pnj(mon_gn, api_drive, api_sheets, m_print=m_print),
        'table_commentaires':
            lambda: ecrire_table_commentaires(mon_gn, api_drive, api_doc, api_sheets, m_print=m_print),
        'table_relations':
            lambda: ecrire_table_relation(mon_gn, api_drive, api_sheets, m_print=m_print),
        'aides_de_jeu':
            lambda: ecrire_texte_info(mon_gn, api_doc, api_drive, m_print=m_print),
        'table_evenements':
            lambda: ecrire_table_evenements(mon_gn, api_drive, api_sheets, m_print=m_print),
        'table_questionnaire':
            lambda: ecrire_table_questionnaire(mon_gn, api_drive, api_sheets, m_print=m_print),
        'resume_par_perso':
            lambda: ecrire_resume_intrigues_persos(mon_gn, api_doc, api_drive, m_print=m_print),
        'solveur_planning':
            lambda: ecrire_solveur_planning_dans_drive(mon_gn, api_sheets, api_drive, m_print=m_print)
    }
    # debug_list_key = list(dict_methodes)
    # print(f"DEBUG= liste clefs = {debug_list_key}")
    nb_parametres_demandes = 0
    for key in dict_methodes:
        # for key in list(dict_methodes):
        valeur = locals()[key]
        # print(f'DEBUG : clef :{key} - valeur : {valeur}')
        if valeur:
            nb_parametres_demandes += 1

    # nb_parametres_demandes = sum(bool(locals()[key]) for key in dict_methodes)
    # print(f'Nombre de parametres demandés : {nb_parametres_demandes}')
    if nb_parametres_demandes:
        pas_visualisation = 25.0 / nb_parametres_demandes
        for param in dict_methodes:
            # si le boolean qui a le meme nom est vrai
            if locals()[param]:
                dict_methodes[param]()
                visualisation(pas_visualisation)
    else:
        visualisation(25)

    if generer_fichiers_pjs:
        generer_squelettes_dans_drive(mon_gn, api_doc, api_drive, pj=True,
                                      m_print=m_print, visualisation=visualisation, taille_visualisation=12.5)
    else:
        visualisation(12.5)

    if generer_fichiers_pnjs:
        generer_squelettes_dans_drive(mon_gn, api_doc, api_drive, pj=False,
                                      m_print=m_print, visualisation=visualisation, taille_visualisation=12.5)
    else:
        visualisation(12.5)

    m_print("******* fin de la génération  ****************\n\n\n\n")
    visualisation(1000)


def retirer_intrigues_supprimees(mon_gn: GN, ids_intrigues_lus: list[str]):
    retirer_elements_supprimes(ids_intrigues_lus, mon_gn.intrigues)


def retirer_persos_supprimees(mon_gn: GN, ids_pjs_lus: list[str]):
    retirer_elements_supprimes(ids_pjs_lus, mon_gn.personnages)

def retirer_fiches_evenements_supprimes(mon_gn: GN, ids_evenements_lus: list[str]):
    retirer_elements_supprimes(ids_evenements_lus, mon_gn.evenements)


def retirer_objets_supprimes(mon_gn: GN, ids_objets_lus: list[str]):
    retirer_elements_supprimes(ids_objets_lus, mon_gn.objets_de_reference)


def retirer_elements_supprimes(ids_lus: list[str], dict_reference: dict):
    if ids_lus is None:
        return
    # print(f"debug : id lus = {ids_lus}")
    # print(f"debug : ids_dict = {dict_reference.keys()}")
    ids_a_supprimer = [mon_id for mon_id in dict_reference if mon_id not in ids_lus]
    # print(f"debug : id a supprimer = {ids_a_supprimer}")

    for id_lu in ids_a_supprimer:
        a_supprimer = dict_reference.pop(id_lu)
        # print(f"debug : intrigue en cours de suppression {a_supprimer.nom}")
        # logging.debug(f"l'objet {a_supprimer} a été identifié comme à supprimer (id = {id_lu})")
        if a_supprimer is not None:
            a_supprimer.clear()
            logging.debug("et il a été supprimé)")


# def lister_erreurs(mon_gn, prefixe, taille_min_log=0, verbal=False):
#     log_erreur = ""
#
#     intrigues_triees = sorted(mon_gn.intrigues.values(), key=lambda x: x.orgaReferent)
#     # for intrigue in gn.intrigues.values():
#
#     current_orga = "ceci est un placeholder"
#     for intrigue in intrigues_triees:
#         if current_orga != intrigue.orgaReferent:
#             current_orga = intrigue.orgaReferent
#             log_erreur += f"{current_orga} voici les intrigues avec des soucis dans leurs tableaux de persos \n"
#         if intrigue.error_log.nb_erreurs() > taille_min_log:
#             # print(f"poy! {intrigue.error_log}")
#             log_erreur += f"Pour {intrigue.nom} : \n" \
#                           f"{intrigue.error_log} \n"
#             log_erreur += suggerer_tableau_persos(mon_gn, intrigue)
#             log_erreur += "\n \n"
#     if verbal:
#         print(log_erreur)
#     if prefixe is not None:

#             f.close()
#     return log_erreur


def attrappeur_dexceptions(func):
    def wrapper(*args, **kwargs):
        # Check if 'm_print' is in the function signature
        # sig = signature(func)
        # m_print = kwargs.get('m_print') if 'm_print' in sig.parameters else print
        m_print = kwargs.get('m_print', print)
        logging.debug(f"lancement de {func.__name__}")

        try:
            return func(*args, **kwargs)
        except Exception as e:
            message = f"[{func.__name__}] a rencontré un problème, le fichier ne sera pas généré"
            logging.debug(f"{message} : {e}")
            logging.debug(traceback.format_exc())
            print(f"{message} : {e}")
            m_print(message)

    return wrapper


# Custom print method


def ecrire_fichier_erreur_localement(mon_gn: GN, prefixe: str, verbal: False):
    log_erreur = generer_texte_erreurs_intrigues(mon_gn, verbal=verbal)

    with open(f'{prefixe} - problèmes tableaux persos.txt', 'w', encoding="utf-8") as f:
        f.write(log_erreur)


def generer_texte_erreurs_intrigues(mon_gn, verbal=False):
    log_erreur = ""

    intrigues_triees = sorted(mon_gn.intrigues.values(), key=lambda x: x.orga_referent)
    # for intrigue in gn.intrigues.values():

    current_orga = "ceci est un placeholder"
    for intrigue in intrigues_triees:
        if current_orga != intrigue.orga_referent:
            current_orga = intrigue.orga_referent
            log_erreur += f"{current_orga} voici les intrigues avec des soucis dans leurs tableaux de persos \n"

        if intrigue.error_log.nb_erreurs() > 0:
            log_erreur += f"Pour {intrigue.nom} : \n" \
                          f"Url : {intrigue.get_full_url()} \n" \
                          f"{intrigue.error_log} \n"
            log_erreur += suggerer_tableau_persos(mon_gn, intrigue)
            log_erreur += "\n \n"
    if verbal:
        print(log_erreur)

    return log_erreur


def generer_texte_erreurs_fiches_evenements(mon_gn, verbal=False):
    log_erreur = ""

    evenements_tries = sorted(mon_gn.evenements.values(), key=lambda x: x.referent)

    current_orga = "ceci est un placeholder"
    for evenement in evenements_tries:
        if current_orga != evenement.referent:
            current_orga = evenement.referent
            log_erreur += f"{current_orga} voici les évènements avec des soucis dans leur fiche : \n"

        if evenement.erreur_manager.nb_erreurs() > 0:
            log_erreur += f"Pour {evenement.nom_evenement} : \n" \
                          f"{evenement.erreur_manager} \n"
            log_erreur += "\n \n"
    if verbal:
        print(log_erreur)

    return log_erreur


def generer_texte_resume_intrigues_persos(mon_gn: GN, verbal=False):
    tab_brut = [
        {'orga': perso.orga_referent,
         'nom_perso': perso.nom,
         'texte_recap': '\n' + perso.str_recap_intrigues() + '\n'  # contournement de erreurs d'écriture
         # 'texte_recap': perso.str_recap_intrigues() if len(perso.str_recap_intrigues()) else ' '
         }
        for perso in mon_gn.get_dict_pj().values()
    ]

    tab_tri = sorted(tab_brut, key=lambda x: (x['orga'], x['nom_perso']))

    to_return = ""
    orga_en_cours = "drgrsdgegerg"

    for perso in tab_tri:
        if orga_en_cours != perso['orga']:
            orga_en_cours = perso["orga"]
            to_return += f'********** Personnages de {orga_en_cours} : ********** \n'

        to_return += f'***** {perso["nom_perso"]} : ***** \n'
        to_return += perso['texte_recap']

    return to_return


@attrappeur_dexceptions
def ecrire_resume_intrigues_persos(mon_gn: GN, api_doc, api_drive, verbal=False, m_print=print):
    m_print("******* resume des intrigues par perso ******************")

    parent = mon_gn.get_dossier_outputs_drive()
    texte_resume = generer_texte_resume_intrigues_persos(mon_gn, verbal)

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- Implications par persos dans intrigues'
    mon_id = g_io.creer_google_doc(api_drive, nom_fichier, parent,
                                   id_dossier_archive=mon_gn.get_id_dossier_archive())
    g_io.write_to_doc(api_doc, mon_id, texte_resume, verbal=False)


@attrappeur_dexceptions
def ecrire_erreurs_intrigues_dans_drive(mon_gn: GN, api_doc, api_drive, verbal=False, m_print=print):
    m_print("* génération du fichier des erreurs intrigues * ")
    parent = mon_gn.get_dossier_outputs_drive()
    texte_erreurs = generer_texte_erreurs_intrigues(mon_gn, verbal=verbal)

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- Récap erreurs persos dans intrigues'
    mon_id = g_io.creer_google_doc(api_drive, nom_fichier, parent,
                                   id_dossier_archive=mon_gn.get_id_dossier_archive())
    if g_io.write_to_doc(
            api_doc, mon_id, texte_erreurs
    ):
        g_io.formatter_fichier_erreurs(api_doc, mon_id)


@attrappeur_dexceptions
def ecrire_erreurs_evenements_dans_drive(mon_gn: GN, api_doc, api_drive, parent, verbal=False, m_print=print):
    m_print("* génération du fichier des erreurs évènements * ")

    texte_erreurs = generer_texte_erreurs_fiches_evenements(mon_gn, verbal=verbal)

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- Récap erreurs évènements'
    mon_id = g_io.creer_google_doc(api_drive, nom_fichier, parent,
                                   id_dossier_archive=mon_gn.get_id_dossier_archive())
    if g_io.write_to_doc(
            api_doc, mon_id, texte_erreurs
    ):
        g_io.formatter_fichier_erreurs(api_doc, mon_id)


def rationaliser_liste_noms(noms_en_entree, seuil=70):
    """
    Rationalise une liste de noms en éliminant les doublons et en groupant les noms similaires.

    Cette fonction prend une liste de noms et utilise un processus de dédoublonnage pour retirer
    les entrées qui sont considérées comme des doublons, en fonction d'un seuil de similitude.
    Les noms en trop, qui ne sont pas retenus dans la liste dédoublonnée, sont ensuite comparés
    aux noms conservés pour identifier le meilleur match possible en utilisant un score de similarité.
    Les noms sont ensuite regroupés en fonction de leur match le plus similaire dans le dictionnaire final.

    Paramètres:
        noms_en_entree (list): Une liste de chaînes de caractères représentant les noms à rationaliser.
        seuil (int, optionnel): Le seuil de similitude pour considérer deux noms comme étant des doublons.
                                La valeur par défaut est 70.

    Retourne:
        dict: Un dictionnaire où chaque clé est un nom unique de la liste dédoublonnée et chaque valeur
              est une liste des noms originaux qui correspondent à cette clé basée sur le score de
              similitude le plus élevé.

    Exemple:
        >>> rationaliser_liste_noms(['Jean Dupont', 'Jean du Pont', 'J. Dupont', 'Isabelle Durand', 'I. Durand'])
        {'Jean Dupont': ['Jean du Pont', 'J. Dupont'], 'Isabelle Durand': ['I. Durand']}
    """
    cut = process.dedupe(noms_en_entree, seuil)
    off = [e for e in noms_en_entree if e not in cut]
    dico = {e: [] for e in cut}
    for e in off:
        score = process.extractOne(e, cut)
        dico[score[0]].append(e)

    return dico


def suggerer_tableau_persos(mon_gn: GN, intrigue: Intrigue, verbal: bool = False):
    noms_personnages = mon_gn.noms_personnages()
    noms_roles_dans_tableau_intrigue = [x.personnage.nom for x in intrigue.rolesContenus.values()
                                        if not x.issu_dune_faction and x.personnage is not None]

    tous_les_noms_lus_dans_scenes = []
    for scene in intrigue.scenes:
        if scene.noms_roles_lus is not None:
            tous_les_noms_lus_dans_scenes += scene.noms_roles_lus
    tous_les_noms_lus_dans_scenes = [x.strip() for x in tous_les_noms_lus_dans_scenes]

    # ajouter les noms issus des evenements
    tous_les_noms_lus_dans_scenes += intrigue.get_noms_intervenants()
    tous_les_noms_lus_dans_scenes += intrigue.get_noms_pjs_concernes()

    # simplifier sous forme de set
    tous_les_noms_lus_dans_scenes = set(tous_les_noms_lus_dans_scenes)

    # rationnaliser la liste des noms avant de processer pour enlever les doublons évidents,
    # on les remettra à la fin
    dico_dedup = rationaliser_liste_noms(tous_les_noms_lus_dans_scenes)
    tous_les_noms_lus_dans_scenes = list(dico_dedup.keys())

    scores = {}

    # remplir un tableau, pour chaque nom, de toutes les correspondances possibles et permutations
    for original_nom in tous_les_noms_lus_dans_scenes:
        permutations = original_nom.split(' aka ')
        scores[original_nom] = []
        for nom in permutations:
            scores[original_nom].extend(process.extract(nom, noms_personnages))

        # trier les couples nom, score par ordre de score
        scores[original_nom].sort(key=lambda x: x[1])

    # rechercher la solution : initialisation des variables
    solution = []
    solution_trouvee = False

    # cosntruire la solution de départ en créant des triplettes [nom proposé, score, nom de départ]
    # invariant : la solution est triée et l'élément le plus faible est en premier
    for original_nom, matches in scores.items():
        score_a_inclure = matches.pop()
        solution.append([score_a_inclure[0], score_a_inclure[1], original_nom])
    solution.sort(key=lambda x: x[1])

    # met à jour la solution en prenant la valeur suivante de l'élément nom à updater désigné
    def maj_solution(solution, scores, nom_a_updater):
        matches = scores[nom_a_updater]
        if not len(matches):
            return None

        score_a_inclure = matches.pop()
        for triplette in solution:
            if triplette[2] == nom_a_updater:
                triplette[0], triplette[1] = score_a_inclure

        solution.sort(key=lambda x: x[1])
        return solution

    while solution and not solution_trouvee:
        solution_trouvee = True
        # est-ce que la solution est valable?

        # pour cela, on va vérifier que chaque nom n'est présent qu'eun fois.
        # Si ce n'est pas le cas, on mettra à jour la solution en trouvant le nom d'origine qui était associé au nom
        # en doublon le plus faible et en cherchant les solutions alternatives

        # on parcourt les clefs pour identifier s'il y en a en double.
        # dans ce cas, cela veut dire qu'un meme nom est proposé deux fois : il faudra réessayer avec une autre solution
        # sachant qu'elles sont triées par ordre du score le plus faible au plus fort,
        # donc pour virer la clef la plus faible, il faut comparer à toutes les valeurs suivantes
        if verbal:
            print(f"Je m'apprête à commencer une itération avec la solution suivante :\n"
                  f"{solution}")

        for i, triplette in enumerate(solution):
            nom_propose, _, nom_origine = triplette
            noms_a_verifier = [triplette[0] for triplette in solution[i + 1:]]
            if verbal:
                print(f"DEBUG : je suis en train de chercher l'élément {nom_propose} dans \n "
                      f"{noms_a_verifier}")

            if nom_propose in noms_a_verifier:
                if verbal:
                    print("et il était bien présent, j'itère")
                solution_trouvee = False
                solution = maj_solution(solution, scores, nom_origine)

    if verbal:
        print(f'DEBUG : trouvé = {solution_trouvee} \n la solution est {solution}')

    # A ce stade là, la solution est dans le dictionnaire "solution"

    if not solution or not solution_trouvee:
        return "Impossible de construire une proposition de tableau"

    # tableau_persos = [['Nom proposé', 'nom dans les scènes', 'score', 'déjà dans le tableau?']]
    tableau_pjs = [['Nom proposé', 'nom dans les scènes', 'score', 'déjà dans le tableau?']]
    tableau_pnjs = [['Nom proposé', 'nom dans les scènes', 'score', 'déjà dans le tableau?']]
    tableau_rerolls = [['Nom proposé', 'nom dans les scènes', 'score', 'déjà dans le tableau?']]

    dict_nom_perso = mon_gn.get_dict_noms_persos(True, True, True)

    # on ajoute l'info de la présence dans la solution et on la trie :
    # d'abord les présents, puis les scores
    for sol in solution:
        sol.append(sol[0] in noms_roles_dans_tableau_intrigue)
    solution.sort(key=lambda x: (x[3], x[1]), reverse=True)

    for nom_personnage, score, nom_role, present in solution:
        personnage = dict_nom_perso[nom_personnage]
        if personnage.est_un_pj():
            tab = tableau_pjs
        elif personnage.est_un_pnj():
            tab = tableau_pnjs
        else:
            tab = tableau_rerolls

        tab.append([
            nom_personnage,
            ', '.join([nom_role] + dico_dedup[nom_role]),
            f'{score} % de certitude',
            'oui' if present else 'non'
        ])

    to_print = "Tableau des PJs suggéré : \n"
    to_print += lecteurGoogle.formatter_tableau_pour_export(tableau_pjs)
    to_print += '\n'
    to_print += "Tableau des PNJs suggéré : \n"
    to_print += lecteurGoogle.formatter_tableau_pour_export(tableau_pnjs)
    to_print += '\n'
    to_print += "Tableau des Rerolls suggéré : \n"
    to_print += lecteurGoogle.formatter_tableau_pour_export(tableau_rerolls)
    to_print += '\n'

    if verbal:
        print(to_print)

    return to_print


def suggerer_tableau_persos_old(mon_gn: GN, intrigue: Intrigue, verbal: bool = False):
    """
    Suggère un tableau de personnages participant à une intrigue donnée, en se basant sur les scènes qui la composent.

    Args:
        mon_gn (GN): Un objet GN contenant les informations sur le jeu de rôle.
        intrigue (Intrigue): Un objet Intrigue représentant l'intrigue pour laquelle les personnages sont recherchés.
        verbal (bool, optional): Si True, affiche le résultat à l'écran. Par défaut à False.

    Returns:
        str: Une chaîne de caractères formatée avec les personnages suggérés et leur niveau de certitude.
    """
    noms_personnages = mon_gn.noms_personnages()
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
        nom_sans_alias = nom.split(' aka ')[0]
        score_perso = process.extractOne(nom_sans_alias, noms_personnages)
        # score_perso = process.extractOne(str(nom), noms_personnages)
        if score_perso[0] in noms_roles_dans_tableau_intrigue:
            prefixe = "[OK]"
        else:
            prefixe = "[XX]"

        meilleur_nom = f"{score_perso[0]} pour {nom} ({score_perso[1]} % de certitude)"

        tableau_sortie.append([prefixe, meilleur_nom])
        tableau_sortie = sorted(tableau_sortie)

    for e in tableau_sortie:
        to_print += f"{e[0]} {e[1]} \n"

    if verbal:
        print(to_print)

    return to_print


@attrappeur_dexceptions
def generer_tableau_changelog_sur_drive(mon_gn: GN, api_drive, api_sheets, m_print=print):
    m_print("*******changelog*****************************")
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
        for role in ma_scene.get_roles():
            if role.est_un_pnj():
                continue
            if role.personnage is None:
                continue
            if len(role.personnage.orga_referent) < 3:
                orga_referent = "Orga sans nom"
            else:
                orga_referent = role.personnage.orga_referent.strip().upper()
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
        dict_scene = {'nom_scene': ma_scene.titre,
                      'date': ma_scene.derniere_mise_a_jour.strftime("%Y-%m-%d %H:%M:%S"),
                      'qui': ma_scene.modifie_par, 'intrigue': ma_scene.conteneur.get_nom(),
                      'document': ma_scene.conteneur.get_full_url()
                      }
        dict_orgas = {}
        # dict_scene['dict_orgas'] = dict_orgas
        for role in ma_scene.get_roles():
            if role.est_un_pnj():
                continue
            if role.personnage is None:
                continue
            orga_referent = role.personnage.orga_referent.strip().upper()
            if len(orga_referent) < 3:
                orga_referent = "Orga sans nom"
            if orga_referent not in dict_orgas:
                dict_orgas[orga_referent] = [role.personnage.nom]
            else:
                dict_orgas[orga_referent] += [role.personnage.nom]
        tableau_scene_orgas.append([dict_scene, dict_orgas])

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Changelog'
    dossier_output = mon_gn.get_dossier_outputs_drive()
    mon_id = g_io.creer_google_sheet(api_drive, nom_fichier, dossier_output,
                                     id_dossier_archive=mon_gn.get_id_dossier_archive())
    g_io.exporter_changelog(tableau_scene_orgas, mon_id, dict_orgas_persos, api_sheets)
    g_io.supprimer_feuille_1(api_sheets, mon_id)


@attrappeur_dexceptions
def creer_table_intrigues_sur_drive(mon_gn: GN, api_sheets, api_drive, m_print=print):
    m_print("******* statut intrigues *******************")

    table_intrigues = [
        ["nom intrigue", "nombre de scenes", "dernière édition", "modifié par", "Orga referent", "statut", "Problèmes",
         "url"]]
    table_intrigues.extend(
        [
            intrigue.nom,
            len(intrigue.scenes),
            intrigue.lastFileEdit.strftime("%Y-%m-%d %H:%M:%S"),
            intrigue.modifie_par,
            intrigue.orga_referent,
            intrigue.questions_ouvertes,
            intrigue.error_log.nb_erreurs(),
            intrigue.get_full_url(),
        ]
        for intrigue in mon_gn.intrigues.values()
    )
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Etat des intrigues'
    dossier_export = mon_gn.get_dossier_outputs_drive()
    mon_id = g_io.creer_google_sheet(api_drive, nom_fichier, dossier_export,
                                     id_dossier_archive=mon_gn.get_id_dossier_archive())
    # extraire_texte_de_google_doc.exporter_table_intrigue(api_doc, nom_fichier, dossier_export, df)
    # extraire_texte_de_google_doc.write_to_sheet(api_sheets, df, mon_id)
    g_io.write_to_sheet(api_sheets, table_intrigues, mon_id)


@attrappeur_dexceptions
def generer_squelettes_dans_drive(mon_gn: GN, api_doc, api_drive, pj=True, m_print=print,
                                  visualisation=print_progress, taille_visualisation=100.0):
    m_print(f"*******génération squelettes {'PJs' if pj else 'PNJs'} ***********")
    parent = mon_gn.get_dossier_outputs_drive()
    pj_pnj = "PJ" if pj else "PNJ"
    nom_dossier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} - Squelettes {pj_pnj}'
    nouveau_dossier = g_io.creer_dossier_drive(api_drive,
                                               parent,
                                               nom_dossier,
                                               id_dossier_archive=mon_gn.get_id_dossier_archive())
    d = squelettes_par_perso(mon_gn, pj=pj, m_print=m_print)
    nb_persos_source = len(d)
    if nb_persos_source == 0:
        visualisation(taille_visualisation)
        return
    pas_visualisation = taille_visualisation / nb_persos_source
    for index, nom_perso in enumerate(d, start=1):
        prefixe = f"Écriture des fichiers des {pj_pnj} dans drive ({index}/{nb_persos_source})"

        # créer le fichier et récupérer l'ID
        nom_fichier = f'{nom_perso} - squelette au {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}'
        texte = d[nom_perso]

        # extraireTexteDeGoogleDoc.inserer_squelettes_dans_drive(nouveau_dossier,
        # api_doc, api_drive, texte, nom_fichier,prefixe)

        m_print(f'{prefixe} : {nom_perso}')
        visualisation(pas_visualisation)

        nb_tries = 0
        max_tries = 3
        while True:
            try:
                # pas d'archivage car le dossier a déjà été archivé
                file_id = g_io.creer_google_doc(api_drive, nom_fichier, nouveau_dossier,
                                                id_dossier_archive=None)
                g_io.write_to_doc(api_doc, file_id, texte, titre=nom_fichier)
                # g_io.formatter_titres_scenes_dans_squelettes(api_doc, file_id)
                break
            except Exception as e:
                nb_tries += 1
                if nb_tries <= max_tries:
                    m_print(f"Une erreur est survenue, nouvelle tentative ({nb_tries}/{max_tries})")
                    print(f"Exception attrapée durant la génération : {e}")
                    traceback.print_exc()  # This will print the full traceback
                else:
                    raise e


def squelettes_par_perso(mon_gn: GN, pj=True, m_print=print):
    squelettes_persos = {}
    if pj:
        liste_persos_source = mon_gn.get_dict_pj().values()
    else:
        liste_persos_source = mon_gn.get_dict_pnj().values()

    # for perso in liste_persos_source:
    #     print(f"génération du texte des persos : personnage en cours d'écriture : {perso.nom}")
    nb_persos_source = len(liste_persos_source)
    pj_pnj = "pjs" if pj else "pnjs"
    for index, perso in enumerate(liste_persos_source, start=1):
        m_print(f"Génération des fichiers des {pj_pnj} ({index}/{nb_persos_source})"
                f": personnage en cours de synthèse : {perso.nom}")

        # ajout des informations issues des fiches :
        texte_perso = generer_squelette_perso(mon_gn, perso)
        squelettes_persos[perso.nom] = texte_perso

    return squelettes_persos


# def generer_squelette_perso(mon_gn, perso):
#     texte_perso = ""
#     texte_perso += f"Début du squelette pour {perso.nom} (Orga Référent : {perso.orga_referent}) : \n"
#     texte_perso += f"type de personnage : {perso.string_type_personnage()} \n"
#     texte_perso += f"résumé de la bio : \n"
#     texte_perso += f"{perso.description} \n"
#     texte_perso += f"Psychologie : \n"
#     texte_perso += f"{perso.concept} \n"
#     texte_perso += f"Motivations et objectifs : \n"
#     # logging.debug(f"driver avant insertion {perso.driver}")
#     texte_perso += f"{perso.driver} \n"
#     texte_perso += f"Chronologie : \n "
#     texte_perso += f"{perso.datesClefs} \n"
#     texte_perso += "\n *** Intrigues : *** \n"
#     texte_perso += perso.str_recap_intrigues()
#     texte_perso += "\n *** Relations : *** \n"
#     texte_perso += perso.str_relations()
#     # ajout des informations issues des interventions (si pnj):
#     if len(perso.intervient_comme) > 0:
#         texte_perso += "\n *** briefs pour les interventions dans les évènements : *** \n"
#         texte_perso += '\n'.join([i.str_pour_squelette() for i in perso.intervient_comme])
#     # ajout des informations issues des infos pour evènement:
#     if len(perso.informations_evenements) > 0:
#         texte_perso += "\n *** informations à fournir pour organiser les évènements : *** \n"
#         # texte_perso += '\n'.join([i.str_pour_squelette() for i in perso.informations_evenements])
#         tab_evts = [['évènement', 'infos à fournir']]
#         tab_evts.extend(evt.row_infos_evenement_pour_squelette() for evt in perso.informations_evenements)
#         texte_perso += lecteurGoogle.formatter_tableau_pour_export(tab_evts)
#     # ajout des informations issues des intrigues :
#     texte_perso += "\n *** Scenes associées : *** \n"
#     mes_scenes = []
#     for role in perso.roles:
#         mes_scenes.extend(iter(role.scenes))
#     mes_scenes = Scene.trier_scenes(mes_scenes, date_gn=mon_gn.get_date_gn())
#     # print(f'DEBUG = personnage en cours de génération des scènes = {perso.nom}, {perso.url}')
#     for scene in mes_scenes:
#         # print(scene)
#         texte_perso += scene.str_pour_squelette(mon_gn.get_date_gn()) + '\n'
#     texte_perso += '****************************************************** \n'
#     return texte_perso

def generer_squelette_perso(mon_gn, perso):
    elements = [
        f"Début du squelette pour {perso.nom} (Orga Référent : {perso.orga_referent}) :",
        f"type de personnage : {perso.string_type_personnage()}",
        "résumé de la bio :",
        perso.description,
        "Psychologie :",
        perso.concept,
        "Motivations et objectifs :",
        perso.driver,
        "Chronologie :",
        perso.datesClefs,
        "\n *** Intrigues : ***",
        perso.str_recap_intrigues(),
        "\n *** Relations : ***",
        perso.str_relations()
    ]

    if perso.intervient_comme:
        interventions = '\n'.join(i.str_pour_squelette() for i in perso.intervient_comme)
        elements.append("\n *** briefs pour les interventions dans les évènements : ***")
        elements.append(interventions)

    if perso.informations_evenements:
        # tab_evts = [['évènement', 'J', 'Heure', 'Description', 'infos à fournir']] + \
        tab_evts = [['évènement', 'infos à fournir']] + \
                   [evt.row_infos_evenement_pour_squelette() for evt in perso.informations_evenements]
        elements.append("\n *** informations à fournir pour organiser les évènements : ***")
        elements.append(lecteurGoogle.formatter_tableau_pour_export(tab_evts))

    mes_scenes = []
    for role in perso.roles:
        mes_scenes.extend(iter(role.scenes))
    mes_scenes = Scene.trier_scenes(mes_scenes, date_gn=mon_gn.get_date_gn())

    scenes_str = '\n'.join(scene.str_pour_squelette(mon_gn.get_date_gn()) for scene in mes_scenes)
    elements.append("\n *** Scenes associées : ***")
    elements.append(scenes_str)

    elements.append('******************************************************')

    return '\n'.join(elements)


def ecrire_squelettes_localement(mon_gn: GN, prefixe=None, pj=True):
    squelettes_persos = squelettes_par_perso(mon_gn, pj)
    toutes_scenes = "".join(squelettes_persos.values())

    if prefixe is not None:
        with open(f'{prefixe} - squelettes.txt', 'w', encoding="utf-8") as f:
            f.write(toutes_scenes)
            f.close()

    return toutes_scenes


def generer_liste_pnj_dedup_avec_perso(mon_gn, threshold=89, verbal=False):
    dict_nom_role_nom_pnj = {}
    for intrigue in mon_gn.intrigues.values():
        for role in intrigue.rolesContenus.values():
            if role.est_un_pnj() or role.est_un_reroll():
                dict_nom_role_nom_pnj[role.nom] = role.personnage.nom if role.personnage is not None else "aucun perso"

    dict_nom_brief_nom_pnj = {}
    for evenement in mon_gn.evenements.values():
        for intervenant_evenement in evenement.intervenants_evenement.values():
            dict_nom_brief_nom_pnj[intervenant_evenement.nom_pnj] = \
                intervenant_evenement.pnj.nom if intervenant_evenement.pnj else "aucun perso"

    dict_noms_noms_pnjs = dict_nom_role_nom_pnj | dict_nom_brief_nom_pnj

    noms_pnjs = list(dict_noms_noms_pnjs)
    # noms_dedup = process.dedupe(noms_pnjs, threshold=threshold)
    dico_dedup = rationaliser_liste_noms(noms_pnjs, threshold)
    noms_dedup = sorted(list(dico_dedup.keys()))

    persos_dedup = [dict_noms_noms_pnjs[nom_pnj] for nom_pnj in noms_dedup]
    variations_orthographe = [dico_dedup[nom_pnj] for nom_pnj in noms_dedup]

    logging.debug(f"liste des pnjs dédup : {noms_dedup}")

    if verbal:
        for v in noms_dedup:
            print(v)
    return noms_dedup, variations_orthographe, persos_dedup


def generer_liste_pnj_dedup_avec_perso_old(mon_gn, threshold=89, verbal=False):
    dict_nom_role_nom_pnj = {}
    for intrigue in mon_gn.intrigues.values():
        for role in intrigue.rolesContenus.values():
            if role.est_un_pnj() or role.est_un_reroll():
                dict_nom_role_nom_pnj[role.nom] = role.personnage.nom if role.personnage is not None else "aucun perso"

    dict_nom_brief_nom_pnj = {}
    for evenement in mon_gn.evenements.values():
        for intervenant_evenement in evenement.intervenants_evenement.values():
            dict_nom_brief_nom_pnj[intervenant_evenement.nom_pnj] = \
                intervenant_evenement.pnj.nom if intervenant_evenement.pnj else "aucun perso"

    dict_noms_noms_pnjs = dict_nom_role_nom_pnj | dict_nom_brief_nom_pnj

    noms_pnjs = list(dict_noms_noms_pnjs)
    noms_dedup = process.dedupe(noms_pnjs, threshold=threshold)
    noms_dedup = sorted(noms_dedup)

    persos_dedup = [dict_noms_noms_pnjs[nom_pnj] for nom_pnj in noms_dedup]

    logging.debug(f"liste des pnjs dédup : {noms_dedup}")

    if verbal:
        for v in noms_dedup:
            print(v)
    return noms_dedup, persos_dedup


# def generer_liste_pnj_dedup(mon_gn, threshold=89, verbal=False):
#     to_return, _ = generer_liste_pnj_dedup_avec_perso(mon_gn, threshold, verbal)
#     return to_return


# def ecrire_liste_pnj_dedup_localement(mon_gn: GN, prefixe: str, threshold=89, verbal=False):
#     to_print = '\n'.join(generer_liste_pnj_dedup(mon_gn, threshold, verbal))
#     if prefixe is not None:
#         with open(f"{prefixe} - liste_pnjs_dedupliqués.txt", 'w', encoding="utf-8") as f:
#             f.write(to_print)
#             f.close()


def generer_changelog(mon_gn, prefixe, nb_jours=1, verbal=False):
    date_reference = datetime.date.today() - datetime.timedelta(days=nb_jours)

    # on crée un tableau avec tous lse changements :
    # [orga referent | personnage | titre intrigue | url intrigue | date changement intrigue]
    # structure souhaitée :
    # orga referent / persos / titre intrigue/ url intrigue | date changement intrigue

    restitution = {}
    for intrigue in mon_gn.intrigues.values():
        if intrigue.lastFileEdit.date() > date_reference:
            for role in intrigue.rolesContenus.values():
                if role.personnage is not None and est_un_pj(role.personnage.pj):
                    referent = role.personnage.orga_referent.strip()

                    if len(referent) < 3:
                        referent = "Orga sans nom"

                    # print(f"je m'apprête à ajouter une ligne pour {referent} :
                    # {role.personnage.nom} dans {intrigue.nom}")
                    nom_perso = role.personnage.nom
                    # nomIntrigue = intrigue.nom

                    # on vérifie que le référent et le personnage existent, sinon on initialise
                    if referent not in restitution:
                        restitution[referent] = {}
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
        with open(f'{prefixe} - changements - {str(nb_jours)}j.txt', 'w', encoding="utf-8") as f:
            f.write(texte)
            f.close()

    return texte


# def ecrire_fichier_config(dict_config: dict, nom_fichier: str):
#     config = configparser.ConfigParser()
#
#     # Create the sections
#     config['dossiers'] = {'intrigues': ",".join(dict_config['dossier_intrigues']),
#                           'id_factions': dict_config['id_factions'],
#                           'dossier_output_squelettes_pjs': dict_config['dossier_output']}
#
#     for nb_fichiers_persos, perso in enumerate(dict_config['dossiers_pjs'], start=1):
#         config['dossiers'][f'base_persos_{str(nb_fichiers_persos)}'] = perso
#
#     config['globaux'] = {'association_auto': dict_config['association_auto'],
#                          'type_fiche': dict_config['type_fiche']}
#
#     config['sauvegarde'] = {'nom_fichier_sauvegarde': dict_config['nom_fichier_sauvegarde']}
#
#     config['pjs_a_importer'] = {'noms_persos': ",".join(dict_config['noms_persos']),
#                                 'nom_fichier_pnjs': dict_config['fichier_noms_pnjs']}
#
#     # Write the config file
#     with open(nom_fichier, 'w') as configfile:
#         config.write(configfile)


def generer_table_objets_from_intrigues_et_evenements(mon_gn):
    to_return = [['code', 'description', 'Avec FX?', 'Avec informatique?', 'Détail', 'Débute Où?', 'fourni par Qui?',
                  'Intrigues', 'Evènements',
                  'fiche objet trouvée?', 'Orga référent']]
    for objet_ref in mon_gn.objets_de_reference.values():
        ma_liste = [objet for objet in objet_ref.objets_dans_intrigues if objet.intrigue is not None]
        for objet in ma_liste:
            code = objet.code.replace('\n', '\v')
            description = objet.description.replace('\n', '\v')
            avecfx = objet.avec_fx()
            avecinformatique = objet.avec_informatique()
            details_fx_info = '\n'.join(
                [objet.specialEffect.replace('\n', '\v') + objet.informatique.replace('\n', '\v')])
            debuteou = objet.emplacementDebut.replace('\n', '\v')
            fournipar = objet.fourniParJoueur.replace('\n', '\v')
            # intrigue = objet.intrigue
            intrigue = lien_vers_hyperlink(objet.intrigue.get_full_url(), objet.intrigue.nom)
            evenement = ""
            fiche_objet = "aucune" if objet_ref.ajoute_via_forcage else objet_ref.get_full_url()
            orga_referent = objet.get_orga_referent()
            to_return.append([f"{code}",
                              f"{description}",
                              f"{avecfx}",
                              f"{avecinformatique}",
                              f"{details_fx_info}",
                              f"{debuteou}",
                              f"{fournipar}",
                              f"{intrigue}",
                              f"{evenement}",
                              f"{fiche_objet}",
                              f"{orga_referent}"]
                             )
        # ma_liste = [objet for objet in objet_ref.objets_dans_evenements if objet.evenement is not None]
        for objet in objet_ref.objets_dans_evenements:
            code = objet.code.replace('\n', '\v')
            description = objet.description.replace('\n', '\v')
            avecfx = ""
            details_fx_info = ""
            debuteou = objet.commence.replace('\n', '\v')
            fournipar = ""
            intrigue = ""
            # evenement = objet.evenement.nom_evenement
            evenement = lien_vers_hyperlink(objet.evenement.get_full_url(), objet.evenement.nom_evenement)

            fiche_objet = "aucune" if objet_ref.ajoute_via_forcage else objet_ref.get_full_url()
            orga_referent = objet.get_orga_referent()
            to_return.append([f"{code}",
                              f"{description}",
                              f"{avecfx}",
                              f"{details_fx_info}",
                              f"{debuteou}",
                              f"{fournipar}",
                              f"{intrigue}",
                              f"{evenement}",
                              f"{fiche_objet}",
                              f"{orga_referent}"]
                             )

    return to_return


def generer_table_objets_uniques(mon_gn):
    to_return = [['Code', 'Nom / Description', 'Intrigues', 'Evènements', 'fiche objet trouvée?', 'orga']]
    for objet_ref in mon_gn.objets_de_reference.values():
        code = objet_ref.code_objet.replace('\n', '\v')
        if objet_ref.nom_objet != "":
            nom = objet_ref.nom_objet
        elif len(objet_ref.objets_dans_intrigues) != 0:
            nom = list(objet_ref.objets_dans_intrigues)[0].description
        else:
            nom = list(objet_ref.objets_dans_evenements)[0].description
        liste_noms_intrigues = [o.intrigue.nom for o in objet_ref.objets_dans_intrigues if o.intrigue is not None]
        # liste_noms_intrigues = [lien_vers_hyperlink(o.intrigue.get_full_url(), o.intrigue.nom)
        #                         for o in objet_ref.objets_dans_intrigues if o.intrigue is not None]
        intrigues = '\n'.join(liste_noms_intrigues)
        liste_noms_evenements = [o.evenement.nom_evenement for o in objet_ref.objets_dans_evenements if
                                 o.evenement is not None]
        evenements = '\n'.join(liste_noms_evenements)
        fiche_objet = "aucune" if objet_ref.ajoute_via_forcage else lien_vers_hyperlink(objet_ref.get_full_url())
        orga = objet_ref.get_orga_referent()
        # fiche_objet = "aucune" if objet_ref.ajoute_via_forcage else objet_ref.get_full_url()
        to_return.append([f"{code if len(code) > 1 else 'Pas de code'}",
                          f"{nom}",
                          f"{intrigues}",
                          f"{evenements}",
                          f"{fiche_objet}",
                          f"{orga}"
                          ]
                         )

    return to_return


def lien_vers_hyperlink(lien: str, texte_lien=None):
    if texte_lien is None:
        texte_lien = lien
    return f'=HYPERLINK(\"{lien}\"; \"{texte_lien}\")'


@attrappeur_dexceptions
def ecrire_table_objet_dans_drive(mon_gn: GN, api_drive, api_sheets, m_print=print):
    m_print("************* table objets *******************")
    parent = mon_gn.get_dossier_outputs_drive()
    table_detaillee = generer_table_objets_from_intrigues_et_evenements(mon_gn)
    table_condensee = generer_table_objets_uniques(mon_gn)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- Table des objets'
    mon_id = g_io.creer_google_sheet(api_drive, nom_fichier, parent,
                                     id_dossier_archive=mon_gn.get_id_dossier_archive())
    g_io.write_to_sheet(api_sheets, table_detaillee, mon_id, "lus dans les fiches")
    g_io.write_to_sheet(api_sheets, table_condensee, mon_id, "objets uniques")
    g_io.supprimer_feuille_1(api_sheets, mon_id)


def generer_table_chrono_condensee_raw(gn: GN):
    # pour chaque personnage, construire un tableau contenant, dans l'ordre chronologique,
    # toutes les scènes du personnage avec le texte "il y a..., titrescène"
    tableau_sortie = []
    for perso in list(gn.personnages.values()):
        mes_scenes = []
        for role in perso.roles:
            mes_scenes.extend(iter(role.scenes))
        mes_scenes = Scene.trier_scenes(mes_scenes, date_gn=gn.get_date_gn())

        # créer des lignes [date][évènement]
        # ma_ligne = [personnage.nom] + [[s.get_formatted_date(date_gn=gn.date_gn), s.titre] for s in mes_scenes]
        ma_ligne = [perso.nom] + mes_scenes
        tableau_sortie.append(ma_ligne)

    return tableau_sortie


@attrappeur_dexceptions
def ecrire_solveur_planning_dans_drive(mon_gn: GN, api_sheets, api_drive, m_print=print):
    m_print("******* génération du planning évènementiel ******************")

    tables_planning, texte_erreur = generer_tables_planning_evenementiel(mon_gn)

    # faire un onglet par session
    # voir si on ne peut pas chopper le paramètre des sessions qu'on veut explorer (sera utile aussi pour les squelettes)
    parent = mon_gn.get_dossier_outputs_drive()
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- planning evènementiel'
    file_id = g_io.creer_google_sheet(api_drive, nom_fichier, parent,
                                      id_dossier_archive=mon_gn.get_id_dossier_archive())
    for session in tables_planning.keys():
        g_io.write_to_sheet(api_sheets, tables_planning[session], file_id, feuille=session)
    g_io.supprimer_feuille_1(api_sheets, file_id)

    if texte_erreur:
        m_print("Une ou plusieurs erreurs ont été identifiées pendant le calcul du planning, "
                "vérifiez le fichier d'erreur associé")
        texte_erreur_concat = '\n'.join(texte_erreur)
        logging.debug('erreurs dans la préparation des évènements pour la création de planning : ')
        logging.debug(texte_erreur_concat)
        print(f"DEBUG : erreurs evenements pre ORTOOLS : {texte_erreur_concat}")
        # todo : écrire les erreurs dans un fichier


def generer_tables_planning_evenementiel(mon_gn: GN):
    # identifier toutes les sessions
    sessions = mon_gn.get_liste_sessions_froms_pnjs()

    # faire un premier onglet sans session
    evenementiel_generique, texte_erreur = cpe.creer_planning_evenementiel(mon_gn)
    tables_planning = {'evenementiel générique': evenementiel_generique}
    for session in sessions:
        tables_planning[session] = cpe.creer_planning_evenementiel(mon_gn, session=session)

    return tables_planning, texte_erreur


def generer_table_chrono_condensee(tableau_raw, date_gn):
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
                # row.append(f"{date} - {event}")
                row.append(lien_vers_hyperlink(story[i + 1].conteneur.get_full_url(), f"{date} - {event}"))
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
    #     print(f"clef-formatted-titre = {scene.clef_tri(date_gn)}
    #     / {scene.get_formatted_date(date_gn=date_gn)} / {scene.titre}")
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
    logging.debug(f"correspondance date_to_index = {date_to_index}")
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
            # hyperlinks impossibles car potentiellement plusieurs liens dans la meme case
            # matrix[i + 1][j + 1] = '\n'.join([matrix[i + 1][j + 1],
            #                                   lien_vers_hyperlink(event.conteneur.get_full_url(),
            #                                                       f"{event.titre} \n ({event.conteneur.nom})")])

    return matrix


def generer_table_chrono_scenes(mon_gn: GN):
    # Dates	Horaires	Episodes / Intrigues	Titre	Evênement	PJ concernés	PNJ concernés
    toutes_scenes = Scene.trier_scenes(mon_gn.lister_toutes_les_scenes())
    to_return = [['Date', 'Intrigue', 'Scène', 'PJs concernés', 'PNJ, concernés']]

    for scene in toutes_scenes:
        to_return.append([
            scene.get_formatted_date(mon_gn.get_date_gn()),
            # scene.conteneur.nom
            lien_vers_hyperlink(scene.conteneur.get_full_url(), scene.conteneur.nom),
            scene.titre,
            ', '.join([role.str_avec_perso() for role in scene.get_roles() if role is not None and role.est_un_pj()]),
            ', '.join([role.str_avec_perso() for role in scene.get_roles() if role is not None and role.est_un_pnj()]),

        ])
    return to_return


@attrappeur_dexceptions
def ecrire_table_chrono_dans_drive(mon_gn: GN, api_drive, api_sheets, m_print=print):
    m_print("******* table planning ***********************")
    parent = mon_gn.get_dossier_outputs_drive()
    table_raw = generer_table_chrono_condensee_raw(mon_gn)
    table_simple = generer_table_chrono_condensee(table_raw, mon_gn.get_date_gn())
    table_complete = generer_table_chrono_complete(table_raw, mon_gn.get_date_gn())
    table_chrono_scenes = generer_table_chrono_scenes(mon_gn)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- synthèse chrono'
    file_id = g_io.creer_google_sheet(api_drive, nom_fichier, parent,
                                      id_dossier_archive=mon_gn.get_id_dossier_archive())
    g_io.write_to_sheet(api_sheets, table_simple, file_id, feuille="condensée")
    g_io.write_to_sheet(api_sheets, table_complete, file_id, feuille="étendue")
    g_io.write_to_sheet(api_sheets, table_chrono_scenes, file_id,
                        feuille="toutes les scènes")
    g_io.supprimer_feuille_1(api_sheets, file_id)


def generer_tableau_recap_persos(gn: GN):
    # to_return = []
    to_return = [["Nom Perso", "Orga Référent", "Points", "Nombre d'intrigue", "Intrigues"]]
    for perso in gn.get_dict_pj().values():
        # table_perso = [role.conteneur.nom for role in perso.roles]
        table_perso = [lien_vers_hyperlink(role.conteneur.get_full_url(), role.conteneur.nom) for role in perso.roles]
        # for role in perso.roles:
        #     table_perso += [role.conteneur.nom]
        table_perso = sorted(table_perso)
        # pip = perso.sommer_pip()
        # densite = pip / len(table_perso) if len(table_perso) > 0 else 0

        tableau_pip = perso.get_tableau_pips()
        pip = sum(tableau_pip)
        taille_pip = len(tableau_pip)

        # nb_intrigues = pip / taille_pip if taille_pip > 0 else 0

        # table_perso = [perso.nom] + [perso.orga_referent] + [pip] + [f"{nb_intrigues:.2f}"] + table_perso
        table_perso = [perso.nom] + [perso.orga_referent] + [pip] + [taille_pip] + table_perso
        to_return.append(table_perso)

    return to_return


@attrappeur_dexceptions
def ecrire_table_persos(mon_gn: GN, api_drive, api_sheets, m_print=print):
    m_print("******* table récap PJS ********************")

    parent = mon_gn.get_dossier_outputs_drive()
    table = generer_tableau_recap_persos(mon_gn)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- synthèse des intrigues par personnage'
    file_id = g_io.creer_google_sheet(api_drive, nom_fichier, parent,
                                      id_dossier_archive=mon_gn.get_id_dossier_archive())
    g_io.write_to_sheet(api_sheets, table, file_id)


def generer_table_pnjs_etendue(gn: GN, verbal=False):
    table_pnj = [["nom PNJ", "description",
                  "type_pj",
                  "niveau implication",
                  "details intervention",
                  "intrigue", "nom dans l'intrigue"]]

    # print("ping table pnj")
    # print(f"pnjs contenus : {gn.dictPNJs.keys()}")
    liste_pnj = gn.get_dict_pnj().values()
    for pnj in liste_pnj:
        table_pnj.extend(
            [
                pnj.nom,
                role.description,
                pnj.string_type_personnage(),
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
                  "intrigues",
                  "évènements",
                  "Nombre scènes et évènements"]]

    logging.debug(f"pnjs contenus : {gn.get_dict_pnj()}")

    table_pnj.extend(
        [
            pnj.nom,
            pnj.string_type_personnage(),
            pnj.toutes_les_apparitions(),
            pnj.str_interventions(),
            pnj.nombre_scenes() + pnj.nombre_evenements()
        ]
        for pnj in gn.get_dict_pnj().values()
    )

    if verbal:
        for pnj in gn.get_dict_pnj().values():
            print(f"{pnj.nom}")
            for role in pnj.roles:
                print(f"table pnj : pnj en cours d'ajout : {pnj.nom}")
                print(f"{pnj.nom}")
                print(f"{role.description}")
                print(f"{pnj.string_type_personnage()}")
                print(f"{role.niveauImplication}")
                print(f"{role.perimetre_intervention}")
                print(f"{role.conteneur.nom}")
                print(f"{role.nom}")

    if verbal:
        print(table_pnj)

    return table_pnj


@attrappeur_dexceptions
def ecrire_table_pnj(mon_gn: GN, api_drive, api_sheets, m_print=print):
    m_print("******* table récap PNJS ********************")

    parent = mon_gn.get_dossier_outputs_drive()
    table_etendue = generer_table_pnjs_etendue(mon_gn)
    table_simple = generer_table_pnjs_simple(mon_gn)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- table des PNJs'
    file_id = g_io.creer_google_sheet(api_drive, nom_fichier, parent,
                                      id_dossier_archive=mon_gn.get_id_dossier_archive())
    g_io.write_to_sheet(api_sheets, table_simple, file_id, feuille="En synthèse")
    g_io.write_to_sheet(api_sheets, table_etendue, file_id, feuille="Vision détaillée")
    if mon_gn.get_mode_association() == GN.ModeAssociation.AUTO:
        table_pnj_dedup = generer_table_pnj_dedupliquee(mon_gn)
        g_io.write_to_sheet(api_sheets, table_pnj_dedup, file_id,
                            feuille="Suggestion liste dedupliquée")
    g_io.supprimer_feuille_1(api_sheets, file_id)


def generer_table_pnj_dedupliquee(mon_gn: GN):
    table_pnj = [["Nom", "Déjà présent avec exactement ce nom?", "Autres orthographes identifiées",
                  "Actuellement affecté à"]]

    noms_actuels = mon_gn.noms_pnjs()
    noms_dedup, orthographes, persos_affectes = generer_liste_pnj_dedup_avec_perso(mon_gn)

    table_pnj.extend(
        [nom_pnj, "oui" if nom_pnj in noms_actuels else "non", ','.join(variations), nom_perso]
        for nom_pnj, variations, nom_perso in zip(noms_dedup, orthographes, persos_affectes)
    )
    return table_pnj


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
        mes_scenes = Scene.trier_scenes(dict_infos[info], date_gn=gn.get_date_gn())

        to_return += f"Scènes associées à {info} : \n"
        # for scene in dict_infos[info]:
        for scene in mes_scenes:
            to_return += scene.str_pour_squelette() + '\n'
        to_return += '***************************** \n'
    return to_return


@attrappeur_dexceptions
def ecrire_texte_info(mon_gn: GN, api_doc, api_drive, m_print=print):
    m_print("******* aides de jeu *************************")

    parent = mon_gn.get_dossier_outputs_drive()

    texte = generer_textes_infos(mon_gn)
    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- données pour aides de jeu'
    mon_id = g_io.creer_google_doc(api_drive, nom_fichier, parent,
                                   id_dossier_archive=mon_gn.get_id_dossier_archive())
    g_io.write_to_doc(
        api_doc, mon_id, texte
    )


def generer_table_commentaires(gn: GN, prefixe=None):
    # Get a list of all unique authors and destinataires
    intrigues = gn.intrigues.values()
    destinataires = set()
    dict_auteur_intrigues = {}  # [auteur][intrigue] > commentaires, utilisé our générer le doc complet
    dict_intrigues_destinataires = {}  # [intrigue] > liste noms destinataires

    # for intrigue in intrigues:
    #     for commentaire in intrigue.commentaires:
    #         if commentaire.auteur not in dict_auteur_intrigues:
    #             dict_auteur_intrigues[commentaire.auteur] = set()
    #         dict_auteur_intrigues[commentaire.auteur].add(intrigue)
    #         destinataires.update(commentaire.destinataires)
    for intrigue in intrigues:
        for commentaire in intrigue.commentaires:
            if commentaire.auteur not in dict_auteur_intrigues:
                dict_auteur_intrigues[commentaire.auteur] = {}
            if intrigue not in dict_auteur_intrigues[commentaire.auteur]:
                dict_auteur_intrigues[commentaire.auteur][intrigue] = set()
            # print(f"clef dict_auteur_intrigues[commentaire.auteur] : {dict_auteur_intrigues[commentaire.auteur]}")
            dict_auteur_intrigues[commentaire.auteur][intrigue].add(commentaire)
            destinataires.update(commentaire.destinataires)

            valeur_nom = lien_vers_hyperlink(intrigue.get_full_url(), intrigue.nom)
            if valeur_nom not in dict_intrigues_destinataires:
                dict_intrigues_destinataires[valeur_nom] = set()
            dict_intrigues_destinataires[valeur_nom].update(commentaire.destinataires)
            # if intrigue.nom not in dict_intrigues_destinataires:
            #     dict_intrigues_destinataires[intrigue.nom] = set()
            # dict_intrigues_destinataires[intrigue.nom].update(commentaire.destinataires)

    dict_auteurs_tableaux = {auteur: [["Intrigue"] + list(destinataires)] for auteur in dict_auteur_intrigues}

    # Formatter, pour chaque auteur, un tableau des intrigues où il a écrit des commentaires
    for auteur in dict_auteur_intrigues:
        for intrigue in dict_auteur_intrigues[auteur]:
            valeur_nom_intrigue = lien_vers_hyperlink(intrigue.get_full_url(), intrigue.nom)
            row = [valeur_nom_intrigue] + [""] * len(destinataires)
            # row = [intrigue.nom] + [""] * len(destinataires)
            # for commentaire in intrigue.commentaires:
            for commentaire in dict_auteur_intrigues[auteur][intrigue]:
                # if auteur != commentaire.auteur:
                #     continue
                for destinataire in commentaire.destinataires:
                    column_index = list(destinataires).index(destinataire)
                    row[column_index + 1] = "x"
            dict_auteurs_tableaux[auteur].append(row)

    # Formatter un talbeau global intrigues > commentaires pour qui
    tableau_global = [["Intrigue"] + list(destinataires)]
    for nom_intrigue in dict_intrigues_destinataires:
        row = [nom_intrigue] + [""] * len(destinataires)
        # for commentaire in intrigue.commentaires:
        for destinataire in dict_intrigues_destinataires[nom_intrigue]:
            column_index = list(destinataires).index(destinataire)
            row[column_index + 1] = "x"
        tableau_global.append(row)

    if prefixe is not None:
        # Write the 2D list to a CSV file
        for auteur in dict_auteurs_tableaux:
            with open(f"{prefixe} comment_table_{auteur}.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(dict_auteurs_tableaux[auteur])

    return dict_auteurs_tableaux, dict_auteur_intrigues, tableau_global


def generer_texte_commentaires(dict_auteur_intrigues):
    to_return = ""
    for auteur in dict_auteur_intrigues:
        to_return += f"\t \t {auteur}, voici les commentaires ouverts dont tu es l'auteur \n"
        for intrigue in dict_auteur_intrigues[auteur]:
            to_return += f"\t pour l'intrigue {intrigue} : \n\n"
            for commentaire in dict_auteur_intrigues[auteur][intrigue]:
                to_return += commentaire.texte + '\n\n'
            to_return += '\n'
        to_return += '******************************************* \n'
    return to_return


@attrappeur_dexceptions
def ecrire_table_commentaires(mon_gn: GN, api_drive, api_doc, api_sheets, m_print=print):
    m_print("******* table commentaires *******************")

    parent = mon_gn.get_dossier_outputs_drive()
    dict_auteurs_tableaux, dict_auteur_intrigues, tableau_global = generer_table_commentaires(mon_gn)
    texte = generer_texte_commentaires(dict_auteur_intrigues)

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- commentaires ouverts dans les documents'
    mon_id = g_io.creer_google_doc(api_drive, nom_fichier, parent,
                                   id_dossier_archive=mon_gn.get_id_dossier_archive())
    g_io.write_to_doc(
        api_doc, mon_id, texte
    )

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- table des commentaires'

    file_id = g_io.creer_google_sheet(api_drive, nom_fichier, parent,
                                      id_dossier_archive=mon_gn.get_id_dossier_archive())
    for auteur in dict_auteurs_tableaux:
        g_io.write_to_sheet(api_sheets, dict_auteurs_tableaux[auteur], file_id,
                            feuille=auteur)
    g_io.write_to_sheet(api_sheets, tableau_global, file_id,
                        feuille="tableau global")
    g_io.supprimer_feuille_1(api_sheets, file_id)


def generer_table_relations_personnages(gn):
    # tous_les_persos = gn.dictPJs.values()
    tous_les_persos = gn.personnages.values()

    dict_relations_nature = {}  # [perso.nom][nom corelationnaire] > [] de natures de relations
    for perso in tous_les_persos:
        for role in perso.roles:
            for relation in role.relations:
                if perso.nom not in dict_relations_nature:
                    dict_relations_nature[perso.nom] = {}
                partenaires, nature_relation, reciproque = relation.trouver_partenaires(role)
                for corelationnaire in partenaires:
                    if corelationnaire.personnage is not None:
                        texte_role = corelationnaire.personnage.nom
                    else:
                        texte_role = f"{corelationnaire.nom} (pas de perso affecté)"
                    if texte_role not in dict_relations_nature[perso.nom]:
                        dict_relations_nature[perso.nom][texte_role] = []
                    dict_relations_nature[perso.nom][texte_role].append(nature_relation)

    liste_partenaires = set()
    for value in dict_relations_nature.values():
        for nom_partenaire in value:
            liste_partenaires.add(nom_partenaire)

    liste_partenaires = list(liste_partenaires)
    liste_persos = list(dict_relations_nature)

    print(liste_persos)
    print(liste_partenaires)

    # préparation des fonctions d'indexation
    partenaire_to_index = {c: i for i, c in enumerate(liste_partenaires)}
    perso_to_index = {p: i for i, p in enumerate(liste_persos)}

    # Initialize the matrix with empty values
    nb_personnages = len(liste_persos)
    nb_partenaires = len(liste_partenaires)

    # matrix = [['' for j in range(num_stories + 1)] for i in range(num_dates + 1)]
    matrix = [['' for _ in range(nb_partenaires + 1)] for _ in range(nb_personnages + 1)]

    # remplir la première ligne avec les noms des partenaires
    for j, partenaire in enumerate(liste_partenaires):
        matrix[0][j + 1] = partenaire

    # remplir la première colonne avec le nom de tous les persos
    for i, perso in enumerate(liste_persos):
        matrix[i + 1][0] = perso

    # remplir la table
    for perso in dict_relations_nature:
        for partenaire in dict_relations_nature[perso]:
            i = perso_to_index[perso]
            j = partenaire_to_index[partenaire]
            # print(f"relations entre {perso} et {partenaire} : {dict_relations_nature[perso][partenaire]}")
            matrix[i + 1][j + 1] = '\n'.join(dict_relations_nature[perso][partenaire])

    return matrix


@attrappeur_dexceptions
def ecrire_table_relation(mon_gn: GN, api_drive, api_sheets, m_print=print):
    m_print("********** table relations *******************")

    parent = mon_gn.get_dossier_outputs_drive()
    tab_relations = generer_table_relations_personnages(mon_gn)

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- table des relations'

    file_id = g_io.creer_google_sheet(api_drive, nom_fichier, parent,
                                      id_dossier_archive=mon_gn.get_id_dossier_archive())
    g_io.write_to_sheet(api_sheets, tab_relations, file_id)


def generer_table_evenements(gn: GN):
    # Jour / heure / lieu / description / pnj impliqués / costume / implication /  débute / pj impliqués /
    toutes_interventions = []
    # for evenement in gn.evenements.values():
    for evenement in gn.lister_tous_les_conteneurs_evenements_unitaires():
        toutes_interventions.extend(evenement.interventions)

    toutes_interventions = sorted(toutes_interventions, key=lambda x: [x.jour_formatte(), x.heure_debut_formattee()])

    to_return = [["Code", "Jour", "Heure", "Lieu", "Description", "PNJs impliqués", "Costumes PNJs", "Implication PNJs",
                  "Démarrage PNJ", "PJ impliqués", "Intrigue", 'Évènement', 'Référent']]
    for intervention in toutes_interventions:
        intervenants = intervention.liste_intervenants

        pnj_pour_tableau = [f"{e}. {intervenant.str_avec_perso()}"
                            for e, intervenant in enumerate(intervenants, start=1)]

        costumes_pnjs = [f"{e}. {intervenant.costumes_et_accessoires}"
                         for e, intervenant in enumerate(intervenants, start=1)]

        implications_pnjs = [f"{e}. {intervenant.implication}"
                             for e, intervenant in enumerate(intervenants, start=1)]

        demarrage_pnjs = [f"{e}. {intervenant.situation_de_depart}"
                          for e, intervenant in enumerate(intervenants, start=1)]

        pj_pour_tableau = [pj.str_avec_perso()
                           for pj in intervention.liste_pjs_concernes]

        nom_intrigue = intervention.get_nom_intrigue()
        # nom_intrigue = intervention.evenement.intrigue.nom if intervention.evenement.intrigue is not None \
        #     else f"Pas d'intrigue pour l'évènement {intervention.evenement.code_evenement}"

        ligne = [intervention.get_code_evenement(),
                 intervention.jour_formatte(),
                 intervention.heure_debut_formattee(),
                 intervention.get_lieu(),
                 intervention.description,
                 '\n'.join(pnj_pour_tableau),
                 '\n'.join(costumes_pnjs),
                 '\n'.join(implications_pnjs),
                 '\n'.join(demarrage_pnjs),
                 '\n'.join(pj_pour_tableau),
                 nom_intrigue,
                 intervention.get_nom_conteneur(),
                 intervention.evenement.get_referent()
                 ]
        # ligne = [intervention.evenement.code_evenement,
        #          intervention.jour_formatte(),
        #          intervention.heure_debut_formattee(),
        #          intervention.evenement.lieu,
        #          intervention.description,
        #          '\n'.join(pnj_pour_tableau),
        #          '\n'.join(costumes_pnjs),
        #          '\n'.join(implications_pnjs),
        #          '\n'.join(demarrage_pnjs),
        #          '\n'.join(pj_pour_tableau),
        #          nom_intrigue,
        #          intervention.evenement.nom_evenement,
        #          intervention.evenement.referent
        #          ]
        # # print(f"debug : ligne : {ligne}")
        to_return.append(ligne)
        # print(f"debug : ligne = {ligne}")
        # print(f"debug : To8r = {to_return}")

    return to_return


@attrappeur_dexceptions
def ecrire_table_evenements(mon_gn: GN, api_drive, api_sheets, m_print=print):
    m_print("******* table des évènements ******************")

    parent = mon_gn.get_dossier_outputs_drive()
    tab_evenements = generer_table_evenements(mon_gn)

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- table des evenements'

    file_id = g_io.creer_google_sheet(api_drive, nom_fichier, parent,
                                      id_dossier_archive=mon_gn.get_id_dossier_archive())
    g_io.write_to_sheet(api_sheets, tab_evenements, file_id)


def generer_table_questionnaire(gn: GN):
    toutes_les_questions = [
        [intrigue] + intrigue.input_questionnaire_inscription
        for intrigue in gn.intrigues.values()
    ]

    tous_les_headers = set()

    # Collecter tous les en-têtes uniques à partir des questions
    for intrigue_questions in toutes_les_questions:
        for dico in intrigue_questions[1:]:
            tous_les_headers.update(dico.keys())

    # S'assurer que "Identifiant" est le premier dans la liste des en-têtes
    liste_headers = ["Identifiant"] + [header for header in tous_les_headers if header != "Identifiant"]

    # Initialiser le tableau de sortie avec les entêtes
    tableau_final = [liste_headers]

    for intrigue_questions in toutes_les_questions:
        intrigue = intrigue_questions[0]
        id_intrigue = g_io.ref_du_doc(intrigue.nom, prefixes="I")

        for j, dico in enumerate(intrigue_questions[1:], 1):
            prefixes_id_questions = f"I{id_intrigue:03d}-{j}"
            # Assurer que l'identifiant est le premier élément de chaque ligne
            ligne_a_ajouter = [prefixes_id_questions] + [dico.get(cle, '') for cle in liste_headers if
                                                         cle != "Identifiant"]
            tableau_final.append(ligne_a_ajouter)

    return tableau_final

    ##########################################
    # for intrigue in gn.intrigues.values():
    #     for i, questions in enumerate(intrigue.questionnaire, start=1):
    #         ligne = [prefixes_id_questions + str(i)] + questions
    #         toutes_les_questions.append(ligne)
    # return toutes_les_questions


@attrappeur_dexceptions
def ecrire_table_questionnaire(gn: GN, api_drive, api_sheets, m_print=print):
    m_print("******* table des questions pour inscription ******************")

    parent = gn.get_dossier_outputs_drive()
    tab_questionnaire = generer_table_questionnaire(gn)

    nom_fichier = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                  f'- Fichier questionnaire inscription'

    file_id = g_io.creer_google_sheet(api_drive, nom_fichier, parent,
                                      id_dossier_archive=gn.get_id_dossier_archive())
    g_io.write_to_sheet(api_sheets, tab_questionnaire, file_id)


def fichier_ini_defaut():
    try:
        ini_mgn_files = [f for f in os.listdir('.') if f.endswith('.ini') or f.endswith('.mgn')]
        return os.path.abspath(ini_mgn_files[0]) if len(ini_mgn_files) == 1 else "config.ini"
    except Exception:
        return "pas de fichier magnet chargé"


def verifier_derniere_version(api_doc):
    try:

        # document = api_doc.documents().get(documentId=ID_FICHIER_VERSION).execute()
        # contenu_document = document.get('body').get('content')
        # text = lecteurGoogle.read_structural_elements(contenu_document)
        # text = text.replace('\v', '\n')  # pour nettoyer les backspace verticaux qui se glissent
        texte, _ = g_io.lire_google_doc(api_doc, ID_FICHIER_VERSION, extraire_formattage=False, avec_bullets=True)
        to_return = ""
        last_url = None
        # start_include = False
        ma_version = version.parse(VERSION)
        last_version = None

        for ligne in texte.splitlines():
            try:
                version_lue = version.parse(ligne)
                if last_version is None:
                    last_version = version_lue
                if version_lue <= ma_version:
                    break
            except version.InvalidVersion:
                pass

            if ligne.startswith("https"):
                if last_url is None:
                    last_url = ligne
            else:
                to_return += ligne + '\n'

        # print(f"last version / ma version = {last_version} / {ma_version} / {ma_version > last_version}")
        return last_version <= ma_version, to_return, last_url
        # return last_url is None, to_return, last_url

    except Exception as e:
        print(f"{e}")
        logging.debug(f"Une erreur est survenue pendant la lecture du fichier de version {e}")
        return True, [e], None
