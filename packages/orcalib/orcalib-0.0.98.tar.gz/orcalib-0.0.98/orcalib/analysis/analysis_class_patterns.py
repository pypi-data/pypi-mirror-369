import json
import logging
from collections import defaultdict
from typing import Any

import numpy as np
from pydantic import BaseModel

from ..agents.agent_utils import run_agent_safely
from ..agents.describe_class_patterns import (
    ClassPatternsDescription,
    ClassPatternsInput,
    ClassRepresentatives,
    DescribeClassPatternsContext,
    describe_class_patterns_agent,
)
from ..memoryset import LabeledMemory, LabeledMemoryLookup
from ..utils.pydantic import UUID7
from .analysis import MemorysetAnalysis


class MemoryClassPatternsMetrics(BaseModel):
    spread: float
    """Average distance to neighbors of the same class"""
    uniformity: float
    """Fraction of neighbors that are of the same class"""


class MemorysetClassPatternsMetrics(BaseModel):
    class ClassRepresentatives(BaseModel):
        label: int
        """The class label"""
        label_name: str | None
        """The human-readable name of the class"""
        representative_memory_ids: list[UUID7]
        """IDs of the most representative memories for this class"""

    class_representatives: list[ClassRepresentatives]
    """Most representative memories for each class"""

    patterns_description: ClassPatternsDescription | None = None
    """Structured JSON object with a description of the patterns that distinguish the classes"""

    mean_spread: float
    """Mean spread score across all memories"""

    variance_spread: float
    """Variance of spread scores across all memories"""

    mean_uniformity: float
    """Mean uniformity score across all memories"""

    variance_uniformity: float
    """Variance of uniformity scores across all memories"""


class MemorysetClassPatternsAnalysisConfig(BaseModel):
    representatives_per_class: int = 5
    """Number of representative memories to select per class"""

    enable_patterns_description: bool = True
    """Whether to generate natural language descriptions of class patterns using an LLM agent"""


