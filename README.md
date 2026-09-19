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

---

## ⚙️ Instalación

1. Clona el repositorio en tu equipo local:
   ```bash
   git clone [https://github.com/CbasHernandez/Analizador-Granulom-trico-.git](https://github.com/CbasHernandez/Analizador-Granulom-trico-.git)
   cd Analizador-Granulom-trico-# Analizador-Granulom-trico-

![Ejemplo del Analizador](nombre_de_tu_imagen.png)
