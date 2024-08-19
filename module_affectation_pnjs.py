import time

from modeleGN import *
import google_io as g_io
from random import *


def fusionner_colonnes(a: list, b: list, verbal=0):
    if verbal:
        print(f"{'  ' * verbal} tentative de fusion : \n   {a} \n   {b}")
    if len(a) != len(b):
        return None
    result = []
    for x, y in zip(a, b):
        if x and y:
            return None
        result.append(x or y or None)
    if verbal:
        print(f"{'  ' * verbal}>résutat : {result}")
    return result


def heure_en_pas(j_formatte: str, h_formattee: str, pas: int, jplusun=False) -> int:
    # Extract the day number from j_formatte
    try:
        day_number = int(j_formatte[1:])
    except Exception:
        day_number = 0

    if jplusun:
        day_number += 1

    # Extract the hour and minute from h_formattee
    hour, minute = map(int, h_formattee.split('h'))

    # Calculate the total number of minutes (pas)
    total_minutes = (day_number * 24 * 60) + (hour * 60) + minute

    return total_minutes // pas


def pas_en_heure(nombre_de_pas: int, pas: int) -> str:
    # Calcul du nombre total de minutes
    total_minutes = nombre_de_pas * pas

    # Calcul du nombre de jours, heures et minutes
    jour = total_minutes // (24 * 60)
    minutes_restantes = total_minutes % (24 * 60)
    heure = minutes_restantes // 60
    minute = minutes_restantes % 60

    # Formattage du résultat
    resultat = f"J{jour}, {heure:02d}h{minute:02d}"
    return resultat


# # Example usage:
# result = heure_en_pas("J5", "21h34", 1)
# print(result)  # Output: 76894

def dico_brief2tableau_interventions_always(dico_pnjs_always, max_date, min_date, dico_genre, filler="En jeu"):
    lignes_persos_always, noms_persos, overlapping, genres_always = dico_brief2tableau_interventions_sans_split(
        dico_pnjs_always,
        max_date, min_date,
        dico_genre=dico_genre)

    lignes_persos_filled = []
    for ligne in lignes_persos_always:
        lignes_persos_filled.append([source or filler for source in ligne])
    return lignes_persos_filled, noms_persos, overlapping, genres_always


def dico_brief2tableau_interventions_cont(dico_pnjs_continus, max_date, min_date, dico_genre, filler='En jeu'):
    lignes_persos_cont, noms_persos, overlapping, genres_cont = dico_brief2tableau_interventions_sans_split(
        dico_pnjs_continus,
        max_date,
        min_date,
        dico_genre)

    # chaque ligne du dictionnaire contient une liste d'éléments de la forme :
    # [debut_en_pas, fin_en_pas, intervention.description, conteneur.nom_evenement])
    for i, nom_perso in enumerate(noms_persos):
        elements = dico_pnjs_continus[nom_perso]
        debut_perso = min(element[0] for element in elements)
        fin_perso = max(element[1] for element in elements)
        for j in range(debut_perso - min_date, fin_perso - min_date + 1):
            lignes_persos_cont[i][j] = lignes_persos_cont[i][j] or f"{filler} - {nom_perso}"

    return lignes_persos_cont, noms_persos, overlapping, genres_cont


def generer_table_n2(colonnes_source, table_genre, verbal=True):
    dictionnaire_combinaisons = {}
    nb_col_source = len(colonnes_source)
    range_source = range(nb_col_source)

    table_genre = table_genre or [GENRE_INDETERMINE] * len(colonnes_source)

    table_n2 = []
    for i in range_source:
        for j in range(i + 1, len(colonnes_source)):
            if verbal:
                print(f"table_genre[i] = {table_genre[i]}")
                print(f"table_genre[j] = {table_genre[j]}")
                print(f"genre indéterminé = {GENRE_INDETERMINE}")
                print(
                    f"compatibles = {table_genre[i] == table_genre[j] or table_genre[i] == GENRE_INDETERMINE or table_genre[j] == GENRE_INDETERMINE}")

            # if resultat := fusionner_colonnes(colonnes_source[i], colonnes_source[j], 0):
            if (table_genre[i] == table_genre[j] or
                table_genre[i] == GENRE_INDETERMINE or
                table_genre[j] == GENRE_INDETERMINE) and \
                    (resultat := fusionner_colonnes(colonnes_source[i], colonnes_source[j], 0)):
                dictionnaire_combinaisons[(i, j)] = resultat
                table_n2.append({i, j})
    return range_source, nb_col_source, table_n2

