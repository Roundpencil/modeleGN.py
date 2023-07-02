from __future__ import print_function

import configparser
from enum import Enum
from typing import Optional

import fuzzywuzzy.process
from googleapiclient.errors import HttpError

import lecteurGoogle
from modeleGN import *


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

    mon_objet = fonction_extraction(text, document.get('title'), item["id"], last_file_edit, derniere_modification_par,
                                    dict_reference, verbal)
    # mon_objet.url = item["id"]
    # on enregistre la date de dernière mise à jour

    if mon_objet is not None and save_last_change:
        mon_objet.set_last_processing(datetime.datetime.now())
    # print(f'url intrigue = {mon_objet.url}')
    # print(f"intrigue {mon_objet.nom}, date de modification : {item['modifiedTime']}")

    return mon_objet


def extraire_intrigue_de_texte(texte_intrigue, nom_intrigue, id_url, last_file_edit, derniere_modification_par,
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

    labels = [lab.value for lab in Labels]

    indexes = lecteurGoogle.identifier_sections_fiche(labels, texte_intrigue)
    # print(f"debug : indexes = {indexes}")

    dict_methodes = {
        Labels.REFERENT: intrigue_referent,
        Labels.TODO: intrigue_todo,
        Labels.PITCH: intrigue_pitch,
        Labels.CROISEES: intrigue_croisee,
        Labels.PJS: intrigue_pjs,
        Labels.PNJS: intrigue_pnjs,
        Labels.REROLLS: intrigue_rerolls,
        Labels.OBJETS: intrigue_objets,
        Labels.SCENESFX: intrigue_scenesfx,
        Labels.TIMELINE: intrigue_timeline,
        Labels.SCENES: intrigue_scenes,
        Labels.RESOLUTION: intrigue_resolution,
        Labels.NOTES: intrigue_notes,
        Labels.QUESTIONNAIRE: intrigue_questionnaire,
        Labels.RELATIONS_BI: intrigue_relations_bi,
        Labels.RELATIONS_MULTI: intrigue_relations_multi
    }

    for label in Labels:
        if indexes[label.value]["debut"] == -1:
            print(f"pas de {label.value} avec l'intrigue {nom_intrigue}")
        else:
            ma_methode = dict_methodes[label]
            texte = texte_intrigue[indexes[label.value]["debut"]:indexes[label.value]["fin"]]
            # print(f"debug : texte label {label.value} = {texte}")
            ma_methode(texte, current_intrigue, label.value)

    return current_intrigue


def intrigue_referent(texte: str, intrigue: Intrigue, texte_label: str):
    intrigue.orga_referent = retirer_label(texte, texte_label)


def intrigue_todo(texte: str, intrigue: Intrigue, texte_label: str):
    intrigue.questions_ouvertes = retirer_label(texte, texte_label)


def intrigue_croisee(texte: str, intrigue: Intrigue, texte_label: str):
    logging.debug(f"balise {texte_label} non prise en charge = {texte}")


def intrigue_pitch(texte: str, intrigue: Intrigue, texte_label: str):
    intrigue.pitch = retirer_premiere_ligne(texte)


def intrigue_pjs(texte: str, current_intrigue: Intrigue, texte_label: str):
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

    dict_headers = generer_dict_header_vers_no_colonne(en_tetes=tableau_pjs[0],
                                                       noms_colonnes=[nom_col.value for nom_col in NomsColonnes],
                                                       erreur_manager=current_intrigue.error_log)
    # noms_colonnes = [nc.value for nc in NomsColonnes]
    # headers = tableau_pjs[0]
    # dict_headers = generer_dict_header_vers_no_colonne(headers, noms_colonnes, current_intrigue.error_log)

    grille_types_persos = {"PJ": TypePerso.EST_PJ,
                           "PNJ": TypePerso.EST_PNJ_HORS_JEU,
                           "Reroll": TypePerso.EST_REROLL,
                           "PNJ Infiltré": TypePerso.EST_PNJ_INFILTRE,
                           "PNJ Hors Jeu": TypePerso.EST_PNJ_HORS_JEU,
                           "PNJ Permanent": TypePerso.EST_PNJ_PERMANENT,
                           "PNJ Temporaire": TypePerso.EST_PNJ_TEMPORAIRE}

    for ligne in tableau_pjs[1:]:
        nom = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.NOM_PERSO.value, "rôle sans nom :(")
        logging.debug(f"value  ={NomsColonnes.NOM_PERSO.value}, nom = {nom}")
        description = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.DESCRIPTION.value, "")
        pipi = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP_I.value, 0)
        pipr = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP_R.value, 0)
        sexe = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.GENRE.value, "i")
        type_intrigue = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.TYPE_INTRIGUE.value, "")
        niveau_implication = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.IMPLICATION.value, "")
        pip_globaux = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP.value, 0)
        type_personnage_brut = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.TYPE_PERSONNAGE.value,
                                                              "PJ")
        type_personnage_brut = process.extractOne(type_personnage_brut, grille_types_persos.keys())[0]
        type_perso = grille_types_persos[type_personnage_brut]

        # nettoyage du nom
        nom = nom.split("http")[0].split('aka')[0]

        if len(liste_pips := str(pip_globaux).split('/')) == 2:
            pip_globaux = 0
            pipi = liste_pips[0] + pipi
            pipr = liste_pips[1] + pipr
        affectation = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.AFFECTATION.value, "")
        logging.debug(f"Tableau des headers : {dict_headers}")
        logging.debug(f"ligne = {ligne}")
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

    # if nb_colonnes == 4:
    #     lire_tableau_pj_chalacta(current_intrigue, tableau_pjs)
    # elif nb_colonnes == 5:
    #     lire_tableau_pj_5_colonnes(current_intrigue, tableau_pjs)
    # elif nb_colonnes == 6:
    #     lire_tableau_pj_6_colonnes(current_intrigue, tableau_pjs)
    # else:
    #     current_intrigue.error_log.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
    #                                               "Tableau des personnages dans l'intrigue non standard",
    #                                               ErreurManager.ORIGINES.SCENE)
    #     print("Erreur : tableau d'intrigue non standard")


def generer_dict_header_vers_no_colonne(en_tetes, noms_colonnes, erreur_manager: ErreurManager):
    """
    Associe les entêtes du tableau aux noms de colonnes prévus et renvoie un dictionnaire avec les correspondances.

    :param en_tetes: Liste des entêtes du tableau.
    :param noms_colonnes: Liste des noms de colonnes attendus.
    :param erreur_manager: Instance d'ErreurManager pour gérer les erreurs.
    :return: Dictionnaire avec les correspondances entre les entêtes et les noms de colonnes.
    """
    tab_rectifie = []
    min_score = 100
    pire_match = ""
    for head in en_tetes:
        score = process.extractOne(head, noms_colonnes)
        tab_rectifie.append(score[0])
        if score[1] < min_score:
            min_score = score[1]
            pire_match = score[0]
    logging.debug("lecture auto des tableaux :")
    for i in range(len(en_tetes)):
        logging.debug(f"{en_tetes[i]} > {tab_rectifie[i]}")
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
    return {en_tete: i for i, en_tete in enumerate(tab_rectifie)}


def en_tete_vers_valeur_dans_ligne(ligne_tableau: list[str], dict_header_vers_no_colonne: dict, header_value, default):
    """
    Récupère la valeur d'une colonne spécifique dans une ligne de tableau en utilisant le mappage des entêtes.

    :param ligne_tableau: Liste des valeurs de la ligne du tableau.
    :param dict_header_vers_no_colonne: Dictionnaire avec les correspondances entre les entêtes et les noms de colonnes.
    :param header_value: Entête de la colonne à rechercher.
    :param default: Valeur par défaut à renvoyer si l'entête n'est pas trouvée.
    :return: Valeur de la colonne correspondant à l'entête donnée ou la valeur par défaut si l'entête n'est pas trouvée.
    """
    logging.debug(f"header / table header {header_value} {dict_header_vers_no_colonne.get(header_value)}")
    logging.debug(f"ligne : {ligne_tableau}")
    debug_value = dict_header_vers_no_colonne.get(header_value)
    if debug_value is not None:
        logging.debug(f"pour la valeur {debug_value} : {ligne_tableau[debug_value]}")
    index = dict_header_vers_no_colonne.get(header_value)
    return ligne_tableau[index] if index is not None else default


