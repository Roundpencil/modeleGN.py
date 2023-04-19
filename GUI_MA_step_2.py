from enum import Enum
from tkinter import ttk
import tkinter as tk


class NotebookFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.root = root
        self.root.title("Configuration File Editor")

        # Top frame for file selection
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)


        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        self.create_tabs()
        self.pack()

    class ParamsMultiples(Enum):
        INTRIGUES = "id_dossier_intrigue_"
        PJS = "id_dossier_pjs_"
        PNJS = "id_dossier_pnjs_"
        EVENEMENTS = "id_dossier_evenements_"
        OBJETS = "id_dossier_objets_"

    def create_tabs(self):
        for param in self.ParamsMultiples:
            v_parametre = param.value
            nom_tab = v_parametre[11:-1]
            panneau = PanneauParametresMultiples(self.notebook, v_parametre)
            self.notebook.add(panneau, text=nom_tab)
        # tab1 = ttk.Frame(self.notebook)
        # self.notebook.add(tab1, text="Tab 1")
        #
        # tab2 = ttk.Frame(self.notebook)
        # self.notebook.add(tab2, text="Tab 2")

class PanneauParametresMultiples(tk.Frame):
    def __init__(self,parent,  prefixe_parametre):
        super().__init__(parent)

        self.mes_widgets = set()
        self.prefixe_parametre = prefixe_parametre

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
        return [widget.get_tuple_champ_entree for widget in self.mes_widgets]

    def add_button_click(self):
        widget_a_rajouter = widget_entree(self, self.retirer_widget_entree,
                                          prefixe_parametre=self.prefixe_parametre
                                          )
        no_ligne = len(self.mes_widgets) +1
        widget_a_rajouter.grid(row=no_ligne, column=0, columnspan=3)
        self.mes_widgets.add(widget_a_rajouter)

        print("Add button clicked")
        print(f"{[widget.get_tuple_champ_entree() for widget in self.mes_widgets]}")

    def retirer_widget_entree(self, widget_a_retirer:tk.Frame):
        self.mes_widgets.remove(widget_a_retirer)
        widget_a_retirer.destroy()

class widget_entree(tk.Frame):
    def __init__(self, master, fonction_destruction, prefixe_parametre:str, nom_param:str = "", valeur_param:str = ""):
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