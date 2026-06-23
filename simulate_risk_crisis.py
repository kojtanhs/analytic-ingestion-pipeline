import pandas as pd
import numpy as np
from google.cloud import bigquery
import random
from datetime import datetime, timedelta

def inject_massive_risk_data():
    # 1. Definición explícita de variables al inicio de la función
    project_id = "project-6ec21dbe-fdf3-4e8d-bb6"
    dataset_id = "raw_synapse"
    table_id = "tbl_crm_credit_app_raw"
    
    # Inicializamos el cliente amarrado al proyecto
    client = bigquery.Client(project=project_id)
    
    records = 1000
    print(f"  Generating {records} simulated credit applications for risk stress testing...")
    
    # Generar fechas aleatorias dentro de las últimas 48 horas
    base_date = datetime.now()
    dates = [base_date - timedelta(minutes=random.randint(0, 2880)) for _ in range(records)]
    
    # 70% de probabilidad de crisis (alto riesgo), 30% sano
    is_crisis = np.random.choice([True, False], size=records, p=[0.7, 0.3])
    
    amt_req = []
    val_income = []
    pct_debt_ratio = []
    status_op = []
    
    for crisis in is_crisis:
        if crisis:
            # CRISIS: Bajos ingresos, deudas infladas y montos altos
            amt_req.append(round(random.uniform(5000, 15000), 2))
            val_income.append(round(random.uniform(400, 800), 2))
            pct_debt_ratio.append(round(random.uniform(0.65, 0.95), 2))
            status_op.append('REJECTED')
        else:
            # SANO: Ingresos estables, baja deuda y montos moderados
            amt_req.append(round(random.uniform(500, 2000), 2))
            val_income.append(round(random.uniform(1200, 3500), 2))
            pct_debt_ratio.append(round(random.uniform(0.10, 0.40), 2))
            status_op.append('APPROVED')

    # Estructurar el DataFrame para BigQuery
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

    # Construcción directa de la referencia de la tabla usando strings limpios
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    
    print(f"  Uploading raw chaotic data stream to BigQuery: {table_ref}...")
    
    # Inyección limpia
    client.load_table_from_dataframe(
        df, 
        table_ref, 
        job_config=job_config
    ).result()
    
    print("  Raw injection complete. Ready for dbt pipeline processing!")

if __name__ == "__main__":
    inject_massive_risk_data()
