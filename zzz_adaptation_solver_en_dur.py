from ortools.sat.python import cp_model

from google_io import evenement_extraire_ligne_chrono
from modeleGN import *


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

# code identification nb pnjs simultanés nécessaires :
# mini = min(evt['start'] for evt in evenements)
# maxi = max(evt['end'] for evt in evenements)
# cumul = {i: 0 for i in range(mini, maxi + 1)}
# for evt in evenements:
#     for t in range(mini, maxi + 1):
#         if evt['start'] <= t < evt['end']:
#             cumul[t] += len(evt['pnjs'])
#
# nb_pnjs_necessaires = max([cumul[t] for t in range(mini, maxi + 1)])

def construire_timing_pnjs(evenements, aides: list[str], affectations_predefinies=None, consever_liens_aides_pnjs=True):
    if affectations_predefinies is None:
        affectations_predefinies = {}
    pnjs = {pnj for evenement in evenements for pnj in evenement['pnjs']}

    # Création du modèle
    model = cp_model.CpModel()

    # Création des variables pour le modèle
    interventions = {}
    for evt in evenements:
        evt_id = evt['nom']
        for pnj in evt["pnjs"]:
            for p in aides:
                variable_name = f"evt_{evt_id}_pnj_{pnj}_p_{p}"
                interventions[variable_name] = model.NewBoolVar(variable_name)

    # print(f"debug : {interventions}")
    # Ajout des contraintes au modèle

    # Chaque PNJ doit être joué par une personne à la fois
    for evt in evenements:
        evt_id = evt['nom']
        for pnj in evt["pnjs"]:
            model.Add(sum(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] for p in aides) == 1)

    # Les personnes ne peuvent pas jouer plusieurs PNJ en même temps
    for p in aides:
        for t in range(max(evt["end"] for evt in evenements)):
            variables_a_temps_t = []
            for evt in evenements:
                evt_id = evt['nom']
                for pnj in evt["pnjs"]:
                    if evt["start"] <= t < evt["end"]:
                        variables_a_temps_t.append(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"])
            if variables_a_temps_t:
                model.Add(sum(variables_a_temps_t) <= 1)

    if consever_liens_aides_pnjs:
        # Un PNJ doit être joué par la même personne tout au long du jeu
        for pnj in pnjs:
            for i, p1 in enumerate(aides):
                for p2 in aides[i + 1:]:
                    # for p2 in range(p1 + 1, nb_personnes):
                    for evt1 in evenements:
                        evt_id1 = evt1['nom']
                        for evt2 in evenements:
                            evt_id2 = evt2['nom']
                            if pnj in evt1["pnjs"] and pnj in evt2["pnjs"]:
                                # print(f"debug : evt1 = {evt1} \n"
                                #       f"evt2 = {evt2} \n"
                                #       f"pnjs evts1 = {evt1['pnjs']} \n "
                                #       f"pnjs evts2 = {evt2['pnjs']}")
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
    # temps_total_par_personne = [model.NewIntVar(0, 100, f"temps_total_p_{p}") for p in aides]
    # for p in aides:
    #     model.Add(temps_total_par_personne[p] == sum(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] * (evt["end"] - evt["start"]) for evt_id, evt in enumerate(evenements) for pnj in evt["pnjs"]))
    # model.Minimize(sum(temps_total_par_personne))

    temps_total_par_personne = [model.NewIntVar(0, 100, f"temps_total_p_{p}") for p in aides]
    for i, p in enumerate(aides):
        model.Add(temps_total_par_personne[i] == sum(
            interventions[f"evt_{evt['nom']}_pnj_{pnj}_p_{p}"] * (evt["end"] - evt["start"])
            for evt in evenements for pnj in evt["pnjs"]))

    # temps_total_par_personne = [model.NewIntVar(0, 100, f"temps_total_p_{p}") for p in aides]
    # for p in aides:
    #     model.Add(temps_total_par_personne[p] == sum(
    #         interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"] * (evt["end"] - evt["start"]) for evt_id, evt in
    #         enumerate(evenements) for pnj in evt["pnjs"]))

    plus_petit_temps = model.NewIntVar(0, 100, "plus_petit_temps")
    for i, p in enumerate(aides):
        model.Add(plus_petit_temps <= temps_total_par_personne[i])
    model.Maximize(plus_petit_temps)

    # Résoudre le modèle
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # état de la solution
    print(f"solution = {status}")

    #####################################################################################################################

    # Afficher les résultats
    if status not in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        return None
    # if status == cp_model.OPTIMAL:
    print("Temps total par personne :")
    for i, p in enumerate(aides):
        print(f"Personne {p}: {solver.Value(temps_total_par_personne[i])} unités de temps")

    print("\nPlanning des interventions :")
    for evt in evenements:
        evt_id = evt['nom']
        for pnj in evt["pnjs"]:
            for p in aides:
                if solver.Value(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"]) == 1:
                    print(f"Personne {p} joue le PNJ {pnj} lors de l'événement {evt_id}")
                # else:
                #     print("Pas de solution trouvée.")

    # # Afficher les résultats
    # if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
    #     # if status == cp_model.OPTIMAL:
    #     print("Temps total par personne :")
    #     for i, p in enumerate(aides):
    #         print(f"Personne {p}: {solver.Value(temps_total_par_personne[i])} minutes")
    #
    #     print("\nPlanning des interventions :")
    #     for evt in evenements:
    #         evt_id = evt['nom']
    #         for pnj in evt["pnjs"]:
    #             for p in aides:
    #                 if solver.Value(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"]) == 1:
    #                     print(f"Personne {p} joue le PNJ {pnj} lors de l'événement {evt_id}")
    #                 # else:
    #                 #     print("Pas de solution trouvée.")
    #
    # Trouver la dernière heure de fin des événements
    premiere_heure = min(evt["start"] for evt in evenements)
    derniere_heure = max(evt["end"] for evt in evenements)

    # construire table planning
    table_planning = [["Heure", "Evenement(s)"] + list(aides)]

    # construire les lignes du planning pour chaque heure
    for t in range(premiere_heure, derniere_heure):
        current_ligne = [t, ""]
        for p in aides:
            pnj_et_evt = None
            for evt in evenements:
                evt_id = evt['nom']
                if evt["start"] <= t < evt["end"]:
                    # ajouter le nom de l'évènement dans la colonne dédiée
                    if evt_id not in current_ligne[1]:
                        current_ligne[1] += f'\n{evt_id}'
                        # current_ligne[1] += f'\n{evt_id}'

                    # remplir es colonnes des PNJs
                    for pnj in evt["pnjs"]:
                        if solver.Value(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"]) == 1:
                            pnj_et_evt = f"{pnj} ({evt_id})"
                        break
                if pnj_et_evt:
                    break

            current_ligne.append(pnj_et_evt or "")
            # if pnj_et_evt:
            #     # print(f"\t{pnj_et_evt}", end=";")
            #     current_ligne.append(pnj_et_evt)
            # else:
            #     print("-", end=";")
        table_planning.append(current_ligne)

    return table_planning
    #
    # # Afficher l'en-tête du planning
    # print("Heure", end=";")
    # for p in aides:
    #     print(f"{p}", end=";")
    # print()
    #
    # # Afficher les lignes du planning pour chaque heure
    # for t in range(premiere_heure, derniere_heure):
    #     print(t, end=";")
    #     for p in aides:
    #         pnj_et_evt = None
    #         for evt in evenements:
    #             evt_id = evt['nom']
    #             for pnj in evt["pnjs"]:
    #                 if evt["start"] <= t < evt["end"] and solver.Value(interventions[f"evt_{evt_id}_pnj_{pnj}_p_{p}"]) == 1:
    #                     pnj_et_evt = f"{pnj} ({evt_id})"
    #                     break
    #             if pnj_et_evt:
    #                 break
    #
    #         if pnj_et_evt:
    #             print(f"\t{pnj_et_evt}", end=";")
    #         else:
    #             print("-", end=";")
    #     print()


def generer_tableau_aide(nb_aides, aides_connus=None):
    if aides_connus is None:
        aides_connus = []
    aides_a_ajouter = max(nb_aides - len(aides_connus), 0)
    return aides_connus + [f"aide {i}" for i in range(1, aides_a_ajouter + 1)]


def recherche_dichotomique_aides(evenements, min_aides=0, max_aides=100, aides_connus=None,
                                 consever_liens_aides_pnjs=True):
    table_planning = None
    while min_aides < max_aides:
        print(f"debug : min actuel = {min_aides} / max actuel = {max_aides}")
        milieu = (min_aides + max_aides) // 2
        aides_testes = generer_tableau_aide(milieu, aides_connus)
        if table_planning := construire_timing_pnjs(evenements, aides_testes,
                                                    consever_liens_aides_pnjs=consever_liens_aides_pnjs):
            max_aides = milieu
        else:
            min_aides = milieu + 1
    if table_planning:
        return table_planning
    else:
        return construire_timing_pnjs(evenements, generer_tableau_aide(min(min_aides + 1, max_aides), aides_connus),
                                      consever_liens_aides_pnjs=consever_liens_aides_pnjs)

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

def preparer_donnees_pour_ortools(gn: GN, pas=None):
    if pas is None:
        pas = determiner_pas(gn.evenements.values())
        print(f'debug : pas final = {pas}')

    return evenements_2_dict_ortools(gn.evenements.values(), pas)


def evenements_2_dict_ortools(liste_evenements: list[Evenement], pas):
    evenements_formattes = []
    for evenement in liste_evenements:
        for i, intervention in enumerate(evenement.interventions, start=1):
            # {"start": 0, "end": 4, "pnjs": [0, 1]},
            jour_nombre = int(''.join(chiffre for chiffre in texte if chiffre.isdigit()))
            heure_debut = heure_en_pas(intervention.heure_debut, pas) + jour_nombre * 100
            heure_fin = heure_en_pas(intervention.heure_fin, pas) + jour_nombre * 100
            if heure_fin <= heure_debut:
                heure_fin = heure_debut + 1
                # si il y a eu un soucis dans la création de l'heure de fin, on ajoute un pas par défaut
                # pour nous assurer que tous les évènements on un début et une fin
            pnjs = [intervenant.pnj.nom for intervenant in intervention.liste_intervenants]
            current_dict = {"start": heure_debut,
                            "end": heure_fin,
                            "pnjs": pnjs,
                            "nom": f"{evenement.nom_evenement} - {i}"
                            }
            evenements_formattes.append(current_dict)
    return evenements_formattes

def heure_en_pas(heure_en_texte: str, pas: int):
    try:
        heure_splittee = heure_en_texte.split('h')
        minutes = int(heure_splittee[0]) * 60 + (int(heure_splittee[1]) if len(heure_splittee[1]) else 0)
        return minutes // pas
    except:
        return 0


def main():
    evenements = [{'start': 60, 'end': 61, 'pnjs': ['Foster - Magnet'], 'nom': 'E027 - Fête des sports - 1'},
                  {'start': 48, 'end': 49, 'pnjs': ['Ms. Beakman'], 'nom': 'E004-1 - coup de fil de mr wang - 1'},
                  {'start': 60, 'end': 61, 'pnjs': ['Snyder - Magnet'], 'nom': 'E029 - Le conseil des élèves - 1'},
                  {'start': 0, 'end': 1, 'pnjs': ['Charlie - Magnet', 'Ruth Greeliegh - Infirmière - Magnet'],
                   'nom': 'E015-1- Il faut sauver Charlie - 1'},
                  {'start': 35, 'end': 36, 'pnjs': ['PNJ Statue'],
                   'nom': 'E008-1 - appel du conseil des observateurs - 1'},
                  {'start': 34, 'end': 35, 'pnjs': ['Première tueuse'], 'nom': 'E022-1 - La nouvelle tueuse - 1'},
                  {'start': 57, 'end': 58, 'pnjs': ['Snyder - Magnet'],
                   'nom': 'E020 - Convocation des Cordettes chez Snyder - 1'},
                  {'start': 0, 'end': 1, 'pnjs': ['Gardien du cimetière'],
                   'nom': 'E023-3 - Choix de la faux par la nouvelle tueuse - 1'},
                  {'start': 94, 'end': 95, 'pnjs': ['Gardien du cimetière'],
                   'nom': 'E023-1 - Rencontre Gage vs Gardienne - 1'},

                  {'start': 56, 'end': 57, 'pnjs': ['PNJ MESSAGE'], 'nom': 'E025-1 - Le Club de Science - 1'},

                  {'start': 72, 'end': 73, 'pnjs': ['PNJ torrance 1', 'PNJ Torrance 2'],
                   'nom': 'E014-1 - Attaque de l’équipe pendant le dogball - 1'},
                  {'start': 0, 'end': 1, 'pnjs': ['PNJ MESSAGE'], 'nom': 'E013-1 - Peter Clarner devient Crochet - 1'},
                  {'start': 36, 'end': 37, 'pnjs': ['PNJ MESSAGE'],
                   'nom': 'E100-8 - Arrivée des élèves pour les cours - 1'},
                  {'start': 76, 'end': 77, 'pnjs': ['Snyder - Magnet'], 'nom': 'E100-10 - La soirée d’adieu - 1'},
                  {'start': 44, 'end': 45, 'pnjs': ['Eleonore Abernathy. la Vieille  aux chats'],
                   'nom': 'E048-1 - Eleonore Abernaty is back - 1'},

                  # {'start': 82, 'end': 83, 'pnjs': ['Jackson Hunt - Magnet'], 'nom': 'E017-2 - Mon père, ce héros Reprise - 1'},
                  {'start': 70, 'end': 71, 'pnjs': ['PNJ torrance 1'],
                   'nom': 'E035-3- Vengeance du lycée de Torrance - 1'},

                  {'start': 70, 'end': 71, 'pnjs': ['PNJ torrance 1'],
                   'nom': 'E035-3- Vengeance du lycée de Torrance - 2'},
                  {'start': 36, 'end': 37, 'pnjs': ['Foster - Magnet', 'Joy Bennet'],
                   'nom': "E034-1 - Sélection des pompoms de l'année prochaine - 1"},
                  {'start': 91, 'end': 92, 'pnjs': ['PNJ MESSAGE'], 'nom': 'E010-1 - Effets secondaires Larry - 1'},
                  {'start': 94, 'end': 95, 'pnjs': ['PNJ MESSAGE'], 'nom': 'E006-1 -  Cauchemar Wendell - 1'},
                  {'start': 0, 'end': 1, 'pnjs': ['clown de Zoé'], 'nom': 'E005-1 - la fuite du clown de Zoé - 1'},
                  {'start': 0, 'end': 1, 'pnjs': ['Vendeur de bananes de Larry'],
                   'nom': 'E005-2 - la fuite du marchand de bananes de Larry - 1'},
                  {'start': 92, 'end': 93, 'pnjs': ['Aradia - Intrigue 006 - La vigilante Malgrès elle'],
                   'nom': "E006-3 - Sortie d'Aradia Rituel - 1"},
                  {'start': 4, 'end': 5, 'pnjs': ['Aradia - Intrigue 006 - La vigilante Malgrès elle', 'PNJ MESSAGE'],
                   'nom': "E006-3 - Sortie d'Aradia Rituel - 2"},
                  {'start': 64, 'end': 65, 'pnjs': ['Snyder - Magnet'],
                   'nom': 'E026-3 - Annonce à Snyder des résultats du meilleur projet caritatif - 1'},
                  {'start': 40, 'end': 41, 'pnjs': ['PNJ MESSAGE'],
                   'nom': 'E026-1 - Vote pour le meilleur projet caritatif - 1'},
                  {'start': 80, 'end': 81, 'pnjs': ['Snyder - Magnet'], 'nom': 'E048-2 - Tags du lycée - 1'},
                  {'start': 38, 'end': 39, 'pnjs': ['Snyder - Magnet'],
                   'nom': 'E100-9 - Discour de Snyder - Matinée - 1'},
                  {'start': 56, 'end': 57, 'pnjs': ['PNJ MESSAGE'],
                   'nom': "E100-3 - Début d'arrivée des PJ /Parking et placement en chambre / Brief individuel - 1"},
                  {'start': 94, 'end': 95, 'pnjs': ['Le Maître'],
                   'nom': 'E046-1 Cauchemar “rencontre avec le Maître” - 1'},
                  {'start': 32, 'end': 33, 'pnjs': ['PNJ MESSAGE'], 'nom': 'E046-3 - Lettre du père Lancaster - 1'},
                  {'start': 36, 'end': 37, 'pnjs': ['Snyder - Magnet'],
                   'nom': 'E037 - Annonce de la mort de Cordélia - 1'},
                  {'start': 0, 'end': 1, 'pnjs': ['Ellen Brooks'],
                   'nom': 'E061-2 - Séance de spiritisme Ellen Brooks - 1'},
                  {'start': 57, 'end': 58, 'pnjs': ['Ellen Brooks'], 'nom': 'E061-1 - Intervention d’Ellen Brooks - 1'},
                  {'start': 55, 'end': 56, 'pnjs': ['Infirmier 1'], 'nom': 'E070-3 - Infirmiers en collecte - 1'},
                  {'start': 40, 'end': 41, 'pnjs': ['Ruth Greeliegh - Infirmière - Magnet'],
                   'nom': 'E070-2 - Collecte de sang - 1'},
                  {'start': 40, 'end': 41, 'pnjs': ['Ruth Greeliegh - Infirmière - Magnet'],
                   'nom': 'E070-2 - Collecte de sang - 2'}, {'start': 40, 'end': 41, 'pnjs': ['Snyder - Magnet'],
                                                             'nom': 'E070-1- Annonce que la collecte de sang est ouverte '
                                                                    '- 1'},
                  {'start': 64, 'end': 65, 'pnjs': ['Snyder - Magnet', 'Max Miller', 'PNJ MESSAGE'],
                   'nom': 'E002-5 - Interrogatoire sur le Sunnycola - 1'},
                  {'start': 58, 'end': 59, 'pnjs': ['PNJ MESSAGE'],
                   'nom': 'E002-4 - Intervention de la brigade '
                          'sanitaire - 1'},
                  {'start': 44, 'end': 45, 'pnjs': ['PNJ MESSAGE'], 'nom': 'E002-3 - Livraison de Sunnycola - 1'},
                  {'start': 88, 'end': 89, 'pnjs': ['Snyder - Magnet'],
                   'nom': 'E002-2 - Dépouillement et annonce des résultats - 1'},
                  {'start': 90, 'end': 91, 'pnjs': ['Max Miller'],
                   'nom': 'E002-2 - Dépouillement et annonce des résultats - 2'},
                  {'start': 76, 'end': 77, 'pnjs': ['PNJ MESSAGE'],
                   'nom': 'E002-1 - Vote pour le mannequin vedette Sunnycola - 1'},
                  {'start': 8, 'end': 9, 'pnjs': ['Le Maître', 'Ruth Greeliegh - Infirmière - Magnet'],
                   'nom': 'E046-4 - Appel du Maitre - 1'},
                  {'start': 95, 'end': 96, 'pnjs': ['Ruth Greeliegh - Infirmière - Magnet'],
                   'nom': 'E046-2 - Cauchemar Bonus Holly - 1'},
                  {'start': 75, 'end': 76, 'pnjs': ['PNJ torrance 1', 'PNJ Torrance 2'],
                   'nom': 'E014-2 -Echanges des trophées - 1'},
                  {'start': 92, 'end': 93, 'pnjs': ['Jackson Hunt - Magnet'], 'nom': 'E017-1 - Mon père, ce héros - 1'},
                  {'start': 92, 'end': 93, 'pnjs': ['Gardien du cimetière'],
                   'nom': 'E003-1 - Hommage au Professeur Baird - 1'},
                  {'start': 60, 'end': 61, 'pnjs': ['Ignace'], 'nom': "E007-1 - Convocation de l'UAI - 1"}
                  ]

    # evenements = [
    #     {'start': 15, 'end': 16, 'pnjs': ['Foster - Magnet'], 'nom': 'E027 - Fête des sports - 1'},
    #     {'start': 12, 'end': 13, 'pnjs': ['Ms. Beakman'], 'nom': 'E004-1 - coup de fil de mr wang - 1'},
    #     {'start': 15, 'end': 16, 'pnjs': ['Snyder - Magnet'], 'nom': 'E029 - Le conseil des élèves - 1'},
    #     {'start': 0, 'end': 1, 'pnjs': ['Charlie - Magnet', 'Ruth Greeliegh - Infirmière - Magnet'], 'nom': 'E015-1- Il '
    #                                                                                                         'faut sauver '
    #                                                                                                         'Charlie - 1'},
    #     {'start': 8, 'end': 9, 'pnjs': ['PNJ Statue'], 'nom': 'E008-1 - appel du conseil des observateurs - 1'}]

    # pnjs = ['b', 'c', 'e', 'd', 'f', 'a']
    # pnjs = []
    # for evenement in evenements:
    #     pnjs.extend(evenement['pnjs'])
    # pnjs = set(pnjs)

    # pnjs = {pnj for evenement in evenements for pnj in evenement['pnjs']}

    # aides = ['aide 0', 'aide 1', 'aide 2', 'aide 3']

    affectations_predefinies = {
        # 'aide 0': 'b',  # La personne 0 jouera le PNJ 1
        # 'aide 2': 'c',  # La personne 2 jouera le PNJ 3
    }

    # table_planning = construire_timing_pnjs()

    table_planning = recherche_dichotomique_aides(evenements, min_aides=1, max_aides=30,
                                                  consever_liens_aides_pnjs=False)

    # table_planning = construire_timing_pnjs(evenements, generer_tableau_aide(30), consever_liens_aides_pnjs=False)

    print(table_planning)
    table_planning_csv = ""
    for ligne in table_planning:
        for colonne in ligne:
            table_planning_csv += str(colonne).replace('\n', ' // ') + ';'
        table_planning_csv += '\n'


    #
    # table_planning_csv = "".join(
    #     ';'.join(ligne) + '\n' for ligne in table_planning
    # )

    # table_planning_csv = '\n'.join(
    #     ';'.join(ligne) for ligne in table_planning
    # )
    print(table_planning_csv)


# todo : préparation des données :
# enlever les évènements sans personnage lors de  la constitution des fichiers
# ajouter une fonction pour détecter qu'un pnj est à deux endroits à la fois en parvourant toutes ses interventions et en lui construirant un tableau de type cumul par heure
# détecter les PNJs en double dans leur évènement
# vérifier qu'on gere bien les évènements à une tab par jour > ajouter des pas fictifs? 1000 pour le premier jour, etc?
# lors de la restitution, sauter les lignes vides

if __name__ == '__main__':
    main()
