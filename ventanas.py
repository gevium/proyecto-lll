import tkinter as tk
from tkinter import messagebox
from clases import Jugadores_Json, Torre, Muro, Unidad, TORRES, UNIDADES, FACCIONES
from combate import EstadoJuego, ejecutar_combate, preparar_nueva_ronda

def cargar_imagen(ruta):
    img = tk.PhotoImage(file=ruta)
    return img.subsample(16, 16)  # 1024/16 = 64px exacto


IMAGENES = {}  # diccionario vacio al inicio

def cargar_todas_las_imagenes():
    global IMAGENES
    IMAGENES = {
        "soldado_medieval": cargar_imagen("imagenes/soldado_medieval.png"),
        "soldado_futurista": cargar_imagen("imagenes/soldado_tecno.png"),
        "soldado_naturaleza": cargar_imagen("imagenes/soldado_natural.png"),
        "tanque_medieval": cargar_imagen("imagenes/tanque_medieval.png"),
        "tanque_futurista": cargar_imagen("imagenes/tanque_tecno.png"),
        "tanque_naturaleza": cargar_imagen("imagenes/tanque_natural.png"),
        "rapida_medieval": cargar_imagen("imagenes/u_rapida_medieval.png"),
        "rapida_futurista": cargar_imagen("imagenes/u_rapida_tecno.png"),
        "rapida_naturaleza": cargar_imagen("imagenes/u_rapida_natural.png"),
        "basica_medieval": cargar_imagen("imagenes/torre_N1_medieval.png"),
        "pesada_medieval": cargar_imagen("imagenes/torre_N2_medieval.png"),
        "magica_medieval": cargar_imagen("imagenes/torre_N3_medieval.png"),
        "basica_futurista": cargar_imagen("imagenes/torre_N1_tecno.png"),
        "pesada_futurista": cargar_imagen("imagenes/torre_N2_tecno.png"),
        "magica_futurista": cargar_imagen("imagenes/torre_N3_tecno.png"),
        "basica_naturaleza": cargar_imagen("imagenes/torre_N1_natural.png"),
        "pesada_naturaleza": cargar_imagen("imagenes/torre_N2_natural.png"),
        "magica_naturaleza": cargar_imagen("imagenes/torre_N3_natural.png"),
        "muro_medieval": cargar_imagen("imagenes/muro_medieval.png"),
        "muro_futurista": cargar_imagen("imagenes/muro_tecno.png"),
        "muro_naturaleza": cargar_imagen("imagenes/muro_natural.png"),
        "base": cargar_imagen("imagenes/base.png"),
        "cesped": cargar_imagen("imagenes/cesped.png"),
        "fondo": tk.PhotoImage(file="imagenes/fondo.png")
    }

'''
##############################################################################
VARIABLES/CONSTANTES GLOBALES
##############################################################################
'''

TAMANO_CASILLA = 64  
FILAS = 11
COLUMNAS = 11

gestor = Jugadores_Json() #Instancia que permite leer y escribir las cuentas de usuario en JSON
sesion_actual = {"jugador1": None, "jugador2": None} #Dicccionario para ubicar las instancias (elementos) de los jugadores actuales

#Paleta de colores y fuentes para ventanas generales
COLOR_FONDO = "#7f9db6"       # azul oscuro que combina con el fondo
COLOR_PANEL = "#7f9db6"       # panel más oscuro semiopaco
COLOR_BOTON = "#94A4B2"       # dorado oscuro medieval
COLOR_BOTON_TEXTO = "#354256" # texto crema
COLOR_TITULO = "#202636"      # títulos crema
FUENTE_TITULO = ("Georgia", 16, "bold")
FUENTE_NORMAL = ("Arial", 10)
FUENTE_BOTON = ("Arial", 10, "bold")

'''
##############################################################################
FUNCIONES PARA EL INICIO-REGISTRO DE SESION
##############################################################################
'''

#Elimina cualquier widget de la ventana que sea llamada
def limpiar_pantalla(root):
    for widget in root.winfo_children():
        widget.destroy()
    label_fondo = tk.Label(root, image=IMAGENES["fondo"])
    label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
    label_fondo.lower()

#Funcion que permite gestionar la informacion brindada para el registro de un usuario
def registrar(entry_user, entry_contra):
    usuario = entry_user.get().strip() #Se obtiene el nombre registrado
    contraseña = entry_contra.get().strip() #Se obtiene la contraseña registrada

    #Se validad que ningun campo quede vacío
    if not usuario or not contraseña:
        messagebox.showwarning("Aviso", "Los campos se encuentran vacíos.")
        return
    
    confirmacion, mensaje = gestor.registrar(usuario, contraseña) #se hace el registro en el diccionario

    #Mensaje de confirmacion
    if confirmacion:
        messagebox.showinfo("Registro", mensaje)
    else:
        messagebox.showwarning("ERROR", mensaje)

