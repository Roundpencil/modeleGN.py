from __future__ import print_function

import configparser
import io
import os
from enum import Enum
from typing import Optional

import fuzzywuzzy.process
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaIoBaseUpload

from modeleGN import *

ID_FICHIER_ARCHIVES = '1tEXjKfiU8k_SU_jyVAoUQU1K9Gp77Cv0'


def extraire_intrigues(mon_gn: GN, api_drive, api_doc, singletest="-01", verbal=False, fast=True, m_print=print,
                       visualisation=lambda x: print("barre de visualisation virtuelle : +", x),
                       taille_visualisation=100.0):
    print("Début de la lecture des intrigues")
    return extraire_texte_de_google_doc(api_drive, api_doc, extraire_intrigue_de_texte, mon_gn.intrigues,
                                        mon_gn.get_dossiers_intrigues(),
                                        singletest, verbal=verbal, fast=fast, prefixes=mon_gn.get_prefixe_intrigues(),
                                        m_print=m_print,
                                        visualisation=visualisation,
                                        taille_visualisation=taille_visualisation
                                        )


def extraire_pjs(mon_gn: GN, api_drive, api_doc, singletest="-01", verbal=False, fast=True, m_print=print,
                 visualisation=lambda x: print("barre de visualisation virtuelle : +", x),
                 taille_visualisation=100.0):
    print(f"je m'apprête à extraire les PJs depuis {mon_gn.get_dossiers_pjs()}")
    return extraire_texte_de_google_doc(
        api_drive, api_doc, extraire_persos_de_texte, mon_gn.personnages, mon_gn.get_dossiers_pjs(),
        # api_drive, api_doc, extraire_persos_de_texte, mon_gn.dictPJs, mon_gn.dossiers_pjs,
        singletest,
        verbal=verbal, fast=fast, prefixes=mon_gn.get_prefixe_pjs(), m_print=m_print,
        visualisation=visualisation,
        taille_visualisation=taille_visualisation)


def extraire_pnjs(mon_gn: GN, api_drive, api_doc, singletest="-01", verbal=False, fast=True, m_print=print,
                  visualisation=lambda x: print("barre de visualisation virtuelle : +", x),
                  taille_visualisation=100.0):
    print(f"je m'apprête à extraire les PNJs depuis {mon_gn.get_dossiers_pnjs()}")
    if mon_gn.get_dossiers_pnjs() is None or len(mon_gn.get_dossiers_pnjs()) == 0:
        logging.debug("pas de dossier pnj trouvé dans le gn")
        return
    # return extraire_texte_de_google_doc(
    #     mon_gn, api_drive, api_doc, extraire_persos_de_texte, mon_gn.dictPNJs,
    #                                     mon_gn.dossiers_pnjs,
    #                                     singletest,
    #                                     verbal=verbal, fast=fast, prefixes="p")

    return extraire_texte_de_google_doc(api_drive, api_doc, extraire_pnj_de_texte, mon_gn.personnages,
                                        mon_gn.get_dossiers_pnjs(),
                                        singletest,
                                        verbal=verbal, fast=fast, prefixes=mon_gn.get_prefixe_pnjs(), m_print=m_print,
                                        visualisation=visualisation,
                                        taille_visualisation=taille_visualisation)


def extraire_evenements(mon_gn: GN, api_drive, api_doc, singletest="-01", verbal=False, fast=True, m_print=print,
                        visualisation=lambda x: print("barre de visualisation virtuelle : +", x),
                        taille_visualisation=100.0):
    print(f"je m'apprete à extraire les évènements depuis {mon_gn.get_dossiers_evenements()}")
    if mon_gn.get_dossiers_evenements() is None or len(mon_gn.get_dossiers_evenements()) == 0:
        logging.debug("pas de dossier évènement trouvé dans le gn")
        return
    return extraire_texte_de_google_doc(api_drive, api_doc, extraire_evenement_de_texte, mon_gn.evenements,
                                        mon_gn.get_dossiers_evenements(),
                                        singletest,
                                        verbal=verbal, fast=fast, prefixes=mon_gn.get_prefixe_evenements(),
                                        m_print=m_print,
                                        visualisation=visualisation,
                                        taille_visualisation=taille_visualisation)


def extraire_objets(mon_gn: GN, api_drive, api_doc, singletest="-01", verbal=False, fast=True, m_print=print,
                    visualisation=lambda x: print("barre de visualisation virtuelle : +", x),
                    taille_visualisation=100.0):
    print(f"je m'apprete à extraire les objets depuis {mon_gn.get_dossiers_objets()}")
    if mon_gn.get_dossiers_objets() is None or len(mon_gn.get_dossiers_objets()) == 0:
        logging.debug("pas de dossier objets trouvé dans le gn")
        return
    return extraire_texte_de_google_doc(api_drive, api_doc, extraire_objets_de_texte, mon_gn.objets_de_reference,
                                        mon_gn.get_dossiers_objets(),
                                        singletest,
                                        verbal=verbal, fast=fast, prefixes=mon_gn.get_prefixe_objets(), m_print=m_print,
                                        visualisation=visualisation,
                                        taille_visualisation=taille_visualisation)


# def extraire_texte_de_google_doc(api_drive, api_doc, fonction_extraction, dict_ids: dict, folder_array,
#                                  single_test="-01", verbal=False, fast=True, prefixes="", m_print=print,
#                                  visualisation=lambda x: print("barre de visualisation virtuelle : +", x),
#                                  taille_visualisation=100.0):
#     items = lecteurGoogle.generer_liste_items(api_drive=api_drive, nom_fichier=folder_array)
#     # print(f"folder = {folder_array}  items = {items}")
#
#     if not items:
#         print('No files found.')
#         return
#
#     # print(f"single_test : {type(single_test)} = {single_test}")
#     if int(single_test) > 0:
#         for item in items:
#             try:
#                 # Retrieve the documents contents from the Docs api_doc.
#                 item_id = item['id']
#                 document = api_doc.documents().get(documentId=item_id).execute()
#                 titre_doc = document.get('title')
#
#                 m_print(f"Document en cours de lecture (singletest = {single_test}) : {titre_doc}")
#
#                 # Alors on se demande si c'est le bon doc
#                 # if document.get('title')[0:3].strip() != str(single_test):  # numéro de l'intrigue
#                 #     # si ce n'est pas la bonne, pas la peine d'aller plus loin
#                 #     continue
#                 if ref_du_doc(titre_doc, prefixes=prefixes) != int(single_test):
#                     continue
#
#                 m_print(f"j'ai trouvé le doc #{single_test} : {document.get('title')}")
#                 # if item['id'] in gn.intrigues.keys():
#                 #     gn.intrigues[item['id']].clear()
#                 #     del gn.intrigues[item['id']]
#
#                 objet_de_reference = None
#                 if item['id'] in dict_ids:
#                     # dict_ids[item['id']].clear()
#                     objet_de_reference = dict_ids.pop(item['id'])
#
#                 nouvel_objet = extraire_elements_de_document(document, item, dict_ids, fonction_extraction,
#                                                              save_last_change=False, verbal=verbal)
#                 # et on ajoute les commentaires :
#                 commentaires = extraire_commentaires_de_document_drive(api_drive, item['id'])
#                 if callable(getattr(nouvel_objet, 'ajouter_commentaires', None)):
#                     nouvel_objet.ajouter_commentaires(commentaires)
#
#                 if objet_de_reference is not None:
#                     if isinstance(nouvel_objet, ConteneurDeScene):
#                         nouvel_objet.updater_dates_maj_scenes(objet_de_reference)
#                     objet_de_reference.clear()
#
#                 break
#                 # on a trouvé le bon doc, on arrête de chercher
#             except HttpError as err:
#                 print(f'An error occurred: {err}')
#                 # return #ajouté pour débugger
#
#     else:
#         # dans ce cas, on lit tout, jusqu'à ce qu'on tombe sur une entrée qui n'a pas été modifiée
#         nb_items = len(items)
#         pas_visualisation = taille_visualisation / nb_items
#         # print(f"debug : taille visualisation / pas de visuations : {taille_visualisation} / {pas_visualisation}")
#         for i, item in enumerate(items, start=1):
#             try:
#                 visualisation(pas_visualisation)
#                 # Retrieve the documents contents from the Docs api_doc.
#                 document = api_doc.documents().get(documentId=item['id']).execute()
#
#                 m_print(f"Document en cours de lecture ({i}/{nb_items}) : {document.get('title')}")
#
#                 # print(f"débug : ref du doc = {ref_du_doc(document.get('title'))}")
#
#                 # si la ref du doc est -1 ou 0 il ne nous interesse pas
#                 titre_doc = document.get('title')
#                 if ref_du_doc(titre_doc, prefixes=prefixes) in [-1, 0]:
#                     logging.debug(f"Le nom du document {titre_doc} n'est pas un fichier à prendre en compte")
#                     continue
#
#                 # print("... est une intrigue !")
#
#                 objet_de_reference = None
#
#                 # on vérifie d'abord s'il est nécessaire de traiter (dernière maj intrigue > derniere maj objet) :
#                 #   SI l'intrigue existe dans le GN ?
#                 # if item['id'] in gn.intrigues .keys():
#                 if item['id'] in dict_ids:
#                     # print(f"debug : {item['id']} est dans dict_id")
#
#                     #       SI la date de mise à jour du fichier n'est pas postérieure à la date de MAJ de l'intrigue
#                     # print("l'intrigue fait déjà partie du GN ! ")
#                     # print(f"Variable / type : gn.intrigues[item['id']].lastChange /
#                     # {type(gn.intrigues[item['id']].lastChange)} / {gn.intrigues[item['id']].lastChange}")
#                     # print(f"Variable / type : item['modifiedTime'] / {type(item['modifiedTime'])} /
#                     # {item['modifiedTime']}")
#
#                     # on enlève les 5 derniers chars qui sont un point, les millisecondes et Z, pour formatter
#                     if fast and \
#                             dict_ids[item['id']].lastProcessing >= datetime.datetime.strptime(
#                         item['modifiedTime'][:-5], '%Y-%m-%dT%H:%M:%S'):
#
#                         m_print(
#                             f"et il n'a pas changé (dernier changement : "
#                             f"{datetime.datetime.strptime(item['modifiedTime'][:-5], '%Y-%m-%dT%H:%M:%S')}) "
#                             f"depuis le dernier passage ({dict_ids[item['id']].lastProcessing})")
#
#                         visualisation(pas_visualisation * (nb_items - i))
#                         # ALORS : Si c'est la même que la plus vielle mise à jour : on arrête
#                         # si c'était la plus vieille du GN, pas la peine de continuer
#
#                         break
#                         # on a trouvé une intrigue qui n'a pas bougé :
#                         # toutes les suivantes qu'il nous remontera seront plus anciennes
#                         # donc on arrête de parcourir
#                     else:
#                         # print("elle a changé depuis mon dernier passage : supprimons-la !")
#                         # dans ce cas, il faut la supprimer, car on va tout réécrire
#                         # gn.intrigues[item['id']].clear()
#                         # del gn.intrigues[item['id']]
#
#                         objet_de_reference = dict_ids.pop(item['id'])
#
#                 # puis, dans tous les cas, on la crée
#                 # print("debug : extraction objet")
#                 nouvel_objet = extraire_elements_de_document(document, item, dict_ids, fonction_extraction,
#                                                              verbal=verbal)
#                 commentaires = extraire_commentaires_de_document_drive(api_drive, item['id'])
#                 if callable(getattr(nouvel_objet, 'ajouter_commentaires', None)):
#                     nouvel_objet.ajouter_commentaires(commentaires)
#
#                 if objet_de_reference is not None:
#                     if isinstance(nouvel_objet, ConteneurDeScene):
#                         nouvel_objet.updater_dates_maj_scenes(objet_de_reference)
#                     objet_de_reference.clear()
#
#             except HttpError as err:
#                 print(f'An error occurred: {err}')
#                 m_print(f"Document en cours de lecture ({i}/{nb_items}) : pas d'info MAGnet contenue")
#
#                 # return #ajouté pour débugger
#
#     return [item['id'] for item in items]

def extraire_texte_de_google_doc(api_drive, api_doc, fonction_extraction, dict_ids: dict, folder_array,
                                 single_test="-01", verbal=False, fast=True, prefixes="", m_print=print,
                                 visualisation=lambda x: print("barre de visualisation virtuelle : +", x),
                                 taille_visualisation=100.0):
    items = lecteurGoogle.generer_liste_items(api_drive=api_drive, nom_fichier=folder_array)

    if not items:
        print('No files found.')
        return

    is_single_test = int(single_test) > 0
    nb_items = len(items)
    pas_visualisation = taille_visualisation / nb_items

    for i, item in enumerate(items, start=1):
        try:
            visualisation(pas_visualisation)
            item_id = item['id']
            document = api_doc.documents().get(documentId=item_id).execute()
            titre_doc = document.get('title')
            m_print(f"Document en cours de lecture ({i} / {nb_items}) : {titre_doc}")
            print(f"Document en cours de lecture ({i} / {nb_items}) : {titre_doc}")

            ref_doc = ref_du_doc(titre_doc, prefixes=prefixes)

            if is_single_test:
                if ref_doc != int(single_test):
                    continue
                m_print(f"j'ai trouvé le doc #{single_test} : {titre_doc}")
            else:
                if ref_doc in [-1, 0]:
                    logging.debug(f"Le nom du document {titre_doc} n'est pas un fichier à prendre en compte")
                    continue

                if fast and is_item_not_modified(item, dict_ids):
                    visualisation(pas_visualisation * (nb_items - i))
                    m_print(f"et il n'a pas changé (dernier changement : "
                            f"{datetime.datetime.strptime(item['modifiedTime'][:-5], '%Y-%m-%dT%H:%M:%S')}) "
                            f"depuis le dernier passage ({dict_ids[item['id']].get_last_processing()})")
                    break

            objet_de_reference = dict_ids.pop(item_id, None)
            nouvel_objet = extraire_elements_de_document(document, item, dict_ids, fonction_extraction, verbal=verbal)
            commentaires = extraire_commentaires_de_document_drive(api_drive, item_id)
            ajouter_commentaires_si_possible(nouvel_objet, commentaires)
            update_scenes_dates_if_needed(objet_de_reference, nouvel_objet)

        except HttpError as err:
            print(f'An error occurred: {err}')
            m_print(f"Document en cours de lecture ({i}/{nb_items}) : pas d'info MAGnet contenue")

    return [item['id'] for item in items]


def is_item_not_modified(item, dict_ids):
    if item['id'] not in dict_ids:
        return False

    last_processed_time = dict_ids[item['id']].get_last_processing()
    item_modified_time = datetime.datetime.strptime(item['modifiedTime'][:-5], '%Y-%m-%dT%H:%M:%S')
    return last_processed_time >= item_modified_time


def ajouter_commentaires_si_possible(objet, commentaires):
    if callable(getattr(objet, 'ajouter_commentaires', None)):
        objet.ajouter_commentaires(commentaires)


def update_scenes_dates_if_needed(objet_de_reference, nouvel_objet):
    if objet_de_reference is not None and isinstance(nouvel_objet, ConteneurDeScene):
        nouvel_objet.updater_dates_maj_scenes(objet_de_reference)
        objet_de_reference.clear()


def extraire_elements_de_document(document, item, dict_reference: dict, fonction_extraction, save_last_change=True,
                                  verbal=False):
    # print("et du coup, il est temps de créer un nouveau fichier")
    # à ce stade, soit on sait qu'elle n'existait pas, soit on l'a effacée pour la réécrire
    contenu_document = document.get('body').get('content')
    texte_avec_format = lecteurGoogle.read_structural_elements(contenu_document)
    texte_avec_format = texte_avec_format.replace('\v', '\n')  # pour nettoyer les backspace verticaux qui se glissent

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

    mon_objet = fonction_extraction(texte_avec_format, document.get('title'), item["id"], last_file_edit,
                                    derniere_modification_par,
                                    dict_reference, verbal)
    # mon_objet.url = item["id"]
    # on enregistre la date de dernière mise à jour

    if mon_objet is not None and save_last_change:
        mon_objet.set_last_processing(datetime.datetime.now())
    # print(f'url intrigue = {mon_objet.url}')
    # print(f"intrigue {mon_objet.nom}, date de modification : {item['modifiedTime']}")

    return mon_objet


def extraire_intrigue_de_texte(texte_avec_format, nom_intrigue,
                               id_url, last_file_edit, derniere_modification_par,
                               dict_intrigues,
                               verbal=False):
    # print("texte intrigue en entrée : ")
    # print(texteIntrigue.replace('\v', '\n'))
    # texteIntrigue = texteIntrigue.replace('\v', '\n')
    # print("*****************************")
    current_intrigue = Intrigue(nom=nom_intrigue, url=id_url, derniere_edition_fichier=last_file_edit)
    current_intrigue.modifie_par = derniere_modification_par
    dict_intrigues[id_url] = current_intrigue

    # noms_persos = gn.liste_noms_pjs()

    # on fait un dict du début de chaque label
    class Labels(Enum):
        REFERENT = "orga référent :"
        TODO = "etat de l’intrigue :"
        PITCH = "résumé de l’intrigue"
        CROISEES = "intrigues croisées :"
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
        RELATIONS_BI = "relations bilatérales induites par cette intrigue"
        RELATIONS_MULTI = "relations multilatérales induites par cette intrigue"
        GRILLE_EVENEMENTS = 'événementiel à prévoir en jeu'

    labels = [lab.value for lab in Labels]

    # indexes = lecteurGoogle.identifier_sections_fiche(labels, texte_seul)
    # print(f"debug : indexes = {indexes}")
    dict_sections, erreurs = lecteurGoogle.text_2_dict_sections(labels, texte_avec_format)
    current_intrigue.add_list_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                           erreurs,
                                           ErreurManager.ORIGINES.STRUCTURE_FICHIER_INTRIGUE)

    dict_methodes = {
        Labels.REFERENT: lambda x, y: intrigue_referent(x, current_intrigue, Labels.REFERENT.value),
        Labels.TODO: lambda x, y: intrigue_todo(x, current_intrigue, Labels.TODO.value),
        Labels.PITCH: lambda x, y: intrigue_pitch(x, current_intrigue),
        Labels.CROISEES: lambda x, y: intrigue_croisee(x, Labels.CROISEES.value),
        Labels.PJS: lambda x, y: intrigue_pjs(x, current_intrigue),
        Labels.PNJS: lambda x, y: intrigue_pnjs(x, current_intrigue),
        Labels.REROLLS: lambda x, y: intrigue_rerolls(x, current_intrigue),
        Labels.OBJETS: lambda x, y: intrigue_objets(x, current_intrigue),
        Labels.SCENESFX: lambda x, y: intrigue_scenesfx(x, current_intrigue),
        Labels.TIMELINE: lambda x, y: intrigue_timeline(x, current_intrigue),
        Labels.SCENES: lambda x, y: intrigue_scenes(x, y, current_intrigue, Labels.SCENES.value),
        Labels.RESOLUTION: lambda x, y: intrigue_resolution(x, current_intrigue),
        Labels.NOTES: lambda x, y: intrigue_notes(x, current_intrigue),
        Labels.QUESTIONNAIRE: lambda x, y: intrigue_questionnaire(x, current_intrigue),
        Labels.RELATIONS_BI: lambda x, y: intrigue_relations_bi(x, current_intrigue),
        Labels.RELATIONS_MULTI: lambda x, y: intrigue_relations_multi(x, current_intrigue),
        Labels.GRILLE_EVENEMENTS: lambda x, y: evenement_lire_chrono(x, current_intrigue)
    }

    for label in Labels:
        if paire := dict_sections.get(label.value):
            ma_methode = dict_methodes[label]
            ma_methode(paire['brut'], paire['formatté'])
        elif verbal:
            print(f"pas de {label.value} avec l'intrigue {nom_intrigue}")

        # if indexes[label.value]["debut"] == -1:
        #     print(f"pas de {label.value} avec l'intrigue {nom_intrigue}")
        # else:
        #     ma_methode = dict_methodes[label]
        #     input_pure = texte_seul[indexes[label.value]["debut"]:indexes[label.value]["fin"]]
        #     input_format = texte_avec_format[indexes[label.value]["debut"]:indexes[label.value]["fin"]]
        #     # print(f"debug : texte label {label.value} = {texte}")
        #     # ma_methode(texte, current_intrigue, label.value)
        #     ma_methode(input_pure, input_format)

    return current_intrigue


def intrigue_referent(texte: str, intrigue: Intrigue, texte_label: str):
    intrigue.orga_referent = retirer_label(texte, texte_label)


def intrigue_todo(texte: str, intrigue: Intrigue, texte_label: str):
    intrigue.questions_ouvertes = retirer_label(texte, texte_label)


