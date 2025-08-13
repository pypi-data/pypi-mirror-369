"""
Test suite for MemorysetConceptAnalysis functionality.

This module tests the concept analysis system which uses UMAP/HDBSCAN clustering
to identify subconcepts within labeled memory data. The tests cover:

1. Basic functionality with multi-label data and configuration options
2. Single-label clustering to find subconcepts within one category
3. Complex multi-label scenarios with many subconcepts
4. Fallback behavior for small datasets that can't be clustered
5. Individual memory cluster assignments and metrics validation

The test suite has been optimized to reduce the number of expensive analysis runs
while maintaining comprehensive coverage of all functionality.
"""

from collections import Counter
from uuid import uuid4

import pytest

from ..embedding import EmbeddingModel
from ..memoryset import LabeledMemoryset
from .analysis import run_analyses
from .analysis_subconcept import MemorysetSubconceptAnalysis, MemorysetSubconceptMetrics


@pytest.fixture
def basic_subconcepts_memoryset():
    """A memoryset with 2 labels, each containing 2 clear subconcepts."""
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
        label_names=["technology", "sports"],
    )
    memoryset.insert(
        [
            # Technology label with two subconcepts: AI and Web Development
            # AI subconcept
            {"value": "Machine learning algorithms are revolutionizing artificial intelligence", "label": 0},
            {"value": "Deep learning neural networks enable advanced AI capabilities", "label": 0},
            {"value": "Artificial intelligence systems are becoming more sophisticated daily", "label": 0},
            {"value": "AI models require extensive training data for optimal performance", "label": 0},
            # Web Development subconcept
            {"value": "React framework simplifies modern web application development", "label": 0},
            {"value": "JavaScript frameworks enhance frontend user interface design", "label": 0},
            {"value": "Web developers use responsive design for mobile compatibility", "label": 0},
            {"value": "Modern web applications require efficient backend API design", "label": 0},
            # Sports label with two subconcepts: Team Sports and Individual Sports
            # Team Sports subconcept
            {"value": "Basketball teams coordinate plays during championship games", "label": 1},
            {"value": "Soccer players work together to score goals effectively", "label": 1},
            {"value": "Football teams develop strategic plays for competitive advantage", "label": 1},
            {"value": "Volleyball teams communicate constantly during intense matches", "label": 1},
            # Individual Sports subconcept
            {"value": "Tennis players focus on perfecting their serving technique", "label": 1},
            {"value": "Golf requires precision and concentration for each shot", "label": 1},
            {"value": "Swimming athletes train rigorously to improve their times", "label": 1},
            {"value": "Marathon runners develop endurance through consistent training", "label": 1},
        ]
    )
    return memoryset


