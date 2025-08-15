# Running the MVA Pipeline

This document provides instructions on how to set up the environment and run the MVA analysis pipeline.

## 1. Prerequisites

-   Python 3.9+
-   Access to a database containing the manufacturing data.

## 2. Setup

### a. Clone the Repository

```bash
git clone <repository_url>
cd mva_spike
```

### b. Create a Virtual Environment (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### c. Install Dependencies

Install the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### d. Configure the Database Connection

The pipeline needs to connect to your manufacturing database to extract the raw data. The connection details are specified in the `mva_pipeline/config.yaml` file.

1.  **Copy the default configuration:**
    -   While a `config.yaml` is provided, you may want to create a copy for your specific environment.

2.  **Edit `config.yaml`:**
    Open `mva_pipeline/config.yaml` and update the `db_url` with your database connection string. The format is:

    ```yaml
    db_url: "postgresql://<user>:<password>@<host>:<port>/<database>"
    ```

    You can also adjust other parameters in this file, such as the `output_dir` and the `link_keys` used to join the tables.

## 3. Running the Pipeline

The pipeline is executed through the command-line interface (CLI) defined in `mva_pipeline/cli.py`. It consists of three main steps that should be run in order: `extract`, `build`, and `analyze`.

You can run the CLI using `python3 -m mva_pipeline.cli`.

### Step 1: Extract Data

This command connects to the database, finds all tables containing the specified `link_keys`, and exports them as Parquet files into the `outputs/data_raw/` directory.

```bash
python3 -m mva_pipeline.cli extract
```

You can specify a custom config file using the `--config` flag:

```bash
python3 -m mva_pipeline.cli extract --config /path/to/your/config.yaml
```

### Step 2: Build Batch Matrix

This command takes the raw Parquet files from the previous step and transforms them into a single "wide" data matrix. Each row represents a batch, and each column represents a feature. It also creates a robust-scaled version of the matrix for the analysis.

```bash
python3 -m mva_pipeline.cli build
```

The output files, `batch_matrix.parquet` and `batch_matrix_scaled.parquet`, will be saved in the `outputs/` directory.

### Step 3: Analyze Data

This is the final step, which runs the full MVA analysis on the built batch matrix. This includes:
-   Synthetic data augmentation
-   Anomaly detection
-   Supervised PCA for yield analysis
-   Root cause analysis
-   Unified feature importance calculation

```bash
python3 -m mva_pipeline.cli analyze
```

The results of the analysis will be saved in various subdirectories within the `outputs/` folder (e.g., `outputs/anomaly`, `outputs/pca`, etc.). The console will print a summary of the results upon completion.

## 4. Full Pipeline Execution

To run the entire pipeline from start to finish, simply execute the three commands in sequence:

```bash
python3 -m mva_pipeline.cli extract
python3 -m mva_pipeline.cli build
python3 -m mva_pipeline.cli analyze
``` 