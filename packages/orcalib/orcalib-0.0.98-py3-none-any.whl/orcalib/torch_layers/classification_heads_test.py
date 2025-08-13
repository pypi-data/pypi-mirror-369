import torch

from .classification_heads import (
    FeedForwardClassificationHead,
    MemoryMixtureOfExpertsClassificationHead,
    NearestMemoriesClassificationHead,
)


def test_mmoe_head():
    # Given an MMOE head
    embedding_dim = 128
    num_classes = 4
    memory_count = 5
    batch_size = 2
    mmoe_head = MemoryMixtureOfExpertsClassificationHead(embedding_dim=embedding_dim, num_classes=num_classes)
    # And a batch of memories and an input embedding
    memories_labels = torch.tensor([[1, 1, 2, 0, 1], [1, 2, 0, 2, 2]])
    assert memories_labels.shape == (batch_size, memory_count)
    input_embeds = torch.rand(batch_size, embedding_dim)
    memories_embeds = torch.rand(batch_size, memory_count, embedding_dim)
    # When the forward method is called
    logits = mmoe_head.forward(
        input_embeddings=input_embeds,
        memories_labels=memories_labels,
        memories_embeddings=memories_embeds,
    )
    # Then the logits should be a tensor of shape batch_size x num_classes
    assert logits.shape == (batch_size, num_classes)
    # And the correct labels should be predicted as if it is a KNN head
    assert torch.argmax(logits, dim=1).tolist() == [1, 2]
    # And the last memory weights should be a tensor of shape batch_size x memory_count
    assert mmoe_head.last_memories_attention_weights is not None
    assert mmoe_head.last_memories_attention_weights.shape == (batch_size, memory_count)


def test_simple_knn_head():
    # Given a KNN head
    num_classes = 3
    batch_size = 2
    memory_count = 5
    knn_head = NearestMemoriesClassificationHead(num_classes=num_classes)
    # And a batch of memory labels
    memories_labels = torch.tensor([[1, 1, 2, 0, 1], [1, 2, 0, 2, 2]])
    assert memories_labels.shape == (batch_size, memory_count)
    # When the forward method is called
    logits = knn_head.forward(memories_labels=memories_labels)
    # Then the logits should be a tensor of shape batch_size x num_classes
    assert logits.shape == (batch_size, num_classes)
    # And the correct labels should be predicted
    assert logits.allclose(torch.tensor([[0.2, 0.6, 0.2], [0.2, 0.2, 0.6]]))
    assert torch.argmax(logits, dim=1).tolist() == [1, 2]
    # And the sum of the logits should be 1 for each batch
    assert logits.sum(dim=1).tolist() == [1, 1]


def test_weighted_knn_head():
    # Given a weighted KNN head
    num_classes = 3
    batch_size = 2
    memory_count = 5
    knn_head = NearestMemoriesClassificationHead(num_classes=num_classes, weigh_memories=True)
    # And a batch of memory labels and weights
    memories_labels = torch.tensor([[1, 0, 2, 0, 2], [1, 1, 1, 2, 2]])
    assert memories_labels.shape == (batch_size, memory_count)
    memories_weights = torch.tensor([[0.9, 0.1, 0.3, 0.3, 0.5], [0.1, 0.2, 0.3, 0.6, 0.01]])
    assert memories_weights.shape == (batch_size, memory_count)
    # When the forward method is called
    logits = knn_head.forward(memories_labels=memories_labels, memories_weights=memories_weights)
    # Then the logits should be a tensor of shape batch_size x num_classes
    assert logits.shape == (batch_size, num_classes)
    # And the correct labels should be predicted
    assert torch.argmax(logits, dim=1).tolist() == [1, 2]
    # And the logits should reflect the confidence of the predictions
    assert logits.allclose(torch.tensor([[0.4 / 5, 0.9 / 5, 0.8 / 5], [0, 0.6 / 5, 0.61 / 5]]))


