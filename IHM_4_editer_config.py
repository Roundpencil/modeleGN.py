import configparser
from enum import Enum
from tkinter import ttk, filedialog
import tkinter as tk

import IHM_2_generation
import google_io as g_io
import lecteurGoogle

from tkinter import messagebox

class FenetreEditionConfig(ttk.Frame):
    def __init__(self, master, api_drive, config_parser=configparser.ConfigParser(), nom_fichier_ini=None):
        super().__init__(master)

        self.api_drive = api_drive
        self.mes_panneaux = {}
        self.nom_fichier_ini = nom_fichier_ini

        self.root = self.winfo_toplevel()
        # self.fenetre_wizard = master.master
        self.winfo_toplevel().title("Editeur de fichier configuration")
        self.grid_propagate(True)

        # Top frame for file selection
        self.top_frame = tk.Frame(self.root)
        self.top_frame.grid(row=0, column=0, pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.bouton_verif = ttk.Button(self, text="Vérifier validité paramètres", command=self.verifier_config_parser)
        self.bouton_verif.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))

        self.bouton_save = ttk.Button(self, text="Enregistrer les changements", command=self.enregistrer_ini)
        self.bouton_save.grid(row=2, column=1, padx=(5, 5), pady=(5, 5))
        if self.nom_fichier_ini is None:
            self.bouton_save['state'] = 'disabled'

        self.bouton_save_as = ttk.Button(self, text="Enregistrer sous...", command=self.enregistrer_sous_ini)
        self.bouton_save_as.grid(row=2, column=2, padx=(5, 5), pady=(5, 5))

        self.create_tabs(config_parser)
        self.grid()

    # class FenetreEditionConfig(ttk.Frame):
    #     def __init__(self, master, api_drive, config_parser=configparser.ConfigParser(), nom_fichier_ini=None, *args,
    #                  **kwargs):
    #         super().__init__(master, *args, **kwargs)
    #
    #         self.api_drive = api_drive
    #         self.mes_panneaux = {}
    #         self.nom_fichier_ini = nom_fichier_ini
    #
    #         self.fenetre_wizard = master.master
    #         self.winfo_toplevel().title("Editeur de fichier configuration")
    #
    #         # Top frame for file selection
    #         self.top_frame = tk.Frame(self.fenetre_wizard)
    #         self.top_frame.pack(pady=10)
    #
    #         self.notebook = ttk.Notebook(self)
    #         # self.notebook.pack(expand=True, fill=tk.BOTH)
    #         self.notebook.grid(row=0, column=0, columnspan=3)
    #
    #         self.bouton_verif = ttk.Button(self, text="Vérifier validité paramètres", command=self.verifier_config_parser)
    #         # self.bouton_save.pack(expand=True, fill=tk.BOTH)
    #         self.bouton_verif.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))
    #
    #         self.bouton_save = ttk.Button(self, text="Enregistrer les changements", command=self.enregistrer_ini)
    #         # self.bouton_save.pack(expand=True, fill=tk.BOTH)
    #         self.bouton_save.grid(row=1, column=1, padx=(5, 5), pady=(5, 5))
    #         if self.nom_fichier_ini is None:
    #             self.bouton_save['state'] = 'disabled'
    #
    #         self.bouton_save_as = ttk.Button(self, text="Enregistrer sous...", command=self.enregistrer_sous_ini)
    #         # self.bouton_save.pack(expand=True, fill=tk.BOTH)
    #         self.bouton_save_as.grid(row=1, column=2, padx=(5, 5), pady=(5, 5))
    #
    #         self.create_tabs(config_parser)
    #         self.pack()
    #         # self.grid()

    # def create_tabs(self, config_parser):
    #
    #     # create tabs and add them to the notebook
    #     for panneau in self.api_drive.get_liste_panneaux():
    #         tab = ttk.Frame(self.notebook)
    #         self.notebook.add(tab, text=panneau)
    #         self.mes_panneaux[panneau] = {}
    #
    #         # create and place widgets in each tab
    #         label = tk.Label(tab, text="Nom:")
    #         label.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))
    #         nom_entree = tk.Entry(tab)
    #         nom_entree.grid(row=0, column=1, padx=(5, 5), pady=(5, 5))
    #         self.mes_panneaux[panneau]["nom"] = nom_entree
    #
    #         label = tk.Label(tab, text="Type:")
    #         label.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))
    #         type_entree = tk.Entry(tab)
    #         type_entree.grid(row=1, column=1, padx=(5, 5), pady=(5, 5))
    #         self.mes_panneaux[panneau]["type"] = type_entree
    #
    #         label = tk.Label(tab, text="Valeur:")
    #         label.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))
    #         valeur_entree = tk.Entry(tab)
    #         valeur_entree.grid(row=2, column=1, padx=(5, 5), pady=(5, 5))
    #         self.mes_panneaux[panneau]["valeur"] = valeur_entree

    class ParamsMultiples(Enum):
        INTRIGUES = "id_dossier_intrigues"
        PJS = "id_dossier_pjs"
        PNJS = "id_dossier_pnjs"
        EVENEMENTS = "id_dossier_evenements"
        OBJETS = "id_dossier_objets"

    def create_tabs(self, config_parser):
        # print("bonne méthode")
        premier_panneau = PremierPanneau(parent=self, config_parser=config_parser)
        self.notebook.add(premier_panneau, text="Paramètres du GN")
        self.mes_panneaux['premier panneau'] = premier_panneau

        for param in self.ParamsMultiples:
            v_parametre = param.value
            nom_tab = v_parametre[11:-1]
            panneau = PanneauParametresMultiples(self.notebook, v_parametre, config_parser=config_parser)
            self.mes_panneaux[v_parametre] = panneau
            self.notebook.add(panneau, text=nom_tab)

        self.mes_panneaux[self.ParamsMultiples.INTRIGUES.value].set_entrees_min(1)

    def get_all_parametres(self):
        to_return = []
        for panneau in self.mes_panneaux:
            to_return.extend(panneau.get_tuples_parametres())
        return to_return

    def enregistrer_ini(self):
        # config = self.generer_configparser()
        #
        # with open('config_text.ini', 'w') as configfile:
        #     config.write(configfile)
        config_parser = self.generer_configparser()
        with open(self.nom_fichier_ini, "w") as config_file:
            config_parser.write(config_file)
        messagebox.showinfo("Enregistrement réussi",
                            f"Le fichier {self.nom_fichier_ini} a bien été mis à jour")

    def enregistrer_sous_ini(self):
        # fenetre_wizard = tk.Tk()
        # fenetre_wizard.withdraw()  # cache la fenêtre principale

        if file_path := filedialog.asksaveasfilename(
                defaultextension=".ini",
                filetypes=[("INI files", "*.ini"), ("All files", "*.*")],
                title="Choisissez un fichier pour enregistrer la configuration",
        ):
            self.nom_fichier_ini = file_path
            self.enregistrer_ini()
            self.bouton_save['state'] = 'normal'

    def verifier_config_parser(self):
        config = self.generer_configparser()
        param, resultat = g_io.verifier_config_parser(self.api_drive, config)
        IHM_2_generation.afficher_resultats_test_config(self.master, resultat, param is None)

    def generer_configparser(self):
        dict_essentiel, dict_optionnel = self.mes_panneaux['premier panneau'].generer_dictionnaires_parametres()
        tuples_intrigues = self.mes_panneaux[self.ParamsMultiples.INTRIGUES.value].get_tuples_parametres()
        # print(f"tuples = {tuples_intrigues}")
        dict_essentiel = dict_essentiel | dict(tuples_intrigues)
        print(f"dict_essentiel : {dict_essentiel}")
        tuples_pjs = self.mes_panneaux[self.ParamsMultiples.PJS.value].get_tuples_parametres()
        tuples_pnjs = self.mes_panneaux[self.ParamsMultiples.PNJS.value].get_tuples_parametres()
        tuples_evenements = self.mes_panneaux[self.ParamsMultiples.EVENEMENTS.value].get_tuples_parametres()
        tuples_objets = self.mes_panneaux[self.ParamsMultiples.OBJETS.value].get_tuples_parametres()
        dict_optionnel = dict_optionnel | \
                         dict(tuples_pjs) | \
                         dict(tuples_pnjs) | \
                         dict(tuples_evenements) | \
                         dict(tuples_objets)
        print(f"dict_optionnel : {dict_optionnel}")
        # dict_essentiel = self.retirer_clefs_vides(dict_essentiel)
        # dict_optionnel = self.retirer_clefs_vides(dict_optionnel)
        # fabrication d'un config parser
        config_ = configparser.ConfigParser()
        config_.add_section('Essentiels')
        for param in dict_essentiel:
            print(f"param, dict_essentiel[param] = {param}, {dict_essentiel[param]}")
            config_.set("Essentiels", param, dict_essentiel[param])
        config_.add_section('Optionnels')
        for param in dict_optionnel:
            config_.set("Optionnels", param, dict_optionnel[param])
        return config_

    def retirer_clefs_vides(self, d: dict):
        return {key: value for key, value in d.items() if value != ''}


