# MVA Pipeline package
__version__ = "0.1.0"

import logging

# Configure package-level logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())  # Prevent "No handlers" warnings

# Convenient re-exports so users can do `from mva_pipeline import tools` or
# import specific utilities directly, e.g. `from mva_pipeline import get_top_anomalies`.

from . import tools as tools  # noqa: F401

# Surface the main pipeline entry point
from .pipeline import run_pipeline  # noqa: F401

# Surface the most common helper functions at the package root.
from .tools import (  # noqa: F401; Anomaly Detection Tools; Yield Driver Analysis Tools; PCA Analysis Tools; SHAP Analysis Tools; Batch Comparison Tools; Utility Functions
    compare_batches,
    compare_feature_importance_methods,
    explain_batch,
    filter_anomalies_by_doc_ids,
    find_similar_batches,
    get_anomaly_statistics,
    get_batch_pca_scores,
    get_batch_shap_explanation,
    get_feature_scores,
    get_global_shap_patterns,
    get_pca_summary,
    get_pipeline_status,
    get_tool_specs,
    get_top_anomalies,
    get_top_yield_drivers,
    list_available_features,
)
