# Multivariate Analysis (MVA) Pipeline for Pharmaceutical Manufacturing

This repository contains a sophisticated data analysis pipeline designed to improve yield and reduce anomalies in pharmaceutical manufacturing processes. By leveraging multivariate analysis (MVA), machine learning, and statistical techniques, this pipeline provides deep insights into complex production data, enabling proactive quality control and process optimization.

## 1. The Challenge: Complexity in Pharmaceutical Manufacturing

Pharmaceutical manufacturing is a highly complex and regulated process. It involves numerous stages, each with a multitude of parameters that can influence the final product's quality and yield. Key challenges include:

-   **High-Dimensional Data**: A single manufacturing batch can generate thousands of data points, including sensor readings, material measurements, and quality control checks. Analyzing this high-dimensional data using traditional univariate methods (looking at one variable at a time) is often ineffective.
-   **Interacting Variables**: Process parameters are rarely independent. A change in one variable (e.g., temperature) can have cascading effects on others (e.g., pressure, reaction rate). These interactions are often non-linear and difficult to detect.
-   **Anomaly Detection**: Deviations from the optimal process, or anomalies, can lead to batch failures, reduced yield, and significant financial losses. These anomalies are often subtle and hidden within the process's natural variability.
-   **Root Cause Analysis**: When an anomaly or low-yield batch occurs, identifying the root cause is critical but challenging. It requires sifting through vast amounts of data to pinpoint the specific combination of factors responsible for the deviation.

## 2. Our Solution: A Multivariate Approach

This pipeline addresses these challenges by adopting a multivariate approach, which considers all process variables simultaneously. This holistic view allows us to model the relationships between variables and understand the process as an integrated system.

### Core Concepts

#### a. The "Golden Batch"

The "Golden Batch" concept is central to our approach. It refers to an idealized manufacturing run that represents the optimal process conditions, leading to the desired product quality and yield. While a single perfect batch may not exist, we can define a "Golden Profile" or a statistical envelope of normal operating conditions based on historical data from successful batches.

Our pipeline uses data from high-quality batches to learn this Golden Profile. All subsequent batches are then compared against this profile to assess their performance.

#### b. Dimensionality Reduction with PCA

Principal Component Analysis (PCA) is a powerful technique for dimensionality reduction. In a high-dimensional space of process variables, PCA identifies the principal components—the underlying dimensions that capture the most variance in the data.

-   **Why we use it**: By projecting the data onto a smaller number of principal components, we can visualize and analyze the process more effectively. This reduces noise and reveals the underlying structure of the data. In our pipeline, we use a supervised version of PCA where the principal components are selected based on their correlation with the final product yield. This ensures that we focus on the process variability that is most impactful to the outcome.

#### c. Anomaly Detection with Isolation Forests

An isolation forest is a modern, effective algorithm for detecting anomalies. It works by randomly partitioning the data until each data point is isolated from the others.

-   **Why we use it**: Anomalies are "few and different," which means they are more susceptible to isolation. Therefore, they will be isolated in fewer steps than normal data points. The "anomaly score" is based on the average path length required to isolate a data point across many random trees. This method is computationally efficient and works well with high-dimensional data, making it ideal for our use case.

#### d. Root Cause Analysis (RCA)

When a batch is flagged as an anomaly or exhibits low yield, we need to understand why. Our root cause analysis module uses machine learning models to identify the key features (process variables) that contributed to the deviation.

-   **Why we use it**: By analyzing the feature importance scores from models trained to distinguish between good and bad outcomes, we can pinpoint the specific variables that are most likely responsible for the problem. This provides actionable insights for process engineers to investigate and correct.

#### e. Synthetic Data Augmentation

To train robust machine learning models, a large and diverse dataset is often required. In manufacturing, data for certain conditions (especially anomalous ones) may be scarce.

