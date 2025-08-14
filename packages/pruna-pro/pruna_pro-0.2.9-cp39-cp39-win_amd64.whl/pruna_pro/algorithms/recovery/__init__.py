from pruna.algorithms.pruna_base import PrunaAlgorithmBase
from pruna.engine.save import SAVE_FUNCTIONS

from pruna_pro import RECOVERER


class PrunaRecoverer(PrunaAlgorithmBase):
    """Base class for recovery algorithms."""

    algorithm_group = RECOVERER
    # since we can fuse the LoRA layers into the original model, we can use the original saving method of the model
    save_fn = SAVE_FUNCTIONS.pickled
