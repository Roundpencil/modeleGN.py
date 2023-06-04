import contextlib
from ortools.sat.python import cp_model
from modeleGN import *


def heure_en_pas(heure_en_texte: str, pas: int):
    try:
        heure_splittee = heure_en_texte.split('h')
        minutes = int(heure_splittee[0]) * 60 + (int(heure_splittee[1]) if len(heure_splittee[1]) else 0)
        return minutes // pas
    except:
        return 0


def determiner_pas(evenements: list[Evenement]):
    minutes = {'0'}
    for evenement in evenements:
        with contextlib.suppress(Exception):
            minutes.add(evenement.heure_de_demarrage.split('h')[1])
            minutes.add(evenement.heure_de_fin.split('h')[1])

    print(f"debug : minutes avant rationalisation : {minutes}")
    maximum = max(int(m) for m in minutes if m.isnumeric())
    print(f"debug : pas trouvé avant arrondi = {maximum}")
    if maximum == 0:
        return 60
    elif maximum <= 30:
        return 30
    else:
        return 15


def creer_dict_intervenants_id(evenements: list[Evenement]):
    tous_les_intervenants = set()
    for evenement in evenements:
        for intervenant in evenement.intervenants_evenement:
            tous_les_intervenants.add(intervenant)
    return {intervenant: i for i, intervenant in enumerate(tous_les_intervenants)}


# préparer les données à partir des évènements
def evenements_2_dict_ortools(gn: GN):
    pas = determiner_pas(gn.evenements.values())
    dict_intervenants_id = creer_dict_intervenants_id(gn.evenements.values())

    evenements_formattes = []
    for evenement in gn.evenements.values():
        for i, intervention in enumerate(evenement.interventions, start=1):
            # {"start": 0, "end": 4, "pnjs": [0, 1]},
            heure_debut = heure_en_pas(intervention.heure_debut, pas)
            heure_fin = heure_en_pas(intervention.heure_fin, pas)
            if heure_fin <= heure_debut:
                heure_fin = heure_debut + 1
                # si il y a eu un soucis dans la création de l'heure de fin, on ajoute un pas par défaut
                # pour nous assurer que tous les évènements on un début et une fin
            pnjs = [dict_intervenants_id[intervenant.nom_pnj] for intervenant in intervention.liste_intervenants]
            current_dict = {"start": heure_debut,
                            "end": heure_fin,
                            "pnjs": pnjs,
                            "nom": f"{evenement.nom_evenement} - {i}"
                            }
            evenements_formattes.append(current_dict)
    return evenements_formattes, dict_intervenants_id