#Funcion que permite manejar la autentificacion del usuario
def iniciar_sesion(root, entry_user, entry_contra, label_estado, btn_comenzar):
    usuario = entry_user.get().strip() #Se obtiene el nombre ingresado
    contraseña = entry_contra.get().strip() #Se obtiene la contraseña ingresada

    #Se validan que los campos no estén vacíos
    if not usuario or not contraseña:
        messagebox.showwarning("Aviso", "Los campos se encuentran vacíos.")
        return

    #Si ambos usuarios ya fueron ingresados, no se puede volver a registrar un tercero
    if sesion_actual["jugador1"] is not None and sesion_actual["jugador2"] is not None:
        messagebox.showwarning("Aviso", "Ya hay dos jugadores listos. Presioná Comenzar.")
        return

    confirmacion, jugador = gestor.iniciar_sesion(usuario, contraseña) #se buscan las credenciales en el diccionario
    if not confirmacion: #Si retornó False, alguna de las credenciales es incorrecta
        messagebox.showwarning("ERROR", "Usuario o contraseña incorrectos.")
        return

    #Se asigna el jugador 1
    if sesion_actual["jugador1"] is None: #El campo inicia vacío
        sesion_actual["jugador1"] = jugador 
        label_estado.config(text=f"✔ {jugador.nombre_usuario} ha sido seleccionado. Esperando jugador 2...", fg=COLOR_TITULO)
        entry_user.delete(0, tk.END) #Se limpian los campos
        entry_contra.delete(0, tk.END)

    #Si ya hay un jugador 1 registrado, se pasa al jugador 2
    elif sesion_actual["jugador2"] is None:

        #Se valida que sea una cuenta diferente
        if jugador.nombre_usuario == sesion_actual["jugador1"].nombre_usuario:
            messagebox.showwarning("Aviso", "El jugador 2 debe ser una cuenta diferente.")
            return
        sesion_actual["jugador2"] = jugador
        label_estado.config(text=f"✔ {jugador.nombre_usuario} ha sido seleccionado. ¡Es hora de para comenzar!", fg=COLOR_TITULO)
        btn_comenzar.config(state="normal") #Se activa el boton para comenzar partida
        entry_user.delete(0, tk.END)
        entry_contra.delete(0, tk.END)


'''
##############################################################################
FUNCIONES DE INTERFAZ GRAFICA = FIG
1. Mostrar pantalla de login y registro 
##############################################################################
'''

#Funcion para mostrar login y registro. Dibuja el menú de inicio y resetea variables de sesión
def mostrar_login(root):
    limpiar_pantalla(root) #se limpia la ventana
    sesion_actual["jugador1"] = None #Se resetean las sesiones
    sesion_actual["jugador2"] = None

    #Elementos de interfaz (LABELS Y BOTONES):
    root.configure(bg=COLOR_FONDO)

    tk.Label(root, text="Defensa y Asalto de Base", font=("Georgia", 28, "bold"), bg=COLOR_FONDO, fg=COLOR_TITULO).pack(pady=(70, 0))

    frame = tk.Frame(root, bg=COLOR_PANEL, padx=30, pady=30)
    frame.pack(pady=10)

    tk.Label(frame, text="USUARIO:", font=FUENTE_NORMAL, bg=COLOR_PANEL).pack(pady=(10,0))
    entry_user = tk.Entry(frame, font=FUENTE_NORMAL, width=25)
    entry_user.pack(pady=5)

    tk.Label(frame, text="CONTRASEÑA:", font=FUENTE_NORMAL, bg=COLOR_PANEL).pack(pady=(10,0))
    entry_contra = tk.Entry(frame, font=FUENTE_NORMAL, width=25, show="*")
    entry_contra.pack(pady=5)

    tk.Button(frame, text="Iniciar sesión", font=FUENTE_BOTON, bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=20,  command=lambda: iniciar_sesion(root, entry_user, entry_contra, label_estado, btn_comenzar)).pack(pady=(15,5))
    tk.Button(frame, text="Registrarse", font=FUENTE_BOTON, bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=20, command=lambda: registrar(entry_user, entry_contra)).pack(pady=5)
    
    label_estado = tk.Label(frame, text="Esperando jugador 1...", font=FUENTE_NORMAL, bg=COLOR_PANEL, fg=COLOR_BOTON_TEXTO)
    label_estado.pack(pady=5)

    btn_comenzar = tk.Button(frame, text="⚔ Comenzar partida", font=FUENTE_BOTON, bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=20, state="disabled", command=lambda: mostrar_seleccion_faccion(root, sesion_actual["jugador1"], sesion_actual["jugador2"]))
    btn_comenzar.pack(pady=5)

    tk.Button(frame, text="Top Jugadores", font=FUENTE_BOTON, bg=COLOR_PANEL, fg=COLOR_BOTON_TEXTO, width=20, command=lambda: mostrar_top_jugadores(root)).pack(pady=5)

'''
##############################################################################
ACTUALIZAR INTERFAZ DEL MAPA
##############################################################################
'''

