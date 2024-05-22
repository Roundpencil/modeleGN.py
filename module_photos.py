import dataclasses
from dataclasses import dataclass
import re
from datetime import datetime

import lecteurGoogle
from lecteurGoogle import *
import google_io as g_io


# def lister_images_dans_dossier(folder_id, drive_service):
#     images_dict = {}
#
#     # Définir la requête pour rechercher des fichiers d'images dans le dossier spécifié
#     query = f"'{folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png') and trashed = false"
#     response = drive_service.files().list(q=query,
#                                           spaces='drive',
#                                           fields='files(id, name)',
#                                           orderBy='createdTime').execute()
#
#     # Extraire le nom de fichier sans extension et l'ID, et les ajouter au dictionnaire
#     for file in response.get('files', []):
#         # Supprimer l'extension du fichier pour obtenir le nom de l'image
#         file_name_without_extension = '.'.join(file.get('name').split('.')[:-1]).strip()
#         images_dict[file_name_without_extension] = file.get('id')
#
#     return images_dict

def lister_images_dans_dossier(folder_id, drive_service):
    images_dict = {}

    # Définir la requête pour rechercher des fichiers d'images dans le dossier spécifié
    query = f"'{folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png') and trashed = false"
    page_token = None  # Initialiser le token de pagination à None

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
            images_dict[file_name_without_extension] = file.get('id')

        page_token = response.get('nextPageToken')  # Récupérer le nextPageToken de la réponse

        if not page_token:  # Si il n'y a pas de nextPageToken, c'est la fin des résultats
            break  # Sortir de la boucle

    return images_dict


def base_nom_prenom(nom_secable):
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
    result = api_sheets.spreadsheets().values().get(spreadsheetId=sheet_id, range=sheet_name,
                                                    majorDimension="ROWS").execute()
    values = result.get('values', [])
    if verbal:
        print(values)
    to_return = {}
    for value in values[1:]:
        value = value + [''] * (5 - len(value))
        value = [value[0]] + [element.lower() for element in value[1:]]
        photo, nom_secable, nom_insecable, alias_secable, alias_insecable = value
        photo = photo.strip()
        to_return[photo] = []
        if nom_secable:
            a_ajouter = base_nom_prenom(nom_secable)
            to_return[photo].extend(a_ajouter)

        if nom_insecable := nom_insecable.strip():
            to_return[photo].append(nom_insecable)

        if alias_secable := alias_secable.strip():
            tous_mes_alias = alias_secable.split(separateur)
            for alias in tous_mes_alias:
                a_ajouter = base_nom_prenom(alias)
                to_return[photo].extend(a_ajouter)

        if alias_insecable := alias_insecable.strip():
            a_ajouter = alias_insecable.split(separateur)
            for alias in a_ajouter:
                to_return[photo].append(alias.strip())
        to_return[photo] = list(set(to_return[photo]))

    return to_return


def trouver_mots_phrases(liste_mots_phrases, texte):
    mots_phrases_indices = {}
    texte_lower = texte.lower()
    # Pattern pour détecter si un mot/phrase est bien entouré par des non-mots ou en début/fin de texte.
    word_boundary_pattern = r'(?<!\w){}(?!\w)'

    for mot_phrase in liste_mots_phrases:
        mot_phrase_inf = mot_phrase.lower()
        mots_phrases_indices[mot_phrase_inf] = []
        pattern = word_boundary_pattern.format(re.escape(mot_phrase_inf))
        for match in re.finditer(pattern, texte_lower):
            mots_phrases_indices[mot_phrase_inf].append(match.start())

    resultats = []
    for mot_phrase in liste_mots_phrases:
        mot_phrase_inf = mot_phrase.lower()
        if mot_phrase_inf in mots_phrases_indices:
            for indice in mots_phrases_indices[mot_phrase_inf]:
                resultats.append([indice, mot_phrase])

    return resultats


import re


def trouver_mots_phrases_plus_long(liste_mots_phrases, texte):
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
        autres_items = set_global - items_clef  # Enlève les éléments de la liste courante pour comparer seulement avec les autres

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

    def verifier_et_ajuster_solution(current_bulles):
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
    while not solution:
        bulles = reconstituer_bulles(toutes_les_bulles)
        solution = verifier_et_ajuster_solution(bulles)

    # une fois que j'ai une solution, je renvoie des duplets image_id, position
    to_return = [[bulle[2].image(), bulle[2].top_index(), bulle[2].top_mot()] for bulle in bulles]
    return to_return


