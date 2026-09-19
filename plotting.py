"""
Módulo de visualización y generación de la curva granulométrica de suelos
utilizando Matplotlib según las convenciones de la Ingeniería Geotécnica.
"""

from typing import Optional
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

from models import ResultadoGranulometria


def generar_figura_curva_granulometrica(
    resultado: ResultadoGranulometria,
    figsize=(8.5, 5.5),
    dpi=120,
    mostrar_zonas: bool = True,
    eje_invertido: bool = True
) -> Figure:
    """
    Genera un objeto Figure de Matplotlib con la curva granulométrica semilogarítmica.

    Parámetros:
    - resultado: Instancia de ResultadoGranulometria con datos calculados.
    - figsize: Dimensiones de la figura en pulgadas.
    - dpi: Resolución de la figura.
    - mostrar_zonas: Si es True, colorea y etiqueta las zonas de Grava, Arenas y Finos.
    - eje_invertido: Si es True, el eje X va de mayor a menor diámetro (estándar geotécnico).
    """
    # Usar estilo limpio y profesional
    fig = Figure(figsize=figsize, dpi=dpi, tight_layout=True)
    ax = fig.add_subplot(111)

    # Filtrar puntos con abertura > 0 para escala logarítmica
    puntos_tamices = [
        (f.tamiz, f.abertura_mm, f.porcentaje_pasa)
        for f in resultado.tabla if f.abertura_mm > 0
    ]

    if not puntos_tamices:
        ax.text(0.5, 0.5, "No hay datos de tamices para graficar",
                ha="center", va="center", transform=ax.transAxes, fontsize=12)
        return fig

    # Ordenar por abertura descendente
    puntos_tamices.sort(key=lambda p: p[1], reverse=True)

    nombres = [p[0] for p in puntos_tamices]
    aberturas = np.array([p[1] for p in puntos_tamices])
    pasas = np.array([p[2] for p in puntos_tamices])

    # Definir límites del eje X
    max_abertura = max(aberturas)
    min_abertura = min(aberturas)

    # Establecer límites redondeados a décadas completas
    x_max = 10 ** (np.ceil(np.log10(max(max_abertura * 1.5, 10.0))))
    x_min = 10 ** (np.floor(np.log10(min(min_abertura * 0.5, 0.05))))

    # Configuración del eje X logarítmico
    ax.set_xscale('log')
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0, 105)

    if eje_invertido:
        # Convención geotécnica internacional: Partículas gruesas a la izquierda, finas a la derecha
        ax.set_xlim(x_max, x_min)

    # Cuadrícula semilogarítmica completa (mayor y menor)
    ax.grid(True, which='major', color='#999999', linestyle='-', linewidth=0.8, alpha=0.7)
    ax.grid(True, which='minor', color='#d5d5d5', linestyle=':', linewidth=0.5, alpha=0.6)

    # Zonas de clasificación de suelos según ASTM D2487 (Grava, Arena Gruesa/Media/Fina, Finos)
    if mostrar_zonas:
        # Límites en mm:
        # Finos: < 0.075 mm
        # Arena Fina: 0.075 - 0.425 mm
        # Arena Media: 0.425 - 2.0 mm
        # Arena Gruesa: 2.0 - 4.75 mm
        # Grava: 4.75 - 75.0 mm
        zonas = [
            ("FINOS\n(Limos/Arcillas)", x_min, 0.075, "#fff2df"),
            ("A. Fina", 0.075, 0.425, "#e8f4f8"),
            ("A. Media", 0.425, 2.00, "#d4edf4"),
            ("A. Gruesa", 2.00, 4.75, "#bfe3ef"),
            ("GRAVA", 4.75, x_max, "#e2eed8")
        ]

        for nombre_zona, lim_inf, lim_sup, color in zonas:
            if lim_sup > x_min and lim_inf < x_max:
                x0 = max(lim_inf, x_min)
                x1 = min(lim_sup, x_max)
                if x0 < x1:
                    ax.axvspan(x0, x1, ymin=0.92, ymax=1.0, color=color, alpha=0.85, zorder=1)
                    ax.axvline(x=lim_sup, color='#777777', linestyle='--', linewidth=0.7, alpha=0.5, zorder=2)
                    x_centro = np.sqrt(x0 * x1)
                    ax.text(x_centro, 96, nombre_zona, ha='center', va='center',
                            fontsize=7.5, fontweight='bold', color='#333333', zorder=3)

    # Curva granulométrica principal
    ax.plot(aberturas, pasas, color='#0052cc', linewidth=2.2,
            marker='o', markersize=6, markerfacecolor='#003366',
            markeredgecolor='white', markeredgewidth=1.2,
            label=f'Curva Muestra {resultado.datos_muestra.id_muestra}', zorder=4)

    # Anotaciones de tamices principales en los puntos
    for nom, d, p in zip(nombres, aberturas, pasas):
        # Mostrar etiquetas de tamices comunes
        if nom in ['3"', '1 1/2"', '3/4"', '3/8"', '#4', '#10', '#20', '#40', '#60', '#100', '#200']:
            desplazamiento_y = 5 if p < 90 else -12
            ax.annotate(nom, (d, p), textcoords="offset points",
                        xytext=(0, desplazamiento_y), ha='center',
                        fontsize=7.5, color='#172b4d', fontweight='bold', zorder=5)

    # Resaltar D10, D30 y D60 si están disponibles
    parametros_d = [
        (resultado.d10, 10, 'D10', '#d9381e'),
        (resultado.d30, 30, 'D30', '#e67e22'),
        (resultado.d60, 60, 'D60', '#27ae60')
    ]

    for d_val, p_val, d_nombre, color in parametros_d:
        if d_val is not None and x_min <= d_val <= x_max:
            # Línea horizontal desde el eje Y hasta la curva
            ax.axhline(y=p_val, color=color, linestyle=':', linewidth=1.1, alpha=0.85, zorder=3)
            # Línea vertical desde la curva hasta el eje X
            ax.vlines(x=d_val, ymin=0, ymax=p_val, color=color, linestyle='--', linewidth=1.2, alpha=0.85, zorder=3)
            # Punto sobre la curva
            ax.plot(d_val, p_val, marker='s', markersize=6, color=color, zorder=5)
            # Etiqueta
            ax.text(d_val, p_val + 2.5, f"{d_nombre}={d_val:.3f} mm",
                    ha='center', va='bottom', fontsize=8, color=color,
                    fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=color, alpha=0.9))

    # Títulos y etiquetas de ejes
    ax.set_title(
        f"CURVA GRANULOMÉTRICA DE SUELOS (ASTM D422 / ASTM D6913)\n"
        f"Muestra: {resultado.datos_muestra.id_muestra} | "
        f"Proyecto: {resultado.datos_muestra.proyecto}",
        fontsize=11, fontweight='bold', pad=12, color='#172b4d'
    )
    ax.set_xlabel("Diámetro de las partículas / Abertura de malla (mm) [Escala Logarítmica]",
                  fontsize=10, fontweight='bold', labelpad=8, color='#172b4d')
    ax.set_ylabel("Porcentaje que pasa (%)", fontsize=10, fontweight='bold', labelpad=8, color='#172b4d')

    # Cuadro resumen con parámetros geotécnicos dentro de la gráfica
    cu_txt = f"{resultado.cu:.2f}" if resultado.cu is not None else "N/D"
    cc_txt = f"{resultado.cc:.2f}" if resultado.cc is not None else "N/D"
    resumen_text = (
        f"PARÁMETROS:\n"
        f"Grava: {resultado.porcentaje_grava:.1f}%\n"
        f"Arena: {resultado.porcentaje_arena:.1f}%\n"
        f"Finos: {resultado.porcentaje_finos:.1f}%\n"
        f"Cu = {cu_txt}\n"
        f"Cc = {cc_txt}\n"
        f"SUCS: {resultado.clasificacion_sucs}"
    )

    # Posicionar cuadro según dirección de eje
    loc_x = 0.03 if not eje_invertido else 0.77
    ax.text(loc_x, 0.12, resumen_text, transform=ax.transAxes,
            fontsize=8.5, family='monospace', verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#f8f9fa', edgecolor='#b0bec5', alpha=0.95),
            zorder=6)

    # Leyenda
    ax.legend(loc='lower left' if eje_invertido else 'lower right', fontsize=8.5, framealpha=0.9)

    return fig
