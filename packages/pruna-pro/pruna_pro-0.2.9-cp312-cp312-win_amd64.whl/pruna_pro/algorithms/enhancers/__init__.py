from pruna.algorithms.pruna_base import PrunaAlgorithmBase
from pruna.engine.save import SAVE_FUNCTIONS

from pruna_pro import ENHANCER


class PrunaEnhancer(PrunaAlgorithmBase):
    """Base class for enhancers."""

    algorithm_group = ENHANCER
    save_fn = SAVE_FUNCTIONS.reapply
