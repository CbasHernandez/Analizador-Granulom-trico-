"""
Módulo de cálculo granulométrico de suelos según normas ASTM C136, ASTM D422 y ASTM D2487 (SUCS).
"""

import math
from typing import List, Optional, Tuple
import numpy as np

from models import Tamiz, FilaGranulometria, DatosMuestra, ResultadoGranulometria


class CalculadorGranulometria:
    """Motor de cálculo y análisis geotécnico para ensayos granulométricos."""

    @staticmethod
    def calcular(tamices: List[Tamiz], datos_muestra: Optional[DatosMuestra] = None) -> ResultadoGranulometria:
        """
        Realiza todos los cálculos granulométricos a partir de la lista de tamices.
        """
        if datos_muestra is None:
            datos_muestra = DatosMuestra()

        advertencias: List[str] = []

        # Ordenar tamices de mayor a menor abertura (el Fondo con abertura 0.0 va al final)
        tamices_ordenados = sorted(tamices, key=lambda t: t.abertura_mm, reverse=True)

        # Suma de pesos retenidos en los tamices
        peso_total_retenido = sum(t.peso_retenido_g for t in tamices_ordenados)

        if peso_total_retenido <= 0:
            raise ValueError("El peso total retenido debe ser mayor que cero.")

        # Determinar peso total de la muestra
        if datos_muestra.peso_total_especificado is not None and datos_muestra.peso_total_especificado > 0:
            peso_total_muestra = datos_muestra.peso_total_especificado
            perdida_peso = abs(peso_total_muestra - peso_total_retenido)
            pct_perdida = (perdida_peso / peso_total_muestra) * 100.0

            # Validación de pérdida según normas ASTM
            if pct_perdida > 1.0:
                advertencias.append(
                    f"Advertencia: La diferencia entre el peso total y la suma de retenidos es de "
                    f"{perdida_peso:.2f} g ({pct_perdida:.2f}%). La norma ASTM C136/D6913 recomienda "
                    f"que no exceda el 1.0% para ensayos de alta precisión."
                )
        else:
            peso_total_muestra = peso_total_retenido
            perdida_peso = 0.0
            pct_perdida = 0.0

        # Cálculo de porcentajes por tamiz
        filas: List[FilaGranulometria] = []
        peso_acumulado = 0.0
        pct_acumulado = 0.0

        for idx, t in enumerate(tamices_ordenados):
            peso_acumulado += t.peso_retenido_g
            pct_retenido = (t.peso_retenido_g / peso_total_muestra) * 100.0
            pct_acumulado = (peso_acumulado / peso_total_muestra) * 100.0

            # Asegurar que el retenido acumulado no supere 100% numéricamente
            if pct_acumulado > 100.0:
                pct_acumulado = 100.0

            pct_pasa = 100.0 - pct_acumulado
            if pct_pasa < 0.0:
                pct_pasa = 0.0

            # Si es el último y es el fondo, forzar pasa = 0%
            if t.abertura_mm == 0.0 or idx == len(tamices_ordenados) - 1:
                pct_pasa = 0.0
                pct_acumulado = 100.0

            filas.append(FilaGranulometria(
                tamiz=t.nombre,
                abertura_mm=t.abertura_mm,
                peso_retenido_g=t.peso_retenido_g,
                porcentaje_retenido=pct_retenido,
                porcentaje_retenido_acumulado=pct_acumulado,
                porcentaje_pasa=pct_pasa
            ))

        # Fracciones granulométricas de suelo (ASTM D2487):
        # Tamiz #4: 4.75 mm (Límite Grava / Arena)
        # Tamiz #200: 0.075 mm (Límite Arena / Finos)
        # Tamiz #10: 2.00 mm (Límite Arena gruesa / Arena media)
        # Tamiz #40: 0.425 mm (Límite Arena media / Arena fina)
        pasa_tamiz_4 = CalculadorGranulometria._obtener_o_interpolar_pasa(filas, 4.75)
        pasa_tamiz_200 = CalculadorGranulometria._obtener_o_interpolar_pasa(filas, 0.075)
        pasa_tamiz_10 = CalculadorGranulometria._obtener_o_interpolar_pasa(filas, 2.00)
        pasa_tamiz_40 = CalculadorGranulometria._obtener_o_interpolar_pasa(filas, 0.425)

        pct_grava = max(0.0, 100.0 - pasa_tamiz_4)
        pct_finos = max(0.0, pasa_tamiz_200)
        pct_arena = max(0.0, pasa_tamiz_4 - pct_finos)

        pct_arena_gruesa = max(0.0, pasa_tamiz_4 - pasa_tamiz_10)
        pct_arena_media = max(0.0, pasa_tamiz_10 - pasa_tamiz_40)
        pct_arena_fina = max(0.0, pasa_tamiz_40 - pasa_tamiz_200)

        # Ajuste para consistencia de suma = 100%
        suma_fracciones = pct_grava + pct_arena + pct_finos
        if abs(suma_fracciones - 100.0) > 0.05 and suma_fracciones > 0:
            factor = 100.0 / suma_fracciones
            pct_grava *= factor
            pct_arena *= factor
            pct_finos *= factor

        # Diámetros característicos D10, D30, D60 por interpolación logarítmica
        d10 = CalculadorGranulometria.interpolar_diametro(filas, 10.0)
        d30 = CalculadorGranulometria.interpolar_diametro(filas, 30.0)
        d60 = CalculadorGranulometria.interpolar_diametro(filas, 60.0)

        # Coeficientes Cu y Cc
        cu: Optional[float] = None
        cc: Optional[float] = None

        if d10 is not None and d60 is not None and d10 > 0:
            cu = d60 / d10

        if d10 is not None and d30 is not None and d60 is not None and (d10 * d60) > 0:
            cc = (d30 ** 2) / (d10 * d60)

        # Clasificación SUCS estimada
        sucs, desc = CalculadorGranulometria.clasificar_sucs(
            pct_grava=pct_grava,
            pct_arena=pct_arena,
            pct_finos=pct_finos,
            cu=cu,
            cc=cc
        )

        return ResultadoGranulometria(
            datos_muestra=datos_muestra,
            tabla=filas,
            peso_total_muestra_g=peso_total_muestra,
            peso_total_retenido_g=peso_total_retenido,
            perdida_peso_g=perdida_peso,
            porcentaje_perdida=pct_perdida,
            d10=d10,
            d30=d30,
            d60=d60,
            cu=cu,
            cc=cc,
            porcentaje_grava=pct_grava,
            porcentaje_arena=pct_arena,
            porcentaje_arena_gruesa=pct_arena_gruesa,
            porcentaje_arena_media=pct_arena_media,
            porcentaje_arena_fina=pct_arena_fina,
            porcentaje_finos=pct_finos,
            clasificacion_sucs=sucs,
            descripcion_suelo=desc,
            advertencias=advertencias
        )

    @staticmethod
    def _obtener_o_interpolar_pasa(filas: List[FilaGranulometria], abertura_objetivo: float) -> float:
        """Obtiene el porcentaje que pasa por una abertura dada, interpolando si es necesario."""
        # Buscar coincidencia exacta
        for f in filas:
            if abs(f.abertura_mm - abertura_objetivo) < 1e-4:
                return f.porcentaje_pasa

        # Filtrar filas con abertura > 0
        puntos = [(f.abertura_mm, f.porcentaje_pasa) for f in filas if f.abertura_mm > 0]
        if not puntos:
            return 0.0

        puntos.sort(key=lambda p: p[0])  # ordenar por abertura ascendente

        aberturas = np.array([p[0] for p in puntos])
        pasas = np.array([p[1] for p in puntos])

        if abertura_objetivo >= aberturas[-1]:
            return 100.0 if pasas[-1] >= 99.9 else pasas[-1]
        if abertura_objetivo <= aberturas[0]:
            return pasas[0]

        # Interpolación semilogarítmica: log10(D) vs % Pasa
        log_aberturas = np.log10(aberturas)
        log_obj = math.log10(abertura_objetivo)

        pct_interp = float(np.interp(log_obj, log_aberturas, pasas))
        return max(0.0, min(100.0, pct_interp))

    @staticmethod
    def interpolar_diametro(filas: List[FilaGranulometria], porcentaje_objetivo: float) -> Optional[float]:
        """
        Calcula el diámetro de partícula correspondiente a un porcentaje que pasa dado (Dx)
        utilizando interpolación logarítmica estándar (ASTM D2487/D6913):
        log(D) = log(D1) + [(x - P1)/(P2 - P1)] * [log(D2) - log(D1)]
        """
        # Extraer puntos con abertura > 0
        puntos = [(f.abertura_mm, f.porcentaje_pasa) for f in filas if f.abertura_mm > 0]
        if not puntos:
            return None

        # Ordenar por porcentaje que pasa ascendente
        puntos.sort(key=lambda p: p[1])

        # Extraer arrays
        pasas = [p[1] for p in puntos]
        aberturas = [p[0] for p in puntos]

        # Si el porcentaje objetivo está por debajo del menor % pasa registrado en tamices físicos
        if porcentaje_objetivo < pasas[0]:
            # Si el último tamiz (#200) tiene por ejemplo 1.82% y buscamos D10, D10 está por encima (está en el rango)
            # Solo si porcentaje_objetivo < pasas[0] significa que ni el tamiz más fino retuvo suficiente
            # En tal caso, si se cuenta con fondo (0 mm, 0%), podemos interpolar con el límite de finos/arcillas (0.002 o 0.001 mm)
            # Pero en rigor técnico, sin hidrómetro, no se extrapola arbitrariamente
            return None

        # Si el porcentaje objetivo está por encima del mayor % pasa registrado
        if porcentaje_objetivo > pasas[-1]:
            return None

        # Buscar el intervalo [P1, P2] tal que P1 <= porcentaje_objetivo <= P2
        for i in range(len(puntos) - 1):
            p1, d1 = pasas[i], aberturas[i]
            p2, d2 = pasas[i + 1], aberturas[i + 1]

            if p1 <= porcentaje_objetivo <= p2:
                if abs(p2 - p1) < 1e-9:
                    return d1
                # Interpolación logarítmica estándar
                log_d1 = math.log10(d1)
                log_d2 = math.log10(d2)
                log_dx = log_d1 + ((porcentaje_objetivo - p1) / (p2 - p1)) * (log_d2 - log_d1)
                return 10 ** log_dx

        return None

    @staticmethod
    def clasificar_sucs(pct_grava: float, pct_arena: float, pct_finos: float,
                         cu: Optional[float], cc: Optional[float]) -> Tuple[str, str]:
        """
        Determina la clasificación aproximada SUCS (ASTM D2487) y descripción geotécnica.
        """
        # 1. Suelos Finos (% Finos >= 50%)
        if pct_finos >= 50.0:
            return (
                "FINO (Limo / Arcilla)",
                f"Suelo de grano fino ({pct_finos:.1f}% de finos). Se requieren los Límites de Atterberg "
                f"(Límite Líquido e Índice de Plasticidad) para clasificar entre CL, CH, ML, MH según SUCS."
            )

        # 2. Suelos Gruesos (% Finos < 50%)
        fraccion_gruesa = pct_grava + pct_arena
        if fraccion_gruesa <= 0:
            return "Indeterminado", "No hay suficiente fracción gruesa para clasificar."

        es_grava = pct_grava > pct_arena

        if es_grava:
            # Tipo GRAVA
            if pct_finos < 5.0:
                bien_graduada = (cu is not None and cu >= 4.0) and (cc is not None and 1.0 <= cc <= 3.0)
                if bien_graduada:
                    return "GW", "Grava bien graduada con poco o nada de finos."
                else:
                    return "GP", "Grava pobremente graduada (uniforme o con salto granulométrico) con poco o nada de finos."
            elif 5.0 <= pct_finos <= 12.0:
                bien_graduada = (cu is not None and cu >= 4.0) and (cc is not None and 1.0 <= cc <= 3.0)
                prefijo = "GW" if bien_graduada else "GP"
                return (
                    f"{prefijo}-GM / {prefijo}-GC",
                    f"Grava con finos ({pct_finos:.1f}%). Clasificación de doble símbolo ({prefijo}-GM o {prefijo}-GC). "
                    f"Requiere Límites de Atterberg para determinar si los finos son limosos o arcillosos."
                )
            else:  # pct_finos > 12.0
                return (
                    "GM / GC",
                    f"Grava con finos ({pct_finos:.1f}% de finos). Requiere Límites de Atterberg para subclasificar "
                    f"entre GM (Grava limosa) y GC (Grava arcillosa)."
                )
        else:
            # Tipo ARENA
            if pct_finos < 5.0:
                bien_graduada = (cu is not None and cu >= 6.0) and (cc is not None and 1.0 <= cc <= 3.0)
                if bien_graduada:
                    return "SW", "Arena bien graduada con poco o nada de finos."
                else:
                    return "SP", "Arena pobremente graduada con poco o nada de finos."
            elif 5.0 <= pct_finos <= 12.0:
                bien_graduada = (cu is not None and cu >= 6.0) and (cc is not None and 1.0 <= cc <= 3.0)
                prefijo = "SW" if bien_graduada else "SP"
                return (
                    f"{prefijo}-SM / {prefijo}-SC",
                    f"Arena con finos ({pct_finos:.1f}%). Clasificación de doble símbolo ({prefijo}-SM o {prefijo}-SC). "
                    f"Requiere Límites de Atterberg para determinar si los finos son limosos o arcillosos."
                )
            else:  # pct_finos > 12.0
                return (
                    "SM / SC",
                    f"Arena con finos ({pct_finos:.1f}% de finos). Requiere Límites de Atterberg para subclasificar "
                    f"entre SM (Arena limosa) y SC (Arena arcillosa)."
                )
