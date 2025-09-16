import traceback
from datetime import datetime
import re

from fuzzywuzzy import process
from googleapiclient.errors import HttpError

import google_io as g_io
import lecteurGoogle

from enum import Enum

from searchfile import folderid

NOMS_LIGNE = ["nom photo", "nom personnage secable", "nom personnage insécable", "alias sécables", "alias insécables"]

SOUSDOSSIER = "/"

class FormatsNomsPhotos(Enum):
    PERSO = "Juste le nom des personnages"
    JOUEUR = "Juste le nom des joueurs et joueuse"
    JOUEUR_PERSO= "Joueurs [séparateur] Personnage"
    PERSO_JOUEUR = "Personnage [séparateur] Joueurs"

def lister_sous_dossiers_niveau1(drive_service, parent_id):
    """
    Retourne un dict {id: nom} contenant uniquement les sous-dossiers de premier niveau
    d'un dossier parent donné.
    """
    dossiers = {}
    erreurs = None
    page_token = None
    query = f"'{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"

    try:
        while True:
            response = (drive_service.files()
                        .list(q=query,
                              spaces='drive',
                              fields='nextPageToken, files(id, name)',
                              pageToken=page_token)
                        .execute())

            for f in response.get('files', []):
                dossiers[f['id']] = f['name']

            page_token = response.get('nextPageToken')
            if not page_token:
                break

    except HttpError as e:
        print("Erreur Http:", e)
        erreurs = f"problème lors de la recherche des sous-dossier de {parent_id} : {e}"
    except Exception as e:
        print("Erreur:", e)
        erreurs = f"problème lors de la recherche des sous-dossier de {parent_id} : {e}"

    return dossiers, erreurs

def lister_images_dans_dossier(folder_id, drive_service, recurrent = False):
    """
    Liste les images (JPEG/PNG) d’un dossier Google Drive, avec option de parcours récursif.

    Args:
        folder_id (str): ID du dossier racine à analyser.
        drive_service: Client de l’API Google Drive (service.files().list, etc.).
        recurrent (bool, optional): Si True, parcourt également les sous-dossiers de niveau arbitraire.
            Si False, ne parcourt que le dossier donné. Par défaut False.

    Returns:
        tuple[dict[str, str], Optional[str]]:
            - dict qui mappe « chemin_ou_prefixe+nom_sans_extension » → id_fichier_image
            - message d’erreur agrégé (str) si au moins une erreur est survenue, sinon None.

    Notes:
        - Les chemins de sous-dossiers sont concaténés avec la constante SOUSDOSSIER ("/").
        - Les noms retournés n’ont pas d’extension (".jpg", ".png" retirés).
    """
    dict_dossier_prefixe = {folder_id: ""} # on initialise le doctionnaire avec le premier dossier
    tableau_erreurs = []
    dict_retour = {}

    if recurrent:
        to_recurse = dict_dossier_prefixe.copy()
        while to_recurse:
            current_folder_id, current_prefix = next(iter(to_recurse.items()))
            # retirer du dictionnaire
            to_recurse.pop(current_folder_id)
            # chercher tous les dossiers dans le dossier actuel
            to_include, erreurs = lister_sous_dossiers_niveau1(drive_service, current_folder_id)
            if erreurs:
                tableau_erreurs.append(erreurs)
                # ca a planté pas la peine d'insister
                continue

            for subfolder_id, subfolder_name in to_include.items():
                print(f"dans folder_id {folderid}, j'ai trouvé {subfolder_id} qui s'appelait {subfolder_name}")
                #lui facbriquer un nouveau prefixe qui reprend le current prefixe
                next_prefix = current_prefix + subfolder_name + SOUSDOSSIER

                #l'ajouter au dict_dossier_prefixe avec son nouveau prefixe
                dict_dossier_prefixe[subfolder_id] = next_prefix
                #l'ajouter au to_recurse avec son nouveau prefixe
                to_recurse[subfolder_id] = next_prefix

    for folder_id, prefixe in dict_dossier_prefixe.items():
        images_dans_dossier, retour_erreurs = lister_images_dans_un_dossier(folder_id, drive_service, prefixe)
        dict_retour |= images_dans_dossier
        tableau_erreurs.append(retour_erreurs)

    if any(tableau_erreurs):
        erreurs = "\n".join(e for e in tableau_erreurs if e is not None)
    else:
        erreurs = None

    # return lister_images_dans_un_dossier(folder_id, drive_service)
    return dict_retour, erreurs

def lister_images_dans_un_dossier(folder_id, drive_service, prefix_nom = ""):
    """
    Récupère toutes les images (JPEG/PNG) immédiates d’un dossier Google Drive (sans descendre dans les sous-dossiers).

    Args:
        folder_id (str): ID du dossier Google Drive à parcourir.
        drive_service: Client de l’API Google Drive.
        prefix_nom (str, optional): Préfixe ajouté devant chaque nom de fichier (utile pour les sous-dossiers).
            Par défaut "".

    Returns:
        tuple[dict[str, str], Optional[str]]:
            - dict {prefix_nom + nom_sans_extension: id_image}
            - str d’erreur lisible, ou None si tout s’est bien passé.

    Exceptions gérées:
        - HttpError: converti en message d’erreur explicite (dossier introuvable, etc.).
        - Exception: renvoyée comme message d’erreur générique.
    """
    images_dict = {}
    erreurs = None

    # Définir la requête pour rechercher des fichiers d'images dans le dossier spécifié
    query = f"'{folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png') and trashed = false"
    page_token = None  # Initialiser le token de pagination à None

    try:
        while True:  # Commencer une boucle pour gérer la pagination
            response = drive_service.files().list(q=query,
                                                  spaces='drive',
                                                  fields='nextPageToken, files(id, name)',
                                                  orderBy='createdTime',
                                                  pageToken=page_token).execute()  # Ajouter pageToken à la requête

            # Extraire le nom de fichier sans extension et l'ID, et les ajouter au dictionnaire
            for file in response.get('files', []):
                # Supprimer l'extension du fichier pour obtenir le nom de l'image
                file_name_without_extension = '.'.join(file.get('name').split('.')[:-1]).strip()
                images_dict[prefix_nom + file_name_without_extension] = file.get('id')

            page_token = response.get('nextPageToken')  # Récupérer le nextPageToken de la réponse

            if not page_token:  # S'il n'y a pas de nextPageToken, c'est la fin des résultats
                break  # Sortir de la boucle
    except HttpError as e:
        print(e)
        # Vérifier le code HTTP
        if "'reason': 'notFound'" in str(e):
            erreurs = "Erreur : Le dossier d'entrée est introuvable"
        else:
            erreurs = "Erreur Http non détaillée (contacter le support pour plus d'informations) : " + str(e)
    except Exception as e:
        print(e)
        erreurs = "Erreur non détaillée (contacter le support pour plus d'informations) : " + str(e)

    return images_dict, erreurs


