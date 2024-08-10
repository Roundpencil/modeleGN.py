import tkinter as tk
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

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
