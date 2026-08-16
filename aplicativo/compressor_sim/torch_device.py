"""Seleção de device (GPU/CPU) para os módulos PyTorch (`vae.py`, `piml.py`).

Um único ponto de decisão, reaproveitado pelos dois módulos, para não
duplicar a mesma lógica: usa GPU (CUDA) automaticamente quando disponível,
cai para CPU quando não há — sem exigir nenhuma configuração manual do
usuário. `requirements.txt` instala o build padrão do PyTorch (que já traz
suporte a CUDA); esta função é o que de fato decide, em tempo de execução,
se essa capacidade é usada.
"""

from __future__ import annotations

import torch

_device_cache: torch.device | None = None


def obter_device() -> torch.device:
    """Devolve `cuda` se uma GPU NVIDIA estiver disponível, senão `cpu`.

    Resultado cacheado após a primeira chamada — `torch.cuda.is_available()`
    consulta o driver, então não é gratuito repetir a cada treino.
    """
    global _device_cache
    if _device_cache is None:
        _device_cache = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _device_cache


__all__ = ["obter_device"]
