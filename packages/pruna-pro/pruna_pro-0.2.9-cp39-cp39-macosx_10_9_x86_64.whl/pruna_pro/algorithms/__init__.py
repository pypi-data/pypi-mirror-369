from copy import deepcopy
from typing import Any

from pruna import PRUNA_ALGORITHMS
from pruna.config.smash_space import ALGORITHM_GROUPS

import pruna_pro.algorithms.compilation.stable_fast  # noqa: F401
import pruna_pro.algorithms.compilation.torch_compile  # noqa: F401
from pruna_pro.algorithms.caching.adaptive_caching import AdaptiveCacher
from pruna_pro.algorithms.caching.auto_caching import AutoCacher
from pruna_pro.algorithms.caching.flux_caching import FluxCachingCacher
from pruna_pro.algorithms.caching.periodic_caching import PeriodicCacher
from pruna_pro.algorithms.caching.taylor_auto_caching import TaylorAutoCacher
from pruna_pro.algorithms.caching.taylor_caching import TaylorCacher
from pruna_pro.algorithms.compilation.ipex_llm import IPEXLLMCompiler
from pruna_pro.algorithms.compilation.x_fast import XFastCompiler
from pruna_pro.algorithms.distilling.hyper import HyperDistiller
from pruna_pro.algorithms.distributing.ring import RingDistributer
from pruna_pro.algorithms.enhancers.denoise import Img2ImgDenoiseEnhancer
from pruna_pro.algorithms.enhancers.upscale import RealESRGANEnhancer
from pruna_pro.algorithms.pruning.padding_pruning import PaddingPruner
from pruna_pro.algorithms.quantization.diffusers_higgs import DiffusersHiggsQuantizer
from pruna_pro.algorithms.quantization.fp8 import Fp8Quantizer
from pruna_pro.algorithms.quantization.huggingface_higgs import HiggsQuantizer
from pruna_pro.algorithms.quantization.torchao_autoquant import AutoquantQuantizer
from pruna_pro.algorithms.recovery.perp import (
    TextToImageInPlacePERPRecoverer,
    TextToImageLoRARecoverer,
    TextToImagePERPRecoverer,
    TextToTextInPlacePERPRecoverer,
    TextToTextLoRARecoverer,
    TextToTextPERPRecoverer,
)

PRUNA_PRO_ALGORITHMS: dict[str, dict[str, Any]] = deepcopy(PRUNA_ALGORITHMS)

for algorithm_group in ALGORITHM_GROUPS:
    if algorithm_group not in PRUNA_PRO_ALGORITHMS:
        PRUNA_PRO_ALGORITHMS[algorithm_group] = {}

PRUNA_PRO_ALGORITHMS["compiler"]["x_fast"] = XFastCompiler()
PRUNA_PRO_ALGORITHMS["compiler"]["ipex_llm"] = IPEXLLMCompiler()
PRUNA_PRO_ALGORITHMS["cacher"]["adaptive"] = AdaptiveCacher()
PRUNA_PRO_ALGORITHMS["cacher"]["auto"] = AutoCacher()
PRUNA_PRO_ALGORITHMS["cacher"]["flux_caching"] = FluxCachingCacher()
PRUNA_PRO_ALGORITHMS["cacher"]["periodic"] = PeriodicCacher()
PRUNA_PRO_ALGORITHMS["quantizer"]["torchao_autoquant"] = AutoquantQuantizer()
PRUNA_PRO_ALGORITHMS["quantizer"]["higgs"] = HiggsQuantizer()
PRUNA_PRO_ALGORITHMS["quantizer"]["diffusers_higgs"] = DiffusersHiggsQuantizer()
PRUNA_PRO_ALGORITHMS["quantizer"]["fp8"] = Fp8Quantizer()
PRUNA_PRO_ALGORITHMS["distiller"]["hyper"] = HyperDistiller()
PRUNA_PRO_ALGORITHMS["recoverer"]["text_to_text_perp"] = TextToTextPERPRecoverer()
PRUNA_PRO_ALGORITHMS["recoverer"]["text_to_text_inplace_perp"] = TextToTextInPlacePERPRecoverer()
PRUNA_PRO_ALGORITHMS["recoverer"]["text_to_text_lora"] = TextToTextLoRARecoverer()
PRUNA_PRO_ALGORITHMS["recoverer"]["text_to_image_perp"] = TextToImagePERPRecoverer()
PRUNA_PRO_ALGORITHMS["recoverer"]["text_to_image_inplace_perp"] = TextToImageInPlacePERPRecoverer()
PRUNA_PRO_ALGORITHMS["recoverer"]["text_to_image_lora"] = TextToImageLoRARecoverer()
PRUNA_PRO_ALGORITHMS["cacher"]["taylor"] = TaylorCacher()
PRUNA_PRO_ALGORITHMS["cacher"]["taylor_auto"] = TaylorAutoCacher()
PRUNA_PRO_ALGORITHMS["enhancer"]["realesrgan_upscale"] = RealESRGANEnhancer()
PRUNA_PRO_ALGORITHMS["enhancer"]["img2img_denoise"] = Img2ImgDenoiseEnhancer()
PRUNA_PRO_ALGORITHMS["pruner"]["padding_pruning"] = PaddingPruner()
PRUNA_PRO_ALGORITHMS["distributer"]["ring_attn"] = RingDistributer()
