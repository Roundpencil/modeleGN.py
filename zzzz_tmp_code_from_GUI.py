import configparser

import google_io as g_io


# def lire_verifier_config_updater_gui(self, boutons: list, display_label, v_config_label, afficher=False):
#     config_file = display_label['text']
#     param_gn, resultats = g_io.charger_et_verifier_fichier_config(config_file, self.api_drive)
#
#     # print(f"repr des champs : {repr(display_label)} - {display_label}, {repr(v_config_label)} - {v_config_label}")
#     print(f"pgr = {(param_gn, resultats)}")
#     # print(f"param GN = {param_gn}")
#     if param_gn is not None:
#         if afficher:
#             self.afficher_resultats(resultats, param_gn)
#         # dans ce cas on a réussi à charger et les tests sont ok
#         v_config_label.config(text="Vérification fichier de configuration ok")
#         self.dict_config = param_gn
#         self.lire_gn_et_injecter_config(boutons)
#         self.updater_boutons_disponibles(True, boutons)
#         return True
#     else:
#         self.afficher_resultats(resultats, False)
#         v_config_label.config(text="Verifications fichier de configuration ko : corrigez les et re-vérifiez")
#         self.updater_boutons_disponibles(False, boutons)
#         return False


# def lire_gn_et_injecter_config(self, boutons: list, m_print=print):
#     print(f"dict config au début de la création = {self.dict_config}")
#     # try:
#     try:
#         self.gn = g_io.charger_gn_from_dict(api_drive=self.api_drive, dict_config=self.dict_config, m_print=m_print)
#         # self.gn = GN.load(self.dict_config['nom_fichier_sauvegarde'], dict_config=self.dict_config)
#
#     except Exception as f:
#         # print(traceback.format_exc())
#         print(f"une erreur est survenue qui a conduit à re-créer un fichier de sauvegarde : {f}")
#         print(
#             f"le fichier de sauvegarde {self.dict_config['nom_fichier_sauvegarde']} n'existe pas, j'en crée un nouveau")
#         self.gn = GN(dict_config=self.dict_config, ma_version=VERSION)
#
#     except Exception as e:
#         print(f"une erreur est survenue pendant la lecture du fichier ini : {e}")
#         traceback.print_exc()
#         self.dict_config = None
#         self.updater_boutons_disponibles(False, boutons)

#
# def afficher_resultats(self, resultats, test_global_reussi):
#     afficher_resultats_test_config(self.master, resultats, test_global_reussi)














# def charger_et_verifier_fichier_config(fichier_ini: str, api_drive):
#     config, erreurs_loading = charger_fichier_config(fichier_ini)
#     if erreurs_loading:
#         return config, erreurs_loading
#     return verifier_config_parser(api_drive, config)
#