def base_nom_prenom(nom_secable):
    """
    Génère une liste de variantes simples à partir d’un nom « sécable ».

    Exemple:
        "Jean Dupont" → ["Jean Dupont", "Jean", "Dupont"]

    Args:
        nom_secable (str): Nom complet potentiellement composé (espaces).

    Returns:
        list[str]: Variantes utiles pour la recherche/fuzzymatching.
            Liste vide si l’entrée est vide ou uniquement des espaces.
    """
    base_nettoyee = nom_secable.strip()
    if not base_nettoyee:
        return []

    to_return = [base_nettoyee]
    nom_prenom = base_nettoyee.split()
    if len(nom_prenom) > 1:
        to_return.append(nom_prenom[0].strip())
        to_return.append(''.join(nom_prenom[1:]).strip())
    return to_return

def lire_table_photos(api_sheets, sheet_id, sheet_name='Feuille 1', separateur=';', verbal=False):
    """
        Lit une feuille Google Sheets contenant les photos et les noms/associations de personnages,
        puis construit un dictionnaire pour associer chaque photo à une liste de mots-clés.

        Le dictionnaire produit permet ensuite de retrouver la bonne photo à partir des mots-clés
        lors d'une insertion ou d'un traitement ultérieur.

        Args:
            api_sheets: Objet ou service client permettant d'interagir avec l'API Google Sheets.
            sheet_id (str): Identifiant unique de la feuille Google Sheets à lire.
            sheet_name (str, optional): Nom de l'onglet à lire dans la feuille.
                Par défaut 'Feuille 1'.
            separateur (str, optional): Caractère utilisé pour séparer plusieurs mots-clés
                associés à une photo dans la feuille. Par défaut ';'.
            verbal (bool, optional): Si True, affiche des informations de débogage
                sur la lecture et le traitement de la feuille. Par défaut False.

        Returns:
            dict: Un dictionnaire de la forme :
                {
                    "nom_photo": ["mot_clef1", "mot_clef2", ...],
                    ...
                }
        """
    result = api_sheets.spreadsheets().values().get(spreadsheetId=sheet_id, range=f"'{sheet_name}'",
                                                    majorDimension="ROWS").execute()
    values = result.get('values', [])

    if values[0][0:6] != NOMS_LIGNE:
        raise ValueError("Le fichier source ne possède pas les bon entêtes de colonne")

    if verbal:
        print(values)
    to_return = dict()
    for value in values[1:]:
        if len(value) > 5:
            value = value[:6]
        else:
            value = value + [''] * (5 - len(value))
        value = [value[0]] + [element.lower() for element in value[1:]]
        photo, nom_secable, nom_insecable, alias_secable, alias_insecable = value
        photo = photo.strip()
        to_return[photo] = []

        if nom_insecable := nom_insecable.strip():
            to_return[photo].append(nom_insecable)

        if nom_secable:
            a_ajouter = base_nom_prenom(nom_secable)
            to_return[photo].extend(a_ajouter)

        if alias_insecable := alias_insecable.strip():
            a_ajouter = alias_insecable.split(separateur)
            for alias in a_ajouter:
                to_return[photo].append(alias.strip())

        if alias_secable := alias_secable.strip():
            tous_mes_alias = alias_secable.split(separateur)
            for alias in tous_mes_alias:
                a_ajouter = base_nom_prenom(alias)
                to_return[photo].extend(a_ajouter)

        to_return[photo] = list(set(to_return[photo]))

    return to_return


# def trouver_mots_phrases(liste_mots_phrases, texte):
#     """
#     Trouve toutes les occurrences exactes (à frontière de mot) d’une liste de mots/phrases dans un texte.
#
#     Args:
#         liste_mots_phrases (Iterable[str]): Mots/expressions à chercher (sensibles aux accents, non à la casse).
#         texte (str): Texte source.
#
#     Returns:
#         list[list[int, str]]: Liste de [index_depart, mot_ou_phrase_trouvé] pour chaque correspondance,
#         non triée entre différents motifs (ordre d’itération).
#     """
#     mots_phrases_indices = {}
#     texte_lower = texte.lower()
#     # Pattern pour détecter si un mot/phrase est bien entouré par des non-mots ou en début/fin de texte.
#     word_boundary_pattern = r'(?<!\w){}(?!\w)'
#
#     for mot_phrase in liste_mots_phrases:
#         mot_phrase_inf = mot_phrase.lower()
#         mots_phrases_indices[mot_phrase_inf] = []
#         pattern = word_boundary_pattern.format(re.escape(mot_phrase_inf))
#         for match in re.finditer(pattern, texte_lower):
#             mots_phrases_indices[mot_phrase_inf].append(match.start())
#
#     resultats = []
#     for mot_phrase in liste_mots_phrases:
#         mot_phrase_inf = mot_phrase.lower()
#         if mot_phrase_inf in mots_phrases_indices:
#             for indice in mots_phrases_indices[mot_phrase_inf]:
#                 resultats.append([indice, mot_phrase])
#
#     return resultats


def trouver_mots_phrases_plus_long(liste_mots_phrases, texte):
    """
    Comme trouver_mots_phrases, mais ne conserve qu’une seule correspondance par index:
    si plusieurs motifs commencent au même index, on garde le plus long.

    Args:
        liste_mots_phrases (Iterable[str]): Mots/expressions à chercher.
        texte (str): Texte source.

    Returns:
        list[list[int, str]]: Liste triée par index de [index_depart, motif_plus_long_à_cet_index].
    """
    mots_phrases_indices = {}
    texte_lower = texte.lower()
    # Pattern pour détecter si un mot/phrase est bien entouré par des non-mots ou en début/fin de texte.
    word_boundary_pattern = r'(?<!\w){}(?!\w)'

    for mot_phrase in liste_mots_phrases:
        mot_phrase_inf = mot_phrase.lower()
        pattern = word_boundary_pattern.format(re.escape(mot_phrase_inf))
        for match in re.finditer(pattern, texte_lower):
            indice = match.start()
            if indice not in mots_phrases_indices:
                mots_phrases_indices[indice] = []
            mots_phrases_indices[indice].append(mot_phrase)

    # Filtrer pour ne garder que le mot/phrase le plus long à chaque indice
    resultats_filtres = []
    for indice, mots_phrases in mots_phrases_indices.items():
        plus_long_mot_phrase = max(mots_phrases, key=len)  # Trouve le mot/phrase le plus long
        resultats_filtres.append([indice, plus_long_mot_phrase])

    # Trier les résultats par indice pour garder l'ordre d'apparition dans le texte
    resultats_filtres.sort(key=lambda x: x[0])

    return resultats_filtres


