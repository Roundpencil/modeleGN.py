import re
import unittest
from enum import Enum

# --- Définitions factices pour le test ---

class DateScene:
    # La regex donnée pour 'il y a'
    PATTERN_IL_Y_A = r"\s*il\s*y\s*a\s*"

# Ces fonctions "externes" enregistrent leur appel dans la scène.
def dummy_extraire_qui_scene(texte, conteneur, scene, avec_tableau_des_persos):
    scene.calls.append(('extraire_qui_scene', texte, avec_tableau_des_persos))

def dummy_extraire_factions_scene(texte, scene):
    scene.calls.append(('extraire_factions_scene', texte))

def dummy_extraire_infos_scene(texte, scene):
    scene.calls.append(('extraire_infos_scene', texte))

# La fonction à tester.
def extraire_balise(input_balise: str, scene_a_ajouter, conteneur,
                    tableau_roles_existant: bool = True):
    class Balises(Enum):
        QUAND    = r"^##\s*quand\s*[:?]"
        IL_Y_A  = r"^##" + DateScene.PATTERN_IL_Y_A
        DATE    = r"^##\s*date\s*[:?]"
        QUI     = r"^##\s*qui\s*[:?]"
        FACTIONS= r"^##\s*(faction|factions)\s*[:?]"
        INFOS   = r"^##\s*(info|infos)\s*[:?]"
        HEURE   = r"^##\s*heure\s*[:?]"
        OU      = r"^##\s*(ou|où|lieu)\s*[:?]"

    dict_methodes = {
        Balises.QUAND:     lambda x: scene_a_ajouter.set_date_scene(x),
        Balises.IL_Y_A:    lambda x: scene_a_ajouter.set_date_scene(x),
        Balises.DATE:      lambda x: scene_a_ajouter.set_date_scene(x),
        Balises.QUI:       lambda x: dummy_extraire_qui_scene(x, conteneur, scene_a_ajouter, tableau_roles_existant),
        Balises.FACTIONS:  lambda x: dummy_extraire_factions_scene(x, scene_a_ajouter),
        Balises.INFOS:     lambda x: dummy_extraire_infos_scene(x, scene_a_ajouter),
        Balises.HEURE:     lambda x: scene_a_ajouter.set_heure_debut(x),
        Balises.OU:        lambda x: scene_a_ajouter.set_lieu(x)
    }

    for balise in Balises:
        if match := re.search(balise.value, input_balise, re.IGNORECASE):
            end_pos = match.end()
            texte_balise = input_balise[end_pos:]
            dict_methodes[balise](texte_balise)
            return True

    return False

# Objets factices pour simuler la scène et le conteneur

class DummyScene:
    def __init__(self):
        # On va enregistrer ici les appels réalisés par les méthodes
        self.calls = []
    def set_date_scene(self, texte):
        self.calls.append(('set_date_scene', texte))
    def set_heure_debut(self, texte):
        self.calls.append(('set_heure_debut', texte))
    def set_lieu(self, texte):
        self.calls.append(('set_lieu', texte))

class DummyConteneur:
    pass

# --- La classe de tests ---

class TestExtraireBalise(unittest.TestCase):
    def setUp(self):
        # Pour chaque test, on crée de nouveaux objets "scene" et "conteneur"
        self.scene = DummyScene()
        self.conteneur = DummyConteneur()

    def test_quand(self):
        input_str = "## quand: 12/12/2025"
        result = extraire_balise(input_str, self.scene, self.conteneur)
        self.assertTrue(result)
        # Le pattern "^##\s*quand\s*[:?]" capture "## quand:"
        # et le reste (après la balise) est " 12/12/2025"
        self.assertEqual(self.scene.calls, [('set_date_scene', " 12/12/2025")])

    def test_il_y_a(self):
        input_str = "## il y a 3 ans"
        result = extraire_balise(input_str, self.scene, self.conteneur)
        self.assertTrue(result)
        # Le pattern "^##\s*il\s*y\s*a\s*" capture "## il y a" et laisse " 3 ans"
        self.assertEqual(self.scene.calls, [('set_date_scene', " 3 ans")])

    def test_date(self):
        input_str = "## date? 2025-02-05"
        result = extraire_balise(input_str, self.scene, self.conteneur)
        self.assertTrue(result)
        self.assertEqual(self.scene.calls, [('set_date_scene', " 2025-02-05")])

    def test_qui(self):
        input_str = "## qui: Alice, Bob"
        result = extraire_balise(input_str, self.scene, self.conteneur)
        self.assertTrue(result)
        # Pour la balise QUI, c'est la fonction dummy_extraire_qui_scene qui est appelée.
        self.assertEqual(self.scene.calls, [('extraire_qui_scene', " Alice, Bob", True)])

    def test_factions(self):
        input_str = "## factions: rebels"
        result = extraire_balise(input_str, self.scene, self.conteneur)
        self.assertTrue(result)
        self.assertEqual(self.scene.calls, [('extraire_factions_scene', " rebels")])

    def test_infos(self):
        input_str = "## infos: des infos complémentaires"
        result = extraire_balise(input_str, self.scene, self.conteneur)
        self.assertTrue(result)
        self.assertEqual(self.scene.calls, [('extraire_infos_scene', " des infos complémentaires")])

    def test_heure(self):
        input_str = "## heure: 14h00"
        result = extraire_balise(input_str, self.scene, self.conteneur)
        self.assertTrue(result)
        self.assertEqual(self.scene.calls, [('set_heure_debut', " 14h00")])

    def test_ou(self):
        input_str = "## ou: dans Paris"
        result = extraire_balise(input_str, self.scene, self.conteneur)
        self.assertTrue(result)
        self.assertEqual(self.scene.calls, [('set_lieu', " dans Paris")])

    def test_aucune_balise(self):
        input_str = "Pas de balise ici"
        result = extraire_balise(input_str, self.scene, self.conteneur)
        self.assertFalse(result)
        self.assertEqual(self.scene.calls, [])

if __name__ == '__main__':
    unittest.main()