#Funcion que limpia el canvas del mapa, y dibuja celda por celda
def redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA,estado,faccion_defensor,  faccion_atacante=None):
    canvas.delete("all") #se limpia los valores actuales

    #Comienza el recorrido de la matriz
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            x1 = columna * TAMANO_CASILLA
            y1 = fila * TAMANO_CASILLA
            x2 = x1 + TAMANO_CASILLA
            y2 = y1 + TAMANO_CASILLA

            entidad = estado.mapa[fila][columna] #Obtiene el objeto situado en esa coordenada lógica de la matriz
            
            #En base a su tipo (o si está vacía, se le asiga un color)
            #Se usan las contanstes con las facciones anteriormente seleccionadas
            if entidad is None:
                canvas.create_image(x1 + 25, y1 + 25, image=IMAGENES["cesped"])
            elif entidad.tipo == "base":
                canvas.create_image(x1 + 25, y1 + 25, image=IMAGENES["cesped"])
                canvas.create_image(x1 + 25, y1 + 25, image=IMAGENES["base"])
            elif entidad.tipo == "torre":
                canvas.create_image(x1 + 25, y1 + 25, image=IMAGENES["cesped"])
                clave = f"{entidad.habilidad.split('_')[0]}_{faccion_defensor}"
                # mapear habilidad a tipo de torre
                tipo_torre = {"disparo": "basica", "daño": "pesada", "congelar": "magica"}.get(entidad.habilidad.split("_")[0], "basica")
                clave = f"{tipo_torre}_{faccion_defensor}"
                canvas.create_image(x1 + 25, y1 + 25, image=IMAGENES.get(clave, IMAGENES["base"]))
            elif entidad.tipo == "muro":
                canvas.create_image(x1 + 25, y1 + 25, image=IMAGENES["cesped"])
                canvas.create_image(x1 + 25, y1 + 25, image=IMAGENES[f"muro_{faccion_defensor}"])
            elif entidad.tipo == "unidad":
                canvas.create_image(x1 + 25, y1 + 25, image=IMAGENES["cesped"])
                # mapear nombre a clave
                tipo_unidad = {"Soldado": "soldado", "Tanque": "tanque", "Unidad Rapida": "rapida"}.get(entidad.nombre, "soldado")
                clave = f"{tipo_unidad}_{faccion_atacante}"
                if faccion_atacante:
                    canvas.create_image(x1 + 32, y1 + 32, image=IMAGENES.get(clave, IMAGENES["base"]))

'''
##############################################################################
FIG
2. Mostrar canvas con el mapa y panel/seleccion del defensor 
##############################################################################
'''