def creer_planning(gn: GN, recursion=50, pas=15,
                   observateur=lambda x, y, z: print(f"{x} itérations effectuées, "
                                                     f"temps écoulée : {y}, "
                                                     f"meilleure solution : {z}")):
    min_date = sys.maxsize
    max_date = 0

    dico_pnjs_anonymes, dico_pnjs_temp, dico_pnjs_continus, dico_pnjs_always, \
        max_date, min_date = preparer_donnees_pour_planning(gn, max_date, min_date, pas)

    dico_genre = {pnj.get_nom(): pnj.get_genre() for pnj in gn.get_dict_pnj().values()}

    # pnjs anonymes
    lignes_persos_ano, noms_persos_ano, _, genres_ano = dico_brief2tableau_interventions_sans_split(
        dico_pnjs_anonymes,
        max_date,
        min_date,
        dico_genre,
        merge=False,
        verbal=False)

    # maintenant, on fusionne les recouvrements et on récupère les tableaux persos pour les PNJs temporaires
    lignes_persos_tmp, noms_persos_tmp, overlapping_tmp, genres_tmp = dico_brief2tableau_interventions_sans_split(
        dico_pnjs_temp,
        max_date,
        min_date,
        dico_genre)
    # pnjs continus
    lignes_persos_cont, noms_persos_cont, overlapping_cont, genres_cont = dico_brief2tableau_interventions_cont(
        dico_pnjs_continus,
        max_date,
        min_date,
        dico_genre)
    #  - Permanents / infiltrés : tout remplir de min date à max date
    lignes_persos_always, noms_persos_always, overlapping_always, genres_always = \
        dico_brief2tableau_interventions_always(
            dico_pnjs_always,
            max_date,
            min_date,
            dico_genre)

    lignes_persos = lignes_persos_ano + lignes_persos_tmp + lignes_persos_cont + lignes_persos_always
    noms_persos = noms_persos_ano + noms_persos_tmp + noms_persos_cont + noms_persos_always
    overlapping = {**overlapping_tmp, **overlapping_cont, **overlapping_always}
    table_genre = genres_ano + genres_tmp + genres_cont + genres_always

    # a ce statde la, on a  :
    #  - un dictionnaire avec tous les PJs et des tableaux d'évènements
    #  - le min et le max en pas qu'il y a sur le jeu

    # on veut donc :
    # préparer les données sous la forme d'un tableau qui lie, une fois fini, lie les aides aux personnages

    mink = len(lignes_persos)
    best = lignes_persos

    #initialisation de la table n2 des associations 2 à deux des lignes compatibbles
    range_source, nb_col_source, table_n2 = generer_table_n2(lignes_persos, table_genre)

    start_time = time.time()
    for i in range(recursion):
        k = table_evenementiel_monte_carlo(range_source, nb_col_source, table_n2)

        if not k:
            print("solution sous optimale")
        elif len(k) < mink:
            best = k
            mink = len(k)
            print(f"mink = {mink}")
        temps_ecoule = time.time() - start_time
        observateur(i, temps_ecoule, mink)

    # onrefait les entêtes
    heures = [pas_en_heure(i, pas) for i in range(min_date, max_date + 1)]

    # return best
    sol_complete = indices2solution(best, lignes_persos, heures, noms_persos)

    # on remplaces les pas dans overlapping par des vraies valeurs d'heure
    for clef in overlapping:
        overlapping[clef] = [[pas_en_heure(date, pas), detail] for date, detail in overlapping[clef]]
    return sol_complete, overlapping


