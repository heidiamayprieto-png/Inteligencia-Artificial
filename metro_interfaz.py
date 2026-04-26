import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from metro import G, h, estaciones, mejor_ruta_estaciones, formatear_camino, accesibilidad

coords_estaciones = {
    "Observatorio": (91.5, 277),
    "Tacubaya": (135, 240),
    "Juanacatlan": (178, 206),
    "Chapultepec": (218, 175),
    "Sevilla": (260, 140),
    "Insurgentes": (304, 113),
    "Cuauhtemoc": (351, 113),
    "Balderas": (401, 112),
    "Universidad": (402, 537),
    "Copilco": (402, 504),
    "M.A. De Quevedo": (402, 470),
    "Viveros": (402, 438),
    "Coyoacan": (402, 405),
    "Zapata": (402, 372),
    "Division del Norte": (402, 340),
    "Eugenia": (402, 306),
    "Etiopia": (402, 274),
    "Centro Medico": (402, 240),
    "Hospital General": (403, 178),
    "Niños Heroes": (402, 144),
    "Juarez": (402, 52),
    "Barranca del Muerto": (135, 425),
    "Mixcoac": (135, 370),
    "San Antonio": (135, 330),
    "San Pedro de los Pinos": (135, 298),
    "Constituyentes": (135, 183),
    "Auditorio": (135, 125),
    "Polanco": (135, 60),
    "Patriotismo": (229, 240),
    "Chilpancingo": (335.5, 240),
    "Lazaro Cardenas": (511.5, 240),
    "Insurgentes Sur": (210, 370),
    "Hospital 20 de Noviembre": (298, 370),
    "Parque de los Venados": (503, 372),
    "Eje Central": (567, 448)
}

