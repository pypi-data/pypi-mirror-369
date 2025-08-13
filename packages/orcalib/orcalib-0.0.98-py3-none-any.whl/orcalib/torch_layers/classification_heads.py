from abc import ABC, abstractmethod

import torch
from torch import Tensor, nn


class ClassificationHead(ABC, nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()
        self.num_classes = num_classes
        self.last_memories_attention_weights: Tensor | None = None  # batch_size x memory_count

    @abstractmethod
    def forward(
        self,
        input_embeddings: Tensor | None = None,
        memories_labels: Tensor | None = None,
        memories_embeddings: Tensor | None = None,
        memories_weights: Tensor | None = None,
    ) -> Tensor:
        """
        Compute the logits for each class by mixing the memories based on the input embedding

        Args:
            memories_labels: class labels of the memories, long tensor of shape batch_size x memory_count
            input_embeddings: embedding of the model input, float tensor of shape batch_size x embedding_dim
            memories_embeddings: embeddings of the memories, float tensor of shape batch_size x memory_count x embedding_dim
            memories_weights: optional weights for each memory should be between 0 and 1, float tensor of shape batch_size x memory_count

        Returns:
            logits for each class, float tensor of shape batch_size x num_classes
        """
        raise NotImplementedError


class MemoryMixtureOfExpertsClassificationHead(ClassificationHead):
    """
    Classification head that returns logits based on labels of the memories weighted by learned
    weights that are a function of the input embedding and the memories embeddings
    """

    def __init__(self, embedding_dim: int, num_classes: int):
        """
        Initialize the classification head

        Args:
            embedding_dim: dimension of the embeddings
            num_classes: number of label classes
        """
        super().__init__(num_classes)
        self.embedding_dim = embedding_dim
        init_tensor = torch.nn.init.orthogonal_(torch.empty(embedding_dim, embedding_dim))
        self.memory_weights = nn.Parameter(init_tensor.clone().T.contiguous())
        self.input_weights = nn.Parameter(init_tensor.clone())
        self.nonlinear = nn.LeakyReLU()

    def forward(
        self,
        input_embeddings=None,
        memories_labels=None,
        memories_embeddings=None,
        memories_weights=None,
    ) -> Tensor:
        assert input_embeddings is not None and memories_embeddings is not None and memories_labels is not None
        one_hot_memory_labels = nn.functional.one_hot(memories_labels, self.num_classes).to(
            memories_embeddings.dtype
        )  # batch_size x memory_count x num_classes
        mmoe_memories_weights = self.nonlinear(
            torch.bmm(
                (input_embeddings @ self.input_weights).unsqueeze(1),
                self.memory_weights @ memories_embeddings.permute(0, 2, 1),
            )
        )  # batch_size x 1 x memory_count
        logits = (
            torch.bmm(mmoe_memories_weights, one_hot_memory_labels).squeeze(1).softmax(dim=1)
        )  # batch_size x num_classes
        self.last_memories_attention_weights = mmoe_memories_weights.squeeze(1)
        return logits


class BalancedMemoryMixtureOfExpertsClassificationHead(ClassificationHead):
    """
    Classification head that returns logits based on labels of the memories weighted by learned
    weights that are a function of the input embedding and the memories embeddings
    """

    def __init__(self, embedding_dim: int, num_classes: int):
        """
        Initialize the classification head

        Args:
            embedding_dim: dimension of the embeddings
            num_classes: number of label classes
        """
        super().__init__(num_classes)
        self.embedding_dim = embedding_dim
        init_tensor = torch.nn.init.orthogonal_(torch.empty(embedding_dim, embedding_dim))
        self.memory_weights = nn.Parameter(init_tensor.clone().T.contiguous())
        self.input_weights = nn.Parameter(init_tensor.clone())
        self.nonlinear = nn.LeakyReLU()

    def _per_label_normalization_factor(self, memories_labels):
        # count how often each label appears in each batch
        label_counts = torch.zeros(memories_labels.shape[0], self.num_classes, device=memories_labels.device).to(
            torch.long
        )
        label_factors = label_counts.scatter_add_(
            1, memories_labels, torch.ones_like(memories_labels, device=memories_labels.device)
        )
        return label_factors.where(
            label_factors != 0, 1
        )  # prevents division by zero for labels that don't appear in the batch

    def forward(
        self,
        input_embeddings=None,
        memories_labels=None,
        memories_embeddings=None,
        memories_weights=None,
    ) -> Tensor:
        assert input_embeddings is not None and memories_embeddings is not None and memories_labels is not None
        one_hot_memory_labels = nn.functional.one_hot(memories_labels, self.num_classes).to(
            memories_embeddings.dtype
        )  # batch_size x memory_count x num_classes
        mmoe_memories_weights = self.nonlinear(
            torch.bmm(
                (input_embeddings @ self.input_weights).unsqueeze(1),
                self.memory_weights @ memories_embeddings.permute(0, 2, 1),
            )
        )  # batch_size x 1 x memory_count
        logits = torch.bmm(mmoe_memories_weights, one_hot_memory_labels).squeeze(1)  # batch_size x num_classes
        logits = logits / self._per_label_normalization_factor(memories_labels)

        logits = logits.softmax(dim=1)
        self.last_memories_attention_weights = mmoe_memories_weights.squeeze(1)
        return logits


class NearestMemoriesClassificationHead(ClassificationHead):
    """
    Classification head that returns logits based on the labels of the nearest memories
    """

    def __init__(
        self,
        num_classes: int,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
    ):
        """
        Initialize the classification head

        Args:
            num_classes: number of label classes
            weigh_memories: whether to weigh the memories with the passed in memories_weights
            min_memory_weight: optional minimum weight for a memory to contribute to the logits
        """
        super().__init__(num_classes)
        self.weigh_memories = weigh_memories
        self.min_memory_weight = min_memory_weight
        # dummy parameter to ensure that the dtype of the model can be detected
        self._dummy_param = nn.Parameter(torch.tensor(0.0), requires_grad=False)

    def forward(
        self,
        input_embeddings=None,
        memories_labels=None,
        memories_embeddings=None,
        memories_weights=None,
    ) -> Tensor:
        assert memories_labels is not None
        device = memories_labels.device
        batch_size = memories_labels.shape[0]
        memory_count = memories_labels.shape[1]
        memory_counts = torch.tensor([memory_count] * batch_size, device=device)  # batch_size x 1

        if self.weigh_memories:
            assert memories_weights is not None
            self.last_memories_attention_weights = memories_weights
        else:
            self.last_memories_attention_weights = torch.ones_like(memories_labels, dtype=torch.float, device=device)

        if self.min_memory_weight is not None:
            assert memories_weights is not None
            # set memory weights that are less than min_memory_weight to minuscule values
            mask = memories_weights >= self.min_memory_weight
            # to ensure correct 0 confidence predictions, we don't completely ignore cutoff labels
            mask_weights = torch.where(mask, 1.0, 1e-10)
            self.last_memories_attention_weights = self.last_memories_attention_weights * mask_weights
            memory_counts = mask.sum(dim=1)

        assert self.last_memories_attention_weights.shape == memories_labels.shape
        logits = torch.zeros(batch_size, self.num_classes, device=device)  # batch_size x num_labels
        logits.scatter_add_(1, memories_labels, self.last_memories_attention_weights)
        # if memory count is zero, don't normalize by memory count the logit will be 0s already
        logits = logits / torch.where(memory_counts == 0, 1, memory_counts).unsqueeze(1)
        # ensure logits are between 0 and 1 if memory weights are
        return logits


class FeedForwardClassificationHead(ClassificationHead):
    """
    Classification head that returns logits based on a feedforward neural network over the input
    embeddings with a specified number of hidden layers. This includes activation functions,
    layer norms, and dropout.

    Note:
        Use this with `num_layers=0` for a logistic regression head.
    """

    def __init__(
        self,
        num_classes: int,
        embedding_dim: int,
        layer_dims: list[int] | int | None = None,
        num_layers: int | None = None,
        activation: nn.Module = nn.ReLU(),
        dropout_prob: float = 0.1,
        use_layer_norm: bool = True,
    ):
        """
        Initialize the classification head

        Args:
            num_classes: number of label classes
            embedding_dim: dimension of the embeddings
            layer_dims: dimensions of the layers, either a single int for all layers or a list of
                ints for each layer. If a list of ints is passed it will override the `num_layers`
            num_layers: number of layers to use in addition to the output layer, if neither
                `layer_dims` nor this is set, defaults to 2 layers
            activation: activation function to use for the layers
            dropout_prob: dropout probability, set to 0 to disable dropout
            use_layer_norm: whether to use layer normalization
        """
        super().__init__(num_classes)
        self.embedding_dim = embedding_dim
        self.dropout_prob = dropout_prob
        if layer_dims is None:
            self.num_layers = num_layers if num_layers is not None else 2
            self.layer_dims = [(embedding_dim, embedding_dim)] * self.num_layers
        elif isinstance(layer_dims, int):
            self.num_layers = num_layers if num_layers is not None else 2
            self.layer_dims = [(embedding_dim, layer_dims)] + [(layer_dims, layer_dims)] * self.num_layers
        elif isinstance(layer_dims, list):
            if num_layers is not None and num_layers != len(layer_dims):
                raise ValueError("`num_layers` must be `None` or match the length of `layer_dims` if both are provided")
            self.num_layers = len(layer_dims)
            self.layer_dims = [(embedding_dim, layer_dims[0])] + [
                (layer_dims[i], layer_dims[i + 1]) for i in range(self.num_layers - 1)
            ]

        self.head = nn.Sequential(
            *[
                nn.Sequential(
                    nn.Linear(dims[0], dims[1]),
                    activation,
                    nn.LayerNorm(dims[1]) if use_layer_norm else nn.Identity(),
                    nn.Dropout(dropout_prob) if dropout_prob > 0 else nn.Identity(),
                )
                for dims in self.layer_dims
            ],
            nn.Linear(self.layer_dims[-1][1], num_classes),
            nn.Softmax(dim=1),
        )

    def forward(
        self,
        input_embeddings=None,
        memories_labels=None,
        memories_embeddings=None,
        memories_weights=None,
    ) -> Tensor:
        assert input_embeddings is not None
        return self.head(input_embeddings)
