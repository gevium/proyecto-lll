import json as json
import os as os #permite manejar el sistema de archivos

'''
########################################################################
DATOS DE LAS ENTIDADES (CONSTANTES)
########################################################################
'''
TORRES = {
    "basica": {"nombre": "Torre Basica", "costo": 50, "vida": 80, "daño": 15,"alcance": 2, "habilidad": "disparo_doble", "turnos_habilidad": 3},
    "pesada": {"nombre": "Torre Pesada", "costo": 120,"vida": 180, "daño": 25,"alcance": 2,"habilidad": "daño_area","turnos_habilidad": 4},
    "magica": {"nombre": "Torre Magica","costo": 90, "vida": 60,"daño": 10, "alcance": 3,"habilidad": "congelar", "turnos_habilidad": 5}
}
 
UNIDADES = {
    "soldado": {"nombre": "Soldado", "costo": 40, "vida": 60, "daño": 18, "velocidad": 1, "habilidad": "ataque_doble","turnos_habilidad": 3},
    "tanque": {"nombre": "Tanque", "costo": 100, "vida": 200, "daño": 28,"velocidad": 1,"habilidad": "escudo_temporal", "turnos_habilidad": 4},
    "rapida": {"nombre": "Unidad Rapida","costo": 60,"vida": 50,"daño": 12,"velocidad": 2,"habilidad": "aumento_velocidad","turnos_habilidad": 3}
}
 
#FACCIONES
#Se pueden remplazar con imagenes. Version preliminar: colores
FACCIONES = {
    "medieval": {"nombre": "Medieval", "color_boton": "#986846"},
    "futurista": {"nombre": "Futurista", "color_boton": "#4F8D94"},
    "naturaleza": {"nombre": "Naturaleza", "color_boton": "#7EB758"}
}
 
#Valores iniciales
DINERO_INICIAL_DEFENSOR = 200
DINERO_INICIAL_ATACANTE = 200
VIDA_BASE_CENTRAL = 200
RONDAS_PARA_GANAR = 3

RUTA_ARCHIVO = os.path.join("data", "jugadores.json") #ruta hacia el archivo de jugadores

'''
########################################################################
CLASES
########################################################################
'''

'''CLASE JUGADOR'''
class Jugador:
        
        #Constructor del jugador
        def __init__(self, nombre_usuario, contraseña, victorias_defensor=0, victorias_atacante=0):
            self.nombre_usuario = nombre_usuario
            self.contraseña = contraseña
            self.victorias_defensor = victorias_defensor
            self.victorias_atacante = victorias_atacante

        #Permite actualizar victorias del jugador según su rol
        def sumar_victoria (self, rol):
            if rol == "defensor":
                self.victorias_defensor += 1
            elif rol == "atacante":
                self.victorias_atacante += 1
        
        #Convierte la información de un jugador en un diccionario (con el fin de poder utilizarlo en Json)
        def convertir_diccionario(self):
             return {"nombre_usuario": self.nombre_usuario,"contraseña": self.contraseña,"victorias_defensor": self.victorias_defensor,"victorias_atacante": self.victorias_atacante}
        
        #Crea un jugador con la información de un diccionario (para traer jugador del archivo Json)
        @staticmethod
        def crear_jugador_dicc(datos):
             return Jugador (datos["nombre_usuario"], datos["contraseña"], datos.get("victorias_defensor", 0), datos.get("victorias_atacante", 0))
        #el datos.get() evita errores en caso de que no se haya introducido un valor en victorias_defensor o victorias_atacante        


