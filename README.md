# Analytical Ingestion Pipeline (ELT)

A production-grade dbt (Data Build Tool) repository designed to orchestrate an Extract-Load-Transform pipeline within a BigQuery Data Lakehouse environment.

## Pipeline Architecture and Data Flow

The analytical ingestion pipeline follows a strict ELT (Extract-Load-Transform) paradigm structured via a multi-layered medallion architecture. Raw operational data is transformed into partitioned, query-optimized analytical datasets within the warehouse environment.

```mermaid
graph LR
    classDef source fill:#1a1a2e,stroke:#e74c3c,stroke-width:2px,color:#fff;
    classDef staging fill:#16213e,stroke:#d35400,stroke-width:2px,color:#fff;
    classDef intermediate fill:#1f4068,stroke:#f1c40f,stroke-width:2px,color:#fff;
    classDef marts fill:#0f3460,stroke:#27ae60,stroke-width:2px,color:#fff;

    A[Raw Operational SQL: Credit Applications & Retail Transactions] -->|Direct Load| B[Staging Layer: stg_credit_applications.sql]
    class A source;
    class B staging;

    B --> C[Intermediate Layer: int_customer_credit_profile.sql]
    class C intermediate;

    C --> D[Marts Layer: fct_credit_risk_analytics.sql]
    class D marts;

    subgraph Warehouse Transformations & Lineage
        B -.->|Type Casting, Renaming & Data Cleansing| B
        C -.->|Window Functions, Time-Series & Cross-Silo Aggregations| C
        D -.->|Feature Engineering, Partitioning & Clustering| D
    end
```

## Architecture

The pipeline enforces a structured three-tier medal architecture to ingest and clean transactional legacy data for downstream AI consumption:

1. **Staging Layer (Bronze):** Sanitizes and casts raw relational data into standardized GoogleSQL types.
2. **Intermediate Layer (Silver):** Executes advanced window functions to compute non-leaking historical customer profiles.
3. **Marts Layer (Gold):** Generates optimized, partitioned, and clusterized fact tables optimized for ML model training.

```text
analytic-ingestion-pipeline/
├── dbt_project.yml
└── models/
    ├── staging/      (stg_credit_applications.sql, schema.yml)
    ├── intermediate/ (int_customer_credit_profile.sql)
    └── marts/        (fct_credit_risk_analytics.sql)
```