def intrigue_croisee(texte: str, texte_label: str):
    logging.debug(f"balise {texte_label} non prise en charge = {texte}")


def intrigue_pitch(texte: str, intrigue: Intrigue):
    intrigue.pitch = retirer_premiere_ligne(texte)


def intrigue_pjs(texte: str, current_intrigue: Intrigue):
    tableau_pjs, nb_colonnes = reconstituer_tableau(texte, sans_la_premiere_ligne=False)

    if nb_colonnes == 0:
        texte_erreur = "le tableau des PJs est inexploitable"
        current_intrigue.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                          texte_erreur,
                                          ErreurManager.ORIGINES.SCENE)
        return

    class NomsColonnes(Enum):
        AFFECTATION = "Affecté à"
        GENRE = "Genre"
        NOM_PERSO = "Nom du personnage"
        PIP_I = "Points d’intérêt intrigue"
        PIP_R = "Points d’intérêt roleplay"
        IMPLICATION = "Type d’implication"
        TYPE_INTRIGUE = "Type d’intrigue"
        PIP = "Points d’intérêt"
        DESCRIPTION = "Résumé de l’implication"
        TYPE_PERSONNAGE = "Type de Personnage"

    # dict_headers = generer_dict_header_vers_no_colonne(en_tetes=tableau_pjs[0],
    #                                                    noms_colonnes=[nom_col.value for nom_col in NomsColonnes],
    #                                                    erreur_manager=current_intrigue.error_log)
    # # noms_colonnes = [nc.value for nc in NomsColonnes]
    # # headers = tableau_pjs[0]
    # # dict_headers = generer_dict_header_vers_no_colonne(headers, noms_colonnes, current_intrigue.error_log)
    #
    # grille_types_persos = {"PJ": TypePerso.EST_PJ,
    #                        "PNJ": TypePerso.EST_PNJ_HORS_JEU,
    #                        "Reroll": TypePerso.EST_REROLL,
    #                        "PNJ Infiltré": TypePerso.EST_PNJ_INFILTRE,
    #                        "PNJ Hors Jeu": TypePerso.EST_PNJ_HORS_JEU,
    #                        "PNJ Permanent": TypePerso.EST_PNJ_PERMANENT,
    #                        "PNJ Temporaire": TypePerso.EST_PNJ_TEMPORAIRE}
    #
    # for ligne in tableau_pjs[1:]:
    #     nom = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.NOM_PERSO.value, "rôle sans nom :(")
    #     logging.debug(f"value  ={NomsColonnes.NOM_PERSO.value}, nom = {nom}")
    #     description = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.DESCRIPTION.value, "")
    #     pipi = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP_I.value, 0)
    #     pipr = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP_R.value, 0)
    #     sexe = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.GENRE.value, "i")
    #     type_intrigue = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.TYPE_INTRIGUE.value, "")
    #     niveau_implication = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.IMPLICATION.value, "")
    #     pip_globaux = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP.value, 0)
    #     type_personnage_brut = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.TYPE_PERSONNAGE.value,
    #                                                           "PJ")

    # grille_types_persos = {"PJ": TypePerso.EST_PJ,
    #                        "PNJ": TypePerso.EST_PNJ_HORS_JEU,
    #                        "Reroll": TypePerso.EST_REROLL,
    #                        "PNJ Infiltré": TypePerso.EST_PNJ_INFILTRE,
    #                        "PNJ Hors Jeu": TypePerso.EST_PNJ_HORS_JEU,
    #                        "PNJ Permanent": TypePerso.EST_PNJ_PERMANENT,
    #                        "PNJ Temporaire": TypePerso.EST_PNJ_TEMPORAIRE}

    liste_dicos_pjs = generer_liste_de_dict_from_tableau(tableau_pjs,
                                                         noms_colonnes=[nom_col.value for nom_col in NomsColonnes],
                                                         erreur_manager=current_intrigue.error_log)

    for dico_pj in liste_dicos_pjs:
        nom = dico_pj.get(NomsColonnes.NOM_PERSO.value, "rôle sans nom :(")
        logging.debug(f"value  ={NomsColonnes.NOM_PERSO.value}, nom = {nom}")
        description = dico_pj.get(NomsColonnes.DESCRIPTION.value, "")
        pipi = dico_pj.get(NomsColonnes.PIP_I.value, 0)
        pipr = dico_pj.get(NomsColonnes.PIP_R.value, 0)
        sexe = dico_pj.get(NomsColonnes.GENRE.value, "i")
        type_intrigue = dico_pj.get(NomsColonnes.TYPE_INTRIGUE.value, "")
        niveau_implication = dico_pj.get(NomsColonnes.IMPLICATION.value, "")
        pip_globaux = dico_pj.get(NomsColonnes.PIP.value, 0)
        type_personnage_brut = dico_pj.get(NomsColonnes.TYPE_PERSONNAGE.value, "PJ")

        # type_personnage_brut = process.extractOne(type_personnage_brut, grille_types_persos.keys())[0]
        # type_perso = grille_types_persos[type_personnage_brut]
        type_perso = identifier_type_perso(type_personnage_brut, avec_pjs=True, avec_pnjs=True, avec_rerolls=True)

        # nettoyage du nom
        # nom_et_alias = nom.split("http")[0].split(' aka ')
        # nom = nom_et_alias[0]
        # alias = nom_et_alias[1:] if len(nom_et_alias) > 1 else None
        nom, alias = separer_nom_et_alias(nom.split("http")[0])

        if len(liste_pips := str(pip_globaux).split('/')) == 2:
            pip_globaux = 0
            pipi = liste_pips[0] + pipi
            pipr = liste_pips[1] + pipr
        # affectation = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.AFFECTATION.value, "")
        affectation = dico_pj.get(NomsColonnes.AFFECTATION.value, "")

        # logging.debug(f"Tableau des headers : {dict_headers}")
        # logging.debug(f"ligne = {ligne}")
        logging.debug(f"lecture associée : "
                      f"{[nom, description, pipi, pipr, sexe, type_intrigue, niveau_implication, pip_globaux, affectation]}")
        role_a_ajouter = Role(current_intrigue,
                              nom=nom,
                              description=description,
                              type_intrigue=type_intrigue,
                              niveau_implication=niveau_implication,
                              pipi=pipi,
                              pipr=pipr,
                              genre=sexe,
                              pip_globaux=pip_globaux,
                              affectation=affectation,
                              pj=type_perso,
                              alias_dans_intrigue=alias
                              )
        current_intrigue.rolesContenus[role_a_ajouter.nom] = role_a_ajouter


# def generer_dict_header_vers_no_colonne(en_tetes, noms_colonnes, erreur_manager: ErreurManager):
#     """
#     Associe les entêtes du tableau aux noms de colonnes prévus et renvoie un dictionnaire avec les correspondances.
#
#     :param en_tetes: Liste des entêtes du tableau.
#     :param noms_colonnes: Liste des noms de colonnes attendus.
#     :param erreur_manager: Instance d'ErreurManager pour gérer les erreurs.
#     :return: Dictionnaire avec les correspondances entre les entêtes et les noms de colonnes.
#     """
#     tab_rectifie = normaliser_en_tete_tableau(en_tetes, noms_colonnes, erreur_manager)
#     return {en_tete: i for i, en_tete in enumerate(tab_rectifie)}


def normaliser_en_tete_tableau(en_tetes_bruts: list[str], noms_colonnes_cibles: list[str],
                               erreur_manager: ErreurManager, verbal=False):
    """
    Normalise les en-têtes d'un tableau en fonction d'une liste de noms de colonnes cibles.

    Cette fonction prend une liste d'en-têtes bruts et les compare à une liste de noms de colonnes cibles,
    en trouvant le meilleur match pour chaque en-tête. Les en-têtes sont ainsi "rectifiés" pour correspondre
    aux noms de colonnes attendus. En cas de faible score de correspondance ou de duplication des en-têtes rectifiés,
    des erreurs sont enregistrées à l'aide de l'`erreur_manager` :
    Warning: En cas de score inférieur à 85 % lors de la correspondance des en-têtes.
    Erreur: Si une valeur d'en-tête est trouvée en double après rectification.


    Parameters:
        en_tetes_bruts (list[str]): Liste des en-têtes tels que lus dans le tableau brut.
        noms_colonnes_cibles (list[str]): Liste des noms de colonnes attendus ou cibles.
        erreur_manager (ErreurManager): Gestionnaire des erreurs pour enregistrer les problèmes rencontrés.
        verbal: Pour afficher des messages d'erreurs

    Returns:
        list[str]: Liste des en-têtes rectifiés correspondant aux noms de colonnes cibles.

    Note:
        Si les résultats de la correspondance sont jugés insuffisants, une autre approche plus complexe
        peut être envisagée au prix d'une diminution de la performance globale.
        :param erreur_manager:
        :param verbal:
    """

    # si on a en entrée un tableau vide, alors on renvoie un tableau vide pour obtenir un dictionnaire avec une clef
    # inutilisable derrière, dont les fonctions get renverrons la valeur par défaut.
    if en_tetes_bruts == ['']:
        return ['']

    # À noter : cette fonction est une version simplifiée de celle qui suggère les tableaux en trouvant le meilleur
    # match. Si les résultats sont trop mauvais, il est possible d'utiliser la même structure, au prix de perdre en
    # performance globale.

    if verbal:
        print(f'En-têtes lus : {en_tetes_bruts}')
        print(f'Noms colonnes cibles : {noms_colonnes_cibles}')

    tab_rectifie = []
    min_score = 100
    pire_match = ""
    for head in en_tetes_bruts:
        score = process.extractOne(head, noms_colonnes_cibles)
        tab_rectifie.append(score[0])
        if score[1] < min_score:
            min_score = score[1]
            pire_match = score[0]

        if verbal:
            print(f'En-Tête : {head}; proposition : {score[0]}; score : {score[1]}')

    logging.debug("lecture auto des tableaux :")
    for i in range(len(en_tetes_bruts)):
        logging.debug(f"{en_tetes_bruts[i]} > {tab_rectifie[i]}")
    if min_score < 85:
        texte_erreur = f"Attention, score bas de lecture des entêtes du tableau des personnages. " \
                       f"Pire score : {min_score}% pour {pire_match}. Tableau lu = {tab_rectifie}"
        erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                      texte_erreur,
                                      ErreurManager.ORIGINES.SCENE)
    if len(set(tab_rectifie)) != len(tab_rectifie):
        texte_erreur = f"une valeur a été trouvée en double dans les en-têtes de colonne d'un tableau. " \
                       f"Tableau lu = {tab_rectifie}"
        erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                      texte_erreur,
                                      ErreurManager.ORIGINES.SCENE)
    return tab_rectifie


def generer_liste_de_dict_from_tableau(tableau_avec_en_tetes, noms_colonnes, erreur_manager: ErreurManager,
                                       verbal=False):
    entetes_normalises = normaliser_en_tete_tableau(tableau_avec_en_tetes[0], noms_colonnes, erreur_manager,
                                                    verbal=verbal)

    # on crée un tableau de dictionnaires avec les valeurs lues
    to_return = []
    valeurs = tableau_avec_en_tetes[1:]
    for ligne in valeurs:
        current_dict = {
            entetes_normalises[i]: valeur_colonne
            for i, valeur_colonne in enumerate(ligne)
        }
        to_return.append(current_dict)

    return to_return


# def en_tete_vers_valeur_dans_ligne(ligne_tableau: list[str], dict_header_vers_no_colonne: dict, header_value, default):
#     """
#     Récupère la valeur d'une colonne spécifique dans une ligne de tableau en utilisant le mappage des entêtes.
#
#     :param ligne_tableau: Liste des valeurs de la ligne du tableau.
#     :param dict_header_vers_no_colonne: Dictionnaire avec les correspondances entre les entêtes et les noms de colonnes.
#     :param header_value: Entête de la colonne à rechercher.
#     :param default: Valeur par défaut à renvoyer si l'entête n'est pas trouvée.
#     :return: Valeur de la colonne correspondant à l'entête donnée ou la valeur par défaut si l'entête n'est pas trouvée.
#     """
#     logging.debug(f"header / table header {header_value} {dict_header_vers_no_colonne.get(header_value)}")
#     logging.debug(f"ligne : {ligne_tableau}")
#     debug_value = dict_header_vers_no_colonne.get(header_value)
#     if debug_value is not None:
#         logging.debug(f"pour la valeur {debug_value} : {ligne_tableau[debug_value]}")
#     index = dict_header_vers_no_colonne.get(header_value)
#     return ligne_tableau[index] if index is not None else default


def intrigue_pnjs(texte: str, current_intrigue: Intrigue, seuil_type_perso=85):
    tableau_pnjs, nb_colonnes = reconstituer_tableau(texte, sans_la_premiere_ligne=False)

    if nb_colonnes == 0:
        texte_erreur = "le tableau des Rerolls est inexploitable"
        current_intrigue.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                          texte_erreur,
                                          ErreurManager.ORIGINES.SCENE)
        return

    # header = tableau_pnjs[0]

    class NomsColonnes(Enum):
        AFFECTATION = "Affecté à"
        GENRE = "Genre"
        NOM_PERSO = "Nom du PNJ et/ou fonction"
        IMPLICATION = "Type d’implication"
        TYPE_INTRIGUE = "Type d’intrigue"
        DESCRIPTION = "Résumé de l’implication"
        TYPE_PERSONNAGE = "Intervention"

    # grille_types_persos = {"PNJ": TypePerso.EST_PNJ_HORS_JEU,
    #                        "PNJ Infiltré": TypePerso.EST_PNJ_INFILTRE,
    #                        "PNJ Hors Jeu": TypePerso.EST_PNJ_HORS_JEU,
    #                        "PNJ Permanent": TypePerso.EST_PNJ_PERMANENT,
    #                        "PNJ Temporaire": TypePerso.EST_PNJ_TEMPORAIRE}

    # noms_colonnes = [c.value for c in NomsColonnes]
    # dict_headers = generer_dict_header_vers_no_colonne(header, noms_colonnes, current_intrigue.error_log)
    #
    # for pnj in tableau_pnjs[1:]:
    #     affectation = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.AFFECTATION.value, "")
    #     genre = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.GENRE.value, "i")
    #     nom = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.NOM_PERSO.value, "")
    #     implication = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.IMPLICATION.value, "")
    #     description = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.DESCRIPTION.value, "")
    #     type_personnage_brut = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.TYPE_PERSONNAGE.value,
    #                                                           "PNJ Hors Jeu")
    #     score_type_perso = process.extractOne(type_personnage_brut, grille_types_persos.keys())
    #
    #     if score_type_perso[1] < seuil_type_perso:
    #         type_perso = TypePerso.EST_PNJ_HORS_JEU
    #     else:
    #         type_personnage = score_type_perso[0]
    #         type_perso = grille_types_persos[type_personnage]
    #
    #     nom, alias = separer_nom_et_alias(nom.split("http")[0])
    #
    #     pnj_a_ajouter = Role(current_intrigue,
    #                          nom=nom,
    #                          description=description,
    #                          pj=type_perso,
    #                          niveau_implication=implication,
    #                          perimetre_intervention=type_personnage_brut,
    #                          genre=genre,
    #                          affectation=affectation,
    #                          alias_dans_intrigue=alias)
    #
    #     # du coup, on peut l'ajouter aux intrigues
    #     current_intrigue.rolesContenus[pnj_a_ajouter.nom] = pnj_a_ajouter

    noms_colonnes = [c.value for c in NomsColonnes]

    liste_dicos_pnjs = generer_liste_de_dict_from_tableau(tableau_pnjs, noms_colonnes, current_intrigue.error_log)
    for dico_pnj in liste_dicos_pnjs:
        affectation = dico_pnj.get(NomsColonnes.AFFECTATION.value, "")
        genre = dico_pnj.get(NomsColonnes.GENRE.value, "i")
        nom = dico_pnj.get(NomsColonnes.NOM_PERSO.value, "")
        implication = dico_pnj.get(NomsColonnes.IMPLICATION.value, "")
        description = dico_pnj.get(NomsColonnes.DESCRIPTION.value, "")
        type_personnage_brut = dico_pnj.get(NomsColonnes.TYPE_PERSONNAGE.value, "PNJ Hors Jeu")

        # score_type_perso = process.extractOne(type_personnage_brut, grille_types_persos.keys())
        #
        # if score_type_perso[1] < seuil_type_perso:
        #     type_perso = TypePerso.EST_PNJ_HORS_JEU
        # else:
        #     type_personnage = score_type_perso[0]
        #     type_perso = grille_types_persos[type_personnage]
        type_perso = identifier_type_perso(type_personnage_brut, avec_pnjs=True, seuil=seuil_type_perso)

        nom, alias = separer_nom_et_alias(nom.split("http")[0])

        pnj_a_ajouter = Role(current_intrigue,
                             nom=nom,
                             description=description,
                             pj=type_perso,
                             niveau_implication=implication,
                             perimetre_intervention=type_personnage_brut,
                             genre=genre,
                             affectation=affectation,
                             alias_dans_intrigue=alias)

        # du coup, on peut l'ajouter aux intrigues
        current_intrigue.rolesContenus[pnj_a_ajouter.nom] = pnj_a_ajouter


def separer_nom_et_alias(nom):
    nom_et_alias = nom.split(' aka ')
    nom = nom_et_alias[0]
    alias = nom_et_alias[1:] if len(nom_et_alias) > 1 else None
    return nom, alias


def intrigue_rerolls(texte: str, current_intrigue: Intrigue):
    tableau_rerolls, nb_colonnes = reconstituer_tableau(texte, sans_la_premiere_ligne=False)

    # tab_rerolls, _ = reconstituer_tableau(texte)
    # # faire un tableau avec une ligne par Reroll
    # for reroll in tab_rerolls:  # on enlève la première ligne qui contient les titres
    #     # même pnj que les PJs
    #     re_roll_a_ajouter = Role(intrigue, nom=reroll[0], description=reroll[3],
    #                              pj=TypePerso.EST_REROLL, type_intrigue=reroll[2],
    #                              niveau_implication=reroll[1])
    #
    #     # du coup, on peut l'ajouter aux intrigues
    #     intrigue.rolesContenus[re_roll_a_ajouter.nom] = re_roll_a_ajouter
    if nb_colonnes == 0:
        texte_erreur = "le tableau des Rerolls est inexploitable"
        current_intrigue.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                          texte_erreur,
                                          ErreurManager.ORIGINES.SCENE)
        return

    class NomsColonnes(Enum):
        AFFECTATION = "Affecté à"
        GENRE = "Genre"
        NOM_PERSO = "Nom du personnage"
        PIP_I = "Points d’intérêt intrigue"
        PIP_R = "Points d’intérêt roleplay"
        IMPLICATION = "Type d’implication"
        TYPE_INTRIGUE = "Type d’intrigue"
        PIP = "Points d’intérêt"
        DESCRIPTION = "Résumé de l’implication"

    noms_colonnes = [nc.value for nc in NomsColonnes]
    # headers = tableau_rerolls[0]
    # dict_headers = generer_dict_header_vers_no_colonne(headers, noms_colonnes, current_intrigue.error_log)
    #
    # for ligne in tableau_rerolls[1:]:
    #     nom = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.NOM_PERSO.value, "rôle sans nom :(")
    #     logging.debug(f"value  ={NomsColonnes.NOM_PERSO.value}, nom = {nom}")
    #     description = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.DESCRIPTION.value, "")
    #     pipi = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP_I.value, 0)
    #     pipr = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP_R.value, 0)
    #     sexe = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.GENRE.value, "i")
    #     type_intrigue = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.TYPE_INTRIGUE.value, "")
    #     niveau_implication = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.IMPLICATION.value, "")
    #     pip_globaux = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP.value, 0)

    liste_dicos_rerolls = generer_liste_de_dict_from_tableau(tableau_rerolls, noms_colonnes, current_intrigue.error_log)

    for dico_reroll in liste_dicos_rerolls:
        nom = dico_reroll.get(NomsColonnes.NOM_PERSO.value, "rôle sans nom :(")
        logging.debug(f"value  ={NomsColonnes.NOM_PERSO.value}, nom = {nom}")
        description = dico_reroll.get(NomsColonnes.DESCRIPTION.value, "")
        pipi = dico_reroll.get(NomsColonnes.PIP_I.value, 0)
        pipr = dico_reroll.get(NomsColonnes.PIP_R.value, 0)
        sexe = dico_reroll.get(NomsColonnes.GENRE.value, "i")
        type_intrigue = dico_reroll.get(NomsColonnes.TYPE_INTRIGUE.value, "")
        niveau_implication = dico_reroll.get(NomsColonnes.IMPLICATION.value, "")
        pip_globaux = dico_reroll.get(NomsColonnes.PIP.value, 0)

        if len(liste_pips := str(pip_globaux).split('/')) == 2:
            pip_globaux = 0
            pipi = liste_pips[0] + pipi
            pipr = liste_pips[1] + pipr
        affectation = dico_reroll.get(NomsColonnes.AFFECTATION.value, "")

        # logging.debug(f"Tableau des headers : {dict_headers}")
        # logging.debug(f"ligne = {ligne}")
        logging.debug(f"lecture associée : "
                      f"{[nom, description, pipi, pipr, sexe, type_intrigue, niveau_implication, pip_globaux, affectation]}")
        nom, alias = separer_nom_et_alias(nom.split("http")[0])
        role_a_ajouter = Role(current_intrigue,
                              nom=nom,
                              description=description,
                              type_intrigue=type_intrigue,
                              niveau_implication=niveau_implication,
                              pipi=pipi,
                              pipr=pipr,
                              genre=sexe,
                              pip_globaux=pip_globaux,
                              affectation=affectation,
                              pj=TypePerso.EST_REROLL,
                              alias_dans_intrigue=alias
                              )
        current_intrigue.rolesContenus[role_a_ajouter.nom] = role_a_ajouter


