## dernière version fonctionnelle !!


from ortools.sat.python import cp_model

from modeleGN import *

MULTIPLICATEURS_MINUTES = 10000

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

def construire_timing_pnjs(evenements, aides: list[str], affectations_predefinies=None,
                           consever_liens_aides_pnjs=True, verbal = False):
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

    if verbal:
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


    #################################################################"

    # Trouver la dernière heure de fin des événements
    premiere_heure, derniere_heure = trouver_premiere_derniere_heure_en_pas(evenements)

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


def trouver_premiere_derniere_heure_en_pas(evenements):
    premiere_heure = min(evt["start"] for evt in evenements)
    derniere_heure = max(evt["end"] for evt in evenements)
    return premiere_heure, derniere_heure


def generer_tableau_aide(nb_aides, aides_connus=None):
    """
    Génère une liste de joueurs jouant des PNJs (des "aides").

    Génère une liste d'aide en fonction du nombre d'aides spécifié.
    Si une liste d'aides est connue, la fonction essaiera de les utiliser,
    et si des aides supplémentaires sont nécessaires, elles seront ajoutées séquentiellement.

    Args:
        nb_aides (int): Le nombre total d'éléments d'aide requis.
        aides_connus (list, optionnel) : Liste d'éléments d'aide connus. Par défaut, None.

    Returns:
        list: Une liste d'aides, contenant 'nb_aides' éléments ou plus si disponibles.
    """
    if aides_connus is None:
        aides_connus = []
    aides_a_ajouter = max(nb_aides - len(aides_connus), 0)
    return aides_connus + [f"aide {i}" for i in range(1, aides_a_ajouter + 1)]


def recherche_dichotomique_aides(evenements, min_aides=0, max_aides=100, aides_connus=None,
                                 consever_liens_aides_pnjs=True, affectations_predefinies=None):
    table_planning = None
    while min_aides < max_aides:
        print(f"debug : min actuel = {min_aides} / max actuel = {max_aides}")
        milieu = (min_aides + max_aides) // 2
        aides_testes = generer_tableau_aide(milieu, aides_connus)
        if table_planning := construire_timing_pnjs(evenements, aides_testes,
                                                    consever_liens_aides_pnjs=consever_liens_aides_pnjs,
                                                    affectations_predefinies=affectations_predefinies):
            max_aides = milieu
        else:
            min_aides = milieu + 1

    # si on est bons à la fin de la recherche dichotomique, on retourne le résultat,
    # sinon le résultat avec une aide de plus
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


def preparer_donnees_pour_ortools(gn: GN, pas=None, avec_corrections=True):
    if pas is None:
        pas = determiner_pas(gn.evenements.values())
        print(f'debug : pas final = {pas}')

    texte_erreurs = ""
    evenements = evenements_2_dict_ortools(gn.evenements.values(), pas, texte_erreurs)

    if avec_corrections:
        texte_cumul = identifier_erreurs_cumul(evenements, pas)
        texte_erreurs += texte_cumul

    return evenements, pas, texte_erreurs


def identifier_erreurs_cumul(evenements: list, pas):
    premiere_heure, derniere_heure = trouver_premiere_derniere_heure_en_pas(evenements)
    liste_pnjs = {pnj for evenement in evenements for pnj in evenement['pnjs']}

    cumul = {pnj: {h: [] for h in range(premiere_heure, derniere_heure + 1)} for pnj in liste_pnjs}
    for pnj in liste_pnjs:
        for heure in range(premiere_heure, derniere_heure + 1):
            for i, evt in enumerate(evenements):
                if evt['start'] <= heure < evt['end']:
                    cumul[pnj][heure].extend([i] * evt['pnjs'].count(pnj))
                # if evt['start'] <= heure < evt['end'] and pnj in evt['pnjs']:
                #     cumul[pnj][heure].append(i)

    texte_erreurs = ""
    for pnj in cumul:
        for heure in cumul[pnj]:
            # on obtient la liste des i associés aux évnements
            is_evt = cumul[pnj][heure]
            if len(is_evt) > 1:
                str_evts = '\n\t'.join(evenements[index]['nom'] for index in is_evt)
                texte_erreurs += f"erreur avec le pnj {pnj}, " \
                                 f"dans plus d'un évènement à {pas_2_h(heure, pas)} : \n\t" \
                                 f"{str_evts} \n "
                # une fois qu'on a trouvé l'erreur, on corrige dans la liste
                i = 1
                for index in is_evt:
                    print(f"debug : pour le pnj {pnj} à l'heure {heure}, is_evt = {is_evt}")
                    # print(f"debug : pnj = {pnj}, "
                    #       f"heure = {heure}, "
                    #       f"evt en cours : {evt}, "
                    #       f"evts = {evenements_a_cette_heure}")
                    found = True
                    index_a_changer = -1
                    while found:
                        try:
                            print(f"debug : evenements[index]['pnjs'] = {evenements[index]['pnjs']}")
                            index_a_changer = evenements[index]['pnjs'].index(pnj, index_a_changer + 1)
                            print(
                                f"debug : pnj {pnj} : index à changer pour l'evenement {evenements[index]['nom']} : {index_a_changer}")
                            print(f"valeur à cette index = {evenements[index]['pnjs'][index_a_changer]}")
                            evenements[index]['pnjs'][index_a_changer] += f" - ubiquité {i}"
                            i += 1
                            print(f"debug : valeurs apres changement : "
                                  f"nom = {evenements[index]['pnjs'][index_a_changer]}"
                                  f"i = {i}"
                                  f"tous les PNJs : {evenements[index]['pnjs']} \n\n")
                        except Exception as e:
                            print(e)
                            found = False
    return texte_erreurs


