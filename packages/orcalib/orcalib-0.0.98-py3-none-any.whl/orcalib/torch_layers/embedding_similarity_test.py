import pytest
import torch

from .embedding_similarity import (
    CosineSimilarity,
    FeedForwardSimilarity,
    InnerProductSimilarity,
)

BATCH_SIZE = 4
NUM_MEMORIES = 9
EMBEDDING_DIM = 128


# TODO: support "single_pair" and "single_multi_memory"
@pytest.fixture(params=["batched_multi_memory", "batched_pair"])
def inputs(request):
    batched = request.param.startswith("batched")
    multi_memory = request.param.endswith("multi_memory")
    if batched:
        input_embeddings = torch.rand(BATCH_SIZE, EMBEDDING_DIM)
    else:
        input_embeddings = torch.rand(EMBEDDING_DIM)
    if multi_memory:
        memories_embeddings = torch.rand(BATCH_SIZE, NUM_MEMORIES, EMBEDDING_DIM)
    else:
        memories_embeddings = torch.rand(BATCH_SIZE, EMBEDDING_DIM)
    return input_embeddings, memories_embeddings, batched, multi_memory


def test_feed_forward_similarity(inputs):
    input_embeddings, memories_embeddings, batched, multi_memory = inputs
    # Given a linear reranking head
    head = FeedForwardSimilarity(embedding_dim=EMBEDDING_DIM)
    # When I pass it input and memory embeddings
    memories_weights = head.forward(input_embeddings, memories_embeddings)
    # Then it should return a tensor of shape (batch_size, memory_count)
    if batched:
        if multi_memory:
            assert memories_weights.shape == (BATCH_SIZE, NUM_MEMORIES)
        else:
            assert memories_weights.shape == (BATCH_SIZE,)
    else:
        if multi_memory:
            assert memories_weights.shape == (NUM_MEMORIES,)
        else:
            assert memories_weights.shape == ()
    # And the weights should be in the range [0, 1]
    assert torch.all(memories_weights >= 0)
    assert torch.all(memories_weights <= 1)


def test_cosine_similarity(inputs):
    input_embeddings, memories_embeddings, batched, multi_memory = inputs
    # Given a cosine reranking head
    head = CosineSimilarity()
    # When I pass it input and memory embeddings
    memories_weights = head.forward(input_embeddings, memories_embeddings)
    # Then it should return a tensor of shape (batch_size, memory_count)
    if batched:
        if multi_memory:
            assert memories_weights.shape == (BATCH_SIZE, NUM_MEMORIES)
        else:
            assert memories_weights.shape == (BATCH_SIZE,)
    else:
        if multi_memory:
            assert memories_weights.shape == (NUM_MEMORIES,)
        else:
            assert memories_weights.shape == ()
    # And the weights should be in the range [0, 1]
    assert torch.all(memories_weights >= 0)
    assert torch.all(memories_weights <= 1)


def test_inner_product_similarity(inputs):
    input_embeddings, memories_embeddings, batched, multi_memory = inputs
    # Given an inner product reranking head
    head = InnerProductSimilarity()
    # When I pass it normalized input and memory embeddings
    input_embeddings = input_embeddings / input_embeddings.norm(dim=-1, keepdim=True)
    memories_embeddings = memories_embeddings / memories_embeddings.norm(dim=-1, keepdim=True)
    memories_weights = head.forward(input_embeddings, memories_embeddings)
    # Then it should return a tensor of shape (batch_size, memory_count)
    if batched:
        if multi_memory:
            assert memories_weights.shape == (BATCH_SIZE, NUM_MEMORIES)
        else:
            assert memories_weights.shape == (BATCH_SIZE,)
    else:
        if multi_memory:
            assert memories_weights.shape == (NUM_MEMORIES,)
        else:
            assert memories_weights.shape == ()
    # And the weights should be in the range [0, 1]
    assert torch.all(memories_weights >= 0)
    assert torch.all(memories_weights <= 1)
