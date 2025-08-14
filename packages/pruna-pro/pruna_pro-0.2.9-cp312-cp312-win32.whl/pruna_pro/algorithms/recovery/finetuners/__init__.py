from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import torch
from pruna.config.smash_config import SmashConfigPrefixWrapper


class PrunaFinetuner(ABC):
    """Base class for recovery finetuners."""

    @classmethod
    @abstractmethod
    def get_hyperparameters(cls, **override_defaults: Any) -> list:
        """
        Configure all algorithm-specific hyperparameters with ConfigSpace.

        Parameters
        ----------
        **override_defaults : Any
            Values used to override the default hyperparameters when using multiple finetuners together.

        Returns
        -------
        list
            The hyperparameters.
        """
        pass

    @classmethod
    @abstractmethod
    def finetune(
        cls, model: torch.nn.Module, smash_config: SmashConfigPrefixWrapper, seed: int, recoverer: str
    ) -> torch.nn.Module:
        """
        Apply the component to the model: activate parameters for Adapters, or finetune them for Finetuners.

        Parameters
        ----------
        model : torch.nn.Module
            The model to apply the component to.
        smash_config : SmashConfigPrefixWrapper
            The configuration for the component.
        seed : int
            The seed to use for finetuning.
        recoverer : str
            The name of the recoverer used, for logging purposes.

        Returns
        -------
        torch.nn.Module
            The model with the component applied.
        """
        pass
