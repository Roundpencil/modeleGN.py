import configparser
from enum import Enum
from tkinter import ttk
import tkinter as tk


class NotebookFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.mes_panneaux = {}

        self.root = root
        self.root.title("Editeur de fichier configuration")

        # Top frame for file selection
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        self.bouton_go = ttk.Button(self, text="Générer fichier ini", command=self.generer_fichier_ini)
        self.bouton_go.pack(expand=True, fill=tk.BOTH)
        self.create_tabs()
        self.pack()

    class ParamsMultiples(Enum):
        INTRIGUES = "id_dossier_intrigues_"
        PJS = "id_dossier_pjs_"
        PNJS = "id_dossier_pnjs_"
        EVENEMENTS = "id_dossier_evenements_"
        OBJETS = "id_dossier_objets_"

    def create_tabs(self):
        premier_panneau = PremierPanneau(parent=self)
        self.notebook.add(premier_panneau, text="Paramètres du GN")
        self.mes_panneaux['premier panneau'] = premier_panneau

        for param in self.ParamsMultiples:
            v_parametre = param.value
            nom_tab = v_parametre[11:-1]
            panneau = PanneauParametresMultiples(self.notebook, v_parametre)
            self.mes_panneaux[v_parametre] = panneau
            self.notebook.add(panneau, text=nom_tab)

        self.mes_panneaux[self.ParamsMultiples.INTRIGUES.value].set_entrees_min(1)

    def get_all_parametres(self):
        to_return = []
        for panneau in self.mes_panneaux:
            to_return.extend(panneau.get_tuples_parametres())
        return to_return

    def generer_fichier_ini(self):
        dict_essentiel, dict_optionnel = self.mes_panneaux['premier panneau'].generer_dictionnaires_parametres()

        tuples_intrigues = self.mes_panneaux[self.ParamsMultiples.INTRIGUES.value].get_tuples_parametres()
        # print(f"tuples = {tuples_intrigues}")
        dict_essentiel = dict_essentiel | dict(tuples_intrigues)
        # print(f"dict_essentiel : {dict_essentiel}")

        tuples_pjs = self.mes_panneaux[self.ParamsMultiples.PJS.value].get_tuples_parametres()
        tuples_pnjs = self.mes_panneaux[self.ParamsMultiples.PNJS.value].get_tuples_parametres()
        tuples_evenements = self.mes_panneaux[self.ParamsMultiples.EVENEMENTS.value].get_tuples_parametres()
        tuples_objets = self.mes_panneaux[self.ParamsMultiples.OBJETS.value].get_tuples_parametres()

        dict_optionnel = dict_optionnel | \
                         dict(tuples_pjs) | \
                         dict(tuples_pnjs) | \
                         dict(tuples_evenements) | \
                         dict(tuples_objets)
        # print(f"dict_optionnel : {dict_optionnel}")

        # dict_essentiel = self.retirer_clefs_vides(dict_essentiel)
        # dict_optionnel = self.retirer_clefs_vides(dict_optionnel)

        # fabrication d'un config parser
        config = configparser.ConfigParser()
        config.add_section('Essentiels')
        for param in dict_essentiel:
            config.set("Essentiels", param, dict_essentiel[param])

        config.add_section('Optionnels')
        for param in dict_optionnel:
            config.set("Optionnels", param, dict_optionnel[param])

        with open('config_text.ini', 'w') as configfile:
            config.write(configfile)

    def retirer_clefs_vides(self, d:dict):
        return {key: value for key, value in d.items() if value != ''}

class PremierPanneau(ttk.Frame):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.mes_widgets_essentiels = {}
        self.mes_widgets_optionnels = {}
        self.essentials_frame = None
        self.optionals_frame = None

        self.essential_params = {
            "dossier_output_squelettes_pjs": "Dossier Output Squelettes PJs",
            "mode_association": "Mode Association",
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
            "prefixe_PJs": "Prefixe PJs",
            "prefixe_PNJs": "Prefixe PNJs",
            "prefixe_objets": "Prefixe Objets",
        }

        self.create_param_entries()

    def create_param_entries(self):
        # Create essential parameters LabelFrame
        self.essentials_frame = ttk.LabelFrame(self, text="Essentiels")
        self.essentials_frame.pack(pady=10, padx=10, fill="x")

        for index, (key, label_text) in enumerate(self.essential_params.items()):
            label = ttk.Label(self.essentials_frame, text=label_text)
            label.grid(column=0, row=index, padx=10, pady=5, sticky="w")

            entry = ttk.Entry(self.essentials_frame, name=f'{key}_entry')
            entry.grid(column=1, row=index, padx=10, pady=5, sticky="ew")
            # mon_widget = WidgetPremierPanneau(self.essentials_frame, label_text, key, False)
            # mon_widget.grid(column=0, row=index, padx=10, pady=5, sticky="w")
            # self.mes_widgets_essentiels[key] = mon_widget

        self.essentials_frame.columnconfigure(1, weight=1)

        # Create optional parameters LabelFrame
        self.optionals_frame = ttk.LabelFrame(self, text="Optionnels")
        self.optionals_frame.pack(pady=10, padx=10, fill="x")

        for index, (key, label_text) in enumerate(self.optional_params.items()):
            #     label = ttk.Label(self.optionals_frame, text=label_text)
            #     label.grid(column=0, row=index, padx=10, pady=5, sticky="w")
            #
            #     entry = ttk.Entry(self.optionals_frame, name=f'{key}_entry')
            #     entry.grid(column=1, row=index, padx=10, pady=5, sticky="ew")
            #
            # self.optionals_frame.columnconfigure(1, weight=1)
            var = tk.BooleanVar(value=True)
            entry = ttk.Entry(self.optionals_frame, name=f'{key}_entry')

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
        if var.get():
            entry['state'] = 'normal'
        else:
            # entry.delete(0, tk.END)  # Clear the entry
            entry['state'] = 'disabled'

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

        # dict_essentiels = {key: self.essentials_frame.nametowidget(f'{key}_entry').get()
        #                    for key in self.essential_params}

        for key in self.optional_params:
            # entry = self.optionals_frame.nametowidget(f'{key}_entry')
            # #     tuples.append((key, entry.get()))
            # dict_optionnels[key] = entry.get()
            entry = self.optionals_frame.nametowidget(f'{key}_entry')
            print(f"debug : {entry}, {entry['state']}, {entry.get()}")
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
    def __init__(self, parent, prefixe_parametre, entrees_min = 0):
        super().__init__(parent)


        self.mes_widgets = set()
        self.prefixe_parametre = prefixe_parametre

        self.entree_min = entrees_min
        self.set_entrees_min(entrees_min)

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

    def get_tuples_parametres(self):
        return [widget.get_tuple_champ_entree() for widget in self.mes_widgets]

    def add_widget_entree(self):
        widget_a_rajouter = widget_entree(self, self.retirer_widget_entree,
                                          prefixe_parametre=self.prefixe_parametre
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


class widget_entree(ttk.Frame):
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
        self.valeur_parametre = ttk.Entry(self, textvariable=self.valeur_parametre_var)
        self.valeur_parametre.grid(column=2, row=0)

        self.bouton_detruire = ttk.Button(self, text="x", command=lambda: fonction_destruction(self))
        self.bouton_detruire.grid(column=3, row=0)

    def get_tuple_champ_entree(self):
        return self.prefixe_parametre + self.nom_parametre_var.get(), self.valeur_parametre_var.get()


if __name__ == "__main__":
    root = tk.Tk()
    app = NotebookFrame(master=root)
    # app = PanneauParametresMultiples("Parameter_de_demo")
    app.mainloop()