import asyncio
from typing import cast
from unittest.mock import Mock, patch

import numpy as np
import pytest
from attr import dataclass
from uuid_utils.compat import uuid7

from ..memoryset import LabeledMemoryLookup  # Import for type hints
from .analysis_class_patterns import (
    MemoryClassPatternsMetrics,
    MemorysetClassPatternsAnalysis,
    MemorysetClassPatternsAnalysisConfig,
    MemorysetClassPatternsMetrics,
)


def test_class_patterns_analysis_config():
    """Test the configuration model."""
    config = MemorysetClassPatternsAnalysisConfig()
    assert config.representatives_per_class == 5
    assert config.enable_patterns_description is True

    config_custom = MemorysetClassPatternsAnalysisConfig(representatives_per_class=3, enable_patterns_description=False)
    assert config_custom.representatives_per_class == 3
    assert config_custom.enable_patterns_description is False


def test_class_patterns_analysis_initialization():
    """Test analysis initialization."""
    analysis = MemorysetClassPatternsAnalysis()
    assert analysis.config.representatives_per_class == 5
    assert analysis.config.enable_patterns_description is True
    assert analysis.name == "class_patterns"

    custom_config = MemorysetClassPatternsAnalysisConfig(representatives_per_class=3, enable_patterns_description=False)
    analysis_custom = MemorysetClassPatternsAnalysis(custom_config)
    assert analysis_custom.config.representatives_per_class == 3
    assert analysis_custom.config.enable_patterns_description is False


def test_on_batch_perfect_uniformity():
    """Test on_batch with perfect class uniformity."""
    analysis = MemorysetClassPatternsAnalysis()

    # Mock setup
    memory_id = uuid7()
    memory = Mock()
    memory.memory_id = memory_id
    memory.label = 0

    # All neighbors are same class
    neighbors = [Mock() for _ in range(5)]
    for neighbor in neighbors:
        neighbor.label = 0
        neighbor.lookup_score = 0.8

    # Test the method - using type: ignore to suppress type checker warnings for test mocks
    result = analysis.on_batch([memory], [neighbors])  # type: ignore

    # Verify results - on_batch returns list of tuples
    assert len(result) == 1
    result_memory_id, metrics = result[0]
    assert result_memory_id == memory_id
    assert metrics.uniformity == 1.0  # All neighbors same class
    assert abs(metrics.spread - 0.2) < 0.01  # Average distance to same-class neighbors (1 - 0.8)


def test_after_all_representative_selection():
    """Test that after_all selects the most representative memories correctly."""
    analysis = MemorysetClassPatternsAnalysis()
    analysis.config.representatives_per_class = 2

    # Mock memoryset
    analysis.memoryset = Mock()
    analysis.memoryset.label_names = ["positive", "negative"]
    analysis.memoryset.description = "sentiment analysis"

    # Create test data - mix of perfect and imperfect uniformity
    memory_ids = [uuid7() for _ in range(5)]

    # Class 0 (positive): 3 memories with perfect uniformity, different spreads
    analysis._all_metrics[memory_ids[0]] = (0, 0.1, 1.0)  # Best spread for class 0
    analysis._all_metrics[memory_ids[1]] = (0, 0.3, 1.0)  # Worst spread for class 0
    analysis._all_metrics[memory_ids[2]] = (0, 0.2, 1.0)  # Middle spread for class 0

    # Class 1 (negative): 1 memory with perfect uniformity
    analysis._all_metrics[memory_ids[3]] = (1, 0.15, 1.0)

    # Class 0: 1 memory with imperfect uniformity (should not be selected)
    analysis._all_metrics[memory_ids[4]] = (0, 0.05, 0.8)  # Best spread but imperfect uniformity

    # Mock memory retrieval
    def mock_get(memory_id):
        memory = Mock()
        memory.value = "Sample text"
        return memory

    analysis.memoryset.get = mock_get

    result = analysis.after_all()

    # Should select 2 best (lowest spread) perfect uniformity memories for class 0
    # and 1 memory for class 1
    class_0_representatives = next(cr for cr in result.class_representatives if cr.label == 0)
    class_1_representatives = next(cr for cr in result.class_representatives if cr.label == 1)

    assert len(class_0_representatives.representative_memory_ids) == 2
    assert len(class_1_representatives.representative_memory_ids) == 1

    # Should select memories with spreads 0.1 and 0.2 (best two with perfect uniformity)
    # NOT the one with spread 0.05 because it has imperfect uniformity
    assert memory_ids[0] in class_0_representatives.representative_memory_ids  # spread 0.1
    assert memory_ids[2] in class_0_representatives.representative_memory_ids  # spread 0.2
    assert memory_ids[4] not in class_0_representatives.representative_memory_ids  # spread 0.05 but uniformity 0.8

    assert memory_ids[3] in class_1_representatives.representative_memory_ids

    # Verify statistics include ALL metrics (including the imperfect uniformity one)
    # All spreads: [0.1, 0.3, 0.2, 0.15, 0.05] -> mean = 0.16
    assert abs(result.mean_spread - 0.16) < 0.001

    # All uniformities: [1.0, 1.0, 1.0, 1.0, 0.8] -> mean = 0.96
    assert abs(result.mean_uniformity - 0.96) < 0.001


