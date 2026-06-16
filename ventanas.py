import tkinter as tk
from tkinter import messagebox
from clases import Jugadores_Json

gestor = Jugadores_Json()

#Elimina cualquier widget de la ventana llamada
def limpiar_pantalla(root):
    for widget in root.winfo_children():
        widget.destroy()

def registrar(entry_user, entry_contra):
    usuario = entry_user.get().strip()
    contraseña = entry_contra.get().strip()

    if not usuario or not contraseña:
        messagebox.showwarning("Aviso", "Los campos se encuentran vacíos.")
        return
    
    confirmacion, mensaje = gestor.registrar(usuario, contraseña)

    if confirmacion:
        messagebox.showinfo("Registro", mensaje)
    else:
        messagebox.showwarning("ERROR", mensaje)


def iniciar_sesion(root, entry_user, entry_contra):
    usuario = entry_user.get().strip()
    contraseña = entry_contra.get().strip()

    if not usuario or not contraseña:
        messagebox.showwarning("Aviso","Los campos se encuentran vacíos.")
        return
    
    confirmacion, jugador = gestor.iniciar_sesion(usuario, contraseña)

    if confirmacion:
        messagebox.showinfo("Inicio", "Realizado con éxito")
        mostrar_mapa(root, jugador)
    else:
        messagebox.showwarning("ERROR", "Algo ocurrió mal")

def mostrar_login(root):
    limpiar_pantalla(root)

    tk.Label(root, text= "Bienvenido a: Defensa y Asalto de Base").pack(pady=10, anchor="w")

    tk.Label(root, text= "Escriba el nombre de usuario:").pack(pady=10, anchor="w")
    entry_user = tk.Entry(root)
    entry_user.pack(pady =5, anchor= "w")

    tk.Label(root, text= "Escriba su contraseña:").pack(pady=10, anchor="w")
    entry_contra = tk.Entry(root)
    entry_contra.pack(pady =5, anchor= "w")

    tk.Button(root, text = "Iniciar sesión", command=lambda: iniciar_sesion(root,entry_user, entry_contra), width=20).pack(pady=10)
    tk.Button(root, text = "Registrarse", command=lambda: registrar(root, entry_user, entry_contra), width=20).pack(pady=10)

def mostrar_mapa(root, jugador):
    limpiar_pantalla(root)
    
    TAMANO_CASILLA = 50  
    FILAS = 11
    COLUMNAS = 11

    seleccion_actual = None  # puede ser "basica", "pesada", "magica", "muro"
    
    canvas = tk.Canvas(root, width=COLUMNAS * TAMANO_CASILLA, height=FILAS * TAMANO_CASILLA)
    canvas.pack()

    canvas.bind("<Button-1>", lambda event: colocar_en_mapa(event, canvas))

    tk.Button(panel_izq, text="Torre Basica - $50", 
          command=lambda: cambiar_seleccion("basica"))
    
    #dibujar cada casilla
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            x1 = columna * TAMANO_CASILLA
            y1 = fila * TAMANO_CASILLA
            x2 = x1 + TAMANO_CASILLA
            y2 = y1 + TAMANO_CASILLA
            canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="black")
    
    # dibujar la base central en (5, 5)
    fila_base = 5
    columna_base = 5
    x1 = columna_base * TAMANO_CASILLA
    y1 = fila_base * TAMANO_CASILLA
    x2 = x1 + TAMANO_CASILLA
    y2 = y1 + TAMANO_CASILLA
    canvas.create_rectangle(x1, y1, x2, y2, fill="gold", outline="black")
    canvas.create_text(x1 + 25, y1 + 25, text="BASE", font=("Arial", 7, "bold"))
