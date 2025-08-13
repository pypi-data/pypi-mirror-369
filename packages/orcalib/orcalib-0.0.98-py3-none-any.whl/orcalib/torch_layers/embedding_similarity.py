from abc import ABC, abstractmethod

import torch
from torch import Tensor, nn


class EmbeddingSimilarity(nn.Module, ABC):
    """
    Abstract class for computing similarity between input and memory embeddings.
    """

    @abstractmethod
    def forward(self, input_embeddings: Tensor, memories_embeddings: Tensor) -> Tensor:
        """
        Compute similarity scores between the given input and memory embeddings

        Args:
            input_embedding: input embeddings, float tensor of shape batch_size x embedding_dim
            memories_embedding: memory embeddings, float tensor of shape batch_size (x memory_count) x embedding_dim

        Returns:
            similarity scores between 0 and 1 for each memory in each batch, float tensor of shape batch_size (x memory_count)
        """
        raise NotImplementedError


class FeedForwardSimilarity(EmbeddingSimilarity):
    """
    Module to compute the similarity between input and memory embeddings using a feedforward network
    with two hidden layers and an output layer that returns sigmoid activated scores between 0 and 1.

    Warning:
        Unlike other similarity heads, this layer has trainable parameters and will not output
        meaningful similarity scores unless trained on a dataset of input-memory pairs.
    """

    def __init__(self, embedding_dim: int):
        super().__init__()
        self.head = nn.Sequential(
            nn.Dropout(0.1),
            # hidden layers
            nn.Linear(embedding_dim * 2, embedding_dim),
            nn.ReLU(),
            nn.LayerNorm(embedding_dim),
            nn.Linear(embedding_dim, embedding_dim),
            nn.ReLU(),
            nn.LayerNorm(embedding_dim),
            # output layer
            nn.Linear(embedding_dim, 1),
            nn.Sigmoid(),
        )

    def forward(self, input_embeddings: Tensor, memories_embeddings: Tensor) -> Tensor:
        if len(memories_embeddings.shape) == 3:
            # Expand input_embedding to match the shape of memories_embedding
            input_embeddings = input_embeddings.unsqueeze(1).expand(-1, memories_embeddings.size(1), -1)
        # Concatenate along the last dimension
        combined = torch.cat([input_embeddings, memories_embeddings], dim=-1)
        return self.head(combined).squeeze(-1)


class CosineSimilarity(EmbeddingSimilarity):
    """
    A shallow wrapper around torch.nn.CosineSimilarity that supports scoring multiple memories at once.
    """

    def __init__(self):
        super().__init__()
        self.head = nn.CosineSimilarity(dim=-1)

    def forward(self, input_embeddings: Tensor, memories_embeddings: Tensor) -> Tensor:
        # Use broadcasting to compute cosine similarity
        return self.head(
            input_embeddings.unsqueeze(1) if len(memories_embeddings.shape) == 3 else input_embeddings,
            memories_embeddings,
        )


class InnerProductSimilarity(EmbeddingSimilarity):
    """
    Module to compute the inner product between input and memory embeddings.

    Note:
        Inner product is equivalent to cosine similarity when the input embeddings are normalized.
        It will only output scores between 0 and 1 when the input embeddings are normalized.
    """

    def __init__(self):
        super().__init__()

    def forward(self, input_embeddings: Tensor, memories_embeddings: Tensor) -> Tensor:
        if len(memories_embeddings.shape) == 3:
            return torch.bmm(
                input_embeddings.unsqueeze(1) if len(memories_embeddings.shape) == 3 else input_embeddings,
                memories_embeddings.transpose(1, 2),
            ).squeeze(1)
        else:
            return torch.sum(input_embeddings * memories_embeddings, dim=-1)