def proposer_affectation_pnjs(nb_pnj, nb_personnes, dict_evenements_formatte, affectations_predefinies=None):
    # Création du modèle
    if affectations_predefinies is None:
        affectations_predefinies = {}
    model = cp_model.CpModel()

    # Création des variables pour le modèle
    interventions = {}
    for evt_id, evt in enumerate(dict_evenements_formatte):
        for pnj in evt["pnjs"]:
            for p in range(nb_personnes):
                variable_name = f"evt_{evt_id}_pnj_{pnj}_p_{p}"
                interventions[variable_name] = model.NewBoolVar(variable_name)

    # Ajout des contraintes au modèle

    # Chaque PNJ doit être joué par une personne à la fois
    for evt_id, evt in enumerate(dict_evenements_formatte):
        for pnj in evt["pnjs"]:
            model.Add(sum(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] for p in range(nb_personnes)) == 1)

    # Les personnes ne peuvent pas jouer plusieurs PNJ en même temps
    for p in range(nb_personnes):
        for t in range(max(evt["end"] for evt in dict_evenements_formatte)):
            variables_a_temps_t = []
            for evt_id, evt in enumerate(dict_evenements_formatte):
                for pnj in evt["pnjs"]:
                    if evt["start"] <= t < evt["end"]:
                        variables_a_temps_t.append(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"])
            if variables_a_temps_t:
                model.Add(sum(variables_a_temps_t) <= 1)

    # Un PNJ doit être joué par la même personne tout au long du jeu
    for pnj in range(nb_pnj):
        for p1 in range(nb_personnes):
            for p2 in range(p1 + 1, nb_personnes):
                for evt_id1, evt1 in enumerate(dict_evenements_formatte):
                    for evt_id2, evt2 in enumerate(dict_evenements_formatte):
                        if pnj in evt1["pnjs"] and pnj in evt2["pnjs"]:
                            model.Add(interventions[f"evt_{evt_id1}_pnj_{pnj}_p_{p1}"] + interventions[
                                f"evt_{evt_id2}_pnj_{pnj}_p_{p2}"] <= 1)

    # Affectations prédéfinies
    for pnj, personne in affectations_predefinies.items():
        for evt_id, evt in enumerate(dict_evenements_formatte):
            if pnj in evt["pnjs"]:
                model.Add(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{personne}"] == 1)

    # Définition de l'objectif du modèle
    # ancien objectif
    # temps_total_par_personne = [model.NewIntVar(0, 100, f"temps_total_p_{p}") for p in range(nb_personnes)]
    # for p in range(nb_personnes):
    #     model.Add(temps_total_par_personne[p] == sum(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] * (evt["end"] - evt["start"]) for evt_id, evt in enumerate(evenements) for pnj in evt["pnjs"]))
    # model.Minimize(sum(temps_total_par_personne))

    temps_total_par_personne = [model.NewIntVar(0, 100, f"temps_total_p_{p}") for p in range(nb_personnes)]
    for p in range(nb_personnes):
        model.Add(temps_total_par_personne[p] == sum(
            interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] * (evt["end"] - evt["start"]) for evt_id, evt in
            enumerate(dict_evenements_formatte) for pnj in evt["pnjs"]))

    plus_petit_temps = model.NewIntVar(0, 100, "plus_petit_temps")
    for p in range(nb_personnes):
        model.Add(plus_petit_temps <= temps_total_par_personne[p])
    model.Maximize(plus_petit_temps)

    # Résoudre le modèle
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # état de la solution
    print(f"solution = {status}")
    return solver, status, interventions, temps_total_par_personne


def afficher_resultats_solver(solver, status, nb_personnes, temps_total_par_personne, evenements, interventions):
    # Afficher les résultats
    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        # if status == cp_model.OPTIMAL:
        print("Temps total par personne :")
        for p in range(nb_personnes):
            print(f"Personne {p}: {solver.Value(temps_total_par_personne[p])} minutes")

        print("\nPlanning des interventions :")
        for evt_id, evt in enumerate(evenements):
            for pnj in evt["pnjs"]:
                for p in range(nb_personnes):
                    if solver.Value(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"]) == 1:
                        print(f"Personne {p} joue le PNJ {pnj} lors de l'événement {evt_id}")
                    else:
                        print("Pas de solution trouvée.")

    # Trouver la dernière heure de fin des événements
    derniere_heure = max(evt["end"] for evt in evenements)

    # Afficher l'en-tête du planning
    print("Heure", end=";")
    for p in range(nb_personnes):
        print(f"Personne {p}", end=";")
    print()

    # Afficher les lignes du planning pour chaque heure
    for t in range(derniere_heure):
        print(t, end=";")
        for p in range(nb_personnes):
            pnj_et_evt = None
            for evt_id, evt in enumerate(evenements):
                for pnj in evt["pnjs"]:
                    if evt["start"] <= t < evt["end"] and solver.Value(
                            interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"]) == 1:
                        pnj_et_evt = f"PNJ {pnj} (Evt {evt_id})"
                        break
                if pnj_et_evt:
                    break

            if pnj_et_evt:
                print(f"\t{pnj_et_evt}", end=";")
            else:
                print("-", end=";")
        print()


####################################################################################################################

# # Définition des variables et des données d'exemple
# nb_pnj = 6
# nb_personnes = 4
# evenements = [
#     {"start": 0, "end": 4, "pnjs": [0, 1]},
#     {"start": 2, "end": 6, "pnjs": [2, 3]},
#     {"start": 5, "end": 9, "pnjs": [0]},
#     {"start": 6, "end": 7, "pnjs": [4]},
#     {"start": 15, "end": 16, "pnjs": [5]},
#     {"start": 8, "end": 13, "pnjs": [1, 3, 2]},
# ]
#
# affectations_predefinies = {
#     1: 0,  # La personne 0 jouera le PNJ 1
#     3: 2,  # La personne 2 jouera le PNJ 3
# }
#
# # Création du modèle
# model = cp_model.CpModel()
#
# # Création des variables pour le modèle
# interventions = {}
# for evt_id, evt in enumerate(evenements):
#     for pnj in evt["pnjs"]:
#         for p in range(nb_personnes):
#             variable_name = f"evt_{evt_id}_pnj_{pnj}_p_{p}"
#             interventions[variable_name] = model.NewBoolVar(variable_name)
#
# # Ajout des contraintes au modèle
#
# # Chaque PNJ doit être joué par une personne à la fois
# for evt_id, evt in enumerate(evenements):
#     for pnj in evt["pnjs"]:
#         model.Add(sum(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] for p in range(nb_personnes)) == 1)
#
# # Les personnes ne peuvent pas jouer plusieurs PNJ en même temps
# for p in range(nb_personnes):
#     for t in range(max(evt["end"] for evt in evenements)):
#         variables_a_temps_t = []
#         for evt_id, evt in enumerate(evenements):
#             for pnj in evt["pnjs"]:
#                 if evt["start"] <= t < evt["end"]:
#                     variables_a_temps_t.append(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"])
#         if variables_a_temps_t:
#             model.Add(sum(variables_a_temps_t) <= 1)
#
# # Un PNJ doit être joué par la même personne tout au long du jeu
# for pnj in range(nb_pnj):
#     for p1 in range(nb_personnes):
#         for p2 in range(p1 + 1, nb_personnes):
#             for evt_id1, evt1 in enumerate(evenements):
#                 for evt_id2, evt2 in enumerate(evenements):
#                     if pnj in evt1["pnjs"] and pnj in evt2["pnjs"]:
#                         model.Add(interventions[f"evt_{evt_id1}_pnj_{pnj}_p_{p1}"] + interventions[
#                             f"evt_{evt_id2}_pnj_{pnj}_p_{p2}"] <= 1)
#
# # Affectations prédéfinies
# for pnj, personne in affectations_predefinies.items():
#     for evt_id, evt in enumerate(evenements):
#         if pnj in evt["pnjs"]:
#             model.Add(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{personne}"] == 1)
#
# # Définition de l'objectif du modèle
# # ancien objectif
# # temps_total_par_personne = [model.NewIntVar(0, 100, f"temps_total_p_{p}") for p in range(nb_personnes)]
# # for p in range(nb_personnes):
# #     model.Add(temps_total_par_personne[p] == sum(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] * (evt["end"] - evt["start"]) for evt_id, evt in enumerate(evenements) for pnj in evt["pnjs"]))
# # model.Minimize(sum(temps_total_par_personne))
#
# temps_total_par_personne = [model.NewIntVar(0, 100, f"temps_total_p_{p}") for p in range(nb_personnes)]
# for p in range(nb_personnes):
#     model.Add(temps_total_par_personne[p] == sum(
#         interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] * (evt["end"] - evt["start"]) for evt_id, evt in
#         enumerate(evenements) for pnj in evt["pnjs"]))
#
# plus_petit_temps = model.NewIntVar(0, 100, "plus_petit_temps")
# for p in range(nb_personnes):
#     model.Add(plus_petit_temps <= temps_total_par_personne[p])
# model.Maximize(plus_petit_temps)
#
# # Résoudre le modèle
# solver = cp_model.CpSolver()
# status = solver.Solve(model)
#
# # état de la solution
# print(f"solution = {status}")

######################################################################################################################


# # Afficher les résultats
# if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
#     # if status == cp_model.OPTIMAL:
#     print("Temps total par personne :")
#     for p in range(nb_personnes):
#         print(f"Personne {p}: {solver.Value(temps_total_par_personne[p])} minutes")
#
#     print("\nPlanning des interventions :")
#     for evt_id, evt in enumerate(evenements):
#         for pnj in evt["pnjs"]:
#             for p in range(nb_personnes):
#                 if solver.Value(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"]) == 1:
#                     print(f"Personne {p} joue le PNJ {pnj} lors de l'événement {evt_id}")
#                 else:
#                     print("Pas de solution trouvée.")
#
# # Trouver la dernière heure de fin des événements
# derniere_heure = max(evt["end"] for evt in evenements)
#
# # Afficher l'en-tête du planning
# print("Heure", end=";")
# for p in range(nb_personnes):
#     print(f"Personne {p}", end=";")
# print()
#
# # Afficher les lignes du planning pour chaque heure
# for t in range(derniere_heure):
#     print(t, end=";")
#     for p in range(nb_personnes):
#         pnj_et_evt = None
#         for evt_id, evt in enumerate(evenements):
#             for pnj in evt["pnjs"]:
#                 if evt["start"] <= t < evt["end"] and solver.Value(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"]) == 1:
#                     pnj_et_evt = f"PNJ {pnj} (Evt {evt_id})"
#                     break
#             if pnj_et_evt:
#                 break
#
#         if pnj_et_evt:
#             print(f"\t{pnj_et_evt}", end=";")
#         else:
#             print("-", end=";")
#     print()


def est_ok(x):
    # Remplacez cette fonction par votre propre implémentation
    return x >= 10


def recherche_dichotomique(min_val_base, max_val_base):
    while min_val_base < max_val_base:
        milieu = (min_val_base + max_val_base) // 2
        if est_ok(milieu):
            max_val_base = milieu
        else:
            min_val_base = milieu + 1
    return min_val_base

# #code de démo recherche dichotomique
# # Remplacez min_val et max_val par les valeurs de début et de fin de votre plage
# min_val = 1
# max_val = 100
# resultat = recherche_dichotomique(min_val, max_val)
#
# print(f"Le plus petit x satisfaisant est_ok(x) est : {resultat}")

#code de test du solver :
# from MAGnet import *
# from zz_futur__tables_internvetions_PNJS import *
#
# gn = GN.load('GN Buffy')
# evts, dict_ids_noms = evenements_2_dict_ortools(gn)
# nb_personnes = 10
# solver, status, interventions, temps_total_par_personne = proposer_affectation_pnjs(len(dict_ids_noms), nb_personnes, evts)
# afficher_resultats_solver(solver, status, nb_personnes, temps_total_par_personne, evts, interventions)