def pas_2_h(heure_en_pas, pas):
    heure_en_pas = int(heure_en_pas)
    jour = heure_en_pas // MULTIPLICATEURS_MINUTES
    minutes = (heure_en_pas % MULTIPLICATEURS_MINUTES) * pas
    # jour = heure_en_pas // 100
    # minutes = (heure_en_pas % 100) * pas
    return f"J{jour} - {minutes // 60}h{minutes % 60}"


def evenements_2_dict_ortools(liste_evenements: list[Evenement], pas, texte_erreurs):
    evenements_formattes = []
    for evenement in liste_evenements:
        for i, intervention in enumerate(evenement.interventions, start=1):
            # {"start": 0, "end": 4, "pnjs": [0, 1]},

            jour_nombre = ''.join(chiffre for chiffre in evenement.date if chiffre.isdigit())
            jour_nombre = int(jour_nombre) if jour_nombre else 0

            heure_debut = heure_en_pas(intervention.heure_debut, pas) + jour_nombre * MULTIPLICATEURS_MINUTES
            heure_fin = heure_en_pas(intervention.heure_fin, pas) + jour_nombre * MULTIPLICATEURS_MINUTES
            # heure_debut = heure_en_pas(intervention.heure_debut, pas) + jour_nombre * 100
            # heure_fin = heure_en_pas(intervention.heure_fin, pas) + jour_nombre * 100
            nom_intervention = f"{evenement.nom_evenement} - {i}"

            if heure_fin <= heure_debut:
                heure_fin = heure_debut + 1
                # si il y a eu un soucis dans la création de l'heure de fin, on ajoute un pas par défaut
                # pour nous assurer que tous les évènements on un début et une fin

            if pnjs := [intervenant.pnj.nom for intervenant in intervention.liste_intervenants]:
                current_dict = {"start": heure_debut,
                                "end": heure_fin,
                                "pnjs": pnjs,
                                "nom": nom_intervention
                                }
                evenements_formattes.append(current_dict)
            else:
                texte_erreurs += f"Attention, l'intervention {nom_intervention} n'implique aucun PNJ"
    return evenements_formattes


def heure_en_pas(heure_en_texte: str, pas: int):
    try:
        heure_splittee = heure_en_texte.split('h')
        minutes = int(heure_splittee[0]) * 60 + (int(heure_splittee[1]) if len(heure_splittee[1]) else 0)
        return minutes // pas
    except:
        return 0


def main():
    # gn = GN.load('GN Buffy')
    # evenements, pas, texte_erreurs = preparer_donnees_pour_ortools(gn)
    nom_gn = 'archive Chalacta'
    gn = GN.load(nom_gn)

    table_planning = creer_planning_evenementiel(gn)

    print(table_planning)

    # #DEBUG : commentaire momentané de l'affichage du DSV pour comprendre ce que sort la méthode
    # table_planning_csv = ';'.join(table_planning[0]) + ';\n'
    # for ligne in table_planning[1:]:
    #     # if sum(len(x) for x in ligne[2:]) == len(ligne[2:]):
    #     if len(ligne[1]) < 1:
    #         continue
    #
    #     table_planning_csv += f'{pas_2_h(ligne[0], pas)};'
    #     for colonne in ligne[1:]:
    #         # table_planning_csv += str(colonne).replace('\n', ' // ') + ';'
    #         table_planning_csv += '//'.join(str(colonne).split('\n')) + ';'
    #     table_planning_csv += '\n'
    #
    # #
    # # table_planning_csv = "".join(
    # #     ';'.join(ligne) + '\n' for ligne in table_planning
    # # )
    #
    # # table_planning_csv = '\n'.join(
    # #     ';'.join(ligne) for ligne in table_planning
    # # )
    # print(table_planning_csv)


