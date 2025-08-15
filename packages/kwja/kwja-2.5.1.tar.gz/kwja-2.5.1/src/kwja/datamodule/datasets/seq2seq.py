import logging
from dataclasses import dataclass
from pathlib import Path

from rhoknp import Document
from transformers import PreTrainedTokenizerFast

from kwja.datamodule.datasets.base import BaseDataset
from kwja.datamodule.examples import Seq2SeqExample
from kwja.utils.constants import IGNORE_INDEX
from kwja.utils.logging_util import track
from kwja.utils.normalization import normalize_morpheme
from kwja.utils.seq2seq_format import Seq2SeqFormatter

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Seq2SeqModuleFeatures:
    example_ids: int
    surfs: list[str]
    input_ids: list[int]
    attention_mask: list[int]
    seq2seq_labels: list[int]


class Seq2SeqDataset(BaseDataset[Seq2SeqExample, Seq2SeqModuleFeatures]):
    def __init__(
        self,
        path: str,
        tokenizer: PreTrainedTokenizerFast,
        max_src_length: int,
        max_tgt_length: int,
        ext: str = "knp",
    ) -> None:
        super().__init__(tokenizer, max_src_length)
        self.path = Path(path)

        self.max_src_length: int = max_src_length
        self.max_tgt_length: int = max_tgt_length

        self.formatter: Seq2SeqFormatter = Seq2SeqFormatter(tokenizer)

        self.documents: list[Document] = self._load_documents(self.path, ext)
        is_train: bool = self.path.name == "train"
        self.examples: list[Seq2SeqExample] = self._load_examples(self.documents, is_train)

    @staticmethod
    def _load_documents(document_dir: Path, ext: str = "knp") -> list[Document]:
        documents = []
        for path in track(sorted(document_dir.glob(f"*.{ext}")), description="Loading documents"):
            documents.append(Document.from_knp(path.read_text()))
        return documents

    def _load_examples(self, documents: list[Document], is_train: bool) -> list[Seq2SeqExample]:
        examples: list[Seq2SeqExample] = []
        example_id: int = 0
        for document in track(documents, description="Loading examples"):
            processed_document = self._postprocess_document(document)
            for sentence in processed_document.sentences:
                src_tokens: list[str] = self.formatter.get_src_tokens(sentence)
                src_input_ids: list[int] = [
                    *self.tokenizer.convert_tokens_to_ids(src_tokens),
                    self.tokenizer.eos_token_id,
                ]
                src_attention_mask: list[int] = [1] * len(src_input_ids)
                src_input_ids += [self.tokenizer.pad_token_id] * (self.max_src_length - len(src_input_ids))
                src_attention_mask += [0] * (self.max_src_length - len(src_attention_mask))
                if len(src_input_ids) > self.max_src_length:
                    logger.warning(f"Length of source sentence is too long: {sentence.text}")
                    continue
                tgt_tokens: list[str] = self.formatter.get_tgt_tokens(sentence)
                tgt_input_ids: list[int] = [
                    *self.tokenizer.convert_tokens_to_ids(tgt_tokens),
                    self.tokenizer.eos_token_id,
                ]
                tgt_input_ids += [self.tokenizer.pad_token_id] * (self.max_tgt_length - len(tgt_input_ids))
                if len(tgt_input_ids) > self.max_tgt_length:
                    logger.warning(f"Length of target sentence is too long: {sentence.text}")
                    continue
                examples.append(
                    Seq2SeqExample(
                        example_id=example_id,
                        surfs=self.formatter.get_surfs(sentence),
                        src_input_ids=src_input_ids,
                        src_attention_mask=src_attention_mask,
                        tgt_input_ids=tgt_input_ids,
                        sid=sentence.sid,
                    )
                )
                example_id += 1
        if len(examples) == 0:
            logger.error(
                f"No examples to process. Make sure there exist any documents in {self.path} and they are not too long."
            )
        if not is_train:
            # sort by length of input sentences for efficient inference in validation and test
            examples = sorted(examples, key=lambda x: len(x.surfs))
            for i, _example in enumerate(examples):
                examples[i].example_id = i
        return examples

    def encode(self, example: Seq2SeqExample) -> Seq2SeqModuleFeatures:
        seq2seq_labels: list[int] = [
            (seq2seq_tag if seq2seq_tag != self.tokenizer.pad_token_id else IGNORE_INDEX)
            for seq2seq_tag in example.tgt_input_ids
        ]
        assert len(seq2seq_labels) == self.max_tgt_length

        return Seq2SeqModuleFeatures(
            example_ids=example.example_id,
            surfs=example.surfs,
            input_ids=example.src_input_ids,
            attention_mask=example.src_attention_mask,
            seq2seq_labels=seq2seq_labels,
        )

    def _postprocess_document(self, document: Document) -> Document:
        for morpheme in document.morphemes:
            surf = morpheme.text
            normalize_morpheme(morpheme)
            if morpheme.text != surf:
                logger.warning(f"apply normalization ({surf} -> {morpheme.text})")
        # propagate updates of morpheme.text to sentence.text and document.text
        return document.reparse()