# def is_element_integrable(element:list, autres_elements:list[list], elements_a_retirer=None, verbal=True):
#     if verbal:
#         print(f"Je commence une récursion : \n"
#               f"\telement = {element}\n"
#               f"\tautres e = {autres_elements}\n"
#               f"\tretirer = {elements_a_retirer}")
#     if not elements_a_retirer:
#         elements_a_retirer = []
#     start = element[0]
#     end = element[1]
#     nom_evenement = element[3]
#     for autre_element in autres_elements:
#         if autre_element[0] <= end and start <= autre_element[1]:
#             if verbal:
#                 print(f"j'ai trouvé un élément non intégrable : "
#                       f"start = {start}, end = {end}, nom = {element[3]} à cause de {autre_element}")
#
#             if autre_element[3] == nom_evenement:
#                 # dans ce cas il s'agit du même évènement, il faut :
#                 #  - les fusionner
#                 #  - retirer l'autre du stock
#                 # ne pas mettre à jour futur stock
#                 # ne pas mettre à jour l'indice de récursions
#                 element[0] = min(start, autre_element[0])
#                 element[1] = max(end, autre_element[1])
#                 element[2] = f"{element[2]}\n{autre_element[2]}"
#                 autres_elements.remove(autre_element)
#                 elements_a_retirer.append(autre_element)
#                 if verbal:
#                     print("\taprès fusion, j'ai : \n"
#                           f"\telement = {element}\n"
#                           f"\tautres_elements = {autres_elements}\n"
#                           f"\telements à retirer = {elements_a_retirer}")
#                 # il est possible que l'élément fusionné ne soit pas compatible avec les précédents :
#                 # il faut recommencer
#                 return is_element_integrable(element, autres_elements, elements_a_retirer)
#             else:
#                 return False
#                 # les deux évènements ne sont pas compatible, il faut itérer
#         elif verbal:
#             print(f"\tl' autre_élément={autre_element} ne pose pas de soucis pour l'element={element}")
#
#     return True

# def fusionner_elements_planning(elements):
#     """
#     Merge a list of planning elements into a single element.
#
#     Parameters:
#     elements (list of lists): Each element is in the format
#                                [debut_en_pas, fin_en_pas, intervention.description, conteneur.nom_evenement]
#
#     Returns:
#     list: A merged element in the format [min_debut, max_fin, combined_descriptions, unique_event_names]
#     """
#
#     if not elements:
#         raise ValueError()
#
#     min_debut = min(element[0] for element in elements)
#     max_fin = max(element[1] for element in elements)
#     combined_descriptions = '\n'.join(element[2] for element in elements)
#     unique_event_names = '\n'.join(set(element[3] for element in elements))
#
#     merged_element = [min_debut, max_fin, combined_descriptions, unique_event_names]
#
#     return merged_element


# def is_element_integrable(element: list, autres_elements: list[list], elements_a_retirer=None, verbal=True):
#     if verbal:
#         print(f"Je commence une récursion : \n"
#               f"\telement = {element}\n"
#               f"\tautres e = {autres_elements}\n"
#               f"\tretirer = {elements_a_retirer}")
#     if elements_a_retirer is None:
#         elements_a_retirer = []
#
#     start = element[0]
#     end = element[1]
#     nom_evenement = element[3]
#
#     for autre_element in autres_elements:
#         if autre_element[0] <= end and start <= autre_element[1]:
#             if verbal:
#                 print(f"j'ai trouvé un élément non intégrable : "
#                       f"start = {start}, end = {end}, nom = {element[3]} à cause de {autre_element}")
#
#             if autre_element[3] == nom_evenement:
#                 # element[0] = min(start, autre_element[0])
#                 # element[1] = max(end, autre_element[1])
#                 # element[2] = f"{element[2]}\n{autre_element[2]}"
#                 element = fusionner_elements_planning([autre_element, element])
#
#                 autres_elements.remove(autre_element)
#                 elements_a_retirer.append(autre_element)
#
#                 if verbal:
#                     print("\taprès fusion, j'ai : \n"
#                           f"\telement = {element}\n"
#                           f"\tautres_elements = {autres_elements}\n"
#                           f"\telements à retirer = {elements_a_retirer}")
#
#                 # Recursively check again
#                 status, updated_elements_a_retirer = is_element_integrable(element, autres_elements, elements_a_retirer)
#                 return status, updated_elements_a_retirer
#             else:
#                 return False, elements_a_retirer
#         elif verbal:
#             print(f"\tl' autre_élément={autre_element} ne pose pas de soucis pour l'element={element}")
#
#     return True, elements_a_retirer


