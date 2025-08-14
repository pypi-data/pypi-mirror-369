from pruna.algorithms.pruna_base import PrunaAlgorithmBase
from pruna.engine.save import SAVE_FUNCTIONS

from pruna_pro import DISTRIBUTER


class PrunaDistributer(PrunaAlgorithmBase):
    """Base class for distribution algorithms."""

    algorithm_group = DISTRIBUTER
    save_fn = SAVE_FUNCTIONS.save_before_apply
