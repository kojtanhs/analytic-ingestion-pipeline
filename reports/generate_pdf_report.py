from google.cloud import bigquery
from weasyprint import HTML
import pandas as pd
import os

def create_executive_pdf():
    # Inicialización forzada del cliente con el ID de tu proyecto para evitar //
    client = bigquery.Client(project="project-6ec21dbe-fdf3-4e8d-bb6")
    
    try:
        current_user = os.getlogin()
    except Exception:
        current_user = "juanjo_mrmz"
    
    query = """
    SELECT 
        credit_application_id,
        application_status,
        requested_credit_amount,
        declared_monthly_income,
        monthly_debt_ratio
    FROM `project-6ec21dbe-fdf3-4e8d-bb6.dbt_staging_analytics.fct_credit_risk_analytics`
    """
    
    print("  Pulling clean metrics from fct_credit_risk_analytics...")
    df = client.query(query).to_dataframe()
    
    # 1. Asegurar que los estados estén en texto limpio, sin espacios y en mayúsculas
    df['application_status'] = df['application_status'].astype(str).str.strip().str.upper()
    
    # 2. Asegurar que los montos sean interpretados como números reales (float)
    df['requested_credit_amount'] = pd.to_numeric(df['requested_credit_amount'], errors='coerce').fillna(0)

    # 3. Mapeo y cálculo seguro de las métricas sobre el DataFrame
    total_apps = int(len(df))
    approved_amt = float(df[df['application_status'] == 'APPROVED']['requested_credit_amount'].sum())
    rejected_amt = float(df[df['application_status'] == 'REJECTED']['requested_credit_amount'].sum())
    avg_income = float(df['declared_monthly_income'].mean())
    avg_dti = float(df['monthly_debt_ratio'].mean())
    
    # Ajustar porcentaje de DTI si viene en formato decimal (ej: 0.62 -> 62.0%)
    if avg_dti < 1.0:
        avg_dti = avg_dti * 100

    # Separamos el CSS en bloques limpios para evitar conflicto de llaves {}
    css_styles = """
        @page { size: A4; margin: 20mm 15mm; background-color: #ffffff; }
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #2d3748; margin: 0; padding: 0; font-size: 11pt; line-height: 1.6; }
        .header-bar { background-color: #1a365d; color: white; margin: -20mm -15mm 25px -15mm; padding: 30px 15mm; }
        .header-bar h1 { margin: 0; font-size: 22pt; font-weight: 700; letter-spacing: -0.5px; }
        .header-bar p { margin: 5px 0 0 0; font-size: 10pt; color: #90cdf4; text-transform: uppercase; letter-spacing: 1px; }
        h2 { color: #2c5282; font-size: 14pt; border-left: 4px solid #3182ce; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; }
        th { background-color: #ebf8ff; color: #2b6cb0; font-weight: bold; text-align: left; padding: 10px; font-size: 10pt; border-bottom: 2px solid #bee3f8; }
        td { padding: 12px 10px; border-bottom: 1px solid #e2e8f0; font-size: 10.5pt; }
        tr:nth-child(even) td { background-color: #f7fafc; }
        .metric-value { font-weight: bold; color: #1a365d; }
        ul { padding-left: 20px; }
        li { margin-bottom: 10px; }
    """

    # Construimos el esqueleto HTML inyectando las variables de forma segura con .format()
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            {styles}
        </style>
    </head>
    <body>
        <div class="header-bar">
            <h1>EXECUTIVE RISK & CREDIT REPORT</h1>
            <p>Automated OLAP Pipeline Delivery • Prepared by: {user}</p>
        </div>

        <h2>1. Key Performance Indicators (KPIs)</h2>
        <table>
            <thead>
                <tr>
                    <th style="width: 35%;">Financial Metric</th>
                    <th style="width: 20%;">Value</th>
                    <th style="width: 45%;">Operational Risk Context</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><b>Total Credit Applications</b></td>
                    <td class="metric-value">{total_apps}</td>
                    <td>Applications successfully refined and tested by the dbt framework.</td>
                </tr>
                <tr>
                    <td><b>Total Approved Capital</b></td>
                    <td class="metric-value">${approved_amt:,.2f}</td>
                    <td>Liquidity allocated safely across creditworthy segments.</td>
                </tr>
                <tr>
                    <td><b>Total Rejected Capital</b></td>
                    <td class="metric-value">${rejected_amt:,.2f}</td>
                    <td>High-risk capital intercepted and isolated from leverage exposure.</td>
                </tr>
                <tr>
                    <td><b>Average Customer Income</b></td>
                    <td class="metric-value">${avg_income:,.2f}</td>
                    <td>Mean financial capacity verified across the client cohort.</td>
                </tr>
                <tr>
                    <td><b>Average Debt-to-Income (DTI)</b></td>
                    <td class="metric-value">{avg_dti:.2f}%</td>
                    <td>Portfolio burden index indicating healthy optimization margins.</td>
                </tr>
            </tbody>
        </table>

        <h2>2. Strategic Insights for Decision Making</h2>
        <ul>
            <li><strong>Automated Risk Fencing:</strong> The system intercepted and successfully contained <strong>${rejected_amt:,.2f}</strong> in bad credit exposure via automated staging tests, ensuring zero structural leakage to the core balances.</li>
            <li><strong>Placement Thresholds:</strong> With an average DTI ratio of <strong>{avg_dti:.2f}%</strong>, the current customer cluster shows robust resilience, enabling the institution to maximize current placement safely.</li>
        </ul>
    </body>
    </html>
    """
    
    # Inyección explícita sin interferencia de llaves de CSS
    html_content = html_template.format(
        styles=css_styles,
        user=current_user,
        total_apps=total_apps,
        approved_amt=approved_amt,
        rejected_amt=rejected_amt,
        avg_income=avg_income,
        avg_dti=avg_dti
    )
    
    html_path = os.path.expanduser("~/analytic-ingestion-pipeline/reports/executive_summary.html")
    with open(html_path, "w") as f:
        f.write(html_content)
        
    pdf_path = os.path.expanduser("~/analytic-ingestion-pipeline/reports/executive_credit_risk_report.pdf")
    print("  Rendering high-fidelity executive PDF via WeasyPrint...")
    HTML(html_path).write_pdf(pdf_path)
    print(f"  PDF compiled successfully at: {pdf_path}")

if __name__ == "__main__":
    create_executive_pdf()
