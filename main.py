"""
Módulo principal (Punto de entrada) para el Analizador Granulométrico.
Proporciona la interfaz gráfica de usuario (GUI) utilizando Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Importar los módulos de tu backend
from models import Tamiz, DatosMuestra
from calculator import CalculadorGranulometria
from plotting import generar_figura_curva_granulometrica
from exporter import ExportadorGranulometria
from standard_sieves import obtener_serie_propuesta_ejemplo

class AnalizadorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Granulométrico de Suelos")
        self.root.geometry("1100x700")
        self.root.minsize(1000, 650)
        
        self.resultado_actual = None
        self.figura_actual = None

        self._crear_interfaz()
        self._cargar_datos_defecto()

    def _crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ================= PANEL IZQUIERDO (Datos) =================
        left_panel = ttk.Frame(main_frame, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # --- Metadatos ---
        frame_meta = ttk.LabelFrame(left_panel, text="Datos de la Muestra", padding="10")
        frame_meta.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_meta, text="ID Muestra:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ent_id = ttk.Entry(frame_meta, width=25)
        self.ent_id.grid(row=0, column=1, pady=2, padx=5)

        ttk.Label(frame_meta, text="Proyecto:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ent_proyecto = ttk.Entry(frame_meta, width=25)
        self.ent_proyecto.grid(row=1, column=1, pady=2, padx=5)

        ttk.Label(frame_meta, text="Peso Total (g):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.ent_peso_total = ttk.Entry(frame_meta, width=25)
        self.ent_peso_total.grid(row=2, column=1, pady=2, padx=5)

        # --- Tabla de Tamices (Entradas) ---
        frame_tamices = ttk.LabelFrame(left_panel, text="Datos del Tamizado", padding="10")
        frame_tamices.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Encabezados de la tabla
        ttk.Label(frame_tamices, text="Tamiz", font=('Helvetica', 9, 'bold')).grid(row=0, column=0, padx=2)
        ttk.Label(frame_tamices, text="Abertura (mm)", font=('Helvetica', 9, 'bold')).grid(row=0, column=1, padx=2)
        ttk.Label(frame_tamices, text="Retenido (g)", font=('Helvetica', 9, 'bold')).grid(row=0, column=2, padx=2)

        self.filas_entradas = []
        # Crear 10 filas para ingresar tamices
        for i in range(1, 11):
            ent_nom = ttk.Entry(frame_tamices, width=10)
            ent_nom.grid(row=i, column=0, pady=2, padx=2)
            
            ent_ab = ttk.Entry(frame_tamices, width=12)
            ent_ab.grid(row=i, column=1, pady=2, padx=2)
            
            ent_ret = ttk.Entry(frame_tamices, width=12)
            ent_ret.grid(row=i, column=2, pady=2, padx=2)
            
            self.filas_entradas.append((ent_nom, ent_ab, ent_ret))

        # --- Botones de Acción ---
        frame_botones = ttk.Frame(left_panel)
        frame_botones.pack(fill=tk.X)

        btn_calcular = ttk.Button(frame_botones, text="CALCULAR", command=self.procesar_calculo)
        btn_calcular.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        btn_limpiar = ttk.Button(frame_botones, text="LIMPIAR", command=self.limpiar_datos)
        btn_limpiar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))


        # ================= PANEL DERECHO (Resultados y Gráfica) =================
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Resultados Numéricos ---
        frame_resultados = ttk.LabelFrame(right_panel, text="Resultados Geotécnicos", padding="10")
        frame_resultados.pack(fill=tk.X, pady=(0, 10))

        self.lbl_sucs = ttk.Label(frame_resultados, text="Clasificación SUCS: -", font=('Helvetica', 11, 'bold'), foreground="#1B365D")
        self.lbl_sucs.pack(anchor=tk.W)
        
        self.lbl_desc = ttk.Label(frame_resultados, text="Descripción: -", wraplength=600)
        self.lbl_desc.pack(anchor=tk.W, pady=(5, 10))

        # Sub-panel para fracciones y parámetros
        sub_res = ttk.Frame(frame_resultados)
        sub_res.pack(fill=tk.X)
        
        self.lbl_fracciones = ttk.Label(sub_res, text="Grava: -% | Arena: -% | Finos: -%", font=('Helvetica', 10))
        self.lbl_fracciones.pack(side=tk.LEFT)
        
        self.lbl_parametros = ttk.Label(sub_res, text="Cu: - | Cc: -", font=('Helvetica', 10))
        self.lbl_parametros.pack(side=tk.RIGHT)

        # --- Área de Gráfica ---
        self.frame_grafica = ttk.LabelFrame(right_panel, text="Curva Granulométrica", padding="5")
        self.frame_grafica.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # --- Botones de Exportación ---
        frame_exportar = ttk.Frame(right_panel)
        frame_exportar.pack(fill=tk.X)

        self.btn_pdf = ttk.Button(frame_exportar, text="Exportar a PDF", command=self.exportar_pdf, state=tk.DISABLED)
        self.btn_pdf.pack(side=tk.RIGHT, padx=(5, 0))

        self.btn_excel = ttk.Button(frame_exportar, text="Exportar a Excel", command=self.exportar_excel, state=tk.DISABLED)
        self.btn_excel.pack(side=tk.RIGHT)

    def _cargar_datos_defecto(self):
        """Carga los datos de ejemplo del documento en la interfaz."""
        self.ent_id.insert(0, "Muestra-01")
        self.ent_proyecto.insert(0, "Proyecto Ejemplo de Clase")
        self.ent_peso_total.insert(0, "550.0")

        tamices_ejemplo = obtener_serie_propuesta_ejemplo()
        for i, tamiz in enumerate(tamices_ejemplo):
            if i < len(self.filas_entradas):
                nom, ab, ret = self.filas_entradas[i]
                nom.insert(0, tamiz.nombre)
                ab.insert(0, str(tamiz.abertura_mm))
                ret.insert(0, str(tamiz.peso_retenido_g))

    def limpiar_datos(self):
        """Limpia todos los campos de entrada."""
        self.ent_id.delete(0, tk.END)
        self.ent_proyecto.delete(0, tk.END)
        self.ent_peso_total.delete(0, tk.END)
        for nom, ab, ret in self.filas_entradas:
            nom.delete(0, tk.END)
            ab.delete(0, tk.END)
            ret.delete(0, tk.END)

    def procesar_calculo(self):
        """Lee los datos de la interfaz, calcula y muestra los resultados."""
        try:
            # 1. Recopilar metadatos
            peso_txt = self.ent_peso_total.get()
            peso_total = float(peso_txt) if peso_txt.strip() else None

            datos_muestra = DatosMuestra(
                id_muestra=self.ent_id.get() or "M-01",
                proyecto=self.ent_proyecto.get() or "Sin Proyecto",
                peso_total_especificado=peso_total
            )

            # 2. Recopilar tamices de la tabla
            lista_tamices = []
            for nom_ent, ab_ent, ret_ent in self.filas_entradas:
                nom = nom_ent.get().strip()
                ab_txt = ab_ent.get().strip()
                ret_txt = ret_ent.get().strip()
                
                if nom and ab_txt and ret_txt:
                    lista_tamices.append(Tamiz(
                        nombre=nom, 
                        abertura_mm=float(ab_txt), 
                        peso_retenido_g=float(ret_txt)
                    ))

            if not lista_tamices:
                messagebox.showwarning("Advertencia", "No se ingresaron tamices válidos.")
                return

            # 3. Calcular usando el backend
            self.resultado_actual = CalculadorGranulometria.calcular(lista_tamices, datos_muestra)

            # 4. Actualizar textos en la interfaz
            self.lbl_sucs.config(text=f"Clasificación SUCS: {self.resultado_actual.clasificacion_sucs}")
            self.lbl_desc.config(text=f"Descripción: {self.resultado_actual.descripcion_suelo}")
            self.lbl_fracciones.config(
                text=f"Grava: {self.resultado_actual.porcentaje_grava:.2f}% | "
                     f"Arena: {self.resultado_actual.porcentaje_arena:.2f}% | "
                     f"Finos: {self.resultado_actual.porcentaje_finos:.2f}%"
            )
            
            cu_str = f"{self.resultado_actual.cu:.2f}" if self.resultado_actual.cu else "N/D"
            cc_str = f"{self.resultado_actual.cc:.2f}" if self.resultado_actual.cc else "N/D"
            self.lbl_parametros.config(text=f"Cu: {cu_str} | Cc: {cc_str}")

            # Mostrar advertencias si hay pérdida de peso
            if self.resultado_actual.advertencias:
                advertencias_texto = "\n".join(self.resultado_actual.advertencias)
                messagebox.showinfo("Observación de Ensayo", advertencias_texto)

            # 5. Generar e incrustar la gráfica en la interfaz
            self.actualizar_grafica()

            # Habilitar botones de exportación
            self.btn_pdf.config(state=tk.NORMAL)
            self.btn_excel.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error de Cálculo", f"Verifique los datos ingresados.\nDetalle: {str(e)}")

    def actualizar_grafica(self):
        """Genera la figura de Matplotlib y la inserta en Tkinter."""
        # Limpiar gráfica anterior si existe
        for widget in self.frame_grafica.winfo_children():
            widget.destroy()

        # Generar figura usando tu módulo plotting.py
        self.figura_actual = generar_figura_curva_granulometrica(
            self.resultado_actual, 
            figsize=(7.5, 4.5), 
            dpi=100
        )
        
        # Incrustar en Tkinter
        canvas = FigureCanvasTkAgg(self.figura_actual, master=self.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def exportar_excel(self):
        if not self.resultado_actual:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel", "*.xlsx")],
            title="Guardar Informe Excel"
        )
        if filepath:
            try:
                ExportadorGranulometria.exportar_excel(self.resultado_actual, filepath)
                messagebox.showinfo("Éxito", "Archivo Excel generado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar a Excel:\n{str(e)}")

    def exportar_pdf(self):
        if not self.resultado_actual:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar Informe PDF"
        )
        if filepath:
            try:
                ExportadorGranulometria.exportar_pdf(self.resultado_actual, filepath)
                messagebox.showinfo("Éxito", "Archivo PDF generado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar a PDF:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnalizadorGUI(root)
    root.mainloop()