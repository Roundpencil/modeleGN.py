import queue
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from datetime import datetime, timedelta
import threading

import google_io as g_io
import module_affectation_pnjs
from modeleGN import GN, id_2_doc_address, id_2_sheet_address
from module_affectation_pnjs import creer_planning
from tkinter import ttk


class GUIPNJS(ttk.Frame):
    def __init__(self, parent, api_drive, api_doc, api_sheet):
        super().__init__(parent)
        self.bouton_enregistrer = None
        self.winfo_toplevel().title("Module affectation des PNJs")

        self.root = self
        # self.root.title("My Tkinter GUI")
        # self.root.geometry("620x300")

        self.file_label = tk.Label(self.root, text="")
        self.test_status = tk.StringVar(value="Non testé")
        self.estimated_iteration_time = tk.DoubleVar(value=0)
        self.estimated_total_time = tk.StringVar(value="")
        self.estimated_end_time = tk.StringVar(value="")
        self.done_iterations = tk.StringVar(value="0")
        self.meilleure_solution = tk.StringVar(value="0")

        self.gn = None
        self.api_sheet = api_sheet
        self.api_drive = api_drive
        self.api_doc = api_doc

        self.planning_thread = None
        self.result_queue = None
        self.overlapping_queue = None

        self.create_widgets()

    def create_widgets(self):
        tk.Button(self.root, text="Charger fichier MGN", command=self.charger_fichier_mgn).grid(row=10, column=0,
                                                                                                padx=5, pady=10,
                                                                                                sticky="e")
        self.file_label.grid(row=10, column=1, columnspan=3, pady=10, sticky="w")

        tk.Label(self.root, text="Temps itération moyen :") \
            .grid(row=36, column=0, padx=5, pady=10, sticky="e")
        tk.Label(self.root, textvariable=self.estimated_iteration_time, width=20).grid(row=36, column=1,
                                                                                       padx=5, pady=10,
                                                                                       sticky="w")

        tk.Label(self.root, text="Nombre d'itérations:", width=20).grid(row=30, column=0, padx=5, pady=5, sticky="e")
        self.iterations_entry = tk.Entry(self.root)
        self.iterations_entry.insert(0, '250')
        self.iterations_entry.grid(row=30, column=1, padx=5, pady=5, sticky="w")
        self.iterations_entry.bind("<KeyRelease>", self.update_estimated_total_time)

        tk.Label(self.root, text="Durée d'un pas (en mn) :", width=20).grid(row=30, column=2, padx=5, pady=5,
                                                                            sticky="e")
        self.pas_entry = tk.Entry(self.root)
        self.pas_entry.insert(0, "15")
        self.pas_entry.grid(row=30, column=3, padx=5, pady=5, sticky="w")

        tk.Label(self.root, text="Temps estimé :").grid(row=36, column=2, padx=5, pady=10, sticky="e")
        tk.Label(self.root, textvariable=self.estimated_total_time).grid(row=36, column=3, padx=5, pady=10, sticky="w")

        tk.Button(self.root, text="Lancer / Relancer", command=self.start_process).grid(row=40, column=0, columnspan=1,
                                                                                        pady=10)

        self.progress_bar = Progressbar(self.root, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.grid(row=40, column=1, columnspan=3, pady=10, sticky="nsew", padx=5)

        tk.Label(self.root, text="Itérations effectuées :").grid(row=60, column=0, padx=5, pady=10, sticky="e")
        tk.Label(self.root, textvariable=self.done_iterations).grid(row=60, column=1, columnspan=1, pady=10,
                                                                    sticky="w")
        self.bouton_enregistrer = tk.Button(self.root,
                                            text="Enregistrer résultat (planning et \n fichier des erreurs)"
                                                 " dans dossier output",
                                            command=self.save_to_drive, state='disabled')
        self.bouton_enregistrer.grid(row=60, column=2, padx=5, columnspan=2, pady=10, sticky="e", rowspan=2)

        tk.Label(self.root, text="Heure de fin estimée :").grid(row=61, column=0, padx=5, pady=10, sticky="e")
        tk.Label(self.root, textvariable=self.estimated_end_time).grid(row=61, column=1, columnspan=1, pady=10,
                                                                       sticky="w")

        tk.Label(self.root, text="Meilleure solution :").grid(row=62, column=0, padx=5, pady=10, sticky="e")
        tk.Label(self.root, textvariable=self.meilleure_solution).grid(row=62, column=1, columnspan=1, pady=10,
                                                                       sticky="w")

    def charger_fichier_mgn(self):
        file_path = filedialog.askopenfilename(
            title="Ouvrir un fichier MGN",
            filetypes=(("Fichiers MGN", "*.mgn"), ("Tous les fichiers", "*.*"))
        )
        if file_path:
            self.file_label.config(text=f"Fichier sélectionné : {file_path}")
            self.gn = GN.load(file_path)

    def tester_fichier(self):
        self.test_status.set("OK")
        self.estimated_iteration_time.set(2.5)
        self.update_estimated_total_time()

    def update_estimated_total_time(self, *args):
        try:
            iterations = int(self.iterations_entry.get())
            if self.estimated_iteration_time.get() > 0:
                total_time_seconds = iterations * self.estimated_iteration_time.get()
                hours, remainder = divmod(total_time_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.estimated_total_time.set(f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}")
            else:
                self.estimated_total_time.set("")
        except ValueError:
            self.estimated_total_time.set("")

    def start_process(self):
        try:
            # je compte mon nombre d'itérations et mon pas
            iterations = int(self.iterations_entry.get())
            pas = int(self.pas_entry.get())

            # j'initialise ma barre de progres
            self.progress_bar["maximum"] = iterations
            self.progress_bar["value"] = 0

            # # Create a thread to run the creer_planning function
            # planning_thread = threading.Thread(target=creer_planning,
            #                                    args=(self.gn, iterations, pas,
            #                                          lambda x, y, z: self.observateur(iterations, x, y, z)))
            #
            # planning_thread.start()

            # Define the wrapper function
            def wrapper(gn, iterations_to_to, taille_pas, observateur, result_queue, overlapping_queue):
                result, overlapping = creer_planning(gn, iterations_to_to, taille_pas, observateur)
                result_queue.put(result)
                overlapping_queue.put(overlapping)

            # Create a queue to store the result
            self.result_queue = queue.Queue()
            self.overlapping_queue = queue.Queue()

            # Create a thread to run the wrapper function
            self.planning_thread = threading.Thread(
                target=wrapper,
                args=(self.gn, iterations, pas, lambda x, y, z: self.observateur(iterations, x, y, z),
                      self.result_queue, self.overlapping_queue)
            )

            # Start the thread
            self.planning_thread.start()

        except ValueError as e:
            if "invalid literal" in str(e):
                e = "Le nombre d'itérations et la durée en pas doivent être des nombres"

            messagebox.showerror("Une erreur est survenue", str(e))

    def update_progress_bar(self, iteration):
        self.progress_bar["value"] = iteration + 1

    def observateur(self, iterations, iteration, temps_ecoule, mink):
        # mettre à jour la barre de progression
        self.update_progress_bar(iteration)

        # mettre à jour le temps moyen par itération
        self.update_estimated_iteration_time(iteration, temps_ecoule)

        # mettre à jour le compteur d'heure de fin
        self.update_heure_fin(iterations, iteration, temps_ecoule)

        # mettre à jour le compteur d'itérations
        self.update_compteur_iterations(iterations, iteration)

        # mettre à jour la meilleure solution
        self.update_meilleure_solution(mink)

        if iteration + 1 == iterations:
            messagebox.showinfo("Opération Terminée", f"Durée totale {temps_ecoule} secondes")
            self.bouton_enregistrer.config(state="normal")

    def update_heure_fin(self, iterations, iteration, temps_ecoule, verbal=False):
        secondes_restantes = (iterations - iteration) * self.estimated_iteration_time.get()
        if verbal:
            print(f"secondes restantes : {secondes_restantes}")
        end_time = datetime.now() + timedelta(seconds=secondes_restantes)
        self.estimated_end_time.set(end_time.strftime("%H:%M:%S"))

    def update_estimated_iteration_time(self, iteration, temps_ecoule):
        self.estimated_iteration_time.set(temps_ecoule / (iteration + 1))

    def update_compteur_iterations(self, iterations, iteration):
        self.done_iterations.set(f"{iteration + 1}/{iterations}")

    def update_meilleure_solution(self, mink):
        self.meilleure_solution.set(f"{mink} PNJs")

    def save_to_drive(self, verbal=True):
        # # Wait for the thread to finish
        self.planning_thread.join()
        if verbal:
            print("Thread joints")

        # Retrieve the result from the queue
        resultat = self.result_queue.get()
        overlapping = self.overlapping_queue.get()
        if verbal:
            print("résultat lu dans la queue")

        if not resultat:
            messagebox.showerror("Opération impossible",
                                 "Sauver nécessite d'avoir fait tourner le solveur au moins une fois")
        id_folder = self.gn.get_dossier_outputs_drive()
        nom_fichier = f'{datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                      f'- Planning activité par PNJ'
        id_archive = self.gn.get_id_dossier_archive()
        id_sheet = g_io.creer_google_sheet(self.api_drive, nom_fichier, id_folder, id_dossier_archive=id_archive)
        g_io.write_to_sheet(self.api_sheet, resultat, id_sheet)

        formatted_overlapping = module_affectation_pnjs.formatter_overlapping_pour_export(overlapping)
        nom_fichier = f'{datetime.now().strftime("%Y-%m-%d %H:%M")} ' \
                      f'- Détail des évènements se recouvrant par PNJ'
        id_doc = g_io.creer_google_doc(self.api_drive, nom_fichier, id_folder, id_dossier_archive=id_archive)
        g_io.write_to_doc(self.api_doc, id_doc, formatted_overlapping)

        def open_doc_file():
            # Replace with your URL or file path
            url = id_2_doc_address(id_doc)
            webbrowser.open(url)

        def open_sheet_file():
            # Replace with your URL or file path
            url = id_2_sheet_address(id_sheet)
            webbrowser.open(url)

        def close_popup():
            popup.destroy()

        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Sauvegarde réussie")

        # Set the popup window dimensions
        popup.geometry("300x150")

        # Add text to the popup
        message = tk.Label(popup, text="Les fichiers ont bien été créé", pady=20)
        message.pack()

        # Add buttons to the popup
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)

        ok_button = tk.Button(button_frame, text="Ok", command=close_popup, width=15)
        ok_button.grid(row=0, column=0, padx=5)

        open_button = tk.Button(button_frame, text="Ouvrir le fichier planning", command=open_sheet_file, width=15)
        open_button.grid(row=0, column=1, padx=5)

        open_button = tk.Button(button_frame, text="Ouvrir le fichier des recouvrements", command=open_doc_file,
                                width=15)
        open_button.grid(row=0, column=2, padx=5)


def main():
    root = tk.Tk()
    app = MyTkinterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