def intrigue_objets(texte: str, current_intrigue: Intrigue):
    tab_objets, nb_colonnes = reconstituer_tableau(texte, sans_la_premiere_ligne=False)

    if nb_colonnes == 0:
        texte_erreur = "le tableau des objets  est inexploitable"
        current_intrigue.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                          texte_erreur,
                                          ErreurManager.ORIGINES.SCENE)
        return

    class NomsColonnes(Enum):
        CODE = "Code"
        DESCRIPTION = "Description"
        FX = "Effets spéciaux nécessaires (si aucun, vide)"
        RFID = "RFID (non / oui (si pas plus clair sur ce qu’il fait) / description de ce qu’il fait)"
        START = "Où se trouve-t-il en début de jeu ? (Personnage ou lieu)"
        FOURNI_PAR = "Fourni par ?"
        LIEN_FICHE = "Lien vers la fiche objet (Facultatif)"
        INFORMATIQUE = "Informatique"

    noms_colonnes = [nc.value for nc in NomsColonnes]
    headers = tab_objets[0]
    # dict_headers = generer_dict_header_vers_no_colonne(headers, noms_colonnes, current_intrigue.error_log)

    liste_dico_objets = generer_liste_de_dict_from_tableau(tab_objets, noms_colonnes, current_intrigue.error_log)

    # faire un tableau avec une ligne par objet
    for dico_objet in liste_dico_objets:
        mon_objet = Objet(code=dico_objet.get(NomsColonnes.CODE.value, ""),
                          description=dico_objet.get(NomsColonnes.DESCRIPTION.value, ""),
                          fourni_par=dico_objet.get(NomsColonnes.FOURNI_PAR.value, ""),
                          emplacement_debut=dico_objet.get(NomsColonnes.START.value, ""),
                          special_effect=dico_objet.get(NomsColonnes.FX.value, "")
                                         + dico_objet.get(NomsColonnes.RFID.value, ""),
                          informatique=dico_objet.get(NomsColonnes.INFORMATIQUE.value, "")
                          )

        current_intrigue.objets.add(mon_objet)
        mon_objet.intrigue = current_intrigue


def intrigue_scenesfx(texte: str, intrigue: Intrigue):
    # print(f" debug : texte fx = {texte}")
    tableau_evenements, nb_colonnes = reconstituer_tableau(texte)
    if nb_colonnes != 4:
        logging.debug(f" Problème avec le tableau évènement : {tableau_evenements}")
        return

    codes_raw = [ligne[0].strip() for ligne in tableau_evenements]
    intrigue.codes_evenements_raw = codes_raw


def intrigue_timeline(texte: str, intrigue: Intrigue):
    intrigue.timeline = retirer_premiere_ligne(texte)


def intrigue_scenes(texte_pur: str, texte_formatte: str, intrigue: Intrigue, texte_label: str):
    # texte = retirer_label(texte_pur, texte_label)
    # pas besoin de formatter, on ne prendra jamais j'index 0 qui contiendra l'entete + plus toutes les merdes
    # qui précèdent la première scène
    texte2scenes(intrigue, intrigue.nom, texte_pur, texte_formatte)


def intrigue_resolution(texte: str, intrigue: Intrigue):
    intrigue.resolution = retirer_premiere_ligne(texte)


def intrigue_notes(texte: str, intrigue: Intrigue):
    intrigue.notes = retirer_premiere_ligne(texte)


def intrigue_questionnaire(texte: str, intrigue: Intrigue):
    tab_questions, nb_colonnes = reconstituer_tableau(texte, sans_la_premiere_ligne=False)
    if not tab_questions or not nb_colonnes:
        return

    class NomsColonnes(Enum):
        QUESTION = "Question à inclure dans le questionnaire"
        EXPLICATION = "Explication si nécessaire"
        PERSO_CONCERNE = "Personnage(s) concerné(s) par la question"

    noms_colonnes = [nc.value for nc in NomsColonnes]
    intrigue.input_questionnaire_inscription += generer_liste_de_dict_from_tableau(tab_questions,
                                                                                   noms_colonnes,
                                                                                   intrigue.error_log)
    # if nb_colonnes != 2:
    #     texte_erreur = "le tableau questionnaire est inexploitable"
    #     intrigue.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
    #                               texte_erreur,
    #                               ErreurManager.ORIGINES.SCENE)


def intrigue_relations_bi(texte: str, intrigue: Intrigue):
    tab_relations_bi, _ = reconstituer_tableau(texte)
    extraire_relations_bi(intrigue, tab_relations_bi)


def intrigue_relations_multi(texte: str, intrigue: Intrigue):
    tab_relations_multi, _ = reconstituer_tableau(texte)
    # on a alors un tableau à deux colonnes avec les noms des persos et leurs relations
    extraire_relation_multi(intrigue, tab_relations_multi)


def extraire_relations_bi(conteneur: ConteneurDeScene, tab_relations_bi: list[[str, str, str, str]],
                          avec_tableau_persos: bool = True):
    # print(f"tab relations_bi = {tab_relations_bi}")
    for ligne_relation_bi in tab_relations_bi:
        if len(ligne_relation_bi[0]) == 0 or len(ligne_relation_bi[1]) == 0:
            texte_erreur = f"Le personnage " \
                           f"{ligne_relation_bi[0] if len(ligne_relation_bi[1]) == 0 else ligne_relation_bi[1]}" \
                           f"n'a pas de partenaire dans sa relation"
            conteneur.error_log.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                               texte_erreur,
                                               ErreurManager.ORIGINES.SCENE)
            continue

        tab_retour = qui_2_roles(
            [ligne_relation_bi[0], ligne_relation_bi[1]],
            conteneur,
            avec_tableau_des_persos=avec_tableau_persos
        )
        perso_a = tab_retour[0][1]
        perso_b = tab_retour[1][1]
        relation_a_ajouter = Relation.creer_relation_bilaterale(perso_a,
                                                                perso_b,
                                                                ligne_relation_bi[2],
                                                                ligne_relation_bi[3])
        perso_a.relations.add(relation_a_ajouter)
        perso_b.relations.add(relation_a_ajouter)


def extraire_relation_multi(conteneur, tab_relations_multi, verbal=False,
                            avec_tableau_des_persos=True, seuil=70):
    for ligne_relation_muti in tab_relations_multi:
        noms_roles = ligne_relation_muti[0].split(', ')
        description_relation_multi = ligne_relation_muti[1]
        # tab_retour_multi = qui_2_roles(noms_roles, conteneur,
        #                                conteneur.get_noms_roles(), avec_tableau_des_persos)
        tab_retour_multi = qui_2_roles(noms_roles, conteneur, avec_tableau_des_persos)
        roles_dans_relation_multi = []
        for correspondance in tab_retour_multi:
            nom, role, score = correspondance
            if score == 0:
                texte_erreur = f"Erreur, le nom : {nom} dans la relation {description_relation_multi} " \
                               f"n'a pas été associée à un rôle"
                conteneur.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                           texte_erreur,
                                           ErreurManager.ORIGINES.SCENE)
                if verbal:
                    print(texte_erreur)
                continue

            # si le role n'est pas None, l'ajouter à la liste des rôles qui feront partie de la relation
            roles_dans_relation_multi.append(role)
            if score < seuil:
                warning_text = f"Association relation ({score}%) - nom  : {nom} " \
                               f"> Role : {role.nom} dans {conteneur.nom}"
                conteneur.add_to_error_log(ErreurManager.NIVEAUX.WARNING,
                                           warning_text,
                                           ErreurManager.ORIGINES.SCENE)

        # à ce stade, on a viré les %, généré des messages d'alerte et préparé les listes
        relation_multi_a_ajouter = Relation.creer_relation_multilaterale(roles_dans_relation_multi,
                                                                         description_relation_multi
                                                                         )
        for role in roles_dans_relation_multi:
            role.relations.add(relation_multi_a_ajouter)


def extraire_balise(input_balise: str, scene_a_ajouter: Scene, conteneur: ConteneurDeScene,
                    tableau_roles_existant: bool = True):
    class Balises(Enum):
        QUAND = r"^##\s*quand\s*[:?]"
        IL_Y_A = r"^##\s*il y a\s*"
        DATE = r"^##\s*date\s*[:?]"
        QUI = r"^##\s*qui\s*[:?]"
        # NIVEAU = r"^##\s*niveau\s*[:?]"
        # RESUME = r"^##\s*résumé\s*[:?]"
        FACTIONS = r"^##\s*(faction|factions)\s*[:?]"
        INFOS = r"^##\s*(info|infos)\s*[:?]"
        HEURE = r"^##\s*heure\s*[:?]"
        OU = r"^##\s*(ou|où|lieu)\s*[:?]"

    dict_methodes = {
        Balises.QUAND: lambda x: extraire_date_scene(x, scene_a_ajouter),
        Balises.IL_Y_A: lambda x: extraire_il_y_a_scene(x, scene_a_ajouter),
        Balises.DATE: lambda x: extraire_date_absolue(x, scene_a_ajouter),
        Balises.QUI: lambda x: extraire_qui_scene(x, conteneur, scene_a_ajouter,
                                                  avec_tableau_des_persos=tableau_roles_existant),
        # Balises.RESUME:lambda x :None,
        Balises.FACTIONS: lambda x: extraire_factions_scene(x, scene_a_ajouter),
        Balises.INFOS: lambda x: extraire_infos_scene(x, scene_a_ajouter),
        Balises.HEURE: lambda x: scene_a_ajouter.set_heure_debut(x),
        Balises.OU: lambda x: scene_a_ajouter.set_lieu(x)
    }

    for balise in Balises:
        if match := re.search(balise.value, input_balise, re.IGNORECASE):
            end_pos = match.end()
            texte_balise = input_balise[end_pos:]
            methode_a_utiliser = dict_methodes[balise]
            methode_a_utiliser(texte_balise)
            return True

    return False


def texte2scenes(conteneur: ConteneurDeScene, nom_conteneur, texte_scenes_pur, texte_scenes_avec_format,
                 tableau_roles_existant=True, verbal=False):
    if verbal:
        print(f"Je viens d'entrer dans une scène avec le texte formatté suivant : \n {texte_scenes_avec_format}")

    # processed_text = []
    lignes_texte_pur = texte_scenes_pur.split('\n')
    lignes_texte_formatte = texte_scenes_avec_format.split('\n')

    scene_a_ajouter = None
    description_en_cours = []

    for ligne_pur, ligne_formatte in zip(lignes_texte_pur, lignes_texte_formatte):
        if ligne_pur.strip().startswith('###'):
            # on "vide" la scène en cours avant d'en recommencer une nouvelle
            ajouter_description_scene(conteneur, description_en_cours, scene_a_ajouter)

            description_en_cours.clear()
            titre_scene = ligne_pur.strip()[3:]
            scene_a_ajouter = conteneur.ajouter_scene(titre_scene)
            scene_a_ajouter.modifie_par = conteneur.modifie_par
        elif ligne_pur.strip().startswith('##'):
            if scene_a_ajouter:
                if not extraire_balise(ligne_pur.strip(), scene_a_ajouter, conteneur, tableau_roles_existant):
                    texte_erreur = f"balise inconnue : {ligne_pur} dans le conteneur {nom_conteneur}"
                    print(texte_erreur)
                    description_en_cours.append(ligne_formatte)
                    conteneur.error_log.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                       texte_erreur,
                                                       ErreurManager.ORIGINES.SCENE)
        else:
            if scene_a_ajouter:
                description_en_cours.append(ligne_formatte)

    # ajouter la fin du code de la dernière scène
    # texte_final = '\n'.join(description_en_cours)
    # for clef_formattage in lecteurGoogle.VALEURS_FORMATTAGE:
    #     texte_final = corriger_formattage(texte_final,
    #                                       lecteurGoogle.VALEURS_FORMATTAGE[clef_formattage][0],
    #                                       lecteurGoogle.VALEURS_FORMATTAGE[clef_formattage][1])
    # if scene_a_ajouter:
    #     scene_a_ajouter.description = texte_final
    ajouter_description_scene(conteneur, description_en_cours, scene_a_ajouter)

    # return processed_text


def ajouter_description_scene(conteneur, description_en_cours, scene_a_ajouter):
    # on commence par vider le stock dans la dernière scène enregistrée s'il y en a une, sinon on l'affiche
    texte_final = '\n'.join(description_en_cours)
    for clef_formattage in lecteurGoogle.VALEURS_FORMATTAGE:
        texte_final = corriger_formattage(texte_final,
                                          lecteurGoogle.VALEURS_FORMATTAGE[clef_formattage][0],
                                          lecteurGoogle.VALEURS_FORMATTAGE[clef_formattage][1])
    if scene_a_ajouter:
        scene_a_ajouter.description = texte_final
    elif texte_final.strip():
        message = f"Attention, le texte <<{repr(texte_final)}>> lu dans l'intrigue " \
                  f"ne fait partie d'aucune scène "
        print(message)
        conteneur.error_log.ajouter_erreur(ErreurManager.NIVEAUX.WARNING, message, ErreurManager.ORIGINES.SCENE)
        # print(f"Attention, le texte <<{texte_final}>> lu dans l'intrigue "
        #       f"ne fait partie d'aucune scène ")


# def texte2scenes(conteneur: ConteneurDeScene, nom_conteneur, texte_scenes_pur, texte_scenes_avec_format,
#                  tableau_roles_existant=True):
#     scenes_pur = texte_scenes_pur.split("###")
#     scenes_avec_format = texte_scenes_avec_format.split("###")
#
#     for scene_texte_pur, scene_avec_format in itertools.islice(zip(scenes_pur, scenes_avec_format), 1, None):
#
#         if len(scene_texte_pur) < 10:
#             continue
#
#         titre_scene = scene_texte_pur.splitlines()[0].strip()
#         scene_a_ajouter = conteneur.ajouter_scene(titre_scene)
#         scene_a_ajouter.modifie_par = conteneur.modifie_par
#
#         balises = re.findall(r'##.*', scene_texte_pur)
#         for balise in balises:
#             if not extraire_balise(balise, scene_a_ajouter, conteneur, tableau_roles_existant):
#                 texte_erreur = f"balise inconnue : {balise} dans le conteneur {nom_conteneur}"
#                 print(texte_erreur)
#                 scene_a_ajouter.description += balise
#                 conteneur.error_log.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
#                                                    texte_erreur,
#                                                    ErreurManager.ORIGINES.SCENE)
#
#         # et on reconstitue le texte à reprendre pour la description de la scène en reprenant scene_raw
#         # scene_a_ajouter.description = ''.join(scene_raw.splitlines(keepends=True)[1 + len(balises):])
#
#         texte_a_ajouter = ''.join(scene_avec_format.splitlines(keepends=True)[1 + len(balises):])
#         for clef_formattage in lecteurGoogle.VALEURS_FORMATTAGE:
#             texte_a_ajouter = corriger_formattage(texte_a_ajouter,
#                                                   lecteurGoogle.VALEURS_FORMATTAGE[clef_formattage][0],
#                                                   lecteurGoogle.VALEURS_FORMATTAGE[clef_formattage][1])
#
#         scene_a_ajouter.description = texte_a_ajouter


def corriger_formattage(texte, balise_debut, balise_fin):
    # Regular expression pattern to find all occurrences of the tags
    pattern = f"({re.escape(balise_debut)}|{re.escape(balise_fin)})"

    # Splitting the text into parts and tags
    parts = re.split(pattern, texte)

    stack = []
    valid_indices = set()

    for idx, part in enumerate(parts):
        if part == balise_debut:
            stack.append(idx)
        elif part == balise_fin and stack:
            start_idx = stack.pop()
            valid_indices.add(start_idx)
            valid_indices.add(idx)

    # Reconstruct the text with valid tags and text parts
    cleaned_text = ''.join(part for idx, part in enumerate(parts) if
                           idx in valid_indices or (part != balise_debut and part != balise_fin))

    return cleaned_text


def extraire_factions_scene(texte_lu: str, scene: Scene):
    for section in texte_lu.split(','):
        if len(section.strip()) > 1:
            scene.nom_factions.add(section.strip())


def extraire_infos_scene(texte_lu: str, scene: Scene):
    for section in texte_lu.split(','):
        if len(section) > 1:
            scene.infos.add(section.strip())


def extraire_qui_scene(liste_noms, conteneur, scene_a_ajouter, verbal=False, seuil=80,
                       avec_tableau_des_persos: bool = True):
    roles = [r.strip() for r in liste_noms.split(",") if len(r.strip()) > 0]
    scene_a_ajouter.noms_roles_lus = roles

    tab_corr = qui_2_roles(roles, conteneur, avec_tableau_des_persos)
    logging.debug(f"a partir de la liste de noms : {roles} j'ai généré : \n {tab_corr}")
    for element in tab_corr:
        nom_du_role, role_a_ajouter, score = element
        if score == 0:
            texte_erreur = f"Erreur, le nom : {nom_du_role} n'a pu être associé à aucun rôle " \
                           f"dans {scene_a_ajouter.titre}"
            if verbal:
                print(texte_erreur)
            conteneur.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                       texte_erreur,
                                       ErreurManager.ORIGINES.SCENE)
        else:
            role_a_ajouter.ajouter_a_scene(scene_a_ajouter, nom_brut=nom_du_role, score=score)
            # if score != 100:
            #     conteneur.rolesContenus[role_a_ajouter.nom] = role_a_ajouter
            if score < seuil:
                warning_text = f"Association Scene ({score}) - nom dans scène : {nom_du_role} " \
                               f"> Role : {role_a_ajouter.nom} dans {conteneur.nom}/{scene_a_ajouter.titre}"
                conteneur.add_to_error_log(ErreurManager.NIVEAUX.WARNING,
                                           warning_text,
                                           ErreurManager.ORIGINES.SCENE)
                if verbal:
                    print(warning_text)


def generer_permutations_alias(nom_du_role: str):
    noms_et_alias = nom_du_role.split(' aka ')
    to_return = [noms_et_alias[0]]
    for alias in noms_et_alias[1:]:
        to_return.extend((f'{to_return} aka {alias}', alias))
    return to_return


