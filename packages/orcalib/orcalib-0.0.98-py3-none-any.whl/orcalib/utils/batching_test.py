from dataclasses import dataclass
from typing import Any

from .batching import (
    batch_by_token_length,
    estimate_token_count_from_chars,
    pre_truncate_text,
)


@dataclass
class MockItem:
    """Mock item with a value attribute for testing."""

    value: Any


def test_estimate_token_count_from_chars():
    """Test token count estimation from character count."""

    assert estimate_token_count_from_chars("hello") == 1  # 5 chars / 4 chars_per_token

    # Custom chars_per_token
    assert estimate_token_count_from_chars("hello world", chars_per_token=2) == 5  # 11 chars / 2

    # Empty string should return 1 (minimum)
    assert estimate_token_count_from_chars("") == 1

    # Very long text
    long_text = "word " * 100  # 500 chars
    assert estimate_token_count_from_chars(long_text) == 125  # 500 / 4 = 125


def test_pre_truncate_text():
    """Test text pre-truncation based on estimated tokens."""
    long_text = "word " * 200  # 1000 chars, 250 tokens

    # Should truncate for small token limit
    truncated = pre_truncate_text(long_text, max_tokens=50)
    assert len(truncated) < len(long_text)
    assert len(truncated) <= 50 * 4 * 0.9

    # Should not truncate short text
    short_text = "hello world"
    not_truncated = pre_truncate_text(short_text, max_tokens=50)
    assert not_truncated == short_text

    # Should handle empty text
    assert pre_truncate_text("", max_tokens=50) == ""

    # Should handle text that's exactly at the limit
    exact_text = "a" * (50 * 4)  # Exactly 50 estimated tokens
    result = pre_truncate_text(exact_text, max_tokens=50)
    assert result == exact_text


def test_batch_by_token_length_empty():
    """Test smart batching with empty input."""
    result = batch_by_token_length([])
    assert result == []


def test_batch_by_token_length_dynamic_batch_sizes():
    """Test that batch sizes adapt based on token length."""
    # Create items of different token lengths
    short_items = [MockItem(value="short") for _ in range(10)]  # ~1 token each
    long_items = [MockItem(value="very long text " * 100) for _ in range(10)]  # ~400 tokens each

    # Test short texts get larger batches
    short_batches = batch_by_token_length(short_items, base_batch_size=8)
    # Short texts should allow larger batches
    assert any(len(batch) > 8 for batch in short_batches)

    # Test long texts get smaller batches
    long_batches = batch_by_token_length(long_items, base_batch_size=8)
    # Long texts should get smaller batches
    assert all(len(batch) <= 8 for batch in long_batches)


def test_batch_by_token_length_token_limits():
    """Test that smart batching respects token limits."""
    # Create items that would exceed token limits if batched naively
    very_long_text = "word " * 1000  # Should be ~4000 tokens

    items = [MockItem(value=very_long_text) for _ in range(3)]

    batches = batch_by_token_length(items, base_batch_size=32, max_tokens_per_batch=5000)

    # Should create batches that respect token limits
    assert len(batches) >= 1  # At least 1 batch
    assert len(batches) <= 3  # At most one per item (due to token limit)

    # All items should be present across batches
    total_items = sum(len(batch) for batch in batches)
    assert total_items == 3