# def test_iselementintegrable():
#     stock = [[0, 5, "description1", 'evt1'], [1, 4, "description2", 'evt1'], [1, 4, "description2", 'evt2'],
#              [7, 10, "description2", 'evt1']]
#     stock.sort(key=lambda x: x[3])
#     print(f"sorted stock = {stock}")
#     retirer = []
#     test = [0, 6, "test", 'evt1']
#     print(is_element_integrable(test, stock, retirer))
#     print(stock)
#     print(test)


# def dico_brief2tableau_interventions_avec_split(dico_briefs, max_date, min_date, verbal=True):
#     """
#        Convertit un dictionnaire d'événements d'intervention en une liste de listes représentant un planning
#        d'interventions sur une plage de dates donnée. Cette fonction gère les événements qui se chevauchent
#        en créant plusieurs lignes pour la même personne si nécessaire.
#
#        Paramètres :
#        ----------
#        dico_briefs : dict
#            Un dictionnaire où les clés sont les noms des individus ('intervenants'), et les valeurs sont des listes de
#            tuples. Chaque tuple représente une intervention et contient :
#            - start (int) : La date de début de l'intervention.
#            - end (int) : La date de fin de l'intervention.
#            - name (str) : Le nom ou identifiant de l'intervention.
#
#        max_date : int
#            La date maximale considérée pour le planning, utilisée pour déterminer le nombre de colonnes dans la liste de sortie.
#
#        min_date : int
#            La date minimale considérée pour le planning, utilisée pour déterminer l'indice de départ pour chaque
#            événement dans la liste de sortie.
#
#        verbal : bool, optionnel (défaut=True)
#            Si défini à True, la fonction imprimera des messages sur les événements non intégrables qui se chevauchent.
#
#        Renvoie :
#        -------
#        output : liste de listes
#            Une liste où chaque sous-liste représente une ligne pour une personne dans le planning.
#            Chaque position dans une sous-liste
#            correspond à un jour entre `min_date` et `max_date`. Si une intervention a lieu un jour donné, la sous-liste
#            contiendra une chaîne décrivant l'intervention ; sinon, elle contiendra None.
#
#        noms_persos : liste
#            Une liste de chaînes de caractères, où chaque chaîne est le nom d'un individu avec un suffixe indiquant
#            le niveau de récursion, utilisé pour différencier plusieurs lignes pour la même personne si elle a des
#            interventions qui se chevauchent.
#
#        Remarques :
#        -----
#        - La fonction vérifie les interventions qui se chevauchent pour chaque individu. Si un chevauchement est détecté,
#          l'événement qui se chevauche est ajouté à un stock futur pour être traité lors de la prochaine récursion.
#        - Si deux événements se chevauchent, l'événement qui se chevauche n'est pas intégré dans la ligne actuelle,
#          et la fonction continue le traitement jusqu'à ce que tous les événements soient intégrés.
#        - Chaque intervention est représentée dans la sortie par une chaîne qui combine le nom de l'individu,
#          le suffixe de récursion et le nom de l'intervention.
#        - La fonction suppose que les dates et les interventions sont indexées à partir de zéro et que les valeurs
#          de `dico_briefs` contiennent des tuples d'au moins 3 éléments (start, end, name).
#        """
#     output = []
#     noms_persos = []
#     for intervenant in dico_briefs:
#         stock = dico_briefs[intervenant]
#         stock.sort(key=lambda x: x[3])  # trier par évènement pour faciliter le rapprochement
#         go_on = True
#         nb_recursions = 0
#         while go_on:
#             ligne = [None] * (max_date - min_date + 1)
#             futur_stock = []
#             nom_a_afficher = intervenant + (f"_{nb_recursions + 1}" if nb_recursions else "")
#
#             for i, element in enumerate(stock):
#
#                 ou_chercher = stock[i + 1:]
#                 integrable, elements_a_supprimer = is_element_integrable(element, ou_chercher)
#                 if integrable:
#                     start = element[0]
#                     end = element[1]
#                     nom_evenement = element[3]
#                     # suffixe = f"_{nb_recursions}" if nb_recursions else ""
#                     # ligne[start - min_date:end + 1 - min_date] = \
#                     #     [f"{intervenant}{suffixe} - {element[3]}"] * (end - start + 1)
#                     ligne[start - min_date:end + 1 - min_date] = \
#                         [f"{nom_a_afficher} - {nom_evenement}"] * (end - start + 1)
#                 else:
#                     futur_stock.append(element)
#                 # dans tous les cas, il faut retirer les éléments à supprimer
#                 stock = [element for element in stock if element not in elements_a_supprimer]
#             go_on = len(futur_stock)
#             # print(f"futur stock = {futur_stock}")
#             stock = futur_stock
#             # print(f"stock = {stock}")
#             nb_recursions += 1
#             output.append(ligne)
#             noms_persos.append(nom_a_afficher)
#     return output, noms_persos