#Funcion que permite inicializar el mapa, y muestra el panel del turno del defensor
def mostrar_mapa_y_defensor(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado=None):
    limpiar_pantalla(root)

    if estado is None: #si es la primera ronda crea el estado, si no, reutiliza el existente
        estado = EstadoJuego(jugador1, jugador2)

    seleccion_actual = [None] #si se usa seleccion_actual = None, la función cambiar_seleccion no podría avisarle a la función colocar_estructura qué botón tocó el usuario.

    def ir_a_fase_atacante(): #crearla adentro de la funcion permite evitar llamar tantos parametros en tk.Button
        mostrar_fase_atacante(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado)
    
    #Elementos de interfaz gráfica
    frame_principal = tk.Frame(root, bg="#ACC5DF")
    frame_principal.pack(fill="both", expand=True)

    panel_izq = tk.Frame(frame_principal, width=200, bg="#ACC5DF")
    panel_izq.pack(side="left", fill="y")
    panel_izq.pack_propagate(False)

    panel_centro = tk.Frame(frame_principal, bg= "#ACC5DF")
    panel_centro.pack(side= "left")

    tk.Label(panel_izq, text=jugador1.nombre_usuario, font=("Arial", 12, "bold"), bg="#ACC5DF", fg=COLOR_TITULO).pack(pady=(15,0))
    tk.Label(panel_izq, text="(Defensor)", font=("Arial", 9, "italic"), bg="#ACC5DF", fg=COLOR_TITULO).pack()

    label_dinero = tk.Label(panel_izq, text=f"${estado.dinero_defensor}", font=("Arial", 12), bg="#ACC5DF", fg=COLOR_TITULO)
    label_dinero.pack(pady=10)

    tk.Label(panel_izq, text="Ronda", font=FUENTE_BOTON, bg="#ACC5DF", fg=COLOR_TITULO).pack(pady=(15,2))
    
    label_ronda = tk.Label(panel_izq, text=f"{estado.ronda_actual}", font=("Arial", 14, "bold"), bg="#ACC5DF", fg=COLOR_TITULO)
    label_ronda.pack()

    tk.Label(panel_izq, text="Torres", font=FUENTE_BOTON, bg="#ACC5DF", fg=COLOR_TITULO).pack(pady=(10,2))
    tk.Button(panel_izq, text="Básica - $50", font=FUENTE_NORMAL, bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=15, command=lambda: cambiar_seleccion("basica")).pack(pady=3)
    tk.Button(panel_izq, text="Pesada - $120", font=FUENTE_NORMAL, bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=15, command=lambda: cambiar_seleccion("pesada")).pack(pady=3)
    tk.Button(panel_izq, text="Mágica - $90", font=FUENTE_NORMAL, bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=15, command=lambda: cambiar_seleccion("magica")).pack(pady=3)

    tk.Label(panel_izq, text="Muros", font=FUENTE_BOTON, bg="#ACC5DF", fg=COLOR_TITULO).pack(pady=(10,2))
    tk.Button(panel_izq, text="Muro - $20", font=FUENTE_NORMAL, bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=15, command=lambda: cambiar_seleccion("muro")).pack(pady=3)

    tk.Button(panel_izq, text="✔ Listo", font=FUENTE_BOTON, bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=15, command=ir_a_fase_atacante).pack(pady=20)
    
    #Se cra el canvas con la matriz
    canvas = tk.Canvas(panel_centro, width=COLUMNAS * TAMANO_CASILLA, height=FILAS * TAMANO_CASILLA, highlightthickness=0)
    canvas.pack(side="top", fill="both", expand=True)

    #Más funciones internas
    #Funcion que actualiza la variable con la estructura/entidad seleccionada
    def cambiar_seleccion(tipo):
        seleccion_actual[0] = tipo

    #Detecta el click del mouse y lo utiliza para colocar la seleccion actual en la mtriz
    def colocar_estructura(event):

        if seleccion_actual[0] is None:
            return #Si el usuario no ha seleccionado nada, 
        
        columna = event.x // TAMANO_CASILLA #Se obtiene la ubicacion, en pixeles, del click
        fila = event.y // TAMANO_CASILLA

        if (fila, columna) == (5, 5): #No se puede colocar nada encima de la celda (5,5)
            return
        if estado.mapa[fila][columna] is not None: #No se puede colocar una entidad encima de otra
            return

        tipo = seleccion_actual[0]

        if tipo == "muro":
            entidad = Muro(20) #Si es un muro, se crea el objeto muro (con 20 de costo)
        else: #Si no es muro, es torre
            datos = TORRES[tipo] #Valores base de la torre
            entidad = Torre(datos["nombre"], datos["costo"], datos["vida"], datos["daño"], datos["alcance"], 
                            datos["habilidad"], datos["turnos_habilidad"]) #Se crea el elemento torre

        #Si el defensor no tiene suficiente dinero, se detiene la funcion
        if estado.dinero_defensor < entidad.costo:
            messagebox.showwarning("Sin dinero", "No tienes suficiente dinero.")
            return

        if tipo == "muro": #se añade a la lista de "muros" actual
            estado.muros.append(entidad)
        else: #se añade a la lista de "torres" actual
            estado.torres.append(entidad)

        entidad.posicion = (fila, columna) #Se le asigna la posicion
        estado.mapa[fila][columna] = entidad

        #Se hace el cobro del objeto y se actualiza la etiqueta de saldo
        estado.dinero_defensor -= entidad.costo
        label_dinero.config(text=f"${estado.dinero_defensor}")

        #Se redibuja el mapa
        redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA, estado, faccion_defensor, faccion_atacante)

    #Deteccion de clicks
    canvas.bind("<Button-1>", colocar_estructura)

    #Dibujo inicial del mapa al abrir la ventana
    redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA, estado, faccion_defensor, faccion_atacante)