def nettoyer_doublons_souschaines(dico):
    """
       Supprime, dans les listes de chaque clé, les éléments :
         1) dupliqués globalement (présents dans ≥ 2 clés),
         2) qui sont des sous-chaînes d’un élément présent dans une autre clé.

       ⚠️ La fonction modifie le dictionnaire **sur place** et le renvoie.

       Args:
           dico (dict[str, list[str]]): Dictionnaire {clé: [éléments]}.

       Returns:
           dict[str, list[str]]: Dictionnaire nettoyé (modifié sur place et renvoyé).

       Exemple:
           >>> d = {
           ...     "A": ["Jean", "Jean Dupont", "Dup", "Du"],
           ...     "B": ["Dupont", "Marie", "Jean"],
           ...     "C": ["Mar", "Marie Curie"]
           ... }
           >>> nettoyer_doublons_souschaines(d)
           {'A': ['Jean Dupont'], 'B': [], 'C': ['Marie Curie']}

           Explications :
           - "Jean" est dupliqué globalement (A et B) ⇒ supprimé partout.
           - "Dup" et "Du" sont des sous-chaînes de "Dupont" (autre liste) ⇒ supprimés.
           - "Dupont" est une sous-chaîne de "Jean Dupont" (autre liste) ⇒ supprimé.
           - "Mar" est une sous-chaîne de "Marie Curie" (autre liste) ⇒ supprimé.
           - "Marie" est une sous-chaîne de "Marie Curie" (autre liste) ⇒ supprimé.
           - "Jean Dupont" et "Marie Curie" restent car ils ne sont ni dupliqués, ni sous-chaînes d’un autre élément.
       """
    a_supprimer = set()

    # On identifie les doublons dans tout le dictionnaire
    tous_les_items = [item for sublist in dico.values() for item in sublist]
    for item in tous_les_items:
        if tous_les_items.count(item) > 1:
            a_supprimer.add(item)

    # On crée un set global pour faciliter la vérification des sous-chaînes
    set_global = set(tous_les_items)

    # Pour chaque clé, vérifie si les éléments de sa liste sont des sous-chaînes des éléments des autres listes
    for clef in dico:
        items_clef = set(dico[clef])
        autres_items = set_global - items_clef
        # Enlève les éléments de la liste courante pour comparer seulement avec les autres

        for item in items_clef:
            for autre_item in autres_items:
                if item in autre_item:  # Si l'item est une sous-chaîne d'un autre item pas dans la même liste
                    a_supprimer.add(item)
                    break  # Pas besoin de vérifier les autres si on a déjà trouvé une sous-chaîne

    # Nettoyage du dictionnaire
    for clef in dico:
        dico[clef] = [item for item in dico[clef] if item not in a_supprimer]

    return dico


def eviter_recouvrement(dict_img_positions):
    """
    Résout des conflits de recouvrement entre occurrences de mots-clés de plusieurs images dans un texte.

    Principe:
        - Chaque image possède une liste d’options [index, mot] ordonnée.
        - On essaie d’assigner à chaque image une occurrence telle qu’aucune plage [index, index+len(mot)]
          ne se recoupe avec celle d’une autre image. En cas de conflit, on essaie la « solution suivante »
          pour l’image concernée jusqu’à obtenir un ensemble sans conflit.

    Args:
        dict_img_positions (dict[str, list[list[int, str]]]):
            Pour chaque image, liste des [index, mot] possibles déjà triée/ordonnancée.

    Returns:
        list[list[str, int, str]]: Liste de [nom_image, index_choisi, mot_choisi] formant une solution sans recouvrement.
    """
    class Bulle:
        def __init__(self, nom_image: str, liste_positions_nom: list[list]):
            self.nom_image = nom_image
            self.liste_positions_nom = liste_positions_nom

        def top_index(self):
            return self.liste_positions_nom[0][0]

        def top_mot(self):
            return self.liste_positions_nom[0][1]

        def image(self):
            return self.nom_image

        def has_elements(self):
            return len(self.liste_positions_nom) > 0

        def next_solution(self):
            self.liste_positions_nom = self.liste_positions_nom[1:]

    toutes_les_bulles = [Bulle(nom_image=clef, liste_positions_nom=dict_img_positions[clef])
                         for clef in dict_img_positions]

    def reconstituer_bulles(liste_bulles: list[Bulle]):
        ma_liste = [[bulle.top_index(), bulle.top_mot(), bulle]
                    for bulle in liste_bulles if bulle.has_elements()]
        return sorted(ma_liste, key=lambda x: len(x[1]))

    def verifier_et_ajuster_solution(current_bulles, verbal=False):
        if verbal:
            print(f'set actuel : {current_bulles}')
        # pour chaque bulle, je vérifie l'absence de conflit avec chacune des bulles suivantes dans la liste
        for index, bulle in enumerate(current_bulles, start=0):
            my_start = bulle[0]
            my_end = my_start + len(bulle[1])
            my_bulle = bulle[2]
            for autre_bulle in current_bulles[index + 1:]:
                # y a t-il un conflit?
                his_start = autre_bulle[0]
                his_end = his_start + len(autre_bulle[1])

                conflit = (his_start <= my_start <= his_end) or (his_start <= my_end <= his_end)
                # en cas de conflit, je fais évoluer la bulle et je revoie faux

                if conflit:
                    print(f'conflit trouvé : current = {bulle}, autre = {autre_bulle}')
                    my_bulle.next_solution()
                    return False

                # en cas de non conflit, je continue jusuq'à arriver à la fin
        return True

    # invariant : je dispose d'une solution triée du plus petit mot au plus gros
    solution = False
    bulles =  []
    while not solution:
        bulles = reconstituer_bulles(toutes_les_bulles)
        solution = verifier_et_ajuster_solution(bulles)

    # une fois que j'ai une solution, je renvoie des duplets image_id, position
    to_return = [[bulle[2].image(), bulle[2].top_index(), bulle[2].top_mot()] for bulle in bulles]
    return to_return