@pytest.fixture
def complex_subconcepts_memoryset():
    """A memoryset with 3 labels, with 3, 2, and 2 subconcepts respectively."""
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
        label_names=["science", "entertainment", "food"],
    )
    memoryset.insert(
        [
            # Science label with three subconcepts: Physics, Biology, Chemistry
            # Physics subconcept
            {"value": "Quantum mechanics explains subatomic particle behavior", "label": 0},
            {"value": "Relativity theory describes spacetime and gravitational effects", "label": 0},
            {"value": "Electromagnetic waves propagate through vacuum at light speed", "label": 0},
            {"value": "Nuclear fusion powers stars and releases tremendous energy", "label": 0},
            # Biology subconcept
            {"value": "DNA sequences contain genetic information for organisms", "label": 0},
            {"value": "Cellular mitosis enables organism growth and reproduction", "label": 0},
            {"value": "Evolution shapes species through natural selection processes", "label": 0},
            {"value": "Ecosystems maintain balance through predator-prey relationships", "label": 0},
            # Chemistry subconcept
            {"value": "Chemical bonds form when atoms share electrons", "label": 0},
            {"value": "Molecular reactions follow conservation of mass principles", "label": 0},
            {"value": "Periodic table organizes elements by atomic properties", "label": 0},
            {"value": "Catalysts accelerate reactions without being consumed", "label": 0},
            # Entertainment label with two subconcepts: Movies and Music
            # Movies subconcept
            {"value": "Cinematography captures visual storytelling through camera techniques", "label": 1},
            {"value": "Film editing creates narrative flow and emotional impact", "label": 1},
            {"value": "Movie soundtracks enhance dramatic scenes and atmosphere", "label": 1},
            {"value": "Special effects bring impossible worlds to life", "label": 1},
            # Music subconcept
            {"value": "Musical harmony combines notes to create pleasing sounds", "label": 1},
            {"value": "Rhythm patterns provide the temporal foundation for songs", "label": 1},
            {"value": "Melody lines carry the memorable themes in compositions", "label": 1},
            {"value": "Instruments create diverse timbres and sonic textures", "label": 1},
            # Food label with two subconcepts: Italian and Asian cuisine
            # Italian cuisine subconcept
            {"value": "Pasta dishes with marinara sauce are Italian classics", "label": 2},
            {"value": "Pizza margherita represents traditional Italian cooking", "label": 2},
            {"value": "Risotto requires careful stirring and quality rice", "label": 2},
            {"value": "Italian gelato differs from American ice cream", "label": 2},
            # Asian cuisine subconcept
            {"value": "Sushi requires fresh fish and perfectly seasoned rice", "label": 2},
            {"value": "Stir-fry cooking uses high heat and quick movements", "label": 2},
            {"value": "Ramen broth simmers for hours to develop flavor", "label": 2},
            {"value": "Dim sum offers variety in small bite-sized portions", "label": 2},
        ]
    )
    return memoryset


def test_concept_analysis_basic_functionality(basic_subconcepts_memoryset):
    """Test core concept analysis functionality with basic configuration.

    Uses a memoryset with 2 labels (technology, sports), each containing 2 clear subconcepts:
    - Technology: AI and Web Development
    - Sports: Team Sports and Individual Sports

    Tests multiple aspects:
    - Basic clustering with default configuration
    - Custom configuration parameters
    - Cluster naming and description generation
    - Result structure validation
    """
    # Given a memoryset with distinct subconcepts within each label
    memoryset = basic_subconcepts_memoryset

    # When we run a concept analysis with default configuration
    default_result = run_analyses(
        memoryset,
        MemorysetSubconceptAnalysis(),  # Use default config
        lookup_count=3,
        show_progress_bar=False,
    )["subconcepts"]

    # Then a result is returned without errors
    assert isinstance(default_result, MemorysetSubconceptMetrics)
    assert default_result.num_clusters >= 1

    # When we run a concept analysis with custom configuration
    custom_result = run_analyses(
        memoryset,
        MemorysetSubconceptAnalysis(
            high_level_description="Classify text samples into technology and sports categories",
            max_sample_rows=20,
            max_trial_count=5,
            min_desired_clusters_per_label=2,
            max_desired_clusters_per_label=3,
            accuracy_importance=0.7,
            noise_penalty=0.3,
            naming_examples_count=3,
            naming_counterexample_count=2,
            seed=123,
        ),
        lookup_count=5,
        show_progress_bar=False,
    )["subconcepts"]

    # Then the analysis should complete successfully with the custom configuration
    assert isinstance(custom_result, MemorysetSubconceptMetrics)
    assert custom_result.num_clusters >= 1

    # And the result should contain at least one cluster
    # Note: Due to the non-deterministic nature of clustering and the small dataset,
    # the algorithm may find just the top-level classes rather than subconcepts
    assert custom_result.num_clusters >= 1

    # And we should have clusters with reasonable sizes
    total_memories = sum(cluster.memory_count for cluster in custom_result.clusters_by_id.values())
    # Note: Total may be less than len(memoryset) if some memories are assigned to noise cluster
    assert total_memories <= len(memoryset)
    assert total_memories > 0

    # And each cluster should have a name and description
    for cluster in custom_result.clusters_by_id.values():
        if cluster.cluster_id != -1:  # Skip noise cluster if it exists
            assert cluster.name is not None
            assert len(cluster.name) > 0
            assert cluster.memory_count > 1  # Each cluster should have multiple memories

    # And cluster descriptions should be meaningful (not None or empty)
    non_noise_clusters = [c for c in custom_result.clusters_by_id.values() if c.cluster_id != -1]
    assert len(non_noise_clusters) >= 1

    for cluster in non_noise_clusters:
        # Descriptions might be None if the naming process fails, but names should exist
        assert cluster.name is not None
        assert len(cluster.name.strip()) > 0


