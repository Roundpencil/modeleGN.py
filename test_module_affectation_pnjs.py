import sys
import unittest

from modeleGN import GN
from module_affectation_pnjs import (
    fusionner_colonnes, heure_en_pas, pas_en_heure, creer_planning,
    fusionner_elements_planning, is_element_integrable, dico_brief2tableau_interventions_avec_split,
    preparer_donnees_pour_planning, dico_brief2tableau_interventions_sans_split
)


class TestAffectionPjsPnjs(unittest.TestCase):

    def test_fusionner_colonnes(self):
        self.assertEqual(fusionner_colonnes([1, 0, None], [0, 2, 3]), [1, 2, 3])
        self.assertEqual(fusionner_colonnes([None, None], [0, None]), [0, None])
        self.assertIsNone(fusionner_colonnes([1, 0], [0, 2]))  # Test avec une collision

    def test_heure_en_pas(self):
        self.assertEqual(heure_en_pas("J1", "12h30", 1), 1500)
        self.assertEqual(heure_en_pas("J2", "00h00", 60), 24)
        self.assertEqual(heure_en_pas("J1", "23h59", 1), 1439)
        self.assertEqual(heure_en_pas("J1", "12h00", 60, jplusun=True), 36)

    def test_pas_en_heure(self):
        self.assertEqual(pas_en_heure(1500, 1), "J1, 12h30")
        self.assertEqual(pas_en_heure(24, 60), "J1, 00h24")
        self.assertEqual(pas_en_heure(1439, 1), "J0, 23h59")
        self.assertEqual(pas_en_heure(36, 60), "J0, 00h36")

    def test_fusionner_elements_planning(self):
        elements = [
            [0, 10, "Intervention 1", "Event A"],
            [11, 20, "Intervention 2", "Event B"]
        ]
        result = fusionner_elements_planning(elements)
        expected = [0, 20, "Intervention 1\nIntervention 2", "Event A\nEvent B"]
        self.assertEqual(result, expected)

    def test_is_element_integrable(self):
        elements = [
            [0, 5, "description1", 'evt1'],
            [7, 10, "description2", 'evt2']
        ]
        element = [6, 8, "new_description", 'evt3']
        result, _ = is_element_integrable(element, elements)
        self.assertTrue(result)

        overlapping_element = [4, 8, "description_overlap", 'evt1']
        result, _ = is_element_integrable(overlapping_element, elements)
        self.assertFalse(result)

    def test_dico_brief2tableau_interventions(self):
        dico_briefs = {
            'Intervenant1': [
                (0, 5, "Intervention1"),
                (6, 10, "Intervention2")
            ],
            'Intervenant2': [
                (0, 2, "Intervention3"),
                (8, 12, "Intervention4")
            ]
        }
        max_date = 12
        min_date = 0
        output, noms_persos = dico_brief2tableau_interventions_avec_split(dico_briefs, max_date, min_date)
        self.assertEqual(len(output), 2)
        self.assertEqual(len(noms_persos), 2)
        self.assertIn("Intervenant1", noms_persos[0])
        self.assertIn("Intervenant2", noms_persos[1])

    def test_preparer_donnees_pour_planning(self):
        # Assuming GN is properly mocked or instantiated
        gn = GN.load('demo.mgn')
        dico_pnjs_temp, dico_pnjs_continus, dico_pnjs_always, max_date, min_date = preparer_donnees_pour_planning(gn,
                                                                                                                  sys.maxsize,
                                                                                                                  0, 15)
        self.assertIsInstance(dico_pnjs_temp, dict)
        self.assertIsInstance(dico_pnjs_continus, dict)
        self.assertIsInstance(dico_pnjs_always, dict)
        self.assertTrue(max_date > min_date)

    def test_creer_planning(self):
        gn = GN.load('demo.mgn')  # Assuming GN is properly mocked or instantiated
        result = creer_planning(gn)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

class TestDicoBrief2TableauInterventionsSansSplit(unittest.TestCase):

    def setUp(self):
        # Set up any initial data needed for the tests
        self.min_date = 1
        self.max_date = 7

        self.dico_briefs1 = {
            'John Doe': [(1, 3, None, 'Event A'), (5, 7, None, 'Event B')],
            'Jane Smith': [(2, 4, None, 'Event C')]
        }

        self.dico_briefs2 = {
            'John Doe': [(1, 1, None, 'Event D')],
            'Jane Smith': [(3, 5, None, 'Event E'), (6, 6, None, 'Event F')]
        }

        self.dico_briefs_overlap = {
            'John Doe': [(2, 5, None, 'Event A'), (4, 6, None, 'Event B')]
        }

        self.expected_output1 = [
            ['John Doe - Event A', 'John Doe - Event A', 'John Doe - Event A', None, None, 'John Doe - Event B', 'John Doe - Event B', 'John Doe - Event B'],
            [None, 'Jane Smith - Event C', 'Jane Smith - Event C', 'Jane Smith - Event C', None, None, None, None]
        ]

        self.expected_output2 = [
            ['John Doe - Event D', None, None, None, None, None, None],
            [None, None, 'Jane Smith - Event E', 'Jane Smith - Event E', 'Jane Smith - Event E', 'Jane Smith - Event F', None]
        ]

        self.expected_output_overlap = [
            ['John Doe - Event A', 'John Doe - Event A\nJohn Doe - Event B', 'John Doe - Event A\nJohn Doe - Event B', 'John Doe - Event B', None, None, None]
        ]

        self.expected_names1 = ['John Doe', 'Jane Smith']
        self.expected_names2 = ['John Doe', 'Jane Smith']
        self.expected_names_overlap = ['John Doe']

    def test_case_1(self):
        # Test case with multiple events per person
        output, noms_persos = dico_brief2tableau_interventions_sans_split(self.dico_briefs1, self.max_date, self.min_date)
        self.assertEqual(output, self.expected_output1)
        self.assertEqual(noms_persos, self.expected_names1)

    def test_case_2(self):
        # Test case with single-day events and overlapping events
        output, noms_persos = dico_brief2tableau_interventions_sans_split(self.dico_briefs2, self.max_date, self.min_date)
        self.assertEqual(output, self.expected_output2)
        self.assertEqual(noms_persos, self.expected_names2)

    def test_overlap_events(self):
        # Test case where the timing of events overlaps for the same individual
        output, noms_persos = dico_brief2tableau_interventions_sans_split(self.dico_briefs_overlap, self.max_date, self.min_date)
        self.assertEqual(output, self.expected_output_overlap)
        self.assertEqual(noms_persos, self.expected_names_overlap)

    def test_empty_briefs(self):
        # Test case with an empty dictionary
        output, noms_persos = dico_brief2tableau_interventions_sans_split({}, self.max_date, self.min_date)
        self.assertEqual(output, [])
        self.assertEqual(noms_persos, [])

    def test_no_events(self):
        # Test case where events fall outside the min_date and max_date range
        dico_briefs = {
            'John Doe': [(8, 10, None, 'Event G')],
        }
        output, noms_persos = dico_brief2tableau_interventions_sans_split(dico_briefs, self.max_date, self.min_date)
        expected_output = [['None', 'None', 'None', 'None', 'None', 'None', 'None']]
        expected_names = ['John Doe']
        self.assertEqual(output, expected_output)
        self.assertEqual(noms_persos, expected_names)

if __name__ == "__main__":
    unittest.main()