class PremierPanneau(ttk.Frame):
    def __init__(self, parent=None, config_parser=configparser.ConfigParser(), *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # self.mode_association_var = None
        self.mes_widgets_essentiels = {}
        self.mes_widgets_optionnels = {}
        self.essentials_frame = None
        self.optionals_frame = None

        self.essential_params = {
            "dossier_output_squelettes_pjs": "Dossier Output Squelettes PJs",
            "nom_fichier_sauvegarde": "Nom Fichier Sauvegarde",
        }

        self.optional_params = {
            "id_factions": "ID Factions",
            "id_pjs_et_pnjs": "ID PJs et PNJs",
            "nom_fichier_pnjs": "Nom Fichier PNJs",
            "noms_persos": "Noms Persos",
            "date_gn": "Date GN",
            "prefixe_intrigues": "Prefixe Intrigues",
            "prefixe_evenements": "Prefixe Evenements",
            "prefixe_PJ": "Prefixe PJs",
            "prefixe_PNJ": "Prefixe PNJs",
            "prefixe_objets": "Prefixe Objets",
        }

        self.create_param_entries(config_parser)

    def create_param_entries(self, config_parser):
        # Create essential parameters LabelFrame
        self.essentials_frame = ttk.LabelFrame(self, text="Essentiels")
        self.essentials_frame.pack(pady=10, padx=10, fill="x")

        for index, (key, label_text) in enumerate(self.essential_params.items()):
            label = ttk.Label(self.essentials_frame, text=label_text)
            label.grid(column=0, row=index, padx=10, pady=5, sticky="w")

            entry = GidEntry(self.essentials_frame, name=f'{key}_entry')
            entry.grid(column=1, row=index, padx=10, pady=5, sticky="ew")
            entry.insert(0, config_parser.get("Essentiels", key, fallback=""))

            # mon_widget = WidgetPremierPanneau(self.essentials_frame, label_text, key, False)
            # mon_widget.grid(column=0, row=index, padx=10, pady=5, sticky="w")
            # self.mes_widgets_essentiels[key] = mon_widget

            # mode_association_var.set("0 - Automatique")
            mode_association_options = ["0 - Automatique", "1 - Manuel via fiches"]
            mode_association_dropdown = ttk.Combobox(self.essentials_frame,
                                                     values=mode_association_options, state="readonly",
                                                     name='mode_association_entry')
            if (association := config_parser.get("Essentiels", 'mode_association', fallback='')) \
                    in mode_association_options:
                # print(f"debub : mode assocaition = {association}")
                mode_association_dropdown.set(association)
            else:
                mode_association_dropdown.set("0 - Automatique")

            mode_association_dropdown.grid(column=1, row=len(self.essential_params), padx=10, pady=5, sticky="ew")

        self.essentials_frame.columnconfigure(1, weight=1)

        # Create optional parameters LabelFrame
        self.optionals_frame = ttk.LabelFrame(self, text="Optionnels")
        self.optionals_frame.pack(pady=10, padx=10, fill="x")

        for index, (key, label_text) in enumerate(self.optional_params.items()):
            valeur_par_defaut = config_parser.get("Optionnels", key, fallback='')
            var = tk.BooleanVar(value=valeur_par_defaut == '')
            entry = GidEntry(self.optionals_frame, name=f'{key}_entry')
            entry.insert(0, valeur_par_defaut)

            chk = ttk.Checkbutton(self.optionals_frame, variable=var,
                                  command=lambda e=self.optionals_frame.nametowidget(f'{key}_entry'),
                                                 v=var: self.toggle_entry(e, v))
            chk.grid(column=0, row=index, padx=(10, 0), pady=5, sticky="w")

            label = ttk.Label(self.optionals_frame, text=label_text)
            label.grid(column=1, row=index, padx=(0, 10), pady=5, sticky="w")

            entry.grid(column=2, row=index, padx=10, pady=5, sticky="ew")

            chk.invoke()  # Set the initial state of the checkboxes and entries

            self.optionals_frame.columnconfigure(2, weight=1)

    def toggle_entry(self, entry, var):
        entry['state'] = 'normal' if var.get() else 'disabled'

    def generer_dictionnaires_parametres(self):
        # tuples = []
        dict_essentiels = {}
        dict_optionnels = {}

        # for wid in self.winfo_children():
        #     print(str(wid))
        #
        for key in self.essential_params:
            entry = self.essentials_frame.nametowidget(f'{key}_entry')
            # tuples.append((key, entry.get()))
            dict_essentiels[key] = entry.get()
            print(f"debug : widget, clef, get = {entry}, {key}_entry, {entry.get()}")

        # dict_essentiels = {key: self.essentials_frame.nametowidget(f'{key}_entry').get()
        #                    for key in self.essential_params}

        entry = self.essentials_frame.nametowidget('mode_association_entry')
        # tuples.append((key, entry.get()))
        dict_essentiels['mode_association'] = entry.get()
        print(f"debug : widget, clef, get = {entry}, mode_association_entry, {entry.get()}")

        for key in self.optional_params:
            # entry = self.optionals_frame.nametowidget(f'{key}_entry')
            # #     tuples.append((key, entry.get()))
            # dict_optionnels[key] = entry.get()
            entry = self.optionals_frame.nametowidget(f'{key}_entry')
            # print(f"debug : {entry}, {entry['state']}, {entry.get()}")
            if entry['state'] == 'normal':
                dict_optionnels[key] = entry.get()
            # else:
            #     dict_optionnels[key] = ''
        # print(tuples)
        return dict_essentiels, dict_optionnels


# class WidgetPremierPanneau(ttk.Frame):
#     def __init__(self, parent, label_text, nom_parametre, avec_box=False):
#         super().__init__(parent)
#
#         self.nom_parametre = nom_parametre
#         self.var = tk.BooleanVar(value=True)
#
#         if avec_box:
#             self.chk = ttk.Checkbutton(self, variable=self.var, command=self.toggle_entry)
#             self.chk.grid(column=0, row=0, padx=(10, 0), pady=5, sticky="w")
#             self.chk.invoke()  # Set the initial state of the checkbox and entry
#
#         self.label = ttk.Label(self, text=label_text)
#         self.label.grid(column=1, row=0, padx=(0, 10), pady=5, sticky="w")
#
#         self.entry = ttk.Entry(self)
#         self.entry.grid(column=2, row=0, padx=10, pady=5, sticky="ew")
#
#         self.columnconfigure(2, weight=1)
#
#
#
#     def toggle_entry(self):
#         if self.var.get():
#             self.entry['state'] = 'normal'
#         else:
#             self.entry.delete(0, tk.END)  # Clear the entry
#             self.entry['state'] = 'disabled'
#
#     def get_tuple_champ_entree(self):
#         if self.var.get():
#             return self.nom_parametre, self.entry.get()
#         else:
#             return None, None


class PanneauParametresMultiples(ttk.Frame):
    def __init__(self, parent, prefixe_parametre, entrees_min=0, config_parser=None):
        super().__init__(parent)

        self.mes_widgets = set()
        self.prefixe_parametre = prefixe_parametre

        self.entree_min = entrees_min

        # self.row = 0
        # self.title("Editeur de fichier de configuration")
        # self.geometry("600x400")
        # self.columnconfigure(0, weight=1)
        self.grid()

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew")

        self.prefix_label = ttk.Label(self, text="prefixe paramètre")
        self.prefix_label.grid(row=0, column=0)

        self.suffix_label = ttk.Label(self, text="suffixe paramètre")
        self.suffix_label.grid(row=0, column=1)

        self.google_id_label = ttk.Label(self, text="id Google")
        self.google_id_label.grid(row=0, column=2)

        self.add_button = ttk.Button(self, text="+", command=self.add_button_click)
        self.add_button.grid(row=0, column=3)

        if config_parser is not None:
            valeurs_a_ajouter = []
            # on trouve tous les couples suffixes / valeurs dans le fichier de paramètres
            for section in config_parser.sections():
                valeurs_a_ajouter.extend(
                    [
                        key[len(self.prefixe_parametre):],
                        config_parser[section][key],
                    ]
                    for key in config_parser[section]
                    if self.prefixe_parametre in key
                )
            # on ajoute le bon nombre de champs
            for couple in valeurs_a_ajouter:
                self.add_widget_entree(couple[0], couple[1])

        self.set_entrees_min(entrees_min)

    def get_tuples_parametres(self):
        return [widget.get_tuple_champ_entree() for widget in self.mes_widgets]

    def add_widget_entree(self, suffixe="", valeur=""):
        widget_a_rajouter = WidgetEntree(self, self.retirer_widget_entree,
                                         prefixe_parametre=self.prefixe_parametre,
                                         nom_param=suffixe,
                                         valeur_param=valeur
                                         )
        no_ligne = len(self.mes_widgets) + 1
        widget_a_rajouter.grid(row=no_ligne, column=0, columnspan=4)
        self.mes_widgets.add(widget_a_rajouter)

    def set_entrees_min(self, entree_min: int):
        self.entree_min = entree_min
        while len(self.mes_widgets) < self.entree_min:
            self.add_widget_entree()

    def add_button_click(self):
        self.add_widget_entree()
        # widget_a_rajouter = widget_entree(self, self.retirer_widget_entree,
        #                                   prefixe_parametre=self.prefixe_parametre
        #                                   )
        # no_ligne = len(self.mes_widgets) + 1
        # widget_a_rajouter.grid(row=no_ligne, column=0, columnspan=4)
        # self.mes_widgets.add(widget_a_rajouter)

        # print("Add button clicked")
        # print(f"{[widget.get_tuple_champ_entree() for widget in self.mes_widgets]}")

    def retirer_widget_entree(self, widget_a_retirer: tk.Frame):
        if len(self.mes_widgets) > self.entree_min:
            self.mes_widgets.remove(widget_a_retirer)
            widget_a_retirer.destroy()


class WidgetEntree(ttk.Frame):
    def __init__(self, master, fonction_destruction, prefixe_parametre: str, nom_param: str = "",
                 valeur_param: str = ""):
        super().__init__(master=master)
        self.prefixe_parametre = prefixe_parametre

        self.label = ttk.Label(self, text=prefixe_parametre)
        self.label.grid(column=0, row=0)

        self.nom_parametre_var = tk.StringVar()
        self.nom_parametre_var.set(nom_param)
        self.nom_parametre = ttk.Entry(self, textvariable=self.nom_parametre_var)
        self.nom_parametre.grid(column=1, row=0)

        self.valeur_parametre_var = tk.StringVar()
        self.valeur_parametre_var.set(valeur_param)
        self.valeur_parametre = GidEntry(self, textvariable=self.valeur_parametre_var)
        self.valeur_parametre.grid(column=2, row=0)

        self.bouton_detruire = ttk.Button(self, text="x", command=lambda: fonction_destruction(self))
        self.bouton_detruire.grid(column=3, row=0)

    def get_tuple_champ_entree(self):
        return self.prefixe_parametre + self.nom_parametre_var.get(), self.valeur_parametre_var.get()


class GidEntry(ttk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self) -> str:
        raw = super().get()
        print(f"debug : raw = {raw} / mixed = {g_io.extraire_id_google_si_possible(raw)}")
        return g_io.extraire_id_google_si_possible(raw)[0]


if __name__ == "__main__":
    config = configparser.ConfigParser()

    # Lisez le fichier "config.ini"
    config.read('Test Factions.ini')

    root = tk.Tk()
    api_drive, _, _ = lecteurGoogle.creer_lecteurs_google_apis()
    app = FenetreEditionConfig(master=root, api_drive=api_drive, config_parser=config)
    # app = PanneauParametresMultiples("Parameter_de_demo")
    app.mainloop()