def requete_pour_inserer_img_et_formatter(image_id, position, longueur=0, verbal=False, avec_bold=True):
    """
    Construit les requêtes Google Docs API pour insérer une image inline et (optionnellement) mettre en gras
    le mot-clé correspondant.

    Args:
        image_id (str): ID Drive de l’image à insérer.
        position (int): Index (offset) dans le document où insérer.
        longueur (int, optional): Longueur du mot/segment à mettre en gras à partir de 'position'. Par défaut 0.
        verbal (bool, optional): Affiche des traces si True. Par défaut False.
        avec_bold (bool, optional): Si True, ajoute une requête updateTextStyle pour mettre en gras. Par défaut True.

    Returns:
        list[dict]: Liste de requêtes (payloads) prêtes pour documents().batchUpdate(...).
    """

    # Obtenir l'URL de l'image depuis Google Drive
    # image_file = drive_service.files().get(fileId=image_id, fields='webViewLink').execute()
    # image_url = image_file.get('webViewLink')
    if verbal:
        print(f'image_id = {image_id}')

    image_url = f'https://drive.google.com/uc?export=view&id={image_id}'
    # Créer une requête pour insérer l'image dans le Google Doc
    insert_image_request = {
        'insertInlineImage': {
            'location': {'index': position},
            'uri': image_url,
            'objectSize': {
                'height': {'magnitude': 100, 'unit': 'PT'},
                'width': {'magnitude': 100, 'unit': 'PT'}
            }
        }
    }
    #
    # insert_image_request = {
    #     "createPositionedObject": {
    #                     "location": {
    #                         "index": position
    #                     },
    #                     "positionedObjectProperties": {
    #                         "embeddedObject": {
    #                             "imageProperties": {
    #                                 "contentUri": image_url
    #                             }
    #                         },
    #                         "positioning": {
    #                             "layout": "WRAP_TEXT",
    #                             "leftOffset": {
    #                                 "unit": "PT",
    #                                 "magnitude": 100
    #                             },
    #                             "topOffset": {
    #                                 "unit": "PT",
    #                                 "magnitude": 200
    #                             }
    #                         }
    #                     }
    #                 }
    #             }

    # Créer une requête pour mettre en gras le texte
    bold_text_request = {
        'updateTextStyle': {
            'range': {
                'startIndex': position,
                'endIndex': position + longueur + 1
            },
            'textStyle': {
                'bold': True
            },
            'fields': 'bold'
        }
    }

    # Regrouper les requêtes
    if avec_bold:
        requests = [bold_text_request, insert_image_request]
    else:
        requests = [insert_image_request]

    # # Exécuter la requête
    # result = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    # print(f'Image insérée avec succès : {result}')
    return requests


# def lire_dictionnaires_copier_fiche_inserer_photos(api_drive, api_doc, api_sheets,
#                                                    id_sheet_photos_aliases, id_dossier_images,
#                                                    id_doc_source, id_dossier_output, sheet_name='Feuille 1', offset=0,
#                                                    verbal=False):
#     dico_photos_motsclefs, dict_img_id = preparer_donnees_photos(api_drive, api_sheets, id_dossier_images,
#                                                                  id_sheet_photos_aliases, sheet_name, verbal)
#
#     return copier_fiche_inserer_photos(api_doc, api_drive, dico_photos_motsclefs, dict_img_id, id_doc_source,
#                                        id_dossier_output, offset, verbal)


def preparer_donnees_photos(api_drive, api_sheets, id_dossier_images, id_sheet_photos_aliases, sheet_name, verbal):
    """
     Prépare les données nécessaires pour associer des photos à leurs mots-clés
     à partir d'une feuille Google Sheets et d'un dossier d'images Google Drive.

     Étapes principales :
       1. Lecture de la table des correspondances (photos ↔ mots-clés) depuis Google Sheets.
       2. Nettoyage des doublons et sous-chaînes redondantes dans les mots-clés.
       3. Détection de la présence éventuelle de sous-dossiers dans les noms de photos.
       4. Récupération de la liste des images et de leurs identifiants dans un dossier Google Drive.

     Args:
         api_drive: Objet ou service client permettant d’interagir avec l’API Google Drive.
         api_sheets: Objet ou service client permettant d’interagir avec l’API Google Sheets.
         id_dossier_images (str): Identifiant du dossier Google Drive contenant les images.
         id_sheet_photos_aliases (str): Identifiant de la feuille Google Sheets contenant les associations
             entre photos et mots-clés.
         sheet_name (str): Nom de l’onglet de la feuille Google Sheets à lire.
         verbal (bool): Si True, affiche des informations de débogage pendant l’exécution.

     Returns:
         tuple:
             - dict: Dictionnaire des associations photo → [liste de mots-clés].
             - dict: Dictionnaire des images trouvées dans le dossier Google Drive,
               généralement sous la forme {nom_fichier: id_image}.
     """
    dico_photos_motsclefs = lire_table_photos(api_sheets, id_sheet_photos_aliases, sheet_name=sheet_name, verbal=verbal)
    dico_photos_motsclefs = nettoyer_doublons_souschaines(dico_photos_motsclefs)
    include_subfolders = any(SOUSDOSSIER in nom_photo for nom_photo in dico_photos_motsclefs.keys())
    if verbal:
        print(dico_photos_motsclefs)
    dict_img_id, erreurs = lister_images_dans_dossier(id_dossier_images, api_drive, recurrent=include_subfolders)
    if verbal:
        print(dict_img_id)
    return dico_photos_motsclefs, dict_img_id