'''
##############################################################################
FIG
3. Seleccion de las facciones
##############################################################################
'''
#Muestra el menu de la seleccion de facciones
def mostrar_seleccion_faccion(root, jugador1, jugador2):
    limpiar_pantalla(root)
    root.configure(bg=COLOR_FONDO)

    faccion_j1 = {"valor": None} #Diccionarios para almacenar las selecciones de faccion
    faccion_j2 = {"valor": None}

    #Elementos de interfaz
    tk.Label(root, text="Selección de Facción", font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TITULO).pack(pady=20)

    frame_columnas = tk.Frame(root, bg=COLOR_FONDO)
    frame_columnas.pack(pady=10)

    #JUGADOR 1 - FACCIONES
    frame_j1 = tk.Frame(frame_columnas, bg=COLOR_PANEL, bd=2, relief="groove", padx=15, pady=15)
    frame_j1.grid(row=0, column=0, padx=20)

    tk.Label(frame_j1, text=jugador1.nombre_usuario, font=("Arial", 11, "bold"), bg=COLOR_PANEL, fg=COLOR_TITULO).pack()
    tk.Label(frame_j1, text="(Defensor)", font=("Arial", 9, "italic"),bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=2)
    label_seleccion_j1 = tk.Label(frame_j1, text="Sin selección",font=FUENTE_NORMAL, bg=COLOR_PANEL, fg=COLOR_BOTON_TEXTO)
    label_seleccion_j1.pack(pady=5)

    #JUGADOR 2 - FACCIONES
    frame_j2 = tk.Frame(frame_columnas, bg=COLOR_PANEL, bd=2, relief="groove", padx=15, pady=15)
    frame_j2.grid(row=0, column=1, padx=20)

    tk.Label(frame_j2, text=jugador2.nombre_usuario, font=("Arial", 11, "bold"), bg=COLOR_PANEL, fg=COLOR_TITULO).pack()
    tk.Label(frame_j2, text="(Atacante)", font=("Arial", 9, "italic"), bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=2)
    label_seleccion_j2 = tk.Label(frame_j2, text="Sin selección", font=FUENTE_NORMAL, bg=COLOR_PANEL, fg=COLOR_BOTON_TEXTO)
    label_seleccion_j2.pack(pady=5)

    label_aviso = tk.Label(root, text="", fg="#1A173A", bg=COLOR_FONDO, font=FUENTE_NORMAL)
    label_aviso.pack(pady=5)

    btn_continuar = tk.Button(root, text="⚔ Comenzar partida", font=FUENTE_BOTON,bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=20, state="disabled")
    btn_continuar.pack(pady=10)

    #Funcion que verifica que ambos jugadores hayan escogido facciones
    #O bien, que ambos tengan facciones diferentes
    def verificar_selecciones():
        if faccion_j1["valor"] is None or faccion_j2["valor"] is None:
            return
        if faccion_j1["valor"] == faccion_j2["valor"]:
            label_aviso.config(text="Las facciones deben ser diferentes.")
            btn_continuar.config(state="disabled")
            return
        label_aviso.config(text="") #Si todo está bien, se limpian las advertencias
        btn_continuar.config(state="normal")

    #Se actualiza la interfaz que se utilizará para el jugador 1
    def elegir_j1(clave):
        faccion_j1["valor"] = clave
        nombre = FACCIONES[clave]["nombre"]
        label_seleccion_j1.config(text=f"✔ {nombre}", fg=COLOR_TITULO)
        verificar_selecciones()

    for clave, datos in FACCIONES.items():
        def hacer_elegir_j1(c=clave): #asegura que el boton escoja el valor correcto
            elegir_j1(c)
        tk.Button(frame_j1, text=datos["nombre"], font=FUENTE_NORMAL, bg=datos["color_boton"], fg="white", width=15, command=hacer_elegir_j1).pack(pady=3)

    #Se actualiza la interfaz que se utilizará para el jugador 2
    def elegir_j2(clave):
        faccion_j2["valor"] = clave
        nombre = FACCIONES[clave]["nombre"]
        label_seleccion_j2.config(text=f"✔ {nombre}", fg=COLOR_TITULO)
        verificar_selecciones()

    for clave, datos in FACCIONES.items():
        def hacer_elegir_j2(c=clave): #asegura que el boton escoja el valor correcto
            elegir_j2(c)
        tk.Button(frame_j2, text=datos["nombre"], font=FUENTE_NORMAL, bg=datos["color_boton"], fg="white", width=15, command=hacer_elegir_j2).pack(pady=3)

    #Funcion que permite iniciar la partida
    def continuar():
        sesion_actual["jugador1"] = None #Se reinician los jugadores
        sesion_actual["jugador2"] = None
        mostrar_mapa_y_defensor(root, jugador1, jugador2, faccion_j1["valor"], faccion_j2["valor"]) #Se les asigna sus facciones correspondientes.

    btn_continuar.config(command=continuar) #Se habilita el boton