def intrigue_pnjs(texte: str, current_intrigue: Intrigue, texte_label: str, seuil_type_perso=85):
    # tableau_pnjs, _ = reconstituer_tableau(texte)
    # # faire un tableau avec une ligne par PNJ
    # # print(f"tableau pnj décodé : {tableau_pnjs}")
    # for pnj in tableau_pnjs:
    #     # print(f"section pnj en cours de lecture : {pnj}")
    #     # print(f"taille = {len(pnj)}")
    #     # print(f"pnj en cours = {pnj}")
    #
    #     # 0 Nom duPNJ et / ou fonction :
    #     # 1 Intervention:(Permanente ou Temporaire)
    #     # 2 Type d’implication: (Active, Passive, Info, ou Objet)
    #     # 3 Résumé de l’implication
    #     pnj_a_ajouter = Role(current_intrigue, nom=pnj[0], description=pnj[3],
    #                          pj=TypePerso.EST_PNJ_HORS_JEU, niveau_implication=pnj[2],
    #                          perimetre_intervention=pnj[1])
    #
    #     # print("Je suis en train de regarder {0} et son implication est {1}"
    #     # .format(pnj_a_ajouter.nom, pnj[1].strip()))
    #
    #     # cherche ensuite le niveau d'implication du pj
    #     if pnj[1].lower().find('perman') > -1:
    #         # print(pnj_a_ajouter.nom + " est permanent !!")
    #         pnj_a_ajouter.pj = TypePerso.EST_PNJ_PERMANENT
    #     elif pnj[1].lower().find('infiltr') > -1:
    #         pnj_a_ajouter.pj = TypePerso.EST_PNJ_INFILTRE
    #         # print(pnj_a_ajouter.nom + " est temporaire !!")
    #     # elif pnj[1].strip().lower().find('temp') > -1:
    #     #     pnj_a_ajouter.pj = modeleGN.EST_PNJ_TEMPORAIRE
    #     #     # print(pnj_a_ajouter.nom + " est temporaire !!")
    #     elif len(pnj[1]) > 1:
    #         pnj_a_ajouter.pj = TypePerso.EST_PNJ_TEMPORAIRE
    #         # print(pnj_a_ajouter.nom + " est temporaire !!")
    #
    #     # sinon PNJ hors-jeu est la valeur par défaut : ne rien faire
    #
    #     # du coup, on peut l'ajouter aux intrigues
    #     current_intrigue.rolesContenus[pnj_a_ajouter.nom] = pnj_a_ajouter
    tableau_pnjs, nb_colonnes = reconstituer_tableau(texte, sans_la_premiere_ligne=False)

    if nb_colonnes == 0:
        texte_erreur = "le tableau des Rerolls est inexploitable"
        current_intrigue.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                          texte_erreur,
                                          ErreurManager.ORIGINES.SCENE)
        return

    header = tableau_pnjs[0]

    class NomsColonnes(Enum):
        AFFECTATION = "Affecté à"
        GENRE = "Genre"
        NOM_PERSO = "Nom du PNJ et/ou fonction"
        IMPLICATION = "Type d’implication"
        TYPE_INTRIGUE = "Type d’intrigue"
        DESCRIPTION = "Résumé de l’implication"
        TYPE_PERSONNAGE = "Intervention"

    noms_colonnes = [c.value for c in NomsColonnes]
    dict_headers = generer_dict_header_vers_no_colonne(header, noms_colonnes, current_intrigue.error_log)

    grille_types_persos = {"PNJ": TypePerso.EST_PNJ_HORS_JEU,
                           "PNJ Infiltré": TypePerso.EST_PNJ_INFILTRE,
                           "PNJ Hors Jeu": TypePerso.EST_PNJ_HORS_JEU,
                           "PNJ Permanent": TypePerso.EST_PNJ_PERMANENT,
                           "PNJ Temporaire": TypePerso.EST_PNJ_TEMPORAIRE}

    for pnj in tableau_pnjs[1:]:
        affectation = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.AFFECTATION.value, "")
        genre = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.GENRE.value, "i")
        nom = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.NOM_PERSO.value, "")
        implication = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.IMPLICATION.value, "")
        description = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.DESCRIPTION.value, "")
        type_personnage_brut = en_tete_vers_valeur_dans_ligne(pnj, dict_headers, NomsColonnes.TYPE_PERSONNAGE.value,
                                                              "PNJ Hors Jeu")
        score_type_perso = process.extractOne(type_personnage_brut, grille_types_persos.keys())

        if score_type_perso[1] < seuil_type_perso:
            type_perso = TypePerso.EST_PNJ_HORS_JEU
        else:
            type_personnage = score_type_perso[0]
            type_perso = grille_types_persos[type_personnage]

        pnj_a_ajouter = Role(current_intrigue,
                             nom=nom,
                             description=description,
                             pj=type_perso,
                             niveau_implication=implication,
                             perimetre_intervention=type_personnage_brut,
                             genre=genre,
                             affectation=affectation)

        # du coup, on peut l'ajouter aux intrigues
        current_intrigue.rolesContenus[pnj_a_ajouter.nom] = pnj_a_ajouter


def intrigue_rerolls(texte: str, current_intrigue: Intrigue, texte_label: str):
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
    headers = tableau_rerolls[0]
    dict_headers = generer_dict_header_vers_no_colonne(headers, noms_colonnes, current_intrigue.error_log)

    for ligne in tableau_rerolls[1:]:
        nom = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.NOM_PERSO.value, "rôle sans nom :(")
        logging.debug(f"value  ={NomsColonnes.NOM_PERSO.value}, nom = {nom}")
        description = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.DESCRIPTION.value, "")
        pipi = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP_I.value, 0)
        pipr = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP_R.value, 0)
        sexe = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.GENRE.value, "i")
        type_intrigue = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.TYPE_INTRIGUE.value, "")
        niveau_implication = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.IMPLICATION.value, "")
        pip_globaux = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.PIP.value, 0)

        if len(liste_pips := str(pip_globaux).split('/')) == 2:
            pip_globaux = 0
            pipi = liste_pips[0] + pipi
            pipr = liste_pips[1] + pipr
        affectation = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.AFFECTATION.value, "")
        logging.debug(f"Tableau des headers : {dict_headers}")
        logging.debug(f"ligne = {ligne}")
        logging.debug(f"lecture associée : "
                      f"{[nom, description, pipi, pipr, sexe, type_intrigue, niveau_implication, pip_globaux, affectation]}")
        role_a_ajouter = Role(current_intrigue,
                              nom=nom.split("http")[0],
                              description=description,
                              type_intrigue=type_intrigue,
                              niveau_implication=niveau_implication,
                              pipi=pipi,
                              pipr=pipr,
                              genre=sexe,
                              pip_globaux=pip_globaux,
                              affectation=affectation,
                              pj=TypePerso.EST_REROLL
                              )
        current_intrigue.rolesContenus[role_a_ajouter.nom] = role_a_ajouter


def intrigue_objets(texte: str, current_intrigue: Intrigue, texte_label: str):
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

    noms_colonnes = [nc.value for nc in NomsColonnes]
    headers = tab_objets[0]
    dict_headers = generer_dict_header_vers_no_colonne(headers, noms_colonnes, current_intrigue.error_log)

    # faire un tableau avec une ligne par objet
    for ligne in tab_objets[1:]:
        code = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.CODE.value, "")
        description = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.DESCRIPTION.value, "")
        fourni_par = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.FOURNI_PAR.value, "")
        emplacement_debut = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.START.value, "")
        special_effect_1 = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.FX.value, "")
        special_effect_2 = en_tete_vers_valeur_dans_ligne(ligne, dict_headers, NomsColonnes.RFID.value, "")
        special_effect = special_effect_1 + special_effect_2

        mon_objet = Objet(code=code,
                          description=description,
                          fourni_par=fourni_par,
                          emplacement_debut=emplacement_debut,
                          special_effect=special_effect)

        current_intrigue.objets.add(mon_objet)
        mon_objet.intrigue = current_intrigue
        #
        # mon_objet = None
        # if nb_colonnes == 4:
        #     mon_objet = Objet(description=objet[0].strip(),
        #                       special_effect=objet[1].strip() if objet[1].strip().lower() != "non" else '',
        #                       emplacement_debut=objet[2].strip(),
        #                       fourni_par=objet[3].strip())
        #     # if pnj[3].strip().lower() != "non":  # si on a mis non pour le RFID ca ne veut pas dire oui :)
        #     #     mon_objet.specialEffect = pnj[1].strip()
        #
        # elif nb_colonnes == 3:
        #     mon_objet = Objet(description=objet[0].strip(),
        #                       emplacement_debut=objet[1].strip(),
        #                       fourni_par=objet[2].strip())
        # elif nb_colonnes == 6:
        #     mon_objet = Objet(code=objet[0].strip(),
        #                       description=objet[1].strip(),
        #                       special_effect=objet[2].strip() if objet[2].strip().lower() != "non" else '',
        #                       emplacement_debut=objet[3].strip(),
        #                       fourni_par=objet[4].strip())
        # else:
        #     print(f"Erreur de format d'objet dans l'intrigue {current_intrigue.nom} : {mon_objet}")
        #
        # if mon_objet is not None:
        #     current_intrigue.objets.add(mon_objet)
        #     mon_objet.intrigue = current_intrigue


def intrigue_scenesfx(texte: str, intrigue: Intrigue, texte_label: str):
    # print(f" debug : texte fx = {texte}")
    tableau_evenements, nb_colonnes = reconstituer_tableau(texte)
    if nb_colonnes != 4:
        logging.debug(f" Problème avec le tableau évènement : {tableau_evenements}")
        return

    codes_raw = [ligne[0].strip() for ligne in tableau_evenements]
    intrigue.codes_evenements_raw = codes_raw


def intrigue_timeline(texte: str, intrigue: Intrigue, texte_label: str):
    intrigue.timeline = retirer_premiere_ligne(texte)


def intrigue_scenes(texte: str, intrigue: Intrigue, texte_label: str):
    texte = retirer_label(texte, texte_label)
    texte2scenes(intrigue, intrigue.nom, texte)


def intrigue_resolution(texte: str, intrigue: Intrigue, texte_label: str):
    intrigue.resolution = retirer_premiere_ligne(texte)


def intrigue_notes(texte: str, intrigue: Intrigue, texte_label: str):
    intrigue.notes = retirer_premiere_ligne(texte)


