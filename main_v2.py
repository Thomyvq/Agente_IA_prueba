import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import random
import numpy as np
import time

class LineFollowerApp:
    import tkinter as tk
from tkinter import ttk, messagebox
import random
import numpy as np
import time

class LineFollowerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agente Seguidor de Líneas")
        
        # Configurando el tamaño inicial de la ventana
        self.root.geometry("1200x800")
        
        self.malla = None
        self.N = 0
        self.M = 0
        self.agente = None
        self.cell_size = 40  # Tamaño de cada celda
        self.iteraciones = []
        self.numero_paso = 0  # Para numerar cada paso
        self.pasos_recorridos = []  # Lista para guardar el recorrido del agente

        # Configurar el layout principal con un frame para botones y otro para el canvas y logs
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        self.btn_frame = tk.Frame(self.main_frame)
        self.btn_frame.pack(side=tk.TOP, pady=10)
        
        # Botones
        self.btn_generar_malla = tk.Button(self.btn_frame, text="Generar Malla", command=self.generar_malla, width=20, height=2)
        self.btn_generar_malla.grid(row=0, column=0, padx=10)
        
        self.btn_inicializar_agente = tk.Button(self.btn_frame, text="Inicializar Agente", command=self.inicializar_agente, state=tk.DISABLED, width=20, height=2)
        self.btn_inicializar_agente.grid(row=0, column=1, padx=10)
        
        self.btn_iniciar_simulacion = tk.Button(self.btn_frame, text="Iniciar Simulación", command=self.iniciar_simulacion, state=tk.DISABLED, width=20, height=2)
        self.btn_iniciar_simulacion.grid(row=0, column=2, padx=10)
        
        self.btn_reiniciar = tk.Button(self.btn_frame, text="Reiniciar", command=self.reiniciar, state=tk.DISABLED, width=20, height=2)
        self.btn_reiniciar.grid(row=0, column=3, padx=10)

        # Crear el Canvas donde se dibuja la malla
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='white', width=480, height=480)  # Inicialmente 480x480, pero se ajusta dinámicamente
        self.canvas.pack()

        # Frame para tabla de resultados y tabla de movimientos
        self.log_frame = tk.Frame(self.main_frame)
        self.log_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)
        
        # Tabla de resultados usando Treeview
        self.resultados_label = tk.Label(self.log_frame, text="Resultados del Agente", font=("Helvetica", 14))
        self.resultados_label.pack(pady=5)
        
        self.tree = ttk.Treeview(self.log_frame, columns=("estadistico", "resultado", "choques", "avances", "rotaciones"), show='headings', height=10)
        self.tree.pack(pady=5)
        
        self.tree.heading("estadistico", text="Estadístico")
        self.tree.heading("resultado", text="Resultado")
        #self.tree.heading("choques", text="")
        #self.tree.heading("avances", text="")
        #self.tree.heading("rotaciones", text="")
        
        # Ajuste de columnas para visualización correcta
        self.tree.column("estadistico", width=250)
        self.tree.column("resultado", width=250)


        self.posiciones_agente = []  # Para almacenar las posiciones del agente
        self.direcciones_agente = []  # Para almacenar las direcciones del agente
        
        # Crear un Text widget para mostrar el log de movimientos
        self.log_label = tk.Label(self.log_frame, text="Registro de Movimientos", font=("Helvetica", 14))
        self.log_label.pack(pady=5)
        
        self.log_text = tk.Text(self.log_frame, height=20, width=50, wrap="word", font=("Helvetica", 10))
        self.log_text.pack(padx=5, pady=5)
        
        # Agregar scrollbars al log de movimientos
        log_scroll = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scroll.set)
        
        # Contadores de métricas
        self.contador_reglas = set()
        self.contador_choques = 0
        self.contador_avances = 0
        self.contador_rotaciones = 0
        self.iteraciones_bucle = 0
        self.retornó_inicial = False

    def generar_malla(self):
        # Genera el tamaño de la malla
        self.N = random.randint(8, 12)
        self.M = random.randint(8, 12)
        self.malla = np.zeros((self.N, self.M), dtype=int)

        # Ajustar tamaño del canvas dinámicamente según el tamaño de la malla
        canvas_width = self.M * self.cell_size
        canvas_height = self.N * self.cell_size
        self.canvas.config(width=canvas_width, height=canvas_height)
        
        # Agregar líneas oscuras (1) y paredes (2)
        for i in range(self.N):
            num_lineas = random.randint(1, self.M // 2)
            for _ in range(num_lineas):
                pos = random.randint(0, self.M - 1)
                self.malla[i][pos] = 1  # Celda oscura (línea)
        
        for _ in range(random.randint(2, 5)):  # Agregar entre 2 y 5 paredes
            pos_x = random.randint(0, self.N - 1)
            pos_y = random.randint(0, self.M - 1)
            self.malla[pos_x][pos_y] = 2  # Celda de pared

        # Habilitar el botón para inicializar el agente y reiniciar
        self.btn_inicializar_agente.config(state=tk.NORMAL)
        self.btn_reiniciar.config(state=tk.NORMAL)
        self.dibujar_malla()

    def dibujar_malla(self):
        self.canvas.delete("all")
        
        # Dibujar las celdas en el canvas
        for i in range(self.N):
            for j in range(self.M):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                if self.malla[i][j] == 1:
                    color = 'black'  # Línea oscura
                elif self.malla[i][j] == 2:
                    color = 'gray'  # Pared
                else:
                    color = 'white'  # Celda vacía
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='gray')

    def inicializar_agente(self):
        if self.malla is None:
            messagebox.showerror("Error", "Primero debe generar la malla.")
            return
        
        self.agente = AgenteSeguidorLineas(self.malla, self.N, self.M)
        self.btn_iniciar_simulacion.config(state=tk.NORMAL)
        self.numero_paso = 0  # Iniciar la numeración desde cero
        self.pasos_recorridos.clear()  # Limpiar los pasos anteriores
        self.dibujar_agente()

    def dibujar_agente(self):
        if self.agente:
            x, y = self.agente.pos_x, self.agente.pos_y
            # Dibujar el agente en la celda actual
            self.canvas.create_rectangle(
                y * self.cell_size + 5, x * self.cell_size + 5,
                (y + 1) * self.cell_size - 5, (x + 1) * self.cell_size - 5,
                fill='red'
            )

    def generar_malla(self):
        self.N = random.randint(8, 12)
        self.M = random.randint(8, 12)
        self.malla = np.zeros((self.N, self.M), dtype=int)

        # Agregar líneas oscuras (1)
        for i in range(self.N):
            num_lineas = random.randint(1, self.M // 2)
            for _ in range(num_lineas):
                pos = random.randint(0, self.M - 1)
                self.malla[i][pos] = 1  # Celda oscura (línea)

        # Agregar paredes representadas por 2
        for _ in range(random.randint(2, 5)):  # Agregar entre 2 y 5 paredes
            pos_x = random.randint(0, self.N - 1)
            pos_y = random.randint(0, self.M - 1)
            self.malla[pos_x][pos_y] = 2  # Celda de pared

        self.btn_inicializar_agente.config(state=tk.NORMAL)
        self.btn_reiniciar.config(state=tk.NORMAL)
        self.dibujar_malla()
    
    def dibujar_malla(self):
        self.canvas.delete("all")
        
        # Dibujar recorrido anterior (líneas punteadas)
        for paso in self.pasos_recorridos:
            x, y = paso
            self.canvas.create_oval(
                y * self.cell_size + 15, x * self.cell_size + 15,
                y * self.cell_size + 25, x * self.cell_size + 25,
                outline='blue', width=2
            )
        
        for i in range(self.N):
            for j in range(self.M):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                if self.malla[i][j] == 1:
                    color = 'black'  # Línea
                elif self.malla[i][j] == 2:
                    color = 'gray'  # Pared
                else:
                    color = 'white'  # Espacio vacío
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='gray')
    
    def inicializar_agente(self):
        if self.malla is None:
            messagebox.showerror("Error", "Primero debe generar la malla.")
            return
        
        self.agente = AgenteSeguidorLineas(self.malla, self.N, self.M)
        self.btn_iniciar_simulacion.config(state=tk.NORMAL)
        self.numero_paso = 0  # Iniciar la numeración desde cero
        self.pasos_recorridos.clear()  # Limpiar los pasos anteriores
        self.log_text.delete(1.0, tk.END)  # Limpiar el registro de movimientos
        self.tree.delete(*self.tree.get_children())  # Limpiar la tabla de resultados
        self.contador_reglas.clear()
        self.contador_choques = 0
        self.contador_avances = 0
        self.contador_rotaciones = 0
        self.iteraciones_bucle = 0
        self.retornó_inicial = False
        self.posiciones_agente.clear()
        self.direcciones_agente.clear()
        self.agente.pos_inicial = (self.agente.pos_x, self.agente.pos_y)
        self.dibujar_agente()
        
    def dibujar_agente(self):
        # Dibujar el agente en el canvas
        if self.agente:
            x, y = self.agente.pos_x, self.agente.pos_y
            # Dibujar un cuadrado para el cuerpo del agente
            self.canvas.create_rectangle(
                y * self.cell_size + 5, x * self.cell_size + 5, 
                (y + 1) * self.cell_size - 5, (x + 1) * self.cell_size - 5, 
                fill='red'
            )
            # Dibujar un pequeño rectángulo en la parte superior para mostrar la "cabeza"
            if self.agente.direccion == 'Norte':
                self.canvas.create_rectangle(
                    y * self.cell_size + 15, x * self.cell_size + 5, 
                    y * self.cell_size + 25, x * self.cell_size + 15, 
                    fill='yellow'
                )
            elif self.agente.direccion == 'Sur':
                self.canvas.create_rectangle(
                    y * self.cell_size + 15, (x + 1) * self.cell_size - 15, 
                    y * self.cell_size + 25, (x + 1) * self.cell_size - 5, 
                    fill='yellow'
                )
            elif self.agente.direccion == 'Este':
                self.canvas.create_rectangle(
                    (y + 1) * self.cell_size - 15, x * self.cell_size + 15, 
                    (y + 1) * self.cell_size - 5, x * self.cell_size + 25, 
                    fill='yellow'
                )
            elif self.agente.direccion == 'Oeste':
                self.canvas.create_rectangle(
                    y * self.cell_size + 5, x * self.cell_size + 15, 
                    y * self.cell_size + 15, x * self.cell_size + 25, 
                    fill='yellow'
                )
            # Mostrar el número del paso dentro del agente
            self.canvas.create_text(
                y * self.cell_size + self.cell_size // 2, 
                x * self.cell_size + self.cell_size // 2, 
                text=str(self.numero_paso), fill='white', font=("Helvetica", 12)
            )
    
    def iniciar_simulacion(self):
        self.iteraciones.clear()
        self.log_text.delete(1.0, tk.END)
        self.posiciones_agente.clear()  # Limpiar las posiciones almacenadas
        self.direcciones_agente.clear()  # Limpiar las direcciones almacenadas
        self.pasos_recorridos.clear()
        self.numero_paso = 0
        self.contador_reglas.clear()
        self.contador_choques = 0
        self.contador_avances = 0
        self.contador_rotaciones = 0
        self.iteraciones_bucle = 0
        self.retornó_inicial = False
        self.dibujar_malla()
        self.dibujar_agente()
        self.log_movimiento(header=True)  # Insertar encabezado en el log
        
        # Simulación en bucle con pausa para ver los movimientos paso a paso
        for i in range(1000):  # Aumentar el límite para detectar bucles
            self.agente.mover()
            self.numero_paso += 1
            self.log_movimiento()
            self.pasos_recorridos.append((self.agente.pos_x, self.agente.pos_y))  # Guardar la posición
            self.dibujar_malla()  # Redibujar la malla con recorrido
            self.dibujar_agente()  # Dibujar el agente con el número del paso
            self.posiciones_agente.append((self.agente.pos_x, self.agente.pos_y))
            self.direcciones_agente.append(self.agente.direccion)
            self.dibujar_ruta()
            self.root.update()  # Actualizar la interfaz
            time.sleep(0.1)  # Pausar 0.1 segundos entre movimientos
            
            # Actualizar contadores
            if self.agente.regla_aplicada:
                self.contador_reglas.add(self.agente.regla_aplicada)
            if self.agente.accion == 'Avanzar':
                self.contador_avances += 1
            elif self.agente.accion.startswith('Girar'):
                self.contador_rotaciones += 1
            if self.agente.choco:
                self.contador_choques += 1
                self.agente.choco = False  # Resetear el estado de choque
            
            # Verificar si ha retornado a la posición inicial
            if (self.agente.pos_x, self.agente.pos_y) == self.agente.pos_inicial and self.numero_paso != 0:
                self.retornó_inicial = True
                break
            
            # Verificar si ha entrado en un bucle
            if self.chequear_bucle():
                self.iteraciones_bucle = self.numero_paso
                break
        
        # Calcular desempeño
        total_acciones = self.contador_avances + self.contador_rotaciones
        if total_acciones > 0:
            desempeño = self.contador_avances / total_acciones
        else:
            desempeño = 0.0
        
        # Insertar resultados en la tabla
        resultados = [
            ("Número de reglas usadas", len(self.contador_reglas)),
            ("Número de choques con paredes u obstáculos", self.contador_choques),
            ("Número de avances realizados", self.contador_avances),
            ("Número de rotaciones realizadas", self.contador_rotaciones),
            ("Desempeño del agente (Avances/Total Acciones)", f"{desempeño:.2f}"),
            ("¿Retornó a la posición inicial?", "Sí" if self.retornó_inicial else "No"),
            ("Número de iteraciones hasta bucle infinito", self.iteraciones_bucle if self.iteraciones_bucle else "No detectado"),
            ("Complejidad del agente (O(N*M))", f"O({self.N}*{self.M})"),
            ("Cálculo de bucle infinito", "Detección basada en repetición de estados" if self.iteraciones_bucle else "No entró en bucle")
        ]
        
        for métrica, valor in resultados:
            self.tree.insert("", "end", values=(métrica, valor))
        
        messagebox.showinfo("Simulación Finalizada", "La simulación ha terminado. Revisa los resultados en la tabla.")
    
    def log_movimiento(self, header=False):
        # Validar si el widget Text existe
        if self.log_text.winfo_exists():
            headers = "{:<15} {:<30} {:<20} {:<20} {:<15}".format(
                "Pos. Inicial", "Percepciones", "Regla", "Acción", "Pos. Final")
            if self.numero_paso == 0 and header:
                self.log_text.insert(tk.END, headers + "\n" + "-" * 100 + "\n")
            
            pos_inicial = f"({self.agente.pos_inicial[0]}, {self.agente.pos_inicial[1]})" if self.numero_paso == 0 else f"({self.agente.prev_pos_x}, {self.agente.prev_pos_y})"
            percepciones = f"Cam. Principal: {self.agente.percepcion_camara_principal()}, " \
                           f"Cam. Frontal: {self.agente.percepcion_camara_frontal()}"
            regla = self.agente.regla_aplicada if self.agente.regla_aplicada else "N/A"
            accion = self.agente.accion if self.agente.accion else "N/A"
            pos_final = f"({self.agente.pos_x}, {self.agente.pos_y})"
            
            row = "{:<15} {:<30} {:<20} {:<20} {:<15}".format(
                pos_inicial, percepciones, regla, accion, pos_final)
            
            self.log_text.insert(tk.END, row + "\n")
    
    def chequear_bucle(self):
        # Verificar si el agente ha repetido un estado anterior
        estado_actual = (self.agente.pos_x, self.agente.pos_y, self.agente.direccion)
        if estado_actual in self.iteraciones:
            return True
        self.iteraciones.append(estado_actual)
        return False
            
    def dibujar_ruta(self):
        if len(self.pasos_recorridos) > 1:
            for i in range(len(self.pasos_recorridos) - 1):
                x1, y1 = self.pasos_recorridos[i][1] * self.cell_size + self.cell_size // 2, self.pasos_recorridos[i][0] * self.cell_size + self.cell_size // 2
                x2, y2 = self.pasos_recorridos[i + 1][1] * self.cell_size + self.cell_size // 2, self.pasos_recorridos[i + 1][0] * self.cell_size + self.cell_size // 2
                
                # Dibujar línea punteada
                self.canvas.create_line(x1, y1, x2, y2, dash=(2, 2), fill='blue')
    
    def reiniciar(self):
        self.malla = None
        self.N = 0
        self.M = 0
        self.agente = None
        self.iteraciones.clear()
        self.pasos_recorridos.clear()
        self.posiciones_agente.clear()
        self.direcciones_agente.clear()
        self.contador_reglas.clear()
        self.contador_choques = 0
        self.contador_avances = 0
        self.contador_rotaciones = 0
        self.iteraciones_bucle = 0
        self.retornó_inicial = False
        self.btn_inicializar_agente.config(state=tk.DISABLED)
        self.btn_reiniciar.config(state=tk.DISABLED)
        self.btn_iniciar_simulacion.config(state=tk.DISABLED)
        self.canvas.delete("all")
        self.log_text.delete(1.0, tk.END)
        self.tree.delete(*self.tree.get_children())  # Limpiar la tabla de resultados

