import tkinter as tk
from tkinter import messagebox
from clases import Jugadores_Json, Torre, Muro, TORRES, FACCIONES
from combate import EstadoJuego

gestor = Jugadores_Json()
sesion_actual = {"jugador1": None, "jugador2": None}

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

    """
    if confirmacion:
        messagebox.showinfo("Inicio", "Realizado con éxito")
        mostrar_mapa(root, jugador)
    else:
        messagebox.showwarning("ERROR", "Algo ocurrió mal")
    """
    
    if not confirmacion:
        messagebox.showwarning("ERROR", "Algo ocurrió mal")
        return
    
    if sesion_actual["jugador1"] is None:
        sesion_actual["jugador1"] = jugador
        messagebox.showinfo("Jugador 1", f"Bienvenido {jugador.nombre_usuario}.\nAhora inicie sesión el jugador 2.")
        entry_user.delete(0, tk.END)
        entry_contra.delete(0, tk.END)

    elif sesion_actual["jugador2"] is None:
        if jugador.nombre_usuario == sesion_actual["jugador1"].nombre_usuario:
            messagebox.showwarning("Aviso", "El jugador 2 debe ser una cuenta diferente.")
            return
        sesion_actual["jugador2"] = jugador
        mostrar_seleccion_faccion(root, sesion_actual["jugador1"], sesion_actual["jugador2"])

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

def mostrar_mapa(root, jugador1, jugador2, faccion_defensor, faccion_atacante):
    limpiar_pantalla(root)
    
    TAMANO_CASILLA = 50  
    FILAS = 11
    COLUMNAS = 11

    estado = EstadoJuego(jugador1, jugador2)

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

        if (fila, columna) == (5, 5):
            return
        if estado.mapa[fila][columna] is not None:
            return

        tipo = seleccion_actual[0]
        if tipo == "muro":
            entidad = Muro(20)
            estado.muros.append(entidad)
        else:
            datos = TORRES[tipo]
            entidad = Torre(datos["nombre"], datos["costo"], datos["vida"],
                            datos["daño"], datos["alcance"], datos["habilidad"],
                            datos["turnos_habilidad"])
            estado.torres.append(entidad)

        entidad.posicion = (fila, columna)
        estado.mapa[fila][columna] = entidad
        estado.dinero_defensor -= entidad.costo

        x1 = columna * TAMANO_CASILLA
        y1 = fila * TAMANO_CASILLA
        x2 = x1 + TAMANO_CASILLA
        y2 = y1 + TAMANO_CASILLA
        
        color = FACCIONES[faccion_defensor]["color_muro"] if tipo == "muro" else FACCIONES[faccion_defensor]["color_torre"]
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
        label_dinero.config(text=f"Dinero: ${estado.dinero_defensor}")


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
    label_dinero = tk.Label(panel_izq, text=f"Dinero: ${estado.dinero_defensor}", bg="lightgray", font=("Arial", 10, "bold"))
    label_dinero.pack(pady=5)
    tk.Label(panel_izq, text="Torres:", bg="lightgray").pack(pady=5)
    tk.Button(panel_izq, text="Basica - $50", command=lambda: cambiar_seleccion("basica")).pack(pady=3)
    tk.Button(panel_izq, text="Pesada - $120", command=lambda: cambiar_seleccion("pesada")).pack(pady=3)
    tk.Button(panel_izq, text="Magica - $90", command=lambda: cambiar_seleccion("magica")).pack(pady=3)
    tk.Label(panel_izq, text="Muros:", bg="lightgray").pack(pady=5)
    tk.Button(panel_izq, text="Muro - $20", command=lambda: cambiar_seleccion("muro")).pack(pady=3)
    
    def ir_a_fase_atacante():
        mostrar_fase_atacante(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado)

    tk.Button(panel_izq, text="Listo", command=ir_a_fase_atacante, bg="lightgreen", width=15).pack(pady=15)

    # dibujar la base central en (5, 5)
    fila_base = 5
    columna_base = 5
    x1 = columna_base * TAMANO_CASILLA
    y1 = fila_base * TAMANO_CASILLA
    x2 = x1 + TAMANO_CASILLA
    y2 = y1 + TAMANO_CASILLA
    canvas.create_rectangle(x1, y1, x2, y2, fill="gold", outline="black")
    canvas.create_text(x1 + 25, y1 + 25, text="BASE", font=("Arial", 7, "bold"))
    #label_dinero.config(text=f"Dinero: ${estado.dinero_defensor}")

