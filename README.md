[README.md](https://github.com/user-attachments/files/29182686/README.md)
**DEFENSA Y ASALTO DE BASE**

REQUISITOS

* Python 3.10 o superior  
* Tkinter (incluido con Python)

CÓMO EJECUTAR
* Accediendo desde github:
1. Clonar el repositorio:
   git clone https://github.com/gevium/proyecto-lll.git
2. Entrar a la carpeta del proyecto:
   cd nombre-del-repo
3. Ejecutar el archivo principal:
   python principal.py
>>>**Importante:** el programa debe ejecutarse **desde la carpeta raíz** del proyecto para que las rutas a `imagenes/` y `data/` funcionen correctamente.
* Accediendo desde el zip con los archivos actualizados del proyecto
1. Descomprimir el archivo .zip  
2. Abrir una terminal en la carpeta del proyecto  
3. Ejecutar: python principal.py

ARCHIVOS PRINCIPALES

* principal.py  → punto de entrada del programa  
* ventanas.py → interfaz gráfica (Tkinter)  
* clases.py → lógica del juego (torres, unidades, jugadores, facciones)  
* combate.py → motor de combate por rondas/turnos  
* prueba.py → script de pruebas del flujo de combate  
* data/jugadores.json → datos de jugadores registrados (usuario, contraseña, victorias)  
* imagenes/ → recursos gráficos (torres, unidades, muros, fondos) por facción