'''CLASE JUGADORES JSON (inicio de sesión)'''
class Jugadores_Json:
     
    #construcor
    def __init__(self, ruta = RUTA_ARCHIVO):
        self.jugadores = {}
        self.ruta = ruta
        self.cargar()
    
    #funcion que permite cargar los jugadores desde el archivo json
    def cargar(self):
        if os.path.exists(self.ruta):
            with open(self.ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                for nombre, info in datos.items():
                    self.jugadores[nombre] = Jugador.crear_jugador_dicc(info)
        else:
            self.jugadores = {} #no hay jugadores
    
    #permite guardar todos los nombres en el archivo json
    def guardar(self):
        datos = {nombre: jugador.convertir_diccionario() for nombre, jugador in self.jugadores.items()}
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
        with open(self.ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    #permite registrar el nombre del jugador. Retorna True si se logro con exito
    def registrar(self, nombre_usuario, contraseña):
        if nombre_usuario in self.jugadores:
            return False, "Ese nombre de usuario ya existe."
 
        nuevo_jugador = Jugador(nombre_usuario, contraseña)
        self.jugadores[nombre_usuario] = nuevo_jugador
        self.guardar()
        return True, "Registro exitoso."

    #verifica que el jugador y su contraseña existan en el diccionario
    def iniciar_sesion(self, nombre_usuario, contraseña):
        if nombre_usuario not in self.jugadores: #validacion
            return False, "Usuario no encontrado."
 
        jugador = self.jugadores[nombre_usuario]
        if jugador.contraseña != contraseña: #validacion 
            return False, "contraseña incorrecta."
 
        return True, jugador #retorna tupla
    
    #Retorna una lista de los jugadores con mas victorias como rol defensor
    def obtener_top_defensores(self, cantidad=5):
        lista = list(self.jugadores.values())
        lista.sort(key=lambda j: j.victorias_defensor, reverse=True)
        return lista[:cantidad]
    
    #Retorna una lista de los jugadores con mas victorias como rol atacante
    def obtener_top_atacantes(self, cantidad=5):
        lista = list(self.jugadores.values())
        lista.sort(key=lambda j: j.victorias_atacante, reverse=True)
        return lista[:cantidad]
    

'''CLASE ENTIDADES (muros, torres, etc)'''
class Entidad:

    #Constructor
    def __init__(self, nombre, vida, daño=0):
        self.nombre = nombre
        self.vida_maxima = vida
        self.vida = vida
        self.daño = daño

    #Resta vida a la identidad. Retorna True si la entidad fue destruida (su vida llego a 0)
    def recibir_daño(self, cantidad):
        self.vida -= cantidad
        if self.vida < 0:
            self.vida = 0
    
    #Permite verificar si la entidad ya fue destruida, en base a su vida
    def esta_destruido(self):
        return self.vida <= 0

'''CLASE TORRE (entidad)''' 
class Torre (Entidad):
    
    #Constructor
    def __init__(self, nombre, costo, vida, daño, alcance, habilidad, turnos_habilidad):
        super().__init__(nombre, vida, daño)
        self.costo = costo
        self.alcance = alcance
        self.habilidad = habilidad
        self.turnos_habilidad = turnos_habilidad
        self.turnos_restantes = turnos_habilidad  #contador para saber cuando se activa la habilidad
        self.posicion = None  #(fila, columna) en el mapa
        self.tipo = "torre"
 
    #Verifica si una posicion esta dentro del alcance de la torre
    def en_rango(self, fila_objetivo, columna_objetivo):
        if self.posicion is None: #en caso de que aun no haya sido asignada una posicion
            return False
        fila, columna = self.posicion
        distancia = abs(fila - fila_objetivo) + abs(columna - columna_objetivo)
        return distancia <= self.alcance #si la distancia es menor que el alcance de la torre, retorna True
    
    #activa la habilidad de una torre en base a su nom re
    def activar_habilidad(self, juego, objetivo=None):
        #DISPARO DOBLE
        if self.habilidad == "disparo_doble":
            if objetivo is not None:
                objetivo.recibir_daño(self.daño)

        #DAÑAR AREA
        elif self.habilidad == "daño_area":
            if objetivo is not None and self.posicion is not None: #si el objetivo existe y ya tiene posicion 
                for unidad in juego.unidades:
                    if self.en_rango(unidad.posicion[0], unidad.posicion[1]):
                        unidad.recibir_daño(self.daño // 2)
        
        #CONGELAR
        elif self.habilidad == "congelar":
            if objetivo is not None:
                objetivo.congelada = True
                objetivo.turnos_congelada = 2

        #REPARAR
        elif self.habilidad == "reparar":
            for torre in juego.torres:
                if torre is not self and self.en_rango(*torre.posicion):
                    torre.vida = min(torre.vida_maxima, torre.vida + 20)

        #AUMENTAR DAÑO
        elif self.habilidad == "aumentar_daño":
            self.daño_temporal = int(self.daño * 1.5)
 
        #Reinicia el contador de turnos para la proxima activacion
        self.turnos_restantes = self.turnos_habilidad

"""CLASE UNIDAD"""
class Unidad(Entidad):

    #Constructor
    def __init__(self, nombre, costo, vida, daño, velocidad, habilidad, turnos_habilidad):
        super().__init__(nombre, vida, daño)
        self.costo = costo
        self.velocidad = velocidad
        self.habilidad = habilidad
        self.turnos_habilidad = turnos_habilidad
        self.turnos_restantes = turnos_habilidad
        self.posicion = None  #(fila, columna) en el mapa
        self.congelada = False
        self.turnos_congelada = 0
        self.escudo = 0
        self.tipo = "unidad"
    
    #Mueve la unidad a una nueva posicion si no esta congelada
    def mover(self, destino):
        if self.congelada:
            self.turnos_congelada -= 1
            if self.turnos_congelada <= 0:
                self.congelada = False
            return
        self.posicion = destino
    
    #Funcion que recibe el daño
    def recibir_daño(self, cantidad):
        if self.escudo > 0:
            absorbido = min(self.escudo, cantidad) #diferencia entre la capacidad actual del escudo y el daño recibido
            self.escudo -= absorbido
            cantidad -= absorbido
        super().recibir_daño(cantidad) #se llama recibir_daño de la clase padre, para terminar de complementar la funcion

    #funcion que activa la habilidad de la identidad, en base a su nombre (tipo de habilidad)
    def activar_habilidad(self, juego, objetivo=None):

        #ATAQUE DOBLE
        if self.habilidad == "ataque_doble":
            if objetivo is not None:
                objetivo.recibir_daño(self.daño)

        #ESCUDO TEMPORANL
        elif self.habilidad == "escudo_temporal":
            self.escudo = 30

        #CURARION
        elif self.habilidad == "curacion":
            self.vida = min(self.vida_maxima, self.vida + 25)

        #AUMENTO DE VELOCIDAD
        elif self.habilidad == "aumento_velocidad":
            self.velocidad += 1

        #DAÑO EXTRA A LAS TORRES
        elif self.habilidad == "daño_extra_torres":
            if objetivo is not None and isinstance(objetivo, Torre):
                objetivo.recibir_daño(self.daño)

        #Se actualiza los turnos de la unidad
        self.turnos_restantes = self.turnos_habilidad
 
'''CLASE MURO (entidad)'''
class Muro(Entidad):
    
    #Constructor
    def __init__(self, costo, vida=50):
        super().__init__("Muro", vida)
        self.costo = costo
        self.posicion = None
        self.tipo = "muro"
 
'''CLASE BASE CENTRAL (entidad)'''
class BaseCentral(Entidad):

    #Constructor
    def __init__(self, vida=200, posicion=(0, 0)):
        super().__init__("Base Central", vida)
        self.posicion = posicion
        self.tipo = "base"