def qui_2_roles(roles: list[str], conteneur: ConteneurDeScene, avec_tableau_des_persos: bool = True):
    """
        Identifie et renvoie une liste de rôles présents dans une scène en fonction des noms fournis.

        Cette fonction permet d'associer des rôles à des noms détectés dans une scène en utilisant soit un conteneur
        pré-établi si 'avec_tableau_des_persos' est True, soit en les créant sur le pouce si ce n'est pas le cas.

        Args:
            roles: Une liste de chaînes de caractères représentant les noms des rôles à identifier.
            conteneur: Une instance de ConteneurDeScene qui contient des rôles et des méthodes pour gérer ces rôles.
            avec_tableau_des_persos: Un booléen qui indique si la fonction doit utiliser un tableau de référence
                                     des personnages (True par défaut). Si False, les rôles sont créés sans référence.

        Returns: Une liste composée de sous-listes tripartites. Chaque sous-liste correspond à un rôle analysé et
        contient les éléments suivants : - Le nom du rôle (`str`): la désignation textuelle exacte du rôle telle
        qu'elle apparaît dans la liste des rôles fournie. - L'instance du rôle (`Role` ou `None`): l'objet
        représentant le rôle associé à ce nom dans le conteneur de scènes, ou `None` si aucune correspondance n'est
        trouvée. - Le score de correspondance (`int`): une valeur numérique indiquant le degré de certitude de
        l'association. Un score de 100 signale une concordance directe et indiscutable avec un rôle connu dans le
        conteneur. Si un tableau de référence est consulté pour l'association, ce score reflète la proximité de la
        correspondance entre le nom fourni et les noms connus, avec des valeurs potentiellement inférieures à 100
        pour les correspondances moins précises.


        Exemple d'utilisation:
            >>> conteneur_test = ConteneurDeScene()
            >>> qui_2_roles(['Gardien', 'Voleur'], conteneur_test)
            [['Gardien', <objet Role Gardien>, 100], ['Voleur', <objet Role Voleur>, 100]]

        Note:
            - L'identification des rôles sans tableau de référence se fait par une recherche directe dans les rôles
              déjà contenus dans le 'conteneur'.
            - Avec un tableau de référence, la fonction génère des permutations d'alias pour chaque rôle et utilise
              une fonction de calcul de score pour déterminer la meilleure correspondance.
            - Les noms de rôles de moins de deux caractères sont ignorés durant le processus.
        """
    to_return = []  # nom, role,score
    # print("rôles trouvés en lecture brute : " + str(roles))

    if not avec_tableau_des_persos:
        # SI NomsRoles est None, ca veut dire qu'on travaille sans tableau de référence des rôles
        # > on les crée sans se poser de questions

        # print("Je suis entrée dans une situation ou il n'y avait pas de référence des noms")
        for nom_du_role in roles:
            # on cherche s'il existe déjà un rôle avec ce nom dans le conteneur
            # roleAAjouter = None
            nom_du_role = nom_du_role.strip()
            if nom_du_role in conteneur.rolesContenus:
                # print(f"nom trouvé dans le contenu : {nom_du_role}")
                to_return.append([nom_du_role, conteneur.rolesContenus[nom_du_role], 100])
            else:
                # print(f"nouveau role créé dans le contenu : {nom_du_role}")
                role_a_ajouter = Role(conteneur, nom=nom_du_role)
                to_return.append([nom_du_role, role_a_ajouter, 100])
                conteneur.rolesContenus[nom_du_role] = role_a_ajouter

        # et on s'arrête là
        return to_return

    # Sinon, on a un tableau des persos : la liste des noms possible est finie
    # dans ce cas, on prend les noms du tableau, qui font foi, et on s'en sert pour identifier
    # les noms de la scène
    dico_noms_avec_alias = conteneur.get_dico_roles_avec_alias()
    noms_roles_dans_conteneur = list(dico_noms_avec_alias.keys())

    # pour chaque rôle lu dans la liste des qui
    for nom_du_role in roles:
        if len(nom_du_role) < 2:
            continue

        noms_a_tester = generer_permutations_alias(nom_du_role.strip())
        scores = []
        # tester chacune de ses permutations avec des alias
        for nom in noms_a_tester:
            # Sinon, il faut normaliser et extraire les rôles. on commence par tester tous ses alias
            # pour chaque nom de la liste : retrouver le nom le plus proche dans la liste des noms du GN
            if score := process.extractOne(nom, noms_roles_dans_conteneur):
                scores.append(score)

        # A ce stade on a , pour chaque alias, un score

        if scores:
            # si on a au moins un résultat
            meilleur_score = max(scores, key=lambda x: x[1])
            mon_role = dico_noms_avec_alias[meilleur_score[0]]
            to_return.append([nom_du_role, mon_role, meilleur_score[1]])
        else:
            to_return.append([nom_du_role, None, 0])

    return to_return


def extraire_date_scene(balise_date, scene_a_ajouter):
    # réécrite pour merger les fonctions il y a et quand :

    # est-ce que la date est écrite au format quand ? il y a ?
    if balise_date.strip().lower()[:6] == 'il y a':
        # print(f" 'quand il y a' trouvée : {balise_date}")
        return extraire_il_y_a_scene(balise_date.strip()[7:], scene_a_ajouter)
    else:
        scene_a_ajouter.date = balise_date.strip()
    # print("date de la scène : " + scene_a_ajouter.date)


def extraire_il_y_a_scene(balise_date, scene_a_ajouter):
    # print("input_balise date : " + balise_date)
    # print(f" pour sandrine : nom_scene avec il y a  : {scene_a_ajouter.titre}")
    # trouver s'il y a un nombre a[ns]
    date_en_jours = calculer_jours_il_y_a(balise_date)
    # print(f"dans extraire il y a scene : {date_en_jours} avant de mettre à jour")

    scene_a_ajouter.date = date_en_jours
    # print(f"et après mise à jour de la scène : {scene_a_ajouter.date}")


def extraire_date_absolue(texte_brut: str, scene_a_ajouter: Scene):
    if texte_brut.endswith("h"):
        texte_brut += "00"
    scene_a_ajouter.date_absolue = dateparser.parse(texte_brut, languages=['fr'])


def calculer_jours_il_y_a(balise_date):
    # print(f"input_balise date il y a en entrée {balise_date}")
    balise_date = balise_date.lower()
    try:
        ma_date = balise_date
        # print(f"ma date avant stripping : {ma_date}")
        # print(balise_date.strip().lower()[0:6])
        # #si il y a un "il y a" dans la input_balise, il faut le virer
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

        ans = 0 if not ans else ans.group(0)[:-1]  # enlever le dernier char car c'est le marqueur de temps
        mois = 0 if not mois else mois.group(0)[:-1]
        semaines = 0 if not semaines else semaines.group(0)[:-1]
        jours = 0 if not jours else jours.group(0)[:-1]

        # if mois is None:
        #     mois = 0
        # else:
        #     mois = mois.group(0)[:-1]
        #
        # if semaines is None:
        #     semaines = 0
        # else:
        #     semaines = semaines.group(0)[:-1]
        # if jours is None:
        #     jours = 0
        # else:
        #     jours = jours.group(0)[:-1]

        # print(f"{ma_date} > ans/jours/mois = {ans}/{mois}/{jours}")

        date_en_jours = -1 * (float(ans) * 365 + float(mois) * 30.5 + float(semaines) * 7 + float(jours))
        # print(f"input_balise date il y a en sortie {date_en_jours}")

        return date_en_jours
    except ValueError:
        print(f"Erreur avec la date {balise_date}")
        return balise_date.strip()


def extraire_evenement_de_texte(texte_evenement: str, nom_evenement: str, id_url: str, lastFileEdit,
                                derniere_modification_par: str, dict_evenements, verbal=False):
    # print("je suis entré dans  la création d'un évènement")
    # Créer un nouvel évènement
    nom_evenement_en_cours = re.sub(r"^\d+\s*-", '', nom_evenement).strip()

    current_evenement = FicheEvenement(nom_evenement=nom_evenement_en_cours,
                                       id_url=id_url,
                                       derniere_edition_date=lastFileEdit,
                                       derniere_edition_par=derniere_modification_par)
    dict_evenements[id_url] = current_evenement

    #     print(f"evenements apres création de l'évènement {nom_evenement_en_cours} : {gn.evenements} ")

    class Labels(Enum):
        FICHE = "fiche technique"
        SYNOPSIS = "synopsis"
        LIES = "événements liés"
        BRIEFS = "brief pnjs"
        INFOS_PJS = "pj impliqués et informations à fournir"
        INFOS_FACTIONS = "factions impliquées et informations à fournir"
        OBJETS = "objets utilisés"
        CHRONO = "chronologie de "
        AUTRES = "informations supplémentaires"

    labels = [e.value for e in Labels]
    # indexes = lecteurGoogle.identifier_sections_fiche(labels, texte_evenement.lower())
    dict_sections, erreurs = lecteurGoogle.text_2_dict_sections(labels, texte_evenement)
    current_evenement.add_list_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                            erreurs,
                                            ErreurManager.ORIGINES.STRUCTURE_FICHIER_INTRIGUE)

    dict_methodes = {
        Labels.FICHE: lambda x: evenement_lire_fiche(x, current_evenement, Labels.FICHE.value),
        Labels.SYNOPSIS: lambda x: evenement_lire_synopsis(x, current_evenement),
        Labels.LIES: lambda x: evenement_lire_lies(x, Labels.LIES.value),
        Labels.BRIEFS: lambda x: evenement_lire_briefs(x, current_evenement, Labels.BRIEFS.value),
        Labels.INFOS_PJS: lambda x: evenement_lire_infos_pj(x, current_evenement, Labels.INFOS_PJS.value),
        Labels.INFOS_FACTIONS: lambda x: evenement_infos_factions(x, current_evenement, Labels.INFOS_FACTIONS.value),
        Labels.OBJETS: lambda x: evenement_lire_objets(x, current_evenement, Labels.OBJETS.value),
        Labels.CHRONO: lambda x: evenement_lire_chrono(x, current_evenement),
        Labels.AUTRES: lambda x: evenement_lire_autres(x, Labels.AUTRES.value),
    }

    # lire les sections dans le fichier et appliquer la bonne méthode
    for label in Labels:
        if paire := dict_sections.get(label.value):
            ma_methode = dict_methodes[label]
            ma_methode(paire['brut'])
        else:
            print(f"pas de {label.value} avec l'évènement {nom_evenement_en_cours}")
            texte_erreur = f"Le label {label.value} n'a pas été trouvé"
            current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                            texte_erreur,
                                                            ErreurManager.ORIGINES.LECTURE_EVENEMENT)

    # for label in Labels:
    #     if indexes[label.value]["debut"] == -1:
    #         if label != Labels.CHRONO:
    #             print(f"pas de {label.value} avec l'évènement {nom_evenement_en_cours}")
    #             texte_erreur = f"Le label {label.value} n'a pas été trouvé"
    #             current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
    #                                                             texte_erreur,
    #                                                             ErreurManager.ORIGINES.LECTURE_EVENEMENT)
    #
    #     else:
    #         texte_section = texte_evenement[indexes[label.value]["debut"]:indexes[label.value]["fin"]]
    #         methode_a_appliquer = dict_methodes[label]
    #         # methode_a_appliquer(texte_section, current_evenement, label.value)
    #         methode_a_appliquer(texte_section)

    # on vérifie ensuite qu'on a bien une chrono, sinon on la force et elle sera remplie par défaut
    # if indexes[Labels.CHRONO.value]["debut"] == -1:

    # à la place on va vérifier l'état du tableau après être passé, s'il est vide, on le force
    if len(current_evenement.interventions) == 0:
        # dans ce cas on reconstruit un tableau de toute pièce en appelant lire_chono_tableau avec non comme argument

        # si on est entré avec les paramètres apr défaut, dans ce cas le tableau est à reconstruire en '',
        tableau_interventions = [[''], ['']]

        evenement_lire_chrono_depuis_tableau(current_conteneur_evenement=current_evenement,
                                             tableau_interventions=tableau_interventions,
                                             nb_colonnes=1)

        texte_erreur = "Le tableau des interventions n'a pas été trouvé " \
                       "> les informations de l'évènement (jour, date, tous les pjs, tous les pnjs, synopsys) " \
                       "ont été reprises"
        current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.INFO,
                                                        texte_erreur,
                                                        ErreurManager.ORIGINES.LECTURE_EVENEMENT)


def evenement_lire_fiche(texte: str, current_evenement: FicheEvenement, texte_label: str):
    texte = retirer_premiere_ligne(texte)
    tableau_fiche, nb_colonnes = reconstituer_tableau(texte, sans_la_premiere_ligne=False)
    # print(f"DEBUG : tableau fiche évènement {current_evenement.nom_evenement}, {tableau_fiche} ")
    if nb_colonnes != 2:
        logging.debug(f"format incorrect de tableau pour {texte_label} : {tableau_fiche}")
        texte_erreur = f"format incorrect de tableau pour {texte_label}"
        current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                        texte_erreur,
                                                        ErreurManager.ORIGINES.LECTURE_EVENEMENT)
        return

    class NomsLignes(Enum):
        CODE = "Code de l'évènement"
        REFERENT = "Référent"
        ETAT = "Etat"
        INTRIGUE_LIEE = "Intrigue Liée"
        LIEU = "Lieu"
        JOUR = 'Jour, au format “J1”, “J2”, etc.'
        HEURE_DEBUT = "Heure de démarrage"
        HEURE_FIN = "Heure de fin"
        DECLENCHEUR = "Déclencheur"
        CONSEQUENCES = "Conséquences Évènement"

    noms_lignes = [e.value for e in NomsLignes]

    min_score = 100
    pire_match = ""

    # print(f"debug : tableau evènement avant harmonisation : {[ligne[0] for ligne in tableau_fiche]}")
    for ligne in tableau_fiche:
        score = process.extractOne(ligne[0], noms_lignes)
        ligne[0] = score[0]
        if score[1] < min_score:
            min_score = score[1]
            pire_match = score[0]

    tab_rectifie = [ligne[0] for ligne in tableau_fiche]
    if min_score < 85:
        texte_erreur = f"Attention, score bas de lecture des lignes du premier tableau de la fiche évènement. " \
                       f"Pire score : {min_score}% pour {pire_match}. " \
                       f"Tableau lu = {tab_rectifie}"
        current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                        texte_erreur,
                                                        ErreurManager.ORIGINES.LECTURE_EVENEMENT)

    if len(set(tab_rectifie)) != len(tab_rectifie):
        texte_erreur = f"une valeur a été trouvée en double dans les lignes du premier tableau de la fiche évènement." \
                       f"Tableau lu = {tab_rectifie}"
        current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                        texte_erreur,
                                                        ErreurManager.ORIGINES.LECTURE_EVENEMENT)

    # print(f"debug : tableau evènement après  harmonisation : {[ligne[0] for ligne in tableau_fiche]}")

    dict_fiche = dict(tableau_fiche)
    # print(f"DEBUG : dict_fiche évènement {dict_fiche}")

    current_evenement.code_evenement = dict_fiche.get(NomsLignes.CODE.value, "").strip()
    current_evenement.etat = dict_fiche.get(NomsLignes.ETAT.value, "").strip()
    current_evenement.referent = dict_fiche.get(NomsLignes.REFERENT.value, "").strip()
    current_evenement.intrigue_liee = dict_fiche.get(NomsLignes.INTRIGUE_LIEE.value, "").strip()
    current_evenement.lieu = dict_fiche.get(NomsLignes.LIEU.value, "").strip()
    current_evenement.date = dict_fiche.get(NomsLignes.JOUR.value, "").strip()
    current_evenement.heure_de_demarrage = dict_fiche.get(NomsLignes.HEURE_DEBUT.value, "").strip()
    # print(f"DEBUG : heure début évènement {dict_fiche.get(NomsLignes.HEURE_DEBUT.value, '').strip()} : "
    #       f"{type(dict_fiche.get(NomsLignes.HEURE_DEBUT.value, '').strip())}")

    current_evenement.heure_de_fin = dict_fiche.get(NomsLignes.HEURE_FIN.value, "").strip()
    current_evenement.declencheur = dict_fiche.get(NomsLignes.DECLENCHEUR.value, "").strip()
    current_evenement.consequences_evenement = dict_fiche.get(NomsLignes.CONSEQUENCES.value, "").strip()


def evenement_lire_synopsis(texte: str, current_evenement: FicheEvenement):
    current_evenement.synopsis = '\n'.join(texte.splitlines()[1:])


def evenement_lire_lies(texte: str, texte_label: str):
    logging.debug(f"balise {texte_label} non prise en charge = {texte}")


def evenement_lire_briefs(texte: str, current_evenement: FicheEvenement, texte_label: str):
    texte = retirer_premiere_ligne(texte)
    tableau_briefs, nb_colonnes = reconstituer_tableau(texte)
    if nb_colonnes != 4:
        logging.debug(f"format incorrect de tableau pour {texte_label} : {tableau_briefs}")
        texte_erreur = f"format incorrect de tableau pour {texte_label}"
        current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                        texte_erreur,
                                                        ErreurManager.ORIGINES.LECTURE_EVENEMENT)
        return

    for ligne in tableau_briefs:
        nom_intervenant = ligne[0]
        intervenant = IntervenantEvenement(nom_pnj=nom_intervenant,
                                           evenement=current_evenement,
                                           costumes_et_accessoires=ligne[1],
                                           implication=ligne[2],
                                           situation_de_depart=ligne[3]
                                           )

        current_evenement.intervenants_evenement[nom_intervenant] = intervenant


def evenement_lire_infos_pj(texte: str, current_evenement: FicheEvenement, texte_label: str):
    texte = retirer_premiere_ligne(texte)
    tableau_pjs, nb_colonnes = reconstituer_tableau(texte)
    if nb_colonnes != 2:
        logging.debug(f"format incorrect de tableau pour {texte_label} : {tableau_pjs}")
        texte_erreur = f"format incorrect de tableau pour {texte_label}"
        current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                        texte_erreur,
                                                        ErreurManager.ORIGINES.LECTURE_EVENEMENT)
        return
    for ligne in tableau_pjs:
        nom_pj = ligne[0]
        info_pj = PJConcerneEvenement(nom_pj=nom_pj,
                                      infos_a_fournir=ligne[1],
                                      evenement=current_evenement)
        current_evenement.pjs_concernes_evenement[nom_pj] = info_pj


def evenement_infos_factions(texte: str, current_evenement: FicheEvenement, texte_label: str):
    texte = retirer_premiere_ligne(texte)
    tableau_factions, nb_colonnes = reconstituer_tableau(texte)
    if nb_colonnes != 2:
        logging.debug(f"format incorrect de tableau pour {texte_label} : {tableau_factions}")
        texte_erreur = f"format incorrect de tableau pour {texte_label}"
        current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                        texte_erreur,
                                                        ErreurManager.ORIGINES.LECTURE_EVENEMENT)
        return
    for ligne in tableau_factions:
        info_faction = InfoFactionsPourEvenement(nom_faction=ligne[0], infos_a_fournir=ligne[1],
                                                 evenement=current_evenement)
        current_evenement.infos_factions.append(info_faction)


def evenement_lire_objets(texte: str, current_evenement: FicheEvenement, texte_label: str):
    texte = retirer_premiere_ligne(texte)
    tableau_objets, nb_colonnes = reconstituer_tableau(texte)
    if nb_colonnes != 4:
        logging.debug(f"format incorrect de tableau pour {texte_label} : {tableau_objets}")
        return

    for ligne in tableau_objets:
        objet = ObjetDansEvenement(code=ligne[0],
                                   description=ligne[1],
                                   commence=ligne[2],
                                   termine=ligne[3],
                                   evenement=current_evenement)
        current_evenement.objets.add(objet)


def evenement_lire_chrono(texte: str, current_evenement: ConteneurDEvenementsUnitaires, seuil_alerte_pnj=70,
                          seuil_alerte_pj=70):
    texte = retirer_premiere_ligne(texte)
    # # on regarde l'entete pour connaitre la taille du tableau,
    # # mais on prend le tableau sans entete pour terminer ce qu'il faut lire
    # _, nb_colonnes = reconstituer_tableau(texte, sans_la_premiere_ligne=False)
    # tableau_interventions, _ = reconstituer_tableau(texte)

    tableau_interventions, nb_colonnes = reconstituer_tableau(texte, sans_la_premiere_ligne=False)

    # print(f"debug : nous sommes dans l'évènement {current_evenement.code_evenement}, "
    #       f"len(tableau) = {len(tableau_interventions)}"
    #       f"tableau interventions : {tableau_interventions}")
    return evenement_lire_chrono_depuis_tableau(tableau_interventions=tableau_interventions,
                                                nb_colonnes=nb_colonnes,
                                                current_conteneur_evenement=current_evenement,
                                                seuil_alerte_pnj=seuil_alerte_pnj,
                                                seuil_alerte_pj=seuil_alerte_pj)


