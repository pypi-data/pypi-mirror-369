from abc import ABC, abstractmethod

import torch
from torch import Tensor, nn


class RegressionHead(ABC, nn.Module):
    def __init__(self):
        super().__init__()
        self.last_memories_attention_weights: Tensor | None = None  # batch_size x memory_count

    @abstractmethod
    def forward(
        self,
        input_embeddings: Tensor | None = None,
        memories_scores: Tensor | None = None,
        memories_embeddings: Tensor | None = None,
        memories_weights: Tensor | None = None,
    ) -> Tensor:
        """
        Compute the output score by mixing the memories based on the input embedding

        Args:
            memories_scores: scores of the memories, float tensor of shape batch_size x memory_count
            input_embeddings: embedding of the model input, float tensor of shape batch_size x embedding_dim
            memories_embeddings: embeddings of the memories, float tensor of shape batch_size x memory_count x embedding_dim
            memories_weights: optional weights for each memory should be between 0 and 1, float tensor of shape batch_size x memory_count

        Returns:
            predicted scores, float tensor of shape batch_size
        """
        raise NotImplementedError


class NearestMemoriesRegressionHead(RegressionHead):
    """
    Regression head that returns scores based on the scores of the nearest memories
    """

    def __init__(
        self,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
    ):
        """
        Initialize the regression head

        Args:
            weigh_memories: whether to weigh the memories with the passed in memories_weights
            min_memory_weight: optional minimum weight for a memory to contribute to the score
        """
        super().__init__()
        self.weigh_memories = weigh_memories
        self.min_memory_weight = min_memory_weight
        # dummy parameter to ensure that the dtype of the model can be detected
        self._dummy_param = nn.Parameter(torch.tensor(0.0), requires_grad=False)

    def forward(
        self,
        input_embeddings=None,
        memories_scores=None,
        memories_embeddings=None,
        memories_weights=None,
    ) -> Tensor:
        assert memories_scores is not None
        device = memories_scores.device
        batch_size = memories_scores.shape[0]
        memory_count = memories_scores.shape[1]

        if self.weigh_memories:
            assert memories_weights is not None
            self.last_memories_attention_weights = memories_weights
        else:
            self.last_memories_attention_weights = torch.ones_like(memories_scores, dtype=torch.float, device=device)

        if self.min_memory_weight is not None:
            assert memories_weights is not None
            # set memory weights that are less than min_memory_weight to minuscule values
            mask = memories_weights >= self.min_memory_weight
            # to ensure correct behavior, we don't completely ignore cutoff memories
            mask_weights = torch.where(mask, 1.0, 1e-10)
            self.last_memories_attention_weights = self.last_memories_attention_weights * mask_weights

        assert self.last_memories_attention_weights.shape == memories_scores.shape

        # Compute weighted average of memory scores
        weighted_scores = self.last_memories_attention_weights * memories_scores
        summed_scores = weighted_scores.sum(dim=1)  # batch_size

        # For weighted average, divide by sum of weights; for unweighted, divide by count
        if self.weigh_memories or self.min_memory_weight is not None:
            weight_sums = self.last_memories_attention_weights.sum(dim=1)  # batch_size
            scores = summed_scores / torch.where(weight_sums == 0, 1, weight_sums)
        else:
            memory_counts = torch.tensor([memory_count] * batch_size, device=device, dtype=torch.float)
            scores = summed_scores / memory_counts

        return scores


class MemoryMixtureOfExpertsRegressionHead(RegressionHead):
    """
    Regression head that returns scores based on scores of the memories weighted by learned
    weights that are a function of the input embedding and the memories embeddings
    """

    def __init__(self, embedding_dim: int):
        """
        Initialize the regression head

        Args:
            embedding_dim: dimension of the embeddings
        """
        super().__init__()
        self.embedding_dim = embedding_dim
        init_tensor = torch.nn.init.orthogonal_(torch.empty(embedding_dim, embedding_dim))
        self.memory_weights = nn.Parameter(init_tensor.clone().T.contiguous())
        self.input_weights = nn.Parameter(init_tensor.clone())
        self.nonlinear = nn.LeakyReLU()

    def forward(
        self,
        input_embeddings=None,
        memories_scores=None,
        memories_embeddings=None,
        memories_weights=None,
    ):
        assert input_embeddings is not None and memories_embeddings is not None and memories_scores is not None
        mmoe_memories_weights = self.nonlinear(
            torch.bmm(
                (input_embeddings @ self.input_weights).unsqueeze(1),
                self.memory_weights @ memories_embeddings.permute(0, 2, 1),
            )
        )  # batch_size x 1 x memory_count
        # Normalize the attention weights using softmax
        mmoe_memories_weights = torch.nn.functional.softmax(mmoe_memories_weights, dim=2)
        scores = torch.bmm(mmoe_memories_weights, memories_scores.unsqueeze(2)).squeeze(2).squeeze(1)  # batch_size
        self.last_memories_attention_weights = mmoe_memories_weights.squeeze(1)
        return scores
