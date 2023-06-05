from ortools.sat.python import cp_model
## Code création données de test :
#
# from zz_futur__tables_internvetions_PNJS import *
# from MAGnet import *
# gn = GN.load('GN Buffy')
# evenements = list(gn.evenements.values())
# little_events = evenements[:5]
# dict_evt_id = creer_dict_intervenants_id(little_events)
# data_bruts = evenements_2_dict_ortools(dict_evt_id, little_events, 60)
# data_bruts
# # Définition des variables et des données d'exemple
# from ortools.sat.python import cp_model
# from modeleGN import *

nb_pnj = 7
nb_personnes = 4
# evenements = [
#     {"start": 0, "end": 4, "pnjs": [0, 1]},
#     {"start": 2, "end": 6, "pnjs": [2, 3]},
#     {"start": 5, "end": 9, "pnjs": [0]},
#     {"start": 6, "end": 7, "pnjs": [4]},
#     {"start": 15, "end": 16, "pnjs": [5]},
#     {"start": 8, "end": 13, "pnjs": [1, 3, 2]},
# ]

evenements = [
    {'start': 15, 'end': 16, 'pnjs': ['b'], 'nom': 'E027 - Fête des sports - 1'},
    {'start': 12, 'end': 13, 'pnjs': ['c'], 'nom': 'E004-1 - coup de fil de mr wang - 1'},
    {'start': 15, 'end': 16, 'pnjs': ['e'], 'nom': 'E029 - Le conseil des élèves - 1'},
    {'start': 0, 'end': 1, 'pnjs': ['d', 'f'], 'nom': 'E015-1- Il faut sauver Charlie - 1'},
    {'start': 8, 'end': 9, 'pnjs': ['a', 'g'], 'nom': 'E008-1 - appel du conseil des observateurs - 1'}]

# evenements = [
#     {'start': 15, 'end': 16, 'pnjs': ['b'], 'nom': 'E027_-_Fête_des_sports_-_1'}, {'start': 12, 'end': 13, 'pnjs': ['c'], 'nom': 'E004-1_-_coup_de_fil_de_mr_wang_-_1'}, {'start': 15, 'end': 16, 'pnjs': ['e'], 'nom': 'E029_-_Le_conseil_des_élèves_-_1'}, {'start': 0, 'end': 1, 'pnjs': ['d', 'f'], 'nom': 'E015-1-_Il_faut_sauver_Charlie_-_1'}, {'start': 8, 'end': 9, 'pnjs': ['a', 'g'], 'nom': 'E008-1_-_appel_du_conseil_des_observateurs_-_1'}]



#todo : remplacer les énumération de personne et les pnjs par leurs noms

affectations_predefinies = {
    # 1: 0,  # La personne 0 jouera le PNJ 1
    # 3: 2,  # La personne 2 jouera le PNJ 3
}

# Création du modèle
model = cp_model.CpModel()

# Création des variables pour le modèle
interventions = {}
for evt in evenements:
    evt_id = evt['nom']
    for pnj in evt["pnjs"]:
        for p in range(nb_personnes):
            variable_name = f"evt_{evt_id}_pnj_{pnj}_p_{p}"
            interventions[variable_name] = model.NewBoolVar(variable_name)

print(f"debug : {interventions}")
# Ajout des contraintes au modèle

# Chaque PNJ doit être joué par une personne à la fois
for evt in evenements:
    evt_id = evt['nom']
    for pnj in evt["pnjs"]:
        model.Add(sum(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] for p in range(nb_personnes)) == 1)

# Les personnes ne peuvent pas jouer plusieurs PNJ en même temps
for p in range(nb_personnes):
    for t in range(max(evt["end"] for evt in evenements)):
        variables_a_temps_t = []
        for evt in evenements:
            evt_id = evt['nom']
            for pnj in evt["pnjs"]:
                if evt["start"] <= t < evt["end"]:
                    variables_a_temps_t.append(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"])
        if variables_a_temps_t:
            model.Add(sum(variables_a_temps_t) <= 1)

# Un PNJ doit être joué par la même personne tout au long du jeu
for pnj in range(nb_pnj):
    for p1 in range(nb_personnes):
        for p2 in range(p1 + 1, nb_personnes):
            for evt1 in evenements:
                evt_id1 = evt['nom']
                for evt2 in evenements:
                    evt_id2 = evt['nom']
                    if pnj in evt1["pnjs"] and pnj in evt2["pnjs"]:
                        model.Add(interventions[f"evt_{evt_id1}_pnj_{pnj}_p_{p1}"] + interventions[
                            f"evt_{evt_id2}_pnj_{pnj}_p_{p2}"] <= 1)

# Affectations prédéfinies
for pnj, personne in affectations_predefinies.items():
    for evt in evenements:
        evt_id = evt['nom']
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
        interventions[f"evt_{evt['nom']}_pnj_{pnj}_p_{p}"] * (evt["end"] - evt["start"])
            for evt in evenements for pnj in evt["pnjs"]))

# temps_total_par_personne = [model.NewIntVar(0, 100, f"temps_total_p_{p}") for p in range(nb_personnes)]
# for p in range(nb_personnes):
#     model.Add(temps_total_par_personne[p] == sum(
#         interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] * (evt["end"] - evt["start"]) for evt_id, evt in
#         enumerate(evenements) for pnj in evt["pnjs"]))

plus_petit_temps = model.NewIntVar(0, 100, "plus_petit_temps")
for p in range(nb_personnes):
    model.Add(plus_petit_temps <= temps_total_par_personne[p])
model.Maximize(plus_petit_temps)

# Résoudre le modèle
solver = cp_model.CpSolver()
status = solver.Solve(model)

# état de la solution
print(f"solution = {status}")

#####################################################################################################################


# Afficher les résultats
if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
    # if status == cp_model.OPTIMAL:
    print("Temps total par personne :")
    for p in range(nb_personnes):
        print(f"Personne {p}: {solver.Value(temps_total_par_personne[p])} minutes")

    print("\nPlanning des interventions :")
    for evt in evenements:
        evt_id = evt['nom']
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
        for evt in evenements:
            evt_id = evt['nom']
            for pnj in evt["pnjs"]:
                if evt["start"] <= t < evt["end"] and solver.Value(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"]) == 1:
                    pnj_et_evt = f"PNJ {pnj} (Evt {evt_id})"
                    break
            if pnj_et_evt:
                break

        if pnj_et_evt:
            print(f"\t{pnj_et_evt}", end=";")
        else:
            print("-", end=";")
    print()