import configparser
import os
from datetime import datetime


def recreate_configparser(dict_config):
    """
    Recreate a ConfigParser object from a dict_config produced by creer_dict_config.

    Parameters:
        dict_config (dict): A configuration dictionary as produced by creer_dict_config.

    Returns:
        configparser.ConfigParser: A new ConfigParser object with sections and options
                                   set according to dict_config.
    """
    config = configparser.ConfigParser()

    # --- Populate the "Essentiels" section ---
    config.add_section("Essentiels")

    # dossier_output_squelettes_pjs is stored in dict_config['dossier_output']
    dossier_output = dict_config.get('dossier_output')
    if dossier_output is not None:
        config.set("Essentiels", "dossier_output_squelettes_pjs", str(dossier_output))

    # mode_association:
    # In the original, the value is read as an integer (or taken from GN.ModeAssociation).
    mode_association = dict_config.get('mode_association')
    if mode_association is not None:
        try:
            # if mode_association is an enum, try to extract its value
            value = mode_association.value
        except AttributeError:
            value = mode_association
        # write the integer value as a string
        config.set("Essentiels", "mode_association", str(int(value)))

    # nom_fichier_sauvegarde:
    nom_fichier_sauvegarde = dict_config.get('nom_fichier_sauvegarde')
    if nom_fichier_sauvegarde is not None:
        config.set("Essentiels", "nom_fichier_sauvegarde", str(nom_fichier_sauvegarde))

    # dossiers_intrigues: in the original, these were read by
    # decouper_clefs (with prefix "id_dossier_intrigues") and the key names
    # were stored in dict_config["nom_dossiers_intrigues"] while their values were
    # in dict_config["dossiers_intrigues"].
    dossiers = dict_config.get("dossiers_intrigues", [])
    noms = dict_config.get("nom_dossiers_intrigues", [])
    for key_name, value in zip(noms, dossiers):
        config.set("Essentiels", key_name, str(value))

    # --- Populate the "Optionnels" section ---
    config.add_section("Optionnels")

    # fichier local sauvegarde: the original code gets Optionnels/nom_fichier_sauvegarde,
    # then uses os.path.join(os.path.curdir, ...) to produce dict_config['dossier_local_fichier_sauvegarde'].
    # For the reverse, we compute the relative path.
    dossier_local = dict_config.get("dossier_local_fichier_sauvegarde")
    if dossier_local is not None:
        # Compute the relative part (if dossier_local equals os.path.curdir, this will be ".")
        rel_path = os.path.relpath(dossier_local, os.path.curdir)
        config.set("Optionnels", "nom_fichier_sauvegarde", str(rel_path))

    # dossiers_pjs, dossiers_pnjs, dossiers_evenements, dossiers_objets
    # For each, the key names stored in dict_config are:
    #   - the list of values is under key: <dossier_key>
    #   - the corresponding list of option names is under key: "nom_" + <dossier_key>
    for dossier_key in ["dossiers_pjs", "dossiers_pnjs", "dossiers_evenements", "dossiers_objets"]:
        values = dict_config.get(dossier_key, [])
        option_names = dict_config.get("nom_" + dossier_key, [])
        for opt_name, value in zip(option_names, values):
            config.set("Optionnels", opt_name, str(value))

    # id_factions (if any)
    id_factions = dict_config.get("id_factions")
    if id_factions is not None:
        config.set("Optionnels", "id_factions", str(id_factions))

    # id_pjs_et_pnjs versus the alternative options:
    # If an id_pjs_et_pnjs exists, we set that. Otherwise we set the alternative
    # options "nom_fichier_pnjs" and "noms_persos".
    id_pjs_et_pnjs = dict_config.get("id_pjs_et_pnjs")
    if id_pjs_et_pnjs:
        config.set("Optionnels", "id_pjs_et_pnjs", str(id_pjs_et_pnjs))
    else:
        fichier_noms_pnjs = dict_config.get("fichier_noms_pnjs")
        if fichier_noms_pnjs is not None:
            config.set("Optionnels", "nom_fichier_pnjs", str(fichier_noms_pnjs))
        # For liste_noms_pjs, if it is a list then join with commas
        liste_noms_pjs = dict_config.get("liste_noms_pjs")
        if liste_noms_pjs is not None:
            if isinstance(liste_noms_pjs, list):
                noms_str = ",".join(str(nom) for nom in liste_noms_pjs)
            else:
                noms_str = str(liste_noms_pjs)
            config.set("Optionnels", "noms_persos", noms_str)

    # date_gn: if a date is stored as a datetime object, we format it.
    date_gn = dict_config.get("date_gn")
    if date_gn is not None:
        if isinstance(date_gn, datetime):
            date_str = date_gn.isoformat()
        else:
            date_str = str(date_gn)
        config.set("Optionnels", "date_gn", date_str)

    # Prefixes
    for key, default in [
        ("prefixe_intrigues", "I"),
        ("prefixe_evenements", "E"),
        ("prefixe_PJs", "P"),
        ("prefixe_PNJs", "N"),
        ("prefixe_objets", "O")
    ]:
        value = dict_config.get(key, default)
        config.set("Optionnels", key, str(value))

    # If 'liste_noms_pjs' wasn’t already handled above (for the id_pjs_et_pnjs alternative),
    # we can set Optionnels/noms_persos with it.
    if (not config.has_option("Optionnels", "noms_persos") and
            dict_config.get("liste_noms_pjs") is not None):
        liste_noms_pjs = dict_config.get("liste_noms_pjs")
        if isinstance(liste_noms_pjs, list):
            noms_str = ",".join(str(nom) for nom in liste_noms_pjs)
        else:
            noms_str = str(liste_noms_pjs)
        config.set("Optionnels", "noms_persos", noms_str)

    # id_dossier_archive (if any)
    id_dossier_archive = dict_config.get("id_dossier_archive")
    if id_dossier_archive is not None:
        config.set("Optionnels", "id_dossier_archive", str(id_dossier_archive))

    return config

