import tkinter as tk
from tkinter import messagebox
from clases import Jugadores_Json, Torre, Muro, Unidad, TORRES, UNIDADES, FACCIONES
from combate import EstadoJuego, ejecutar_combate

gestor = Jugadores_Json()
sesion_actual = {"jugador1": None, "jugador2": None}

# Paleta de colores general
COLOR_FONDO = "#F0F4F8"
COLOR_PANEL = "#D9E2EC"
COLOR_BOTON = "#4A90D9"
COLOR_BOTON_TEXTO = "white"
COLOR_TITULO = "#1A2E4A"
FUENTE_TITULO = ("Georgia", 16, "bold")
FUENTE_NORMAL = ("Arial", 10)
FUENTE_BOTON = ("Arial", 10, "bold")

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


def iniciar_sesion(root, entry_user, entry_contra, label_estado, btn_comenzar):
    usuario = entry_user.get().strip()
    contraseña = entry_contra.get().strip()

    if not usuario or not contraseña:
        messagebox.showwarning("Aviso", "Los campos se encuentran vacíos.")
        return

    if sesion_actual["jugador1"] is not None and sesion_actual["jugador2"] is not None:
        messagebox.showwarning("Aviso", "Ya hay dos jugadores listos. Presioná Comenzar.")
        return

    confirmacion, jugador = gestor.iniciar_sesion(usuario, contraseña)
    if not confirmacion:
        messagebox.showwarning("ERROR", "Usuario o contraseña incorrectos.")
        return

    if sesion_actual["jugador1"] is None:
        sesion_actual["jugador1"] = jugador
        label_estado.config(text=f"✔ {jugador.nombre_usuario} listo. Esperando jugador 2...", fg="green")
        entry_user.delete(0, tk.END)
        entry_contra.delete(0, tk.END)

    elif sesion_actual["jugador2"] is None:
        if jugador.nombre_usuario == sesion_actual["jugador1"].nombre_usuario:
            messagebox.showwarning("Aviso", "El jugador 2 debe ser una cuenta diferente.")
            return
        sesion_actual["jugador2"] = jugador
        label_estado.config(text=f"✔ {jugador.nombre_usuario} listo. ¡Listos para comenzar!", fg="blue")
        btn_comenzar.config(state="normal")
        entry_user.delete(0, tk.END)
        entry_contra.delete(0, tk.END)

def mostrar_login(root):
    limpiar_pantalla(root)
    sesion_actual["jugador1"] = None
    sesion_actual["jugador2"] = None

    root.configure(bg=COLOR_FONDO)

    tk.Label(root, text="⚔ Defensa y Asalto de Base", font=FUENTE_TITULO,
             bg=COLOR_FONDO, fg=COLOR_TITULO).pack(pady=30)

    frame = tk.Frame(root, bg=COLOR_PANEL, padx=30, pady=30)
    frame.pack(pady=10)

    tk.Label(frame, text="Usuario:", font=FUENTE_NORMAL, bg=COLOR_PANEL).pack(anchor="w")
    entry_user = tk.Entry(frame, font=FUENTE_NORMAL, width=25)
    entry_user.pack(pady=5)

    tk.Label(frame, text="Contraseña:", font=FUENTE_NORMAL, bg=COLOR_PANEL).pack(anchor="w", pady=(10,0))
    entry_contra = tk.Entry(frame, font=FUENTE_NORMAL, width=25, show="*")
    entry_contra.pack(pady=5)

    tk.Button(frame, text="Iniciar sesión", font=FUENTE_BOTON,
          bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=20,
          command=lambda: iniciar_sesion(root, entry_user, entry_contra, label_estado, btn_comenzar)).pack(pady=(15,5))
    tk.Button(frame, text="Registrarse", font=FUENTE_BOTON,
              bg=COLOR_PANEL, width=20,
              command=lambda: registrar(entry_user, entry_contra)).pack(pady=5)
    
    label_estado = tk.Label(frame, text="Esperando jugador 1...",
                            font=FUENTE_NORMAL, bg=COLOR_PANEL, fg="gray")
    label_estado.pack(pady=5)

    btn_comenzar = tk.Button(frame, text="⚔ Comenzar partida", font=FUENTE_BOTON,
                            bg="green", fg="white", width=20, state="disabled",
                            command=lambda: mostrar_seleccion_faccion(root, sesion_actual["jugador1"], sesion_actual["jugador2"]))
    btn_comenzar.pack(pady=5)

    tk.Button(frame, text="Top Jugadores", font=FUENTE_BOTON,
              bg=COLOR_PANEL, width=20,
              command=lambda: mostrar_top_jugadores(root)).pack(pady=5)

def redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA,estado,faccion_defensor,  faccion_atacante=None):
    canvas.delete("all")
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            x1 = columna * TAMANO_CASILLA
            y1 = fila * TAMANO_CASILLA
            x2 = x1 + TAMANO_CASILLA
            y2 = y1 + TAMANO_CASILLA
            entidad = estado.mapa[fila][columna]
            if entidad is None:
                canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="black")
            elif entidad.tipo == "base":
                canvas.create_rectangle(x1, y1, x2, y2, fill="gold", outline="black")
                canvas.create_text(x1 + 25, y1 + 25, text="BASE", font=("Arial", 7, "bold"))
            elif entidad.tipo == "torre":
                canvas.create_rectangle(x1, y1, x2, y2, fill=FACCIONES[faccion_defensor]["color_torre"], outline="black")
            elif entidad.tipo == "muro":
                canvas.create_rectangle(x1, y1, x2, y2, fill=FACCIONES[faccion_defensor]["color_muro"], outline="black")
            elif entidad.tipo == "unidad":  # ← agregar esto
                canvas.create_rectangle(x1, y1, x2, y2, fill=FACCIONES[faccion_atacante]["color_unidad"], outline="black")


def mostrar_mapa(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado=None):
    limpiar_pantalla(root)
    
    TAMANO_CASILLA = 50  
    FILAS = 11
    COLUMNAS = 11

    if estado is None:
        estado = EstadoJuego(jugador1, jugador2)

    seleccion_actual = [None] 
    def ir_a_fase_atacante():
        mostrar_fase_atacante(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado)
    
    frame_principal = tk.Frame(root)
    frame_principal.pack(fill="both", expand=True)

    panel_izq = tk.Frame(frame_principal, width=200, bg="lightgray")
    panel_izq.pack(side="left", fill="y")
    panel_izq.pack_propagate(False)

    panel_centro = tk.Frame(frame_principal)
    panel_centro.pack(side="left")

    panel_izq.configure(bg=COLOR_PANEL)

    tk.Label(panel_izq, text=jugador1.nombre_usuario, font=("Arial", 11, "bold"),
            bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=(15,0))
    tk.Label(panel_izq, text="(Defensor)", font=("Arial", 9, "italic"),
            bg=COLOR_PANEL, fg="gray").pack()

    label_dinero = tk.Label(panel_izq, text=f"💰 ${estado.dinero_defensor}",
                            font=FUENTE_BOTON, bg=COLOR_PANEL, fg=COLOR_TITULO)
    label_dinero.pack(pady=10)

    tk.Label(panel_izq, text="Ronda", font=FUENTE_BOTON,
         bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=(15,2))
    label_ronda = tk.Label(panel_izq, text=f"{estado.ronda_actual}",
                       font=("Arial", 14, "bold"), bg=COLOR_PANEL, fg=COLOR_TITULO)
    label_ronda.pack()

    tk.Label(panel_izq, text="Torres", font=FUENTE_BOTON,
            bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=(10,2))
    tk.Button(panel_izq, text="Básica - $50", font=FUENTE_NORMAL,
            bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=15,
            command=lambda: cambiar_seleccion("basica")).pack(pady=3)
    tk.Button(panel_izq, text="Pesada - $120", font=FUENTE_NORMAL,
            bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=15,
            command=lambda: cambiar_seleccion("pesada")).pack(pady=3)
    tk.Button(panel_izq, text="Mágica - $90", font=FUENTE_NORMAL,
            bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=15,
            command=lambda: cambiar_seleccion("magica")).pack(pady=3)

    tk.Label(panel_izq, text="Muros", font=FUENTE_BOTON,
            bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=(10,2))
    tk.Button(panel_izq, text="Muro - $20", font=FUENTE_NORMAL,
            bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=15,
            command=lambda: cambiar_seleccion("muro")).pack(pady=3)

    tk.Button(panel_izq, text="✔ Listo", font=FUENTE_BOTON,
            bg="green", fg="white", width=15,
            command=ir_a_fase_atacante).pack(pady=20)
    
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
        else:
            datos = TORRES[tipo]
            entidad = Torre(datos["nombre"], datos["costo"], datos["vida"],
                            datos["daño"], datos["alcance"], datos["habilidad"],
                            datos["turnos_habilidad"])

        if estado.dinero_defensor < entidad.costo:
            messagebox.showwarning("Sin dinero", "No tienes suficiente dinero.")
            return

        if tipo == "muro":
            estado.muros.append(entidad)
        else:
            estado.torres.append(entidad)

        entidad.posicion = (fila, columna)
        estado.mapa[fila][columna] = entidad
        estado.dinero_defensor -= entidad.costo
        label_dinero.config(text=f"Dinero: ${estado.dinero_defensor}")
        redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA, estado, faccion_defensor, faccion_atacante)


    canvas.bind("<Button-1>", colocar_en_mapa)

    redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA, estado, faccion_defensor, faccion_atacante)