def intrigue_questionnaire(texte: str, intrigue: Intrigue, texte_label: str):
    # intrigue.questionnaire = retirer_premiere_ligne(texte)
    tab_intrigues, nb_colonnes = reconstituer_tableau(texte, sans_la_premiere_ligne=True)
    if nb_colonnes != 2:
        texte_erreur = "le tableau questionnaire est inexploitable"
        intrigue.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                  texte_erreur,
                                  ErreurManager.ORIGINES.SCENE)
    intrigue.questionnaire = tab_intrigues


def intrigue_relations_bi(texte: str, intrigue: Intrigue, texte_label: str):
    tab_relations_bi, _ = reconstituer_tableau(texte)
    extraire_relations_bi(intrigue, tab_relations_bi)


def intrigue_relations_multi(texte: str, intrigue: Intrigue, texte_label: str):
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
            conteneur.get_noms_roles(),
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
        tab_retour_multi = qui_2_roles(noms_roles, conteneur,
                                       conteneur.get_noms_roles(), avec_tableau_des_persos)
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

# deprecated depuis que le tableau est lu dynamiquement
# def lire_tableau_pj_chalacta(current_intrigue, tableau_pjs):
#     for pj in tableau_pjs:  # on commence en 1 pour éviter de prendre la première ligne
#         # print("taille du prochain PJ : " +str(len(pj)))
#
#         if len(pj) < 4:  # testé pour éviter de se taper les lignes vides après le tableau
#             continue
#
#         role_a_ajouter = Role(current_intrigue,
#                               nom=pj[0].split("http")[0],
#                               description=pj[3],
#                               type_intrigue=pj[2],
#                               niveau_implication=pj[1]
#                               )
#         current_intrigue.rolesContenus[role_a_ajouter.nom] = role_a_ajouter
#
#
# def lire_tableau_pj_5_colonnes(current_intrigue, tableau_pjs):
#     for pj in tableau_pjs:  # on commence en 1 pour éviter de prendre la première ligne
#         # print("taille du prochain PJ : " +str(len(pj)))
#
#         if len(pj) < 5:  # testé pour éviter de se taper les lignes vides après le tableau
#             continue
#
#         liste_pips = pj[1].split('/')
#         if len(liste_pips) == 2:
#             pip_globaux = 0
#             pipi = liste_pips[0]
#             pipr = liste_pips[1]
#         else:
#             pip_globaux = liste_pips[0]
#             pipi = 0
#             pipr = 0
#
#         role_a_ajouter = Role(current_intrigue,
#                               nom=pj[0].split("http")[0],
#                               description=pj[4],
#                               type_intrigue=pj[3],
#                               niveau_implication=pj[2],
#                               pip_globaux=pip_globaux,
#                               pipi=pipi,
#                               pipr=pipr
#                               )
#         current_intrigue.rolesContenus[role_a_ajouter.nom] = role_a_ajouter
#
#
# def lire_tableau_pj_6_colonnes(current_intrigue, tableau_pjs):
#     for pj in tableau_pjs:
#         # print("taille du prochain PJ : " + str(len(pj)))
#
#         if len(pj) < 6:  # testé pour éviter de se taper les lignes vides après le tableau
#             continue
#
#         role_a_ajouter = Role(current_intrigue,
#                               nom=pj[0].split("http")[0],
#                               description=pj[5],
#                               type_intrigue=pj[4],
#                               niveau_implication=pj[3],
#                               pipi=pj[1],
#                               pipr=pj[2]
#                               )
#         current_intrigue.rolesContenus[role_a_ajouter.nom] = role_a_ajouter


# def texte2scenes(conteneur: ConteneurDeScene, nom_conteneur, texte_scenes, tableau_roles_existant=True):
#     # à ce stade là on a et les PJs et les PNJs > on peut générer le tableau de référence des noms dans l'intrigue
#     noms_roles = conteneur.get_noms_roles()
#     # print(f"pour {currentIntrigue.nom}, noms_roles =  {noms_roles}")
#
#     # print(f"Texte section scène : {texteScenes}")
#     scenes = texte_scenes.split("###")
#     for scene in scenes:
#         # print("taille de la scène : " + str(len(scene)))
#         if len(scene) < 10:
#             continue
#
#         titre_scene = scene.splitlines()[0].strip()
#         scene_a_ajouter = conteneur.ajouter_scene(titre_scene)
#         scene_a_ajouter.modifie_par = conteneur.modifie_par
#         # print("titre de la scène ajoutée : " + scene_a_ajouter.titre)
#         # print(f"Pour sandrine : extraction des balises pour l'intrigue {conteneur.nom}")
#         balises = re.findall(r'##.*', scene)
#         for balise in balises:
#             # print("balise : " + balise)
#             if balise[:9].lower() == '## quand?':
#                 extraire_date_scene(balise[10:], scene_a_ajouter)
#             elif balise[:10].lower() == '## quand ?':
#                 extraire_date_scene(balise[11:], scene_a_ajouter)
#                 # scene_a_ajouter.date = balise[11:].strip()
#                 # # print("date de la scène : " + scene_a_ajouter.date)
#             elif balise[:9].lower() == '## il y a':
#                 extraire_il_y_a_scene(balise[10:], scene_a_ajouter)
#             elif balise[:9].lower() == '## date :':
#                 extraire_date_absolue(balise[10:], scene_a_ajouter)
#             elif balise[:8].lower() == '## date:':
#                 extraire_date_absolue(balise[9:], scene_a_ajouter)
#             elif balise[:8].lower() == '## date?':
#                 extraire_date_absolue(balise[9:], scene_a_ajouter)
#             elif balise[:7].lower() == '## qui?':
#                 extraire_qui_scene(balise[8:], conteneur, noms_roles, scene_a_ajouter,
#                                    avec_tableau_des_persos=tableau_roles_existant)
#
#             elif balise[:8].lower() == '## qui ?':
#                 extraire_qui_scene(balise[9:], conteneur, noms_roles, scene_a_ajouter,
#                                    avec_tableau_des_persos=tableau_roles_existant)
#
#             elif balise[:11].lower() == '## niveau :':
#                 scene_a_ajouter.niveau = balise[12:].strip()
#
#             elif balise[:11].lower() == '## résumé :':
#                 scene_a_ajouter.resume = balise[12:].strip()
#
#             elif balise[:10].lower() == '## résumé:':
#                 scene_a_ajouter.resume = balise[11:].strip()
#
#             elif balise[:13].lower() == '## factions :':
#                 extraire_factions_scene(balise[14:], scene_a_ajouter)
#
#             elif balise[:12].lower() == '## faction :':
#                 extraire_factions_scene(balise[13:], scene_a_ajouter)
#
#             elif balise[:12].lower() == '## factions:':
#                 # scene_a_ajouter.nom_factions.add([f.strip() for f in balise[13:].split(',')])
#                 extraire_factions_scene(balise[13:], scene_a_ajouter)
#             elif balise[:11].lower() == '## faction:':
#                 # scene_a_ajouter.nom_factions.add([f.strip() for f in balise[12:].split(',')])
#                 extraire_factions_scene(balise[12:], scene_a_ajouter)
#             elif balise[:9].lower() == '## info :':
#                 extraire_infos_scene(balise[10:], scene_a_ajouter)
#                 # scene_a_ajouter.infos.add(tuple([f.strip() for f in .split(',')]))
#             elif balise[:8].lower() == '## info:':
#                 # scene_a_ajouter.infos.add([f.strip() for f in balise[9:].split(',')])
#                 extraire_infos_scene(balise[9:], scene_a_ajouter)
#             else:
#                 texte_erreur = f"balise inconnue : {balise} dans le conteneur {nom_conteneur}"
#                 print(texte_erreur)
#                 scene_a_ajouter.description += balise
#                 conteneur.error_log.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
#                                                    texte_erreur,
#                                                    ErreurManager.ORIGINES.SCENE)
#
#         scene_a_ajouter.description = ''.join(scene.splitlines(keepends=True)[1 + len(balises):])
#         # print("texte de la scene apres insertion : " + scene_a_ajouter.description)
def extraire_balise(balise, scene_a_ajouter, conteneur, noms_roles, tableau_roles_existant=True):
    balise_lower = balise.lower()
    if balise_lower.startswith('## quand?') or balise_lower.startswith('## quand ?'):
        extraire_date_scene(balise.split("?", 1)[1], scene_a_ajouter)
    elif balise_lower.startswith('## il y a'):
        extraire_il_y_a_scene(balise[9:], scene_a_ajouter)
    elif balise_lower.startswith('## date :') or balise_lower.startswith('## date:') or balise_lower.startswith(
            '## date?'):
        extraire_date_absolue(balise.split(":", 1)[1], scene_a_ajouter)
    elif balise_lower.startswith('## qui?') or balise_lower.startswith('## qui ?'):
        extraire_qui_scene(balise.split("?", 1)[1], conteneur, noms_roles, scene_a_ajouter,
                           avec_tableau_des_persos=tableau_roles_existant)
    elif balise_lower.startswith('## niveau :'):
        scene_a_ajouter.niveau = balise[11:].strip()
    elif balise_lower.startswith('## résumé :') or balise_lower.startswith('## résumé:'):
        scene_a_ajouter.resume = balise.split(":", 1)[1].strip()
    elif balise_lower.startswith('## factions :') or balise_lower.startswith('## factions:') or balise_lower.startswith(
            '## faction :') or balise_lower.startswith('## faction:'):
        extraire_factions_scene(balise.split(":", 1)[1], scene_a_ajouter)
    elif balise_lower.startswith('## info :') or balise_lower.startswith('## info:'):
        extraire_infos_scene(balise.split(":", 1)[1], scene_a_ajouter)
    else:
        return False
    return True


