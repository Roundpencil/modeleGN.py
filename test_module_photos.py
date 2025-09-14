import unittest
from module_photos import *
from lecteurGoogle import *

class MyTestCase(unittest.TestCase):
    def test_lister_images_dans_dossier_sans_recurrence(self):
        """Vérifie que lister_images_dans_dossier renvoie le bon mapping et None."""
        dr, _, _ = creer_lecteurs_google_apis()
        result = lister_images_dans_dossier(
            "1tjtsPczZ77IwyIEdHsV_QoXDVYDQCBZR", dr
        )

        attendu = (
            {
                'Camille_Claudel': '12f5fWV8ZNmBA-TV6DnMeEITBHM74SN-u',
                'meudon': '1i6tF8iyAyr2UOLZb0eLjUAa40sdiJFyM'
            },
            None
        )

        self.assertEqual(result, attendu)

    def test_lister_images_dans_un_dossier(self):
        """Vérifie que lister_images_dans_dossier renvoie le bon mapping et None."""
        dr, _, _ = creer_lecteurs_google_apis()
        result = lister_images_dans_un_dossier(
            "1tjtsPczZ77IwyIEdHsV_QoXDVYDQCBZR", dr
        )

        attendu = (
            {
                'Camille_Claudel': '12f5fWV8ZNmBA-TV6DnMeEITBHM74SN-u',
                'meudon': '1i6tF8iyAyr2UOLZb0eLjUAa40sdiJFyM'
            },
            None
        )

        self.assertEqual(result, attendu)

if __name__ == '__main__':
    unittest.main()