'''
##############################################################################
FIG
4. Mostrar el panel/seleccion del atacante + Inicio de combate
##############################################################################
'''
#Despliega la interfaz del atacante
def mostrar_fase_atacante(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado):
    limpiar_pantalla(root) 

    seleccion_actual = [None]

    #Estructuras de la interfaz
    frame_principal = tk.Frame(root, bg="#ACC5DF")
    frame_principal.pack(fill="both", expand=True)

    panel_izq = tk.Frame(frame_principal, width=200, bg="#ACC5DF")
    panel_izq.pack(side="left", fill="y")
    panel_izq.pack_propagate(False)

    panel_centro = tk.Frame(frame_principal, bg="#94A4B2")
    panel_centro.pack(side= "left")

    #se crea el panel derecho con ancho fijo y color de fondo
    panel_der = tk.Frame(frame_principal, width=200, bg="#ACC5DF")
    panel_der.pack(side="left", fill="y")
    panel_der.pack_propagate(False) #evita que el frame se encoja según su contenido


    #se vuelve a dibujar el canvas
    canvas = tk.Canvas(panel_centro, width=COLUMNAS * TAMANO_CASILLA, height=FILAS * TAMANO_CASILLA, highlightthickness=0)
    canvas.pack(side= "left")
    
    #Funciones internas
    def cambiar_seleccion(tipo):
        seleccion_actual[0] = tipo

    #Similar a la funcion "colocar_estructuras" del Defensor, sin enmargo esta se encuentra adaptada a la unidades del Atacante
    def colocar_unidad(event):
        if seleccion_actual[0] is None:
            return

        columna = event.x // TAMANO_CASILLA #Se obtiene el la ubicacion en px del click
        fila = event.y // TAMANO_CASILLA

        #Variable booleana
        #"Referencia" las restricciones de posicionamiento del los atacantes
        en_borde = (columna == 0 or columna == 10 or fila == 0 or fila == 10)
        if not en_borde: #Solo se pueden colocar unidades en los bordes
            messagebox.showwarning("Aviso", "Solo puedes colocar unidades en los bordes del mapa.")
            return

        #Validacion: no puede colocar unidades encima de torres
        if estado.mapa[fila][columna] is not None:
            messagebox.showwarning("Aviso", "Esa casilla ya está ocupada.")
            return

        datos = UNIDADES[seleccion_actual[0]] #Obtiene los valores pedreterminados de las constantes

        #Validacion: el atacante debe tener suficiente dinero
        if estado.dinero_atacante < datos["costo"]:
            messagebox.showwarning("Sin dinero", "No tienes suficiente dinero.")
            return

        #Se crea el objeto unidad
        unidad = Unidad(datos["nombre"], datos["costo"], datos["vida"], datos["daño"], datos["velocidad"], 
                        datos["habilidad"], datos["turnos_habilidad"])
        unidad.posicion = (fila, columna)

        estado.unidades.append(unidad) #Se registra la unidad
        estado.mapa[fila][columna] = unidad 

        estado.dinero_atacante -= datos["costo"] #Se actualiza el dinero del atacante
        label_dinero.config(text=f"${estado.dinero_atacante}")

        redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA, estado, faccion_defensor, faccion_atacante)

    canvas.bind("<Button-1>", colocar_unidad) #Deteccion del click
    
    #Elementos de interfaz
    tk.Label(panel_izq, text=jugador2.nombre_usuario, font=("Arial", 12, "bold"), bg="#ACC5DF", fg=COLOR_TITULO).pack(pady=(15,0))
    tk.Label(panel_izq, text="(Atacante)", font=("Arial", 9, "italic"),bg="#ACC5DF", fg=COLOR_TITULO).pack()

    label_dinero = tk.Label(panel_izq, text=f"${estado.dinero_atacante}", font=("Arial", 12), bg="#ACC5DF", fg=COLOR_TITULO)
    label_dinero.pack(pady=10)

    tk.Label(panel_izq, text="Ronda", font=FUENTE_BOTON, bg="#ACC5DF", fg=COLOR_TITULO).pack(pady=(5,2))
    tk.Label(panel_izq, text=f"{estado.ronda_actual}", font=("Arial", 14, "bold"), bg="#ACC5DF", fg=COLOR_TITULO).pack()

    tk.Label(panel_izq, text="Unidades", font=FUENTE_BOTON, bg="#ACC5DF", fg=COLOR_TITULO).pack(pady=(10,2))


    #titulo del panel
    tk.Label(panel_der, text="Estado de batalla", font=("Arial", 12, "bold"), bg="#ACC5DF", fg=COLOR_TITULO).pack(pady=(15,5))

    #seccion de la base
    tk.Label(panel_der, text="🏰 Base", font=("Arial", 12, "bold"),bg="#ACC5DF", fg=COLOR_TITULO).pack(anchor="w", padx=10)
    label_base = tk.Label(panel_der, text=f"Vida: {estado.base.vida}", font=("Arial", 11), fg=COLOR_TITULO, bg="#ACC5DF")
    label_base.pack(anchor="w", padx=20) #se muestra la vida inicial de la base

    #seccion de torres — el frame_torres se limpia y redibuja en cada turno
    tk.Label(panel_der, text="🗼 Torres", font =("Arial", 12, "bold"), bg="#ACC5DF").pack(anchor="w", padx=10, pady=(10,0))
    frame_torres = tk.Frame(panel_der, bg="#ACC5DF")
    frame_torres.pack(fill="x") #contenedor donde se van a poner los labels de cada torre

    #seccion de unidades — igual que torres, se limpia y redibuja en cada turno
    tk.Label(panel_der, text="⚔ Unidades", font=("Arial", 12, "bold"), bg="#ACC5DF", fg=COLOR_TITULO).pack(anchor="w", padx=10, pady=(10,0))
    frame_unidades = tk.Frame(panel_der, bg="#ACC5DF")
    frame_unidades.pack(fill="x") #contenedor donde se van a poner los labels de cada unidad    

    #Inicia el combate (animación)
    def iniciar_combate():
        
        if not estado.unidades: #Si no hay almenos una unidad, no se puede iniciar
            messagebox.showwarning("Aviso", "Debes colocar al menos una unidad.")
            return
        
        def actualizar_ui(): #Se actualiza la matriz para mostrar el combate
            try:
                #redibuja el canvas con el estado actual del mapa
                redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA, estado, faccion_defensor, faccion_atacante)

                #actualiza el label de vida de la base
                label_base.config(text=f"Vida: {estado.base.vida}/{estado.base.vida_maxima}", font=("Arial", 11),bg="#ACC5DF", fg=COLOR_TITULO)

                #limpia los labels viejos de torres y crea uno nuevo por cada torre viva
                for widget in frame_torres.winfo_children():
                    widget.destroy() #elimina el label del turno anterior
                for torre in estado.torres:
                    tk.Label(frame_torres, text=f"{torre.nombre}: {torre.vida}/{torre.vida_maxima}",font=("Arial", 11),bg="#ACC5DF", fg=COLOR_TITULO).pack(anchor="w", padx=20)

                #limpia los labels viejos de unidades y crea uno nuevo por cada unidad viva
                for widget in frame_unidades.winfo_children():
                    widget.destroy() #elimina el label del turno anterior

                for unidad in estado.unidades:
                    if not unidad.esta_destruido():  # AGREGAR ESTO
                        tk.Label(frame_unidades, text=f"{unidad.nombre}: {unidad.vida}/{unidad.vida_maxima}", 
                                font=FUENTE_NORMAL, bg=COLOR_PANEL).pack(anchor="w", padx=20)
                root.update() #fuerza a tkinter a redibujar la ventana
                root.after(600) #espera 300ms antes del siguiente turno

            except Exception:
                pass #si el canvas fue destruido, ignora el error


        #ejecutar_combater (de combate.py)
        ganador = ejecutar_combate(estado, actualizar_ui)
        mostrar_resultado_ronda(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado, ganador)

    #For que genera los botones de seleccion de unidades atacantes
    for clave, datos in UNIDADES.items():
        def hacer_seleccion(c=clave):
            cambiar_seleccion(c)
        tk.Button(panel_izq, text=f"{datos['nombre']} - ${datos['costo']}", font=FUENTE_NORMAL, bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, command=hacer_seleccion, width=15).pack(pady=3)

    tk.Button(panel_izq, text="Iniciar combate", font=FUENTE_BOTON, bg=COLOR_BOTON_TEXTO, fg="white", command=iniciar_combate, width=15).pack(pady=20)
    redibujar_mapa(canvas, FILAS, COLUMNAS, TAMANO_CASILLA, estado, faccion_defensor, faccion_atacante) 

