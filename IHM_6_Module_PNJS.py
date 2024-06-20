import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from datetime import datetime, timedelta
import threading

from modeleGN import GN
from module_affectation_pnjs import creer_planning


class MyTkinterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("My Tkinter GUI")
        self.root.geometry("600x500")

        self.file_label = tk.Label(self.root, text="")
        self.test_status = tk.StringVar(value="Non testé")
        self.estimated_iteration_time = tk.DoubleVar(value=0)
        self.estimated_total_time = tk.StringVar(value="")
        self.estimated_end_time = tk.StringVar(value="")

        self.gn = None

        self.create_widgets()

    def create_widgets(self):
        tk.Button(self.root, text="Charger fichier MGN", command=self.charger_fichier_mgn).grid(row=10, column=0,
                                                                                                padx=5, pady=10,
                                                                                                sticky="e")
        self.file_label.grid(row=10, column=1, columnspan=2, pady=10, sticky="w")

        tk.Button(self.root, text="Tester fichier", command=self.tester_fichier).grid(row=20, column=0, padx=5, pady=10,
                                                                                      sticky="e")
        tk.Label(self.root, textvariable=self.test_status).grid(row=20, column=1, padx=5, pady=10, sticky="w")
        tk.Label(self.root, text="Temps itération estimé (pas de 15 mn) :") \
            .grid(row=20, column=2, padx=5, pady=10, sticky="e")
        tk.Label(self.root, textvariable=self.estimated_iteration_time).grid(row=20, column=3, padx=5, pady=10,
                                                                             sticky="w")

        tk.Label(self.root, text="Nombre d'itérations:").grid(row=30, column=0, padx=5, pady=5, sticky="e")
        self.iterations_entry = tk.Entry(self.root)
        self.iterations_entry.grid(row=30, column=1, padx=5, pady=5, sticky="w")
        self.iterations_entry.bind("<KeyRelease>", self.update_estimated_total_time)

        tk.Label(self.root, text="Durée d'un pas (en mn) :").grid(row=35, column=0, padx=5, pady=5, sticky="e")
        self.pas_entry = tk.Entry(self.root)
        self.pas_entry.grid(row=35, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.root, text="Temps estimé (pas de 15 mn) :").grid(row=30, column=2, padx=5, pady=10, sticky="e")
        tk.Label(self.root, textvariable=self.estimated_total_time).grid(row=30, column=3, padx=5, pady=10, sticky="w")

        tk.Button(self.root, text="Go", command=self.start_process).grid(row=40, column=0, columnspan=1, pady=10)

        self.progress_bar = Progressbar(self.root, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.grid(row=40, column=1, columnspan=3, pady=10)

        tk.Label(self.root, text="Heure de fin estimée:").grid(row=60, column=0, padx=5, pady=10, sticky="e")
        tk.Label(self.root, textvariable=self.estimated_end_time).grid(row=60, column=1, columnspan=3, pady=10,
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

            # Create a thread to run the creer_planning function
            planning_thread = threading.Thread(target=creer_planning,
                                               args=(self.gn, iterations, pas,
                                                     lambda x, y: self.observateur(iterations, x, y)))

            planning_thread.start()
        except ValueError as e:
            messagebox.showerror("Une erreur est survenue", str(e))
            #todo : meilleur handling des erreurs, à commencer par les cas ou il n'y a pas de nombre

    def update_progress_bar(self, iteration):
        self.progress_bar["value"] = iteration

    def observateur(self, iterations, iteration, temps_ecoule):
        # mettre à jour la barre de progression
        self.update_progress_bar(iteration)

        # mettre à jour le temps moyen par itération
        self.update_estimated_iteration_time(iterations, iteration, temps_ecoule)

        # mettre à jour le compteur de temps
        self.update_heure_fin(iterations, iteration, temps_ecoule)

    def update_heure_fin(self, iterations, iteration, temps_ecoule):
        secondes_restantes = (iterations - iteration) * self.estimated_iteration_time
        end_time = datetime.now() + timedelta(seconds=secondes_restantes)
        self.estimated_end_time.set(end_time.strftime("%H:%M:%S"))

    def update_estimated_iteration_time(self, iterations, iteration, temps_ecoule):
        self.estimated_iteration_time.set(temps_ecoule/iteration)


def main():
    root = tk.Tk()
    app = MyTkinterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
