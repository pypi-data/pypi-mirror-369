# MVA Pipeline Tool Specifications

## Overview

The MVA pipeline exposes 6 analytical tools that provide insights into pharmaceutical manufacturing anomalies and yield optimization. These tools read pre-computed results and return JSON data suitable for LLM agents.

## Prerequisites

1. Run the MVA pipeline: `python -m mva_pipeline.cli analyze`
2. Install the package: `pip install -e .`

## Usage

```python
from mva_pipeline.tools import get_tool_specs

# Get all tool specifications
tools = get_tool_specs()

# Each tool has: name, description, parameters, function
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")
```

## Available Tools

### 1. `get_top_anomalies(n=10)`
**Purpose**: Find batches with highest anomaly scores  
**Returns**: List of `{doc_id, score_if, top_dev_feat}` with human explanations  
**Use case**: "What are the worst performing batches?"

### 2. `explain_batch(doc_id)`
**Purpose**: Detailed analysis of a specific batch  
**Returns**: Full anomaly profile with all scores and flags  
**Use case**: "What went wrong with batch 470?"

### 3. `filter_anomalies_by_doc_ids(doc_ids)`
**Purpose**: Get anomaly data for multiple specific batches  
**Returns**: List of batch analyses (same schema as `explain_batch`)  
**Use case**: "Compare batches 29, 50, and 336"

### 4. `get_top_yield_drivers(n=15)`
**Purpose**: Most important process parameters for yield  
**Returns**: List of `{feature, unified_score, pca_score, shap_score}`  
**Use case**: "What should we optimize to improve yield?"

### 5. `get_feature_scores(feature)`
**Purpose**: Importance scores for a specific parameter  
**Returns**: `{feature, unified_score, pca_score, shap_score}`  
**Use case**: "How important is temperature control?"

### 6. `list_available_features()`
**Purpose**: All available process parameters  
**Returns**: List of feature names  
**Use case**: "What parameters can I analyze?"

## Integration Examples

### OpenAI Function Calling
```python
import openai
from mva_pipeline.tools import get_tool_specs

# Convert to OpenAI format
tools = get_tool_specs()
openai_tools = []

for tool in tools:
    openai_tools.append({
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"], 
            "parameters": tool["parameters"]
        }
    })

# Use with OpenAI API
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What are the top 3 anomalous batches?"}],
    tools=openai_tools
)

# Execute function calls
for call in response.choices[0].message.tool_calls:
    tool = next(t for t in tools if t["name"] == call.function.name)
    result = tool["function"](**json.loads(call.function.arguments))
```

### LangChain Integration
```python
from langchain_core.tools import Tool
from mva_pipeline.tools import get_tool_specs

# Convert to LangChain format
tools = get_tool_specs()
langchain_tools = []

for tool in tools:
    langchain_tools.append(Tool(
        name=tool["name"],
        description=tool["description"],
        func=tool["function"]
    ))

# Use with LangChain agents
```

### Custom Framework
```python
from mva_pipeline.tools import get_tool_specs

tools = get_tool_specs()

# Direct function calls
result = tools[0]["function"](n=5)  # get_top_anomalies
print(result)
```

## Data Schema

### Anomaly Results
```json
{
  "doc_id": 470,
  "anomaly": true,
  "score_if": 6.79,
  "score_lof": -1,
  "score_ee": -1, 
  "dist_maha": 6564.3,
  "is_anomaly_if": false,
  "is_anomaly_lof": true,
  "is_anomaly_ee": true,
  "is_anomaly_maha": true,
  "top_dev_feat": "weighing details → net wt mean (6.8σ) | weighing details → tare wt std (6.1σ)",
  "yield": 656.5
}
```

### Yield Drivers
```json
{
  "feature": "public.bprpoc_naocl_calc_weight__value_r0",
  "unified_score": 0.299,
  "pca_score": 0.808,
  "shap_score": 0.081
}
```

## Error Handling

All functions return JSON-serializable data. Missing files or invalid inputs raise clear exceptions:

- `FileNotFoundError`: Pipeline results not found (run `analyze` first)
- `ValueError`: Invalid doc_id or feature name
- `TypeError`: Invalid argument types

## Feature Name Interpretation

- `naocl_*`: Sodium hypochlorite (bleach) measurements
- `temp_vacuum_records_*`: Temperature and vacuum during processing
- `weighing_details_*`: Material weight measurements  
- `operation_details_*`: Timing and duration data
- `material_usage_details_*`: Raw material consumption tracking 