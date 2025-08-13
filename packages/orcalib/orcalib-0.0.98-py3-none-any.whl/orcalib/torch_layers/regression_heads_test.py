import torch

from .regression_heads import (
    MemoryMixtureOfExpertsRegressionHead,
    NearestMemoriesRegressionHead,
)


def test_mmoe_regression_head():
    # Given an MMOE regression head
    embedding_dim = 128
    memory_count = 5
    batch_size = 2
    mmoe_head = MemoryMixtureOfExpertsRegressionHead(embedding_dim=embedding_dim)
    # And a batch of memories and an input embedding
    memories_scores = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0], [2.0, 4.0, 6.0, 8.0, 10.0]])
    assert memories_scores.shape == (batch_size, memory_count)
    input_embeds = torch.rand(batch_size, embedding_dim)
    memories_embeds = torch.rand(batch_size, memory_count, embedding_dim)
    # When the forward method is called
    scores = mmoe_head.forward(
        input_embeddings=input_embeds,
        memories_scores=memories_scores,
        memories_embeddings=memories_embeds,
    )
    # Then the scores should be a tensor of shape batch_size
    assert scores.shape == (batch_size,)
    # And the scores should be weighted averages of the memory scores
    assert torch.all(scores >= torch.min(memories_scores, dim=1).values)
    assert torch.all(scores <= torch.max(memories_scores, dim=1).values)
    # And the last memory weights should be a tensor of shape batch_size x memory_count
    assert mmoe_head.last_memories_attention_weights is not None
    assert mmoe_head.last_memories_attention_weights.shape == (batch_size, memory_count)
    # And the memory weights should be non-negative (due to LeakyReLU)
    assert torch.all(mmoe_head.last_memories_attention_weights >= 0)


def test_mmoe_regression_head_single_memory():
    # Given an MMOE regression head
    embedding_dim = 128
    memory_count = 1
    batch_size = 2
    mmoe_head = MemoryMixtureOfExpertsRegressionHead(embedding_dim=embedding_dim)
    # And a batch with single memory per example
    memories_scores = torch.tensor([[2.5], [5.0]])
    assert memories_scores.shape == (batch_size, memory_count)
    input_embeds = torch.rand(batch_size, embedding_dim)
    memories_embeds = torch.rand(batch_size, memory_count, embedding_dim)
    # When the forward method is called
    scores = mmoe_head.forward(
        input_embeddings=input_embeds,
        memories_scores=memories_scores,
        memories_embeddings=memories_embeds,
    )
    # Then the scores should match the input scores (since there's only one memory per example)
    assert scores.shape == (batch_size,)
    assert torch.allclose(scores, memories_scores.squeeze(1))
    # And the last memory weights should be a tensor of shape batch_size x memory_count
    assert mmoe_head.last_memories_attention_weights is not None
    assert mmoe_head.last_memories_attention_weights.shape == (batch_size, memory_count)


def test_mmoe_regression_head_with_weights():
    # Given an MMOE regression head
    embedding_dim = 128
    memory_count = 3
    batch_size = 2
    mmoe_head = MemoryMixtureOfExpertsRegressionHead(embedding_dim=embedding_dim)
    # And a batch of memories with weights
    memories_scores = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert memories_scores.shape == (batch_size, memory_count)
    memories_weights = torch.tensor([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    assert memories_weights.shape == (batch_size, memory_count)
    input_embeds = torch.rand(batch_size, embedding_dim)
    memories_embeds = torch.rand(batch_size, memory_count, embedding_dim)
    # When the forward method is called with weights
    scores = mmoe_head.forward(
        input_embeddings=input_embeds,
        memories_scores=memories_scores,
        memories_embeddings=memories_embeds,
        memories_weights=memories_weights,
    )
    # Then the scores should be a tensor of shape batch_size
    assert scores.shape == (batch_size,)
    # And the scores should be weighted appropriately
    assert torch.all(scores >= torch.min(memories_scores, dim=1).values)
    assert torch.all(scores <= torch.max(memories_scores, dim=1).values)
    # And the last memory weights should be a tensor of shape batch_size x memory_count
    assert mmoe_head.last_memories_attention_weights is not None
    assert mmoe_head.last_memories_attention_weights.shape == (batch_size, memory_count)


def test_nearest_memories_regression_head():
    # Given a nearest memories regression head
    batch_size = 2
    memory_count = 5
    regression_head = NearestMemoriesRegressionHead()
    # And a batch of memory scores
    memories_scores = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0], [2.0, 4.0, 6.0, 8.0, 10.0]])
    assert memories_scores.shape == (batch_size, memory_count)
    # When the forward method is called
    scores = regression_head.forward(memories_scores=memories_scores)
    # Then the scores should be a tensor of shape batch_size
    assert scores.shape == (batch_size,)
    # And the scores should be the average of the memory scores
    expected_scores = torch.tensor([3.0, 6.0])  # (1+2+3+4+5)/5 = 3, (2+4+6+8+10)/5 = 6
    assert torch.allclose(scores, expected_scores)
    # And the last memory weights should be all ones
    assert regression_head.last_memories_attention_weights is not None
    assert regression_head.last_memories_attention_weights.shape == (batch_size, memory_count)
    assert torch.allclose(regression_head.last_memories_attention_weights, torch.ones_like(memories_scores))