def test_empty_neighbors():
    """Test handling of memories with no neighbors."""
    analysis = MemorysetClassPatternsAnalysis()

    memory_id = uuid7()
    memory = Mock()
    memory.memory_id = memory_id
    memory.label = 0

    # Empty neighbors list - using type: ignore for test mocks
    result = analysis.on_batch([memory], [[]])  # type: ignore

    # Should handle gracefully - on_batch returns list of tuples
    assert len(result) == 1
    result_memory_id, metrics = result[0]
    assert result_memory_id == memory_id
    assert metrics.uniformity == 0.0  # No neighbors = 0 uniformity
    assert metrics.spread == 0.0  # No same-class neighbors = 0 spread


def test_no_same_class_neighbors():
    """Test handling of memories where no neighbors have the same class."""
    analysis = MemorysetClassPatternsAnalysis()

    memory_id = uuid7()
    memory = Mock()
    memory.memory_id = memory_id
    memory.label = 0

    # All neighbors have different class
    neighbors = [Mock() for _ in range(3)]
    for neighbor in neighbors:
        neighbor.label = 1  # Different from memory.label
        neighbor.lookup_score = 0.7

    # Using type: ignore for test mocks
    result = analysis.on_batch([memory], [neighbors])  # type: ignore

    # Should handle gracefully - on_batch returns list of tuples
    assert len(result) == 1
    result_memory_id, metrics = result[0]
    assert result_memory_id == memory_id
    assert metrics.uniformity == 0.0  # No same-class neighbors
    assert metrics.spread == 1.0  # No same-class neighbors to compute distance to


def test_patterns_description_field():
    """Test that patterns_description field is included in the result."""
    analysis = MemorysetClassPatternsAnalysis()

    # Mock memoryset
    analysis.memoryset = Mock()
    analysis.memoryset.label_names = ["class_0"]
    analysis.memoryset.description = "test"

    # Add some metrics
    memory_id = uuid7()
    analysis._all_metrics[memory_id] = (0, 0.1, 1.0)

    # Mock memory retrieval to trigger agent attempt
    def mock_get(memory_id):
        memory = Mock()
        memory.value = "test value"
        return memory

    analysis.memoryset.get = mock_get

    # Mock the agent utility function to fail
    with patch("orcalib.analysis.analysis_class_patterns.run_agent_safely", side_effect=Exception("Agent failed")):
        result = analysis.after_all()

    # Should have patterns_description field (None due to agent failure)
    assert hasattr(result, "patterns_description")
    assert result.patterns_description is None

    # Should have the new statistics fields
    assert hasattr(result, "mean_spread")
    assert hasattr(result, "variance_spread")
    assert hasattr(result, "mean_uniformity")
    assert hasattr(result, "variance_uniformity")


def test_async_event_loop_handling():
    """Test that the analysis handles event loop contexts correctly."""
    analysis = MemorysetClassPatternsAnalysis()

    # Mock memoryset
    analysis.memoryset = Mock()
    analysis.memoryset.label_names = ["test_class"]
    analysis.memoryset.description = "test dataset"

    # Add some test data
    memory_id = uuid7()
    analysis._all_metrics[memory_id] = (0, 0.1, 1.0)

    def mock_get(memory_id):
        memory = Mock()
        memory.value = "test"
        return memory

    analysis.memoryset.get = mock_get

    # Test in a regular context (no running loop)
    result = analysis.after_all()
    assert isinstance(result, MemorysetClassPatternsMetrics)
    assert len(result.class_representatives) == 1
    # Statistics should be calculated
    assert result.mean_spread == 0.1
    assert result.mean_uniformity == 1.0

    # Test within an async context
    async def test_in_async_context():
        # This should still work (agent will be skipped but analysis completes)
        result = analysis.after_all()
        assert isinstance(result, MemorysetClassPatternsMetrics)
        assert len(result.class_representatives) == 1
        # Statistics should still be calculated
        assert result.mean_spread == 0.1
        assert result.mean_uniformity == 1.0
        return result

    # Run the async test
    result_async = asyncio.run(test_in_async_context())
    assert isinstance(result_async, MemorysetClassPatternsMetrics)