class metro_interfaz:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aplicación Metro Ciudad de México")
        self.root.geometry("1000x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#7DBCDE")

        self.camino = []
        self.tiempo_total = 0
        self.posicion_actual = 0
        self.posiciones_total = 0
        self.mov_suavizados = 0

        self.diseño_interfaz()

        try:
            self.tren = Image.open("tren.png")
            self.tren = self.tren.resize((40, 40))
            self.tk_tren = ImageTk.PhotoImage(self.tren)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la imagen del tren")

    def iniciar_animacion_metro(self):
        if hasattr(self, 'anim'):
            self.root.after_cancel(self.anim)

        if not hasattr(self, "puntos_ruta") or len(self.puntos_ruta) < 2:
            return

        self.canvas.delete("tren")

        x, y = self.puntos_ruta[0]
        self.tren = self.canvas.create_image(x, y, image=self.tk_tren, tags="tren")
        self.estacion_tren = 0
        self.mover_tren()

    def diseño_interfaz(self):
        diseño = ttk.Style()
        diseño.configure("Titulo.TLabel", background="#7DBCDE", foreground="black", font=("Arial", 15))
        diseño.configure("Origen.TLabel", background="#7DBCDE", foreground="black", font=("Arial", 12))
        diseño.configure("Btn.TButton", background="#7DBCDE", foreground="black", font=("Arial", 10))
        diseño.configure("Ruta_accesible.TCheckbutton", font=("Arial", 10, "bold"))

        # ----- FRAME IZQUIERDO -----
        izq = tk.Frame(self.root, bg="#7DBCDE")
        izq.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Encuentra tu ruta
        marco_titulo = tk.Frame(izq, bg="#7DBCDE", bd=2, relief="groove", padx=10, pady=5)
        marco_titulo.pack(pady=(0, 15))
        titulo = ttk.Label(marco_titulo, text="Encuentra tu ruta", style="Titulo.TLabel")
        titulo.pack()

        # Origen
        ttk.Label(izq, text="Origen:", style="Origen.TLabel").pack(anchor=tk.W)
        self.inter_origen = ttk.Combobox(izq, values=estaciones, state='normal')
        self.inter_origen.pack(fill=tk.X, pady=(0, 10))

        # Destino
        ttk.Label(izq, text="Destino:", style="Origen.TLabel").pack(anchor=tk.W)
        self.inter_destino = ttk.Combobox(izq, values=estaciones, state='normal')
        self.inter_destino.pack(fill=tk.X, pady=(0, 10))

        # Día
        inter_hora = tk.Frame(izq, bg="#7DBCDE")
        inter_hora.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(inter_hora, text="Día:", style="Origen.TLabel").pack(side=tk.LEFT)
        self.inter_dia = ttk.Combobox(inter_hora,values=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"], state="readonly", width=10)
        self.inter_dia.set("Lunes")
        self.inter_dia.pack(side=tk.LEFT, padx=(5, 10))

        # Hora
        ttk.Label(inter_hora, text="Hora:", style="Origen.TLabel").pack(side=tk.LEFT)
        self.inter_hora = ttk.Combobox(inter_hora, values=[f"{i:02d}" for i in range(24)], width=3, state='readonly')
        self.inter_hora.set("00")
        self.inter_hora.pack(side=tk.LEFT)

        tk.Label(inter_hora, text=":", bg="#7DBCDE", font=("Arial", 12)).pack(side=tk.LEFT)

        self.inter_minuto = ttk.Combobox(inter_hora, values=[f"{i:02d}" for i in range(60)], width=3, state="readonly")
        self.inter_minuto.set("00")
        self.inter_minuto.pack(side=tk.LEFT, padx=(0, 10))

        # Ruta accesible
        self.es_accesible = tk.BooleanVar(value=False)
        self.inter_accesible = ttk.Checkbutton(izq, text="Ruta accesible", style="Ruta_accesible.TCheckbutton", variable=self.es_accesible)
        self.inter_accesible.pack(anchor=tk.W, pady=(5, 10))

        # Calcular ruta
        self.inter_calcular = ttk.Button(izq, text="Calcular ruta", command=self.calcular_ruta, style="Btn.TButton")
        self.inter_calcular.pack(pady=10, fill=tk.X)

        # Ruta óptima
        ttk.Label(izq, text="Ruta óptima:", style="Origen.TLabel").pack(anchor=tk.W, pady=(10, 0))
        self.inter_ruta = tk.Text(izq, height=12, width=40, state='disabled', bg="#A1CFE8")
        self.inter_ruta.pack(pady=5)

        # Transbordos
        ttk.Label(izq, text="Transbordos:", style="Origen.TLabel").pack(anchor=tk.W, pady=(10, 0))
        self.inter_transbordos = tk.Text(izq, height=5, width=40, state='disabled', bg="#A1CFE8")
        self.inter_transbordos.pack(pady=5)

        # ----- FRAME DERECHO -----
        dcha = tk.Frame(self.root, bg="#7DBCDE")
        dcha.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

        # Mapa del Metro CMDX
        marco_titulo = tk.Frame(dcha, bg="#7DBCDE", bd=2, relief="groove", padx=10, pady=5)
        marco_titulo.pack(pady=(0, 15))
        titulo = ttk.Label(marco_titulo, text="Mapa del Metro CDMX", style="Titulo.TLabel")
        titulo.pack()

        self.canvas = tk.Canvas(dcha, width=1000, height=1000)
        self.canvas.pack()

        # Imagen Mapa del Metro CDMX
        try:
            self.mapa = Image.open("MapaMetroCDMX.png")
            self.mapa = self.mapa.resize((650, 600))
            self.tk_mapa = ImageTk.PhotoImage(self.mapa)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_mapa)
        except Exception as e:
            messagebox.showerror("Error", f"Error el cargar la imagen del Mapa del Metro CDMX")

    def calcular_ruta(self):
        if hasattr(self, 'anim'):
            self.root.after_cancel(self.anim)
            del self.anim

        self.inter_ruta.config(state="normal")
        self.inter_transbordos.config(state="normal")

        self.inter_ruta.delete("1.0", "end")
        self.inter_transbordos.delete("1.0", "end")

        self.camino = []
        self.tiempo_total = 0

        # Resetear ruta y tren
        if hasattr(self, "canvas"):
            self.canvas.delete("tren")
            self.canvas.delete("ruta")

        self.puntos_ruta = []
        self.estacion_tren = 0
        self.posicion_actual = 0
        self.posiciones_total = 0
        self.puntos_ruta = []
        self.estacion_tren = 0
        self.mov_suavizados = 0

        origen = self.inter_origen.get()
        destino = self.inter_destino.get()

        if not origen or not destino:
            messagebox.showwarning("Error", "Selecciona origen y destino")
            return
        if origen == destino:
            messagebox.showinfo("Info", "Mismo origen y destino")
            return

        dia = self.inter_dia.get()
        hora = self.inter_hora.get()
        minuto = self.inter_minuto.get()
        hora_min = f"{hora}:{minuto}"

        accesible = self.es_accesible.get()

        camino, tiempo = mejor_ruta_estaciones(origen, destino, dia, hora_min, False)

        self.inter_ruta.config(state='normal')
        self.inter_ruta.delete("1.0", tk.END)

        self.inter_transbordos.config(state='normal')
        self.inter_transbordos.delete("1.0", tk.END)

        if hasattr(self, "canvas"):
            self.canvas.delete("ruta")

        mensajes = []

        if self.es_accesible.get():
            if not accesibilidad.get(origen, False) and not accesibilidad.get(destino, False):
                mensajes.append(
                    f"No se puede hacer la ruta porque las estaciones {origen} y {destino} no son accesibles.")
            elif not accesibilidad.get(origen, False):
                mensajes.append(f"No se puede hacer la ruta porque la estación {origen} no es accesible.")
            elif not accesibilidad.get(destino, False):
                mensajes.append(f"No se puede hacer la ruta porque la estación {destino} no es accesible.")

            ultima_linea = None
            for nodo in camino:
                estacion, linea = nodo.split("_")
                if ultima_linea is not None and linea != ultima_linea:
                    if not accesibilidad.get(estacion, False):
                        mensajes.append(f"No se puede hacer la ruta porque el transbordo en {estacion} no es accesible.")

                ultima_linea = linea

            if mensajes:
                self.inter_ruta.config(state='normal')
                self.inter_ruta.delete("1.0", tk.END)
                self.inter_ruta.insert("1.0", "\n".join(mensajes))
                self.inter_ruta.config(state='disabled')
                return

        # Horarios metro
        h = int(hora)
        m = int(minuto)
        min_actual = h * 60 + m

        if self.inter_dia.get() == "Sábado":
            apertura = 6 * 60  # 06:00
        elif self.inter_dia.get() == "Domingo":
            apertura = 7 * 60  # 07:00
        else:
            apertura = 5 * 60  # 05:00

        metro_cerrado = not (apertura <= min_actual < 24 * 60)

        espera = 0
        if metro_cerrado:
            if min_actual < apertura:
                espera = apertura - min_actual
            else:
                espera = (24 * 60 - min_actual) + apertura

            ap = f"{apertura // 60:02d}:{apertura % 60:02d}"
            camino, tiempo_ruta = mejor_ruta_estaciones(origen, destino, self.inter_dia.get(), ap, accesible)
            if tiempo_ruta is None:
                tiempo_ruta = 0
            tiempo = espera + tiempo_ruta
        else:
            hora_min = f"{h:02d}:{m:02d}"
            camino, tiempo = mejor_ruta_estaciones(origen, destino, self.inter_dia.get(), hora_min, accesible)

        self.camino = camino
        self.tiempo_total = tiempo

        if not self.camino:
            return

        ruta_formateada = formatear_camino(self.camino)

        self.inter_ruta.config(state='normal')
        self.inter_ruta.delete('1.0', tk.END)

        if metro_cerrado:
            horas = espera // 60
            minutos = espera % 60
            if minutos == 0:
                mens_espera = f"{horas} hora{'s' if horas > 1 else ''}"
            elif horas > 0:
                mens_espera = f"{horas} hora{'s' if horas > 1 else ''} y {minutos} minuto{'s' if minutos != 1 else ''}"
            else:
                mens_espera = f"{minutos} minuto{'s' if minutos != 1 else ''}"
            self.inter_ruta.insert(tk.END, f"Esperar {mens_espera} a la apertura del metro\n\n")

        horas_total = self.tiempo_total // 60
        minutos_total = self.tiempo_total % 60

        if (horas_total == 0):
            self.inter_ruta.insert(tk.END,ruta_formateada + f"\n\nTiempo estimado: {minutos_total} minutos")
        elif (minutos_total == 0):
            self.inter_ruta.insert(tk.END, ruta_formateada + f"\n\nTiempo estimado: {horas_total} horas")
        else:
            self.inter_ruta.insert(tk.END, ruta_formateada + f"\n\nTiempo estimado: {horas_total} horas y {minutos_total} minutos")

        self.inter_ruta.config(state='disabled')

        transbordos = []

        ultima_linea = None
        for nodo in self.camino:
            estacion, linea = nodo.split("_")
            if ultima_linea is None:
                ultima_linea = linea
            elif linea != ultima_linea:
                transbordos.append(f"{estacion}{ultima_linea} -> {estacion}{linea}")
                ultima_linea = linea

        self.inter_transbordos.config(state='normal')
        self.inter_transbordos.delete('1.0', tk.END)

        if transbordos:
            self.inter_transbordos.insert(tk.END, "\n".join(transbordos))
        else:
            self.inter_transbordos.insert(tk.END, "No hay transbordos")

        self.inter_transbordos.config(state='disabled')

        # Dibujo de la ruta
        self.canvas.delete("ruta")
        self.estacion_origen = origen
        self.estacion_destino = destino
        self.dibujar_ruta()
        self.iniciar_animacion_metro()

    def dibujar_ruta(self):
        self.puntos_ruta = []
        prev_coord = None

        for nodo in self.camino:
            estacion = nodo.split("_")[0]
            if estacion not in coords_estaciones:
                continue
            x, y = coords_estaciones[estacion]
            self.puntos_ruta.append((x, y))

        for nodo in self.camino:
            estacion = nodo.split("_")[0]
            if estacion not in coords_estaciones:
                continue
            x, y = coords_estaciones[estacion]
            if prev_coord:
                self.canvas.create_line(prev_coord[0], prev_coord[1], x, y, fill="lightblue", width=3, tags="ruta")
            prev_coord = (x, y)

            if (estacion == "Tacubaya" or estacion == "Balderas" or estacion == "Zapata" or estacion == "Centro Medico" or estacion == "Mixcoac"):
                self.canvas.create_oval(x - 10.5, y - 10.5, x + 10.5, y + 10.5, fill="#3288D1", tags="ruta", outline="")
                if (estacion != self.estacion_origen and estacion != self.estacion_destino):
                    self.canvas.create_oval(x - 5.25, y - 5.25, x + 5.25, y + 5.25, fill="white", tags="ruta", outline="")
            else:
                self.canvas.create_oval(x - 7.35, y - 7.35, x + 7.35, y + 7.35, fill="#3288D1", tags="ruta", outline="")
                if (estacion != self.estacion_origen and estacion != self.estacion_destino):
                    self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="white", tags="ruta", outline="")

    def mover_tren(self):
        if self.estacion_tren >= len(self.puntos_ruta) - 1:
            return

        x_or, y_or = self.puntos_ruta[self.estacion_tren]
        x_dest, y_dest = self.puntos_ruta[self.estacion_tren + 1]

        mov_suavizados = 20
        mov_x = (x_dest - x_or) / mov_suavizados
        mov_y = (y_dest - y_or) / mov_suavizados

        self.canvas.move("tren", mov_x, mov_y)
        self.mov_suavizados += 1

        if self.mov_suavizados >= mov_suavizados:
            self.mov_suavizados = 0
            self.estacion_tren += 1

        self.anim = self.root.after(50, self.mover_tren)

if __name__ == '__main__':
    gui = metro_interfaz()
    gui.root.mainloop()