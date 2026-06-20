import tkinter as tk
from ventanas import mostrar_login


#Función principal: inicializa todo el programa
def iniciar_programa():

    #Se crea la ventana
    principal = tk.Tk()
    principal.title("Defensa y Asalto de Base")
    principal.geometry("1100x700")
    principal.resizable(False, False)
    principal.configure(background="#94A4B2")

    import ventanas #Se cargaj todas las imagenes
    ventanas.cargar_todas_las_imagenes()

    mostrar_login(principal)
    principal.mainloop()

iniciar_programa()