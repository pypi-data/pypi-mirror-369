import torch

from .gather_top_k import GatherTopK


def test_gather_top_k():
    # Given a top k selector
    selector = GatherTopK(k=2)
    # And a set of weights and other properties
    weights = torch.tensor([[0.1, 0.2, 0.3], [0.3, 0.2, 0.1]])
    assert weights.shape == (2, 3)
    prop_2d = torch.tensor([[11, 12, 13], [21, 22, 23]])
    assert prop_2d.shape == (2, 3)
    prop_3d = torch.tensor(
        [
            [[111, 112, 113, 114], [121, 122, 123, 124], [131, 132, 133, 134]],
            [[211, 212, 213, 214], [221, 222, 223, 224], [231, 232, 233, 234]],
        ]
    )
    assert prop_3d.shape == (2, 3, 4)
    # When selecting the top k elements
    top_weights, top_prop_2d, top_prop_3d = selector(weights, prop_2d, prop_3d)
    # Then the selected elements should be the elements with the best weights in order
    assert torch.allclose(top_weights, torch.tensor([[0.3, 0.2], [0.3, 0.2]]))
    assert torch.allclose(top_prop_2d, torch.tensor([[13, 12], [21, 22]]))
    assert torch.allclose(
        top_prop_3d,
        torch.tensor(
            [
                [[131, 132, 133, 134], [121, 122, 123, 124]],
                [[211, 212, 213, 214], [221, 222, 223, 224]],
            ]
        ),
    )
    # And the selected indices should be set on the selector
    assert selector.last_indices is not None
    assert torch.allclose(selector.last_indices, torch.tensor([[2, 1], [0, 1]]))
