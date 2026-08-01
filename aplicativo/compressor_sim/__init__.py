"""Simulador de sistema de ar comprimido com compressor de parafuso.

Baseado nas equações do livro "Gêmeo Digital de Sistemas de Compressão
Offshore" (compressores.tex).
"""

from .sistema import parametros_default, simular

__version__ = "0.1.0"
__all__ = ["parametros_default", "simular"]