'''
##############################################################################
FIG
5. Mostrar resultados
##############################################################################
'''
#Funcion que muestra los resultados obtenidos
def mostrar_resultado_ronda(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado, ganador):
    limpiar_pantalla(root)
    root.configure(bg=COLOR_FONDO)
     
    #Se determina el ganador
    if ganador == "defensor":
        nombre_ganador = jugador1.nombre_usuario
    else:
        nombre_ganador = jugador2.nombre_usuario

    color_ganador = COLOR_PANEL

    #Elementos de interfaz
    tk.Label(root, text="Fin de Ronda", font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TITULO).pack(pady=20)
    tk.Label(root, text=f"🏆 {nombre_ganador} ganó la ronda", font=("Arial", 14, "bold"), bg=color_ganador, fg=COLOR_TITULO).pack(pady=10, ipadx=15, ipady=8)

    frame_marcador = tk.Frame(root, bg=COLOR_PANEL, padx=20, pady=15)
    frame_marcador.pack(pady=15)

    tk.Label(frame_marcador, text="Marcador", font=("Arial", 11, "bold"), bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=(0,8))
    tk.Label(frame_marcador, text=f"{jugador1.nombre_usuario} (Defensor): {estado.rondas_defensor} ronda(s)", font=("Arial", 12, "italic"), bg=COLOR_PANEL).pack()
    tk.Label(frame_marcador, text=f"{jugador2.nombre_usuario} (Atacante): {estado.rondas_atacante} ronda(s)", font=("Arial", 12, "italic"), bg=COLOR_PANEL).pack()

    #Caso 1. Ganó defensor
    if estado.rondas_defensor >= 3: 
        tk.Button(root, text="Ver ganador", font=FUENTE_BOTON, bg=COLOR_PANEL, fg="white", width=20, command=lambda: mostrar_ganador_partida(root, jugador1, jugador2, "defensor")).pack(pady=20)

    #Caso 2. Ganó atacante
    elif estado.rondas_atacante >= 3:
        tk.Button(root, text="Ver ganador", font=FUENTE_BOTON, bg=COLOR_PANEL, fg="white", width=20, command=lambda: mostrar_ganador_partida(root, jugador1, jugador2, "atacante")).pack(pady=20)

    #Caso 3: Ninguno ha ganado
    else:
        tk.Label(root, text=f"Próxima: Ronda {estado.ronda_actual + 1}", font=("Arial", 10, "italic"), bg=COLOR_FONDO, fg="#0C253A").pack(pady=5)

        def siguiente_ronda(): #Se prepara la nueva ronda y se vuelve a mostrar la pantalla del defensor
            preparar_nueva_ronda(estado)
            mostrar_mapa_y_defensor(root, jugador1, jugador2, faccion_defensor, faccion_atacante, estado)

        tk.Button(root, text="Siguiente ronda", font=FUENTE_BOTON, bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO, width=20, command=siguiente_ronda).pack(pady=10)