-   **Why we use it**: We use synthetic data generation techniques to augment our dataset. By creating new, realistic data points—including plausible anomalies—we can improve the performance and robustness of our anomaly detection and root cause analysis models. This ensures that our models are not "surprised" by novel process conditions.

## 3. The Pipeline at a Glance

The pipeline is structured as a series of modular steps:

1.  **Data Extraction**: Raw data from various sources (e.g., database tables from a LIMS or MES) is extracted.
2.  **Data Building**: The raw data is transformed and merged into a single "wide" matrix, where each row represents a batch and each column represents a process parameter or measurement.
3.  **Data Augmentation**: The batch matrix is augmented with synthetic data to create a more robust dataset for analysis.
4.  **Analysis**:
    -   **Anomaly Detection**: Every batch is scored for its deviation from the "Golden Profile."
    -   **Supervised PCA**: The relationship between process variability and yield is modeled.
    -   **Root Cause Analysis**: The key drivers of low yield are identified.
    -   **Unified Importance**: The results from PCA and RCA are combined to provide a single, unified ranking of the most critical process parameters.

By following this structured, multivariate approach, this pipeline provides a powerful tool for understanding, monitoring, and optimizing complex pharmaceutical manufacturing processes.

## Overview

This package provides a complete analytical toolkit for pharmaceutical manufacturing data, featuring:

- **Anomaly Detection**: Multi-algorithm ensemble for identifying problematic batches
- **Yield Optimization**: PCA and SHAP-based feature importance analysis  
- **Root Cause Analysis**: Machine learning-driven insights into yield drivers
- **Tool Interface**: Clean API for external LLM agents and applications

## Installation

### For External Use (Recommended)

Install directly from Git:
```bash
pip install git+https://github.com/your-org/mva-pipeline.git
```

Or clone and install in development mode:
```bash
git clone https://github.com/your-org/mva-pipeline.git
cd mva-pipeline
pip install -e .
```

### Optional Dependencies

Install with LLM integration support:
```bash
pip install "mva-pipeline[llm] @ git+https://github.com/your-org/mva-pipeline.git"
```

Install with development tools:
```bash
pip install -e ".[dev]"
```

## Quick Start - Using the Tools API

### Running the Pipeline

```python
from mva_pipeline import run_pipeline

# Run complete pipeline with caching
result = run_pipeline()

if result['cache_hit']:
    print("🚀 Cache hit! Analytics skipped")
    print(f"Runtime: {result['runtime_seconds']:.1f}s")
else:
    print("🔄 Data changed, running full analytics...")
    print(f"Runtime: {result['runtime_seconds']:.1f}s")
    print(f"Updated: {result['updated']}")

# Access artifacts
print("Available artifacts:")
for name, path in result['artifacts'].items():
    print(f"  {name}: {path}")
```

### Basic Usage

```python
from mva_pipeline.tools import get_tool_specs, get_pipeline_status

# Check what analyses are available
status = get_pipeline_status()
print(f"Available tools: {status['available_tools']}")

# Get all tool specifications for LLM function calling
tools = get_tool_specs()
for tool in tools[:3]:
    print(f"• {tool['name']}: {tool['description']}")
```

### Anomaly Analysis

```python
from mva_pipeline import get_top_anomalies, explain_batch, get_anomaly_statistics

# Get top anomalous batches
anomalies = get_top_anomalies(n=5)
print(f"Top anomaly: Batch {anomalies[0]['doc_id']} (score: {anomalies[0]['score_if']:.2f})")

# Detailed analysis of specific batch
details = explain_batch(doc_id=470)
print(f"Batch 470 anomaly status: {details['anomaly']}")

# Overall statistics
stats = get_anomaly_statistics()
print(f"Anomaly rate: {stats['anomaly_rate']:.1%}")
```

### Yield Driver Analysis

