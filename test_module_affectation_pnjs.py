import unittest

from module_affectation_pnjs import dico_brief2tableau_interventions_cont


class TestDicoBrief2TableauInterventionsCont(unittest.TestCase):

    def test_continuous_pnj_with_single_event(self):
        dico_pnjs_continus = {
            'PNJ_1': [[2, 3, 'Event 1', 'Event Name 1']]
        }
        max_date = 6
        min_date = 1
        expected_output = [
            ['', 'PNJ_1 - Event Name 1', 'PNJ_1 - Event Name 1', '', '', '']
        ]
        expected_names = ['PNJ_1']
        expected_overlapping = {}

        result_lignes, result_names, result_overlapping = dico_brief2tableau_interventions_cont(dico_pnjs_continus,
                                                                                                max_date, min_date)

        self.assertEqual(result_lignes, expected_output)
        self.assertEqual(result_names, expected_names)
        self.assertEqual(result_overlapping, expected_overlapping)

    def test_continuous_pnj_with_multiple_events(self):
        dico_pnjs_continus = {
            'PNJ_1': [[2, 2, 'Event 1', 'Event Name 1'], [4, 5, 'Event 2', 'Event Name 2']]
        }
        max_date = 6
        min_date = 1
        expected_output = [
            ['', 'PNJ_1 - Event Name 1', 'En jeu - PNJ_1', 'PNJ_1 - Event Name 2', 'PNJ_1 - Event Name 2', '']
        ]
        expected_names = ['PNJ_1']
        expected_overlapping = {}

        result_lignes, result_names, result_overlapping = dico_brief2tableau_interventions_cont(dico_pnjs_continus,
                                                                                                max_date, min_date)

        self.assertEqual(result_lignes, expected_output)
        self.assertEqual(result_names, expected_names)
        self.assertEqual(result_overlapping, expected_overlapping)

    def test_continuous_pnj_with_overlapping_events(self):
        dico_pnjs_continus = {
            'PNJ_1': [[1, 2, 'Event 1', 'Event Name 1'], [2, 3, 'Event 2', 'Event Name 2']]
        }
        max_date = 6
        min_date = 1
        expected_output = [
            ['PNJ_1 - Event Name 1', 'PNJ_1 - Event Name 1\nPNJ_1 - Event Name 2', 'PNJ_1 - Event Name 2', '', '', '']
        ]
        expected_names = ['PNJ_1']
        expected_overlapping = {'PNJ_1': [[2, 'PNJ_1 - Event Name 1\nPNJ_1 - Event Name 2']]}

        result_lignes, result_names, result_overlapping = dico_brief2tableau_interventions_cont(dico_pnjs_continus,
                                                                                                max_date, min_date)

        self.assertEqual(result_lignes, expected_output)
        self.assertEqual(result_names, expected_names)
        self.assertEqual(result_overlapping, expected_overlapping)

    # Additional tests can be added here for edge cases, large inputs, etc.


if __name__ == '__main__':
    unittest.main()