def evenement_lire_chrono_depuis_tableau(current_conteneur_evenement: ConteneurDEvenementsUnitaires,
                                         tableau_interventions: list, nb_colonnes: int,
                                         seuil_alerte_pnj=70, seuil_alerte_pj=70):
    class NomsColonnes(Enum):
        JOUR = "jour"
        LIEU = 'lieu'
        HEURE_DEBUT = "heure début"
        HEURE_FIN = "heure fin"
        PNJs = "pnjs"
        PJs = "pjs impliqués"
        QUOI = "quoi?"
        OU = "où?"

    colonnes = [nc.value for nc in NomsColonnes]

    #### déplacé dans l'appel unitaire dans les cas où on n'a pas de tableau
    # # si on est entré avec les paramètres apr défaut, dans ce cas le tableau est à reconstruire en '',
    # # pour recopier plus tard ceux de l'évènement
    # if tableau_interventions is None or nb_colonnes == 0:
    #     nb_colonnes = len(colonnes)
    #     tableau_interventions = [colonnes, [''] * nb_colonnes]
    #

    if not 1 <= nb_colonnes <= len(colonnes):
        logging.debug(f"format incorrect de tableau le la chronologie des évènements : {tableau_interventions}")
        texte_erreur = "format incorrect de tableau pour Chronologie de l'évènement"
        current_conteneur_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                                  texte_erreur,
                                                                  ErreurManager.ORIGINES.LECTURE_EVENEMENT)
        return

    # # du coup si le nombre de colonnes est bon mais que la longueur est nulle, le tableau est vide
    # # il faut donc le remplir
    if len(tableau_interventions) == 1:
        texte_erreur = "Le tableau des interventions a été trouvé, mais ne contenait aucune ligne "
        current_conteneur_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.INFO,
                                                                  texte_erreur,
                                                                  ErreurManager.ORIGINES.LECTURE_EVENEMENT)
        return

    # if len(tableau_interventions) == 1:
    #     tableau_interventions.append([''] * nb_colonnes)
    #     texte_erreur = "Le tableau des interventions a été trouvé, mais ne contenait aucune ligne " \
    #                    "> les informations de l'évènement (jour, date, tous les pjs, tous les pnjs, synopsys) " \
    #                    "ont été reprises"
    #     current_conteneur_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.INFO,
    #                                                               texte_erreur,
    #                                                               ErreurManager.ORIGINES.LECTURE_EVENEMENT)
    #     # print(f"debug : {tableau_interventions} pour l'evènement {current_evenement.nom_evenement}")

    # dict_header_vers_no_colonne = generer_dict_header_vers_no_colonne(en_tetes=tableau_interventions[0],
    #                                                                   noms_colonnes=colonnes,
    #                                                                   erreur_manager=current_conteneur_evenement.erreur_manager,
    #                                                                   )

    liste_dict_lignes = generer_liste_de_dict_from_tableau(tableau_interventions, colonnes,
                                                           current_conteneur_evenement.erreur_manager, verbal=False)

    for dict_ligne in liste_dict_lignes:
        evenement_extraire_ligne_chrono(current_conteneur_evenement, dict_ligne, NomsColonnes,
                                        seuil_alerte_pj, seuil_alerte_pnj)


def evenement_extraire_ligne_chrono(current_conteneur_evenement: ConteneurDEvenementsUnitaires,
                                    dict_ligne: dict,
                                    noms_colonnes,
                                    seuil_alerte_pj: int, seuil_alerte_pnj: int):
    # print(f"debug : "
    #       f"Je suis en train de lire une internvention de de l'évènement {current_evenement.code_evenement}, "
    #       f"et ma ligne est  = {ligne}")
    jour = dict_ligne.get(noms_colonnes.JOUR.value, '')
    heure_debut = dict_ligne.get(noms_colonnes.HEURE_DEBUT.value, '')
    heure_fin = dict_ligne.get(noms_colonnes.HEURE_FIN.value, '')
    pnjs_raw = dict_ligne.get(noms_colonnes.PNJs.value, '')
    pj_raw = dict_ligne.get(noms_colonnes.PJs.value, '')
    description = dict_ligne.get(noms_colonnes.QUOI.value, '')
    lieu = dict_ligne.get(noms_colonnes.OU.value) or dict_ligne.get(noms_colonnes.LIEU.value) or ''

    # print(f"debug : "
    #       f"après correction, j'ai les données suivantes : "
    #       f"jour={jour if jour != '' else current_evenement.date},"
    #       f"heure_debut={heure_debut if heure_debut != '' else current_evenement.heure_de_demarrage},"
    #       f"heure_fin={heure_fin if heure_fin != '' else current_evenement.heure_de_fin}, "
    #       f"description={description if description != '' else current_evenement.synopsis},"
    #       )

    # ce code est commenté car il créeait des évnèement dont la fin 'nétait pas spécifiés
    # et qui pouvaient durer des heures sans que les rédacteurs ne s'en rendent compte
    # intervention = EvenementUnitaire(jour=jour if jour != '' else current_conteneur_evenement.date_par_defaut(),
    #                                  heure_debut=heure_debut if heure_debut != ''
    #                                  else current_conteneur_evenement.heure_de_demarrage_par_defaut(),
    #                                  heure_fin=heure_fin if heure_fin != ''
    #                                  else current_conteneur_evenement.heure_de_fin_par_defaut(),
    #                                  description=description if description != ''
    #                                  else current_conteneur_evenement.synopsis_par_defaut(),
    #                                  conteneur_dinterventions=current_conteneur_evenement,
    #                                  lieu=lieu if lieu != ''
    #                                  else current_conteneur_evenement.lieu_par_defaut()
    #                                  )

    def ajouter_une_minute(time_str: str):
        # print(f"DEBUG : heure à incrémenter : {time_str} et heure debut evenemtn = {current_conteneur_evenement.heure_de_demarrage_par_defaut()}")

        if not time_str:
            time_str = current_conteneur_evenement.heure_de_demarrage_par_defaut()

        # print(f"DEBUG : heure à incrémenter : {time_str}")

        # Splitting the string by 'h' and taking only the first two elements
        parts = time_str.split('h')[:2]

        # Extracting the hour and minute (if minute is not given, default to 0)
        try:
            hour = int(parts[0])
        except ValueError:
            hour = 0

        try:
            minute = int(parts[1]) if len(parts) > 1 else 0
        except ValueError:
            minute = 0

        # Adding one minute
        minute += 1
        if minute == 60:
            minute = 0
            hour += 1
            if hour == 24:
                hour = 0

        # Formatting the new time
        return f"{hour:02d}h{minute:02d}"

    intervention = EvenementUnitaire(jour=jour if jour != '' else current_conteneur_evenement.date_par_defaut(),
                                     heure_debut=heure_debut if heure_debut != ''
                                     else current_conteneur_evenement.heure_de_demarrage_par_defaut(),
                                     heure_fin=heure_fin if heure_fin != ''
                                     else ajouter_une_minute(heure_debut),
                                     description=description if description != ''
                                     else current_conteneur_evenement.synopsis_par_defaut(),
                                     conteneur_dinterventions=current_conteneur_evenement,
                                     lieu=lieu if lieu != ''
                                     else current_conteneur_evenement.lieu_par_defaut()
                                     )

    # intervention = Intervention(jour=ligne[0] if ligne[0] != '' else current_evenement.date,
    #                             heure=ligne[1] if ligne[1] != '' else current_evenement.heure_de_demarrage,
    #                             description=ligne[4] if ligne[4] != '' else current_evenement.synopsis,
    #                             evenement=current_evenement
    #                             )
    noms_pnjs_impliques = [nom.strip() for nom in pnjs_raw.split(',')]
    noms_pnjs_dans_evenement = current_conteneur_evenement.get_noms_pnjs()
    # print(f"debug : {len(current_evenement.interventions)} interventions "
    #       f"dans l'evènement {current_evenement.id_url}")

    current_conteneur_evenement.interventions.append(intervention)
    # print(f"debug : apres ajout de l'intervention {intervention.description} dans l'évènement "
    #       f"{current_evenement.nom_evenement} / {current_evenement.code_evenement}, "
    #       f"celui ci contient {len(current_evenement.interventions)} interventions")
    if noms_pnjs_impliques == ['']:
        a_ajouter = current_conteneur_evenement.get_intervenants_si_vide()
        intervention.liste_intervenants.extend(a_ajouter)
        # intervention.liste_intervenants.extend(current_conteneur_evenement.intervenants_evenement.values())

    else:
        for nom_pnj in noms_pnjs_impliques:
            score = process.extractOne(nom_pnj, noms_pnjs_dans_evenement)
            if score is None:
                texte_erreur = f"Correspondance introuvable pour le nom {nom_pnj} avec la table des PNJs" \
                               f"dans l'évènement {current_conteneur_evenement.code_evenement} " \
                               f"/ {current_conteneur_evenement.nom_evenement} " \
                               f"pour l'intervention {intervention.description}"
                current_conteneur_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                                          texte_erreur,
                                                                          ErreurManager.ORIGINES.CHRONO_EVENEMENT)
                # print(f"debug : {texte_erreur}")
                continue

            if score[1] < seuil_alerte_pnj:
                texte_erreur = f"Le nom du pnj {nom_pnj} trouvé dans la chronologie de l'évènement " \
                               f"a été associé à {score[0]} à seulement {score[1]}% de confiance"
                current_conteneur_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                                          texte_erreur,
                                                                          ErreurManager.ORIGINES.CHRONO_EVENEMENT)
            # intervenant = current_conteneur_evenement.intervenants_evenement[score[0]]
            intervenant = current_conteneur_evenement.get_intervenant_from_nom(score[0])

            intervention.liste_intervenants.append(intervenant)
    for intervenant in intervention.liste_intervenants:
        intervenant.interventions.add(intervention)

    noms_pj_impliques = [nom.strip() for nom in pj_raw.split(',')]
    noms_pjs_dans_evenement = current_conteneur_evenement.get_noms_pjs()
    if noms_pj_impliques == ['']:
        # intervention.liste_pjs_concernes.extend(current_conteneur_evenement.pjs_concernes_evenement.values())
        a_ajouter = current_conteneur_evenement.get_pjs_concernes_si_vide()
        intervention.liste_pjs_concernes.extend(a_ajouter)

    else:
        for nom_pj in noms_pj_impliques:
            score = process.extractOne(nom_pj, noms_pjs_dans_evenement)
            if score is None:
                texte_erreur = f"Correspondance introuvable pour le nom {nom_pj} " \
                               f"dans l'évènement {current_conteneur_evenement.code_evenement} avec la table des PJs" \
                               f"/ {current_conteneur_evenement.nom_evenement}" \
                               f"pour l'intervention {intervention.description}"
                current_conteneur_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                                          texte_erreur,
                                                                          ErreurManager.ORIGINES.CHRONO_EVENEMENT)
                # print(f"debug : {texte_erreur}")
                continue

            if score[1] < seuil_alerte_pj:
                texte_erreur = f"Le nom du pj {nom_pj} trouvé dans la chronologie de l'évènement " \
                               f"a été associé à {score[0]} à seulement {score[1]}% de confiance"
                current_conteneur_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                                          texte_erreur,
                                                                          ErreurManager.ORIGINES.CHRONO_EVENEMENT)
            # pj_concerne = current_conteneur_evenement.pjs_concernes_evenement[score[0]]
            pj_concerne = current_conteneur_evenement.get_pjs_concernes_from_nom(score[0])
            intervention.liste_pjs_concernes.append(pj_concerne)


def evenement_lire_autres(texte: str, texte_label: str):
    logging.debug(f"balise {texte_label} non prise en charge = {texte}")


def retirer_premiere_ligne(texte: str):
    return '\n'.join(texte.splitlines()[1:])


def retirer_label(texte: str, label: str):
    return texte[len(label):].strip()


def extraire_pnj_de_texte(texte_avec_format, nom_doc, id_url, last_file_edit,
                          derniere_modification_par, dict_pnj,
                          verbal):
    return extraire_persos_de_texte(texte_avec_format, nom_doc, id_url, last_file_edit,
                                    derniere_modification_par, dict_pnj,
                                    verbal=verbal, pj=TypePerso.EST_PNJ_HORS_JEU)


def extraire_persos_de_texte(texte_avec_format, nom_doc, id_url, last_file_edit,
                             derniere_modification_par, dict_pj_pnj,
                             verbal=False, pj: TypePerso = TypePerso.EST_PJ):
    print(f"Lecture de {nom_doc}")
    if len(texte_avec_format) < 800:
        print(f"fiche {nom_doc} avec {len(texte_avec_format)} caractères est vide")
        # return  # dans ce cas c'est qu'on est en train de lite un template, qui fait 792 cars

    nom_perso_en_cours = re.sub(r"^[a-zA-Z]?\d+\s*-", '', nom_doc).strip()
    # print(f"nomDoc =_{nomDoc}_ nomPJ =_{nomPJ}_")
    # print(f"Personnage en cours d'importation : {nomPJ} avec {len(textePJ)} caractères")
    current_personnage = Personnage(nom=nom_perso_en_cours, url=id_url, derniere_edition_fichier=last_file_edit, pj=pj)
    current_personnage.modifie_par = derniere_modification_par
    dict_pj_pnj[id_url] = current_personnage

    # texte_persos_low = texte_persos_pur.lower()  # on passe en minuscule pour mieux trouver les chaines

    class Labels(Enum):
        REFERENT = "orga référent :"
        JOUEUR = "joueur"
        JOUEUSE = "joueuse"
        INTERPRETE = "interprète"
        PITCH = "pitch personnage"
        COSTUME = "indications costumes :"
        FACTION1 = "faction principale :"
        FACTION2 = "faction secondaire :"
        GROUPES = "groupes :"
        BIO = "bio résumée"
        PSYCHO = "psychologie :"
        MOTIVATIONS = "motivations et objectifs"
        CHRONOLOGIE = "chronologie"
        INTRIGUES = "intrigues"
        RELATIONS = "relations avec les autres persos"
        SCENES = "scènes"
        RELATIONS_BI = "relations bilatérales"
        RELATIONS_MULTI = "relations multilatérales"

    labels = [label.value for label in Labels]

    # indexes = lecteurGoogle.identifier_sections_fiche(labels, texte_persos_low)
    dict_sections, erreurs = lecteurGoogle.text_2_dict_sections(labels, texte_avec_format)
    current_personnage.add_list_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                             erreurs,
                                             ErreurManager.ORIGINES.STRUCTURE_FICHIER_PERSONNAGE)

    dict_methodes = {
        Labels.REFERENT: lambda x, y: personnage_referent(x, current_personnage, Labels.REFERENT.value),
        Labels.JOUEUR: lambda x, y: personnage_interprete(x, current_personnage, Labels.JOUEUR.value),
        Labels.JOUEUSE: lambda x, y: personnage_interprete(x, current_personnage, Labels.JOUEUSE.value),
        Labels.INTERPRETE: lambda x, y: personnage_interprete(x, current_personnage, Labels.INTERPRETE.value),
        Labels.PITCH: lambda x, y: personnage_pitch(x, current_personnage),
        Labels.COSTUME: lambda x, y: personnage_costume(x, current_personnage, Labels.COSTUME.value),
        Labels.FACTION1: lambda x, y: personnage_faction1(x, current_personnage, Labels.FACTION1.value),
        Labels.FACTION2: lambda x, y: personnage_factions2(x, current_personnage, Labels.FACTION2.value),
        Labels.GROUPES: lambda x, y: personnage_groupes(x, current_personnage, Labels.GROUPES.value),
        Labels.INTRIGUES: lambda x, y: personnage_intrigues(Labels.INTRIGUES.value),
        Labels.BIO: lambda x, y: personnage_bio(x, current_personnage),
        Labels.PSYCHO: lambda x, y: personnage_psycho(x, current_personnage),
        Labels.MOTIVATIONS: lambda x, y: personnage_motivation(x, current_personnage),
        Labels.CHRONOLOGIE: lambda x, y: personnage_chronologie(x, current_personnage),
        Labels.SCENES: lambda x, y: personnage_scenes(x, y, current_personnage),
        Labels.RELATIONS: lambda x, y: personnage_relations(Labels.RELATIONS.value),
        Labels.RELATIONS_BI: lambda x, y: personnage_relations_bi(x, current_personnage),
        Labels.RELATIONS_MULTI: lambda x, y: personnage_relations_multi(x, current_personnage)
    }

    for label in Labels:
        if paire := dict_sections.get(label.value):
            ma_methode = dict_methodes[label]
            ma_methode(paire['brut'], paire['formatté'])
        else:
            print(f"pas de {label.value} avec le personnage {nom_perso_en_cours}")

    # for label in Labels:
    #     if indexes[label.value]["debut"] == -1:
    #         print(f"pas de {label.value} avec le personnage {nom_perso_en_cours}")
    #     else:
    #         ma_methode = dict_methodes[label]
    #         texte_section_pur = texte_persos_pur[indexes[label.value]["debut"]:indexes[label.value]["fin"]]
    #         texte_section_avec_format = texte_avec_format[indexes[label.value]["debut"]:indexes[label.value]["fin"]]
    #
    #         # print(f"debug : texte label {label.value} = {texte}")
    #         # ma_methode(texte, current_personnage, label.value)
    #         ma_methode(texte_section_pur)

    # et on enregistre la date de dernière mise à jour de l'intrigue
    # perso_en_cours.lastProcessing = datetime.datetime.now()
    return current_personnage


def personnage_referent(texte: str, perso_en_cours: Personnage, text_label: str):
    perso_en_cours.orga_referent = retirer_label(texte, text_label)


# def personnage_joueurv1(texte: str, perso_en_cours: Personnage, text_label: str):
#     perso_en_cours.joueurs['V1'] = retirer_label(texte, text_label)
#

def personnage_relations(text_label: str):
    print(f"Balise {text_label} trouvée : cette balise n'est plus prise en compte")


def personnage_intrigues(text_label: str):
    print(f"Balise {text_label} trouvée : cette balise n'a pas d'effet dans MAGnet")


def personnage_interprete(texte: str, perso_en_cours: Personnage, text_label: str):
    pattern = f"{text_label}(.+):(.+)"
    if match := re.match(pattern, texte):
        session_id, interprete_session = match.group(1).strip(), match.group(2).strip()
        perso_en_cours.interpretes[session_id] = interprete_session


# def personnage_joueurv2(texte: str, perso_en_cours: Personnage, text_label: str):
#     perso_en_cours.joueurs['V2'] = retirer_label(texte, text_label)
#
#
# def personnage_joueusev1(texte: str, perso_en_cours: Personnage, text_label: str):
#     perso_en_cours.joueurs['V1'] = retirer_label(texte, text_label)
#
#
# def personnage_joueusev2(texte: str, perso_en_cours: Personnage, text_label: str):
#     perso_en_cours.joueurs['V2'] = retirer_label(texte, text_label)


def personnage_pitch(texte: str, perso_en_cours: Personnage):
    perso_en_cours.pitch = retirer_premiere_ligne(texte)


def personnage_costume(texte: str, perso_en_cours: Personnage, text_label: str):
    perso_en_cours.indicationsCostume = retirer_label(texte, text_label)


def personnage_faction1(texte: str, perso_en_cours: Personnage, text_label: str):
    perso_en_cours.groupes.append(retirer_label(texte, text_label).splitlines()[0])


def personnage_factions2(texte: str, perso_en_cours: Personnage, text_label: str):
    perso_en_cours.groupes.append(retirer_label(texte, text_label).splitlines()[0])


def personnage_groupes(texte: str, perso_en_cours: Personnage, text_label: str):
    texte = retirer_label(texte, text_label)
    perso_en_cours.groupes.extend([nom_groupe.strip() for nom_groupe in texte.split(',')])


def personnage_bio(texte: str, perso_en_cours: Personnage):
    perso_en_cours.description = retirer_premiere_ligne(texte)


def personnage_psycho(texte: str, perso_en_cours: Personnage):
    perso_en_cours.concept = retirer_premiere_ligne(texte)


def personnage_motivation(texte: str, perso_en_cours: Personnage):
    perso_en_cours.driver = retirer_premiere_ligne(texte)


def personnage_chronologie(texte: str, perso_en_cours: Personnage):
    perso_en_cours.datesClefs = retirer_premiere_ligne(texte)


def personnage_relations_bi(texte: str, perso_en_cours: Personnage):
    tableau_relation_bi_brut, _ = reconstituer_tableau(texte)
    print(f"tab brut : {tableau_relation_bi_brut}")
    # comme on est dans une fiche perso, il est implicite que le perso fait partie de la relation : on l'ajoute donc
    tableau_relation_bi_complet = [[perso_en_cours.nom] + ligne for ligne in tableau_relation_bi_brut]
    extraire_relations_bi(perso_en_cours, tableau_relation_bi_complet, avec_tableau_persos=False)


def personnage_relations_multi(texte: str, perso_en_cours: Personnage):
    tableau_relation_multi_brut, _ = reconstituer_tableau(texte)

    # comme on est dans une fiche perso, il est implicite que le perso fait partie de la relation : on l'ajoute donc
    tableau_relation_multi_complet = []
    for ligne in tableau_relation_multi_brut:
        nouvelle_ligne = [f"{perso_en_cours.nom}, {ligne[0]}", ligne[1]]
        tableau_relation_multi_complet.append(nouvelle_ligne)
    extraire_relation_multi(perso_en_cours, tableau_relation_multi_complet, avec_tableau_des_persos=False)


def personnage_scenes(texte_pur: str, texte_avec_format, perso_en_cours: Personnage):
    texte2scenes(perso_en_cours, perso_en_cours.nom, texte_pur, texte_avec_format, tableau_roles_existant=False)