def test_weighted_nearest_memories_regression_head():
    # Given a weighted nearest memories regression head
    batch_size = 2
    memory_count = 5
    regression_head = NearestMemoriesRegressionHead(weigh_memories=True)
    # And a batch of memory scores and weights
    memories_scores = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0], [2.0, 4.0, 6.0, 8.0, 10.0]])
    assert memories_scores.shape == (batch_size, memory_count)
    memories_weights = torch.tensor([[1.0, 1.0, 1.0, 1.0, 1.0], [0.5, 0.5, 0.5, 0.5, 0.5]])
    assert memories_weights.shape == (batch_size, memory_count)
    # When the forward method is called
    scores = regression_head.forward(memories_scores=memories_scores, memories_weights=memories_weights)
    # Then the scores should be a tensor of shape batch_size
    assert scores.shape == (batch_size,)
    # And the scores should be the weighted average of the memory scores
    expected_scores = torch.tensor([3.0, 6.0])  # First batch: normal average, second batch: same due to equal weights
    assert torch.allclose(scores, expected_scores)
    # And the last memory weights should reflect the input weights
    assert regression_head.last_memories_attention_weights is not None
    assert torch.allclose(regression_head.last_memories_attention_weights, memories_weights)


def test_cutoff_nearest_memories_regression_head():
    # Given a nearest memories regression head with a cutoff
    batch_size = 2
    memory_count = 5
    regression_head = NearestMemoriesRegressionHead(min_memory_weight=0.5)
    # And a batch of memory scores and weights
    memories_scores = torch.tensor([[1.0, 2.0, 3.0, 4.0, 5.0], [2.0, 4.0, 6.0, 8.0, 10.0]])
    assert memories_scores.shape == (batch_size, memory_count)
    memories_weights = torch.tensor([[0.9, 0.4, 0.6, 0.4, 0.8], [0.6, 0.3, 0.4, 0.5, 0.7]])
    assert memories_weights.shape == (batch_size, memory_count)
    # When the forward method is called
    scores = regression_head.forward(memories_scores=memories_scores, memories_weights=memories_weights)
    # Then the scores should be a tensor of shape batch_size
    assert scores.shape == (batch_size,)
    # And the scores should only consider memories above the threshold
    # First batch: memories at indices 0, 2, 4 (scores 1.0, 3.0, 5.0) -> average = 3.0
    # Second batch: memories at indices 0, 3, 4 (scores 2.0, 8.0, 10.0) -> average = 6.67
    expected_scores = torch.tensor([3.0, 20.0 / 3])
    assert torch.allclose(scores, expected_scores)
    # And the last memory weights should reflect the cutoff
    assert regression_head.last_memories_attention_weights is not None
    assert regression_head.last_memories_attention_weights.shape == (batch_size, memory_count)


def test_cutoff_weighted_nearest_memories_regression_head():
    # Given a weighted nearest memories regression head with a cutoff
    batch_size = 2
    memory_count = 3
    regression_head = NearestMemoriesRegressionHead(min_memory_weight=0.5, weigh_memories=True)
    # And a batch of memory scores and weights
    memories_scores = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert memories_scores.shape == (batch_size, memory_count)
    memories_weights = torch.tensor([[0.9, 0.4, 0.8], [0.5, 0.5, 0.7]])
    assert memories_weights.shape == (batch_size, memory_count)
    # When the forward method is called
    scores = regression_head.forward(memories_scores=memories_scores, memories_weights=memories_weights)
    # Then the scores should be a tensor of shape batch_size
    assert scores.shape == (batch_size,)
    # And the scores should be weighted averages considering only memories above threshold
    # First batch: memories at indices 0, 2 with weights 0.9, 0.8 and scores 1.0, 3.0
    # weighted sum = 0.9*1.0 + 0.8*3.0 = 3.3, weight sum = 1.7, average = 3.3/1.7
    # Second batch: all memories pass, weighted sum = 0.5*4.0 + 0.5*5.0 + 0.7*6.0 = 8.7, weight sum = 1.7, average = 8.7/1.7
    expected_scores = torch.tensor([3.3 / 1.7, 8.7 / 1.7])
    assert torch.allclose(scores, expected_scores, atol=1e-6)
    # And the last memory weights should reflect the cutoff and weighting
    assert regression_head.last_memories_attention_weights is not None
    assert regression_head.last_memories_attention_weights.shape == (batch_size, memory_count)