def requete_pour_inserer_img_et_formatter(image_id, position, longueur, verbal=False):
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

    ## update chat gpt - ne marche pas
    # insert_image_request = {
    #     'insertInlineImage': {
    #         'location': {'index': position},
    #         'uri': image_url,
    #         'objectSize': {
    #             'height': {'magnitude': 100, 'unit': 'PT'},
    #             'width': {'magnitude': 100, 'unit': 'PT'}
    #         },
    #         'imageProperties': {
    #             'positioning': {
    #                 'layout': 'wrapText',  # Options may include: 'wrapText', 'breakText', etc.
    #                 'wrapOffset': {  # Optional: provide offset values if applicable
    #                     'top': 5,
    #                     'bottom': 5,
    #                     'left': 5,
    #                     'right': 5
    #                 }
    #             }
    #         }
    #     }
    # }

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
    requests = [bold_text_request, insert_image_request]

    # # Exécuter la requête
    # result = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    # print(f'Image insérée avec succès : {result}')
    return requests


##### test lire photos
def copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets,
                                   id_sheet_photos_aliases, id_dossier_images,
                                   id_doc_source, id_dossier_output, sheet_name='Feuille 1', offset=0, verbal=False):
    dico_photos_motsclefs = lire_table_photos(api_sheets, id_sheet_photos_aliases, sheet_name=sheet_name, verbal=verbal)

    dico_photos_motsclefs = nettoyer_doublons_souschaines(dico_photos_motsclefs)
    if verbal:
        print(dico_photos_motsclefs)

    dict_img_id = lister_images_dans_dossier(id_dossier_images, api_drive)
    if verbal:
        print(dict_img_id)

    text = g_io.lire_google_doc(api_doc, id_doc_source, extraire_formattage=False)

    dict_img_indexes = {}
    for img in dico_photos_motsclefs:
        if not img:
            continue
        dict_img_indexes[img] = trouver_mots_phrases_plus_long(dico_photos_motsclefs[img], text)
        dict_img_indexes[img].sort(key=lambda x: x[0])
    if verbal:
        print(dict_img_indexes)

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
            requetes.extend(requete_pour_inserer_img_et_formatter(dict_img_id[image[0]], image[1] + offset, len(image[2])))
    if verbal:
        print(requetes)

    ##### copier le fichier source et le renommer
    # Known Document ID and Destination Folder ID

    # Getting the current date in the format YYYY-MM-DD
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Step 1: Get the name of the original document
    original_file = api_drive.files().get(fileId=id_doc_source, fields='name').execute()
    original_name = original_file.get('name')

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


##### code pour tster le module photos
def tester_module_photo():
    sheet_id = '1WhevQB9MMcYbjGF1nHscCzShFF7Qlt53WkaHHlNpao4'
    folder_id = '169GWiwLFVcbaZsJZvtPGo-q8gfol1gDX'


def test_module():
    sheet_id = '1WhevQB9MMcYbjGF1nHscCzShFF7Qlt53WkaHHlNpao4'
    folder_id = '169GWiwLFVcbaZsJZvtPGo-q8gfol1gDX'

    file_id = '1syyJGdBK2Kkar5UgWNsRWyiU1_plAQfEFeZFX9XWnbo'
    destination_folder_id = '1LV5rFP4JNxDEa5OT00qeNFLok4ZE2oKe'

    api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()
    copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id, destination_folder_id)

    api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()
    copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id, destination_folder_id)


def tester_module_photo_chalacta():
    sheet_id = '1OPW7VRpMze3DexXxK3MYjNtw20Kc56e9QiE5NRMo7z8'
    folder_id = '1Hp0JO1ny5Z8gzY2flEn9PMMU6YxyIN-n'  # photos S1 chalacta

    file_id = '1Les3Sr500Ta8W6QJrSLFFajmpCyOsOxFrthTXFYbRTI'  ## fiche test Lars
    file_id = '1U1OYQPipSYBZrwknPMKIW5qgywhVHoeK1QXen3Xy0us'  ## fiche réelle Lars
    destination_folder_id = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn'  ## répertoire tmp de MAGnet
    # destination_folder_id = '1Ci6v1aQKDx5H2IZsTa44CBbvQ0xbAoNX' #V1 avec photos civils
    offset = 2
    api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()
    copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id, destination_folder_id,
                                   offset)


def tester_module_photo_dossier_chalacta():
    sheet_id = '1OPW7VRpMze3DexXxK3MYjNtw20Kc56e9QiE5NRMo7z8'
    folder_id = '1Hp0JO1ny5Z8gzY2flEn9PMMU6YxyIN-n'  # photos S1 chalacta

    # destination_folder_id = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn' ## répertoire tmp de MAGnet
    parent = ['1sApU23J6e4lFZ0OmDtghq40T1Iw5vMTY']
    # destination_folder_id = '1Ci6v1aQKDx5H2IZsTa44CBbvQ0xbAoNX' #V1 avec photos civils

    api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()

    ids = [idee['id'] for idee in lecteurGoogle.generer_liste_items(api_drive, parent)]
    racine_pj = '1C53BHHW9xjCWgTVRlBlBCU9Vbmosxv0k'
    destination_folder_id = g_io.creer_dossier_drive(api_drive, racine_pj, "output photos")
    print(f"ids fichiers {ids}")
    offset = 2
    for file_id in ids:
        # copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id,
        #                                destination_folder_id, offset=2)
        try:
            copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id,
                                           destination_folder_id, offset=offset)
        except Exception as e:
            continue