def texte2scenes(conteneur: ConteneurDeScene, nom_conteneur, texte_scenes, tableau_roles_existant=True):
    noms_roles = conteneur.get_noms_roles()
    scenes = texte_scenes.split("###")

    for scene in scenes:
        if len(scene) < 10:
            continue

        titre_scene = scene.splitlines()[0].strip()
        scene_a_ajouter = conteneur.ajouter_scene(titre_scene)
        scene_a_ajouter.modifie_par = conteneur.modifie_par

        balises = re.findall(r'##.*', scene)
        for balise in balises:
            if not extraire_balise(balise, scene_a_ajouter, conteneur, noms_roles, tableau_roles_existant):
                texte_erreur = f"balise inconnue : {balise} dans le conteneur {nom_conteneur}"
                print(texte_erreur)
                scene_a_ajouter.description += balise
                conteneur.error_log.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                   texte_erreur,
                                                   ErreurManager.ORIGINES.SCENE)

        scene_a_ajouter.description = ''.join(scene.splitlines(keepends=True)[1 + len(balises):])


def extraire_factions_scene(texte_lu: str, scene: Scene):
    for section in texte_lu.split(','):
        if len(section.strip()) > 1:
            scene.nom_factions.add(section.strip())


def extraire_infos_scene(texte_lu: str, scene: Scene):
    for section in texte_lu.split(','):
        if len(section) > 1:
            scene.infos.add(section.strip())


def extraire_qui_scene(liste_noms, conteneur, noms_roles, scene_a_ajouter, verbal=True, seuil=80,
                       avec_tableau_des_persos: bool = True):
    roles = [r.strip() for r in liste_noms.split(",") if len(r.strip()) > 0]
    scene_a_ajouter.noms_roles_lus = roles

    tab_corr = qui_2_roles(roles, conteneur, noms_roles, avec_tableau_des_persos)
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
            role_a_ajouter.ajouter_a_scene(scene_a_ajouter)
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


def qui_2_roles(roles: list[str], conteneur: ConteneurDeScene, noms_roles_dans_conteneur: list[str],
                avec_tableau_des_persos: bool = True):
    to_return = []  # nom, role,score
    # print("rôles trouvés en lecture brute : " + str(roles))

    if not avec_tableau_des_persos:
        # todo : remplacer l'ajout systématique de perso par une recherche avec processone et un ajout si KO

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

    # dans ce cas, on prend les noms du tableau, qui font fois, et on s'en sert pour identifier
    # les noms de la scène
    for nom_du_role in roles:
        if len(nom_du_role) < 2:
            continue

        # Sinon, il faut normaliser et extraire les rôles
        # pour chaque nom de la liste : retrouver le nom le plus proche dans la liste des noms du GN
        score = process.extractOne(nom_du_role.strip(), noms_roles_dans_conteneur)
        # print("nom normalisé du personnage {0} trouvé dans une scène de {1} : {2}".format(nom_du_role.strip(),
        #                                                                                   conteneur.nom,
        #                                                                                   score))

        if score is not None:
            # trouver le rôle à ajouter à la scène en lisant l'intrigue
            mon_role = conteneur.rolesContenus[score[0]]
            to_return.append([nom_du_role, mon_role, score[1]])
        else:
            to_return.append([nom_du_role, None, 0])

    return to_return


def extraire_date_scene(balise_date, scene_a_ajouter):
    # réécrite pour merger les fonctions il y a et quand :
    # réécrite pour merger les fonctions il y a et quand :

    # est-ce que la date est écrite au format quand ? il y a ?
    if balise_date.strip().lower()[:6] == 'il y a':
        # print(f" 'quand il y a' trouvée : {balise_date}")
        return extraire_il_y_a_scene(balise_date.strip()[7:], scene_a_ajouter)
    else:
        scene_a_ajouter.date = balise_date.strip()
    # print("date de la scène : " + scene_a_ajouter.date)


def extraire_il_y_a_scene(balise_date, scene_a_ajouter):
    # print("balise date : " + balise_date)
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
        # print(f"balise date il y a en sortie {date_en_jours}")

        return date_en_jours
    except ValueError:
        print(f"Erreur avec la date {balise_date}")
        return balise_date.strip()


def extraire_evenement_de_texte(texte_evenement: str, nom_evenement: str, id_url: str, lastFileEdit,
                                derniere_modification_par: str, dict_evenements, verbal=False):
    # print("je suis entré dans  la création d'un évènement")
    # Créer un nouvel évènement
    nom_evenement_en_cours = re.sub(r"^\d+\s*-", '', nom_evenement).strip()

    current_evenement = Evenement(nom_evenement=nom_evenement_en_cours,
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
    indexes = lecteurGoogle.identifier_sections_fiche(labels, texte_evenement.lower())

    # utliser un dictionnaire pour savoir quelle section lire
    dict_methodes = {
        Labels.FICHE: evenement_lire_fiche,
        Labels.SYNOPSIS: evenement_lire_synopsis,
        Labels.LIES: evenement_lire_lies,
        Labels.BRIEFS: evenement_lire_briefs,
        Labels.INFOS_PJS: evenement_lire_infos_pj,
        Labels.INFOS_FACTIONS: evenement_infos_factions,
        Labels.OBJETS: evenement_lire_objets,
        Labels.CHRONO: evenement_lire_chrono,
        Labels.AUTRES: evenement_lire_autres
    }

    # lire les sections dans le fichier et appliquer la bonne méthode
    for label in Labels:
        if indexes[label.value]["debut"] == -1:
            if label != Labels.CHRONO:
                print(f"pas de {label.value} avec l'évènement {nom_evenement_en_cours}")
                texte_erreur = f"Le label {label.value} n'a pas été trouvé"
                current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                                texte_erreur,
                                                                ErreurManager.ORIGINES.LECTURE_EVENEMENT)

        else:
            texte_section = texte_evenement[indexes[label.value]["debut"]:indexes[label.value]["fin"]]
            methode_a_appliquer = dict_methodes[label]
            methode_a_appliquer(texte_section, current_evenement, label.value)
    # on vérifie ensuite qu'on a bien une chrono, sinon on la force et elle sera remplie par défaut
    if indexes[Labels.CHRONO.value]["debut"] == -1:
        # dans ce cas on reconstruit un tableau de toute pièce en appelant lire_chono_tableau avec non comme argument

        evenement_lire_chrono_depuis_tableau(current_evenement=current_evenement)

        texte_erreur = "Le tableau des interventions n'a pas été trouvé " \
                       "> les informations de l'évènement (jour, date, tous les pjs, tous les pnjs, synopsys) " \
                       "ont été reprises"
        current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.INFO,
                                                        texte_erreur,
                                                        ErreurManager.ORIGINES.LECTURE_EVENEMENT)


def evenement_lire_fiche(texte: str, current_evenement: Evenement, texte_label: str):
    texte = retirer_premiere_ligne(texte)
    tableau_fiche, nb_colonnes = reconstituer_tableau(texte, sans_la_premiere_ligne=False)
    # print(f"debug : tableau fiche évènement {current_evenement.nom_evenement}, {tableau_fiche} ")
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
    # print(f"debug : dict fiche = {dict_fiche}")
    # current_evenement.code_evenement = ''.join([dict_fiche.get(key, "").strip()
    #                                             for key in dict_fiche
    #                                             if key.startswith("Code")])
    # current_evenement.etat = dict_fiche.get("État", "").strip()
    # current_evenement.referent = dict_fiche.get("Référent", "").strip()
    # current_evenement.intrigue_liee = dict_fiche.get("Intrigue liée", "").strip()
    # current_evenement.lieu = dict_fiche.get("Lieu", "").strip()
    # current_evenement.date = dict_fiche.get('Jour, au format “J1”, “J2”, etc.', "").strip()
    # current_evenement.heure_de_demarrage = dict_fiche.get("Heure de démarrage", "").strip()
    # current_evenement.declencheur = dict_fiche.get("Déclencheur", "").strip()
    # current_evenement.consequences_evenement = ''.join([dict_fiche.get(key, "").strip()
    #                                                     for key in dict_fiche
    #                                                     if key.startswith("Conséquences ")])

    # print(f"debug : tableau évènement après modification : {dict_fiche}")

    current_evenement.code_evenement = dict_fiche.get(NomsLignes.CODE.value, "").strip()
    current_evenement.etat = dict_fiche.get(NomsLignes.ETAT.value, "").strip()
    current_evenement.referent = dict_fiche.get(NomsLignes.REFERENT.value, "").strip()
    current_evenement.intrigue_liee = dict_fiche.get(NomsLignes.INTRIGUE_LIEE.value, "").strip()
    current_evenement.lieu = dict_fiche.get(NomsLignes.LIEU.value, "").strip()
    current_evenement.date = dict_fiche.get(NomsLignes.JOUR.value, "").strip()
    current_evenement.heure_de_demarrage = dict_fiche.get(NomsLignes.HEURE_DEBUT.value, "").strip()
    current_evenement.heure_de_fin = dict_fiche.get(NomsLignes.HEURE_FIN.value, "").strip()
    current_evenement.declencheur = dict_fiche.get(NomsLignes.DECLENCHEUR.value, "").strip()
    current_evenement.consequences_evenement = dict_fiche.get(NomsLignes.CONSEQUENCES.value, "").strip()


