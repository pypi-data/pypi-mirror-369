import torch
from torch import Tensor, nn


class GatherTopK(nn.Module):
    last_indices: Tensor | None
    """Indices of the last top k elements selected"""

    def __init__(self, k: int):
        """
        Select the top elements based on the weights

        Args:
            k: number of top elements to select
        """
        super().__init__()
        self.k = k
        self.last_indices = None

    def forward(
        self,
        weights: Tensor,
        *other_props: Tensor,
    ) -> tuple[Tensor, ...]:
        """
        Select the top memories based on the weights and return their properties

        Args:
            weights: weights to sort selection by, float tensor of shape batch_size x num_total
            other_props: other properties to select with shape batch_size x num_total (x optional_dim)

        Returns:
            tuple of properties with the top elements selected, always including the weights as the first element, shape batch_size x num_top (x optional_dim)

        Examples:
            >>> selector = GatherTopK(2)
            >>> selector(
            ...     torch.tensor([[0.1, 0.2, 0.3], [0.3, 0.2, 0.1]]),
            ...     torch.tensor([[1, 2, 3], [3, 2, 1]]),
            ...     torch.tensor([[4, 5, 6], [6, 5, 4]]),
            ... )
            (tensor([[0.2, 0.3], [0.3, 0.2]]), tensor([[2, 3], [3, 2]]), tensor([[5, 6], [6, 5]]))
        """
        selected_weights, idxs = torch.topk(weights, self.k, dim=1)
        self.last_indices = idxs
        return (
            selected_weights,
            *(  # expand the indices if the property has more than 2 dimensions
                torch.gather(p, 1, idxs.unsqueeze(-1).expand(-1, -1, p.size(-1)) if len(p.shape) > 2 else idxs)
                for p in other_props
            ),
        )