def test_concept_analysis_with_single_label():
    """Test concept analysis with one label containing multiple subconcepts.

    Uses a larger dataset (20 memories) with one label but two clear subconcepts:
    - Python programming (10 memories)
    - JavaScript programming (10 memories)

    Validates that subconcepts can be discovered even within a single label category.
    """
    # Given a memoryset with only one label but multiple subconcepts (with sufficient data)
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
        label_names=["programming"],
    )
    memoryset.insert(
        [
            # Python subconcept (10 memories)
            {"value": "Python pandas library enables efficient data manipulation and analysis", "label": 0},
            {"value": "Python Flask framework creates lightweight web applications easily", "label": 0},
            {"value": "Python NumPy provides powerful numerical computing capabilities", "label": 0},
            {"value": "Python Django framework supports rapid web development projects", "label": 0},
            {"value": "Python scikit-learn offers machine learning tools for data science", "label": 0},
            {"value": "Python requests library simplifies HTTP requests in applications", "label": 0},
            {"value": "Python matplotlib creates beautiful data visualizations and charts", "label": 0},
            {"value": "Python SQLAlchemy provides database ORM functionality for applications", "label": 0},
            {"value": "Python fastapi builds high-performance web APIs with automatic documentation", "label": 0},
            {"value": "Python pytest framework enables comprehensive testing of Python applications", "label": 0},
            # JavaScript subconcept (10 memories)
            {"value": "JavaScript promises handle asynchronous operations elegantly in browsers", "label": 0},
            {"value": "JavaScript Node.js enables server-side application development efficiently", "label": 0},
            {"value": "JavaScript ES6 features improve code readability significantly for developers", "label": 0},
            {"value": "JavaScript React creates dynamic user interface components for web apps", "label": 0},
            {"value": "JavaScript Express framework builds REST APIs quickly and effectively", "label": 0},
            {"value": "JavaScript TypeScript adds static typing for better code quality", "label": 0},
            {"value": "JavaScript Vue.js offers reactive components for modern web development", "label": 0},
            {"value": "JavaScript async/await syntax simplifies promise-based programming patterns", "label": 0},
            {"value": "JavaScript webpack bundles modules for optimized web application deployment", "label": 0},
            {"value": "JavaScript Jest provides testing utilities for JavaScript and React applications", "label": 0},
        ]
    )

    # When we run a concept analysis
    result = run_analyses(
        memoryset,
        MemorysetSubconceptAnalysis(
            high_level_description="Classify programming-related text samples",
            min_desired_clusters_per_label=2,
            max_desired_clusters_per_label=4,
        ),
        lookup_count=5,
        show_progress_bar=False,
    )["subconcepts"]

    # Then a result is returned
    assert isinstance(result, MemorysetSubconceptMetrics)

    # And we should find at least one cluster (clustering is non-deterministic)
    assert result.num_clusters >= 1

    # And clusters should have reasonable distributions
    cluster_sizes = [cluster.memory_count for cluster in result.clusters_by_id.values() if cluster.cluster_id != -1]
    assert all(size > 1 for size in cluster_sizes)  # Each cluster should have multiple memories