def evenement_lire_synopsis(texte: str, current_evenement: Evenement, texte_label: str):
    current_evenement.synopsis = '\n'.join(texte.splitlines()[1:])


def evenement_lire_lies(texte: str, current_evenement: Evenement, texte_label: str):
    logging.debug(f"balise {texte_label} non prise en charge = {texte}")


def evenement_lire_briefs(texte: str, current_evenement: Evenement, texte_label: str):
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


def evenement_lire_infos_pj(texte: str, current_evenement: Evenement, texte_label: str):
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


def evenement_infos_factions(texte: str, current_evenement: Evenement, texte_label: str):
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


def evenement_lire_objets(texte: str, current_evenement: Evenement, texte_label: str):
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


def evenement_lire_chrono(texte: str, current_evenement: Evenement, texte_label: str,
                          seuil_alerte_pnj=70, seuil_alerte_pj=70):
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
                                                current_evenement=current_evenement,
                                                seuil_alerte_pnj=seuil_alerte_pnj,
                                                seuil_alerte_pj=seuil_alerte_pj)


def evenement_lire_chrono_depuis_tableau(current_evenement: Evenement,
                                         tableau_interventions: list = None, nb_colonnes: int = 0,
                                         seuil_alerte_pnj=70, seuil_alerte_pj=70):
    class NomsColonnes(Enum):
        JOUR = "jour"
        HEURE_DEBUT = "heure début"
        HEURE_FIN = "heure fin"
        PNJs = "pnjs"
        PJs = "pjs impliqués"
        QUOI = "quoi?"

    colonnes = [nc.value for nc in NomsColonnes]

    # si on est entré avec les paramètres apr défaut, dans ce cas le tableau est à reconstruire en '',
    # pour recopier plus tard ceux de l'évènement
    if tableau_interventions is None or nb_colonnes == 0:
        nb_colonnes = len(colonnes)
        tableau_interventions = [colonnes, [''] * nb_colonnes]

    if not 1 <= nb_colonnes <= len(colonnes):
        logging.debug(f"format incorrect de tableau le la chronologie des évènements : {tableau_interventions}")
        texte_erreur = "format incorrect de tableau pour Chronologie de l'évènement"
        current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                        texte_erreur,
                                                        ErreurManager.ORIGINES.LECTURE_EVENEMENT)
        return
    # du coup si le nombre de colonnes est bon mais que la longueur est nulle, le tableau est vide
    # il faut donc le remplir
    if len(tableau_interventions) == 1:
        tableau_interventions.append([''] * nb_colonnes)
        texte_erreur = "Le tableau des interventions a été trouvé, mais ne contenait aucune ligne " \
                       "> les informations de l'évènement (jour, date, tous les pjs, tous les pnjs, synopsys) " \
                       "ont été reprises"
        current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.INFO,
                                                        texte_erreur,
                                                        ErreurManager.ORIGINES.LECTURE_EVENEMENT)
        # print(f"debug : {tableau_interventions} pour l'evènement {current_evenement.nom_evenement}")

    dict_header_vers_no_colonne = generer_dict_header_vers_no_colonne(en_tetes=tableau_interventions[0],
                                                                      noms_colonnes=colonnes,
                                                                      erreur_manager=current_evenement.erreur_manager,
                                                                      )
    for ligne in tableau_interventions[1:]:
        evenement_extraire_ligne_chrono(current_evenement, ligne, dict_header_vers_no_colonne, NomsColonnes,
                                        seuil_alerte_pj, seuil_alerte_pnj)


def evenement_extraire_ligne_chrono(current_evenement: Evenement, ligne, dict_header_vers_no_colonne: dict,
                                    noms_colonnes,
                                    seuil_alerte_pj, seuil_alerte_pnj):
    # print(f"debug : "
    #       f"Je suis en train de lire une internventionde de l'évènement {current_evenement.code_evenement}, "
    #       f"et ma ligne est  = {ligne}")
    jour = en_tete_vers_valeur_dans_ligne(ligne,
                                          dict_header_vers_no_colonne,
                                          noms_colonnes.JOUR.value,
                                          '')
    heure_debut = en_tete_vers_valeur_dans_ligne(ligne,
                                                 dict_header_vers_no_colonne,
                                                 noms_colonnes.HEURE_DEBUT.value,
                                                 '')
    heure_fin = en_tete_vers_valeur_dans_ligne(ligne,
                                               dict_header_vers_no_colonne,
                                               noms_colonnes.HEURE_FIN.value,
                                               '')
    pnjs_raw = en_tete_vers_valeur_dans_ligne(ligne,
                                              dict_header_vers_no_colonne,
                                              noms_colonnes.PNJs.value,
                                              '')
    pj_raw = en_tete_vers_valeur_dans_ligne(ligne,
                                            dict_header_vers_no_colonne,
                                            noms_colonnes.PJs.value,
                                            '')

    description = en_tete_vers_valeur_dans_ligne(ligne,
                                                 dict_header_vers_no_colonne,
                                                 noms_colonnes.QUOI.value,
                                                 '')

    # print(f"debug : "
    #       f"après correction, j'ai les données suivantes : "
    #       f"jour={jour if jour != '' else current_evenement.date},"
    #       f"heure_debut={heure_debut if heure_debut != '' else current_evenement.heure_de_demarrage},"
    #       f"heure_fin={heure_fin if heure_fin != '' else current_evenement.heure_de_fin}, "
    #       f"description={description if description != '' else current_evenement.synopsis},"
    #       )

    intervention = Intervention(jour=jour if jour != '' else current_evenement.date,
                                heure_debut=heure_debut if heure_debut != '' else current_evenement.heure_de_demarrage,
                                heure_fin=heure_fin if heure_fin != '' else current_evenement.heure_de_fin,
                                description=description if description != '' else current_evenement.synopsis,
                                evenement=current_evenement
                                )
    # intervention = Intervention(jour=ligne[0] if ligne[0] != '' else current_evenement.date,
    #                             heure=ligne[1] if ligne[1] != '' else current_evenement.heure_de_demarrage,
    #                             description=ligne[4] if ligne[4] != '' else current_evenement.synopsis,
    #                             evenement=current_evenement
    #                             )
    noms_pnjs_impliques = [nom.strip() for nom in pnjs_raw.split(',')]
    noms_pnjs_dans_evenement = current_evenement.get_noms_pnjs()
    # print(f"debug : {len(current_evenement.interventions)} interventions "
    #       f"dans l'evènement {current_evenement.id_url}")

    current_evenement.interventions.append(intervention)
    # print(f"debug : apres ajout de l'intervention {intervention.description} dans l'évènement "
    #       f"{current_evenement.nom_evenement} / {current_evenement.code_evenement}, "
    #       f"celui ci contient {len(current_evenement.interventions)} interventions")
    if noms_pnjs_impliques == ['']:
        intervention.liste_intervenants.extend(current_evenement.intervenants_evenement.values())
    else:
        for nom_pnj in noms_pnjs_impliques:
            score = process.extractOne(nom_pnj, noms_pnjs_dans_evenement)
            if score is None:
                texte_erreur = f"Correspondance introuvable pour le nom {nom_pnj} avec la table des PNJs" \
                               f"dans l'évènement {current_evenement.code_evenement} " \
                               f"/ {current_evenement.nom_evenement} " \
                               f"pour l'intervention {intervention.description}"
                current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                                texte_erreur,
                                                                ErreurManager.ORIGINES.CHRONO_EVENEMENT)
                # print(f"debug : {texte_erreur}")
                continue

            if score[1] < seuil_alerte_pnj:
                texte_erreur = f"Le nom du pnj {nom_pnj} trouvé dans la chronologie de l'évènement " \
                               f"a été associé à {score[0]} à seulement {score[1]}% de confiance"
                current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                                texte_erreur,
                                                                ErreurManager.ORIGINES.CHRONO_EVENEMENT)
            intervenant = current_evenement.intervenants_evenement[score[0]]
            intervention.liste_intervenants.append(intervenant)
    for intervenant in intervention.liste_intervenants:
        intervenant.interventions.add(intervention)

    noms_pj_impliques = [nom.strip() for nom in pj_raw.split(',')]
    noms_pjs_dans_evenement = current_evenement.get_noms_pjs()
    if noms_pj_impliques == ['']:
        intervention.liste_pjs_concernes.extend(current_evenement.pjs_concernes_evenement.values())
    else:
        for nom_pj in noms_pj_impliques:
            score = process.extractOne(nom_pj, noms_pjs_dans_evenement)
            if score is None:
                texte_erreur = f"Correspondance introuvable pour le nom {nom_pj} " \
                               f"dans l'évènement {current_evenement.code_evenement} avec la table des PJs" \
                               f"/ {current_evenement.nom_evenement}" \
                               f"pour l'intervention {intervention.description}"
                current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                                texte_erreur,
                                                                ErreurManager.ORIGINES.CHRONO_EVENEMENT)
                # print(f"debug : {texte_erreur}")
                continue

            if score[1] < seuil_alerte_pj:
                texte_erreur = f"Le nom du pj {nom_pj} trouvé dans la chronologie de l'évènement " \
                               f"a été associé à {score[0]} à seulement {score[1]}% de confiance"
                current_evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                                texte_erreur,
                                                                ErreurManager.ORIGINES.CHRONO_EVENEMENT)
            pj_concerne = current_evenement.pjs_concernes_evenement[score[0]]
            intervention.liste_pjs_concernes.append(pj_concerne)