def dico_brief2tableau_interventions_sans_split(dico_briefs, max_date, min_date, dico_genre, verbal=False, merge=True):
    lignes_tous_persos = []
    noms_persos = []
    overlapping_events = {}
    table_genre = []
    for intervenant in dico_briefs:
        # ligne = [None] * (max_date - min_date + 1)
        # start = element[0]
        # end = element[1]
        # nom_evenement = element[3]

        toutes_les_lignes_du_perso = [[None] * (element[0] - min_date) +
                                      [f"{intervenant} - {element[3]}"] * (element[1] - element[0] + 1) +
                                      [None] * (max_date - element[1])
                                      for element in dico_briefs[intervenant]]
        if verbal:
            print(f"Voici toutes les lignes pour le personnage {intervenant} : \n"
                  f"{toutes_les_lignes_du_perso}")
        # ligne_perso = ['\n'.join(filter(None, cases)) for cases in zip(*toutes_les_lignes)]

        if merge:  # dans ce cas on va merger les évènement pour ne faire qu'une seule ligne
            ligne_perso = []

            for date, cases in enumerate(zip(*toutes_les_lignes_du_perso), start=min_date):
                filtered_cases = list(filter(None, cases))
                if len(filtered_cases) > 1:
                    # If there are overlapping events
                    if intervenant not in overlapping_events:
                        overlapping_events[intervenant] = []
                    overlapping_events[intervenant].append([date, '\n'.join(filtered_cases)])
                ligne_perso.append('\n'.join(filtered_cases))
            if verbal:
                print(f"ligne perso concaténée = {ligne_perso}")

            lignes_tous_persos.append(ligne_perso)
            noms_persos.append(intervenant)
            table_genre.append(dico_genre[intervenant])
        else:  # dans ce cas, on va créer des doublons pour chaque évènement, pour les PNJs anonymes
            for i, ligne in enumerate(toutes_les_lignes_du_perso):
                nom_ligne = intervenant + f"_{i + 1}" if len(toutes_les_lignes_du_perso) > 1 else ""
                if verbal:
                    print(f"Personnage splitté : {nom_ligne}")
                    print(ligne)
                lignes_tous_persos.append(ligne)
                noms_persos.append(nom_ligne)
                table_genre.append(dico_genre[intervenant])
    return lignes_tous_persos, noms_persos, overlapping_events, table_genre


