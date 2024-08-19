import unittest

from google_io import corriger_formattage


class TestCorrigerBalisesAvecArgumentsPrecises(unittest.TestCase):
    def test_balise_ouverte_sans_fermeture(self):
        input_string = "<clef:arg>Contenu"
        expected_output = "<clef:arg>Contenu</clef:arg>"
        self.assertEqual(corriger_formattage(input_string, "clef"), expected_output)

    def test_balise_fermee_sans_ouverture(self):
        input_string = "Contenu</clef:arg>"
        expected_output = "<clef:arg>Contenu</clef:arg>"
        self.assertEqual(corriger_formattage(input_string, "clef"), expected_output)

    def test_balise_correctement_ouverte_et_fermee(self):
        input_string = "<clef:arg>Contenu</clef:arg>"
        expected_output = "<clef:arg>Contenu</clef:arg>"
        self.assertEqual(corriger_formattage(input_string, "clef"), expected_output)

    def test_balise_avec_arguments_differents(self):
        input_string = "<clef>Contenu</clef:arg>"
        expected_output = "<clef>Contenu<clef:arg></clef:arg></clef>"
        self.assertEqual(corriger_formattage(input_string, "clef"), expected_output)

    def test_balise_fermee_avant_ouverte(self):
        input_string = "blabla </clef> blabla <clef> tatata </clef> bluuuuu <clef>"
        expected_output = "<clef>blabla </clef> blabla <clef> tatata </clef> bluuuuu <clef></clef>"
        self.assertEqual(corriger_formattage(input_string, "clef"), expected_output)

    def test_balises_avec_arguments_multiples(self):
        input_string = "blabla </clef:1> blabla <clef:2> tatata </clef:3> bluuuuu <clef:1>"
        expected_output = "<clef:3><clef:1>blabla </clef:1> blabla <clef:2> tatata </clef:3> bluuuuu " \
                          "<clef:1></clef:2></clef:1>"
        self.assertEqual(corriger_formattage(input_string, "clef"), expected_output)


if __name__ == '__main__':
    unittest.main()