def tester_module_photo_imperiaux(offset = 0):
    sheet_id = '1OPW7VRpMze3DexXxK3MYjNtw20Kc56e9QiE5NRMo7z8'
    # folder_id = '1Hp0JO1ny5Z8gzY2flEn9PMMU6YxyIN-n'  # photos S1 chalacta
    folder_id = '1Y4ONHyZtVkzAuo4EqbubZSrh8hjbJy_O'  # photos S2 chalacta

    # destination_folder_id = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn' ## répertoire tmp de MAGnet
    parent = ['1178b_XzkLaE7t9Kp80uyFuFnZrqANtLz'] #dossier ou lire tout
    # destination_folder_id = '1Ci6v1aQKDx5H2IZsTa44CBbvQ0xbAoNX' #V1 avec photos civils

    api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()

    ids = [idee['id'] for idee in lecteurGoogle.generer_liste_items(api_drive, parent)]
    racine_sortie = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn'
    destination_folder_id = g_io.creer_dossier_drive(api_drive, racine_sortie, "demo imperiaux")
    print(f"ids fichiers {ids}")
    # offset = 0
    for file_id in ids:
        try:
            copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id,
                                           destination_folder_id, offset=offset, sheet_name='Session 2')
        except Exception as e:
            print(e)
            continue

def photos_manu():
    sheet_id = '1OPW7VRpMze3DexXxK3MYjNtw20Kc56e9QiE5NRMo7z8'
    sheet_id = '1gYUOpaxMoBSI2HR25veuz7y9mUFyPTSM1Srg9webIvk'
    # folder_id = '1Hp0JO1ny5Z8gzY2flEn9PMMU6YxyIN-n'  # photos S1 chalacta
    folder_id = '1Y4ONHyZtVkzAuo4EqbubZSrh8hjbJy_O'  # photos S2 chalacta
    # destination_folder_id = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn' ## répertoire tmp de MAGnet
    parent = ['1BsTNOtnVK3RglGhbFoOeoBEQqNw3b6AP'] #dossier ou lire tout
    # destination_folder_id = '1Ci6v1aQKDx5H2IZsTa44CBbvQ0xbAoNX' #V1 avec photos civils

    api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()

    ids = [idee['id'] for idee in lecteurGoogle.generer_liste_items(api_drive, parent)]
    racine_sortie = '1xYPlwiQMPrKmry0aENzJejp8ETIqXmPP'
    destination_folder_id = g_io.creer_dossier_drive(api_drive, racine_sortie, "presque prod Manu")
    print(f"ids fichiers {ids}")
    offset = 0
    for file_id in ids:
        # copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id,
        #                                destination_folder_id, offset=offset)
        try:
            print(f"id en cours : {file_id}")
            retour = copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, file_id,
                                           destination_folder_id, offset=offset, sheet_name='Session 1')
            print(f"retour : {retour}")
        except Exception as e:
            print(f"exception : {e}")
            continue
def photos_unitaire():
    sheet_id = '1OPW7VRpMze3DexXxK3MYjNtw20Kc56e9QiE5NRMo7z8'
    folder_id = '1Hp0JO1ny5Z8gzY2flEn9PMMU6YxyIN-n'  # photos S1 chalacta

    # destination_folder_id = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn' ## répertoire tmp de MAGnet
    parent = ['1BsTNOtnVK3RglGhbFoOeoBEQqNw3b6AP'] #dossier ou lire tout
    # destination_folder_id = '1Ci6v1aQKDx5H2IZsTa44CBbvQ0xbAoNX' #V1 avec photos civils

    api_drive, api_doc, api_sheets = creer_lecteurs_google_apis()

    id = '1G2BxSQdNugGrVysWMPxTZ3ZuocBsLGlXl_HLxeFwYfs' #fichier à lire
    racine_sortie = '1xYPlwiQMPrKmry0aENzJejp8ETIqXmPP'
    destination_folder_id = g_io.creer_dossier_drive(api_drive, racine_sortie, "presque prod Manu")

    offset = 0
    copier_fiche_et_inserer_photos(api_drive, api_doc, api_sheets, sheet_id, folder_id, id,
                                   destination_folder_id, offset=offset, sheet_name='Session 1')

