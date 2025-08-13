from collections import Counter
from uuid import uuid4

import pytest

from orcalib.concepts.recursive_concepts import LeidenClustering, recursive_cluster

from ..embedding import EmbeddingModel
from ..memoryset import LabeledMemoryset


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


def test_recursive_clustering(basic_subconcepts_memoryset):
    """Test recursive clustering on a basic memoryset with clear subconcepts."""
    memoryset = basic_subconcepts_memoryset
    df = memoryset.to_pandas()
    clustering_method = LeidenClustering(n_neighbors=3, resolution=1)

    MAX_EXEMPLAR_COUNT = 2

    cluster_details, cluster_df = recursive_cluster(
        df,
        clustering_method=clustering_method,
        cluster_cutoff_percent=0.25,
        minimum_cluster_size=None,
        max_exemplar_count=MAX_EXEMPLAR_COUNT,
    )

    assert len(set(cluster_df["cluster_id"])) == 4, "Expected 4 clusters for the 2 labels with 2 subconcepts each"
    assert len(set(cluster_df["cluster_id"][0:4])) == 1, "Expected 1 cluster for the AI subconcept"
    assert len(set(cluster_df["cluster_id"][4:8])) == 1, "Expected 1 cluster for the Web Development subconcept"
    assert len(set(cluster_df["cluster_id"][8:12])) == 1, "Expected 1 cluster for the Team Sports subconcept"
    assert len(set(cluster_df["cluster_id"][12:16])) == 1, "Expected 1 cluster for the Individual Sports subconcept"

    assert len(cluster_details) == 4, "Expected 4 cluster details for the 4 subconcepts"
    for cluster in cluster_details.values():
        assert cluster.size == 4, "Each cluster should have exactly 4 items"
        assert cluster.is_noise_cluster is False, "Clusters should not be noise clusters"
        assert (
            len(cluster.exemplars) == MAX_EXEMPLAR_COUNT
        ), f"Each cluster should have exactly {MAX_EXEMPLAR_COUNT} exemplars"
        assert len(set(cluster.exemplars)) == len(cluster.exemplars), "Exemplars in each cluster should be unique"