def creer_requetes_insertion(dict_img_id, dict_img_indexes, offset, verbal):
    """
    Construit la liste des requêtes Google Docs API permettant d’insérer les images
    aux bons emplacements dans le texte, tout en évitant que deux images soient
    placées sur des mots qui se chevauchent.

    Le principe est :
      - Chaque image est associée à une ou plusieurs positions possibles
        (index dans le texte + mot détecté).
      - On sélectionne pour chaque image une position qui ne rentre pas en
        conflit avec les autres (pas de chevauchement de plages de texte).
      - Une fois ces positions validées, on génère les requêtes d’insertion
        et de mise en gras correspondantes.

    Args:
        dict_img_id (dict[str, str]): Dictionnaire {nom_image: id_image_drive}.
        dict_img_indexes (dict[str, list[list[int, str]]]): Dictionnaire
            {nom_image: [[index, mot], ...]} indiquant les occurrences trouvées
            dans le texte pour chaque image.
        offset (int): Décalage à appliquer à chaque index (utile si le document
            contient un en-tête ou du texte avant la zone d’insertion).
        verbal (bool): Si True, affiche des informations de débogage.

    Returns:
        list[dict]: Liste de requêtes (payloads) compatibles avec
        `api_doc.documents().batchUpdate(...)`.

    Exemple:
        >>> dict_img_id = {"img1": "id123", "img2": "id456"}
        >>> dict_img_indexes = {
        ...     "img1": [[5, "Alice"]],
        ...     "img2": [[10, "Bob"]]
        ... }
        >>> creer_requetes_insertion(dict_img_id, dict_img_indexes, offset=0, verbal=False)
        [
            {'updateTextStyle': {...}},
            {'insertInlineImage': {...}},
            {'updateTextStyle': {...}},
            {'insertInlineImage': {...}}
        ]
    """

    # test_data_multiple_overlap = {
    #     "img1": [[0, "hello"], [20, "world"]],
    #     "img2": [[3, "bonjour"], [5, "salut"], [25, "monde"]],
    #     "img3": [[1, "hola"], [15, "mundo"]]
    # }
    image_a_inserer = eviter_recouvrement(dict_img_indexes)
    if verbal:
        print(image_a_inserer)
    # requetes = [requete_pour_inserer_img_et_formatter(dict_img_id[image[0]], image[1], len(image[2])) for
    #             image in sorted(image_a_inserer, key=lambda x: x[1], reverse=True)]
    requetes = []
    for image in sorted(image_a_inserer, key=lambda x: x[1], reverse=True):
        if image[1] > 1:
            requetes.extend(
                requete_pour_inserer_img_et_formatter(dict_img_id[image[0]], image[1] + offset, len(image[2])))
    if verbal:
        print(requetes)
    return requetes


def copier_doc_et_inserer_images(api_doc, api_drive, id_doc_source, id_dossier_output, original_name, requetes,
                                 today_date):
    """
    Copie un document Google Docs, le renomme, le déplace dans un dossier cible,
    puis exécute les requêtes d’insertion/formatage.

    Args:
        api_doc: Client Google Docs API.
        api_drive: Client Google Drive API.
        id_doc_source (str): ID du document source à dupliquer.
        id_dossier_output (str): ID du dossier Drive de destination.
        original_name (str): Nom d’origine du document (utilisé pour le nouveau nom).
        requetes (list[dict]): Requêtes batchUpdate (insertion images, style, etc.).
        today_date (str): Chaîne date/heure à inclure dans le nouveau nom.

    Returns:
        dict: Réponse de documents().batchUpdate(...).
    """

    # Step 2: Copy and Rename the Document
    new_name = f"{original_name} - Enrichi MAGnet {today_date}"
    copied_file = {'name': new_name}
    new_file = api_drive.files().copy(fileId=id_doc_source, body=copied_file).execute()
    new_file_id = new_file['id']  # This is the ID of the new document
    # Step 3: Move the Copy to the New Folder
    api_drive.files().update(fileId=new_file_id,
                             addParents=id_dossier_output,
                             fields='id, parents').execute()
    #### insérer les images
    return api_doc.documents().batchUpdate(documentId=new_file_id, body={'requests': requetes}).execute()


def map_images_to_text_indexes_and_title(api_doc, dico_photos_motsclefs, id_doc_source, verbal=False):
    """
    Associe les identifiants d'images à leurs index de mots-clés correspondants dans le texte d'un document.

    Arguments:
        api_doc: Un client API ou un objet de service utilisé pour lire des documents (par exemple, Google Docs).
        dico_photos_motsclefs: Un dictionnaire où chaque clé est un identifiant d'image et chaque valeur est une liste
        de mots-clés associés à cette image.
        id_doc_source: L'ID du document à partir duquel le texte et le titre sont extraits.
        verbal: Un drapeau booléen qui indique s'il faut imprimer le dictionnaire résultant des index d'images.

    Renvoie:
        tuple: Un tuple contenant :
            - dict_img_indexes (dict): Un dictionnaire associant chaque identifiant d'image à une liste triée d'index
            de mots-clés dans le texte du document.
            - titre (str): Le titre du document.
    """
    text, titre = g_io.lire_google_doc(api_doc, id_doc_source, extraire_formattage=False, chars_images=True)
    dict_img_indexes = {}
    for img in dico_photos_motsclefs:
        if not img:
            continue
        dict_img_indexes[img] = trouver_mots_phrases_plus_long(dico_photos_motsclefs[img], text)
        dict_img_indexes[img].sort(key=lambda x: x[0])
    if verbal:
        print(dict_img_indexes)
    return dict_img_indexes, titre


# la focntion appellée par l'IHM du module Photo
def creer_fichier_trombi(api_drive, api_doc, original_name, date_today, destination_folder_id, dict_img_indexes,
                         dico_photos_motsclefs,
                         dict_img_id,
                         suffixe="_Trombi", verbal=False):
    """
    Crée un document « trombinoscope » listant les noms détectés (triés) et leur image correspondante.

    Args:
        api_drive: Client Google Drive API.
        api_doc: Client Google Docs API.
        original_name (str): Nom de base pour l’intitulé du fichier.
        date_today (str): Date/heure à intégrer au nom.
        destination_folder_id (str): Dossier Drive où créer le doc.
        dict_img_indexes (dict[str, list[list[int, str]]]): Occurrences par image (pour en déduire un nom représentatif).
        dico_photos_motsclefs (dict[str, list[str]]): Dictionnaire photo → mots-clés (non utilisé directement ici).
        dict_img_id (dict[str, str]): Map image → id Drive.
        suffixe (str, optional): Suffixe du nom de fichier. Par défaut "_Trombi".
        verbal (bool, optional): Traces si True.

    Returns:
        dict: Réponse de documents().batchUpdate(...) après insertion de tout le contenu.
    """
    nom_fichier = date_today + suffixe + '_' + original_name

    if verbal:
        print(f"contenu dico_photos_motsclefs : \n \t {dico_photos_motsclefs}")
        print(f"contenu dict_img_indexes : \n \t {dict_img_indexes}")
    # trouver tous les noms qui sont présents

    # dico_noms_photos = {sorted(dico_photos_motsclefs[clef], key=lambda x: len(x), reverse=True)[0]: clef
    #                     for clef in dico_photos_motsclefs}
    dico_noms_photos = {sorted(dict_img_indexes[clef], key=lambda x: len(x[1]), reverse=True)[0][1]: clef
                        for clef in dict_img_indexes}

    if verbal:
        print(f"dico_noms_photos : \n\t {dico_noms_photos}")

    # les trier par ordre alphabétique
    noms_alpha_inverse = sorted(list(dico_noms_photos.keys()), reverse=True)

    requests = []

    for nom in noms_alpha_inverse:
        img = dico_noms_photos[nom]
        img_id = dict_img_id[img]
        # insérer le texte à l'index 1 suivi de \n
        requests.append({
            'insertText': {
                'location': {
                    'index': 1
                },
                'text': f"\n{nom.title()}\n"
            }
        })
        # insérer l'image à l'index 1 suivi de \n
        requests.append(requete_pour_inserer_img_et_formatter(img_id, 1, avec_bold=False))

    # créer un fichier
    id_fichier = g_io.creer_google_doc(api_drive, nom_fichier, destination_folder_id)

    # insérer la requete dans le fichier créé
    return api_doc.documents().batchUpdate(documentId=id_fichier, body={'requests': requests}).execute()