def mostrar_seleccion_faccion(root, jugador1, jugador2):
    limpiar_pantalla(root)
    root.configure(bg=COLOR_FONDO)

    faccion_j1 = {"valor": None}
    faccion_j2 = {"valor": None}

    tk.Label(root, text="Selección de Facción", font=FUENTE_TITULO,
             bg=COLOR_FONDO, fg=COLOR_TITULO).pack(pady=20)

    frame_columnas = tk.Frame(root, bg=COLOR_FONDO)
    frame_columnas.pack(pady=10)

    frame_j1 = tk.Frame(frame_columnas, bg=COLOR_PANEL, bd=2, relief="groove", padx=15, pady=15)
    frame_j1.grid(row=0, column=0, padx=20)

    tk.Label(frame_j1, text=jugador1.nombre_usuario, font=("Arial", 11, "bold"),
             bg=COLOR_PANEL, fg=COLOR_TITULO).pack()
    tk.Label(frame_j1, text="(Defensor)", font=("Arial", 9, "italic"),
             bg=COLOR_PANEL, fg="gray").pack(pady=2)
    label_seleccion_j1 = tk.Label(frame_j1, text="Sin selección",
                                   font=FUENTE_NORMAL, bg=COLOR_PANEL, fg="gray")
    label_seleccion_j1.pack(pady=5)

    frame_j2 = tk.Frame(frame_columnas, bg=COLOR_PANEL, bd=2, relief="groove", padx=15, pady=15)
    frame_j2.grid(row=0, column=1, padx=20)

    tk.Label(frame_j2, text=jugador2.nombre_usuario, font=("Arial", 11, "bold"),
             bg=COLOR_PANEL, fg=COLOR_TITULO).pack()
    tk.Label(frame_j2, text="(Atacante)", font=("Arial", 9, "italic"),
             bg=COLOR_PANEL, fg="gray").pack(pady=2)
    label_seleccion_j2 = tk.Label(frame_j2, text="Sin selección",
                                   font=FUENTE_NORMAL, bg=COLOR_PANEL, fg="gray")
    label_seleccion_j2.pack(pady=5)

    label_aviso = tk.Label(root, text="", fg="red", bg=COLOR_FONDO, font=FUENTE_NORMAL)
    label_aviso.pack(pady=5)

    btn_continuar = tk.Button(root, text="⚔ Comenzar partida", font=FUENTE_BOTON,
                               bg="green", fg="white", width=20, state="disabled")
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
        tk.Button(frame_j1, text=datos["nombre"], font=FUENTE_NORMAL,
                  bg=datos["color_torre"], fg="white", width=15,
                  command=hacer_elegir_j1).pack(pady=3)

    def elegir_j2(clave):
        faccion_j2["valor"] = clave
        nombre = FACCIONES[clave]["nombre"]
        color = FACCIONES[clave]["color_torre"]
        label_seleccion_j2.config(text=f"✔ {nombre}", fg=color)
        verificar_selecciones()

    for clave, datos in FACCIONES.items():
        def hacer_elegir_j2(c=clave):
            elegir_j2(c)
        tk.Button(frame_j2, text=datos["nombre"], font=FUENTE_NORMAL,
                  bg=datos["color_torre"], fg="white", width=15,
                  command=hacer_elegir_j2).pack(pady=3)

    def continuar():
        sesion_actual["jugador1"] = None
        sesion_actual["jugador2"] = None
        mostrar_mapa(root, jugador1, jugador2, faccion_j1["valor"], faccion_j2["valor"])

    btn_continuar.config(command=continuar)