def extraire_objets_de_texte(texte_objets, nom_doc, id_url, last_file_edit, derniere_modification_par,
                             dict_objets_de_reference,
                             verbal=False):
    print(f"Lecture de {nom_doc}")

    nom_objet_en_cours = re.sub(r"^\d+\s*-", '', nom_doc).strip()

    # extraction du code objet qui peut être au format X123-4 - Nom ou X456 - Nom
    pattern = r'^[A-Za-z]?\d+\s*-(\s*\d+\s*-)?'
    if match := re.search(pattern, nom_doc):
        # on prend tout le prefixe, sauf le "-" qui est à la fin, et on strip
        code_objet = match[0][:-1].strip()
    else:
        print(f"debug : pas de match de code objet pour l'objet {nom_doc}")
        code_objet = ""

    # print(f"nomDoc =_{nomDoc}_ nomPJ =_{nomPJ}_")
    # print(f"Personnage en cours d'importation : {nomPJ} avec {len(textePJ)} caractères")
    current_objet = ObjetDeReference(nom_objet=nom_objet_en_cours,
                                     code_objet=code_objet,
                                     id_url=id_url,
                                     derniere_edition_date=last_file_edit,
                                     derniere_edition_par=derniere_modification_par)
    dict_objets_de_reference[id_url] = current_objet

    texte_objets_low = texte_objets.lower()  # on passe en minuscule pour mieux trouver les chaines

    class Labels(Enum):
        REFERENT = "orga référent : "
        INTRIGUE = "intrigue : "
        INTRIGUES = "intrigues : "
        UTILITE = "utilité en jeu : "
        BUDGET = "budget : "
        RECOMMANDATION = "recommandations : "
        MATERIAUX = "suggestion de matériaux, et techniques :"
        MOODBOARD = "moodboard : "
        DESCRIPTION = "description : "
        FX = "effets spéciaux : "

    labels = [label.value for label in Labels]

    # indexes = lecteurGoogle.identifier_sections_fiche(labels, texte_objets_low)
    dict_sections, _ = lecteurGoogle.text_2_dict_sections(labels, texte_objets)

    dict_methodes = {
        Labels.REFERENT: lambda x: objets_referent(x, current_objet, Labels.REFERENT.value),
        Labels.INTRIGUE: lambda x: objets_noms_intrigues(Labels.INTRIGUE.value),
        Labels.INTRIGUES: lambda x: objets_noms_intrigues(Labels.INTRIGUES.value),
        Labels.UTILITE: lambda x: objets_utilite(x, current_objet, Labels.UTILITE.value),
        Labels.BUDGET: lambda x: objets_budget(x, current_objet, Labels.BUDGET.value),
        Labels.RECOMMANDATION: lambda x: objets_recommandation(x, current_objet, Labels.RECOMMANDATION.value),
        Labels.MATERIAUX: lambda x: objets_materiaux(x, current_objet, Labels.MATERIAUX.value),
        Labels.MOODBOARD: lambda x: objets_moodboard(Labels.MOODBOARD.value),
        Labels.DESCRIPTION: lambda x: objets_description(x, current_objet),
        Labels.FX: lambda x: objets_effets_speciaux(x, current_objet, Labels.FX.value)
    }

    for label in Labels:
        if paire := dict_sections.get(label.value):
            ma_methode = dict_methodes[label]
            ma_methode(paire['brut'])
        else:
            print(f"pas de {label.value} avec l'objet {nom_objet_en_cours}")

    # for label in Labels:
    #     if indexes[label.value]["debut"] == -1:
    #         print(f"pas de {label.value} avec l'objet {nom_objet_en_cours}")
    #     else:
    #         ma_methode = dict_methodes[label]
    #         texte = texte_objets[indexes[label.value]["debut"]:indexes[label.value]["fin"]]
    #         # print(f"debug : texte label {label.value} = {texte}")
    #         # ma_methode(texte, current_objet, label.value)
    #         ma_methode(texte)

    # et on enregistre la date de dernière mise à jour de l'intrigue
    current_objet.set_last_processing(datetime.datetime.now())
    return current_objet


def objets_effets_speciaux(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.effets_speciaux = retirer_label(texte, texte_label)


def objets_referent(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.referent = retirer_label(texte, texte_label)


def objets_noms_intrigues(texte_label: str):
    print(f"la balise {texte_label} n'a pas d'utilité pour MAGnet")


def objets_utilite(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.utilite = retirer_label(texte, texte_label)


def objets_budget(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.budget = retirer_label(texte, texte_label)


def objets_recommandation(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.recommandations = retirer_label(texte, texte_label)


def objets_materiaux(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.materiaux = retirer_label(texte, texte_label)


def objets_moodboard(texte_label: str):
    print(f"la balise {texte_label} n'a pas d'utilité pour MAGnet")


def objets_description(texte: str, objet_en_cours: ObjetDeReference):
    objet_en_cours.description = retirer_premiere_ligne(texte)


def ref_du_doc(s: str, prefixes=""):
    s = s.lower()
    prefixes = prefixes.lower()

    if any(s.startswith(letter) for letter in prefixes):
        s = s[1:]
    elif not s[0].isdigit():
        return -1

    return int(match.group(1)) if (match := re.match(r'^(\d+)\s*-.*$', s)) else -1


def extraire_factions(mon_gn: GN, api_doc, verbal=True):
    if mon_gn.get_id_factions() is None:
        logging.info('id faction était None')
        return -1

    # on commence par effacer les factions existantes pour éviter les doublons

    mon_gn.clear_all_factions()

    try:
        id_doc = mon_gn.get_id_factions()
        text, _ = lire_google_doc(api_doc, id_doc)

    except HttpError as err:
        print(f'An error occurred: {err}')
        return

    if verbal:
        print(f"texte = {text}")
    # à ce stade, j'ai lu les factions et je peux dépouiller
    # print(f"clefs dictionnaire : {mon_GN.dictPJs.keys()}")
    lines = text.splitlines()
    noms_persos = mon_gn.noms_personnages()
    # on crée un dictionnaire qui permettra de retrouver les id en fonction des noms
    dict_nom_id = {mon_gn.personnages[x].nom: x for x in mon_gn.personnages}

    current_faction = None
    for line in lines:
        if line.startswith("###"):
            faction_name = line.replace("###", "")
            faction_name = faction_name.strip()
            current_faction = Faction(faction_name)
            mon_gn.factions[faction_name] = current_faction
            logging.info(f"J'ai ajouté la faction {faction_name}")
        elif line.startswith("##"):
            line = line.replace("##", "")
            personnages_names = line.strip().split(",")
            for perso_name in personnages_names:
                perso_name = perso_name.strip()
                if len(perso_name) < 1:
                    continue
                score = fuzzywuzzy.process.extractOne(perso_name, noms_persos)
                # print(f"score durant lecture faction pour {perso_name} = {score}")
                if verbal:
                    print(f"pour le nom {perso_name} lu dans la faction {current_faction.nom}, j'ai {score}")
                logging.info(f"pour le nom {perso_name} lu dans la faction {current_faction.nom}, j'ai {score}")

                personnages_a_ajouter = mon_gn.personnages[dict_nom_id.get(score[0])]
                current_faction.personnages.add(personnages_a_ajouter)
    return 0


def lire_google_doc(api_doc, id_doc, extraire_formattage=True, chars_images=False):
    document = api_doc.documents().get(documentId=id_doc).execute()
    contenu_document = document.get('body').get('content')
    titre = document.get('title')
    text = lecteurGoogle.read_structural_elements(contenu_document, extraire_formattage=extraire_formattage,
                                                  chars_images=chars_images)
    text = text.replace('\v', '\n')  # pour nettoyer les backspace verticaux qui se glissent
    return text, titre


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


def trouver_tuples_formattage(input_string, start_delim, end_delim):
    # Escape the delimiters to handle special regex characters
    start_delim_escaped = re.escape(start_delim)
    end_delim_escaped = re.escape(end_delim)

    # Create the regex pattern
    pattern = f'{start_delim_escaped}(.*?){end_delim_escaped}'

    # Find all matches
    matches = re.finditer(pattern, input_string, re.DOTALL)

    # Create a list of tuples with start and end indices
    result = []
    for match in matches:
        start = match.start()
        end = match.end()
        # length = end - start
        # result.append((start, end, length))
        result.append((start, end))

    return result


def write_to_doc(service, file_id, text: str, titre=False, verbal=False):
    # le code qui ajoute la détection et la construction d'une requete pour les urls à formatter
    formatting_requests = []

    # url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    # pattern évolué pour ne plus prendre en compte les parenthèses
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    # requêtes pour le formattage, d'abord les URLS, ensuite les autres balises
    # requête non ajoutées à la fin car tant que création de colonne vides, décalage de l'offset qui fera planter
    for match in re.finditer(url_pattern, text):
        url = match.group()
        start = match.start()
        end = match.end()

        formatting_requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': start + 1,
                    'endIndex': end + 1,
                },
                'textStyle': {
                    'link': {
                        'url': url
                    }
                },
                'fields': 'link'
            }
        })

    # pour toutes les autres options de fomrmattage :
    #   1. on trouve les tuples
    #   2. on met à jour la requête de formattage pour mettre en forme
    #   3. on met à jour la requete de nettoyage pour supprimer les bornes
    # puis (important !) on trie toutes les cleaning request en commençant par la fin
    # pour ne pas fouttre le bazar dans les indexes

    cleaning_requests = []
    for clef_formattage in lecteurGoogle.VALEURS_FORMATTAGE:
        balise_debut = lecteurGoogle.VALEURS_FORMATTAGE[clef_formattage][0]
        balise_fin = lecteurGoogle.VALEURS_FORMATTAGE[clef_formattage][1]
        # 1. on isole les positions
        liste_tuples_positions = trouver_tuples_formattage(text, balise_debut, balise_fin)

        # 2. on crée le formattage
        for start, end in liste_tuples_positions:
            if clef_formattage == 'backgroundColor':
                formatting_requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': start + 1,
                            'endIndex': end + 1,
                        },
                        'textStyle': {
                            # f"'{clef_formattage}'": True
                            "backgroundColor": {
                                "color": {
                                    "rgbColor": {
                                        "red": 1.0,
                                        "green": 0.95,
                                        "blue": 0.8
                                    }
                                }
                            }
                        },
                        # 'fields': f"'{clef_formattage}'"
                        'fields': f'{clef_formattage}'
                    }
                })
            else:
                formatting_requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': start + 1,
                            'endIndex': end + 1,
                        },
                        'textStyle': {
                            # f"'{clef_formattage}'": True
                            f'{clef_formattage}': True
                        },
                        # 'fields': f"'{clef_formattage}'"
                        'fields': f'{clef_formattage}'
                    }
                })

            # 3. on fait une requête qui nettoie
            cleaning_requests.append({
                'deleteContentRange': {
                    'range': {
                        'startIndex': start + 1,  # Starting index of the text to delete
                        'endIndex': start + 1 + len(balise_debut)  # Ending index of the text to delete
                    }
                }
            })
            cleaning_requests.append({
                'deleteContentRange': {
                    'range': {
                        'startIndex': end + 1 - len(balise_fin),  # Starting index of the text to delete
                        'endIndex': end + 1  # Ending index of the text to delete
                    }
                }
            })

        # une fois tout fini, on trie la cleaning request
        cleaning_requests.sort(key=lambda x: x['deleteContentRange']['range']['startIndex'], reverse=True)

    # a ce stade là, les endroits qui doivent être mis sous forme d'url sont identifiés
    # l'ancien code, fonctionnel
    try:
        requests = []
        start_index = 1

        while lecteurGoogle.DEBUT_TABLEAU in text:
            # Extraire le texte avant le tableau
            start_table = text.find(lecteurGoogle.DEBUT_TABLEAU)
            text_before_table = text[:start_table]

            # Ajouter la requête pour insérer le texte avant le tableau
            requests.append({
                'insertText': {
                    'location': {
                        'index': start_index
                    },
                    'text': text_before_table
                }
            })

            start_index += len(text_before_table)

            # Extraire le texte du tableau
            end_table = text.find(lecteurGoogle.FIN_TABLEAU, start_table) + len(lecteurGoogle.FIN_TABLEAU)
            table_text = text[start_table + len(lecteurGoogle.DEBUT_TABLEAU):end_table - len(lecteurGoogle.FIN_TABLEAU)]

            # Créer le tableau à partir du texte
            rows = table_text.split(lecteurGoogle.FIN_LIGNE)
            table = [row.split(lecteurGoogle.SEPARATEUR_COLONNES) for row in rows]

            num_rows = len(table)
            num_columns = max(len(row) for row in table)

            # print(f'DEBUG : table pour les intrigues : {table}')
            # print(f'DEBUG : {num_columns} x {num_rows}')

            # créer la structure du tableau
            requests.append({
                'insertTable': {
                    'location': {
                        'index': start_index
                    },
                    'rows': num_rows,
                    'columns': num_columns
                }
            })

            # focntions pour calculer l'offset du début d'une cellule dans le tableau ou la reprise
            # a utiliser en remplissant à l'envers, en commencant par la fin, pour ne pas pourrir les calcule
            def calculer_offset(no_ligne, no_colonne, nb_colonnes):
                return 4 + (no_colonne - 1) * 2 + (no_ligne - 1) * (nb_colonnes * 2 + 1)

            def calculer_offset_fin_tableau(nb_lignes, nb_colonnes):
                return calculer_offset(nb_lignes, nb_colonnes, nb_colonnes) + 2

            # # Remplir le tableau avec les valeurs dela table
            taille_texte_insere = 0
            # parcourir la table à l'envers
            for no_ligne in range(num_rows, 0, -1):
                for no_colonne in range(num_columns, 0, -1):
                    offset = calculer_offset(no_ligne, no_colonne, num_columns)
                    try:
                        # afficher le numéro de la colonne, le numéro de la ligne, et le contenu de la case
                        # print(f"Colonne {j}, Ligne {i} : {table[i][j]}")
                        # Insérer le texte dans la cellule
                        texte_a_inserer = table[no_ligne - 1][no_colonne - 1]
                        # print(f'DEBUG : {no_ligne - 1}{no_colonne - 1} texte à insérer : {texte_a_inserer}')
                        if len(texte_a_inserer):
                            requests.append({
                                'insertText': {
                                    'location': {
                                        'index': start_index + offset
                                    },
                                    'text': texte_a_inserer
                                }
                            })
                            taille_texte_insere += len(texte_a_inserer)
                    except IndexError as e:
                        print(f"Erreur dans l'écriture d'un tableau en "
                              f"{no_ligne}:{no_colonne} (offset : {offset} : {e}")

            # mettre à jour l'offset pour reprendre l'inserttion du texte
            start_index += calculer_offset_fin_tableau(num_rows, num_columns) + taille_texte_insere

            # Supprimer le texte du tableau du texte original
            text = text[end_table:]

        # Ajouter la requête pour insérer le reste du texte
        requests.append({
            'insertText': {
                'location': {
                    'index': start_index
                },
                'text': text
            }
        })

        # ajouter le formattage à la requete d'insert
        requests += formatting_requests

        requests += cleaning_requests

        # debug : code récupérer de slack, fontionnel, utilisé pour comprendre les offsets
        # requests = [
        #     {
        #         "insertTable":
        #             {
        #                 "rows": 2,
        #                 "columns": 2,
        #                 "location":
        #                     {
        #                         "index": 1
        #                     }
        #             }
        #     },
        #     {
        #         "insertText":
        #             {
        #                 "text": "B2",
        #                 "location":
        #                     {
        #                         "index": 12
        #                     }
        #             }
        #     },
        #     {
        #         "insertText":
        #             {
        #                 "text": "A2",
        #                 "location":
        #                     {
        #                         "index": 10
        #                     }
        #             }
        #     },
        #     {
        #         "insertText":
        #             {
        #                 "text": "B1",
        #                 "location":
        #                     {
        #                         "index": 7
        #                     }
        #             }
        #     },
        #     {
        #         "insertText":
        #             {
        #                 "text": "A1",
        #                 "location":
        #                     {
        #                         "index": 5
        #                     }
        #             }
        #     }
        # ]

        if verbal:
            print(f"VERBAL : Requete write_to_doc : {requests}")
        # Execute the request.
        result = service.documents().batchUpdate(documentId=file_id, body={'requests': requests}).execute()
        return result
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


# def write_to_doc_old(service, file_id, text: str, titre=False):
#     # le code qui ajoute la détection et la construction d'une requete pour les urls à formatter
#     formatting_requests = []
#
#     # url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
#     # pattern évolué pour ne plus prendre en compte les parenthèses
#     url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
#
#     for match in re.finditer(url_pattern, text):
#         url = match.group()
#         start = match.start()
#         end = match.end()
#
#         formatting_requests.append({
#             'updateTextStyle': {
#                 'range': {
#                     'startIndex': start + 1,
#                     'endIndex': end + 1,
#                 },
#                 'textStyle': {
#                     'link': {
#                         'url': url
#                     }
#                 },
#                 'fields': 'link'
#             }
#         })
#
#     # l'ancien code, fonctionnel
#     try:
#         requests = [{
#             'insertText': {
#                 'location': {
#                     'index': 1
#                 },
#                 'text': text
#             }
#         }]
#
#         # ajouter le formattage à la requete d'insert
#         requests += formatting_requests
#
#         # Execute the request.
#         result = service.documents().batchUpdate(documentId=file_id, body={'requests': requests}).execute()
#         return result
#     except HttpError as error:
#         print(F'An error occurred: {error}')
#         return None


# def formatter_titres_scenes_dans_squelettes(service, file_id):
#     try:
#         # get the document
#         doc = service.documents().get(documentId=file_id).execute()
#
#         # initialize the request list
#         requests = []
#
#         # loop through the paragraphs of the document
#         for para in doc.get('body').get('content'):
#             # check if the paragraph is a text run and starts with "titre scène"
#             if 'paragraph' in para and para.get('paragraph').get('elements')[0].get('textRun').get(
#                     'content').startswith("titre scène"):
#                 # create the update request
#                 requests.append({
#                     'updateTextStyle': {
#                         'range': {
#                             'startIndex': para.get('startIndex'),
#                             'endIndex': para.get('endIndex')
#                         },
#                         'textStyle': {
#                             'bold': True,
#                             'fontSize': {
#                                 'magnitude': 12,
#                                 'unit': 'PT'
#                             }
#                         },
#                         'fields': 'bold,fontSize'
#                     }
#                 })
#         if len(requests) != 0:
#             # execute the requests
#             result = service.documents().batchUpdate(documentId=file_id, body={'requests': requests}).execute()
#             return result
#         else:
#             return None
#     except HttpError as error:
#         print(F'An error occurred: {error}')
#         return None


def creer_fichier(service_drive, nom_fichier: str, id_parent: str, type_mime: str, m_print=print,
                  id_dossier_archive=None) -> Optional[str]:
    """Crée un fichier dans Google Drive avec un type MIME spécifique."""

    # print(f"DEBUG  : fichier archive : {id_dossier_archive}")
    if id_dossier_archive:
        # print("DEBUG  : fichier archive trouvé")
        archiver_fichiers_existants(service_drive, nom_fichier, id_parent, id_dossier_archive,
                                    considerer_supprime=False)
    try:
        metadonnees_fichier = {
            'name': nom_fichier,
            'parents': [id_parent],
            'mimeType': type_mime
        }
        fichier = service_drive.files().create(body=metadonnees_fichier, fields='id').execute()
        m_print(f'ID du fichier pour {nom_fichier}: {fichier.get("id")}')
        return fichier.get("id")
    except HttpError as erreur:
        print(f'Une erreur est survenue : {erreur}')
        print(f'Contenu de l\'erreur : {erreur.content}')
        return None


def creer_dossier_drive(service_drive, id_parent: str, nom_dossier: str, m_print=print, id_dossier_archive=None) -> \
        Optional[str]:
    """Crée un dossier dans Google Drive."""
    type_mime_dossier = 'application/vnd.google-apps.folder'
    return creer_fichier(service_drive, nom_dossier, id_parent, type_mime_dossier,
                         id_dossier_archive=id_dossier_archive)


def creer_google_sheet(service_drive, nom_feuille: str, id_dossier_parent: str, m_print=print,
                       id_dossier_archive=None) -> Optional[str]:
    """Crée un document Google Sheets dans Google Drive."""
    type_mime_feuille = 'application/vnd.google-apps.spreadsheet'
    return creer_fichier(service_drive, nom_feuille, id_dossier_parent, type_mime_feuille,
                         id_dossier_archive=id_dossier_archive)


