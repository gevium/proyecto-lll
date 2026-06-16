import tkinter as tk
from ventanas import mostrar_login

def iniciar_programa():
    principal = tk.Tk()
    principal.title("Defensa y Asalto de Base")
    principal.geometry("500x400")

    mostrar_login(principal)

    principal.mainloop()

iniciar_programa()