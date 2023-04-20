import tkinter as tk
from configparser import ConfigParser, ParsingError
from tkinter import ttk, messagebox, filedialog

import IHM_MAGnet
import IHM_step_two


class MAGnetMainGUI(ttk.Frame):
    def __init__(self, master, api_drive, api_doc, api_sheets, mode_leger=True):
        super().__init__(master)

        # self.geometry("300x150")
        # self.title("Application principale")

        menu = tk.Menu(self)
        self.master.config(menu=menu)
        self.current_window = None

        self.api_drive = api_drive
        self.api_doc = api_drive
        self.api_sheets = api_sheets


        view_menu = tk.Menu(menu)
        menu.add_cascade(label="Vues", menu=view_menu)
        # view_menu.add_command(label="Nouveau GN...", command=self.show_first_window)
        view_menu.add_command(label="Nouveau fichier de configuration", command=self.nouvelle_config)
        view_menu.add_command(label="Editer fichier de configuration...", command=self.editer_config)
        view_menu.add_command(label="Mouliner ", command=self.mouliner)

        # self.mouliner()


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

        future_fenetre = IHM_step_two.FenetreEditionConfig(self, self.api_drive, config_parser, file_path)
        self.change_window(future_fenetre)

    def nouvelle_config(self):
        future_fenetre = IHM_step_two.FenetreEditionConfig(self, self.api_drive)
        self.change_window(future_fenetre)

    def mouliner(self):
        future_fenetre = IHM_MAGnet.Application(api_drive=self.api_drive,
                                                api_doc=self.api_doc,
                                                api_sheets=self.api_sheets,
                                                master=self)
        self.change_window(future_fenetre)


    def change_window(self, new_window):
        if self.current_window:
            self.current_window.pack_forget()

        new_window.pack(fill=tk.BOTH, expand=True)
        self.current_window = new_window


if __name__ == "__main__":
    app = MAGnetMainGUI()
    app.mainloop()
