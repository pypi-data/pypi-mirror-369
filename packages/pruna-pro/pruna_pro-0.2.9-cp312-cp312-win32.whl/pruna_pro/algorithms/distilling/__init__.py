from pruna.algorithms.pruna_base import PrunaAlgorithmBase
from pruna.engine.save import SAVE_FUNCTIONS

from pruna_pro import DISTILLER


class PrunaDistiller(PrunaAlgorithmBase):
    """Base class for distillation algorithms."""

    algorithm_group = DISTILLER
    # Diffusers doesn't offer a good way to save/load adapters at the moment, but hyper is fast to reattach
    save_fn = SAVE_FUNCTIONS.save_before_apply
