"""
Módulo de modelos de datos para el análisis granulométrico de suelos.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import date


@dataclass
class Tamiz:
    """Representa un tamiz con su identificación, abertura y peso retenido."""
    nombre: str
    abertura_mm: float  # 0.0 para el fondo / bandeja
    peso_retenido_g: float = 0.0
    peso_tamiz_tara_g: float = 0.0
    peso_tamiz_mas_suelo_g: float = 0.0

    def __post_init__(self):
        # Si se ingresan pesos con tara, calcular el retenido neto si peso_retenido_g es 0
        if self.peso_retenido_g == 0.0 and self.peso_tamiz_mas_suelo_g > self.peso_tamiz_tara_g > 0.0:
            self.peso_retenido_g = self.peso_tamiz_mas_suelo_g - self.peso_tamiz_tara_g


@dataclass
class FilaGranulometria:
    """Representa una fila calculada de la tabla granulométrica."""
    tamiz: str
    abertura_mm: float
    peso_retenido_g: float
    porcentaje_retenido: float
    porcentaje_retenido_acumulado: float
    porcentaje_pasa: float


@dataclass
class DatosMuestra:
    """Metadatos de la muestra de suelo y ensayo de laboratorio."""
    id_muestra: str = "M-01"
    proyecto: str = "Proyecto de Mecánica de Suelos"
    cliente_o_curso: str = "Programación II - Ingeniería Civil"
    ubicacion_sondeo: str = "Pozo 1 / Muestra superficial"
    operador: str = "Laboratorio de Suelos"
    fecha: str = field(default_factory=lambda: date.today().strftime("%d/%m/%Y"))
    peso_total_especificado: Optional[float] = None
    observaciones: str = ""


@dataclass
class ResultadoGranulometria:
    """Resultado completo del análisis granulométrico."""
    datos_muestra: DatosMuestra
    tabla: List[FilaGranulometria]
    peso_total_muestra_g: float
    peso_total_retenido_g: float
    perdida_peso_g: float
    porcentaje_perdida: float
    d10: Optional[float]
    d30: Optional[float]
    d60: Optional[float]
    cu: Optional[float]
    cc: Optional[float]
    porcentaje_grava: float
    porcentaje_arena: float
    porcentaje_arena_gruesa: float
    porcentaje_arena_media: float
    porcentaje_arena_fina: float
    porcentaje_finos: float
    clasificacion_sucs: str
    descripcion_suelo: str
    advertencias: List[str] = field(default_factory=list)

    def resumen_dict(self) -> Dict[str, Any]:
        """Retorna un diccionario con el resumen de los parámetros geotécnicos."""
        return {
            "Muestra": self.datos_muestra.id_muestra,
            "Peso Total (g)": round(self.peso_total_muestra_g, 2),
            "Pérdida de Lavado/Pesaje (%)": round(self.porcentaje_perdida, 2),
            "Grava (%)": round(self.porcentaje_grava, 2),
            "Arena (%)": round(self.porcentaje_arena, 2),
            "  - Arena Gruesa (%)": round(self.porcentaje_arena_gruesa, 2),
            "  - Arena Media (%)": round(self.porcentaje_arena_media, 2),
            "  - Arena Fina (%)": round(self.porcentaje_arena_fina, 2),
            "Finos (%)": round(self.porcentaje_finos, 2),
            "D10 (mm)": round(self.d10, 3) if self.d10 is not None else "N/D",
            "D30 (mm)": round(self.d30, 3) if self.d30 is not None else "N/D",
            "D60 (mm)": round(self.d60, 3) if self.d60 is not None else "N/D",
            "Cu (Uniformidad)": round(self.cu, 2) if self.cu is not None else "N/D",
            "Cc (Curvatura)": round(self.cc, 2) if self.cc is not None else "N/D",
            "Clasificación SUCS": self.clasificacion_sucs,
            "Descripción": self.descripcion_suelo
        }