class MemorysetClassPatternsAnalysis(
    MemorysetAnalysis[MemorysetClassPatternsAnalysisConfig, MemoryClassPatternsMetrics, MemorysetClassPatternsMetrics]
):
    """
    Analyze class patterns by computing spread and uniformity metrics for each memory,
    then finding the most representative memories for each class and generating
    natural language descriptions of the class patterns.

    For each memory, computes:
    - spread: Average distance to neighbors of the same class (lower = more compact)
    - uniformity: Fraction of neighbors that are of the same class (1.0 = perfect uniformity)

    Then identifies the most representative memories for each class by selecting
    memories with perfect uniformity (1.0) and lowest spread (highest density).

    Finally, uses an AI agent to generate natural language descriptions of what
    distinguishes the different classes based on the representative examples.
    """

    name = "class_patterns"

    def __init__(self, config: MemorysetClassPatternsAnalysisConfig | None = None, **kwargs):
        self.config = config or MemorysetClassPatternsAnalysisConfig(**kwargs)

        # Store all computed metrics for statistical analysis
        self._all_metrics: dict[UUID7, tuple[int, float, float]] = {}  # memory_id -> (label, spread, uniformity)

    def on_batch(
        self, memories_batch: list[LabeledMemory], neighbors_batch: list[list[LabeledMemoryLookup]]
    ) -> list[tuple[UUID7, MemoryClassPatternsMetrics]]:
        metrics: list[tuple[UUID7, MemoryClassPatternsMetrics]] = []

        for i, memory in enumerate(memories_batch):
            neighbors = neighbors_batch[i]
            memory_label = memory.label

            if len(neighbors) == 0:
                # Handle edge case where no neighbors are found
                spread = 0.0
                uniformity = 0.0
            else:
                # Calculate spread: average distance to neighbors of the same class
                same_class_distances = []
                same_class_count = 0

                for neighbor in neighbors:
                    if neighbor.label == memory_label:
                        same_class_count += 1
                        # Convert lookup_score to distance (assuming lookup_score is similarity, distance = 1 - similarity)
                        distance = 1.0 - neighbor.lookup_score
                        same_class_distances.append(distance)

                # Calculate uniformity: fraction of neighbors with same class
                uniformity = same_class_count / len(neighbors)

                # Calculate spread: average distance to same-class neighbors
                if same_class_distances:
                    spread = float(np.mean(same_class_distances))
                else:
                    spread = 1.0  # Maximum distance if no same-class neighbors

            # Store metrics in all_metrics
            self._all_metrics[memory.memory_id] = (memory_label, spread, uniformity)

            metrics.append(
                (
                    memory.memory_id,
                    MemoryClassPatternsMetrics(
                        spread=spread,
                        uniformity=uniformity,
                    ),
                )
            )

        return metrics

    def after_all(self) -> MemorysetClassPatternsMetrics:
        """
        Compile final metrics after processing all batches.

        Finds the most representative memories for each class and generates
        natural language descriptions of the class patterns using an AI agent.

        Returns:
            MemorysetClassPatternsMetrics containing class representatives and patterns description
        """
        # Group memories by class label from all computed metrics
        memories_by_class: dict[int, list[tuple[UUID7, float, float]]] = {}
        for memory_id, (label, spread, uniformity) in self._all_metrics.items():
            if label not in memories_by_class:
                memories_by_class[label] = []
            memories_by_class[label].append((memory_id, spread, uniformity))

        # Get all class labels from the memoryset (not just those with perfect uniformity)
        if self.memoryset.label_names:
            all_class_labels = list(range(len(self.memoryset.label_names)))
        else:
            # Handle case where label_names is None - no classes to process
            all_class_labels = []

        # Process all classes, ensuring deterministic output through sorting
        class_representatives = []
        for label in sorted(all_class_labels):
            if label in memories_by_class:
                # Filter for memories with perfect uniformity for representative selection
                perfect_uniformity_memories = [
                    (memory_id, spread)
                    for memory_id, spread, uniformity in memories_by_class[label]
                    if uniformity == 1.0
                ]

                if perfect_uniformity_memories:
                    # Sort by spread (lowest first = tightest clusters), then by memory_id for determinism
                    sorted_memories = sorted(perfect_uniformity_memories, key=lambda x: (x[1], x[0]))

                    # Take up to representatives_per_class memories
                    selected_memories = sorted_memories[: self.config.representatives_per_class]
                    representative_ids = [memory_id for memory_id, _ in selected_memories]

                    # Get label name
                    label_name = None
                    if self.memoryset.label_names and 0 <= label < len(self.memoryset.label_names):
                        label_name = self.memoryset.label_names[label]

                    class_representatives.append(
                        MemorysetClassPatternsMetrics.ClassRepresentatives(
                            label=label,
                            label_name=label_name,
                            representative_memory_ids=representative_ids,
                        )
                    )
                else:
                    # Class has no memories with perfect uniformity - include empty entry
                    label_name = None
                    if self.memoryset.label_names and 0 <= label < len(self.memoryset.label_names):
                        label_name = self.memoryset.label_names[label]

                    class_representatives.append(
                        MemorysetClassPatternsMetrics.ClassRepresentatives(
                            label=label,
                            label_name=label_name,
                            representative_memory_ids=[],
                        )
                    )
            else:
                # Class has no memories at all - include empty entry for clarity
                label_name = None
                if self.memoryset.label_names and 0 <= label < len(self.memoryset.label_names):
                    label_name = self.memoryset.label_names[label]

                class_representatives.append(
                    MemorysetClassPatternsMetrics.ClassRepresentatives(
                        label=label,
                        label_name=label_name,
                        representative_memory_ids=[],
                    )
                )

        # Calculate mean and variance statistics across all metrics
        if self._all_metrics:
            all_spreads = [spread for _, spread, _ in self._all_metrics.values()]
            all_uniformities = [uniformity for _, _, uniformity in self._all_metrics.values()]

            mean_spread = float(np.mean(all_spreads))
            variance_spread = float(np.var(all_spreads))
            mean_uniformity = float(np.mean(all_uniformities))
            variance_uniformity = float(np.var(all_uniformities))
        else:
            # Handle edge case with no metrics
            mean_spread = variance_spread = 0.0
            mean_uniformity = variance_uniformity = 0.0

        # Generate AI description of patterns
        patterns_description = None
        if self.config.enable_patterns_description and any(
            len(cr.representative_memory_ids) > 0 for cr in class_representatives
        ):
            try:
                patterns_description = self._generate_patterns_description(class_representatives)
            except Exception as e:
                logging.warning(f"Failed to generate class patterns description: {e}")

        return MemorysetClassPatternsMetrics(
            class_representatives=class_representatives,
            patterns_description=patterns_description,
            mean_spread=mean_spread,
            variance_spread=variance_spread,
            mean_uniformity=mean_uniformity,
            variance_uniformity=variance_uniformity,
        )

    def _generate_patterns_description(
        self, class_representatives: list[MemorysetClassPatternsMetrics.ClassRepresentatives]
    ) -> ClassPatternsDescription | None:
        """
        Generate natural language description of class patterns using AI agent.

        Args:
            class_representatives: List of class representatives to analyze

        Returns:
            Natural language description or None if generation fails
        """
        # Prepare data for the agent - only include classes with representatives
        class_reps_for_agent = []

        for class_rep in class_representatives:
            if len(class_rep.representative_memory_ids) > 0:
                # Get memory values for the agent
                representative_values = []
                for memory_id in class_rep.representative_memory_ids:
                    memory = self.memoryset.get(memory_id)
                    if memory and isinstance(memory.value, str):
                        representative_values.append(memory.value)

                # Only include if we have string values
                if representative_values:
                    class_reps_for_agent.append(
                        ClassRepresentatives(
                            label=class_rep.label,
                            label_name=class_rep.label_name,
                            representative_values=representative_values,
                        )
                    )

        if not class_reps_for_agent:
            return None

        # Create context for the agent
        context = DescribeClassPatternsContext(
            memoryset_description=getattr(self.memoryset, "description", "data classification") or "data classification"
        )

        # Call the agent using the centralized utility
        agent_input = ClassPatternsInput(class_representatives=class_reps_for_agent)
        result = run_agent_safely(describe_class_patterns_agent, agent_input, context)
        return result if result else None