'''
##############################################################################
FIG
6. Mostrar resultados
##############################################################################
'''
#Funcion muestra a ganador y suma victorias
def mostrar_ganador_partida(root, jugador1, jugador2, ganador):
    limpiar_pantalla(root)
    root.configure(bg=COLOR_FONDO)

    #Se determina quien fue el ganador
    if ganador == "defensor":
        jugador_ganador = jugador1
        rol_ganador = "defensor"
        color = COLOR_BOTON
    else:
        jugador_ganador = jugador2
        rol_ganador = "atacante"
        color =COLOR_BOTON

    #Se realiza la sumatoria de victorias
    jugador_ganador.sumar_victoria(rol_ganador)

    gestor.guardar() #Se guarda en Json

    #Elementos de interfaz
    tk.Label(root, text="¡Partida terminada!", font=FUENTE_TITULO, bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=30)

    frame = tk.Frame(root, bg=COLOR_PANEL, padx=60, pady=40, bd=2, relief="groove")
    frame.pack(pady=10)

    tk.Label(frame, text=f"¡Felicidades!", font=("Arial", 16, "bold"), bg=COLOR_PANEL, fg=COLOR_BOTON_TEXTO).pack()
    tk.Label(frame, text=f"{jugador_ganador.nombre_usuario}", font=("Arial", 24, "bold"), bg=COLOR_PANEL, fg=COLOR_BOTON_TEXTO).pack()
    tk.Label(frame, text=f"Rol: {rol_ganador.capitalize()}", font=("Arial", 14, "italic"), bg=COLOR_PANEL, fg="white").pack(pady=5)

    tk.Button(root, text="Volver al inicio", font=FUENTE_BOTON, bg=COLOR_PANEL, fg=COLOR_TITULO, width=20,
              command=lambda: mostrar_login(root)).pack(pady=30)
           
'''
##############################################################################
FIG
7. Mostrar top jugadores
##############################################################################
'''

#Muestra la interfaz de los ganadores
def mostrar_top_jugadores(root):
    limpiar_pantalla(root)
    root.configure(bg=COLOR_FONDO)

    #Elementos de intefaz
    tk.Label(root, text="🏆 Top Jugadores", font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TITULO).pack(pady=20)

    frame_columnas = tk.Frame(root, bg=COLOR_FONDO)
    frame_columnas.pack(pady=10)

    #Top Defensores
    frame_def = tk.Frame(frame_columnas, bg=COLOR_PANEL, padx=20, pady=15, bd=2, relief="groove")
    frame_def.grid(row=0, column=0, padx=20)

    tk.Label(frame_def, text="🛡 Top Defensores", font=FUENTE_BOTON,  bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=(0,10))

    #se recolectan los defensores
    top_defensores = gestor.obtener_top_defensores()
    if not top_defensores: #Si no hay jugadores
        tk.Label(frame_def, text="Sin jugadores registrados", font=FUENTE_NORMAL, bg=COLOR_PANEL, fg=COLOR_TITULO).pack()
    
    else:
        for i, jugador in enumerate(top_defensores, start=1):
            texto = f"{i}.  {jugador.nombre_usuario} — {jugador.victorias_defensor} victorias" #texto con el top, nombre y cantidad de victorias
            tk.Label(frame_def, text=texto, font=FUENTE_NORMAL, bg=COLOR_PANEL, fg=COLOR_TITULO, anchor="w").pack(fill="x", pady=3)

    #Top Atacantes
    frame_atk = tk.Frame(frame_columnas, bg=COLOR_PANEL, padx=20, pady=15, bd=2, relief="groove")
    frame_atk.grid(row=0, column=1, padx=20)

    tk.Label(frame_atk, text="⚔ Top Atacantes", font=FUENTE_BOTON,bg=COLOR_PANEL, fg=COLOR_TITULO).pack(pady=(0,10))

    top_atacantes = gestor.obtener_top_atacantes()
    if not top_atacantes: #Si no hay atacantes
        tk.Label(frame_atk, text="Sin jugadores registrados",font=FUENTE_NORMAL, bg=COLOR_PANEL, fg=COLOR_TITULO).pack()
    
    else:
        for i, jugador in enumerate(top_atacantes, start=1):
            texto = f"{i}.  {jugador.nombre_usuario} — {jugador.victorias_atacante} victorias"
            tk.Label(frame_atk, text=texto, font=FUENTE_NORMAL, bg=COLOR_PANEL, fg=COLOR_TITULO, anchor="w").pack(fill="x", pady=3)

    tk.Button(root, text="Volver", font=FUENTE_BOTON, bg=COLOR_PANEL, fg=COLOR_TITULO, width=20, command=lambda: mostrar_login(root)).pack(pady=25)