def test_async_context_behavior():
    """Test specific async context detection behavior with real async contexts."""
    from orcalib.agents.agent_utils import run_agent_safely

    # Create a mock agent that we can call
    mock_agent = Mock()
    mock_input = Mock()
    mock_context = Mock()

    @dataclass
    class SimpleAgentResult:
        description: str

    # Mock the agent's run method to return a realistic result
    async def mock_agent_run(input_data, deps=None):
        mock_result = Mock()
        mock_result.output = SimpleAgentResult("test description")
        return mock_result

    mock_agent.run = mock_agent_run

    # Test 1: No running loop (should work normally)
    # This runs in the main thread with no event loop
    result = run_agent_safely(mock_agent, mock_input, mock_context)
    assert result is not None
    assert cast(SimpleAgentResult, result).description == "test description"

    # Test 2: Inside an async context (should skip agent)
    async def test_in_async_context():
        # This should return None because we're in an async context
        result = run_agent_safely(mock_agent, mock_input, mock_context)
        assert result is None
        return True

    # Run the async test - this creates a running event loop
    success = asyncio.run(test_in_async_context())
    assert success


def test_memory_optimization():
    """Test that all computed metrics are stored for statistical analysis."""
    analysis = MemorysetClassPatternsAnalysis()

    # Create memories with different uniformity levels
    memories = []
    neighbors_batches = []

    # Memory 1: Perfect uniformity
    memory1 = Mock()
    memory1.memory_id = uuid7()
    memory1.label = 0
    neighbors1 = [Mock() for _ in range(3)]
    for neighbor in neighbors1:
        neighbor.label = 0  # All same class
        neighbor.lookup_score = 0.8
    memories.append(memory1)
    neighbors_batches.append(neighbors1)

    # Memory 2: Imperfect uniformity
    memory2 = Mock()
    memory2.memory_id = uuid7()
    memory2.label = 0
    neighbors2 = [Mock() for _ in range(3)]
    neighbors2[0].label = 0  # Same class
    neighbors2[0].lookup_score = 0.8
    neighbors2[1].label = 1  # Different class
    neighbors2[1].lookup_score = 0.7
    neighbors2[2].label = 0  # Same class
    neighbors2[2].lookup_score = 0.9
    memories.append(memory2)
    neighbors_batches.append(neighbors2)

    # Test the method
    _ = analysis.on_batch(memories, neighbors_batches)  # type: ignore

    # Verify that ALL metrics are now stored (not just perfect uniformity)
    assert len(analysis._all_metrics) == 2
    assert memory1.memory_id in analysis._all_metrics
    assert memory2.memory_id in analysis._all_metrics

    # Verify the stored data structure includes label, spread, uniformity
    label1, spread1, uniformity1 = analysis._all_metrics[memory1.memory_id]
    assert label1 == 0
    assert abs(spread1 - 0.2) < 0.01  # Perfect uniformity memory
    assert uniformity1 == 1.0

    label2, spread2, uniformity2 = analysis._all_metrics[memory2.memory_id]
    assert label2 == 0
    assert uniformity2 == 2 / 3  # 2 out of 3 neighbors are same class


