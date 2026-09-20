# Analizador Granulométrico de Suelos

Herramienta computacional orientada a la Ingeniería Civil para el procesamiento, análisis geotécnico y generación de reportes de ensayos de granulometría de suelos por tamizado, bajo especificaciones de las normas ASTM C136, ASTM D422 y ASTM D2487 (SUCS).

---

## 📋 Descripción y Usos

El **Analizador Granulométrico de Suelos** automatiza el cálculo de laboratorio y la interpretación de la distribución del tamaño de partículas de muestras de suelo.

### Funcionalidades principales:
* **Procesamiento de datos:** Cálculo automático de retenidos parciales, retenidos acumulados y porcentajes que pasan por cada tamiz.
* **Parámetros geotécnicos:** Determinación automática de los diámetros característicos ($D_{10}$, $D_{30}$, $D_{60}$) mediante interpolación semilogarítmica, y cálculo de los coeficientes de uniformidad ($C_u$) y curvatura ($C_c$).
* **Clasificación SUCS:** Asignación automática del tipo de suelo según el Sistema Unificado de Clasificación de Suelos (GW, GP, SW, SP, SM, SC, etc.) e identificación de fracciones (Grava, Arena y Finos).
* **Curva Granulométrica:** Generación interactiva de la gráfica semilogarítmica con escala X invertida (convención geotécnica) y delimitación de zonas.
* **Exportación de informes:** Generación de reportes técnicos completos en formato PDF (.pdf) con membrete y tabla de datos, e impresiones técnicas en Excel (.xlsx) con la gráfica incrustada.

---

## 💻 Requisitos del Sistema

* **Python 3.8** o superior.
* Librerías requeridas:
  * `numpy` (operaciones numéricas e interpolación logarítmica)
  * `matplotlib` (renderizado de la curva granulométrica)
  * `openpyxl` (creación y formato de libros Excel)
  * `reportlab` (generación de informes en PDF)
  * 	tkinter para la interfaz gráfica: viene incluido con Python en Windows y macOS, pero en muchas distribuciones de Linux debe instalarse aparte (ver paso 3 de la instalación).

---

## ⚙️ Instalación

1. Clona el repositorio en tu equipo local:
   ```bash
   git clone https://github.com/CbasHernandez/Analizador-Granulom-trico-.git
cd Analizador-Granulom-trico-

2. Instala las dependencias de Python
pip install numpy matplotlib openpyxl reportlab

3. Solo en Linux, instala Tkinter si tu distribución no lo trae por defecto:
sudo apt install python3-tk

4. Ejecuta el programa
python main.py


🖥️ Uso
	1.	Al abrir, la ventana carga una muestra de ejemplo (tamices, aberturas y pesos retenidos) para probar el flujo rápidamente.
	2.	Edita los datos de la muestra y de los tamices según tu ensayo, o pulsa LIMPIAR para empezar desde cero.
	3.	Pulsa CALCULAR para obtener la clasificación SUCS, los porcentajes de grava/arena/finos, los parámetros D10/D30/D60/Cu/Cc y la curva granulométrica.
	4.	Usa Exportar a PDF o Exportar a Excel para guardar el informe técnico completo.

<img width="1094" height="701" alt="Ejemplo" src="https://github.com/user-attachments/assets/daea4a3a-c4df-476f-997c-a6bb8e8cacd8" />

