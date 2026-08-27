"""Simulador de sistema de ar comprimido com compressor de parafuso.

Baseado nas equações do livro "Gêmeo Digital de Sistemas de Compressão
Offshore" (compressores.tex).
"""

from . import (
    calib_lm,
    cenarios_falha,
    constantes,
    dinamica,
    ekf,
    frota_supervisorio,
    mpc,
    nucleo,
    pi_telemetry,
    piml,
    psa_ciclo,
    pso,
    sistema,
    subsistemas,
    treinamento_falhas,
    vae,
)
from .sistema import parametros_default, simular

__version__ = "0.2.0"
__all__ = [
    "parametros_default",
    "simular",
    "calib_lm",
    "cenarios_falha",
    "constantes",
    "dinamica",
    "ekf",
    "frota_supervisorio",
    "mpc",
    "nucleo",
    "pi_telemetry",
    "piml",
    "psa_ciclo",
    "pso",
    "sistema",
    "subsistemas",
    "treinamento_falhas",
    "vae",
]
