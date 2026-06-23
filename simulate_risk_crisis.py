import pandas as pd
import numpy as np
from google.cloud import bigquery
import random
from datetime import datetime, timedelta

def inject_massive_risk_data():
    # 1. Pipeline configuration and target table definitions
    project_id = "project-6ec21dbe-fdf3-4e8d-bb6"
    dataset_id = "raw_synapse"
    table_id = "tbl_crm_credit_app_raw"
    
    # Explicitly bind client to target project to avoid URL formatting issues
    client = bigquery.Client(project=project_id)
    
    records = 1000
    print(f"  Generating {records} simulated credit applications for risk stress testing...")
    
    # Generate randomized application timestamps within the last 48 hours
    base_date = datetime.now()
    dates = [base_date - timedelta(minutes=random.randint(0, 2880)) for _ in range(records)]
    
    # Establish a high-stress distribution: 70% high-risk (crisis), 30% low-risk (healthy)
    is_crisis = np.random.choice([True, False], size=records, p=[0.7, 0.3])
    
    amt_req = []
    val_income = []
    pct_debt_ratio = []
    status_op = []
    
    for crisis in is_crisis:
        if crisis:
            # CRISIS: Low income, elevated debt ratios, and high loan requests
            amt_req.append(round(random.uniform(5000, 15000), 2))
            val_income.append(round(random.uniform(400, 800), 2))
            pct_debt_ratio.append(round(random.uniform(0.65, 0.95), 2))
            status_op.append('REJECTED')
        else:
            # HEALTHY: Stable income, conservative debt, and moderate loan requests
            amt_req.append(round(random.uniform(500, 2000), 2))
            val_income.append(round(random.uniform(1200, 3500), 2))
            pct_debt_ratio.append(round(random.uniform(0.10, 0.40), 2))
            status_op.append('APPROVED')

    # Construct DataFrame aligning with the upstream dbt schema contract
    df = pd.DataFrame({
        'id_app': [f"APP-{100000 + i}" for i in range(records)],
        'cod_cli': [f"CLI-{random.randint(50000, 99999)}" for i in range(records)],
        'cod_store': [f"STR-{random.choice([10, 20, 30, 99])}" for i in range(records)],
        'dt_created': [d.strftime('%Y-%m-%d %H:%M:%S') for d in dates],
        'txt_prod_cat': np.random.choice(['TECH', 'HOME', 'FASHION'], size=records),
        'status_op': status_op,
        'amt_req': amt_req,
        'val_income': val_income,
        'pct_debt_ratio': pct_debt_ratio
    })

    # Define absolute table destination string
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    
    print(f"  Uploading raw chaotic data stream to BigQuery: {table_ref}...")
    
    # Execute synchronous dataframe streaming to BigQuery landing zone
    client.load_table_from_dataframe(
        df, 
        table_ref, 
        job_config=job_config
    ).result()
    
    print("  Raw injection complete. Ready for dbt pipeline processing!")

if __name__ == "__main__":
    inject_massive_risk_data()
