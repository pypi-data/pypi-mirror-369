import pytest
import torch
import torch.nn as nn
from torch.optim.adam import Adam

from .embedding_generation import SentenceEmbeddingGenerator


@pytest.fixture
def encoder():
    encoder = SentenceEmbeddingGenerator(base_model="distilbert-base-uncased", max_sequence_length=64)
    return encoder


def test_tokenize_string(encoder):
    # When tokenizing a single sentence
    tokens = encoder.tokenize("Hello, world!")
    # Then the output should contain the input ids and attention mask
    assert "input_ids" in tokens
    assert "attention_mask" in tokens
    # And the input ids should be a list of integers
    assert isinstance(tokens["input_ids"], list)
    assert all(isinstance(i, int) for i in tokens["input_ids"])
    # And the attention mask should be a list of 1s and 0s
    assert isinstance(tokens["attention_mask"], list)
    assert all(i in [0, 1] for i in tokens["attention_mask"])
    # And the length of the input ids should be equal to the length of the attention mask
    assert len(tokens["input_ids"]) == len(tokens["attention_mask"])


def test_tokenize_input_batch(encoder):
    # When tokenizing a batch of sentences
    tokens = encoder.tokenize(["I1", "I2"], name="input")
    # Then the output should be a matrix
    input_ids = torch.tensor(tokens["input_ids"])
    input_mask = torch.tensor(tokens["input_mask"])
    assert input_ids.shape == input_mask.shape
    assert len(input_ids.shape) == 2
    # And the first dimension should be the batch size
    assert input_ids.shape[0] == 2
    # And the second dimension should be the token count of the longest sentence in the batch
    assert input_ids.shape[1] < encoder.max_sequence_length


def test_tokenize_memories_batch(encoder):
    # When tokenizing a batch of memories
    tokens = encoder.tokenize([["I1 M1", "I1 M2"], ["I2 M1", "I2 M2"], ["I3 M1", "I3 M2"]], name="memories")
    # Then the output should be a 3D-tensor
    memories_ids = torch.tensor(tokens["memories_ids"])
    memories_mask = torch.tensor(tokens["memories_mask"])
    assert memories_ids.shape == memories_mask.shape
    assert len(memories_ids.shape) == 3
    # And the first dimension should be the batch size
    assert memories_ids.shape[0] == 3
    # And the second dimension should be the number of memories
    assert memories_ids.shape[1] == 2
    # And the third dimension should be the token count of the longest sentence in the batch
    assert memories_ids.shape[2] < encoder.max_sequence_length


def test_encode_string(encoder):
    # When encoding a single sentence
    embedding = encoder.encode("Hello, world!")
    # Then the output should be a tensor
    assert isinstance(embedding, torch.Tensor)
    assert embedding.shape == (encoder.embedding_dim,)


def test_encode_batch_strings(encoder):
    # When encoding a batch of sentences
    embeddings = encoder.encode(["Hello, world!", "Hello, universe!"])
    # Then the output should be a tensor
    assert isinstance(embeddings, torch.Tensor)
    assert embeddings.shape == (2, encoder.embedding_dim)


def test_encode_batch_memories(encoder):
    # When encoding a batch of memories
    embeddings = encoder.encode([["I1 M1", "I1 M2"], ["I2 M1", "I2 M2"], ["I3 M1", "I3 M2"]])
    # Then the output should be a tensor
    assert isinstance(embeddings, torch.Tensor)
    assert embeddings.shape == (3, 2, encoder.embedding_dim)


def test_can_be_fine_tuned(encoder):
    # Given a model with an unfrozen encoder and a linear head
    encoder.frozen = False
    head = nn.Linear(encoder.embedding_dim, 2)
    optimizer = Adam([*encoder.parameters(), *head.parameters()])
    # And an encoded input
    input_ids, attention_mask = encoder.tokenize(["This is good", "This is bad"], return_tensors=True)
    # When calling the encoder's forward method
    input_embeds = encoder(input_ids, attention_mask).cpu()
    # Then the output should be the input embeddings
    assert input_embeds.shape == (2, encoder.embedding_dim)
    # And the output should be differentiable
    logits = head(input_embeds).softmax(dim=-1)
    loss = nn.functional.cross_entropy(logits, torch.tensor([0, 1]))
    loss.backward()
    optimizer.step()


def test_normalized_embeddings(encoder):
    # Given an encoder that is set to normalize
    encoder.normalize = True
    # When encoding a single sentence
    embedding = encoder.encode("Hello, world!")
    # Then the output tensor should be normalized
    assert embedding.shape == (encoder.embedding_dim,)
    assert torch.allclose(embedding.norm(), torch.tensor(1.0))


def test_mean_pooling(encoder):
    # Given an encoder that is set to mean pooling
    encoder.pooling = "mean"
    # When encoding a single sentence
    mean_pooling_embedding = encoder.encode("Hello, world!")
    # Then the embeddings should be using mean pooling
    assert mean_pooling_embedding.shape == (encoder.embedding_dim,)
    encoder.pooling = "cls"
    cls_embedding = encoder.encode("Hello, world!")
    assert mean_pooling_embedding.shape == cls_embedding.shape
    assert not torch.allclose(mean_pooling_embedding, cls_embedding)


def test_get_max_sequence_length(encoder):
    # Given a sentence with a certain token count
    sentence, token_count = "Hello, world!", 6
    # When getting the max sequence length for a list of sentences
    max_length = encoder.get_max_sequence_length([sentence, "Hi"])
    # Then the result should be the maximum of the token counts of the sentences
    assert max_length == token_count
    # When getting the max sequence length for a list of sentences that exceed the tokenizer's model_max_length
    max_length = encoder.get_max_sequence_length(["Hello, world!" * 1000])
    # Then the max sequence length should be equal to the tokenizer's model_max_length
    assert max_length == encoder.tokenizer.model_max_length


@pytest.mark.parametrize("sequence_length", [3, 20])
def test_fixed_length_tokenization(encoder, sequence_length):
    # Given a sentence with a certain token count
    sentence = "Hello, world!"
    token_count = encoder.get_max_sequence_length([sentence])
    # When tokenizing a single sentence with a fixed sequence length
    tokens = encoder.tokenize("Hello, world!", sequence_length=sequence_length)
    # Then the output has the given sequence length
    assert len(tokens["input_ids"]) == len(tokens["attention_mask"]) == sequence_length
    # And the attention mask is correct
    assert tokens["attention_mask"] == [1] * min(sequence_length, token_count) + [0] * max(
        0, sequence_length - token_count
    )