def mostrar_fase_atacante(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado):
    limpiar_pantalla(root)

    TAMANO_CASILLA = 50
    FILAS = 11
    COLUMNAS = 11

    seleccion_actual = [None]

    frame_principal = tk.Frame(root)
    frame_principal.pack(fill="both", expand=True)

    panel_izq = tk.Frame(frame_principal, width=200, bg=COLOR_PANEL)
    panel_izq.pack(side="left", fill="y")
    panel_izq.pack_propagate(False)

    panel_centro = tk.Frame(frame_principal)
    panel_centro.pack(side="left")

    canvas = tk.Canvas(panel_centro, width=COLUMNAS * TAMANO_CASILLA, height=FILAS * TAMANO_CASILLA)
    canvas.pack()
    
    #### Funciones internas ####
    def cambiar_seleccion(tipo):
        seleccion_actual[0] = tipo

    def colocar_unidad(event):
        if seleccion_actual[0] is None:
            return

        columna = event.x // TAMANO_CASILLA
        fila = event.y // TAMANO_CASILLA

        en_borde = (columna == 0 or columna == 10 or fila == 0 or fila == 10)
        if not en_borde:
            messagebox.showwarning("Aviso", "Solo puedes colocar unidades en los bordes del mapa.")
            return

        if estado.mapa[fila][columna] is not None:
            messagebox.showwarning("Aviso", "Esa casilla ya está ocupada.")
            return

        datos = UNIDADES[seleccion_actual[0]]

        if estado.dinero_atacante < datos["costo"]:
            messagebox.showwarning("Sin dinero", "No tienes suficiente dinero.")
            return

        unidad = Unidad(datos["nombre"], datos["costo"], datos["vida"],
                        datos["daño"], datos["velocidad"], datos["habilidad"],
                        datos["turnos_habilidad"])
        unidad.posicion = (fila, columna)
        estado.unidades.append(unidad)
        estado.mapa[fila][columna] = unidad
        estado.dinero_atacante -= datos["costo"]

        label_dinero.config(text=f"Dinero: ${estado.dinero_atacante}")
        redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA, estado, faccion_defensor, faccion_atacante)
    canvas.bind("<Button-1>", colocar_unidad)
    
    tk.Label(panel_izq, text=jugador2.nombre_usuario, font=("Arial", 11, "bold"),
            bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=(15,0))
    tk.Label(panel_izq, text="(Atacante)", font=("Arial", 9, "italic"),
            bg=COLOR_PANEL, fg="gray").pack()

    label_dinero = tk.Label(panel_izq, text=f"💰 ${estado.dinero_atacante}",
                            font=FUENTE_BOTON, bg=COLOR_PANEL, fg=COLOR_TITULO)
    label_dinero.pack(pady=10)

    tk.Label(panel_izq, text="Ronda", font=FUENTE_BOTON,
            bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=(5,2))
    tk.Label(panel_izq, text=f"{estado.ronda_actual}", font=("Arial", 14, "bold"),
            bg=COLOR_PANEL, fg=COLOR_TITULO).pack()

    tk.Label(panel_izq, text="Unidades", font=FUENTE_BOTON,
            bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=(10,2))

    def iniciar_combate():
        if not estado.unidades:
            messagebox.showwarning("Aviso", "Debes colocar al menos una unidad.")
            return
        def actualizar_ui():
            redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA, estado, faccion_defensor, faccion_atacante)            
            root.update()
            root.after(300)  # 300ms entre cada turno, podés ajustarlo
        ganador = ejecutar_combate(estado, actualizar_ui)
        mostrar_resultado_ronda(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado, ganador)

    for clave, datos in UNIDADES.items():
        def hacer_seleccion(c=clave):
            cambiar_seleccion(c)
        tk.Button(panel_izq, text=f"{datos['nombre']} - ${datos['costo']}",
                font=FUENTE_NORMAL, bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO,
                command=hacer_seleccion, width=15).pack(pady=3)

    tk.Button(panel_izq, text="⚔ Iniciar combate", font=FUENTE_BOTON,
            bg="red", fg="white", command=iniciar_combate, width=15).pack(pady=20)
  
    #### Dibujar mapa inicial con lo que pone el defensor ####
    redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA, estado, faccion_defensor, faccion_atacante) 