# Clase del agente seguidor de líneas
class AgenteSeguidorLineas:
    def __init__(self, malla, N, M):
        self.malla = malla
        self.N = N
        self.M = M
        self.pos_x = random.randint(0, self.N - 1)  # Posición inicial
        self.pos_y = random.randint(0, self.M - 1)
        self.direccion = random.choice(['Norte', 'Sur', 'Este', 'Oeste'])
        self.regla_aplicada = ''
        self.accion = ''
        self.choco = False  # Variable para recordar el choque
        self.pos_inicial = (self.pos_x, self.pos_y)
        self.prev_pos_x = self.pos_x
        self.prev_pos_y = self.pos_y
    
    def percepcion_orientacion(self):
        return self.direccion
    
    def percepcion_contacto(self):
        # Detectar contacto con las paredes
        if self.direccion == 'Norte' and self.pos_x == 0:
            return 'Contacto'
        if self.direccion == 'Sur' and self.pos_x == self.N - 1:
            return 'Contacto'
        if self.direccion == 'Este' and self.pos_y == self.M - 1:
            return 'Contacto'
        if self.direccion == 'Oeste' and self.pos_y == 0:
            return 'Contacto'
        # Verificar colisiones con celdas de paredes (representadas por 2)
        if self.direccion == 'Norte' and self.malla[self.pos_x - 1][self.pos_y] == 2:
            return 'Contacto'
        if self.direccion == 'Sur' and self.malla[self.pos_x + 1][self.pos_y] == 2:
            return 'Contacto'
        if self.direccion == 'Este' and self.malla[self.pos_x][self.pos_y + 1] == 2:
            return 'Contacto'
        if self.direccion == 'Oeste' and self.malla[self.pos_x][self.pos_y - 1] == 2:
            return 'Contacto'
        return 'No Contacto'
    
    def percepcion_camara_principal(self):
        if self.malla[self.pos_x][self.pos_y] == 1:
            return 'Piso Oscuro'
        return 'Piso Claro'
    
    def percepcion_camara_frontal(self):
        # Simulación de percepciones de cámara frontal
        # Aquí puedes implementar una lógica más detallada según tus necesidades
        percepciones = {'Izquierda': 'Borde', 'Centro': 'Borde', 'Derecha': 'Borde'}
        return percepciones
    
    def mover(self):
        self.prev_pos_x = self.pos_x
        self.prev_pos_y = self.pos_y
        percepciones = self.percepcion_camara_frontal()
        contacto = self.percepcion_contacto()
        
        if contacto == 'Contacto':
            self.choco = True
            self.regla_aplicada = 'Choque'
            self.girar_derecha()
            self.accion = 'Girar +90'
        else:
            # Aplicar regla de movimiento
            self.avanzar()
            self.accion = 'Avanzar'
    
    def avanzar(self):
        if self.direccion == 'Norte':
            self.pos_x -= 1
        elif self.direccion == 'Sur':
            self.pos_x += 1
        elif self.direccion == 'Este':
            self.pos_y += 1
        elif self.direccion == 'Oeste':
            self.pos_y -= 1
    
    def girar_derecha(self):
        if self.direccion == 'Norte':
            self.direccion = 'Este'
        elif self.direccion == 'Este':
            self.direccion = 'Sur'
        elif self.direccion == 'Sur':
            self.direccion = 'Oeste'
        elif self.direccion == 'Oeste':
            self.direccion = 'Norte'
    
    def girar_izquierda(self):
        if self.direccion == 'Norte':
            self.direccion = 'Oeste'
        elif self.direccion == 'Oeste':
            self.direccion = 'Sur'
        elif self.direccion == 'Sur':
            self.direccion = 'Este'
        elif self.direccion == 'Este':
            self.direccion = 'Norte'

# Iniciar la aplicación
root = tk.Tk()
app = LineFollowerApp(root)
root.mainloop()