# def dico_brief2tableau_interventions_old(dico_briefs, max_date, min_date, verbal=True):
#     """
#        Convertit un dictionnaire d'événements d'intervention en une liste de listes représentant un planning
#        d'interventions sur une plage de dates donnée. Cette fonction gère les événements qui se chevauchent
#        en créant plusieurs lignes pour la même personne si nécessaire.
#
#        Paramètres :
#        ----------
#        dico_briefs : dict
#            Un dictionnaire où les clés sont les noms des individus ('intervenants'), et les valeurs sont des listes de
#            tuples. Chaque tuple représente une intervention et contient :
#            - start (int) : La date de début de l'intervention.
#            - end (int) : La date de fin de l'intervention.
#            - name (str) : Le nom ou identifiant de l'intervention.
#
#        max_date : int
#            La date maximale considérée pour le planning, utilisée pour déterminer le nombre de colonnes dans la liste de sortie.
#
#        min_date : int
#            La date minimale considérée pour le planning, utilisée pour déterminer l'indice de départ pour chaque
#            événement dans la liste de sortie.
#
#        verbal : bool, optionnel (défaut=True)
#            Si défini à True, la fonction imprimera des messages sur les événements non intégrables qui se chevauchent.
#
#        Renvoie :
#        -------
#        output : liste de listes
#            Une liste où chaque sous-liste représente une ligne pour une personne dans le planning.
#            Chaque position dans une sous-liste
#            correspond à un jour entre `min_date` et `max_date`. Si une intervention a lieu un jour donné, la sous-liste
#            contiendra une chaîne décrivant l'intervention ; sinon, elle contiendra None.
#
#        noms_persos : liste
#            Une liste de chaînes de caractères, où chaque chaîne est le nom d'un individu avec un suffixe indiquant
#            le niveau de récursion, utilisé pour différencier plusieurs lignes pour la même personne si elle a des
#            interventions qui se chevauchent.
#
#        Remarques :
#        -----
#        - La fonction vérifie les interventions qui se chevauchent pour chaque individu. Si un chevauchement est détecté,
#          l'événement qui se chevauche est ajouté à un stock futur pour être traité lors de la prochaine récursion.
#        - Si deux événements se chevauchent, l'événement qui se chevauche n'est pas intégré dans la ligne actuelle,
#          et la fonction continue le traitement jusqu'à ce que tous les événements soient intégrés.
#        - Chaque intervention est représentée dans la sortie par une chaîne qui combine le nom de l'individu,
#          le suffixe de récursion et le nom de l'intervention.
#        - La fonction suppose que les dates et les interventions sont indexées à partir de zéro et que les valeurs
#          de `dico_briefs` contiennent des tuples d'au moins 3 éléments (start, end, name).
#        """
#     output = []
#     noms_persos = []
#     for intervenant in dico_briefs:
#         stock = dico_briefs[intervenant]
#         stock.sort(key=lambda x: x[3])  # trier par évènement pour faciliter le rapprochement
#         go_on = True
#         nb_recursions = 0
#         while go_on:
#             ligne = [None] * (max_date - min_date + 1)
#             futur_stock = []
#             nom_a_afficher = intervenant + (f"_{nb_recursions + 1}" if nb_recursions else "")
#
#             for i, element in enumerate(stock):
#
#                 ou_chercher = stock[i + 1:]
#                 start = element[0]
#                 end = element[1]
#                 nom_evenement = element[3]
#                 integrable = True
#                 for autre_element in ou_chercher:
#                     if autre_element[0] <= start <= autre_element[1] or autre_element[0] <= end <= autre_element[1]:
#                         # alors on a un recouvrement
#                         # ce qui ne marche pas ici : quand un evenement se recouvre avec lui-même
#                         #  fusionner les deux dès l'étape précédente de création
#                         #  supprimer celui qui se recouvre du stock
#                         #  trouver un moyen de refaire tourner le stock sans ajouter artificiellement un indice
#                         integrable = False
#                         if verbal:
#                             print(f"j'ai trouvé un élément non intégrable pour {nom_a_afficher} : "
#                                   f"start = {start}, end = {end}, nom = {element[3]}")
#
#                         break
#                 if integrable:
#                     start = element[0]
#                     end = element[1]
#                     nom_evenement = element[3]
#                     # suffixe = f"_{nb_recursions}" if nb_recursions else ""
#                     # ligne[start - min_date:end + 1 - min_date] = \
#                     #     [f"{intervenant}{suffixe} - {element[3]}"] * (end - start + 1)
#                     ligne[start - min_date:end + 1 - min_date] = \
#                         [f"{nom_a_afficher} - {nom_evenement}"] * (end - start + 1)
#                 else:
#                     futur_stock.append(element)
#             go_on = len(futur_stock)
#             # print(f"futur stock = {futur_stock}")
#             stock = futur_stock
#             # print(f"stock = {stock}")
#             nb_recursions += 1
#             output.append(ligne)
#             noms_persos.append(nom_a_afficher)
#     return output, noms_persos