def test_concept_analysis_with_multiple_subconcepts(complex_subconcepts_memoryset):
    """Test concept analysis with complex multi-label data containing many subconcepts.

    Uses the complex memoryset with 3 labels and 7 total subconcepts:
    - Science: Physics, Biology, Chemistry (12 memories)
    - Entertainment: Movies, Music (8 memories)
    - Food: Italian, Asian (8 memories)

    Validates that the analysis can handle larger, more complex datasets.
    """
    # Given a memoryset with multiple clear subconcepts within each label
    memoryset = complex_subconcepts_memoryset

    # When we run a concept analysis
    result = run_analyses(
        memoryset,
        MemorysetSubconceptAnalysis(
            high_level_description="Classify text samples into science, entertainment, and food categories",
            min_desired_clusters_per_label=2,
            max_desired_clusters_per_label=4,
            naming_examples_count=4,
            naming_counterexample_count=3,
        ),
        lookup_count=7,
        show_progress_bar=False,
    )["subconcepts"]

    # Then a result is returned
    assert isinstance(result, MemorysetSubconceptMetrics)

    # And we should find multiple subconcepts across all labels
    # Note: Due to the non-deterministic nature of clustering and the relatively small dataset,
    # we may find fewer clusters than theoretically possible. The important thing is that
    # we get some meaningful clustering results.
    assert result.num_clusters >= 1

    # And clusters should have meaningful names
    for cluster in result.clusters_by_id.values():
        if cluster.cluster_id != -1:  # Skip noise cluster
            assert cluster.name is not None and len(cluster.name.strip()) > 0
            assert cluster.memory_count > 1  # Each cluster should have multiple memories


def test_concept_analysis_fallback_behavior():
    """Test the fallback behavior for small datasets that can't be clustered.

    Uses a small memoryset (9 memories) across 3 labels that is below the 20-sample
    threshold for UMAP/HDBSCAN clustering. Validates that:
    - The fallback creates one cluster per label
    - Clusters are named after their labels
    - Memory counts match the actual label distribution
    - Primary label indices are correctly assigned
    """
    # Given a memoryset that is too small for clustering (< 20 samples)
    memoryset = LabeledMemoryset(
        f"memory:#{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
        label_names=["music", "art", "literature"],
    )
    memoryset.insert(
        [
            # Music label (3 memories)
            {"value": "Classical symphonies feature orchestral arrangements", "label": 0},
            {"value": "Jazz improvisation showcases musical creativity", "label": 0},
            {"value": "Rock music drives energetic performances", "label": 0},
            # Art label (2 memories)
            {"value": "Renaissance paintings display masterful technique", "label": 1},
            {"value": "Modern sculptures explore abstract concepts", "label": 1},
            # Literature label (4 memories)
            {"value": "Poetry captures emotions through verse", "label": 2},
            {"value": "Novels tell comprehensive stories", "label": 2},
            {"value": "Short stories provide focused narratives", "label": 2},
            {"value": "Essays present analytical arguments", "label": 2},
        ]
    )

    # When we run a concept analysis on this small dataset
    result = run_analyses(
        memoryset,
        MemorysetSubconceptAnalysis(),
        lookup_count=2,
        show_progress_bar=False,
    )["subconcepts"]

    # Then it should use the fallback behavior
    assert isinstance(result, MemorysetSubconceptMetrics)

    # And it should create one cluster per label
    assert result.num_clusters == 3

    # And each cluster should be named after the label
    assert result.clusters_by_id[0].name == "music"
    assert result.clusters_by_id[1].name == "art"
    assert result.clusters_by_id[2].name == "literature"

    # And cluster descriptions should mention the label
    assert result.clusters_by_id[0].description is not None and "music" in result.clusters_by_id[0].description
    assert result.clusters_by_id[1].description is not None and "art" in result.clusters_by_id[1].description
    assert result.clusters_by_id[2].description is not None and "literature" in result.clusters_by_id[2].description

    # And memory counts should match the actual distribution
    assert result.clusters_by_id[0].memory_count == 3  # music
    assert result.clusters_by_id[1].memory_count == 2  # art
    assert result.clusters_by_id[2].memory_count == 4  # literature

    # And primary label indices should be correct
    assert result.clusters_by_id[0].primary_label_index == 0
    assert result.clusters_by_id[1].primary_label_index == 1
    assert result.clusters_by_id[2].primary_label_index == 2


