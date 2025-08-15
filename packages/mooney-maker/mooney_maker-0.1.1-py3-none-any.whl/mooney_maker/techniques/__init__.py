from mooney_maker.techniques.base import MooneyTechnique

from .basic_global import (
    CannyEdgeSimilarityThresholdTechnique,
    CannyMaxEdgeThresholdTechnique,
    MeanThresholdTechnique,
    OtsusThresholdTechnique,
)
from .edge_optimization_techniques import (
    CannyEdgeDisruptionTechnique,
    CannyEdgeSimilarityTechnique,
    DiffusionEdgeDisruptionTechnique,
    DiffusionEdgeSimilarityTechnique,
    TEEDEdgeDisruptionTechnique,
    TEEDEdgeSimilarityTechnique,
)

TECHNIQUE_REGISTRY = {
    "Mean": MeanThresholdTechnique,
    "Otsu": OtsusThresholdTechnique,
    "CannyMaxEdge": CannyMaxEdgeThresholdTechnique,
    "TEEDEdgeDisruption": TEEDEdgeDisruptionTechnique,
    "TEEDEdgeSimilarity": TEEDEdgeSimilarityTechnique,
    "DiffusionEdgeDisruption": DiffusionEdgeDisruptionTechnique,
    "DiffusionEdgeSimilarity": DiffusionEdgeSimilarityTechnique,
    "CannyEdgeDisruption": CannyEdgeDisruptionTechnique,
    "CannyEdgeSimilarity": CannyEdgeSimilarityTechnique,
}


def get_technique(technique_name, **kwargs) -> MooneyTechnique:
    """Factory function to get the appropriate technique."""
    if technique_name not in TECHNIQUE_REGISTRY:
        raise ValueError(f"Unknown technique: {technique_name}")

    technique_class = TECHNIQUE_REGISTRY[technique_name]
    return technique_class(**kwargs)
