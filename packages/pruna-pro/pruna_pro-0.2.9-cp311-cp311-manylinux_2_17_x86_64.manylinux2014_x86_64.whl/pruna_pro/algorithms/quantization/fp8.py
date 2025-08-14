from __future__ import annotations

from typing import Any, Dict

import torch
from ConfigSpace import Constant
from pruna.algorithms.quantization import PrunaQuantizer
from pruna.config.smash_config import SmashConfigPrefixWrapper
from pruna.engine.model_checks import (
    is_transformer_pipeline,
    is_unet_pipeline,
)
from pruna.engine.save import SAVE_FUNCTIONS

from pruna_pro.algorithms.quantization.utils.fp8 import create_fp8_linear_class, recursive_swap_linears
from pruna_pro.engine.pruna_pro_model import PrunaProModel
from pruna_pro.engine.utils import ModelContext


class Fp8Quantizer(PrunaQuantizer):
    """
    Implement fp8 quantization, using torch._scaled_mm to accelerate the inference.

    Based on the torch.float8_e4m3fn and torch.float8_e5m2 formats, this quantizer compresses the weights,
    but also the activations, to reduce the memory usage and the inference time.
    """

    algorithm_name = "fp8"
    references = {
        "Github": "https://github.com/aredden/flux-fp8-api",
    }
    save_fn = SAVE_FUNCTIONS.save_before_apply
    tokenizer_required = False
    processor_required = False
    runs_on: list[str] = ["cpu", "cuda", "accelerate"]
    dataset_required = False
    compatible_algorithms = dict(
        factorizer=["qkv_diffusers"],
        compiler=["torch_compile"],
        cacher=["flux_caching", "periodic", "adaptive", "fora", "auto", "deepcache", "taylor", "taylor_auto"],
        distributer=["ring_attn"],
    )

    def get_hyperparameters(self) -> list:
        """
        Configure all algorithm-specific hyperparameters with ConfigSpace.

        Returns
        -------
        list
            The hyperparameters.
        """
        return [
            Constant(
                "float8_dtype",
                value="torch.float8_e4m3fn",
                meta=dict(desc="The float8 dtype to use for weight quantization."),
            ),
            Constant(
                "input_float8_dtype",
                value="torch.float8_e5m2",
                meta=dict(desc="The float8 dtype to use for input quantization."),
            ),
        ]

    def model_check_fn(self, model: Any) -> bool:
        """
        Check if the model is directly made of a nn.Module, or if it is a pipeline with a unet/transformer denoiser.

        Parameters
        ----------
        model : Any
            The model to check.

        Returns
        -------
        bool
            True if the model is a nn.Module, or a pipeline with a unet/transformer denoiser, False otherwise.
        """
        if isinstance(model, torch.nn.Module):
            return True
        return is_unet_pipeline(model) or is_transformer_pipeline(model)

    def _apply(self, model: Any, smash_config: SmashConfigPrefixWrapper) -> Any:
        """
        Quantize the model.

        Parameters
        ----------
        model : Any
            The model to quantize.
        smash_config : SmashConfigPrefixWrapper
            The configuration for the quantization.

        Returns
        -------
        Any
            The quantized model.
        """
        PrunaProModel.verify_token(token=None)

        imported_modules = self.import_algorithm_packages()
        f8_linear = create_fp8_linear_class(imported_modules)
        # if is a pipeline with a unet/transformer denoiser.
        if is_unet_pipeline(model) or is_transformer_pipeline(model):
            # Use context manager to handle the model vs working_model.
            with ModelContext(model) as (pipeline, working_model, denoiser_type):
                # the model is a nn.Module (but not a LLM), a priori all its linear layers will be quantized.
                recursive_swap_linears(
                    working_model,
                    float8_dtype=(
                        torch.float8_e4m3fn
                        if smash_config["float8_dtype"] == "torch.float8_e4m3fn"
                        else torch.float8_e5m2
                    ),
                    input_float8_dtype=(
                        torch.float8_e4m3fn
                        if smash_config["input_float8_dtype"] == "torch.float8_e4m3fn"
                        else torch.float8_e5m2
                    ),
                    linear_class=f8_linear,
                )
                pipeline.working_model = working_model
        else:
            recursive_swap_linears(
                model,
                float8_dtype=(
                    torch.float8_e4m3fn if smash_config["float8_dtype"] == "torch.float8_e4m3fn" else torch.float8_e5m2
                ),
                input_float8_dtype=(
                    torch.float8_e4m3fn
                    if smash_config["input_float8_dtype"] == "torch.float8_e4m3fn"
                    else torch.float8_e5m2
                ),
                linear_class=f8_linear,
            )
        return model

    def import_algorithm_packages(self) -> Dict[str, Any]:
        """
        Provide a algorithm packages for the algorithm.

        Returns
        -------
        Dict[str, Any]
            The algorithm packages.
        """
        return dict()
