import tkinter as tk
from tkinter import filedialog


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Mag")
        # self.master.geometry("400x400")
        # self.grid()
        # self.create_widgets()

        # Create the buttons
        self.create_gn_button = tk.Button(self.master, text="Créer nouveau GN", command=self.create_new_gn)
        self.create_gn_button.grid(row=0, column=0, sticky="nsew")

        self.regen_button = tk.Button(self.master, text="Régénérer", command=self.regen)
        self.regen_button.grid(row=1, column=0, sticky="nsew")

        self.diagnostic_button = tk.Button(self.master, text="Mode diagnostic", command=self.diagnostic_mode)
        self.diagnostic_button.grid(row=2, column=0, sticky="nsew")

        self.config_button = tk.Button(self.master, text="Changer fichier de configuration",
                                       command=self.change_config_file)
        self.config_button.grid(row=3, column=0, sticky="nsew")

        # Create the label
        self.current_file_label = tk.Label(self.master, text="Fichier ini actuel : Aucun")
        self.current_file_label.grid(row=4, column=0, columnspan=2,sticky='w')


    # def create_widgets(self):
    #     self.new_gn_button = tk.Button(self, text="Créer nouveau GN", command=self.create_new_gn)
    #     self.new_gn_button.grid(row=0, column=0)
    #
    #     self.update_button = tk.Button(self, text="Générer fiches mises à jour", command=self.regen)
    #     self.update_button.grid(row=0, column=1)
    #
    #     self.diagnostic_button = tk.Button(self, text="Mode diagnostic", command=self.diagnostic_mode)
    #     self.diagnostic_button.grid(row=0, column=2)
    #
    #     self.config_file_button = tk.Button(self, text="Changer fichier de configuration",
    #                                         command=self.change_config_file)
    #     self.config_file_button.grid(row=1, column=0)
    #
    #     self.current_file_label = tk.Label(self, text="Fichier ini actuel")
    #     self.current_file_label.grid(row=1, column=1)

    def create_new_gn(self):
        new_gn_window = tk.Toplevel(self.master)
        new_gn_window.title("Créer nouveau GN")
        new_gn_window.geometry("450x270")

        intrigues_label = tk.Label(new_gn_window, text="Intrigues")
        intrigues_label.grid(row=0, column=0)
        intrigues_entry = tk.Entry(new_gn_window)
        intrigues_entry.grid(row=0, column=1)

        base_persos_gn_label = tk.Label(new_gn_window, text="Base persos GN")
        base_persos_gn_label.grid(row=1, column=0)
        base_persos_gn_entry = tk.Entry(new_gn_window)
        base_persos_gn_entry.grid(row=1, column=1)

        fichier_faction_label = tk.Label(new_gn_window, text="Fichier faction")
        fichier_faction_label.grid(row=2, column=0)
        fichier_faction_entry = tk.Entry(new_gn_window)
        fichier_faction_entry.grid(row=2, column=1)

        id_factions_label = tk.Label(new_gn_window, text="ID factions")
        id_factions_label.grid(row=3, column=0)
        id_factions_entry = tk.Entry(new_gn_window)
        id_factions_entry.grid(row=3, column=1)

        dossier_output_squelettes_pjs_label = tk.Label(new_gn_window, text="Dossier output squelettes PJs")
        dossier_output_squelettes_pjs_label.grid(row=4, column=0)
        dossier_output_squelettes_pjs_entry = tk.Entry(new_gn_window)
        dossier_output_squelettes_pjs_entry.grid(row=4, column=1)

        association_auto_label = tk.Label(new_gn_window, text="Association auto")
        association_auto_label.grid(row=5, column=0)
        association_auto_var = tk.IntVar()
        association_auto_yes = tk.Radiobutton(new_gn_window, text="Oui", variable=association_auto_var, value=1)
        association_auto_yes.grid(row=5, column=1)
        association_auto_no = tk.Radiobutton(new_gn_window, text="Non", variable=association_auto_var, value=0)
        association_auto_no.grid(row=5, column=2)

        type_fiche_label = tk.Label(new_gn_window, text="Type de fiche")
        type_fiche_label.grid(row=6, column=0)
        type_fiche_var = tk.StringVar(new_gn_window)
        type_fiche_var.set("Chalacta")
        type_fiche_dropdown = tk.OptionMenu(new_gn_window, type_fiche_var, "Chalacta", "Modèle 7 colonnes")
        type_fiche_dropdown.grid(row=6, column=1)

        nom_fichier_sauvegarde_label = tk.Label(new_gn_window, text="Nom fichier sauvegarde")
        nom_fichier_sauvegarde_label.grid(row=7, column=0)
        nom_fichier_sauvegarde_entry = tk.Entry(new_gn_window)
        nom_fichier_sauvegarde_entry.grid(row=7, column=1)

        noms_persos_label = tk.Label(new_gn_window, text="Noms persos")
        noms_persos_label.grid(row=8, column=0)
        noms_persos_entry = tk.Entry(new_gn_window)
        noms_persos_entry.grid(row=8, column=1)

        nom_fichier_pnjs_label = tk.Label(new_gn_window, text="Nom fichier PNJs")

        nom_fichier_pnjs_label.grid(row=9, column=0)
        nom_fichier_pnjs_entry = tk.Entry(new_gn_window)
        nom_fichier_pnjs_entry.grid(row=9, column=1)

        submit_button = tk.Button(new_gn_window, text="Valider",
                                  command=lambda: self.submit_new_gn(intrigues_entry.get(), base_persos_gn_entry.get(),
                                                                     fichier_faction_entry.get(), id_factions_entry.get(),
                                                                     dossier_output_squelettes_pjs_entry.get(),
                                                                     association_auto_var.get(), type_fiche_var.get(),
                                                                     nom_fichier_sauvegarde_entry.get(),
                                                                     noms_persos_entry.get(), nom_fichier_pnjs_entry.get()))
        submit_button.grid(row=10, column=0)


    def submit_new_gn(self, intrigues, base_persos_gn, fichier_faction, id_factions, dossier_output_squelettes_pjs,
                      association_auto, type_fiche, nom_fichier_sauvegarde, noms_persos, nom_fichier_pnjs):
        # Do something with the user's input
        print(f"Intrigues: {intrigues}")
        print(f"Base persos GN: {base_persos_gn}")
        print(f"Fichier faction: {fichier_faction}")
        print(f"ID factions: {id_factions}")
        print(f"Dossier output squelettes PJs: {dossier_output_squelettes_pjs}")
        print(f"Association auto: {association_auto}")
        print(f"Type de fiche: {type_fiche}")
        print(f"Nom fichier sauvegarde: {nom_fichier_sauvegarde}")
        print(f"Noms persos: {noms_persos}")
        print(f"Nom fichier PNJs: {nom_fichier_pnjs}")



    def diagnostic_mode(self):
        diagnostic_window = tk.Toplevel(self.master)
        diagnostic_window.title("Mode diagnostic")
        diagnostic_window.geometry("400x400")

        # Create the 3x3 button grid
        for i in range(3):
            for j in range(3):
                button = tk.Button(diagnostic_window)
                button.grid(row=i, column=j)


    def change_config_file(self):
        config_file = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                 filetypes=(("ini files", "*.ini"), ("all files", "*.*")))
        self.current_file_label.config(text=config_file)



    def regen(self):
        regen_window = tk.Toplevel(self.master)
        regen_window.geometry("600x150") # adjust the size of the window

        # Intrigues
        intrigues_label = tk.Label(regen_window, text="Intrigues")
        intrigues_label.grid(row=0, column=0, columnspan=2)

        intrigues_var = tk.StringVar(regen_window)
        intrigues_var.set("Rapide")

        intrigues_rapide = tk.Radiobutton(regen_window, text="Rapide", variable=intrigues_var, value="Rapide", command=lambda:self.regen_intrigue_select("Rapide"))
        intrigues_rapide.grid(row=1, column=0)
        intrigues_complet = tk.Radiobutton(regen_window, text="Complet", variable=intrigues_var, value="Complet", command=lambda:self.regen_intrigue_select("Complet"))
        intrigues_complet.grid(row=1, column=1)
        intrigues_specifique = tk.Radiobutton(regen_window, text="Spécifique", variable=intrigues_var, value="Spécifique", command=lambda:self.regen_intrigue_select("Spécifique"))
        intrigues_specifique.grid(row=1, column=2)

        self.intrigue_specifique_entry = tk.Entry(regen_window)
        self.intrigue_specifique_entry.grid(row=1, column=3)
        self.intrigue_specifique_entry.config(state='disabled')

        # Personnages
        personnages_label = tk.Label(regen_window, text="Personnages")
        personnages_label.grid(row=2, column=0, columnspan=2)

        personnages_var = tk.StringVar(regen_window)
        personnages_var.set("Rapide")

        personnages_rapide = tk.Radiobutton(regen_window, text="Rapide", variable=personnages_var, value="Rapide", command=lambda:self.regen_personnages_select("Rapide"))
        personnages_rapide.grid(row=3, column=0)
        personnages_complet = tk.Radiobutton(regen_window, text="Complet", variable=personnages_var, value="Complet", command=lambda:self.regen_personnages_select("Complet"))
        personnages_complet.grid(row=3, column=1)
        personnages_specifique = tk.Radiobutton(regen_window, text="Spécifique", variable=personnages_var, value="Spécifique", command=lambda:self.regen_personnages_select("Spécifique"))
        personnages_specifique.grid(row=3, column=2)

        self.personnages_specifique_entry = tk.Entry(regen_window)
        self.personnages_specifique_entry.grid(row=3, column=3)
        self.personnages_specifique_entry.config(state='disable')

        charger_fichier_var = tk.BooleanVar()
        charger_fichier_var.set(True)
        charger_fichier_check = tk.Checkbutton(regen_window, text="Charger depuis fichier", variable=charger_fichier_var)
        charger_fichier_check.grid(row=4, column=0)

        sauver_apres_operation_var = tk.BooleanVar()
        sauver_apres_operation_var.set(True)
        sauver_apres_operation_check = tk.Checkbutton(regen_window, text="Sauver après opération", variable=sauver_apres_operation_var)
        sauver_apres_operation_check.grid(row=4, column=1)

        generer_fichiers_drive_var = tk.BooleanVar()
        generer_fichiers_drive_var.set(True)
        generer_fichiers_drive_check = tk.Checkbutton(regen_window, text="Générer fichiers Drive", variable=generer_fichiers_drive_var)
        generer_fichiers_drive_check.grid(row=4, column=2)

        # Buttons
        cancel_button = tk.Button(regen_window, text="Annuler", command=regen_window.destroy)
        cancel_button.grid(row=5, column=0)

        ok_button = tk.Button(regen_window, text="OK",
                              command=lambda: self.process_regen(intrigues_var.get(), personnages_var.get(),
                                                                 charger_fichier_var.get(), sauver_apres_operation_var.get(),
                                                                 generer_fichiers_drive_var.get()))
        ok_button.grid(row=5, column=1)




    # def regen(self):
    #     regen_window = tk.Toplevel(self.master)
    #     regen_window.title("Régénération")
    #     regen_window.geometry("500x500")
    #
    #     # Intrigues
    #     intrigues_label = tk.Label(regen_window, text="Intrigues :")
    #     intrigues_label.grid(row=0, column=0)
    #
    #     intrigues_var = tk.StringVar(regen_window)
    #     intrigues_var.set("Rapide")
    #
    #     intrigues_rapide = tk.Radiobutton(regen_window, text="Rapide", variable=intrigues_var, value="Rapide",
    #                                       command=lambda: self.regen_intrigue_select("Rapide"))
    #     intrigues_rapide.grid(row=0, column=1)
    #     intrigues_complet = tk.Radiobutton(regen_window, text="Complet", variable=intrigues_var, value="Complet",
    #                                        command=lambda: self.regen_intrigue_select("Complet"))
    #     intrigues_complet.grid(row=0, column=2)
    #     intrigues_specifique = tk.Radiobutton(regen_window, text="Spécifique", variable=intrigues_var, value="Spécifique",
    #                                           command=lambda: self.regen_intrigue_select("Spécifique"))
    #     intrigues_specifique.grid(row=0, column=3)
    #
    #     self.intrigue_specifique_entry = tk.Entry(regen_window)
    #     self.intrigue_specifique_entry.grid(row=1, column=1, columnspan=3)
    #     self.intrigue_specifique_entry.config(state='disabled')
    #
    #     # Personnages
    #     personnages_label = tk.Label(regen_window, text="Personnages :")
    #     personnages_label.grid(row=2, column=0)
    #
    #     personnages_var = tk.StringVar(regen_window)
    #
    #
    #     personnages_var.set("Rapide")
    #
    #     personnages_rapide = tk.Radiobutton(regen_window, text="Rapide", variable=personnages_var, value="Rapide",
    #                                         command=lambda: self.regen_personnages_select("Rapide"))
    #     personnages_rapide.grid(row=2, column=1)
    #     personnages_complet = tk.Radiobutton(regen_window, text="Complet", variable=personnages_var, value="Complet",
    #                                          command=lambda: self.regen_personnages_select("Complet"))
    #     personnages_complet.grid(row=2, column=2)
    #     personnages_specifique = tk.Radiobutton(regen_window, text="Spécifique", variable=personnages_var, value="Spécifique",
    #                                             command=lambda: self.regen_personnages_select("Spécifique"))
    #     personnages_specifique.grid(row=2, column=3)
    #
    #     self.personnages_specifique_entry = tk.Entry(regen_window)
    #     self.personnages_specifique_entry.grid(row=3, column=1, columnspan=3)
    #     self.personnages_specifique_entry.config(state='disabled')
    #
    #     # Checkboxes
    #     charger_fichier_var = tk.IntVar(value=1)
    #     charger_fichier_checkbox = tk.Checkbutton(regen_window, text="Charger depuis fichier", variable=charger_fichier_var)
    #     charger_fichier_checkbox.grid(row=4, column=0)
    #
    #     sauver_apres_operation_var = tk.IntVar(value=1)
    #     sauver_apres_operation_checkbox = tk.Checkbutton(regen_window, text="Sauver après opération",
    #                                                      variable=sauver_apres_operation_var)
    #     sauver_apres_operation_checkbox.grid(row=4, column=1)
    #
    #     generer_fichiers_drive_var = tk.IntVar(value=1)
    #     generer_fichiers_drive_checkbox = tk.Checkbutton(regen_window, text="Générer fichiers Drive",
    #                                                      variable=generer_fichiers_drive_var)
    #     generer_fichiers_drive_checkbox.grid(row=4, column=2)
    #
    #     # Buttons
    #     cancel_button = tk.Button(regen_window, text="Annuler", command=regen_window.destroy)
    #     cancel_button.grid(row=5, column=0)
    #
    #     ok_button = tk.Button(regen_window, text="OK",
    #                           command=lambda: self.process_regen(intrigues_var.get(), personnages_var.get(),
    #                                                              charger_fichier_var.get(), sauver_apres_operation_var.get(),
    #                                                              generer_fichiers_drive_var.get()))
    #     ok_button.grid(row=5, column=1)

    def regen_intrigue_select(self, value):
        if value == "Rapide" or value == "Complet":
            self.intrigue_specifique_entry.config(state='disabled')
        elif value == "Spécifique":
            self.intrigue_specifique_entry.config(state='normal')

    def regen_personnages_select(self, value):
        if value == "Rapide" or value == "Complet":
            self.personnages_specifique_entry.config(state='disabled')
        elif value == "Spécifique":
            self.personnages_specifique_entry.config(state='normal')


    def process_regen(self, intrigues_value, personnages_value, charger_fichier_value, sauver_apres_operation_value,
                      generer_fichiers_drive_value):
        if intrigues_value == "Spécifique":
            intrigue_specifique = self.intrigue_specifique_entry.get()
        else:
            intrigue_specifique = ""
        if personnages_value == "Spécifique":
            personnages_specifique = self.personnages_specifique_entry.get()
        else:
            personnages_specifique = ""
        # Call the existing method that process the result with the input values:
        print("intrigues_value, intrigue_specifique, personnages_value, personnages_specifique,"
                        "charger_fichier_value, sauver_apres_operation_value, generer_fichiers_drive_value")


def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


if __name__ == '__main__':
    main()