def preparer_donnees_pour_planning(gn: GN, max_date, min_date, pas, verbal=False):
    dico_pnjs_temp = {}
    dico_pnjs_continus = {}
    dico_pnjs_always = {}
    dico_pnj_anonymes = {}
    conteneurs_evts = gn.lister_tous_les_conteneurs_evenements_unitaires()
    for conteneur in conteneurs_evts:
        for intervention in conteneur.interventions:
            h_debut = intervention.heure_debut_formattee()
            jour = intervention.jour_formatte()
            debut_en_pas = heure_en_pas(jour, h_debut, pas)

            h_fin = intervention.heure_fin_formattee()
            if h_fin:
                fin_en_pas = heure_en_pas(jour, h_fin, pas)
                if fin_en_pas < debut_en_pas:
                    fin_en_pas = heure_en_pas(jour, h_fin, pas, jplusun=True)
            else:
                fin_en_pas = debut_en_pas

            intervenants = intervention.liste_intervenants
            for intervenant in intervenants:
                if verbal:
                    print(f"*** {intervenant.get_nom_pnj_associe()} - {intervenant.get_type_PNJ_from_roles()}")
                # clef = intervenant.str_avec_perso()
                clef = intervenant.get_nom_pnj_associe()
                if intervenant.get_type_PNJ_from_roles() == TypePerso.EST_PNJ_CONTINU:
                    dico_cible = dico_pnjs_continus
                elif intervenant.get_type_PNJ_from_roles() in [TypePerso.EST_PNJ_PERMANENT, TypePerso.EST_PNJ_INFILTRE]:
                    dico_cible = dico_pnjs_always
                elif intervenant.get_type_PNJ_from_roles() == TypePerso.EST_PNJ_ANONYME:
                    dico_cible = dico_pnj_anonymes
                else:
                    dico_cible = dico_pnjs_temp
                if clef not in dico_cible:
                    # dico_pnjs_temp[clef] = []
                    dico_cible[clef] = []
                # dico_pnjs_temp[clef].append(
                #     [debut_en_pas, fin_en_pas, intervention.description, conteneur.nom_evenement])
                dico_cible[clef].append(
                    [debut_en_pas, fin_en_pas, intervention.description, conteneur.nom_evenement])

            min_date = min(min_date, debut_en_pas)
            max_date = max(max_date, fin_en_pas)
    return dico_pnj_anonymes, dico_pnjs_temp, dico_pnjs_continus, dico_pnjs_always, max_date, min_date


####################### v3 de la focntion en approche monte carlo