def mostrar_resultado_ronda(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado, ganador):
    limpiar_pantalla(root)
    root.configure(bg=COLOR_FONDO)

    if ganador == "defensor":
        nombre_ganador = jugador1.nombre_usuario
        color_ganador = COLOR_BOTON
    else:
        nombre_ganador = jugador2.nombre_usuario
        color_ganador = "red"

    tk.Label(root, text="Fin de Ronda", font=FUENTE_TITULO,
             bg=COLOR_FONDO, fg=COLOR_TITULO).pack(pady=20)

    tk.Label(root, text=f"🏆 {nombre_ganador} ganó la ronda",
             font=("Arial", 14, "bold"), bg=color_ganador, fg="white").pack(pady=10, ipadx=15, ipady=8)

    frame_marcador = tk.Frame(root, bg=COLOR_PANEL, padx=20, pady=15)
    frame_marcador.pack(pady=15)

    tk.Label(frame_marcador, text="Marcador", font=FUENTE_BOTON,
             bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=(0,8))
    tk.Label(frame_marcador, text=f"{jugador1.nombre_usuario} (Defensor): {estado.rondas_defensor} ronda(s)",
             font=FUENTE_NORMAL, bg=COLOR_PANEL).pack()
    tk.Label(frame_marcador, text=f"{jugador2.nombre_usuario} (Atacante): {estado.rondas_atacante} ronda(s)",
             font=FUENTE_NORMAL, bg=COLOR_PANEL).pack()

    if estado.rondas_defensor >= 3:
        tk.Button(root, text="🏆 Ver ganador", font=FUENTE_BOTON,
                  bg=COLOR_BOTON, fg="white", width=20,
                  command=lambda: mostrar_ganador_partida(root, jugador1, jugador2, "defensor")).pack(pady=20)

    elif estado.rondas_atacante >= 3:
        tk.Button(root, text="🏆 Ver ganador", font=FUENTE_BOTON,
                  bg="red", fg="white", width=20,
                  command=lambda: mostrar_ganador_partida(root, jugador1, jugador2, "atacante")).pack(pady=20)

    else:
        tk.Label(root, text=f"Próxima: Ronda {estado.ronda_actual + 1}",
                 font=("Arial", 10, "italic"), bg=COLOR_FONDO, fg="gray").pack(pady=5)

        def siguiente_ronda():
            from combate import preparar_nueva_ronda
            preparar_nueva_ronda(estado)
            mostrar_mapa(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado)

        tk.Button(root, text="▶ Siguiente ronda", font=FUENTE_BOTON,
                  bg="green", fg="white", width=20,
                  command=siguiente_ronda).pack(pady=10)

def mostrar_ganador_partida(root, jugador1, jugador2, ganador):
    limpiar_pantalla(root)
    root.configure(bg=COLOR_FONDO)

    if ganador == "defensor":
        jugador_ganador = jugador1
        rol_ganador = "defensor"
        color = COLOR_BOTON
    else:
        jugador_ganador = jugador2
        rol_ganador = "atacante"
        color = "red"

    jugador_ganador.sumar_victoria(rol_ganador)
    gestor.guardar()

    tk.Label(root, text="¡Partida terminada!", font=FUENTE_TITULO,
             bg=COLOR_FONDO, fg=COLOR_TITULO).pack(pady=30)

    frame = tk.Frame(root, bg=color, padx=30, pady=20)
    frame.pack(pady=10)

    tk.Label(frame, text=f"🏆 {jugador_ganador.nombre_usuario}",
             font=("Arial", 18, "bold"), bg=color, fg="white").pack()
    tk.Label(frame, text=f"Rol: {rol_ganador.capitalize()}",
             font=("Arial", 11, "italic"), bg=color, fg="white").pack(pady=5)

    tk.Button(root, text="Volver al inicio", font=FUENTE_BOTON,
              bg=COLOR_PANEL, fg=COLOR_TITULO, width=20,
              command=lambda: mostrar_login(root)).pack(pady=30)
           

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
    tk.Label(root, text="Top 5 Atacantes", font=("Arial", 12, "bold")).pack(pady=5)
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