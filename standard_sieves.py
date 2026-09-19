"""
Módulo con listas predeterminadas de tamices estándar (ASTM C136 / ASTM D422 / ASTM D6913)
y juegos de datos de ejemplo.
"""

from typing import List, Tuple
from models import Tamiz

# Lista maestra de tamices estándar ASTM (Nombre, Abertura en mm)
TAMICES_ASTM_MAESTROS: List[Tuple[str, float]] = [
    ('3"', 75.0),
    ('2"', 50.0),
    ('1 1/2"', 37.5),
    ('1"', 25.0),
    ('3/4"', 19.0),
    ('1/2"', 12.5),
    ('3/8"', 9.50),
    ('1/4"', 6.30),
    ('#4', 4.75),
    ('#8', 2.36),
    ('#10', 2.00),
    ('#16', 1.18),
    ('#20', 0.850),
    ('#30', 0.600),
    ('#40', 0.425),
    ('#50', 0.300),
    ('#60', 0.250),
    ('#80', 0.180),
    ('#100', 0.150),
    ('#200', 0.075),
    ('Fondo', 0.0)
]


def obtener_serie_propuesta_ejemplo() -> List[Tamiz]:
    """
    Retorna la serie exacta de tamices y pesos retenidos descrita
    en la propuesta y capturas del usuario:
      3/8" (9.50 mm): 25 g
      #4   (4.75 mm): 40 g
      #10  (2.00 mm): 75 g
      #20  (0.85 mm): 100 g
      #40  (0.425 mm): 120 g
      #60  (0.250 mm): 80 g
      #100 (0.150 mm): 60 g
      #200 (0.075 mm): 40 g
      Fondo (0.0 mm): 10 g
    Total: 550 g
    """
    return [
        Tamiz(nombre='3/8"', abertura_mm=9.50, peso_retenido_g=25.0),
        Tamiz(nombre='#4', abertura_mm=4.75, peso_retenido_g=40.0),
        Tamiz(nombre='#10', abertura_mm=2.00, peso_retenido_g=75.0),
        Tamiz(nombre='#20', abertura_mm=0.850, peso_retenido_g=100.0),
        Tamiz(nombre='#40', abertura_mm=0.425, peso_retenido_g=120.0),
        Tamiz(nombre='#60', abertura_mm=0.250, peso_retenido_g=80.0),
        Tamiz(nombre='#100', abertura_mm=0.150, peso_retenido_g=60.0),
        Tamiz(nombre='#200', abertura_mm=0.075, peso_retenido_g=40.0),
        Tamiz(nombre='Fondo', abertura_mm=0.0, peso_retenido_g=10.0)
    ]


def obtener_serie_astm_completa() -> List[Tamiz]:
    """Retorna la serie completa estándar ASTM con pesos retenidos inicializados en 0."""
    return [Tamiz(nombre=nombre, abertura_mm=abertura, peso_retenido_g=0.0)
            for nombre, abertura in TAMICES_ASTM_MAESTROS]


def obtener_serie_suelos_clasica() -> List[Tamiz]:
    """
    Retorna la serie típica de laboratorio geotécnico:
    3", 1 1/2", 3/4", 3/8", #4, #10, #20, #40, #60, #100, #200, Fondo
    """
    seleccion = ['3"', '1 1/2"', '3/4"', '3/8"', '#4', '#10', '#20', '#40', '#60', '#100', '#200', 'Fondo']
    mapeo = dict(TAMICES_ASTM_MAESTROS)
    return [Tamiz(nombre=nom, abertura_mm=mapeo[nom], peso_retenido_g=0.0) for nom in seleccion]


def obtener_serie_agregado_grueso() -> List[Tamiz]:
    """Retorna serie para análisis de grava / agregado grueso."""
    seleccion = ['2"', '1 1/2"', '1"', '3/4"', '1/2"', '3/8"', '#4', 'Fondo']
    mapeo = dict(TAMICES_ASTM_MAESTROS)
    return [Tamiz(nombre=nom, abertura_mm=mapeo[nom], peso_retenido_g=0.0) for nom in seleccion]