def test_mean_variance_statistics():
    """Test calculation of mean and variance statistics across all memories."""
    analysis = MemorysetClassPatternsAnalysis()
    analysis.config.representatives_per_class = 2

    # Mock memoryset
    analysis.memoryset = Mock()
    analysis.memoryset.label_names = ["class_0", "class_1"]
    analysis.memoryset.description = "test dataset"

    # Set up test data with known spread and uniformity values
    memory_ids = [uuid7() for _ in range(4)]

    # Memory 1: label=0, spread=0.1, uniformity=1.0
    analysis._all_metrics[memory_ids[0]] = (0, 0.1, 1.0)

    # Memory 2: label=0, spread=0.3, uniformity=0.8
    analysis._all_metrics[memory_ids[1]] = (0, 0.3, 0.8)

    # Memory 3: label=1, spread=0.2, uniformity=1.0
    analysis._all_metrics[memory_ids[2]] = (1, 0.2, 1.0)

    # Memory 4: label=1, spread=0.4, uniformity=0.6
    analysis._all_metrics[memory_ids[3]] = (1, 0.4, 0.6)

    # Mock memory retrieval
    def mock_get(memory_id):
        memory = Mock()
        memory.value = f"Example text for {memory_id}"
        return memory

    analysis.memoryset.get = mock_get

    # Test after_all
    result = analysis.after_all()

    # Verify mean calculations
    # Spread values: [0.1, 0.3, 0.2, 0.4] -> mean = 0.25
    assert abs(result.mean_spread - 0.25) < 0.001

    # Uniformity values: [1.0, 0.8, 1.0, 0.6] -> mean = 0.85
    assert abs(result.mean_uniformity - 0.85) < 0.001

    # Verify variance calculations
    # Spread variance: np.var([0.1, 0.3, 0.2, 0.4]) = 0.015
    expected_spread_var = np.var([0.1, 0.3, 0.2, 0.4])
    assert abs(result.variance_spread - expected_spread_var) < 0.001

    # Uniformity variance: np.var([1.0, 0.8, 1.0, 0.6]) = 0.035
    expected_uniformity_var = np.var([1.0, 0.8, 1.0, 0.6])
    assert abs(result.variance_uniformity - expected_uniformity_var) < 0.001

    # Verify that representatives are still selected from perfect uniformity memories only
    # Only memories 1 and 3 have perfect uniformity, so they should be the representatives
    assert len(result.class_representatives) == 2

    class_0_reps = next(cr for cr in result.class_representatives if cr.label == 0)
    class_1_reps = next(cr for cr in result.class_representatives if cr.label == 1)

    assert len(class_0_reps.representative_memory_ids) == 1  # Only memory 1 has perfect uniformity for class 0
    assert memory_ids[0] in class_0_reps.representative_memory_ids

    assert len(class_1_reps.representative_memory_ids) == 1  # Only memory 3 has perfect uniformity for class 1
    assert memory_ids[2] in class_1_reps.representative_memory_ids


def test_empty_metrics_edge_case():
    """Test behavior when no metrics are computed."""
    analysis = MemorysetClassPatternsAnalysis()
    analysis.memoryset = Mock()
    analysis.memoryset.label_names = ["class_0"]
    analysis.memoryset.description = "empty dataset"

    # No metrics stored
    result = analysis.after_all()

    # Should handle gracefully with zero statistics
    assert result.mean_spread == 0.0
    assert result.variance_spread == 0.0
    assert result.mean_uniformity == 0.0
    assert result.variance_uniformity == 0.0
    assert len(result.class_representatives) == 1
    assert len(result.class_representatives[0].representative_memory_ids) == 0


