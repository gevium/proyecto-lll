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
    tk.Button(root, text = "Registrarse", command=lambda: registrar(entry_user, entry_contra), width=20).pack(pady=10)
    
    def ir_a_top():
        mostrar_top_jugadores(root)
    tk.Button(root, text="Top Jugadores", command=ir_a_top, width=20).pack(pady=10)

def mostrar_mapa(root, jugador):
    limpiar_pantalla(root)
    
    TAMANO_CASILLA = 50  
    FILAS = 11
    COLUMNAS = 11

    seleccion_actual = [None] 
    
    frame_principal = tk.Frame(root)
    frame_principal.pack(fill="both", expand=True)

    panel_izq = tk.Frame(frame_principal, width=150, bg="lightgray")
    panel_izq.pack(side="left", fill="y")

    panel_centro = tk.Frame(frame_principal)
    panel_centro.pack(side="left")

    panel_der = tk.Frame(frame_principal, width=150, bg="lightgray")
    panel_der.pack(side="left", fill="y")

    canvas = tk.Canvas(panel_centro, width=COLUMNAS * TAMANO_CASILLA, height=FILAS * TAMANO_CASILLA)
    canvas.pack()

    # funciones internas
    def cambiar_seleccion(tipo):
        seleccion_actual[0] = tipo

    def colocar_en_mapa(event):
        if seleccion_actual[0] is None:
            return
        columna = event.x // TAMANO_CASILLA
        fila = event.y // TAMANO_CASILLA
        # por ahora solo pinta la casilla
        x1 = columna * TAMANO_CASILLA
        y1 = fila * TAMANO_CASILLA
        x2 = x1 + TAMANO_CASILLA
        y2 = y1 + TAMANO_CASILLA
        canvas.create_rectangle(x1, y1, x2, y2, fill="brown", outline="black")


    canvas.bind("<Button-1>", colocar_en_mapa)
    
    #dibujar cada casilla
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            x1 = columna * TAMANO_CASILLA
            y1 = fila * TAMANO_CASILLA
            x2 = x1 + TAMANO_CASILLA
            y2 = y1 + TAMANO_CASILLA
            canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="black")
    
    # botones en panel_izq
    tk.Label(panel_izq, text="Torres:", bg="lightgray").pack(pady=5)
    tk.Button(panel_izq, text="Basica - $50", command=lambda: cambiar_seleccion("basica")).pack(pady=3)
    tk.Button(panel_izq, text="Pesada - $120", command=lambda: cambiar_seleccion("pesada")).pack(pady=3)
    tk.Button(panel_izq, text="Magica - $90", command=lambda: cambiar_seleccion("magica")).pack(pady=3)
    tk.Label(panel_izq, text="Muros:", bg="lightgray").pack(pady=5)
    tk.Button(panel_izq, text="Muro - $20", command=lambda: cambiar_seleccion("muro")).pack(pady=3)

    # dibujar la base central en (5, 5)
    fila_base = 5
    columna_base = 5
    x1 = columna_base * TAMANO_CASILLA
    y1 = fila_base * TAMANO_CASILLA
    x2 = x1 + TAMANO_CASILLA
    y2 = y1 + TAMANO_CASILLA
    canvas.create_rectangle(x1, y1, x2, y2, fill="gold", outline="black")
    canvas.create_text(x1 + 25, y1 + 25, text="BASE", font=("Arial", 7, "bold"))

def mostrar_top_jugadores(root):
    limpiar_pantalla(root)
    
    tk.Label(root, text="Top Jugadores", font=("Arial", 16, "bold")).pack(pady=10)
    
    ##### Top defensores #####
    tk.Label(root, text="Top 5 Defensores", font=("Arial", 12, "bold")).pack(pady=5)
    top_defensores = gestor.obtener_top_defensores()
    
    if not top_defensores:
        tk.Label(root, text="Sin jugadores registrados").pack()
    else:
        for i, jugador in enumerate(top_defensores, start=1):
            texto = f"{i}. {jugador.nombre_usuario} - {jugador.victorias_defensor} victorias"
            tk.Label(root, text=texto, font=("Arial", 10)).pack(anchor="w", padx=40)
    tk.Label(root, text="").pack()
    
    ##### Top atacantes #####
    tk.Label(root, text="Top 5 Atacantes", font=("Arial", 16, "bold")).pack(pady=5)
    top_atacantes = gestor.obtener_top_atacantes()
    
    if not top_atacantes:
        tk.Label(root, text="Sin jugadores registrados").pack()
    else:
        for i, jugador in enumerate(top_atacantes, start=1):
            texto = f"{i}. {jugador.nombre_usuario} - {jugador.victorias_atacante} victorias"
            tk.Label(root, text=texto, font=("Arial", 10)).pack(anchor="w", padx=40)
    tk.Label(root, text="").pack()
    
    def volver():
        mostrar_login(root)
        
    tk.Button(root, text="Volver", command=volver, width=20).pack(pady=10)