def ajouter_photos_et_creer_tombis(api_doc, api_drive, api_sheets, folder_id, offset, dossier_sources_fiches,
                                   racine_sortie,
                                   sheet_id, nom_onglet="Feuille 1", verbal=False,
                                   inserer_photos=True, creer_trombi=True) -> set:
    """
     Pipeline principal « module Photo » : pour chaque fiche d’entrée, prépare les données,
     insère les images dans une copie de la fiche et/ou génère un trombinoscope.

     Args:
         api_doc: Client Google Docs API.
         api_drive: Client Google Drive API.
         api_sheets: Client Google Sheets API.
         folder_id (str): ID du dossier Drive contenant les images.
         offset (int): Décalage à appliquer lors des insertions dans les docs.
         dossier_sources_fiches (list[str] | iterable): Dossier(s) Drive où lire les fiches sources.
         racine_sortie (str): ID du dossier Drive racine pour créer les sorties.
         sheet_id (str): ID de la feuille Sheets de correspondance photo ↔ mots-clés.
         nom_onglet (str, optional): Nom d’onglet dans la feuille Sheets. Par défaut "Feuille 1".
         verbal (bool, optional): Traces de debug. Par défaut False.
         inserer_photos (bool, optional): Active la génération des fiches enrichies. Par défaut True.
         creer_trombi (bool, optional): Active la création d’un trombinoscope. Par défaut True.

     Returns:
         set[str]: Ensemble de messages d’erreur (éventuellement vide) rencontrés pendant le traitement.
     """
    if not inserer_photos and not creer_trombi:
        return {"Module Photo : Aucun fichier à créer"}
    texte_erreur = set()
    if verbal:
        print(f"{folder_id}, {offset}, {dossier_sources_fiches},{racine_sortie},{sheet_id}")

    try:
        ids = [idee['id'] for idee in lecteurGoogle.generer_liste_items(api_drive, dossier_sources_fiches)]
        # destination_folder_id = g_io.creer_dossier_drive(api_drive, racine_sortie, "Fiches avec photo")
    except HttpError:
        return {"Impossible de lire les fichiers dans le dossier fiches spécifié"}
    except TypeError:
        return {"Le dossier spécifié pour les fichiers d'entrée n'est pas valide"}

    if verbal:
        print(f"ids fichiers {ids}")
    # offset = 0

    try:
        dico_photos_motsclefs, dict_img_id = preparer_donnees_photos(api_drive, api_sheets, folder_id,
                                                                     sheet_id, nom_onglet, verbal)
    except ValueError as ve:
        return {str(ve)}

    destination_folder_id = g_io.creer_dossier_drive(api_drive, racine_sortie,
                                                     f'{datetime.now().strftime("%Y-%m-%d %H:%M")} '
                                                     f'- enrichissement photos')

    for file_id in ids:
        try:
            if verbal:
                print(f"id en cours : {file_id}")

            dict_img_indexes, original_name = map_images_to_text_indexes_and_title(api_doc, dico_photos_motsclefs,
                                                                                   file_id,
                                                                                   verbal)
            date_today = datetime.now().strftime("%Y-%m-%d %H:%M")

            retour = set()
            if inserer_photos:
                requetes = creer_requetes_insertion(dict_img_id, dict_img_indexes, offset, verbal)
                ####### copier le fichier source et le renommer
                # Known Document ID and Destination Folder ID
                retour_inserer = copier_doc_et_inserer_images(api_doc, api_drive, file_id, destination_folder_id,
                                                              original_name,
                                                              requetes,
                                                              date_today)

                retour.update(retour_inserer)
            if creer_trombi:
                retour_creer = creer_fichier_trombi(api_drive, api_doc, original_name, date_today,
                                                    destination_folder_id,
                                                    dict_img_indexes,
                                                    dico_photos_motsclefs, dict_img_id)
                retour.update(retour_creer)
            if verbal:
                print(f"retour : {retour}")
        except KeyError as e:
            print(f"exception : {e}")
            traceback.print_exc()
            texte_erreur.add(f"La photo suivante n'a pas été trouvée dans le dossier photos {str(e)}")
        except HttpError as e:
            # Check if the error message matches the specific error you're interested in
            if 'This operation is not supported for this document' in e.content.decode('utf-8'):
                texte_erreur.add(f"Le dossier source contient un fichier "
                                 f"non pris en charge par l'api google doc (docx, xslx, etc.)")
            elif "insertInlineImage: There was a problem retrieving the image. " \
                 "The provided image should be publicly accessible, within size limit, and in supported formats." \
                    in e.content.decode('utf-8'):
                texte_erreur.add(f"Une ou plusieurs photos ne sont pas publiquement accessibles")
            else:
                texte_erreur.add(f"Erreur HTTP non détaillée dans cette version : {str(e)}")
            print(f"exception : {e}")
            traceback.print_exc()
            # texte_erreur.append(str(e))

        except Exception as e:
            print(f"exception : {e}")
            traceback.print_exc()
            texte_erreur.add(f"Erreur non détaillée dans cette version : {str(e)}")
            continue

    return texte_erreur


