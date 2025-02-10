from packaging import version

from modeleGN import GN, Intrigue, VERSION


# déclaration de la méthode de mise à jour
def _maj_classe(objet_a_maj, renommages:dict, fonctions_update:dict):
    reference = vars(type(objet_a_maj)())
    current = vars(objet_a_maj)
    nom_classe = type(objet_a_maj).__name__
    attributs_a_supprimer = []

    # mettre à jour les noms si dans le dictionnaire il y a un nom correspondant
    if dict_renommage := renommages.get(nom_classe):
        print(f"debug : dict_renommage :  {dict_renommage}")
        for old_attr, new_attr in dict_renommage.items():
            if hasattr(objet_a_maj, old_attr):
                valeur_cible = current[old_attr]
                print(f"debug : l'objet {type(objet_a_maj)} a bien un champ {old_attr} qui vaut {valeur_cible}")
                setattr(objet_a_maj, new_attr, valeur_cible)
                attributs_a_supprimer.append(old_attr)
                # delattr(objet_a_maj, old_attr) ancienne version avant le fait de délayer la suppression

    # ajouter les nouveaux champs
    for ref_attr, ref_value in reference.items():
        if not hasattr(objet_a_maj, ref_attr):
            setattr(objet_a_maj, ref_attr, ref_value)

    #appliquer les fonctions
    if fonction_a_appliquer := fonctions_update.get(nom_classe):
        fonction_a_appliquer(objet_a_maj)

    # supprimer les champs superflus
    for old_attr in attributs_a_supprimer:
        delattr(objet_a_maj, old_attr)

    old_attrs = list(current.keys())
    for old_attr in old_attrs:
        if old_attr not in reference:
            delattr(objet_a_maj, old_attr)

def _vers_1_4_20250205(gn: GN):
    renommages = {
                  }

    fonctions_update = {
                        'Scene':_scene_1_4_20250205
                        }

    version_cible = "1.4.20250205"
    # parcours de toutes les classes pour mettre à jour les Objets
    _montee_de_version(fonctions_update, gn, renommages, version_cible)

def _scene_1_4_20250205(scene):
    #met à jour les dates au nouveau format
    if hasattr(scene, 'scene.date_absolue') and (da := scene.date_absolue):
        scene.set_date_scene(da)
    elif hasattr(scene, 'date'):
        scene.set_date_scene(scene.date)
    elif hasattr(scene, '_date_relative_jours'):
        scene.set_date_scene(scene._date_relative_jours)

def _vers_1_4_20240901(gn: GN):
    renommages = {'GN':
                      {'objets': 'objets_de_reference'},
                  'Personnage':
                      {"orgaReferent": "orga_referent",
                       "joueurs": "interpretes",
                       "sexe": "genre"},
                  'Intrigue':
                      {'orgaReferent': 'orga_referent'},
                  'Intervention': #l'ancien nom de evenementunitaire
                      {'heure': 'heure_debut'},
                  'Role':
                      {"sexe": "genre"}
                  }

    fonctions_update = {
                        'Intervention':_intervention_1_4_20240901,# ancien nom de EvenementUnitaire
                        'Evenement': _evenement_1_4_20240901, #ancien nom de FicheEvenement
                        }
    version_cible = "1.4.20240901"
    # parcours de toutes les classes pour mettre à jour les Objets
    _montee_de_version(fonctions_update, gn, renommages, version_cible)

def _intervention_1_4_20240901(evenement_unitaire):
    if evenement_unitaire.__class__.__name__ == "Intervention":
        evenement_unitaire.__class__.__name__ = "EvenementUnitaire"

def _evenement_1_4_20240901(evenement):
    if evenement.__class__.__name__ == "Evenement":
        evenement.__class__.__name__ = "FicheEvenement"

def _vers_1_2_0(gn: GN):
    renommages = {
                  }

    fonctions_update = {Intrigue: _intrigue_1_2_0
                        }
    version_cible = "1.2.0"
    # parcours de toutes les classes pour mettre à jour les Objets

    _montee_de_version(fonctions_update, gn, renommages, version_cible)

def _intrigue_1_2_0(intrigue):
    intrigue.referent = intrigue.orga_referent

def mettre_a_jour_gn(gn: GN, verbal=True):

    version_fonction = {
        "1.2.0": _vers_1_2_0,
        "1.4.20240901": _vers_1_4_20240901,
        "1.4.20250205":_vers_1_4_20250205
    }
    versions = list(version_fonction.keys())
    versions.sort(key=lambda x: version.parse(x))

    if verbal:
        print(f"Versions pour update = {versions}")

    for version_cible in versions:
        if verbal:
            print(f"faut-il monter de vers = {version_cible}? "
                  f"(de {version.parse(gn.version)}  vers {version.parse(version_cible)})")

        if version.parse(version_cible) > version.parse(gn.version):
            if verbal:
                print(f"\tOui, update en cours...")
            fonction = version_fonction[version_cible]
            fonction(gn)
            if verbal:
                print(f"\tupdate fait")

    if version.parse(gn.version) != version.parse(VERSION):
        print(f"attention la version du GN ({gn.version} n'est pas égale à celle du modèle {VERSION}")
    else:
        print(f"GN mis à jour vers la version {VERSION}")



def _montee_de_version(fonctions_update, gn, renommages, version_cible):
    _maj_classe(gn, renommages, fonctions_update)
    for personnage in gn.personnages.values():
        _maj_classe(personnage, renommages, fonctions_update)
        for scene in personnage.scenes:
            _maj_classe(scene, renommages, fonctions_update)
        for role in personnage.roles:
            _maj_classe(role, renommages, fonctions_update)
    for faction in gn.factions.values():
        _maj_classe(faction, renommages, fonctions_update)
    for intrigue in gn.intrigues.values():
        _maj_classe(intrigue, renommages, fonctions_update)
        for scene in intrigue.scenes:
            _maj_classe(scene, renommages, fonctions_update)
            # print(f'heure de la scène {scene.titre} : {scene.heure_debut}')
    for evenement in gn.evenements.values():
        _maj_classe(evenement, renommages, fonctions_update)
        for evenement_unitaire in evenement.interventions:
            _maj_classe(evenement_unitaire, renommages, fonctions_update)
    for objet in gn.objets_de_reference.values():
        _maj_classe(objet, renommages, fonctions_update)

    gn.version = version_cible