```python
from mva_pipeline import get_top_yield_drivers, get_feature_scores

# Top process parameters affecting yield
drivers = get_top_yield_drivers(n=10)
print(f"Top yield driver: {drivers[0]['feature']} (score: {drivers[0]['unified_score']:.3f})")

# Detailed feature analysis
feature_analysis = get_feature_scores("public.bprpoc_temperature__value_r0")
print(f"PCA score: {feature_analysis['pca_score']:.3f}")
print(f"SHAP score: {feature_analysis['shap_score']:.3f}")
```

### Batch Comparison

```python
from mva_pipeline import compare_batches, find_similar_batches

# Compare specific batches
comparison = compare_batches(doc_ids=[100, 200, 300])
yields = [b['yield'] for b in comparison['batch_comparison']]
print(f"Yield range: {min(yields):.1f} - {max(yields):.1f}")

# Find similar batches
similar = find_similar_batches(doc_id=100, n_similar=5, method="yield")
print(f"Found {len(similar)} similar batches")
```

## 🔧 Command Line Interface

Run the complete analytics pipeline:

```bash
# Extract data from database
mva-pipeline extract

# Build batch matrix
mva-pipeline build

# Run complete analysis
mva-pipeline analyze

# NEW: Run complete pipeline with intelligent caching
mva-pipeline pipeline --verbose
```

### Caching Pipeline

The MVA pipeline now includes intelligent caching that automatically detects when your data has changed and only re-runs analytics when necessary:

```bash
# Run pipeline with caching (recommended)
python -m mva_pipeline.cli pipeline --verbose

# Force rebuild ignoring cache
python -m mva_pipeline.cli pipeline --force

# Skip database extraction (use existing raw data)
python -m mva_pipeline.cli pipeline --skip-extraction

# Use custom raw data directory
python -m mva_pipeline.cli pipeline --raw-dir /path/to/data
```

### How Caching Works

1. **Fingerprinting**: The system computes a SHA1 fingerprint of all Parquet files in your raw data directory based on filename, modification time, and file size.

2. **Cache Check**: Before running expensive analytics, it compares the current fingerprint with the last known fingerprint.

3. **Smart Decisions**:
   - **Cache Hit**: If fingerprints match and all artifacts exist → Fast exit (seconds)
   - **Cache Miss**: If data changed → Full analytics pipeline (minutes)

4. **State Storage**: Fingerprints are stored in Redis (if available) or fallback to `.mva_state.json` file.

### Environment Variables

Configure caching behavior with environment variables:

```bash
# Redis URL for state storage (optional)
export MVA_STATE_REDIS_URL="redis://localhost:6379/0"

# State storage type: redis or file
export MVA_STATE_STORE="redis"

# Custom state file location
export MVA_STATE_FILE="/path/to/custom_state.json"
```

### Configuration

Add caching configuration to your `config.yaml`:

```yaml
# State management for pipeline caching
state_store: redis  # Options: redis, file  
state_file: ".mva_state.json"  # Fallback file location
```

## 📋 Feature Mapping: From Technical Names to Business Insights

The MVA pipeline automatically converts technical statistical feature names into meaningful business concepts for improved user experience. This ensures that business users can understand the analysis results without needing deep technical knowledge.

### How It Works

**The Challenge**: Machine learning models work with statistical aggregations like `public.bprpoc_temp_records__temperature_max` or `public.atrs_test_details__results_std`, which are confusing for business users.

**The Solution**: A smart mapping layer that converts technical features to business concepts while preserving model performance.

### Mapping Philosophy

Our feature mapping focuses on **business insights** rather than just renaming statistical terms:

- **Document Context**: Include data source (ATRS, RMI, BPR) to show where data comes from
- **Business Relevance**: Explain why the measurement matters for manufacturing processes  
- **Statistical Meaning**: Convert technical aggregations to business understanding

### Example Mappings

| Technical Feature | Business Concept | Why This Matters |
|-------------------|------------------|------------------|
| `temperature_max` | "Process Temperature - Peak Values" | High temperature peaks can affect product quality |
| `results_std` | "Quality Control Testing - Process Consistency" | High variation indicates inconsistent process control |
| `quantity_issued_min` | "Material Issuance - Minimum Levels" | Low material levels may indicate supply issues |
| `net_wt_mean` | "Net Weight Management - Typical Levels" | Average weights show overall process control |