# ##### code pour tster le module photos
# def tester_module_photo_chalacta():
#     sheet_id = '1OPW7VRpMze3DexXxK3MYjNtw20Kc56e9QiE5NRMo7z8'
#     folder_id = '1Hp0JO1ny5Z8gzY2flEn9PMMU6YxyIN-n'  # photos S1 chalacta
#
#     file_id = '1Les3Sr500Ta8W6QJrSLFFajmpCyOsOxFrthTXFYbRTI'  ## fiche test Lars
#     file_id = '1U1OYQPipSYBZrwknPMKIW5qgywhVHoeK1QXen3Xy0us'  ## fiche réelle Lars
#     destination_folder_id = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn'  ## répertoire tmp de MAGnet
#     # destination_folder_id = '1Ci6v1aQKDx5H2IZsTa44CBbvQ0xbAoNX' #V1 avec photos civils
#     offset = 2
#     api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()
#     copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id, destination_folder_id,
#                                    offset)
#
#
# def tester_module_photo_dossier_chalacta():
#     sheet_id = '1OPW7VRpMze3DexXxK3MYjNtw20Kc56e9QiE5NRMo7z8'
#     folder_id = '1Hp0JO1ny5Z8gzY2flEn9PMMU6YxyIN-n'  # photos S1 chalacta
#
#     # destination_folder_id = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn' ## répertoire tmp de MAGnet
#     parent = ['1sApU23J6e4lFZ0OmDtghq40T1Iw5vMTY']
#     # destination_folder_id = '1Ci6v1aQKDx5H2IZsTa44CBbvQ0xbAoNX' #V1 avec photos civils
#
#     api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()
#
#     ids = [idee['id'] for idee in lecteurGoogle.generer_liste_items(api_drive, parent)]
#     racine_pj = '1C53BHHW9xjCWgTVRlBlBCU9Vbmosxv0k'
#     destination_folder_id = g_io.creer_dossier_drive(api_drive, racine_pj, "output photos")
#     print(f"ids fichiers {ids}")
#     offset = 2
#     for file_id in ids:
#         # copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id,
#         #                                destination_folder_id, offset=2)
#         try:
#             copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id,
#                                            destination_folder_id, offset=offset)
#         except Exception as e:
#             continue
#
#
# def tester_module_photo_imperiaux(offset=0):
#     sheet_id = '1pdqZdiKec0alZNU5xUtcFUBaZpNH2v44ueQFY4S3Mxs'
#     # folder_id = '1Hp0JO1ny5Z8gzY2flEn9PMMU6YxyIN-n'  # photos S1 chalacta
#     folder_id = '1Y4ONHyZtVkzAuo4EqbubZSrh8hjbJy_O'  # photos S2 chalacta
#
#     # destination_folder_id = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn' ## répertoire tmp de MAGnet
#     parent = ['1178b_XzkLaE7t9Kp80uyFuFnZrqANtLz']  # dossier ou lire tout
#     destination_folder_id = '1-oQmv4A1XInaL_y6gk27vOLCGpkwRdad' #V1 avec photos civils
#
#     # api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()
#     #
#     # ids = [idee['id'] for idee in lecteurGoogle.generer_liste_items(api_drive, parent)]
#     # racine_sortie = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn'
#     # destination_folder_id = g_io.creer_dossier_drive(api_drive, racine_sortie, "demo imperiaux")
#     # print(f"ids fichiers {ids}")
#     # # offset = 0
#     # for file_id in ids:
#     #     try:
#     #         copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id,
#     #                                        destination_folder_id, offset=offset, sheet_name='Session 2')
#     #     except Exception as e:
#     #         print(e)
#     #         continue
#     sortir_dossier_photos(folder_id, parent, sheet_id, destination_folder_id, offset=2)
#     sortir_dossier_photos(folder_id, parent, sheet_id, destination_folder_id, offset=0)
#
# def photos_manu():
#     sheet_id = '1OPW7VRpMze3DexXxK3MYjNtw20Kc56e9QiE5NRMo7z8'
#     sheet_id = '1gYUOpaxMoBSI2HR25veuz7y9mUFyPTSM1Srg9webIvk'
#     # folder_id = '1Hp0JO1ny5Z8gzY2flEn9PMMU6YxyIN-n'  # photos S1 chalacta
#     folder_id = '1Y4ONHyZtVkzAuo4EqbubZSrh8hjbJy_O'  # photos S2 chalacta
#     # destination_folder_id = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn' ## répertoire tmp de MAGnet
#     parent = ['1BsTNOtnVK3RglGhbFoOeoBEQqNw3b6AP']  # dossier ou lire tout
#     # destination_folder_id = '1Ci6v1aQKDx5H2IZsTa44CBbvQ0xbAoNX' #V1 avec photos civils
#     racine_sortie = '1xYPlwiQMPrKmry0aENzJejp8ETIqXmPP'
#
#     sortir_dossier_photos(folder_id, parent, sheet_id, racine_sortie)
#
#
# def phtos_civils(offset):
#     sheet_id = '1pdqZdiKec0alZNU5xUtcFUBaZpNH2v44ueQFY4S3Mxs'
#     # folder_id = '1Hp0JO1ny5Z8gzY2flEn9PMMU6YxyIN-n'  # photos S1 chalacta
#     folder_id = '1Y4ONHyZtVkzAuo4EqbubZSrh8hjbJy_O'  # photos S2 chalacta
#     # destination_folder_id = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn' ## répertoire tmp de MAGnet
#     parent = ['1sApU23J6e4lFZ0OmDtghq40T1Iw5vMTY']  # dossier ou lire tout
#     destination_folder_id = '1C53BHHW9xjCWgTVRlBlBCU9Vbmosxv0k'
#
#     sortir_dossier_photos(folder_id, parent, sheet_id, destination_folder_id, offset=offset)


# def sortir_dossier_photos(folder_id, parent, sheet_id, racine_sortie, offset=0):
#     api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()
#     ajouter_photos_et_creer_tombis(api_doc, api_drive, api_sheets, folder_id, offset, parent, racine_sortie,
#                                       sheet_id)