# def ajouter_intervenants(noms, intervenants_dans_evenement, seuil_alerte, intervention, erreur_manager):
#     for nom in noms:
#         score = process.extractOne(nom, intervenants_dans_evenement)
#         if score is None:
#             texte_erreur = f"Correspondance introuvable pour le nom {nom} avec la table des intervenants"
#             erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR, texte_erreur,
#                                           ErreurManager.ORIGINES.CHRONO_EVENEMENT)
#             continue
#
#         if score[1] < seuil_alerte:
#             texte_erreur = f"Le nom {nom} trouvé dans la chronologie a été associé à {score[0]} à seulement {score[1]}% de confiance"
#             erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING, texte_erreur,
#                                           ErreurManager.ORIGINES.CHRONO_EVENEMENT)
#
#         intervenant = intervenants_dans_evenement[score[0]]
#         intervention.liste_intervenants.append(intervenant)
#
#
# def evenement_extraire_ligne_chrono(current_evenement: Evenement, ligne, seuil_alerte_pj, seuil_alerte_pnj):
#     intervention = Intervention(jour=ligne[0] if ligne[0] != '' else current_evenement.date,
#                                 heure=ligne[1] if ligne[1] != '' else current_evenement.heure_de_demarrage,
#                                 description=ligne[4] if ligne[4] != '' else current_evenement.synopsis,
#                                 evenement=current_evenement
#                                 )
#     current_evenement.interventions.append(intervention)
#
#     noms_pnjs_impliques = [nom.strip() for nom in ligne[2].split(',')]
#     noms_pnjs_dans_evenement = current_evenement.get_noms_pnjs()
#     noms_pj_impliques = [nom.strip() for nom in ligne[3].split(',')]
#     noms_pjs_dans_evenement = current_evenement.get_noms_pjs()
#
#     if noms_pnjs_impliques == ['']:
#         intervention.liste_intervenants.extend(current_evenement.intervenants_evenement.values())
#     else:
#         ajouter_intervenants(noms_pnjs_impliques, noms_pnjs_dans_evenement, seuil_alerte_pnj, intervention,
#                              current_evenement.erreur_manager)
#
#     if noms_pj_impliques == ['']:
#         intervention.liste_pjs_concernes.extend(current_evenement.pjs_concernes_evenement.values())
#     else:
#         ajouter_intervenants(noms_pj_impliques, noms_pjs_dans_evenement, seuil_alerte_pj, intervention,
#                              current_evenement.erreur_manager)
#
#     for intervenant in intervention.liste_intervenants:
#         intervenant.interventions.add(intervention)


def evenement_lire_autres(texte: str, current_evenement: Evenement, texte_label: str):
    logging.debug(f"balise {texte_label} non prise en charge = {texte}")


def retirer_premiere_ligne(texte: str):
    return '\n'.join(texte.splitlines()[1:])


def retirer_label(texte: str, label: str):
    return texte[len(label):].strip()


def extraire_pnj_de_texte(texte_persos, nom_doc, id_url, last_file_edit, derniere_modification_par, dict_pnj,
                          verbal):
    return extraire_persos_de_texte(texte_persos, nom_doc, id_url, last_file_edit, derniere_modification_par, dict_pnj,
                                    verbal=verbal, pj=TypePerso.EST_PNJ_HORS_JEU)


def extraire_persos_de_texte(texte_persos, nom_doc, id_url, last_file_edit, derniere_modification_par, dict_pj_pnj,
                             verbal=False, pj: TypePerso = TypePerso.EST_PJ):
    print(f"Lecture de {nom_doc}")
    if len(texte_persos) < 800:
        print(f"fiche {nom_doc} avec {len(texte_persos)} caractères est vide")
        # return  # dans ce cas c'est qu'on est en train de lite un template, qui fait 792 cars
        # todo : si bug dans la lecture c'est lié à ici, pour accélérer la lecture

    nom_perso_en_cours = re.sub(r"^\d+\s*-", '', nom_doc).strip()
    # print(f"nomDoc =_{nomDoc}_ nomPJ =_{nomPJ}_")
    # print(f"Personnage en cours d'importation : {nomPJ} avec {len(textePJ)} caractères")
    perso_en_cours = Personnage(nom=nom_perso_en_cours, url=id_url, derniere_edition_fichier=last_file_edit, pj=pj)
    perso_en_cours.modifie_par = derniere_modification_par
    dict_pj_pnj[id_url] = perso_en_cours

    texte_persos_low = texte_persos.lower()  # on passe en minuscule pour mieux trouver les chaines

    class Labels(Enum):
        REFERENT = "orga référent : "
        JOUEUR = "joueur"
        JOUEUSE = "joueuse"
        INTERPRETE = "interprète"
        PITCH = "pitch personnage"
        COSTUME = "indications costumes : "
        FACTION1 = "faction principale : "
        FACTION2 = "faction secondaire : "
        GROUPES = "groupes : "
        BIO = "bio résumée"
        PSYCHO = "psychologie : "
        MOTIVATIONS = "motivations et objectifs"
        CHRONOLOGIE = "chronologie"
        INTRIGUES = "intrigues"
        RELATIONS = "relations avec les autres persos"
        SCENES = "scènes"
        RELATIONS_BI = "relations bilatérales"
        RELATIONS_MULTI = "relations multilatérales"

    labels = [label.value for label in Labels]

    indexes = lecteurGoogle.identifier_sections_fiche(labels, texte_persos_low)

    dict_methodes = {
        Labels.REFERENT: personnage_referent,
        Labels.JOUEUR: personnage_interprete,
        Labels.JOUEUSE: personnage_interprete,
        Labels.INTERPRETE: personnage_interprete,
        Labels.PITCH: personnage_pitch,
        Labels.COSTUME: personnage_costume,
        Labels.FACTION1: personnage_faction1,
        Labels.FACTION2: personnage_factions2,
        Labels.GROUPES: personnage_groupes,
        Labels.INTRIGUES: personnage_intrigues,
        Labels.BIO: personnage_bio,
        Labels.PSYCHO: personnage_psycho,
        Labels.MOTIVATIONS: personnage_motivation,
        Labels.CHRONOLOGIE: personnage_chronologie,
        Labels.SCENES: personnage_scenes,
        Labels.RELATIONS: personnage_relations,
        Labels.RELATIONS_BI: personnage_relations_bi,
        Labels.RELATIONS_MULTI: personnage_relations_multi
    }

    for label in Labels:
        if indexes[label.value]["debut"] == -1:
            print(f"pas de {label.value} avec le personnage {nom_perso_en_cours}")
        else:
            ma_methode = dict_methodes[label]
            texte = texte_persos[indexes[label.value]["debut"]:indexes[label.value]["fin"]]
            # print(f"debug : texte label {label.value} = {texte}")
            ma_methode(texte, perso_en_cours, label.value)

    # et on enregistre la date de dernière mise à jour de l'intrigue
    # perso_en_cours.lastProcessing = datetime.datetime.now()
    return perso_en_cours


def personnage_referent(texte: str, perso_en_cours: Personnage, text_label: str):
    perso_en_cours.orga_referent = retirer_label(texte, text_label)


# def personnage_joueurv1(texte: str, perso_en_cours: Personnage, text_label: str):
#     perso_en_cours.joueurs['V1'] = retirer_label(texte, text_label)
#

def personnage_relations(texte: str, perso_en_cours: Personnage, text_label: str):
    print(f"Balise {text_label} trouvée : cette balise n'est plus prise en compte")


def personnage_intrigues(texte: str, perso_en_cours: Personnage, text_label: str):
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


def personnage_pitch(texte: str, perso_en_cours: Personnage, text_label: str):
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


def personnage_bio(texte: str, perso_en_cours: Personnage, text_label: str):
    perso_en_cours.description = retirer_premiere_ligne(texte)


def personnage_psycho(texte: str, perso_en_cours: Personnage, text_label: str):
    perso_en_cours.concept = retirer_premiere_ligne(texte)


def personnage_motivation(texte: str, perso_en_cours: Personnage, text_label: str):
    perso_en_cours.driver = retirer_premiere_ligne(texte)


def personnage_chronologie(texte: str, perso_en_cours: Personnage, text_label: str):
    perso_en_cours.datesClefs = retirer_premiere_ligne(texte)


def personnage_relations_bi(texte: str, perso_en_cours: Personnage, text_label: str):
    tableau_relation_bi_brut, _ = reconstituer_tableau(texte)
    print(f"tab brut : {tableau_relation_bi_brut}")
    # comme on est dans une fiche perso, il est implicite que le perso fait partie de la relation : on l'ajoute donc
    tableau_relation_bi_complet = [[perso_en_cours.nom] + ligne for ligne in tableau_relation_bi_brut]
    extraire_relations_bi(perso_en_cours, tableau_relation_bi_complet, avec_tableau_persos=False)


def personnage_relations_multi(texte: str, perso_en_cours: Personnage, text_label: str):
    tableau_relation_multi_brut, _ = reconstituer_tableau(texte)

    # comme on est dans une fiche perso, il est implicite que le perso fait partie de la relation : on l'ajoute donc
    tableau_relation_multi_complet = []
    for ligne in tableau_relation_multi_brut:
        nouvelle_ligne = [f"{perso_en_cours.nom}, {ligne[0]}", ligne[1]]
        tableau_relation_multi_complet.append(nouvelle_ligne)
    extraire_relation_multi(perso_en_cours, tableau_relation_multi_complet, avec_tableau_des_persos=False)


