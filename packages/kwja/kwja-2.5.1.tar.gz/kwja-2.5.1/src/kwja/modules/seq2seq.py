import os
from statistics import mean
from typing import Any

import hydra
import torch
from omegaconf import DictConfig
from transformers import PreTrainedModel, PreTrainedTokenizerFast
from transformers.generation import LogitsProcessorList

from kwja.modules.base import BaseModule
from kwja.modules.components.logits_processor import (
    SurfForcedDecodingLogitsProcessor,
    get_char2token_items,
    get_reading_candidate_token_ids,
)

if os.environ.get("KWJA_CLI_MODE") == "1":
    from kwja.modules.base import DummyModuleMetric as Seq2SeqModuleMetric  # dummy class for faster loading
else:
    from kwja.metrics import Seq2SeqModuleMetric  # type: ignore


class Seq2SeqModule(BaseModule[Seq2SeqModuleMetric]):
    def __init__(self, hparams: DictConfig) -> None:
        super().__init__(hparams, Seq2SeqModuleMetric(hparams.max_src_length))

        self.tokenizer: PreTrainedTokenizerFast = hydra.utils.call(hparams.module.tokenizer)

        self.encoder_decoder: PreTrainedModel = hydra.utils.call(hparams.encoder.from_config)
        # https://github.com/huggingface/transformers/issues/4875
        self.encoder_decoder.resize_token_embeddings(len(self.tokenizer.vocab))

        self.reading_candidate_token_ids = get_reading_candidate_token_ids(self.tokenizer)
        self.char2token_items = get_char2token_items(self.tokenizer)
        self.use_surf_forced_decoding: bool = getattr(hparams, "use_surf_forced_decoding", False)

    def setup(self, stage: str) -> None:
        if stage == "fit":
            self.encoder_decoder = hydra.utils.call(self.hparams.encoder.from_pretrained)
            # https://github.com/huggingface/transformers/issues/4875
            self.encoder_decoder.resize_token_embeddings(len(self.tokenizer.vocab))

    def forward(self, batch: Any) -> dict[str, torch.Tensor]:
        output = self.encoder_decoder(
            input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], labels=batch["seq2seq_labels"]
        )
        return {"loss": output.loss, "logits": output.logits}

    def training_step(self, batch: Any) -> torch.Tensor:
        ret: dict[str, torch.Tensor] = self(batch)
        self.log("train/loss", ret["loss"])
        return ret["loss"]

    def validation_step(self, batch: Any, batch_idx: int, dataloader_idx: int = 0) -> None:  # noqa: ARG002
        kwargs = self(batch)
        kwargs.update({"example_ids": batch["example_ids"], "loss": kwargs["loss"]})
        metric = self.valid_corpus2metric[self.valid_corpora[dataloader_idx]]
        metric.update(kwargs)

    def on_validation_epoch_end(self) -> None:
        metrics_log: dict[str, dict[str, float]] = {}
        for corpus, metric in self.valid_corpus2metric.items():
            metrics_log[corpus] = metric.compute()
            metric.reset()

        for corpus, metrics in metrics_log.items():
            self.log_dict({f"valid_{corpus}/{key}": value for key, value in metrics.items()})
        for key in next(iter(metrics_log.values())).keys():
            mean_score = mean(metrics_log[corpus][key] for corpus in self.valid_corpora if key in metrics_log[corpus])
            self.log(f"valid/{key}", mean_score)

    def test_step(self, batch: Any, batch_idx: int, dataloader_idx: int = 0) -> None:  # noqa: ARG002
        kwargs = self(batch)
        kwargs.update({"example_ids": batch["example_ids"], "loss": kwargs["loss"]})
        metric = self.test_corpus2metric[self.test_corpora[dataloader_idx]]
        metric.update(kwargs)

    def on_test_epoch_end(self) -> None:
        metrics_log: dict[str, dict[str, float]] = {}
        for corpus, metric in self.test_corpus2metric.items():
            metrics_log[corpus] = metric.compute()
            metric.reset()

        for corpus, metrics in metrics_log.items():
            self.log_dict({f"test_{corpus}/{key}": value for key, value in metrics.items()})
        for key in next(iter(metrics_log.values())).keys():
            mean_score = mean(metrics_log[corpus][key] for corpus in self.test_corpora if key in metrics_log[corpus])
            self.log(f"test/{key}", mean_score)

    def predict_step(self, batch: Any) -> dict[str, Any]:
        generations = self.encoder_decoder.generate(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
            logits_processor=(
                LogitsProcessorList(
                    [
                        SurfForcedDecodingLogitsProcessor(
                            batch_surfs=batch["surfs"],
                            num_beams=self.hparams.decoding.num_beams,
                            tokenizer=self.tokenizer,
                            char2token_items=self.char2token_items,
                            reading_candidate_token_ids=self.reading_candidate_token_ids,
                        ),
                    ]
                )
                if self.use_surf_forced_decoding
                else None
            ),
            **self.hparams.decoding,
        )
        if isinstance(generations, torch.Tensor):
            seq2seq_predictions = generations
        else:
            seq2seq_predictions = generations["sequences"]
        return {
            "example_ids": batch["example_ids"] if "example_ids" in batch else [],
            "seq2seq_predictions": seq2seq_predictions,
        }