def creer_google_doc(service_drive, nom_fichier: str, id_parent: str, m_print=print, id_dossier_archive=None) -> \
        Optional[str]:
    """Crée un document Google Docs dans Google Drive."""
    TYPE_MIME_DOCUMENT = 'application/vnd.google-apps.document'
    return creer_fichier(service_drive, nom_fichier, id_parent, TYPE_MIME_DOCUMENT,
                         id_dossier_archive=id_dossier_archive)


def archiver_fichiers_existants(service, nom_fichier, id_dossier_parent, id_dossier_archive,
                                considerer_supprime=False,
                                fichier_pre_date=True,
                                verbal=False):
    """
    Vérifie si des fichiers avec le même label existent et, le cas échéant, les déplace dans un dossier d'archives.

    Args:
        service (Resource): Le service Google Drive API.
        nom_fichier (str): Le nom du fichier à créer.
        id_dossier_parent (str): L'ID du dossier où chercher les fichiers.
        id_dossier_archive (str): L'ID du dossier où les fichiers seront archivés.
        considerer_supprime (bool): Si True, considère également les fichiers supprimés.
        fichier_pre_date (bool): Si true, on considère que le nom du fichier en entrée commence par une date et un ' - '
        :param fichier_pre_date:
        :param considerer_supprime:
        :param service:
        :param nom_fichier:
        :param id_dossier_archive:
        :param id_dossier_parent:
        :param verbal:
    """
    if nom_fichier is None or id_dossier_parent is None or id_dossier_archive is None:
        logging.debug("un paramètre de archiver fichiers existants est Null : "
                      "nom_fichier = {nom_fichier}, "
                      "id_dossier_parent = {id_dossier_parent}, "
                      "id_dossier_archive = {id_dossier_archive}")
        return

    if verbal:
        print(f"DEBUG : nom fichier en input requete d'archivage : {nom_fichier}")

    # Extraire la date-heure et le label du fichier
    # date_heure, label = nom_fichier.split(' - ')
    if fichier_pre_date:
        parties_nom_fichier = nom_fichier.split(' - ')
        label = ''.join(parties_nom_fichier[1:])
    else:
        label = nom_fichier
    query_supprime = '' if considerer_supprime else ' and trashed = false'

    if verbal:
        print(f"DEBUG : nom fichier dans requete d'archivage : {label}")

    try:
        # Appel de l'API Drive v3 pour lister tous les fichiers
        resultats = service.files().list(
            q=f"'{id_dossier_parent}' in parents and name contains '{label}'{query_supprime}",
            fields="nextPageToken, files(id, name)").execute()

        if verbal:
            print(f"DEBUG : RESULTATS dans archiver = {resultats}")

        items = resultats.get('files', [])

        if verbal:
            print(f"DEBUG : nb items  dans archiver = {len(items)}")

        # Vérifier s'il y a des fichiers avec le label spécifié
        if items:
            for item in items:
                # Déplacer le fichier vers le dossier d'archive
                id_fichier = item['id']
                fichier = service.files().get(fileId=id_fichier,
                                              fields='parents').execute()
                parents_precedents = ",".join(fichier.get('parents'))
                fichier = service.files().update(fileId=id_fichier,
                                                 addParents=id_dossier_archive,
                                                 removeParents=parents_precedents,
                                                 fields='id, parents').execute()
    except HttpError as erreur:
        # journal.error(f'Une erreur HTTP est survenue: {erreur}')
        print(f'Une erreur HTTP est survenue: {erreur}')
    except Exception as e:
        # journal.error(f'Une erreur inattendue est survenue: {e}')
        print(f'Une erreur inattendue est survenue: {e}')


# def creer_dossier_drive(service_drive, id_dossier_parent, nom_dossier):
#     # print(f"debug : {id_dossier_parent}, {nom_dossier}")
#     try:
#         # Création de l'objet dossier
#         nouveau_dossier = {'name': nom_dossier, 'parents': [id_dossier_parent],
#                            'mimeType': 'application/vnd.google-apps.folder'}
#         # Ajout du nouveau dossier
#         dossier_cree = service_drive.files().create(body=nouveau_dossier, fields='id').execute()
#         # Récupération de l'id du nouveau dossier
#         id_dossier = dossier_cree.get('id')
#         return id_dossier
#     except HttpError as error:
#         print(F'An error occurred: {error}')
#         return None

# def creer_google_doc(service, nom_fichier, parent, m_print=print):
#     try:
#         # create the metadata for the new document
#         file_metadata = {
#             'name': nom_fichier,
#             'parents': [parent],
#             'mimeType': 'application/vnd.google-apps.document'
#         }
#
#         # create the document
#         file = service.files().create(body=file_metadata, fields='id').execute()
#         m_print(f'File ID pour {nom_fichier}: {file.get("id")}')
#         return file.get("id")
#
#     except HttpError as error:
#         print(F'An error occurred: {error}')
#         file = None

# def creer_google_sheet(api_drive, nom_sheet: str, parent_folder_id: str):
#     # Create a new document
#     body = {
#         'name': nom_sheet,
#         'parents': [parent_folder_id],
#         'mimeType': 'application/vnd.google-apps.spreadsheet'
#     }
#     new_doc = api_drive.files().create(body=body).execute()
#     return new_doc.get("id")


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
    values = [["nom_scene", "date", "qui", 'intrigue', "document"] + list(dict_orgas_persos.keys())]
    if verbal:
        print(f"en-tetes = {values}")

    for scene_orgas in tableau_scenes_orgas:
        dict_scene, dict_orgas = scene_orgas
        row = [dict_scene["nom_scene"], dict_scene["date"], dict_scene["qui"], dict_scene["intrigue"],
               dict_scene["document"]]

        for orga in dict_orgas_persos:
            if orga in dict_orgas:
                nom_persos = ", ".join(list(dict_orgas[orga]))
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
        persos = list(dict_orgas_persos[orga])
        values = [["nom_scene", "date", "qui", 'intrigue', "document"] + persos]
        if verbal:
            print(f"en-tetes = {values}")
        for scene_orgas in tableau_scenes_orgas:
            dict_scene, dict_orgas = scene_orgas
            row = [dict_scene["nom_scene"], dict_scene["date"], dict_scene["qui"], dict_scene["intrigue"],
                   dict_scene["document"]]

            croix = []
            for perso in dict_orgas_persos[orga]:
                if orga not in dict_orgas or perso not in dict_orgas[orga]:
                    croix.append("")
                else:
                    croix.append("x")
            if sum(len(c) for c in croix) > 0:
                row.extend(croix)
                values.append(row)

            # for perso in dict_orgas_persos[orga]:
            #     if orga not in dict_orgas or perso not in dict_orgas[orga]:
            #         row.append("")
            #     else:
            #         row.append("x")
            # values.append(row)
        body = {
            'range': f'{orga}!A1',
            'values': values,
            'majorDimension': 'ROWS'
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=f'{orga}!A1',
            valueInputOption='RAW', body=body).execute()


def expand_grid(api_sheets, spreadsheet_id, sheet_id, table):
    new_rows = len(table)
    new_cols = max(len(row) for row in table)

    try:
        api_sheets.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": sheet_id,
                                "gridProperties": {
                                    "rowCount": new_rows,
                                    "columnCount": new_cols
                                }
                            },
                            "fields": "gridProperties(rowCount,columnCount)"
                        }
                    }
                ]
            }
        ).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')


# def write_to_sheet(api_sheets, table, spreadsheet_id, feuille="Feuille 1", avec_formules=True):
def write_to_sheet(api_sheets, table, spreadsheet_id, feuille=None, avec_formules=True):
    #
    # if avec_formules:
    #     ecrire_table_google_sheets_avec_formules(api_sheets, table, spreadsheet_id, feuille=feuille)
    # else:
    #     ecrire_table_google_sheets_sans_formules(api_sheets, table, spreadsheet_id, feuille=feuille)

    ecrire_table_google_sheets_avec_formules(api_sheets, table, spreadsheet_id, feuille=feuille)


def ecrire_table_google_sheets_sans_formules(api_sheets, table, spreadsheet_id, feuille=None):
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

    # def write_to_sheet(api_doc, df, spreadsheet_id):
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


# def ecrire_table_google_sheets_avec_formules(api_sheets, table, spreadsheet_id, feuille=None):
#     if feuille is not None:
#         try:
#             api_sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
#                 "requests": [
#                     {
#                         "addSheet": {
#                             "properties": {
#                                 "title": feuille
#                             }
#                         }
#                     }
#                 ]
#             }).execute()
#         except HttpError as error:
#             print(f'An error occurred: {error}')
#
#     # Get the list of sheets in the spreadsheet
#     sheets = api_sheets.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()['sheets']
#
#     # Find the sheetId of the sheet we're writing to
#     # sheetId = None
#     # for sheet in sheets:
#     #     if sheet['properties']['title'] == feuille:
#     #         sheetId = sheet['properties']['sheetId']
#     #         break
#
#     # if sheetId is None:
#     #     print(f"Sheet '{feuille}' not found")
#     #     return None
#     #
#     sheetId = None
#
#     for i, sheet in enumerate(sheets):
#         # Store the ID of the first sheet
#         if i == 0:
#             sheetId = sheet['properties']['sheetId']
#
#         if sheet['properties']['title'] == feuille:
#             sheetId = sheet['properties']['sheetId']
#             break
#
#
#
#     requests = []
#
#     for i, row in enumerate(table):
#         for j, cell in enumerate(row):
#             if isinstance(cell, str) and cell.startswith('='):
#                 # This cell contains a formula
#                 requests.append({
#                     "repeatCell": {
#                         "range": {
#                             "sheetId": sheetId,
#                             "startRowIndex": i,
#                             "endRowIndex": i + 1,
#                             "startColumnIndex": j,
#                             "endColumnIndex": j + 1
#                         },
#                         "cell": {
#                             "userEnteredValue": {
#                                 "formulaValue": cell
#                             }
#                         },
#                         "fields": "userEnteredValue"
#                     }
#                 })
#             else:
#                 # This cell contains regular text
#                 requests.append({
#                     "repeatCell": {
#                         "range": {
#                             "sheetId": sheetId,
#                             "startRowIndex": i,
#                             "endRowIndex": i + 1,
#                             "startColumnIndex": j,
#                             "endColumnIndex": j + 1
#                         },
#                         "cell": {
#                             "userEnteredValue": {
#                                 "stringValue": str(cell)
#                             }
#                         },
#                         "fields": "userEnteredValue"
#                     }
#                 })
#
#     try:
#         result = api_sheets.spreadsheets().batchUpdate(
#             spreadsheetId=spreadsheet_id,
#             body={"requests": requests}
#         ).execute()
#
#     except HttpError as error:
#         print(f'An error occurred: {error}')
#         result = None
#     return result

def ecrire_table_google_sheets_avec_formules(api_sheets, table, spreadsheet_id, feuille=None):
    if feuille is not None:
        try:
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

    # Get the list of sheets in the spreadsheet
    sheets = api_sheets.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()['sheets']

    sheet_id = None

    for i, sheet in enumerate(sheets):
        # Store the ID of the first sheet
        if i == 0:
            sheet_id = sheet['properties']['sheetId']

        if sheet['properties']['title'] == feuille:
            sheet_id = sheet['properties']['sheetId']
            break

    expand_grid(api_sheets, spreadsheet_id, sheet_id, table)

    requests = []

    for i, row in enumerate(table):
        for j, cell in enumerate(row):
            if isinstance(cell, str) and cell.startswith('='):
                # This cell contains a formula
                requests.append({
                    "updateCells": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": i,
                            "endRowIndex": i + 1,
                            "startColumnIndex": j,
                            "endColumnIndex": j + 1
                        },
                        "rows": [{
                            "values": [{
                                "userEnteredValue": {
                                    "formulaValue": cell
                                }
                            }]
                        }],
                        "fields": "userEnteredValue"
                    }
                })
            else:
                # This cell contains regular text
                requests.append({
                    "updateCells": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": i,
                            "endRowIndex": i + 1,
                            "startColumnIndex": j,
                            "endColumnIndex": j + 1
                        },
                        "rows": [{
                            "values": [{
                                "userEnteredValue": {
                                    "stringValue": str(cell)
                                }
                            }]
                        }],
                        "fields": "userEnteredValue"
                    }
                })

    try:
        result = api_sheets.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests}
        ).execute()

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

        if requests:
            # Envoie toutes les requêtes en une seule fois pour mettre à jour le document
            result = api_doc.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
        else:
            return None

    except Exception:
        result = None

    return result


def reconstituer_tableau(texte_lu: str, sans_la_premiere_ligne=True):
    """
    Reconstitue un tableau de données à partir d'une chaîne de texte formatée.

    Cette fonction divise un texte contenant un tableau de données en lignes et colonnes,
    en supprimant optionnellement la première ligne (typiquement des en-têtes).

    Parameters:
    texte_lu (str): Le texte brut contenant le tableau de données.
    sans_la_premiere_ligne (bool, optional): Indique si la première ligne doit être ignorée. Par défaut à True.

    Returns:
    Tuple[List[List[str]], int]:
    - Une liste de listes, chaque sous-liste représentant une ligne du tableau reconstitué.
    - Le nombre de colonnes détecté dans la première ligne valide du tableau, ou 0 si le tableau est vide.

    Raises:
    ValueError: Si `texte_lu` ne contient pas le marqueur de fin de ligne attendu.

    Notes:
    La chaîne de texte est attendue avec un format spécifique, utilisant des constantes de `lecteurGoogle` pour
    indiquer la fin des lignes et la séparation des colonnes. Les lignes vides ou ne contenant que des espaces
    seront ignorées dans le tableau reconstitué.
    """

    # # logging.debug(f"chaine en entrée = {repr(texte_lu)}")
    # last_hash_index = texte_lu.rfind(lecteurGoogle.FIN_LIGNE)
    # if last_hash_index == -1:
    #     return [], 0
    #
    # texte_tableau = texte_lu[:last_hash_index]
    # A TESTER : version alternative du nettoyage des chaines
    pattern = f"{lecteurGoogle.DEBUT_TABLEAU}(.*?){lecteurGoogle.FIN_TABLEAU}"

    match = re.search(pattern, texte_lu, re.DOTALL)
    if not match:
        return [], 0

    texte_tableau = match.group(1)

    # texte_tableau = texte_lu[:last_hash_index + 1]
    # logging.debug(f"chaine réduite = {repr(texte_tableau)}")
    lignes = texte_tableau.split(lecteurGoogle.FIN_LIGNE)
    to_return = []

    base_index = 1 if sans_la_premiere_ligne else 0

    for ligne in lignes[base_index:]:
        tmp_ligne = [element.strip() for element in ligne.split(lecteurGoogle.SEPARATEUR_COLONNES)]
        taille_ligne = sum(len(element) for element in tmp_ligne)
        if taille_ligne > 1:
            to_return.append(tmp_ligne)

    # logging.debug(f"a partir de la chaine {repr(texte_lu)} "
    #               f"j'ai reconstitué le tableau \n {to_return}"
    #               )
    return to_return or [], len(to_return[0]) if to_return else 0


def lire_gspread_pj_pnjs(api_sheets, sheet_id):
    """
    Lit les données des feuilles "PJs" et "PNJs" d'un Google Spreadsheet et les stocke dans deux listes de
    dictionnaires.

    Cette fonction utilise la méthode `mettre_sheet_dans_dictionnaires` pour lire les données des feuilles "PJs" et
    "PNJs" et les stocker dans deux listes de dictionnaires séparées.

    Args:
        api_sheets (googleapiclient.discovery.Resource): L'objet API Google Sheets pour accéder au service.
        sheet_id (str): L'ID du Google Spreadsheet.

    Returns:
        tuple: Un tuple contenant deux listes de dictionnaires :
               - La première liste contient les données de la feuille "PJs".
               - La deuxième liste contient les données de la feuille "PNJs".
    """
    pjs_lus = mettre_sheet_dans_dictionnaires(api_sheets, sheet_id, "PJs")
    pnjs_lus = mettre_sheet_dans_dictionnaires(api_sheets, sheet_id, "PNJs")
    return pjs_lus, pnjs_lus


def mettre_sheet_dans_dictionnaires(api_sheets, sheet_id, sheet_name):
    """
    Récupère les données d'une feuille Google Spreadsheet et les stocke dans une liste de dictionnaires.

    Chaque ligne de la feuille est convertie en un dictionnaire avec les entêtes de colonnes comme clés
    et les cellules comme valeurs. La liste retournée contient ces dictionnaires pour chaque ligne.

    Args:
        api_sheets (googleapiclient.discovery.Resource): L'objet API Google Sheets pour accéder au service.
        sheet_id (str): L'ID du Google Spreadsheet.
        sheet_name (str): Le nom de la feuille à récupérer.

    Returns:
        list[dict]: Une liste de dictionnaires contenant les données de la feuille,
                   ou None en cas d'erreur.
    """
    try:
        result = api_sheets.spreadsheets().values().get(spreadsheetId=sheet_id, range=sheet_name,
                                                        majorDimension="ROWS").execute()
        values = result.get('values', [])
        en_tetes = [en_tete.strip() for en_tete in values[0]]
        # taille_ligne = len(en_tetes)

        to_return = []
        for ligne in values[1:]:
            dico_ligne = {
                en_tete: ligne[i] if i < len(ligne) else ''
                for i, en_tete in enumerate(en_tetes)
            }
            to_return.append(dico_ligne)

        return to_return
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def supprimer_feuille_1(api_sheets, spreadsheet_id):
    sheets = api_sheets.spreadsheets().get(spreadsheetId=spreadsheet_id).execute().get('sheets', '')
    for sheet in sheets:
        if sheet.get("properties", {}).get("title", "") == "Feuille 1":
            sheet_id = sheet.get("properties", {}).get("sheetId", 0)
            api_sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
                "requests": [
                    {
                        "deleteSheet": {
                            "sheetId": sheet_id
                        }
                    }
                ]
            }).execute()
            logging.debug(f"Sheet Feuille 1 supprimée dans {spreadsheet_id}")
            break
    else:
        logging.debug(f"Sheet Feuille 1 non trouvée dans {spreadsheet_id}")


def extraire_commentaires_de_document_drive(api_drive, id_fichier: str):
    try:
        liste = api_drive.comments().list(fileId=id_fichier,
                                          fields="comments(content, replies, resolved, author)").execute()
    except HttpError as error:
        print(f"Erreur durant la lecture des commentaires: {error}")
        return []

    to_return = []
    for current_dict_commentaire in liste['comments']:
        # on vérifie qu'il n'est pas fermé ou résolu
        if current_dict_commentaire.get('resolved', False) or \
                current_dict_commentaire.get('deleted', False):
            continue

        # on ajoute son texte et on va chercher ses réponses
        texte_commentaire = current_dict_commentaire.get("content", "")
        for reply in current_dict_commentaire.get("replies", []):
            if reply.get('resolved', False) or reply.get('deleted', False):
                continue
            texte_commentaire += f"'\n' {reply.get('author', '')} dit : {reply.get('content', '')}"

        # à ce stade là on a choppé tout le texte

        # on choppe l'auteur
        try:
            auteur = current_dict_commentaire['author']['displayName']
        except KeyError:
            logging.debug(f"problème avec le nom de l'auteur "
                          f"{current_dict_commentaire.get('author', 'auteur illisible')}")
            logging.debug(f"clef présentes dans le dictionnaire : "
                          f"{current_dict_commentaire.keys()}")

            auteur = "auteur sans nom"

        # regarde pour qui c'est:
        pattern = r"@[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+"
        destinataires = re.findall(pattern, texte_commentaire)
        destinataires = [d[1:].lower() for d in destinataires]

        to_return.append(Commentaire(texte_commentaire, auteur, destinataires))

    return to_return


def preparer_tests_dict_config(dict_config: dict):
    dossiers_a_verifier = []
    google_docs_a_verifier = []
    google_sheets_a_verifier = []

    for meta_valeur in ['dossiers_intrigues', 'dossiers_pjs', 'dossiers_pnjs', 'dossiers_evenements',
                        'dossiers_objets']:
        if f'nom_{meta_valeur}' not in dict_config:
            dict_config[f'nom_{meta_valeur}'] = []

        longueur_supp = len(dict_config[f'{meta_valeur}']) - len(dict_config[f'nom_{meta_valeur}'])

        if longueur_supp > 0:
            dict_config[f'nom_{meta_valeur}'].extend([meta_valeur] * longueur_supp)

        for clef, valeur in zip(dict_config[f'nom_{meta_valeur}'], dict_config[meta_valeur]):
            dossiers_a_verifier.append([clef, valeur])

    if id_archive := dict_config.get('id_dossier_archive'):
        dossiers_a_verifier.append(['fichier_archive', id_archive])

    # intégration du fichier des factions
    if id_factions := dict_config.get('id_factions'):
        google_docs_a_verifier.append(["id_factions", id_factions])

    # intégration du fichier des ids pjs_pnjs
    if id_pjs_et_pnjs := dict_config.get('id_pjs_et_pnjs'):
        google_sheets_a_verifier.append(["id_pjs_et_pnjs", id_pjs_et_pnjs])

    id_output = dict_config['dossier_output']

    return dossiers_a_verifier, google_docs_a_verifier, google_sheets_a_verifier, id_output