# def photos_unitaire():
#     sheet_id = '1OPW7VRpMze3DexXxK3MYjNtw20Kc56e9QiE5NRMo7z8'
#     folder_id = '1Hp0JO1ny5Z8gzY2flEn9PMMU6YxyIN-n'  # photos S1 chalacta
#
#     # destination_folder_id = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn' ## répertoire tmp de MAGnet
#     parent = ['1BsTNOtnVK3RglGhbFoOeoBEQqNw3b6AP']  # dossier ou lire tout
#     # destination_folder_id = '1Ci6v1aQKDx5H2IZsTa44CBbvQ0xbAoNX' #V1 avec photos civils
#
#     api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()
#
#     id = '1G2BxSQdNugGrVysWMPxTZ3ZuocBsLGlXl_HLxeFwYfs'  # fichier à lire
#     racine_sortie = '1xYPlwiQMPrKmry0aENzJejp8ETIqXmPP'
#     destination_folder_id = g_io.creer_dossier_drive(api_drive, racine_sortie, "presque prod Manu")
#
#     offset = 0
#     copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, id,
#                                    destination_folder_id, offset=offset, sheet_name='Session 1')

def extraire_nom_perso_depuis_photo(nom_photo:str, separateur:str='-', format_nom_photo:str=FormatsNomsPhotos.JOUEUR):
    """
    Extrait le nom du personnage à partir du nom de fichier photo selon une convention donnée.

    Args:
        nom_photo (str): Nom de la photo (sans chemin).
        separateur (str, optional): Séparateur joueur/personnage dans le nom (si applicable). Par défaut "-".
        format_nom_photo (str | FormatsNomsPhotos): Format attendu (PERSO, JOUEUR, JOUEUR_PERSO, PERSO_JOUEUR).

    Returns:
        str: Nom du personnage déduit, ou chaîne vide si non déterminable pour le format choisi.
    """
    # si des séparateurs ont été entrés sans utiliser des liste de persos
    # et faire évoluer les regles selectionnables / non selectionnables dans l'IH
    if format_nom_photo == FormatsNomsPhotos.PERSO.value:
        return nom_photo
    elif format_nom_photo == FormatsNomsPhotos.JOUEUR.value:
        return ''
    elif format_nom_photo == FormatsNomsPhotos.JOUEUR_PERSO.value:
        parts = nom_photo.split(separateur)
        return parts[-1]
    elif format_nom_photo == FormatsNomsPhotos.PERSO_JOUEUR.value:
        parts = nom_photo.split(separateur)
        return parts[0]

    print(f"Erreur : format de nom perso inconnu pour {nom_photo}/{separateur}/{format_nom_photo}")
    return ''

def construire_tableau_photos_noms(api_drive, folder_source_images, noms_persos: dict,
                                   separateur:str, format_nom_photo:str, recurrent = False):
    """
     Construit en mémoire le tableau (lignes) à écrire dans la feuille Sheets
     associant chemins de photos et noms/alias de personnages.

     Deux modes:
         - Avec 'noms_persos' fourni: rapprochement fuzzy entre nom de fichier et clés de 'noms_persos'.
         - Sinon: déduction du nom via extraire_nom_perso_depuis_photo.

     Args:
         api_drive: Client Google Drive API.
         folder_source_images (str): ID du dossier d’images.
         noms_persos (dict | None): Dictionnaire {clé: nom} pour rapprochement fuzzy, ou None.
         separateur (str): Séparateur pour l’extraction nom perso (si utilisé).
         format_nom_photo (str | FormatsNomsPhotos): Convention de nommage des fichiers image.
         recurrent (bool, optional): Inclure récursivement les sous-dossiers. Par défaut False.

     Returns:
         tuple[list[list[str]], Optional[str]]:
             - Tableau « prêt à écrire » (première ligne = en-têtes NOMS_LIGNE).
             - Message d’erreur ou None.
     """
    dico_nom_id, erreurs = lister_images_dans_dossier(folder_id=folder_source_images, drive_service=api_drive,
                                                      recurrent=recurrent)
    if erreurs:
        return None, erreurs

    photo_path = [(path.split(SOUSDOSSIER)[-1], path) for path in dico_nom_id]

    to_write = [[e for e in NOMS_LIGNE]]
    if noms_persos:
        clefs_rapprochement = list(noms_persos.keys())
        for photo, path in photo_path:
            correspondance = process.extractOne(photo, clefs_rapprochement)
            nom_perso = noms_persos[correspondance[0]] if correspondance else ''
            to_write.append([path, nom_perso, '', ''])
    else:
        for photo, path in photo_path:
            nom_perso = extraire_nom_perso_depuis_photo(photo, separateur, format_nom_photo)
            to_write.append([path, nom_perso, '', ''])
    return to_write, None


def ecrire_tableau_photos_noms(api_drive, api_sheets, folder_source_images, noms_persos: dict,
                               dossier_output, nom_fichier,
                               separateur, format_nom_photo:str,
                               include_subfolders = False,
                               verbal=False):
    """
       Crée une Google Sheet dans le dossier spécifié et y écrit le tableau photos ↔ noms généré.

       Args:
           api_drive: Client Google Drive API.
           api_sheets: Client Google Sheets API.
           folder_source_images (str): ID du dossier Drive des images.
           noms_persos (dict | None): Dictionnaire pour rapprochement fuzzy, ou None pour extraction simple.
           dossier_output (str): ID du dossier Drive où créer la feuille.
           nom_fichier (str): Nom de la nouvelle feuille.
           separateur (str): Séparateur joueur/personnage (si utilisé pour l’extraction).
           format_nom_photo (str | FormatsNomsPhotos): Convention de nommage des photos.
           include_subfolders (bool, optional): Si True, inclut les sous-dossiers. Par défaut False.
           verbal (bool, optional): Traces si True.

       Returns:
           tuple[Optional[str], Optional[str]]: (id_sheet, message_erreur)
               - id_sheet (str | None): ID de la feuille créée, ou None si échec.
               - message_erreur (str | None): Description de l’erreur si échec, sinon None.
       """
    to_write, erreurs = construire_tableau_photos_noms(api_drive, folder_source_images, noms_persos,
                                                       separateur, format_nom_photo, recurrent=include_subfolders)
    if erreurs:
        return None, erreurs

    if verbal:
        print(f"nom_fichier : {nom_fichier}, dossier_output : {dossier_output}")
    id_sheet = g_io.creer_google_sheet(api_drive, nom_fichier, dossier_output)
    if not id_sheet:
        return None, "Impossible de créer le fichier de sortie dans le dossier spécifié"
    g_io.write_to_sheet(api_sheets, to_write, id_sheet)
    return id_sheet, None
