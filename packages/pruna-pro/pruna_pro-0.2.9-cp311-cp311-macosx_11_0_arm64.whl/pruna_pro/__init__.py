# flake8: noqa
import pruna.config.smash_space
from pruna.config.smash_space import FACTORIZER, BATCHER, CACHER, COMPILER, PRUNER, QUANTIZER, KERNEL

DISTILLER = "distiller"
RECOVERER = "recoverer"
ENHANCER = "enhancer"
DISTRIBUTER = "distributer"

pruna.config.smash_space.ALGORITHM_GROUPS.clear()
pruna.config.smash_space.ALGORITHM_GROUPS.extend(
    [
        FACTORIZER,
        PRUNER,
        QUANTIZER,
        DISTILLER,
        KERNEL,
        CACHER,
        RECOVERER,
        DISTRIBUTER,
        COMPILER,
        BATCHER,
        ENHANCER,
    ]
)

from importlib_metadata import version
from pruna import SmashConfig

from pruna_pro.engine.pruna_pro_model import PrunaProModel
from pruna_pro.optimization_agent import OptimizationAgent
from pruna_pro.smash import smash
from pruna.telemetry import set_telemetry_metrics

set_telemetry_metrics(
    enabled=True, set_as_default=False
)  # Always have telemetry activated by default for Pro, whatever the default

__version__ = version(__name__)

__all__ = ["PrunaProModel", "smash", "SmashConfig", "__version__", "OptimizationAgent"]