def creer_planning_evenementiel(gn: GN, pas=None,
                                avec_corrections=True,
                                conserver_liens_aides_pnjs=True,
                                nb_aides_predefinis=None,
                                utiliser_affectations_predefinies=True,
                                session=None,
                                ):
    evenements, pas, texte_erreurs = preparer_donnees_pour_ortools(gn, pas=pas, avec_corrections=avec_corrections)
    print(f'DEBUG : {evenements}')
    logging.debug('erreurs dans la préparation des évènements pour la création de planning : ')
    logging.debug(texte_erreurs)
    print(f"DEBUG : erreurs evenements pre ORTOOLS : {texte_erreurs}")

    # ajouter les affectations prédéfinies et en déduire les aides connus
    # modele affectations_predefinies = pnj > personne

    if session and utiliser_affectations_predefinies:
            affectations_predefinies = {pnj.nom: pnj.interpretes[session]
                                        for pnj in gn.get_dict_pnj().values()
                                        if pnj.interpretes.get(session)}
            aides_connus = list(set(affectations_predefinies.values()))
    else:
        affectations_predefinies = None
        aides_connus = None

    table_planning = None
    if nb_aides_predefinis:
        faire une truc

    if not table_planning:
        table_planning = recherche_dichotomique_aides(evenements, min_aides=1, max_aides=30,
                                                      consever_liens_aides_pnjs=conserver_liens_aides_pnjs,
                                                      affectations_predefinies=affectations_predefinies,
                                                      aides_connus=aides_connus)

    # si ca ne marche pas on rentente avec les affectations prédéfinies en moins
    if not table_planning and affectations_predefinies:
        affectations_predefinies = None
        logging.debug("pas de solution possible pour l'évènementiel "
                      "en respectant les choix d'afectaction prédéfini pour les PNJs ")
        table_planning = recherche_dichotomique_aides(evenements, min_aides=1, max_aides=30,
                                                      consever_liens_aides_pnjs=conserver_liens_aides_pnjs,
                                                      affectations_predefinies=affectations_predefinies,
                                                      aides_connus=aides_connus)

    # si ca ne marche pas on libère les contraintes à nouveau en supprimant les liens aides-PNJ
    if not table_planning and conserver_liens_aides_pnjs:
        conserver_liens_aides_pnjs = False
        logging.debug("pas de solution possible pour l'évènementiel "
                      "en conservaant les mêmes aides pour les mêmes PNJs durant tout le jeu")

        table_planning = recherche_dichotomique_aides(evenements, min_aides=1, max_aides=30,
                                                      consever_liens_aides_pnjs=conserver_liens_aides_pnjs,
                                                      affectations_predefinies=affectations_predefinies,
                                                      aides_connus=aides_connus)
    if not table_planning:
        logging.debug("pas de solution possible pour l'évènementiel "
                      "y compris en supprimant toutes les contraintes")
        return [['pas de résultats']]

    # on retire les lignes vides
    table_planning = [row for row in table_planning if any(cell != '' for cell in row[1:])]
    # on re_converti les pas en Jours et heures
    for row in table_planning[1:]:
        row[0] = pas_2_h(row[0], pas)
    return table_planning


# todo :
#  detecter quand il n'y a pas de solutions a la sortie du solveur dichotomique, puis libérer les contraintes
#  nouveau paramètre : NB_aides  > si spécifié, tentative de forcer ce nombre d'aides en amont du calcul si ok > utiliser respecter nb aides
#  nouveau paramètre : pas_evenement pour forcer taille pas. Dire dans le manuel plus grand pas > plus grand tableau > plus grande longueur de solveur
#  nouvel onglet dans les fichiers de castings : aides par sessions (plutot que de prendre les pré-affectation) et les utiliser
#  réintégrer dans le code, ajouter un bouton dans l'interface graphique, vériier ce qu'il se passe dans un gn sans évènements

if __name__ == '__main__':
    main()