def test_classes_without_perfect_uniformity():
    """Test behavior when some classes have no memories with perfect uniformity."""
    analysis = MemorysetClassPatternsAnalysis()
    analysis.config.representatives_per_class = 2

    # Mock memoryset with 3 classes
    analysis.memoryset = Mock()
    analysis.memoryset.label_names = ["class_0", "class_1", "class_2"]
    analysis.memoryset.description = "test dataset"

    # Set up data where:
    # - Class 0: has memories with perfect uniformity
    # - Class 1: has memories with perfect uniformity
    # - Class 2: NO memories with perfect uniformity (all are imperfect)

    memory_ids = [uuid7() for _ in range(4)]

    # Class 0: 2 memories with perfect uniformity
    analysis._all_metrics[memory_ids[0]] = (0, 0.1, 1.0)  # label, spread, uniformity
    analysis._all_metrics[memory_ids[1]] = (0, 0.2, 1.0)

    # Class 1: 1 memory with perfect uniformity
    analysis._all_metrics[memory_ids[2]] = (1, 0.15, 1.0)

    # Class 2: 1 memory with imperfect uniformity (no perfect uniformity)
    analysis._all_metrics[memory_ids[3]] = (2, 0.25, 0.8)

    # Mock memory retrieval
    def mock_get(memory_id):
        memory = Mock()
        memory.value = f"Example text for {memory_id}"
        return memory

    analysis.memoryset.get = mock_get

    # Test after_all
    result = analysis.after_all()

    # Verify the improved behavior
    assert isinstance(result, MemorysetClassPatternsMetrics)

    # NOW all classes should be included, even those without representatives
    assert len(result.class_representatives) == 3  # All 3 classes now present

    # Verify each class is represented
    class_labels = [cr.label for cr in result.class_representatives]
    assert 0 in class_labels  # Class 0 included
    assert 1 in class_labels  # Class 1 included
    assert 2 in class_labels  # Class 2 now INCLUDED (this is the fix!)

    # Verify the content of each class
    for class_rep in result.class_representatives:
        if class_rep.label == 0:
            # Class 0 should have 2 representatives
            assert len(class_rep.representative_memory_ids) == 2
            assert class_rep.label_name == "class_0"
        elif class_rep.label == 1:
            # Class 1 should have 1 representative
            assert len(class_rep.representative_memory_ids) == 1
            assert class_rep.label_name == "class_1"
        elif class_rep.label == 2:
            # Class 2 should have NO representatives but still be present
            assert len(class_rep.representative_memory_ids) == 0  # Empty but present!
            assert class_rep.label_name == "class_2"

    # Verify the new statistics include ALL metrics (including imperfect uniformity)
    # Spread values: [0.1, 0.2, 0.15, 0.25] -> mean = 0.175
    assert abs(result.mean_spread - 0.175) < 0.001

    # Uniformity values: [1.0, 1.0, 1.0, 0.8] -> mean = 0.95
    assert abs(result.mean_uniformity - 0.95) < 0.001

    # Verify variance calculations include all data
    expected_spread_var = np.var([0.1, 0.2, 0.15, 0.25])
    assert abs(result.variance_spread - expected_spread_var) < 0.001

    expected_uniformity_var = np.var([1.0, 1.0, 1.0, 0.8])
    assert abs(result.variance_uniformity - expected_uniformity_var) < 0.001


def test_patterns_description_disabled():
    """Test that patterns_description generation can be disabled via config."""
    # Test with patterns description disabled
    analysis = MemorysetClassPatternsAnalysis()
    analysis.config.enable_patterns_description = False

    # Mock memoryset
    analysis.memoryset = Mock()
    analysis.memoryset.label_names = ["class_0"]
    analysis.memoryset.description = "test"

    # Add some metrics
    memory_id = uuid7()
    analysis._all_metrics[memory_id] = (0, 0.1, 1.0)

    # Mock memory retrieval
    def mock_get(memory_id):
        memory = Mock()
        memory.value = "test value"
        return memory

    analysis.memoryset.get = mock_get

    # Mock the agent utility function - should never be called
    with patch("orcalib.analysis.analysis_class_patterns.run_agent_safely") as mock_agent:
        result = analysis.after_all()

        # Agent should not have been called since it's disabled
        mock_agent.assert_not_called()

        # Should have patterns_description field but it should be None
        assert hasattr(result, "patterns_description")
        assert result.patterns_description is None


def test_none_label_names_handling():
    """Test that the analysis handles None label_names gracefully without TypeError."""
    analysis = MemorysetClassPatternsAnalysis()

    # Mock memoryset with None label_names (this could happen in real scenarios)
    analysis.memoryset = Mock()
    analysis.memoryset.label_names = None  # This is the problematic case
    analysis.memoryset.description = "test dataset with no label names"

    # Add some metrics data
    memory_id = uuid7()
    analysis._all_metrics[memory_id] = (0, 0.1, 1.0)

    # Mock memory retrieval
    def mock_get(memory_id):
        memory = Mock()
        memory.value = "test text"
        return memory

    analysis.memoryset.get = mock_get

    # This should NOT throw a TypeError
    result = analysis.after_all()

    # Verify graceful handling
    assert isinstance(result, MemorysetClassPatternsMetrics)

    # With None label_names, no classes should be processed
    assert len(result.class_representatives) == 0

    # But statistics should still be calculated from the metrics data
    assert result.mean_spread == 0.1
    assert result.variance_spread == 0.0  # Only one data point
    assert result.mean_uniformity == 1.0
    assert result.variance_uniformity == 0.0  # Only one data point

    # No pattern description should be generated since no representatives
    assert result.patterns_description is None
