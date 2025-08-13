"""
Smart batching utilities for optimizing memory usage during embedding operations.

This module provides utilities for creating intelligent batches that group items by similar
token lengths and use dynamic batch sizes to prevent batch poisoning from very long texts.
"""

# Default characters per token estimate for pre-truncation
DEFAULT_CHARS_PER_TOKEN = 4.0


def estimate_token_count_from_chars(text: str, chars_per_token: float = DEFAULT_CHARS_PER_TOKEN) -> int:
    """
    Estimate token count from character count using a rough heuristic.

    Args:
        text: The text to estimate tokens for
        chars_per_token: Average characters per token (empirically ~4.0 for most tokenizers)

    Returns:
        Estimated token count
    """
    return max(1, int(len(text) / chars_per_token))


def pre_truncate_text(text: str, max_tokens: int, chars_per_token: float = DEFAULT_CHARS_PER_TOKEN) -> str:
    """
    Pre-truncate text based on estimated token count to prevent excessive memory usage during tokenization.

    This is a heuristic approach that truncates based on character count before the expensive
    tokenization step. The actual model tokenizer will still apply exact truncation as a safety net.

    Args:
        text: The text to truncate
        max_tokens: Maximum number of tokens allowed
        chars_per_token: Average characters per token for estimation

    Returns:
        Truncated text that should be roughly within the token limit
    """
    if not text:
        return text

    estimated_tokens = estimate_token_count_from_chars(text, chars_per_token)
    if estimated_tokens <= max_tokens:
        return text

    # Add some buffer to the limit
    target_chars = int(max_tokens * chars_per_token * 0.9)

    # Truncate at word boundaries when possible to preserve readability
    if len(text) <= target_chars:
        return text

    truncated = text[:target_chars]

    # Try to truncate at the last complete word to avoid cutting words in half
    last_space = truncated.rfind(" ")
    if last_space > target_chars * 0.8:  # Only use word boundary if it's not too far back
        truncated = truncated[:last_space]

    return truncated


def batch_by_token_length[T](
    items: list[T],
    base_batch_size: int = 32,
    max_tokens_per_batch: int = 8192,
    value_prop: str = "value",
    prompt: str = "",
) -> list[list[T]]:
    """
    Batch items by token length using dynamic batch sizes to optimize memory usage.

    Groups items by similar token lengths and uses adaptive batch sizing to prevent
    batch poisoning from very long texts that can cause memory spikes during embedding.

    Note: This function assumes all items have string values.

    Args:
        items: List of items to batch
        base_batch_size: Base batch size for medium-length texts
        max_tokens_per_batch: Maximum total estimated tokens per batch. Should typically be set to
            embedding_model.max_seq_length * base_batch_size to align with model capabilities.
        value_prop: Property name to use for value
        prompt: Prompt that will be prepended to the value for token estimation.

    Returns:
        List of batches, where each batch is a list of items grouped by similar token lengths

    Examples:
        >>> items = [item1, item2, item3]  # items with .value attribute
        >>> # Use model's context window for optimal batching
        >>> max_tokens = model.max_seq_length * 32  # e.g., 512 * 32 = 16384
        >>> batches = batch_by_token_length(items, base_batch_size=32, max_tokens_per_batch=max_tokens)
        >>> for batch in batches:
        ...     process_batch(batch)
    """
    if not items:
        return []

    # All values are strings - proceed with smart token-based batching
    items_with_tokens = []
    for i, item in enumerate(items):
        value = getattr(item, value_prop)
        assert isinstance(value, str)
        token_count = estimate_token_count_from_chars(prompt + value)
        items_with_tokens.append((token_count, i, item))

    # Sort by token count for length-based grouping (shortest first to prevent batch poisoning)
    items_with_tokens.sort(key=lambda x: (x[0], x[1]))  # Sort by token count, then by index for stability

    batches = []
    current_batch = []
    current_batch_tokens = 0

    for token_count, _, item in items_with_tokens:
        # Calculate dynamic batch size based on token length
        if token_count <= 100:
            # Short texts: Use larger batches
            max_batch_size = base_batch_size * 2  # 64
        elif token_count <= 512:
            # Medium texts: Use base batch size
            max_batch_size = base_batch_size  # 32
        elif token_count <= 1024:
            # Long texts: Use smaller batches
            max_batch_size = base_batch_size // 2  # 16
        else:
            # Very long texts: Use very small batches
            max_batch_size = base_batch_size // 4  # 8

        # Check if adding this item would exceed limits
        would_exceed_size = len(current_batch) >= max_batch_size
        would_exceed_tokens = current_batch_tokens + token_count > max_tokens_per_batch

        if current_batch and (would_exceed_size or would_exceed_tokens):
            # Start new batch
            batches.append(current_batch)
            current_batch = [item]
            current_batch_tokens = token_count
        else:
            # Add to current batch
            current_batch.append(item)
            current_batch_tokens += token_count

    # Add the last batch if it's not empty
    if current_batch:
        batches.append(current_batch)

    return batches


def estimate_batch_memory_usage(
    items: list, chars_per_token: float = 4.0, value_prop: str = "value", prompt: str = ""
) -> tuple[int, int, int]:
    """
    Estimate memory usage characteristics for a batch of items.

    Note: This function assumes all items have string values.
    Args:
        items: List of items to analyze
        chars_per_token: Average characters per token for estimation
        value_prop: Property name to use for value
        prompt: Prompt that will be prepended to the value for token estimation.

    Returns:
        Tuple of (total_estimated_tokens, max_item_tokens, min_item_tokens)
    """
    if not items:
        return 0, 0, 0

    token_counts = []
    for item in items:
        value = getattr(item, value_prop)
        assert isinstance(value, str)
        token_count = estimate_token_count_from_chars(prompt + value, chars_per_token)
        token_counts.append(token_count)

    return sum(token_counts), max(token_counts), min(token_counts)
