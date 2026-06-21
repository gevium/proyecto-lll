import tkinter as tk
from ventanas import mostrar_login
import pygame

#se inicializa la musica
pygame.mixer.init()
pygame.mixer.music.load("musica/musica.mp3")

#funcion para reproudcir la musica
def reproducir_musica():
    pygame.mixer.music.play(-1) 


#Función principal: inicializa todo el programa
def iniciar_programa():

    #Se crea la ventana
    principal = tk.Tk()
    principal.title("Defensa y Asalto de Base")
    principal.geometry("1100x700")
    principal.resizable(False, False)
    principal.configure(background="#94A4B2")

    import ventanas #Se cargan todas las imagenes
    ventanas.cargar_todas_las_imagenes()

    #se comienza a reproducir la musica
    reproducir_musica()

    mostrar_login(principal)
    principal.mainloop()

iniciar_programa()
