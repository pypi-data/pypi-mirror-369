import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Generic, Optional, TypeVar, Union

import hydra
import lightning as L
import torch
from lightning.fabric import Fabric
from lightning.pytorch.utilities.types import OptimizerLRScheduler
from omegaconf import DictConfig, ListConfig, OmegaConf
from typing_extensions import Self


class DummyModuleMetric:
    def __init__(self, _: int) -> None:
        pass

    def update(self, *args: Any, **kwargs: Any) -> None:
        pass

    def compute(self) -> dict[str, float]:
        return {}

    def reset(self) -> None:
        pass

    def pad(self, *args: Any, **kwargs: Any) -> None:
        pass

    def set_properties(self, *args: Any, **kwargs: Any) -> None:
        pass


if os.environ.get("KWJA_CLI_MODE") == "1":
    BaseModuleMetric = DummyModuleMetric  # dummy class for faster loading
else:
    from kwja.metrics.base import BaseModuleMetric  # type: ignore

MetricType = TypeVar("MetricType", bound=BaseModuleMetric)


class BaseModule(L.LightningModule, Generic[MetricType]):
    def __init__(self, hparams: DictConfig, metric: MetricType) -> None:
        super().__init__()
        self.save_hyperparameters(hparams)

        if valid_corpora := getattr(hparams.datamodule, "valid", None):
            self.valid_corpora: list[str] = list(valid_corpora)
            self.valid_corpus2metric: dict[str, MetricType] = {corpus: deepcopy(metric) for corpus in valid_corpora}
        if test_corpora := getattr(hparams.datamodule, "test", None):
            self.test_corpora: list[str] = list(test_corpora)
            self.test_corpus2metric: dict[str, MetricType] = {corpus: deepcopy(metric) for corpus in test_corpora}

    def configure_optimizers(self) -> OptimizerLRScheduler:
        # Split weights in two groups, one with weight decay and the other not.
        no_decay = ("bias", "LayerNorm.weight")
        optimizer_grouped_parameters = [
            {
                "params": [
                    p for n, p in self.named_parameters() if not any(nd in n for nd in no_decay) and p.requires_grad
                ],
                "weight_decay": self.hparams.optimizer.weight_decay,
                "name": "decay",
            },
            {
                "params": [
                    p for n, p in self.named_parameters() if any(nd in n for nd in no_decay) and p.requires_grad
                ],
                "weight_decay": 0.0,
                "name": "no_decay",
            },
        ]
        optimizer = hydra.utils.instantiate(
            self.hparams.optimizer, params=optimizer_grouped_parameters, _convert_="partial"
        )
        total_steps = self.trainer.estimated_stepping_batches
        if hasattr(self.hparams.scheduler, "num_training_steps"):
            self.hparams.scheduler.num_training_steps = total_steps
        lr_scheduler = hydra.utils.instantiate(self.hparams.scheduler, optimizer=optimizer)
        return {"optimizer": optimizer, "lr_scheduler": {"scheduler": lr_scheduler, "interval": "step", "frequency": 1}}

    def on_save_checkpoint(self, checkpoint: dict[str, Any]) -> None:
        hparams: DictConfig = deepcopy(checkpoint["hyper_parameters"])
        OmegaConf.set_struct(hparams, False)
        if self.hparams.ignore_hparams_on_save:
            hparams = filter_dict_items(hparams, self.hparams.hparams_to_ignore_on_save)
        checkpoint["hyper_parameters"] = hparams

    @classmethod
    def fast_load_from_checkpoint(
        cls,
        checkpoint_path: Path,
        map_location: Optional[Union[torch.device, str]] = None,
        accelerator: str = "cpu",
        strict: bool = True,
    ) -> Self:
        checkpoint = torch.load(checkpoint_path, map_location=map_location, weights_only=False)
        fabric = Fabric(accelerator=accelerator)
        with fabric.init_module(empty_init=True):
            module = cls(hparams=checkpoint[cls.CHECKPOINT_HYPER_PARAMS_KEY])  # type: ignore
        state_dict: dict[str, torch.Tensor] = checkpoint["state_dict"]
        # from transformers 4.31.0, `encoder.embeddings.position_ids` is a non-persistent buffer
        # https://github.com/huggingface/transformers/commit/8e5d1619b3e57367701d74647e87b95f8dba5409#diff-6f3cd40371ba02671abf26407e722aa56cf116263be410253f58c8aa063f14adR866
        if strict is True and "encoder.embeddings.position_ids" in state_dict:
            state_dict.pop("encoder.embeddings.position_ids")
        module.load_state_dict(checkpoint["state_dict"], strict=strict)
        return module


def filter_dict_items(item: DictConfig, keys_to_ignore: ListConfig) -> DictConfig:
    """Filter out dictionary items whose key is in keys_to_ignore recursively."""
    for key, value in item.items():
        ignore = False
        for key_to_ignore in keys_to_ignore:
            if isinstance(key_to_ignore, str) and key == key_to_ignore:
                ignore = True
                break
            elif isinstance(key_to_ignore, (dict, DictConfig)) and key in key_to_ignore:
                item[key] = filter_dict_items(value, key_to_ignore[key])
                break
        if ignore is True:
            del item[key]
    return item
