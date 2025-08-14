import tempfile
from typing import Any, Dict

from ConfigSpace import OrdinalHyperparameter
from pruna.algorithms.quantization import PrunaQuantizer
from pruna.config.smash_config import SmashConfigPrefixWrapper
from pruna.engine.model_checks import is_causal_lm
from pruna.engine.utils import move_to_device
from pruna.logging.logger import pruna_logger
from transformers import AutoModelForCausalLM
from transformers.quantizers.auto import (
    AUTO_QUANTIZATION_CONFIG_MAPPING,
    AUTO_QUANTIZER_MAPPING,
)

from pruna_pro.algorithms.quantization.utils.huggingface_higgs import (
    HiggsConfig,
    check_device_capability,
    create_hf_quantizer_class,
    get_modules_to_not_convert,
)
from pruna_pro.engine.pruna_pro_model import PrunaProModel
from pruna_pro.engine.save import SAVE_FUNCTIONS


class HiggsQuantizer(PrunaQuantizer):
    """
    Implement HIGGS quantization using the transformers library.

    HIGGS is a zero-shot quantization method that uses Hadamard preprocessing to transform weights and then selects
    MSE-optimal quantization grids.
    Note: The higgs kernels prepare the model for inference with the batch size specified in the smash config. Make sure
    to set the batch size to a value that corresponds to your inference requirements.
    """

    algorithm_name = "higgs"
    references = {
        "Github": "https://github.com/huggingface/transformers/blob/main/src/transformers/integrations/higgs.py",
        "Article": "https://arxiv.org/abs/2411.17525",
    }
    save_fn: SAVE_FUNCTIONS = SAVE_FUNCTIONS.transformers_higgs  # type: ignore[attr-defined]
    tokenizer_required: bool = False
    processor_required: bool = False
    runs_on: list[str] = ["cuda"]
    dataset_required: bool = False
    compatible_algorithms: dict[str, list[str]] = dict(
        compiler=["torch_compile"],
        pruner=["torch_unstructured"],
    )
    required_install = "``pip install pruna_pro[higgs] --extra-index-url https://prunaai.pythonanywhere.com/``"

    def get_hyperparameters(self) -> list:
        """
        Configure all algorithm-specific hyperparameters with ConfigSpace.

        Returns
        -------
        list
            The hyperparameters.
        """
        return [
            OrdinalHyperparameter(
                "weight_bits",
                sequence=[2, 3, 4],
                default_value=4,
                meta=dict(desc="The number of bits to use for weight quantization."),
            ),
            OrdinalHyperparameter(
                "p",
                sequence=[1, 2],
                default_value=2,
                meta=dict(desc="The number of groups to use for weight quantization."),
            ),
            OrdinalHyperparameter(
                "group_size",
                sequence=[64, 128, 256],
                default_value=256,
                meta=dict(desc="The size of each group."),
            ),
            OrdinalHyperparameter(
                "hadamard_size",
                sequence=[512, 1024, 2048],
                default_value=1024,
                meta=dict(desc="The size of the hadamard matrix."),
            ),
        ]

    def model_check_fn(self, model: Any) -> bool:
        """
        Check if the model is a causal language model.

        Parameters
        ----------
        model : Any
            The model to check.

        Returns
        -------
        bool
            True if the model is a causal language model, False otherwise.
        """
        return is_causal_lm(model)

    def _apply(self, model: Any, smash_config: SmashConfigPrefixWrapper) -> Any:
        """
        Quantize the model using the HIGGS algorithm.

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
        _ = self.import_algorithm_packages()

        weight_type = next(model.parameters()).dtype

        # Create a temporary directory
        with tempfile.TemporaryDirectory(prefix=str(smash_config["cache_dir"])) as temp_dir:
            # cast original model to CPU to free memory for smashed model
            move_to_device(model, "cpu")

            # refrain from quantizing small weights, and the lm_head.
            modules_to_not_convert = get_modules_to_not_convert(
                model,
                smash_config["weight_bits"],
                smash_config["device"],
                smash_config["group_size"],
                smash_config["hadamard_size"],
            )
            model.save_pretrained(temp_dir)
            pruna_logger.info(f"Quantizing model for inference with batch size {smash_config.batch_size}.")
            smash_config.lock_batch_size()
            higgs_config = HiggsConfig(
                bits=smash_config["weight_bits"],
                p=smash_config["p"],
                hadamard_size=smash_config["hadamard_size"],
                group_size=smash_config["group_size"],
                example_batch_size=smash_config.batch_size,
                modules_to_not_convert=modules_to_not_convert,
            )

            smashed_model = AutoModelForCausalLM.from_pretrained(
                temp_dir,
                quantization_config=higgs_config,
                trust_remote_code=True,
                device_map="auto",
                torch_dtype=weight_type,
            )
            move_to_device(smashed_model, smash_config["device"])
        return smashed_model

    def import_algorithm_packages(self) -> Dict[str, Any]:
        """
        Provide a algorithm packages for the algorithm.

        Returns
        -------
        Dict[str, Any]
            The algorithm packages.
        """
        from fast_hadamard_transform import hadamard_transform
        from flute.integrations.higgs import prepare_data_transposed
        from flute.tune import TuneMetaData, maybe_tune_and_repack, qgemm_v2
        from flute.utils import make_workspace_streamk

        check_device_capability()
        imported_modules = dict(
            hadamard_transform=hadamard_transform,
            prepare_data_transposed=prepare_data_transposed,
            maybe_tune_and_repack=maybe_tune_and_repack,
            qgemm_v2=qgemm_v2,
            make_workspace_streamk=make_workspace_streamk,
            TuneMetaData=TuneMetaData,
        )
        # Add HiggsHfQuantizer to the AUTO_QUANTIZER_MAPPING
        higgs_hf_quantizer = create_hf_quantizer_class(imported_modules)
        AUTO_QUANTIZER_MAPPING["higgs"] = higgs_hf_quantizer
        AUTO_QUANTIZATION_CONFIG_MAPPING["higgs"] = HiggsConfig
        return dict()