def mener_tests_config(api_drive, dossiers_a_verifier, google_docs_a_verifier, google_sheets_a_verifier, id_output):
    resultats = []
    test_global_reussi = True
    # a ce stade là on a :
    # 1. intégré tous les paramètres au fichier de sortie
    # 2. fait les premiers tests sur les fichiers essentiels
    # 3. préparé les tableaux à parcourir pour faire les tests d'accès / existence aux dossiers
    # >> on peut lancer les tests
    # print(f'DEBUG : dossiers à verifier : {dossiers_a_verifier}')
    for parametre, dossier_id in dossiers_a_verifier:
        try:
            # dossier = api_drive.files().get(fileId=dossier_id).execute()

            folder_metadata = api_drive.files().get(fileId=dossier_id).execute()
            # print(f"debug : dossier ID {dossier_id}")
            # Récupérer le nom du dossier
            folder_name = folder_metadata['name']

            resultats.append([parametre, folder_name, "Test Réussi"])
        except HttpError as error:
            resultats.append([parametre, "", "Echec du Test"])
            logging.debug(f"Erreur durant la vérification du dossier {dossier_id} : {error}")
            test_global_reussi = False
        except KeyError as error:
            resultats.append([parametre, "impossible de lire le paramètre", "Echec du Test"])
            logging.debug(f"Erreur durant la vérification du dossier {dossier_id} : {error}")
            test_global_reussi = False
    # Test pour les Google Docs
    for parametre, doc_id in google_docs_a_verifier:
        try:
            doc_metadata = api_drive.files().get(fileId=doc_id).execute()
            doc_name = doc_metadata['name']
            resultats.append([parametre, doc_name, "Test Réussi"])
        except HttpError as error:
            resultats.append([parametre, "", "Echec du Test"])
            logging.debug(f"Erreur durant la vérification du fichier {doc_id} : {error}")
            test_global_reussi = False
    # Test pour les Google Sheets
    for parametre, sheet_id in google_sheets_a_verifier:
        try:
            sheet_metadata = api_drive.files().get(fileId=sheet_id).execute()
            sheet_name = sheet_metadata['name']
            resultats.append([parametre, sheet_name, "Test Réussi"])
        except HttpError as error:
            resultats.append([parametre, "", "Echec du Test"])
            logging.debug(f"Erreur durant la vérification du fichier {sheet_id} : {error}")
            test_global_reussi = False
    # Vérification des droits d'écriture dans le dossier de sortie
    dossier_output_id = id_output
    try:
        permissions = api_drive.permissions().list(fileId=dossier_output_id).execute()
        droit_ecriture = any(
            permission['role'] in ['writer', 'owner']
            for permission in permissions['permissions']
        )
        if droit_ecriture:
            resultats.append(["Droits en écriture", "sur le fichier de sortie", "Test Réussi"])
        else:
            resultats.append(["Droits en écriture", "sur le fichier de sortie", "Echec du Test"])
            test_global_reussi = False
    except HttpError as error:
        resultats.append(["Droits en écriture", "sur le fichier de sortie", "Echec du Test"])
        logging.debug(f"Erreur durant la vérification des droits en écriture sur {dossier_output_id} : {error}")
        test_global_reussi = False
    except KeyError as error:
        resultats.append(["Droits en écriture", "sur le fichier de sortie", "Echec du Test"])
        logging.debug(f"Pas de dossier d'écriture : {error}")
        test_global_reussi = False

    return test_global_reussi, resultats


def verifier_dict_config(dict_config: dict, api_drive):
    dossiers_a_verifier, gdocs_a_verifier, gsheets_a_verifier, id_output = preparer_tests_dict_config(dict_config)
    test_ok, commentaires = mener_tests_config(api_drive,
                                               dossiers_a_verifier,
                                               gdocs_a_verifier,
                                               gsheets_a_verifier,
                                               id_output)
    return test_ok, commentaires


def creer_dict_config(config: configparser.ConfigParser):
    resultats = []
    test_global_reussi = True
    dict_config = {}

    # *** vérification que tous les paramètres Essentiels sont présents

    # intégration du fichier de sortie
    try:
        dict_config['dossier_output'] = config.get('Essentiels', 'dossier_output_squelettes_pjs')
    except configparser.NoOptionError:
        resultats.append(
            ["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de dossier de sortie trouvé"])
        test_global_reussi = False

    def decouper_clefs(clef_valeurs, prefixe_param, essentiel: bool):
        clef_nom = f'nom_{clef_valeurs}'
        section = "Essentiels" if essentiel else "Optionnels"
        dict_config[clef_valeurs] = []
        dict_config[clef_nom] = []
        clefs = [key for key in config.options(section) if key.startswith(prefixe_param)]
        for clef in clefs:
            valeur = config.get(section, clef)
            dict_config[clef_valeurs].append(valeur)
            dict_config[clef_nom].append(clef)
            # todo : si remise à plat du dictionnaire de paramètres, renvoyer un dictionnaire nom:valeur plutot que
            #  deux listes séparées qu'il faut faire correspondre pour savoir quel paramètre correspond à quel
            #  nom de paramètre

    # intégration des dossiers intrigues et vérifications

    decouper_clefs(clef_valeurs='dossiers_intrigues',
                   prefixe_param="id_dossier_intrigues",
                   essentiel=True)
    if len(dict_config.get('dossiers_intrigues', [])) == 0:
        resultats.append(["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de dossier intrigue"])
        test_global_reussi = False

    # intégration du mode association et vérifications
    try:
        mode_association_value = int(config.get('Essentiels', 'mode_association', fallback="9")[0])
        if mode_association_value in {0, 1}:
            dict_config['mode_association'] = GN.ModeAssociation(mode_association_value)
        else:
            resultats.append(["Paramètre Essentiels", "Validité du fichier de paramètres", "Mode association invalide"])
            test_global_reussi = False
    except configparser.NoOptionError:
        resultats.append(
            ["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de mode association trouvé"])
        test_global_reussi = False
    except IndexError:
        resultats.append(
            ["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de mode association trouvé"])
        test_global_reussi = False
    # intégration du fichier de sauvegarde
    try:
        dict_config['nom_fichier_sauvegarde'] = config.get('Essentiels', 'nom_fichier_sauvegarde')
    except configparser.NoOptionError:
        resultats.append(["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de fichier de sauvegarde"])
        test_global_reussi = False
    # intégration d'une ligne de bilan des tests essentiels
    if test_global_reussi:
        resultats.append(["Paramètre Essentiels", "Présence des champs", "Test Réussi"])
    # *** intégration des fichiers optionnels
    # création du paramètre fichier local sauvegarde, par défaut ou tel que lu
    try:
        nom_dossier_sauvegarde = config.get('Optionnels', 'nom_fichier_sauvegarde')
        dict_config['dossier_local_fichier_sauvegarde'] = os.path.join(os.path.curdir, nom_dossier_sauvegarde)
    except configparser.NoOptionError:
        dict_config['dossier_local_fichier_sauvegarde'] = os.path.curdir

    # dossiers PJS
    decouper_clefs(clef_valeurs='dossiers_pjs',
                   prefixe_param="id_dossier_pjs",
                   essentiel=False)

    # intégration des dossiers PNJs
    decouper_clefs(clef_valeurs='dossiers_pnjs',
                   prefixe_param="id_dossier_pnjs",
                   essentiel=False)

    # intégration des dossiers Evenements
    decouper_clefs(clef_valeurs='dossiers_evenements',
                   prefixe_param="id_dossier_evenements",
                   essentiel=False)

    # intégration des dossiers objets
    decouper_clefs(clef_valeurs='dossiers_objets',
                   prefixe_param="id_dossier_objets",
                   essentiel=False)

    # intégration du fichier des factions
    id_factions = config.get('Optionnels', 'id_factions', fallback=None)
    dict_config['id_factions'] = id_factions

    # intégration du fichier des ids pjs_pnjs
    id_pjs_et_pnjs = config.get('Optionnels', 'id_pjs_et_pnjs', fallback=None)
    if id_pjs_et_pnjs:
        dict_config['id_pjs_et_pnjs'] = id_pjs_et_pnjs
    else:
        logging.debug("Je suis en train de lire le fichier de config et je n'ai pas trouvé d'id pjpnj en ligne")
        dict_config['fichier_noms_pnjs'] = config.get('Optionnels', 'nom_fichier_pnjs', fallback=None)
        dict_config['liste_noms_pjs'] = [nom_p.strip()
                                         for nom_p in
                                         config.get('Optionnels', 'noms_persos', fallback="").split(',')]

    # ajout de la date du GN
    texte_date_gn = config.get('Optionnels', 'date_gn', fallback=None)
    if texte_date_gn:
        dict_config['date_gn'] = dateparser.parse(texte_date_gn, languages=['fr'])
        logging.debug(f"date_gn formattée = {dict_config['date_gn']}")
    else:
        logging.debug("pour ce GN, date_gn = Pas de date lue")
    dict_config['prefixe_intrigues'] = config.get('Optionnels', 'prefixe_intrigues', fallback="I")
    dict_config['prefixe_evenements'] = config.get('Optionnels', 'prefixe_evenements', fallback="E")
    dict_config['prefixe_PJs'] = config.get('Optionnels', 'prefixe_PJs', fallback="P")
    dict_config['prefixe_PNJs'] = config.get('Optionnels', 'prefixe_PNJs', fallback="N")
    dict_config['prefixe_objets'] = config.get('Optionnels', 'prefixe_objets', fallback="O")
    dict_config['liste_noms_pjs'] = config.get('Optionnels', 'noms_persos', fallback=None)
    # ajouter le dossier archive
    dict_config['id_dossier_archive'] = config.get('Optionnels', 'id_dossier_archive', fallback=None)

    return dict_config, test_global_reussi, resultats


def fichier_ini_2_parser(fichier_ini: str):
    """
    Charge un fichier de configuration INI et retourne l'objet de configuration ainsi qu'une éventuelle erreur.

    Paramètres:
    - fichier_ini (str) : Chemin d'accès complet du fichier INI à charger.

    Retourne: - tuple: Un tuple contenant deux éléments : 1. configparser.ConfigParser: L'objet de configuration
    chargé à partir du fichier INI. Retourne None si une erreur s'est produite. 2. list: Une liste de listes
    contenant des détails sur l'erreur. Retourne None si le chargement a réussi.

    Notes: - En cas d'erreur lors du chargement, la fonction retourne un objet ConfigParser vide et une liste
    décrivant l'erreur. - Si le fichier est chargé avec succès, la fonction retourne l'objet de configuration et la
    valeur None pour l'erreur.
    """
    try:
        # #création du fichier d'entrée
        # init configuration
        config = configparser.ConfigParser()
        config.read(fichier_ini)
    except Exception as e:
        logging.debug(f"Une erreur est survenue en lisant le fichier config : {e}")
        return None, [["Fichier configuration", "Erreur dans la structure du fichier", "Echec du test"]]
    return config, None


def verifier_fichier_gn_et_fournir_dict_config(nom_fichier: str, api_drive, m_print=print):
    if nom_fichier.endswith('.ini'):
        mon_parser, resultats = fichier_ini_2_parser(nom_fichier)
        if not mon_parser:
            m_print("Erreur dans la structure du fichier ini fourni en entrée")
            return False, resultats, None
        dict_config, structure_fichier_ok, details_tests = creer_dict_config(mon_parser)
    elif nom_fichier.endswith('.mgn'):
        mon_gn = GN.load(nom_fichier, m_print=m_print)
        dict_config = mon_gn.dict_config
    else:
        m_print("Erreur : le fichier fourni n'es pas d'un type reconnu par MAGnet")
        return False, [['Fichier non reconnu', '', '']], None

    test_ok, commentaires = verifier_dict_config(dict_config, api_drive)
    return test_ok, commentaires, dict_config


def verifier_config_parser(api_drive, config: configparser.ConfigParser):
    dict_config, test_global_reussi, resultats = creer_dict_config(config)
    if not test_global_reussi:
        return test_global_reussi, resultats
    test_ok, commentaires = verifier_dict_config(dict_config, api_drive)
    return test_ok, commentaires


# todo : voir si pas de redondance avec le teste effectué dans le fichier de config
def verifier_acces_fichier(api_drive, folder_id):
    try:
        # Get the metadata of the folder using its ID
        folder = api_drive.files().get(fileId=folder_id, fields="capabilities").execute()

        # Check if the folder is writable
        can_write = folder['capabilities']['canEdit']

        if can_write:
            return True, "The folder exists and you have write access"
        else:
            return False, "Le fichier existe mais vous n'avez pas les droits en écriture"

    except HttpError as error:
        return False, "Le dossier n'existe pas ou vous n'avez pas le droit d'y accéder"


def copier_fichier_vers_dossier(api_drive, file_id, destination_folder_id):
    try:
        # Get the metadata of the file
        file_metadata = api_drive.files().get(fileId=file_id, fields="name").execute()

        # Set the destination folder ID in the 'parents' field
        file_metadata['parents'] = [destination_folder_id]

        # Copy the file to the destination folder
        copied_file = api_drive.files().copy(fileId=file_id, body=file_metadata).execute()

        # Return the ID of the copied file
        return copied_file['id']

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def extraire_id_google_si_possible(user_text):
    # Regular expression pattern for Google Drive, Sheets, and Docs URLs
    # pattern = r'https?://(?:drive|docs)\.google\.com/(?:drive/u/0/folders/|spreadsheets/d/|document/d/)([a-zA-Z0-9_-]+)'
    pattern = r'https?://(?:drive|docs)\.google\.com/(?:drive/u/[0-9]+/folders/|spreadsheets/d/|document/d/)([a-zA-Z0-9_-]+)'

    if match := re.search(pattern, user_text):
        return match.group(1), True

    elif re.fullmatch(r'[a-zA-Z0-9_-]+', user_text):
        return user_text, True

    else:
        return user_text, False


def telecharger_derniere_archive(source_folder_id, dest_folder, api_drive, save_file_name, last_save_connu=None,
                                 m_print=print):
    save_file_name = normaliser_nom_gn(save_file_name)
    # Find the most recent save file
    # results = service.files().list(q=f"'{source_folder_id}' in parents",
    #                                orderBy="modifiedTime desc",
    #                                pageSize=1).execute()

    query = f"'{source_folder_id}' in parents and name contains '{save_file_name}'"
    # print(f"DEBUG : query telechargement archive = {query}")
    results = api_drive.files().list(q=query,
                                     orderBy="modifiedTime desc",
                                     fields="files(id, name)",
                                     pageSize=1).execute()
    if items := results.get('files', []):
        if last_save_connu:
            nom = items[0]['name']
            last_save_online = nom.split(' - ')[0]
            if last_save_online <= last_save_connu:
                m_print("La version locale est la dernière à jour, pas besoin de télécharger")
                return None

        file_id = items[0]['id']
        request = api_drive.files().get_media(fileId=file_id)
        # local_path = f"{dest_folder}/{items[0]['name']}"
        # local_path = f"{dest_folder}/{save_file_name}"
        local_path = os.path.join(dest_folder, save_file_name)
        print(f"telechargement en cours vers {local_path}")
        with io.FileIO(local_path, 'wb') as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        return local_path
    else:
        print('aucune archive en ligne trouvée')
        return None


def uploader_archive(file_path, folder_id, api_drive, current_date):
    new_filename = f"{current_date} - {os.path.basename(file_path)}"
    new_filename = normaliser_nom_gn(new_filename)

    file_metadata = {
        'name': new_filename,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path,
                            mimetype='application/octet-stream',
                            resumable=True)
    file = api_drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')


def charger_gn(nom_archive: str, source_folder_id: str, dest_folder: str, api_drive=None, m_print=print,
               dict_config=None, last_save_connu=None):
    nom_archive = normaliser_nom_gn(nom_archive)
    chemin_archive = os.path.join(dest_folder, nom_archive)

    # print(f"DEBUG : dict_config = {dict_config}")

    if api_drive:
        m_print("téléchargement de la dernière version de l'archive...")
        if telecharger_derniere_archive(source_folder_id, dest_folder, api_drive, nom_archive, last_save_connu,
                                        m_print=m_print):
            m_print("téléchargement terminé")
        else:
            m_print("Aucun téléchargement effectué")

    return GN.load(chemin_archive, dict_config=dict_config, m_print=m_print)


def charger_gn_from_dict(dict_config: dict, api_drive=None, m_print=print, updater_dict_config=True,
                         last_save_connu=None):
    nom_archive = normaliser_nom_gn(dict_config['nom_fichier_sauvegarde'])
    dest_folder = dict_config['dossier_local_fichier_sauvegarde']
    source_folder_id = dict_config.get('dossier_output')
    chemin_archive = os.path.join(dest_folder, nom_archive)

    archive_locale = GN.load(chemin_archive, dict_config=dict_config, m_print=m_print, creer_si_erreur=False)
    if archive_locale:
        last_save_connu = archive_locale.get_last_save()

    return charger_gn(nom_archive, source_folder_id, dest_folder, api_drive, m_print=m_print,
                      dict_config=dict_config if updater_dict_config else None,
                      last_save_connu=last_save_connu)


def charger_gn_from_gn(mon_gn: GN, api_drive, m_print=print, updater_dict_config=None):
    nom_archive = mon_gn.get_nom_fichier_sauvegarde()
    dest_folder = mon_gn.get_dossier_local_fichier_sauvegarde()
    source_folder_id = mon_gn.get_dossier_outputs_drive()
    last_save_connu = mon_gn.get_last_save()
    return charger_gn(nom_archive, source_folder_id, dest_folder, api_drive, m_print=m_print,
                      dict_config=mon_gn.dict_config if updater_dict_config else None,
                      last_save_connu=last_save_connu)


def sauvegarder_et_uploader_gn(mon_gn: GN, api_drive=None, rendre_gn_recherchable=True):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    path = mon_gn.save(last_save=current_date)

    if api_drive:
        nom_archive = os.path.basename(path)
        dossier_upload = mon_gn.get_dossier_outputs_drive()
        if id_archive := mon_gn.get_id_dossier_archive():
            archiver_fichiers_existants(api_drive, nom_archive, dossier_upload, id_archive, fichier_pre_date=False)
        uploader_archive(path, dossier_upload, api_drive, current_date=current_date)
        if rendre_gn_recherchable:
            ajouter_archive_gn_aux_recherchables(api_drive, dossier_upload)


def ajouter_archive_gn_aux_recherchables(api_drive, dossier_upload: str, fichier_destination=ID_FICHIER_ARCHIVES):
    # print(dossier_upload)
    # print(fichier_destination)
    try:
        # # # Étape 1: Obtenez le contenu actuel du fichier
        # # fichier = api_drive.files().get(fileId=fichier_destination, alt='media').execute()
        # # print(f'{fichier}')
        # # contenu_fichier = fichier.decode('utf-8')
        #
        # # Étape 1: Obtenez le contenu actuel du fichier
        # request = api_drive.files().get(fileId=fichier_destination, alt='media')
        # fh = io.BytesIO(request.execute())
        # contenu_fichier = fh.read().decode('utf-8')
        # print(f"{contenu_fichier}")
        # Étape 1: Obtenez le contenu actuel du fichier
        request = api_drive.files().get_media(fileId=fichier_destination)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
        contenu_fichier = fh.read().decode('utf-8')

        # Étape 2: Vérifiez si dossier_upload est déjà présent dans le fichier
        if dossier_upload in contenu_fichier:
            print(f"L'ID du dossier {dossier_upload} est déjà présent dans le fichier.")
            return

        # Étape 3: Si non, ajoutez dossier_upload à la fin du fichier
        nouveau_contenu = contenu_fichier + '\n' + dossier_upload
        media = MediaIoBaseUpload(io.StringIO(nouveau_contenu), mimetype='text/plain')
        api_drive.files().update(fileId=fichier_destination, media_body=media).execute()

        print(f"L'ID du dossier {dossier_upload} a été ajouté au fichier.")
    except HttpError as error:
        print(f"Une erreur HTTP s'est produite en voulant ajouter le GN aux archives en ligne : {error}")
    except Exception as error:
        print(f"Une erreur inattendue s'est produite en voulant ajouter le GN aux archives en ligne : {error}")


def id_2_sheet_address(id_sheet: str):
    return r"https://docs.google.com/spreadsheets/d/" + id_sheet
