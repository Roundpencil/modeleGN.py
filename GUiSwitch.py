import tkinter as tk
from tkinter import ttk


class FirstWindow(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        ttk.Label(self, text="Première fenêtre").pack(padx=20, pady=20)


class SecondWindow(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        ttk.Label(self, text="Deuxième fenêtre").pack(padx=20, pady=20)


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("300x150")
        self.title("Application principale")

        menu = tk.Menu(self)
        self.config(menu=menu)

        view_menu = tk.Menu(menu)
        menu.add_cascade(label="Vues", menu=view_menu)
        view_menu.add_command(label="Première fenêtre", command=self.show_first_window)
        view_menu.add_command(label="Deuxième fenêtre", command=self.show_second_window)

        self.first_window = FirstWindow(self)
        self.second_window = SecondWindow(self)

        self.current_window = None

    def show_first_window(self):
        self.change_window(self.first_window)

    def show_second_window(self):
        self.change_window(self.second_window)

    def change_window(self, new_window):
        if self.current_window:
            self.current_window.pack_forget()

        new_window.pack(fill=tk.BOTH, expand=True)
        self.current_window = new_window


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
