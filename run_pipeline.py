import subprocess
import sys

def execute_dbt_pipeline():
    print("=" * 60)
    print(" STARTING AUTOMATED RETAIL CREDIT RISK PIPELINE")
    print("=" * 60)
    
    # 1. Run dbt debug
    print("\n  Step 1: Validating Google BigQuery connections...")
    debug_result = subprocess.run(["dbt", "debug"], capture_output=True, text=True)
    if debug_result.returncode != 0:
        print("  Connection failed! Check profiles.yml configuration.")
        print(debug_result.stderr)
        sys.exit(1)
    print("  Connection established successfully!")

    # 2. Run dbt run
    print("\n  Step 2: Executing dbt transformations (stg -> int -> fct)...")
    run_result = subprocess.run(["dbt", "run"], text=True)
    if run_result.returncode != 0:
        print("  Pipeline execution failed during compilation.")
        sys.exit(1)

    # 3. Run dbt test
    print("\n  Step 3: Running data quality and integrity tests...")
    test_result = subprocess.run(["dbt", "test"], text=True)
    if test_result.returncode != 0:
        print(" Data tests failed. Potential data integrity issues detected.")
        sys.exit(1)
        
    print("\n" + "=" * 60)
    print("  PIPELINE EXECUTED SUCCESSFULLY WITH ZERO ERRORS!")
    print("=" * 60)

if __name__ == "__main__":
    execute_dbt_pipeline()