def personnage_scenes(texte: str, perso_en_cours: Personnage, text_label: str):
    texte2scenes(perso_en_cours, perso_en_cours.nom, texte, tableau_roles_existant=False)


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
    objet_en_cours = ObjetDeReference(nom_objet=nom_objet_en_cours,
                                      code_objet=code_objet,
                                      id_url=id_url,
                                      derniere_edition_date=last_file_edit,
                                      derniere_edition_par=derniere_modification_par)
    dict_objets_de_reference[id_url] = objet_en_cours

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

    indexes = lecteurGoogle.identifier_sections_fiche(labels, texte_objets_low)

    dict_methodes = {
        Labels.REFERENT: objets_referent,
        Labels.INTRIGUE: objets_noms_intrigues,
        Labels.INTRIGUES: objets_noms_intrigues,
        Labels.UTILITE: objets_utilite,
        Labels.BUDGET: objets_budget,
        Labels.RECOMMANDATION: objets_recommandation,
        Labels.MATERIAUX: objets_materiaux,
        Labels.MOODBOARD: objets_moodboard,
        Labels.DESCRIPTION: objets_description,
        Labels.FX: objets_effets_speciaux
    }

    for label in Labels:
        if indexes[label.value]["debut"] == -1:
            print(f"pas de {label.value} avec l'objet {nom_objet_en_cours}")
        else:
            ma_methode = dict_methodes[label]
            texte = texte_objets[indexes[label.value]["debut"]:indexes[label.value]["fin"]]
            # print(f"debug : texte label {label.value} = {texte}")
            ma_methode(texte, objet_en_cours, label.value)

    # et on enregistre la date de dernière mise à jour de l'intrigue
    objet_en_cours.set_last_processing(datetime.datetime.now())
    return objet_en_cours