import configparser

def compare_configparsers(config1: configparser.ConfigParser,
                          config2: configparser.ConfigParser) -> dict:
    """
    Compare deux objets ConfigParser section par section.

    Retourne un dictionnaire décrivant les différences. Le format du dictionnaire est le suivant :

    {
        'sections_missing_in_config2': [liste_des_sections_absentes_de_config2],
        'sections_missing_in_config1': [liste_des_sections_absentes_de_config1],
        'NomSectionCommune': {
            'options_missing_in_config2': [liste_des_options_absentes_de_config2],
            'options_missing_in_config1': [liste_des_options_absentes_de_config1],
            'value_differences': {
                'nom_option': (valeur_dans_config1, valeur_dans_config2),
                ...
            }
        },
        ...
    }
    Si aucune différence n'est trouvée, le dictionnaire sera vide.
    """
    differences = {}

    # Récupérer les noms de sections de chacun
    sections1 = set(config1.sections())
    sections2 = set(config2.sections())

    # Sections présentes dans config1 mais pas dans config2
    missing_in_config2 = sections1 - sections2
    if missing_in_config2:
        differences['sections_missing_in_config2'] = list(missing_in_config2)

    # Sections présentes dans config2 mais pas dans config1
    missing_in_config1 = sections2 - sections1
    if missing_in_config1:
        differences['sections_missing_in_config1'] = list(missing_in_config1)

    # Comparer les sections communes
    common_sections = sections1.intersection(sections2)
    for section in common_sections:
        section_diff = {}

        # Options dans chaque section
        options1 = set(config1.options(section))
        options2 = set(config2.options(section))

        # Options présentes dans config1 mais pas dans config2
        missing_options_in_config2 = options1 - options2
        if missing_options_in_config2:
            section_diff['options_missing_in_config2'] = list(missing_options_in_config2)

        # Options présentes dans config2 mais pas dans config1
        missing_options_in_config1 = options2 - options1
        if missing_options_in_config1:
            section_diff['options_missing_in_config1'] = list(missing_options_in_config1)

        # Comparer les valeurs pour les options communes
        common_options = options1.intersection(options2)
        value_diffs = {}
        for option in common_options:
            val1 = config1.get(section, option)
            val2 = config2.get(section, option)
            if val1 != val2:
                value_diffs[option] = (val1, val2)
        if value_diffs:
            section_diff['value_differences'] = value_diffs

        if section_diff:
            differences[section] = section_diff

    return differences

# Exemple d'utilisation :
if __name__ == "__main__":
    # Création de deux ConfigParser pour l'exemple
    config1 = configparser.ConfigParser()
    config1.add_section("Essentiels")
    config1.set("Essentiels", "param1", "valeur1")
    config1.set("Essentiels", "param2", "valeur2")
    config1.add_section("Optionnels")
    config1.set("Optionnels", "opt1", "abc")

    config2 = configparser.ConfigParser()
    config2.add_section("Essentiels")
    config2.set("Essentiels", "param1", "valeur1")         # identique
    config2.set("Essentiels", "param2", "autre_valeur")       # différent
    config2.set("Essentiels", "param3", "valeur3")            # option en plus
    config2.add_section("Divers")                             # section en plus
    config2.add_section("Optionnels")
    config2.set("Optionnels", "opt1", "abc")                  # identique

    diff = compare_configparsers(config1, config2)
    print("Différences trouvées :")
    for key, value in diff.items():
        print(f"{key}: {value}")
