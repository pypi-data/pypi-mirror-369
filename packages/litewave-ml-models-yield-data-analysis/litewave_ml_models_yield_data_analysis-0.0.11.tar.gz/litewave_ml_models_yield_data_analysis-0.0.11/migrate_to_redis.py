"""
Migration script to move existing pipeline outputs to Redis.

This script reads CSV files from the outputs directory and stores them in Redis
for consumption by external agents.
"""

import sys
from pathlib import Path

# Add the mva_pipeline to Python path
sys.path.insert(0, str(Path(__file__).parent / "mva_pipeline"))

from mva_pipeline.redis_manager import get_redis_manager


def migrate_existing_data():
    """Migrate existing pipeline outputs to Redis."""
    print("MIGRATION: Starting migration of existing data to Redis...")

    # Check if outputs directory exists
    outputs_dir = Path("mva_pipeline/outputs")
    if not outputs_dir.exists():
        # Try alternative path
        outputs_dir = Path("outputs")
        if not outputs_dir.exists():
            print("ERROR: No outputs directory found. Run the pipeline first.")
            return False

    # File mappings: local file -> Redis key
    file_mappings = {
        "anomaly/anomaly_results.csv": "anomaly_results",
        "rca/feature_importance.csv": "rca_feature_importance",
        "unified/unified_feature_importance.csv": "unified_importance",
        "pca/pca_loadings.csv": "pca_loadings",
        "pca/pca_components.csv": "pca_components",
        "rca/shap_values.csv": "shap_values",
        "batch_matrix.parquet": "batch_matrix",
    }

    redis_manager = get_redis_manager()
    migrated_count = 0

    for file_path_str, redis_key in file_mappings.items():
        file_path = outputs_dir / file_path_str

        if file_path.exists():
            print(f"DATA: Migrating {file_path.name}...")

            try:
                import pandas as pd

                # Read the file
                if file_path.suffix == ".parquet":
                    df = pd.read_parquet(file_path)
                else:
                    df = pd.read_csv(file_path)

                # Store in Redis
                redis_manager.store_dataframe(redis_key, df)
                print(f"   SUCCESS: Migrated {len(df)} rows to Redis key: {redis_key}")
                migrated_count += 1

            except Exception as e:
                print(f"   ERROR: Failed to migrate {file_path.name}: {e}")
        else:
            print(f"   SKIP: Skipping {file_path.name} (not found)")

    print(
        f"\nSUCCESS: Migration complete! Migrated {migrated_count} datasets to Redis."
    )

    # Check what's available now
    availability = redis_manager.check_data_availability()
    available_count = sum(availability.values())
    print(f"DATA: Redis now contains {available_count} datasets:")
    for dataset, available in availability.items():
        status = "SUCCESS" if available else "ERROR"
        print(f"  - {dataset}: {status}")

    return migrated_count > 0


def verify_migration():
    """Verify the migration worked by testing tools."""
    try:
        print("\nTEST: Verifying migration with tools...")

        # Import and test some tools
        from mva_pipeline.tools import get_pipeline_status

        # Test pipeline status
        status = get_pipeline_status()
        if status.get("available_tools", 0) > 0:
            print(f"SUCCESS: Pipeline status check successful")
            print(f"Available tools: {status['available_tools']}")

            # Show which components are available
            pipeline_status = status.get("pipeline_status", {})
            for component, available in pipeline_status.items():
                status_text = "AVAILABLE" if available else "MISSING"
                print(f"  - {component}: {status_text}")
        else:
            print(
                "WARNING: No tools available. Some data may not have migrated correctly."
            )
            return False

        return True

    except Exception as e:
        print(f"ERROR: Migration verification failed: {e}")
        return False


def test_redis_connection():
    """Test Redis connection before migration."""
    try:
        redis_manager = get_redis_manager()
        # Test with a simple ping
        redis_manager.redis_client.ping()
        print("SUCCESS: Redis connection successful\n")
        return True
    except Exception as e:
        print(f"ERROR: Redis connection failed: {e}")
        print("Make sure Redis is running and accessible.")
        return False


def main():
    """Main migration function."""
    if not test_redis_connection():
        return

    # Run migration
    migration_success = migrate_existing_data()

    if migration_success:
        # Verify migration
        verification_success = verify_migration()

        if verification_success:
            print("\nSUCCESS: Migration and verification completed successfully!")
            print("External agents can now access the data via Redis.")
        else:
            print("\nWARNING: Migration completed but verification failed.")
            print("Some tools may not work correctly.")
    else:
        print("\nERROR: Migration failed. Check the outputs directory and try again.")


if __name__ == "__main__":
    main()
