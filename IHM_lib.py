from tkinter import ttk

import google_io as g_io


class GidEntry(ttk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, verbal=False, process=True) -> str:
        raw = super().get()
        if verbal:
            print(f"debug : raw = {raw} / mixed = {g_io.extraire_id_google_si_possible(raw)}")
        if process:
            return g_io.extraire_id_google_si_possible(raw)[0]
        else:
            return raw
  # todo : généraliser l'usage de cette classe chaque fois qu'il y a un champ d'entrée qui prend en compte un id/une url
  #  y compris dans les autres ihms !!