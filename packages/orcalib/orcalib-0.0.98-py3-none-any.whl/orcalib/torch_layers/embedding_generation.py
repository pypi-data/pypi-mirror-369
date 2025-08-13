from typing import Literal, cast, overload

import torch
from torch import Tensor, nn
from transformers import AutoModel, AutoTokenizer
from transformers.modeling_utils import PreTrainedModel
from transformers.tokenization_utils_base import BatchEncoding, PreTrainedTokenizerBase


class SentenceEmbeddingGenerator(nn.Module):
    """
    Model for creating embeddings for sentences using a pre-trained model.

    Note:
        To fine-tune the embedding layer initialize it with `frozen=False`.
    """

    embedding_dim: int
    max_sequence_length: int

    def __init__(
        self,
        base_model: str,
        tokenizer_model: str | None = None,
        frozen: bool = True,
        pooling: Literal["cls", "mean"] = "cls",
        normalize: bool = False,
        max_sequence_length: int | None = None,
        trust_remote_code: bool = False,
    ):
        """
        Initialize the Embedder

        Args:
            base_model: Name or path of the pre-trained model to use as the base encoder.
            frozen: If True, freezes the base model parameters, preventing updates during training.
            pooling: Pooling strategy for creating sentence embeddings. "cls" uses the [CLS] token embedding,
                while "mean" averages all token embeddings.
            normalize: If True, normalizes the output embeddings to unit length.
            max_sequence_length: Maximum number of tokens to process. If None, uses the model's default max length.
            trust_remote_code: If True, trusts the remote code of the base model.

        Note:
            The embedding dimension is automatically set based on the hidden size of the base model.
        """
        super().__init__()
        # TODO: support LoRA tuning
        self.base_model = base_model
        self.tokenizer_model = tokenizer_model
        self.tokenizer: PreTrainedTokenizerBase = AutoTokenizer.from_pretrained(tokenizer_model or base_model)
        if max_sequence_length is not None and max_sequence_length > self.tokenizer.model_max_length:
            raise ValueError(
                f"max_sequence_length ({max_sequence_length}) is greater than the model's maximum sequence length "
                f"({self.tokenizer.model_max_length})."
            )
        self.max_sequence_length = max_sequence_length or self.tokenizer.model_max_length
        self.normalize = normalize
        self.pooling = pooling
        self.encoder: PreTrainedModel = AutoModel.from_pretrained(base_model, trust_remote_code=trust_remote_code)
        self.embedding_dim = self.encoder.config.hidden_size
        self.frozen = frozen
        if frozen:
            for param in self.encoder.parameters():
                param.requires_grad = False
        if torch.cuda.is_available():
            self.to(torch.device("cuda"))
        elif torch.cuda.is_available():
            self.to(torch.device("mps"))
        else:
            self.to(torch.device("cpu"))

    @property
    def device(self) -> torch.device:
        """Current device of the encoder"""
        return self.encoder.device

    def get_max_sequence_length(self, text: list[str]) -> int:
        """
        Get the maximum sequence length of the given texts to be used for tokenization.

        Args:
            text: the texts to get the maximum sequence length for

        Returns:
            either the maximum sequence length of the given texts or the maximum sequence length
            supported by the model if the texts are longer than the model supports.
        """
        return min(
            max(len(cast(list[str], self.tokenizer(t)["input_ids"])) for t in text),
            self.tokenizer.model_max_length,
        )

    @overload
    def tokenize(
        self,
        text: str | list[str] | list[list[str]],
        *,
        name: str | None = None,
        return_tensors: Literal[False] = False,
        sequence_length: int | None = None,
    ) -> BatchEncoding:
        pass

    @overload
    def tokenize(
        self,
        text: str | list[str] | list[list[str]],
        *,
        name: None = None,
        return_tensors: Literal[True],
        sequence_length: int | None = None,
    ) -> tuple[Tensor, Tensor]:
        pass

    def tokenize(
        self,
        text: str | list[str] | list[list[str]],
        *,
        name: str | None = None,
        return_tensors: bool = False,
        sequence_length: int | None = None,
    ) -> BatchEncoding | tuple[Tensor, Tensor]:
        """
        Tokenize the input text

        Args:
            text: the text to tokenize, can be either a single string or a batch of strings, or a batch of list of strings (for batches of memories)
            name: optional name of the parameter to use in the output, e.g. when set to "memories", the output will have keys "memories_ids" and "memories_mask"
            return_tensors: if True, return the tokenized text as a tuple of tensors, otherwise return a BatchEncoding
            sequence_length: length of the output sequence. If None, will pad to the longest sequence in the batch.
        Returns:
            tokenized text (ids and attention mask) or list of tokenized texts or list of list of tokenized texts or tuple of tensors (ids and attention mask) if return_tensors is True

        Examples:
            >>> embedder.tokenize("Hello, world!")
            {"input_ids": [101, 7592, 2088, 2003, 2074, 102], "attention_mask": [1, 1, 1, 1, 1, 1]}

            >>> embedder.tokenize(["Hello, world!", "Hello, universe!"], name="input")
            {
                "input_ids": [
                    [101, 7592, 2088, 2003, 2074, 102],
                    [101, 7592, 2088, 2003, 2074, 102]
                ],
                "input_mask": [
                    [1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1]
                ]
            }

            >>> embedder.tokenize([
            ...     ["Hello, world!", "Hello, universe!"],
            ...     ["Hello, world!", "Hello, universe!"]
            ... ], name="memories")
            {
                "memories_ids": [
                    [
                        [101, 7592, 2088, 2003, 2074, 102],
                        [101, 7592, 2088, 2003, 2074, 102]
                    ],
                    [
                        [101, 7592, 2088, 2003, 2074, 102],
                        [101, 7592, 2088, 2003, 2074, 102]
                    ]
                ],
                "memories_mask": [
                    [
                        [1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1]
                    ],
                    [
                        [1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1]
                    ]
                ]
            }
        """
        dimensions = (
            1
            if isinstance(text, str)
            else (
                2
                if isinstance(text, (list, tuple)) and isinstance(text[0], str)
                else (
                    3
                    if isinstance(text, (list, tuple))
                    and isinstance(text[0], (list, tuple))
                    and isinstance(text[0][0], str)
                    else None
                )
            )
        )
        padding = "max_length" if sequence_length else "do_not_pad" if dimensions == 1 else "longest"
        max_length = sequence_length or self.max_sequence_length
        if dimensions == 1 or dimensions == 2:
            tokens = self.tokenizer(text, padding=padding, truncation=True, max_length=max_length)
        elif dimensions == 3:
            token_batch = [
                self.tokenizer(ts, padding=padding, truncation=True, max_length=max_length)
                for ts in cast(list[list[str]], text)
            ]
            tokens = dict(
                input_ids=[r["input_ids"] for r in token_batch],
                attention_mask=[r["attention_mask"] for r in token_batch],
            )
        else:
            raise ValueError(f"Invalid dimensions: {dimensions}")

        if return_tensors:
            return (
                torch.tensor(tokens["input_ids"], device=self.device),
                torch.tensor(tokens["attention_mask"], device=self.device),
            )
        else:
            input_ids_name = "input_ids" if name is None else f"{name}_ids"
            attention_mask_name = "attention_mask" if name is None else f"{name}_mask"
            return BatchEncoding(
                {
                    input_ids_name: tokens["input_ids"],
                    attention_mask_name: tokens["attention_mask"],
                }
            )

    def _pool_and_normalize(self, last_hidden_state: Tensor, attention_mask: Tensor) -> Tensor:
        """
        Apply pooling strategy and normalize the embeddings

        Args:
            last_hidden_state: the last hidden state of the encoder
            attention_mask: the attention mask of the encoder

        Returns:
            the pooled and normalized embeddings
        """
        # apply pooling strategy
        if self.pooling == "cls":
            embeds = last_hidden_state[:, 0, :]
        elif self.pooling == "mean":
            token_count = attention_mask.sum(dim=1, keepdim=True)
            embeds = (last_hidden_state * attention_mask.unsqueeze(-1)).sum(dim=1) / token_count.clamp(min=1)
        else:
            raise ValueError(f"Pooling strategy {self.pooling} is not supported")

        # normalize embeddings
        if self.normalize:
            return embeds / embeds.norm(dim=-1, keepdim=True).clamp(min=1.0)
        else:
            return embeds

    def _embed(self, input_ids: Tensor, attention_mask: Tensor) -> Tensor:
        dimensions = len(input_ids.shape)
        if dimensions == 1:
            # if input_ids is a 1D tensor, unsqueeze it to 2D for encoding
            input_ids = input_ids.unsqueeze(0)
            attention_mask = attention_mask.unsqueeze(0)
            last_hidden_state = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
            return self._pool_and_normalize(last_hidden_state, attention_mask).squeeze(0)
        elif dimensions == 2:
            last_hidden_state = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
            return self._pool_and_normalize(last_hidden_state, attention_mask)
        elif dimensions == 3:
            # if input_ids is a 3D tensor, flatten it to 2D for encoding
            shape = input_ids.shape
            input_ids = input_ids.view(shape[0] * shape[1], shape[2])
            attention_mask = attention_mask.view(shape[0] * shape[1], shape[2])
            last_hidden_state = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
            return self._pool_and_normalize(last_hidden_state, attention_mask).view(shape[0], shape[1], -1)
        else:
            raise ValueError(f"Input tensor must be 1D, 2D or 3D, got {dimensions}D")

    def forward(self, input_ids: Tensor, attention_mask: Tensor) -> Tensor:
        """
        Compute embeddings for the input tokens

        Args:
            input_ids: input token ids, long tensor of shape batch_size (x memory_count) x max_token_length
            attention_mask: input mask, float tensor of shape batch_size (x memory_count) x max_token_length

        Returns:
            embeddings for the input tokens, float tensor of shape batch_size (x memory_count) x embedding_dim
        """
        if self.frozen:
            with torch.no_grad():
                return self._embed(input_ids, attention_mask)
        else:
            return self._embed(input_ids, attention_mask)

    @torch.no_grad()
    def encode(self, text: str | list[str] | list[list[str]]) -> Tensor:
        """
        Encode the input text into embeddings

        Note:
            This method is not differentiable and should only be used for inference.

        Args:
            text: the text to encode, can be a single string or a batch of strings, or a batch of list of strings (for batches of memories)

        Returns:
            embeddings for the input text, float tensor of shape (x batch_size) (x memory_count) x embedding_dim
        """
        input_ids, attention_mask = self.tokenize(text, return_tensors=True)
        return self.forward(input_ids, attention_mask)
