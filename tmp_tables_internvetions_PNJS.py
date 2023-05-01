from ortools.sat.python import cp_model

# Définition des variables et des données d'exemple
nb_pnj = 4
nb_personnes = 6
evenements = [
    {"start": 0, "end": 4, "pnjs": [0, 1]},
    {"start": 2, "end": 6, "pnjs": [2, 3]},
    {"start": 5, "end": 9, "pnjs": [0]},
    {"start": 8, "end": 13, "pnjs": [1, 3, 2]},
]

affectations_predefinies = {
    1: 0,  # La personne 0 jouera le PNJ 1
    3: 2,  # La personne 2 jouera le PNJ 3
}


# Création du modèle
model = cp_model.CpModel()

# Création des variables pour le modèle
interventions = {}
for evt_id, evt in enumerate(evenements):
    for pnj in evt["pnjs"]:
        for p in range(nb_personnes):
            variable_name = f"evt_{evt_id}_pnj_{pnj}_p_{p}"
            interventions[variable_name] = model.NewBoolVar(variable_name)

# Ajout des contraintes au modèle

# Chaque PNJ doit être joué par une personne à la fois
for evt_id, evt in enumerate(evenements):
    for pnj in evt["pnjs"]:
        model.Add(sum(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] for p in range(nb_personnes)) == 1)

# Les personnes ne peuvent pas jouer plusieurs PNJ en même temps
for p in range(nb_personnes):
    for t in range(max(evt["end"] for evt in evenements)):
        variables_a_temps_t = []
        for evt_id, evt in enumerate(evenements):
            for pnj in evt["pnjs"]:
                if evt["start"] <= t < evt["end"]:
                    variables_a_temps_t.append(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"])
        if variables_a_temps_t:
            model.Add(sum(variables_a_temps_t) <= 1)

# Un PNJ doit être joué par la même personne tout au long du jeu
for pnj in range(nb_pnj):
    for p1 in range(nb_personnes):
        for p2 in range(p1+1, nb_personnes):
            for evt_id1, evt1 in enumerate(evenements):
                for evt_id2, evt2 in enumerate(evenements):
                    if pnj in evt1["pnjs"] and pnj in evt2["pnjs"]:
                        model.Add(interventions[f"evt_{evt_id1}_pnj_{pnj}_p_{p1}"] + interventions[f"evt_{evt_id2}_pnj_{pnj}_p_{p2}"] <= 1)

# Affectations prédéfinies
for pnj, personne in affectations_predefinies.items():
    for evt_id, evt in enumerate(evenements):
        if pnj in evt["pnjs"]:
            model.Add(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{personne}"] == 1)


# Définition de l'objectif du modèle
temps_total_par_personne = [model.NewIntVar(0, 100, f"temps_total_p_{p}") for p in range(nb_personnes)]
for p in range(nb_personnes):
    model.Add(temps_total_par_personne[p] == sum(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] * (evt["end"] - evt["start"]) for evt_id, evt in enumerate(evenements) for pnj in evt["pnjs"]))
model.Minimize(sum(temps_total_par_personne))

# Résoudre le modèle
solver = cp_model.CpSolver()
status = solver.Solve(model)

#état de la solution
print(f"solution = {status}")

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
