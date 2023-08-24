import google_io as g_io

def lire_verifier_config_updater_gui(self, boutons: list, display_label, v_config_label, afficher=False):
    config_file = display_label['text']
    param_gn, resultats = g_io.charger_et_verifier_fichier_config(config_file, self.api_drive)

    # print(f"repr des champs : {repr(display_label)} - {display_label}, {repr(v_config_label)} - {v_config_label}")
    print(f"pgr = {(param_gn, resultats)}")
    # print(f"param GN = {param_gn}")
    if param_gn is not None:
        if afficher:
            self.afficher_resultats(resultats, param_gn)
        # dans ce cas on a réussi à charger et les tests sont ok
        v_config_label.config(text="Vérification fichier de configuration ok")
        self.dict_config = param_gn
        self.lire_gn_et_injecter_config(boutons)
        self.updater_boutons_disponibles(True, boutons)
        return True
    else:
        self.afficher_resultats(resultats, False)
        v_config_label.config(text="Verifications fichier de configuration ko : corrigez les et re-vérifiez")
        self.updater_boutons_disponibles(False, boutons)
        return False


def lire_gn_et_injecter_config(self, boutons: list, m_print=print):
    print(f"dict config au début de la création = {self.dict_config}")
    # try:
    try:
        self.gn = g_io.charger_gn_from_dict(api_drive=self.api_drive, dict_config=self.dict_config, m_print=m_print)
        # self.gn = GN.load(self.dict_config['nom_fichier_sauvegarde'], dict_config=self.dict_config)

    except Exception as f:
        # print(traceback.format_exc())
        print(f"une erreur est survenue qui a conduit à re-créer un fichier de sauvegarde : {f}")
        print(
            f"le fichier de sauvegarde {self.dict_config['nom_fichier_sauvegarde']} n'existe pas, j'en crée un nouveau")
        self.gn = GN(dict_config=self.dict_config, ma_version=VERSION)

    except Exception as e:
        print(f"une erreur est survenue pendant la lecture du fichier ini : {e}")
        traceback.print_exc()
        self.dict_config = None
        self.updater_boutons_disponibles(False, boutons)


def afficher_resultats(self, resultats, test_global_reussi):
    afficher_resultats_test_config(self.master, resultats, test_global_reussi)


def afficher_resultats_test_config(master, resultats, test_global_reussi):
    def close_popup():
        popup.destroy()

    popup = tk.Toplevel(master)
    if test_global_reussi:
        popup.title("Tests Réussis")
        # popup.iconbitmap("success_icon.ico")  # Replace with the path to the success icon
    else:
        popup.title("Tests Échoués")
        # popup.iconbitmap("failure_icon.ico")  # Replace with the path to the failure icon
    tree = ttk.Treeview(popup, columns=("Paramètre", "Nom du fichier lu", "Résultat du test"))
    tree.heading("#0", text="")
    tree.column("#0", width=0, minwidth=0, stretch=tk.NO)
    tree.heading("Paramètre", text="Nom du paramètre")
    tree.column("Paramètre", anchor=tk.W)
    tree.heading("Nom du fichier lu", text="Nom du fichier lu")
    tree.column("Nom du fichier lu", anchor=tk.W)
    tree.heading("Résultat du test", text="Résultat du test")
    tree.column("Résultat du test", anchor=tk.W)
    for res in resultats:
        tree.insert('', tk.END, values=(res[0], res[1], res[2]))
    tree.pack(padx=10, pady=10)
    # Create an "OK" button to close the popup
    ok_button = tk.Button(popup, text="OK", command=close_popup)
    ok_button.pack(pady=10)
    popup.transient(master)
    popup.grab_set()
    master.wait_window(popup)