def table_evenementiel_monte_carlo(range_source, nb_col_source, table_n2, mink=sys.maxsize, verbal=True):
    # hypotèse : il existe une combianison ABC  SSI AB, AC et BC sont des solutions possibles
    # hypothèse 2 : il existe une combinaison ABCD SSI ABC est possible et AD, BC, et CD sont possibles
    # et ainsi de suite
    # ainsi, je jeps réduire la recherche de solutions en prenant les paires et en cherchant toutes les combianaisons possibles
    # ensuite, je prends toutes les paires de plus haut niveau et je redescende en décomposant mon problème

    # invariant : j'ai une table de niveau N
    # SI il existe une table de niveau N+1 avec au moins un élément ALORS jer cherche une table de niveau N+2
    # SINON  j'ai fini de trouver mes  solutions


    # à ce stade là on a toutes les combinaisons niveau 2 > cf entrée

    ### on commence par setuper toutes les variables dont on aura besoin
    # dico_candidats = {-1: []} # on itnitialise -1 pour avoir tout dans la brique de base
    dico_candidats = {}  # on itnitialise -1 pour avoir tout dans la brique de base
    for a, b in table_n2:
        if a not in dico_candidats:
            dico_candidats[a] = set()
            # dico_candidats[a] = [-1]
            # dico_candidats[-1].append(a)
        if b not in dico_candidats:
            dico_candidats[b] = set()
            # dico_candidats[b] = [-1]
            # dico_candidats[-1].append(b)
        dico_candidats[a].add(b)
        dico_candidats[b].add(a)

    # un dictionnaire qui permet de stocker les colonnes qu'on ne peut plus combiner, et comment elles ont été composées
    solutions = {n: {n} for n in range_source if n not in dico_candidats.keys()}

    # un dictionnaire qui permet de se souvenir de comment chaque colonne a été composée
    combinaisons = {n: {n} for n in dico_candidats.keys()}
    # combinaisons = {n: {n} for n in range_source}

    premier_indice_libre = nb_col_source

    # invariant : on a une colonne source, et plusieurs colonnes candidates
    # on chosit une colonne candidate aléatoirement
    # on la fusionne
    # on retire la colonne candidate des colonnes existantes et la colonne fucionnée pour en faire une nouvelle
    # on met à jour la table des combinatoires avec la nouvelle colonne fusionnée
    # on garde quelque part les "recettes" des colonnes fusionnées
    # si une colonne ne peut plus fusionner avec rien (tableau vide), elle devient résolue

    while dico_candidats:
        # on chosit deux colonnes candidate aléatoirement
        colonne_source = choices(list(dico_candidats.keys()))[0]
        colonne_candidate = choices(list(dico_candidats[colonne_source]))[0]

        # on retire la colonne candidate des colonnes existantes et la colonne fusionnée pour en faire une nouvelle
        indice_nouvelle_colonne = premier_indice_libre
        premier_indice_libre += 1

        combinaisons[indice_nouvelle_colonne] = combinaisons[colonne_source] | combinaisons[colonne_candidate]
        del combinaisons[colonne_source]
        del combinaisons[colonne_candidate]

        # on met à jour la table des combinatoires avec la nouvelle colonne fusionnée
        partenaires_source = dico_candidats[colonne_source]
        partenaires_candidats = dico_candidats[colonne_candidate]

        partenaires_source.remove(colonne_candidate)
        partenaires_candidats.remove(colonne_source)

        # on calcule qui gagne les deux
        intersection = partenaires_candidats & partenaires_source

        # et on met à jour
        if len(intersection):
            dico_candidats[indice_nouvelle_colonne] = intersection
            for partenaire in intersection:
                dico_candidats[partenaire].add(indice_nouvelle_colonne)
        else:
            # si il n'y a personne en commun, c'est qu'on a atteint la limite
            # cette colonne rejoint les solutions
            solutions[indice_nouvelle_colonne] = combinaisons[indice_nouvelle_colonne]

        # on nettoie et met à jour
        for partenaire in partenaires_source:
            dico_candidats[partenaire].remove(colonne_source)
            if not len(dico_candidats[partenaire]):
                del dico_candidats[partenaire]
                solutions[partenaire] = combinaisons[partenaire]

        for partenaire in partenaires_candidats:
            dico_candidats[partenaire].remove(colonne_candidate)
            if not len(dico_candidats[partenaire]):
                del dico_candidats[partenaire]
                solutions[partenaire] = combinaisons[partenaire]

        del dico_candidats[colonne_source]
        del dico_candidats[colonne_candidate]
        if len(solutions) >= mink:
            print(f"mink = {mink}, len(solutions) = {len(solutions)}")
            return None

        # print(dico_candidats)
        # print(premier_indice_libre)
        # print(solution)

    # on dépile les solutions
    def deplier_valeur(set_de_depart: set):
        for valeur in set_de_depart:
            if valeur >= nb_col_source:
                set_de_depart.remove(valeur)
                set_de_depart |= deplier_valeur(combinaisons[valeur])
        return set_de_depart

    # print(f"nb_colonnes = {nb_col_source}")
    solution_depliee = {}
    for key in solutions:
        solution_depliee[key] = deplier_valeur(solutions[key])

    return solution_depliee
    # return solutions


def indices2solution(solution_depliee, colonnes_source, colonne_heure, noms_persos):
    solution_complete = [['', ''] + colonne_heure]
    for i, key in enumerate(solution_depliee, start=1):
        # current_names = []
        # print(f"clef en cours : {key}")
        indices_colonnes = list(solution_depliee[key])
        to_add = colonnes_source[indices_colonnes[0]]
        current_names = [noms_persos[indices_colonnes[0]]]
        for indice in indices_colonnes[1:]:
            to_add = fusionner_colonnes(to_add, colonnes_source[indice])
            current_names.append(noms_persos[indice])

        to_add = [f"PNJ {i}"] + [" / ".join(current_names)] + to_add
        solution_complete.append(to_add)
    # puis on inverse la matrice
    # return solution_complete
    return [[solution_complete[j][i] for j in range(len(solution_complete))] for i in range(len(solution_complete[0]))]


def formatter_overlapping_pour_export(overlapping: dict[str, list[str]]):
    to_export = ""
    for nom in overlapping:
        to_export += lecteurGoogle.formatter_gras(nom) + '\n'
        to_export += lecteurGoogle.formatter_tableau_pour_export(overlapping[nom]) + '\n' * 2
    return to_export


def tester_creation_planning():
    gn = GN.load('archive Chalacta.mgn')
    k, _ = creer_planning(gn)
    _, _, sh = lecteurGoogle.creer_lecteurs_google_apis()
    g_io.write_to_sheet(sh, k, '17v9re5w-03BJ8b4tbMTPpgRA-o2Z6uIB-j6s2bD05k4')
