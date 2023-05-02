import tkinter as tk
import webbrowser
from configparser import ConfigParser, ParsingError
from tkinter import ttk, messagebox, filedialog

import IHM_2_generation
import IHM_3_nouveau_GN
import IHM_4_editer_config
import lecteurGoogle


class MAGnetMainGUI(ttk.Frame):
    def __init__(self, master, api_drive, api_doc, api_sheets, mode_leger=True):
        super().__init__(master)

        # self.geometry("300x150")
        # self.title("Application principale")
        self.api_drive = api_drive
        self.api_doc = api_doc
        self.api_sheets = api_sheets
        self.current_window = None

        #déclration du menu
        # menu = tk.Menu(self)
        # self.master.config(menu=menu)
        #
        # view_menu = tk.Menu(menu)
        # menu.add_cascade(label="Menu", menu=view_menu)
        # view_menu.add_command(label="Nouveau GN...", command=self.nouveau_gn)
        # view_menu.add_command(label="Nouveau fichier de configuration", command=self.nouvelle_config)
        # view_menu.add_command(label="Editer fichier de configuration...", command=self.editer_config)
        # view_menu.add_command(label="Mouliner ", command=self.ecran_mouliner)
        # view_menu.add_command(label="Quitter ", command=self.quitter)
        # Create the top-level menu bar
        menu = tk.Menu(self, tearoff=0)
        self.master.config(menu=menu)

        # Create a "Menu" drop-down menu
        menu1 = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Aller vers", menu=menu1)

        # Add commands to the "Menu" drop-down menu
        menu1.add_command(label="Nouveau GN...", command=self.nouveau_gn)
        menu1.add_command(label="Nouveau fichier de configuration", command=self.nouvelle_config)
        menu1.add_command(label="Editer fichier de configuration...", command=self.editer_config)
        menu1.add_command(label="Mouliner ", command=self.ecran_mouliner)
        menu1.add_command(label="Quitter ", command=self.quitter)

        # Create an "Aide et Références" drop-down menu
        menu2 = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Aide et Références", menu=menu2)

        # Add commands to the "Aide et Références" drop-down menu
        menu2.add_command(label="Ouvrir le manuel", command=self.ouvrir_manuel)
        menu2.add_command(label="Ouvrir les fichiers de référence", command=self.ouvrir_fichiers_reference)
        menu2.add_command(label="Historique des versions", command=self.historique_versions)

        self.ecran_mouliner()

    def quitter(self):
        self.winfo_toplevel().destroy()

    def editer_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("Fichiers INI", "*.ini")])

        if not file_path:
            messagebox.showerror("Erreur", "Aucun fichier sélectionné")
            return

        config_parser = ConfigParser()

        try:
            config_parser.read(file_path)
        except ParsingError as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du fichier .ini :\n{e}")
            return

        future_fenetre = IHM_4_editer_config.FenetreEditionConfig(self.winfo_toplevel(), self.api_drive, config_parser,
                                                           file_path)
        self.change_window(future_fenetre)

    def nouvelle_config(self):
        future_fenetre = IHM_4_editer_config .FenetreEditionConfig(self.winfo_toplevel(), self.api_drive)
        self.change_window(future_fenetre)

    def nouveau_gn(self):
        future_fenetre = IHM_3_nouveau_GN.WizzardGN(self.winfo_toplevel(), api_drive=self.api_drive)
        self.change_window(future_fenetre)

    def ecran_mouliner(self):
        future_fenetre = IHM_2_generation.Application(self.winfo_toplevel(),
                                                api_drive=self.api_drive,
                                                api_doc=self.api_doc,
                                                api_sheets=self.api_sheets,
                                                )
        self.change_window(future_fenetre)

    def ouvrir_manuel(self):
        webbrowser.open_new("https://docs.google.com/document/d"
                            "/1U1D5byuXXv6_dHo13fcn9ka50pYYHzMlNGtH3gfE1Sc")

    def ouvrir_fichiers_reference(self):
        webbrowser.open_new("https://drive.google.com/drive/folders/1mpcnbpP2SV_K-REbcgnsnaCut_w_Xfcc?usp=share_link")

    def historique_versions(self):
        webbrowser.open_new("https://docs.google.com/document/d/"
                            "1FjW4URMWML_UX1Tw7SiJBaoOV4P7F_rKG9pmnOBjO4Q/edit?usp=sharing")


    def change_window(self, new_window):
        if self.current_window:
            self.current_window.grid_forget()
            # self.current_window.destroy()

        # new_window.pack(fill=tk.BOTH, expand=True)
        new_window.grid(row=0, column=0, sticky=tk.NSEW)
        # new_window.grid()
        self.current_window = new_window


if __name__ == "__main__":
    root = tk.Tk()
    api_drive, api_doc, api_sheets = lecteurGoogle.creer_lecteurs_google_apis()
    app = MAGnetMainGUI(master=root, api_drive=api_drive, api_doc=api_doc, api_sheets=api_sheets)

    app.mainloop()