def test_cutoff_knn_head():
    # Given a KNN head with a cutoff
    num_classes = 3
    batch_size = 2
    memory_count = 5
    knn_head = NearestMemoriesClassificationHead(num_classes=num_classes, min_memory_weight=0.5)
    # And a batch of memory labels and weights
    memories_labels = torch.tensor([[1, 0, 0, 2, 2], [1, 1, 1, 2, 2]])
    assert memories_labels.shape == (batch_size, memory_count)
    memories_weights = torch.tensor([[0.9, 0.4, 0.4, 0.4, 0.3], [0.6, 0.3, 0.4, 0.5, 0.5]])
    assert memories_weights.shape == (batch_size, memory_count)
    # When the forward method is called
    logits = knn_head.forward(memories_labels=memories_labels, memories_weights=memories_weights)
    # Then the logits should be a tensor of shape batch_size x num_classes
    assert logits.shape == (batch_size, num_classes)
    # And the correct labels should be predicted
    assert torch.argmax(logits, dim=1).tolist() == [1, 2]
    # And the logits should reflect the confidence of the predictions
    assert logits.allclose(torch.tensor([[0, 1, 0], [0, 1 / 3, 2 / 3]]))


def test_cutoff_weighted_knn_head():
    # Given a KNN head with a cutoff
    num_classes = 3
    batch_size = 2
    memory_count = 5
    knn_head = NearestMemoriesClassificationHead(num_classes=num_classes, min_memory_weight=0.5, weigh_memories=True)
    # And a batch of memory labels and weights
    memories_labels = torch.tensor([[1, 0, 0, 0, 2], [1, 1, 1, 2, 2]])
    assert memories_labels.shape == (batch_size, memory_count)
    memories_weights = torch.tensor([[0.9, 0.4, 0.4, 0.4, 0.8], [0.5, 0.5, 0.5, 0.8, 0.8]])
    assert memories_weights.shape == (batch_size, memory_count)
    # When the forward method is called
    logits = knn_head.forward(memories_labels=memories_labels, memories_weights=memories_weights)
    # Then the logits should be a tensor of shape batch_size x num_classes
    assert logits.shape == (batch_size, num_classes)
    # And the correct labels should be predicted
    assert torch.argmax(logits, dim=1).tolist() == [1, 2]
    # And the logits should reflect the confidence of the predictions
    assert logits.allclose(torch.tensor([[0, 0.9 / 2, 0.8 / 2], [0, 1.5 / 5, 1.6 / 5]]))


def test_cutoff_weighted_knn_head_zero_confidence():
    # Given a KNN head with a cutoff
    num_classes = 3
    memory_count = 5
    knn_head = NearestMemoriesClassificationHead(num_classes=num_classes, min_memory_weight=0.5, weigh_memories=True)
    # And an input where all weights fall below the threshold
    memories_labels = torch.tensor([[1, 0, 0, 0, 2]])
    assert memories_labels.shape == (1, memory_count)
    memories_weights = torch.tensor([[0.3, 0.1, 0.1, 0.2, 0.2]])
    assert memories_weights.shape == (1, memory_count)
    # When the forward method is called
    logits = knn_head.forward(memories_labels=memories_labels, memories_weights=memories_weights)
    assert not torch.isnan(logits).any()
    # Then the logits should be a tensor of shape batch_size x num_classes
    assert logits.shape == (1, num_classes)
    # And the label is predicted to be the most common label
    assert torch.argmax(logits, dim=1).tolist() == [0]
    # But the prediction in the confidence is approximately 0
    assert logits.allclose(torch.tensor([[0.0, 0.0, 0.0]]))


def test_ff_head():
    # Given a feedforward head
    embedding_dim = 128
    num_classes = 4
    batch_size = 2
    ff_head = FeedForwardClassificationHead(embedding_dim=embedding_dim, num_classes=num_classes)
    # And a batch of input embeddings
    input_embeddings = torch.rand(batch_size, embedding_dim)
    # When the forward method is called
    logits = ff_head.forward(input_embeddings=input_embeddings)
    # Then the logits should be a tensor of shape batch_size x num_classes
    assert logits.shape == (batch_size, num_classes)
    # And the sum of the logits should be 1 for each batch
    assert logits.sum(dim=1).allclose(torch.tensor([1.0, 1.0]))


def test_ff_head_with_custom_dimensions():
    # When a feedforward head is instantiated with custom dimensions
    embedding_dim = 128
    layer_dims = [256, 64, 32]
    num_classes = 4
    ff_head = FeedForwardClassificationHead(embedding_dim=embedding_dim, num_classes=num_classes, layer_dims=layer_dims)
    # Then the head should be instantiated with the correct number of layers
    assert ff_head.num_layers == len(layer_dims)
    # And the layers should have the correct dimensions
    assert ff_head.layer_dims == [
        (embedding_dim, layer_dims[0]),
        (layer_dims[0], layer_dims[1]),
        (layer_dims[1], layer_dims[2]),
    ]