def mostrar_seleccion_faccion(root, jugador1, jugador2):
    limpiar_pantalla(root)
    
    faccion_j1 = {"valor": None}
    faccion_j2 = {"valor": None}
    
    tk.Label(root, text="Selección de facción", font=("Arial", 16, "bold")).pack(pady=10)
    
    frame_columnas = tk.Frame(root)
    frame_columnas.pack(pady=10)
    
    #################################
    # Columna Jugador 1 - Defensor  #
    #################################
    
    frame_j1 = tk.Frame(frame_columnas, bd=2, relief="groove", padx=10, pady=10)
    frame_j1.grid(row=0, column=0, padx=20)

    tk.Label(frame_j1, text=jugador1.nombre_usuario, font=("Arial", 11, "bold")).pack()
    tk.Label(frame_j1, text="(Defensor)", font=("Arial", 9, "italic")).pack(pady=2)

    label_seleccion_j1 = tk.Label(frame_j1, text="Sin selección", fg="gray")
    label_seleccion_j1.pack(pady=5)

    label_aviso = tk.Label(root, text="", fg="red")
    label_aviso.pack(pady=5)

    btn_continuar = tk.Button(root, text="Continuar", width=20, state="disabled")
    btn_continuar.pack(pady=10)
    
    def verificar_selecciones():
        if faccion_j1["valor"] is None or faccion_j2["valor"] is None:
            return
        if faccion_j1["valor"] == faccion_j2["valor"]:
            label_aviso.config(text="Las facciones deben ser diferentes.")
            btn_continuar.config(state="disabled")
            return
        label_aviso.config(text="")
        btn_continuar.config(state="normal")
        
    def elegir_j1(clave):
        faccion_j1["valor"] = clave
        nombre = FACCIONES[clave]["nombre"]
        color = FACCIONES[clave]["color_torre"]
        label_seleccion_j1.config(text=f"✔ {nombre}", fg=color)
        verificar_selecciones()
    
    for clave, datos in FACCIONES.items():
        def hacer_elegir_j1(c=clave):
            elegir_j1(c)
        tk.Button(frame_j1, text=datos["nombre"],
                 bg=datos["color_torre"], width=15,
                 command=hacer_elegir_j1).pack(pady=3)
    
    #################################
    # Columna Jugador 2 - Atacante  #
    #################################
    frame_j2 = tk.Frame(frame_columnas, bd=2, relief="groove", padx=10, pady=10)
    frame_j2.grid(row=0, column=1, padx=20)

    tk.Label(frame_j2, text=jugador2.nombre_usuario, font=("Arial", 11, "bold")).pack()
    tk.Label(frame_j2, text="(Atacante)", font=("Arial", 9, "italic")).pack(pady=2)

    label_seleccion_j2 = tk.Label(frame_j2, text="Sin selección", fg="gray")
    label_seleccion_j2.pack(pady=5)
    
    def elegir_j2(clave):
        faccion_j2["valor"] = clave
        nombre = FACCIONES[clave]["nombre"]
        color = FACCIONES[clave]["color_torre"]
        label_seleccion_j2.config(text=f"✔ {nombre}", fg=color)
        verificar_selecciones()
        
    for clave, datos in FACCIONES.items():
        def hacer_elegir_j2(c=clave):
            elegir_j2(c)
        tk.Button(frame_j2, text=datos["nombre"],
                  bg=datos["color_torre"], width=15,
                  command=hacer_elegir_j2).pack(pady=3)
    
    ####### Command del botón continuar #######
    def continuar():
        sesion_actual["jugador1"] = None  # resetear para la próxima partida
        sesion_actual["jugador2"] = None
        mostrar_mapa(root, jugador1, jugador2, faccion_j1["valor"], faccion_j2["valor"])

    btn_continuar.config(command=continuar)

        

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