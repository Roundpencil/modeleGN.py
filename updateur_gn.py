# from modeleGN import *
from packaging import version
from modeleGN import GN, Personnage, Role, Intrigue, EvenementUnitaire, VERSION

# todo :
#  ajouter des fonctions psécifiques à des versions
#  parcourir toutes les versions intermédiaires et trouver toutes les fonctions associées et dictionnaires de renommage
#  faire tourner la fonction tant que la version n'est pas à jour en prenant en input les fonctions de mise à jour
#  et les tableaux de renommage

# déclaration de la méthode de mise à jour
def _maj_classe(objet_a_maj, renommages:dict, fonctions_update:dict):
    reference = vars(type(objet_a_maj)())
    current = vars(objet_a_maj)
    # mettre à jour les noms si dans le dictionnaire il y a un nom correspondant
    if dict_renommage := renommages.get(type(objet_a_maj)):
        print(f"debug : dict_renommage :  {dict_renommage}")
        for old_attr, new_attr in dict_renommage.items():
            if hasattr(objet_a_maj, old_attr):
                valeur_cible = current[old_attr]
                print(f"debug : l'objet {type(objet_a_maj)} a bien un champ {old_attr} qui vaut {valeur_cible}")
                setattr(objet_a_maj, new_attr, valeur_cible)
                delattr(objet_a_maj, old_attr)
    # ajouter les nouveaux champs
    for ref_attr, ref_value in reference.items():
        if not hasattr(objet_a_maj, ref_attr):
            setattr(objet_a_maj, ref_attr, ref_value)
    # supprimer les champs superflus
    old_attrs = list(current.keys())
    for old_attr in old_attrs:
        if old_attr not in reference:
            delattr(objet_a_maj, old_attr)

def _vers_1_4_20250113(gn: GN):
    renommages = {GN:
                      {'objets': 'objets_de_reference'},
                  Personnage:
                      {"orgaReferent": "orga_referent",
                       "joueurs": "interpretes",
                       "sexe": "genre"},
                  Intrigue:
                      {'orgaReferent': 'orga_referent'},
                  EvenementUnitaire:
                      {'heure': 'heure_debut'},
                  Role:
                      {"sexe": "genre"}
                  }

    fonctions_update = {GN:
                            {},
                        Personnage:
                            {},
                        Intrigue:
                            {},
                        EvenementUnitaire:
                            {},
                        Role:
                            {}
                        }
    version_cible = "1.4.20250113"
    # parcours de toutes les classes pour mettre à jour les Objets

    _montee_de_version(fonctions_update, gn, renommages, version_cible)

def mettre_a_jour_gn(gn: GN):
    version_fonction = {"1.4.20250113":_vers_1_4_20250113}
    versions = list(version_fonction.keys())
    versions.sort(key=lambda x: version.parse(x))

    # version_max = versions[:-1]

    for version_cible in versions:
        if version.parse(version_cible) > version.parse(gn.version):
            fonction = version_fonction[version_cible]
            fonction(gn)

    if version.parse(gn.version) != VERSION:
        print("attention la version du GN n'est pas égale à celle du modèle")
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
            print(f'heure de la scène {scene.titre} : {scene.heure_debut}')
    for evenement in gn.evenements.values():
        if evenement.__class__.__name__ == "Evenement":
            evenement.__class__.__name__ = "FicheEvenement"

        _maj_classe(evenement, renommages, fonctions_update)
        for evenement_unitaire in evenement.interventions:
            if evenement_unitaire.__class__.__name__ == "Intervention":
                evenement_unitaire.__class__.__name__ = "EvenementUnitaire"
            _maj_classe(evenement_unitaire, renommages, fonctions_update)
    for objet in gn.objets_de_reference.values():
        _maj_classe(objet, renommages, fonctions_update)
    if version.parse(gn.version) < version.parse('1.2.0'):
        # dans ce cas il faut mettre à jour les noms des référents car pas automatique
        intrigues = gn.intrigues.values()
        for intrigue in intrigues:
            intrigue.referent = intrigue.orga_referent
    gn.version = version_cible