def objets_effets_speciaux(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.effets_speciaux = retirer_label(texte, texte_label)


def objets_referent(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.referent = retirer_label(texte, texte_label)


def objets_noms_intrigues(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    print(f"la balise {texte_label} n'a pas d'utilité pour MAGnet")


def objets_utilite(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.utilite = retirer_label(texte, texte_label)


def objets_budget(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.budget = retirer_label(texte, texte_label)


def objets_recommandation(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.recommandations = retirer_label(texte, texte_label)


def objets_materiaux(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    objet_en_cours.materiaux = retirer_label(texte, texte_label)


def objets_moodboard(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
    print(f"la balise {texte_label} n'a pas d'utilité pour MAGnet")


def objets_description(texte: str, objet_en_cours: ObjetDeReference, texte_label: str):
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
    # todo : réécrire et débugger

    # factions = mon_gn.factions.values()
    # for faction in factions:
    #     faction.personnages.clear()
    #     del faction
    # mon_gn.factions.clear()

    try:
        id_doc = mon_gn.get_id_factions()
        text = lire_google_doc(api_doc, id_doc)

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
    # temp_dict_pjs = {mon_gn.dictPJs[x].nom: x for x in mon_gn.dictPJs}
    # temp_dict_pnjs = {mon_gn.dictPNJs[x].nom: x for x in mon_gn.dictPNJs}
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
                # if temp_dict_pjs.get(score[0]):
                #     personnages_a_ajouter = mon_gn.dictPJs[temp_dict_pjs.get(score[0])]
                #     logging.info("et il venait des pjs")
                # else:
                #     personnages_a_ajouter = mon_gn.dictPNJs[temp_dict_pnjs.get(score[0])]
                #     logging.info("et il venait des pnjs")
                personnages_a_ajouter = mon_gn.personnages[dict_nom_id.get(score[0])]
                current_faction.personnages.add(personnages_a_ajouter)
    return 0


def lire_google_doc(api_doc, id_doc):
    document = api_doc.documents().get(documentId=id_doc).execute()
    contenu_document = document.get('body').get('content')
    text = lecteurGoogle.read_structural_elements(contenu_document)
    text = text.replace('\v', '\n')  # pour nettoyer les backspace verticaux qui se glissent
    return text


# def inserer_squelettes_dans_drive(parent_id: str, api_doc, api_drive, text: str, nom_fichier, titre=False, prefixe=""):
#     file_id = add_doc(api_drive, nom_fichier, parent_id, prefixe_message=prefixe)
#     write_to_doc(api_doc, file_id, text, titre=titre)
#     formatter_titres_scenes_dans_squelettes(api_doc, file_id)


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


# def ecrire_texte_et_tables(service, file_id: str, a_ecrire: list[dict], titre=False):
#
#     chunks = a_ecrire[::-1]
#     requests = []
#     for chunk in chunks:
#         if text := chunk.get('texte'):
#             requests.append({
#                 'insertText': {
#                     'location': {
#                         'index': 1
#                     },
#                     'text': text
#                 }
#             })
#         if table := chunk.get('table'):
#
#
#     try:
#         # Execute the request.
#         result = service.documents().batchUpdate(documentId=file_id, body={'requests': requests}).execute()
#         return result
#     except HttpError as error:
#         print(F'An error occurred: {error}')
#         return None


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





def creer_fichier(service_drive, nom_fichier: str, id_parent: str, type_mime: str, m_print=print, id_dossier_archive = None) -> Optional[str]:
    """Crée un fichier dans Google Drive avec un type MIME spécifique."""

    print(f"DEBUG  : fichier archive : {id_dossier_archive}")
    if id_dossier_archive:
        print("DEBUG  : fichier archive trouvé")
        archiver_fichiers_existants(service_drive, nom_fichier, id_parent, id_dossier_archive, considerer_supprime=False)
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

def creer_dossier_drive(service_drive, id_parent: str, nom_dossier: str, m_print=print, id_dossier_archive = None) -> Optional[str]:
    """Crée un dossier dans Google Drive."""
    TYPE_MIME_DOSSIER = 'application/vnd.google-apps.folder'
    return creer_fichier(service_drive, nom_dossier, id_parent, TYPE_MIME_DOSSIER, id_dossier_archive=id_dossier_archive)

def creer_google_sheet(service_drive, nom_feuille: str, id_dossier_parent: str, m_print=print, id_dossier_archive = None) -> Optional[str]:
    """Crée un document Google Sheets dans Google Drive."""
    TYPE_MIME_FEUILLE = 'application/vnd.google-apps.spreadsheet'
    return creer_fichier(service_drive, nom_feuille, id_dossier_parent, TYPE_MIME_FEUILLE, id_dossier_archive=id_dossier_archive)

def creer_google_doc(service_drive, nom_fichier: str, id_parent: str, m_print=print, id_dossier_archive = None) -> Optional[str]:
    """Crée un document Google Docs dans Google Drive."""
    TYPE_MIME_DOCUMENT = 'application/vnd.google-apps.document'
    return creer_fichier(service_drive, nom_fichier, id_parent, TYPE_MIME_DOCUMENT, id_dossier_archive=id_dossier_archive)


def archiver_fichiers_existants(service, nom_fichier, id_dossier_parent, id_dossier_archive, considerer_supprime=False):
    """
    Vérifie si des fichiers avec le même label existent et, le cas échéant, les déplace dans un dossier d'archives.

    Args:
        service (Resource): Le service Google Drive API.
        nom_fichier (str): Le nom du fichier à créer.
        id_dossier_parent (str): L'ID du dossier où chercher les fichiers.
        id_dossier_archive (str): L'ID du dossier où les fichiers seront archivés.
        considerer_supprime (bool): Si True, considère également les fichiers supprimés.
    """
    # Extraire la date-heure et le label du fichier
    # date_heure, label = nom_fichier.split(' - ')
    parties_nom_fichier = nom_fichier.split(' - ')
    label = ''.join(parties_nom_fichier[1:])
    query_supprime = ' and trashed = false' if not considerer_supprime else ''

    try:
        # Appel de l'API Drive v3 pour lister tous les fichiers
        resultats = service.files().list(
            q=f"'{id_dossier_parent}' in parents and name contains '{label}'{query_supprime}",
            fields="nextPageToken, files(id, name)").execute()
        print(f"DEBUG : RESULTATS dans archiver = {resultats}")

        items = resultats.get('files', [])

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
    values = [["nom_scene", "date", "qui", "document"] + list(dict_orgas_persos.keys())]
    if verbal:
        print(f"en-tetes = {values}")

    for scene_orgas in tableau_scenes_orgas:
        dict_scene, dict_orgas = scene_orgas
        row = [dict_scene["nom_scene"], dict_scene["date"], dict_scene["qui"], dict_scene["document"]]

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

# def ecrire_table_google_sheets(api_sheets, table, spreadsheet_id, feuille="Feuille 1", avec_formules=True):
def ecrire_table_google_sheets(api_sheets, table, spreadsheet_id, feuille=None, avec_formules=True):
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

    sheetId = None

    for i, sheet in enumerate(sheets):
        # Store the ID of the first sheet
        if i == 0:
            sheetId = sheet['properties']['sheetId']

        if sheet['properties']['title'] == feuille:
            sheetId = sheet['properties']['sheetId']
            break

    expand_grid(api_sheets, spreadsheet_id, sheetId, table)

    requests = []

    for i, row in enumerate(table):
        for j, cell in enumerate(row):
            if isinstance(cell, str) and cell.startswith('='):
                # This cell contains a formula
                requests.append({
                    "updateCells": {
                        "range": {
                            "sheetId": sheetId,
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
                            "sheetId": sheetId,
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
    # logging.debug(f"chaine en entrée = {repr(texte_lu)}")
    last_hash_index = texte_lu.rfind(lecteurGoogle.FIN_LIGNE)
    if last_hash_index == -1:
        return [], 0

    texte_tableau = texte_lu[:last_hash_index]

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


# def lire_gspread_pnj(api_sheets, sheet_id):
#     a, b = lire_gspread_pj_pnjs(api_sheets, sheet_id, "PNJs")
#     return a
#
#
# def lire_gspread_pj(api_sheets, sheet_id):
#     return lire_gspread_pj_pnjs(api_sheets, sheet_id, "PJs")


def lire_gspread_pj_pnjs(api_sheets, sheet_id):
    """
    Lit les données des feuilles "PJs" et "PNJs" d'un Google Spreadsheet et les stocke dans deux listes de dictionnaires.

    Cette fonction utilise la méthode `mettre_sheet_dans_dictionnaires` pour lire les données des feuilles "PJs" et "PNJs"
    et les stocker dans deux listes de dictionnaires séparées.

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

    # anciennement :
    # try:
    #
    #     result = api_sheets.spreadsheets().values().get(spreadsheetId=sheet_id, range=sheet_name,
    #                                                     majorDimension="COLUMNS").execute()
    #     values = result.get('values', [])
    #
    #     logging.debug(f"result =  {values}")
    #
    #     noms_pjs = values[0][1:]
    #     orgas_referents = values[1][1:] if len(values) > 1 else None
    #     return noms_pjs, orgas_referents
    # except HttpError as error:
    #     print(f"An error occurred: {error}")
    #     return None

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
        taille_ligne = len(en_tetes)

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


def charger_et_verifier_fichier_config(fichier_init: str, api_drive):
    try:
        # #création du fichier d'entrée
        # init configuration
        config = configparser.ConfigParser()
        config.read(fichier_init)
    except Exception as e:
        logging.debug(f"Une erreur est survenue en lisant le fichier config : {e}")
        return None, [["Fichier configuration", "Erreur dans la structure du fichier", "Echec du test"]]

    return verifier_config_parser(api_drive, config)


def verifier_config_parser(api_drive, config):
    resultats = []
    test_global_reussi = True
    fichier_output = {}

    dossiers_a_verifier = []
    google_docs_a_verifier = []
    google_sheets_a_verifier = []
    # *** vérification que tous les paramètres Essentiels sont présents
    # intégration du fichier de sortie
    try:
        fichier_output['dossier_output'] = config.get('Essentiels', 'dossier_output_squelettes_pjs')
    except configparser.NoOptionError:
        resultats.append(
            ["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de dossier de sortie trouvé"])
        test_global_reussi = False

    # intégration des dossiers intrigues et vérifications
    fichier_output['dossiers_intrigues'] = []
    clefs_intrigues = [key for key in config.options("Essentiels") if key.startswith("id_dossier_intrigues")]
    for clef in clefs_intrigues:
        valeur = config.get("Essentiels", clef)
        dossiers_a_verifier.append([clef, valeur])
        fichier_output['dossiers_intrigues'].append(valeur)
    if len(fichier_output.get('dossiers_intrigues', [])) == 0:
        resultats.append(["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de dossier intrigue"])
        test_global_reussi = False
    # intégration du mode association et vérifications
    try:
        mode_association_value = int(config.get('Essentiels', 'mode_association', fallback="9")[0])
        if mode_association_value in [0, 1]:
            fichier_output['mode_association'] = GN.ModeAssociation(mode_association_value)
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
        fichier_output['nom_fichier_sauvegarde'] = config.get('Essentiels', 'nom_fichier_sauvegarde')
    except configparser.NoOptionError:
        resultats.append(["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de fichier de sauvegarde"])
        test_global_reussi = False
    # intégration d'une ligne de bilan des tests essentiels
    if test_global_reussi:
        resultats.append(["Paramètre Essentiels", "Présence des champs", "Test Réussi"])
    # *** intégration des fichiers optionnels
    # intégration des dossiers PJs
    fichier_output['dossiers_pjs'] = []
    clefs_pjs = [key for key in config.options("Optionnels") if key.startswith("id_dossier_pjs")]
    for clef in clefs_pjs:
        valeur = config.get("Optionnels", clef)
        dossiers_a_verifier.append([clef, valeur])
        fichier_output['dossiers_pjs'].append(valeur)
    # intégration des dossiers PNJs
    fichier_output['dossiers_pnjs'] = []
    clefs_pjs = [key for key in config.options("Optionnels") if key.startswith("id_dossier_pnjs")]
    for clef in clefs_pjs:
        valeur = config.get("Optionnels", clef)
        dossiers_a_verifier.append([clef, valeur])
        fichier_output['dossiers_pnjs'].append(valeur)
    # intégration des dossiers Evenements
    fichier_output['dossiers_evenements'] = []
    clefs_pjs = [key for key in config.options("Optionnels") if key.startswith("id_dossier_evenements")]
    for clef in clefs_pjs:
        valeur = config.get("Optionnels", clef)
        dossiers_a_verifier.append([clef, valeur])
        fichier_output['dossiers_evenements'].append(valeur)
    # intégration des dossiers objets
    fichier_output['dossiers_objets'] = []
    clefs_pjs = [key for key in config.options("Optionnels") if key.startswith("id_dossier_objets")]
    for clef in clefs_pjs:
        valeur = config.get("Optionnels", clef)
        dossiers_a_verifier.append([clef, valeur])
        fichier_output['dossiers_objets'].append(valeur)

    # intégration du fichier des factions
    id_factions = config.get('Optionnels', 'id_factions', fallback=None)
    fichier_output['id_factions'] = id_factions
    if id_factions:
        google_docs_a_verifier.append(["id_factions", id_factions])
    # intégration du fichier des ids pjs_pnjs
    id_pjs_et_pnjs = config.get('Optionnels', 'id_pjs_et_pnjs', fallback=None)
    if id_pjs_et_pnjs:
        fichier_output['id_pjs_et_pnjs'] = id_pjs_et_pnjs
        google_sheets_a_verifier.append(["id_pjs_et_pnjs", id_pjs_et_pnjs])
    else:
        logging.debug("Je suis en train de lire le fichier de config et je n'ai pas trouvé d'id pjpnj en ligne")
        fichier_output['fichier_noms_pnjs'] = config.get('Optionnels', 'nom_fichier_pnjs', fallback=None)
        fichier_output['liste_noms_pjs'] = [nom_p.strip()
                                            for nom_p in
                                            config.get('Optionnels', 'noms_persos', fallback="").split(',')]
    # ajout de la date du GN
    texte_date_gn = config.get('Optionnels', 'date_gn', fallback=None)
    if texte_date_gn:
        fichier_output['date_gn'] = dateparser.parse(texte_date_gn, languages=['fr'])
        logging.debug(f"date_gn formattée = {fichier_output['date_gn']}")
    else:
        logging.debug("pour ce GN, date_gn = Pas de date lue")
    fichier_output['prefixe_intrigues'] = config.get('Optionnels', 'prefixe_intrigues', fallback="I")
    fichier_output['prefixe_evenements'] = config.get('Optionnels', 'prefixe_evenements', fallback="E")
    fichier_output['prefixe_PJs'] = config.get('Optionnels', 'prefixe_PJs', fallback="P")
    fichier_output['prefixe_PNJs'] = config.get('Optionnels', 'prefixe_PNJs', fallback="N")
    fichier_output['prefixe_objets'] = config.get('Optionnels', 'prefixe_objets', fallback="O")
    fichier_output['liste_noms_pjs'] = config.get('Optionnels', 'noms_persos', fallback=None)

    # ajouter le dossier archive
    fichier_output['id_dossier_archive'] = config.get('Optionnels', 'id_dossier_archive', fallback=None)

    # a ce stade là on a :
    # 1. intégré tous les paramètres au fichier de sortie
    # 2. fait les premiers tests sur les fichiers essentiels
    # 3. préparé les tableaux à parcourir pour faire les tests d'accès / existence aux dossiers
    # >> on peut lancer les tests
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
    dossier_output_id = fichier_output['dossier_output']
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
    print(f"{fichier_output if test_global_reussi else None}, {resultats}")
    return fichier_output if test_global_reussi else None, resultats


# # Utilisation de la méthode
# config_dict = charger_fichier_init("config.ini")
# if config_dict:
#     resultats, test_reussi = verifier_fichier_config(config_dict)
#     for param, resultat in resultats:
#         print(f"{param}: {'Réussi' if resultat else 'Échec'}")
#     print(f"Test global: {'Réussi' if test_reussi else 'Échec'}")
# else:
#     print("Erreur lors du chargement du fichier de configuration.")

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
    pattern = r'https?://(?:drive|docs)\.google\.com/(?:drive/u/0/folders/|spreadsheets/d/|document/d/)([a-zA-Z0-9_-]+)'

    # Search for the pattern in the user text
    match = re.search(pattern, user_text)

    # If a match is found, return the resource ID from the match
    if match:
        return match.group(1), True

    # If no match is found, check if the user_text looks like an ID
    elif re.fullmatch(r'[a-zA-Z0-9_-]+', user_text):
        return user_text, True

    # If neither a URL nor an ID, return None
    else:
        return user_text, False