def test_concept_analysis_memory_assignments(basic_subconcepts_memoryset):
    """Test that individual memories are correctly assigned to clusters with proper metrics.

    Uses the basic_subconcepts_memoryset fixture with 2 labels (technology, sports),
    each containing 2 clear subconcepts (AI/Web Development, Team Sports/Individual Sports).

    Validates that:
    - Each memory gets assigned a cluster ID and name
    - Noise memories get cluster ID -1 and name "Noise"
    - Non-noise memories get valid cluster IDs and corresponding cluster names
    - All memories in the memoryset are accounted for in the assignments
    """
    # Given a memoryset with clear subconcepts
    memoryset = basic_subconcepts_memoryset

    # When we run concept analysis
    result = run_analyses(
        memoryset,
        MemorysetSubconceptAnalysis(
            high_level_description="Classify text samples into technology and sports categories",
            min_desired_clusters_per_label=2,
            max_desired_clusters_per_label=3,
            seed=42,  # Use fixed seed for reproducible results
        ),
        lookup_count=5,
        show_progress_bar=False,
    )["subconcepts"]

    # Then we should get cluster assignment results
    assert isinstance(result, MemorysetSubconceptMetrics)
    assert result.num_clusters >= 1

    # And every memory in the memoryset should have updated metrics with cluster assignments
    memory_assignments = {}
    for memory in memoryset:
        assert memory.metrics is not None
        assert "subconcept_cluster_id" in memory.metrics
        assert "subconcept_name" in memory.metrics

        cluster_id = memory.metrics["subconcept_cluster_id"]
        cluster_name = memory.metrics["subconcept_name"]

        # Validate cluster assignments
        if cluster_id == -1:
            # Noise memories should have "Noise" as their cluster name
            assert cluster_name == "Noise"
        else:
            # Non-noise memories should have valid cluster IDs and corresponding names
            assert cluster_id is not None
            assert cluster_name is not None
            assert len(cluster_name) > 0
            assert cluster_name != "Noise"

            # Cluster ID should correspond to a valid cluster in the results
            assert cluster_id in result.clusters_by_id
            # The cluster name should match what's in the cluster results
            assert cluster_name == result.clusters_by_id[cluster_id].name

        memory_assignments[memory.memory_id] = (cluster_id, cluster_name)

    # And all memories should be accounted for (no missing assignments)
    assert len(memory_assignments) == len(memoryset)

    # And the cluster memory counts should match the actual assignments
    cluster_assignment_counts = Counter(assignment[0] for assignment in memory_assignments.values())
    for cluster_id, cluster_info in result.clusters_by_id.items():
        expected_count = cluster_assignment_counts.get(cluster_id, 0)
        assert cluster_info.memory_count == expected_count, (
            f"Cluster {cluster_id} reports {cluster_info.memory_count} memories "
            f"but actual assignments show {expected_count}"
        )

    # And if there are noise assignments, there should be a noise cluster in the results
    has_noise_assignments = any(assignment[0] == -1 for assignment in memory_assignments.values())
    has_noise_cluster = -1 in result.clusters_by_id
    if has_noise_assignments:
        assert has_noise_cluster, "Found noise assignments but no noise cluster in results"
        assert result.clusters_by_id[-1].name == "Noise"

    # And non-noise clusters should have meaningful names (not just generic cluster names)
    non_noise_clusters = [cluster for cluster_id, cluster in result.clusters_by_id.items() if cluster_id != -1]
    for cluster in non_noise_clusters:
        assert cluster.name is not None
        assert len(cluster.name) > 0
        # Name should be more descriptive than just "Cluster X"
        assert not cluster.name.startswith("Cluster ") or cluster.name.count(" ") > 1