### Statistical Aggregation Guide

- `_min` → "Minimum Levels" (potential shortage indicators)
- `_max` → "Peak Values" (potential excess or spike indicators)  
- `_mean` → "Typical Levels" (normal operating conditions)
- `_std` → "Process Consistency" (high std = inconsistent process)

### Dual Output System

The pipeline generates two versions of results:

1. **User-Friendly**: Business concepts for tools API and external users
2. **Technical**: Original feature names preserved for internal processing

```python
# User-friendly output (default)
drivers = get_top_yield_drivers(n=5)
print(drivers[0]['business_concept'])  # "Process Temperature - Peak Values"

# Technical details still available in CSV files
# outputs/unified_importance_technical.csv contains original feature names
```

### Implementation Benefits

- **Preserved Performance**: All statistical features remain in the model
- **Business Clarity**: Users get actionable insights they can understand
- **Backward Compatibility**: Technical versions available for advanced analysis
- **Consistent Mapping**: Same business concepts across all analysis modules

## LLM Integration

The package is designed for seamless integration with LLM agents:

### OpenAI Function Calling

```python
import openai
from mva_pipeline.tools import get_tool_specs

# Get tool specifications
tools = get_tool_specs()

# Use with OpenAI
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What are the top 3 anomalous batches?"}],
    tools=[{
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"], 
            "parameters": tool["parameters"]
        }
    } for tool in tools],
    tool_choice="auto"
)
```

### LangChain Integration

```python
from langchain_core.tools import Tool
from mva_pipeline.tools import get_tool_specs

# Convert to LangChain tools
tools = get_tool_specs()
langchain_tools = [
    Tool(
        name=tool["name"],
        description=tool["description"],
        func=tool["function"]
    )
    for tool in tools
]
```

## 📁 Project Structure

```
mva-pipeline/
├── mva_pipeline/           # Main package
│   ├── tools.py           # Main tools API (16 functions)
│   ├── analysis/          # Core analytics modules
│   ├── db/               # Database utilities
│   └── cli.py            # Command line interface
├── outputs/              # Analysis results (not included in package)
├── setup.py             # Package configuration
├── pyproject.toml       # Modern Python packaging
└── requirements.txt     # Dependencies
```

## Analysis Pipeline

The package follows a structured analytics workflow:

1. **Extract** - Pull data from manufacturing databases
2. **Build** - Create wide batch matrix with feature engineering
3. **Analyze** - Run anomaly detection, PCA, and SHAP analysis
4. **Tools** - Access results via clean API interface

## Available Tools (16 total)

### Anomaly Detection (4 tools)
- `get_top_anomalies()` - Highest scoring anomalous batches
- `explain_batch()` - Detailed anomaly profile for specific batch
- `filter_anomalies_by_doc_ids()` - Bulk anomaly analysis  
- `get_anomaly_statistics()` - Overall detection statistics

### Yield Analysis (3 tools)
- `get_top_yield_drivers()` - Most critical process parameters
- `get_feature_scores()` - Individual feature importance scores
- `compare_feature_importance_methods()` - Method comparison analysis

### Advanced Analytics (6 tools)
- `get_pca_summary()` - Principal component analysis overview
- `get_batch_pca_scores()` - Batch positions in PCA space
- `get_batch_shap_explanation()` - Feature-level yield impact
- `get_global_shap_patterns()` - Global feature effect patterns
- `compare_batches()` - Multi-batch comparison
- `find_similar_batches()` - Similarity-based batch discovery

### Utilities (3 tools)
- `list_available_features()` - Available process parameters
- `get_pipeline_status()` - Analysis completion status
- `get_tool_specs()` - Tool specifications for LLM integration
