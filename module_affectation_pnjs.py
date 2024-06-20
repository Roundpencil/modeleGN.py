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

def creer_planning(gn: GN, recursion=50, pas=15,
                   observateur=lambda x, y, z: print(f"{x} itérations effectuées, "
                                                     f"temps écoulée : {y}, "
                                                     f"meilleure solution : {z}")):
    min_date = sys.maxsize
    max_date = 0

    dico_briefs, max_date, min_date = preparer_donnees_pour_planning(gn, max_date, min_date, pas)

    # maintenant, on enlève les recouvrements et on récupère les tableaux persos
    output, noms_persos = dico_brief2tableau_interventions(dico_briefs, max_date, min_date)

    # a ce statde la, on a  :
    #  - un dictionnaire avec tous les PJs et des tableaux d'évènements
    #  - le min et le max en pas qu'il y a sur le jeu

    # on veut donc :
    # préparer les données sous la forme d'un tableau qui lie, une fois fini, lie les aides aux personnages
    # isoler les personnages en doubles à deux endroits à la fois et leur crééer de l'ubiquité
    # return fournir_solutions(output)
    # return recurrer_table_evenementiel_v2(output)
    mink = len(output)
    best = output

    start_time = time.time()
    for i in range(recursion):
        k = table_evenementiel_monte_carlo(output)
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
    sol_complete = indices2solution(best, output, heures, noms_persos)
    return sol_complete


# TODO : prendre en compte les PNJs infiltrés et permanenes
# TODO : rajouter une amnière de forcer le statut minimal d'un PNJ dans le tablea des noms des PNJs

def dico_brief2tableau_interventions(dico_briefs, max_date, min_date, verbal=True):
    output = []
    noms_persos = []
    for intervenant in dico_briefs:
        stock = dico_briefs[intervenant]
        go_on = True
        nb_recursions = 0
        while go_on:
            ligne = [None] * (max_date - min_date + 1)
            futur_stock = []
            nom_a_afficher = intervenant + (f"_{nb_recursions + 1}" if nb_recursions else "")

            for i, element in enumerate(stock):

                ou_chercher = stock[i + 1:]
                start = element[0]
                end = element[1]
                integrable = True
                for autre_element in ou_chercher:
                    if autre_element[0] <= start <= autre_element[1] or autre_element[0] <= end <= autre_element[1]:
                        # alors on a un recouvrement
                        # todo : quand un evenement se recouvre avec lui-même
                        #  fusionner les deux
                        #  supprimer celui qui se recouvre du stock
                        #  trouver un moyen de refaire tourner le stock sans ajouter artificiellement un indice  
                        integrable = False
                        if verbal:
                            print(f"j'ai trouvé un élément non intégrable pour {nom_a_afficher} : "
                                  f"start = {start}, end = {end}, nom = {element[3]}")

                        break
                if integrable:
                    # suffixe = f"_{nb_recursions}" if nb_recursions else ""
                    # ligne[start - min_date:end + 1 - min_date] = \
                    #     [f"{intervenant}{suffixe} - {element[3]}"] * (end - start + 1)
                    ligne[start - min_date:end + 1 - min_date] = \
                        [f"{nom_a_afficher} - {element[3]}"] * (end - start + 1)
                else:
                    futur_stock.append(element)
            go_on = len(futur_stock)
            # print(f"futur stock = {futur_stock}")
            stock = futur_stock
            # print(f"stock = {stock}")
            nb_recursions += 1
            output.append(ligne)
            noms_persos.append(nom_a_afficher)
    return output, noms_persos


def preparer_donnees_pour_planning(gn: GN, max_date, min_date, pas):
    dico_briefs = {}
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
                clef = intervenant.str_avec_perso()
                if clef not in dico_briefs:
                    dico_briefs[clef] = []
                dico_briefs[clef].append([debut_en_pas, fin_en_pas, intervention.description, conteneur.nom_evenement])

            min_date = min(min_date, debut_en_pas)
            max_date = max(max_date, fin_en_pas)
    return dico_briefs, max_date, min_date


####################### v3 de la focntion en approche monte carlo


def table_evenementiel_monte_carlo(colonnes_source, mink=sys.maxsize):
    # hypotèse : il existe une combianison ABC  SSI AB, AC et BC sont des solutions possibles
    # hypothèse 2 : il existe une combinaison ABCD SSI ABC est possible et AD, BC, et CD sont possibles
    # et ainsi de suite
    # ainsi, je jeps réduire la recherche de solutions en prenant les paires et en cherchant toutes les combianaisons possibles
    # ensuite, je prends toutes les paires de plus haut niveau et je redescende en décomposant mon problème

    # invariant : j'ai une table de niveau N
    # SI il existe une table de niveau N+1 avec au moins un élément ALORS jer cherche une table de niveau N+2
    # SINON  j'ai fini de trouver mes  solutions

    # initialisation : création table niveau 2
    niveau = 2
    # tables = {niveau: []}
    # table_n2 = tables[2]
    table_n2 = []
    dictionnaire_combinaisons = {}
    nb_col_source = len(colonnes_source)
    range_source = range(nb_col_source)

    for i in range_source:
        for j in range(i + 1, len(colonnes_source)):
            if resultat := fusionner_colonnes(colonnes_source[i], colonnes_source[j], 0):
                dictionnaire_combinaisons[(i, j)] = resultat
                table_n2.append({i, j})

    # à ce stade là on a toutes les combinaisons niveau 2

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
        current_names = []
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

def tester_creation_planning():
    gn = GN.load('archive Chalacta.mgn')
    k = creer_planning(gn)
    _, _, sh = lecteurGoogle.creer_lecteurs_google_apis()
    g_io.write_to_sheet(sh, k, '17v9re5w-03BJ8b4tbMTPpgRA-o2Z6uIB-j6s2bD05k4')