def verifier_config_parser(api_drive, config: configparser.ConfigParser):
    resultats = []
    test_global_reussi = True
    fichier_output = {}

    dossiers_a_verifier = []
    google_docs_a_verifier = []
    google_sheets_a_verifier = []
    # *** vérification que tous les paramètres Essentiels sont présents
    # intégration du fichier de sortie
    try:
        fichier_output['dossier_output'] = config.get('Essentiels', 'dossier_output_squelettes_pjs')
    except configparser.NoOptionError:
        resultats.append(
            ["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de dossier de sortie trouvé"])
        test_global_reussi = False

    # intégration des dossiers intrigues et vérifications
    fichier_output['dossiers_intrigues'] = []
    clefs_intrigues = [key for key in config.options("Essentiels") if key.startswith("id_dossier_intrigues")]
    for clef in clefs_intrigues:
        valeur = config.get("Essentiels", clef)
        dossiers_a_verifier.append([clef, valeur])
        fichier_output['dossiers_intrigues'].append(valeur)
    if len(fichier_output.get('dossiers_intrigues', [])) == 0:
        resultats.append(["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de dossier intrigue"])
        test_global_reussi = False
    # intégration du mode association et vérifications
    try:
        mode_association_value = int(config.get('Essentiels', 'mode_association', fallback="9")[0])
        if mode_association_value in [0, 1]:
            fichier_output['mode_association'] = GN.ModeAssociation(mode_association_value)
        else:
            resultats.append(["Paramètre Essentiels", "Validité du fichier de paramètres", "Mode association invalide"])
            test_global_reussi = False
    except configparser.NoOptionError:
        resultats.append(
            ["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de mode association trouvé"])
        test_global_reussi = False
    except IndexError:
        resultats.append(
            ["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de mode association trouvé"])
        test_global_reussi = False

    # intégration du fichier de sauvegarde
    try:
        fichier_output['nom_fichier_sauvegarde'] = config.get('Essentiels', 'nom_fichier_sauvegarde')
    except configparser.NoOptionError:
        resultats.append(["Paramètre Essentiels", "Validité du fichier de paramètres", "Pas de fichier de sauvegarde"])
        test_global_reussi = False

    # intégration d'une ligne de bilan des tests essentiels
    if test_global_reussi:
        resultats.append(["Paramètre Essentiels", "Présence des champs", "Test Réussi"])

    # *** intégration des fichiers optionnels
    # création du paramètre fichier local sauvegarde, par défaut ou tel que lu
    try:
        nom_dossier_sauvegarde = config.get('Optionnels', 'nom_fichier_sauvegarde')
        fichier_output['dossier_local_fichier_sauvegarde'] = os.path.join(os.path.curdir, nom_dossier_sauvegarde)
    except configparser.NoOptionError:
        fichier_output['dossier_local_fichier_sauvegarde'] = os.path.curdir

    # intégration des dossiers PJs
    fichier_output['dossiers_pjs'] = []
    clefs_pjs = [key for key in config.options("Optionnels") if key.startswith("id_dossier_pjs")]
    for clef in clefs_pjs:
        valeur = config.get("Optionnels", clef)
        dossiers_a_verifier.append([clef, valeur])
        fichier_output['dossiers_pjs'].append(valeur)
    # intégration des dossiers PNJs
    fichier_output['dossiers_pnjs'] = []
    clefs_pjs = [key for key in config.options("Optionnels") if key.startswith("id_dossier_pnjs")]
    for clef in clefs_pjs:
        valeur = config.get("Optionnels", clef)
        dossiers_a_verifier.append([clef, valeur])
        fichier_output['dossiers_pnjs'].append(valeur)
    # intégration des dossiers Evenements
    fichier_output['dossiers_evenements'] = []
    clefs_pjs = [key for key in config.options("Optionnels") if key.startswith("id_dossier_evenements")]
    for clef in clefs_pjs:
        valeur = config.get("Optionnels", clef)
        dossiers_a_verifier.append([clef, valeur])
        fichier_output['dossiers_evenements'].append(valeur)
    # intégration des dossiers objets
    fichier_output['dossiers_objets'] = []
    clefs_pjs = [key for key in config.options("Optionnels") if key.startswith("id_dossier_objets")]
    for clef in clefs_pjs:
        valeur = config.get("Optionnels", clef)
        dossiers_a_verifier.append([clef, valeur])
        fichier_output['dossiers_objets'].append(valeur)

    # intégration du fichier des factions
    id_factions = config.get('Optionnels', 'id_factions', fallback=None)
    fichier_output['id_factions'] = id_factions
    if id_factions:
        google_docs_a_verifier.append(["id_factions", id_factions])
    # intégration du fichier des ids pjs_pnjs
    id_pjs_et_pnjs = config.get('Optionnels', 'id_pjs_et_pnjs', fallback=None)
    if id_pjs_et_pnjs:
        fichier_output['id_pjs_et_pnjs'] = id_pjs_et_pnjs
        google_sheets_a_verifier.append(["id_pjs_et_pnjs", id_pjs_et_pnjs])
    else:
        logging.debug("Je suis en train de lire le fichier de config et je n'ai pas trouvé d'id pjpnj en ligne")
        fichier_output['fichier_noms_pnjs'] = config.get('Optionnels', 'nom_fichier_pnjs', fallback=None)
        fichier_output['liste_noms_pjs'] = [nom_p.strip()
                                            for nom_p in
                                            config.get('Optionnels', 'noms_persos', fallback="").split(',')]
    # ajout de la date du GN
    texte_date_gn = config.get('Optionnels', 'date_gn', fallback=None)
    if texte_date_gn:
        fichier_output['date_gn'] = dateparser.parse(texte_date_gn, languages=['fr'])
        logging.debug(f"date_gn formattée = {fichier_output['date_gn']}")
    else:
        logging.debug("pour ce GN, date_gn = Pas de date lue")
    fichier_output['prefixe_intrigues'] = config.get('Optionnels', 'prefixe_intrigues', fallback="I")
    fichier_output['prefixe_evenements'] = config.get('Optionnels', 'prefixe_evenements', fallback="E")
    fichier_output['prefixe_PJs'] = config.get('Optionnels', 'prefixe_PJs', fallback="P")
    fichier_output['prefixe_PNJs'] = config.get('Optionnels', 'prefixe_PNJs', fallback="N")
    fichier_output['prefixe_objets'] = config.get('Optionnels', 'prefixe_objets', fallback="O")
    fichier_output['liste_noms_pjs'] = config.get('Optionnels', 'noms_persos', fallback=None)

    # ajouter le dossier archive
    fichier_output['id_dossier_archive'] = config.get('Optionnels', 'id_dossier_archive', fallback=None)

    # a ce stade là on a :
    # 1. intégré tous les paramètres au fichier de sortie
    # 2. fait les premiers tests sur les fichiers essentiels
    # 3. préparé les tableaux à parcourir pour faire les tests d'accès / existence aux dossiers
    # >> on peut lancer les tests
    for parametre, dossier_id in dossiers_a_verifier:
        try:
            # dossier = api_drive.files().get(fileId=dossier_id).execute()

            folder_metadata = api_drive.files().get(fileId=dossier_id).execute()
            # print(f"debug : dossier ID {dossier_id}")
            # Récupérer le nom du dossier
            folder_name = folder_metadata['name']

            resultats.append([parametre, folder_name, "Test Réussi"])
        except HttpError as error:
            resultats.append([parametre, "", "Echec du Test"])
            logging.debug(f"Erreur durant la vérification du dossier {dossier_id} : {error}")
            test_global_reussi = False
        except KeyError as error:
            resultats.append([parametre, "impossible de lire le paramètre", "Echec du Test"])
            logging.debug(f"Erreur durant la vérification du dossier {dossier_id} : {error}")
            test_global_reussi = False
    # Test pour les Google Docs
    for parametre, doc_id in google_docs_a_verifier:
        try:
            doc_metadata = api_drive.files().get(fileId=doc_id).execute()
            doc_name = doc_metadata['name']
            resultats.append([parametre, doc_name, "Test Réussi"])
        except HttpError as error:
            resultats.append([parametre, "", "Echec du Test"])
            logging.debug(f"Erreur durant la vérification du fichier {doc_id} : {error}")
            test_global_reussi = False
    # Test pour les Google Sheets
    for parametre, sheet_id in google_sheets_a_verifier:
        try:
            sheet_metadata = api_drive.files().get(fileId=sheet_id).execute()
            sheet_name = sheet_metadata['name']
            resultats.append([parametre, sheet_name, "Test Réussi"])
        except HttpError as error:
            resultats.append([parametre, "", "Echec du Test"])
            logging.debug(f"Erreur durant la vérification du fichier {sheet_id} : {error}")
            test_global_reussi = False
    # Vérification des droits d'écriture dans le dossier de sortie
    dossier_output_id = fichier_output['dossier_output']
    try:
        permissions = api_drive.permissions().list(fileId=dossier_output_id).execute()
        droit_ecriture = any(
            permission['role'] in ['writer', 'owner']
            for permission in permissions['permissions']
        )
        if droit_ecriture:
            resultats.append(["Droits en écriture", "sur le fichier de sortie", "Test Réussi"])
        else:
            resultats.append(["Droits en écriture", "sur le fichier de sortie", "Echec du Test"])
            test_global_reussi = False
    except HttpError as error:
        resultats.append(["Droits en écriture", "sur le fichier de sortie", "Echec du Test"])
        logging.debug(f"Erreur durant la vérification des droits en écriture sur {dossier_output_id} : {error}")
        test_global_reussi = False
    except KeyError as error:
        resultats.append(["Droits en écriture", "sur le fichier de sortie", "Echec du Test"])
        logging.debug(f"Pas de dossier d'écriture : {error}")
        test_global_reussi = False
    print(f"{fichier_output if test_global_reussi else None}, {resultats}")

    return (fichier_output, [['test OK']]) if test_global_reussi else (None, resultats)
