# Stock Predictive Analytics Pipeline

An end-to-end, production-grade data engineering platform and predictive analytics lifecycle. This project provisions serverless cloud infrastructure using Infrastructure as Code (IaC), orchestrates distributed Big Data ETL pipelines, and executes advanced statistical and machine learning models to forecast asset valuation trends.

---

## System Architecture

The architecture decouples infrastructure provisioning, ingestion orchestration, compute optimization, and analytical modeling into distinct operational layers:

```text
[Web Sources] ──> [AWS Lambda (Scraping)] ──> [Raw S3 Staging]
                                                     │
[Terraform IaC] ── Configures Infrastructure ───> [AWS Glue / PySpark]
                                                     │
[Power BI Dashboard] <── [Amazon Athena] <── [Optimized S3 Parquet]
                                                     │
                                            [Python ML Engines]
                                             ├── Random Forest (Revenue Variations)
                                             └── SARIMAX (7-Day Macro Horizon)

Tech Stack & Ecosystem
Cloud Infrastructure & IaC: AWS (Lambda, Glue, S3, Athena, CloudWatch), Terraform

Big Data & Distributed Compute: Apache Spark (PySpark), AWS Glue Data Catalog

Data Ingestion & Engineering: Python, BeautifulSoup4, Regex Parsing, Apache Parquet

Predictive Modeling & Analytics: Scikit-Learn (Random Forest Regressor), Statsmodels (SARIMAX), Pandas, NumPy

Business Intelligence: Power BI Desktop (Native Amazon Athena Connectors)

Core Features & Implementation Details
1. Serverless Ingestion & IaC Automation
Event-Driven Scraping: Built an automated serverless pipeline leveraging AWS Lambda and Python (BeautifulSoup) to scrape multi-source corporate financial telemetry directly from live web sources.

Infrastructure as Code: Handcrafted modular Terraform configuration files to provision, isolate, and maintain secure S3 buckets, AWS Glue jobs, and Lambda layers—ensuring 100% reproducible deployments with zero manual drift.

2. Distributed Big Data Processing (ETL)
PySpark Optimization: Developed distributed extract-transform-load workflows running on AWS Glue to process raw data frames, perform regular expression string normalization, and handle missing schemas at scale.

Lakehouse Cost Reduction: Structured efficient S3 partitioning strategies and registered data definitions within the AWS Glue Data Catalog. Converted raw datasets into compressed, columnar Apache Parquet format, dramatically cutting down downstream Amazon Athena SQL query scan footprints and costs.

3. Advanced Predictive Modeling
Ensemble Machine Learning: Trained a Random Forest Regressor to map non-linear financial interactions, predicting stock closing adjustments based on fundamental revenue shifts and isolating feature importances.

Statistical Time-Series Forecasting: Built a univariate SARIMAX statistical engine resampled to weekly (7-day) intervals to project asset pricing lifecycles, calculating a 95% statistical confidence interval to quantify historical trend variance.

Operational Reporting: Output tables are directly routed into interactive Power BI dashboards via Athena connectors, creating an automated data pipeline that updates downstream visuals as soon as new mathematical predictions land.

Repository Structure
Plaintext
├── .gitignore                          # Standard git exclusions (caches, credentials)
├── main.tf                             # Terraform infrastructure root manifest
├── variables.tf                        # Infrastructure parameter configurations
├── python-layer/                       # Packaged dependencies for AWS Lambda deployment
│   └── yfinance_linux_layer.zip        # Pre-compiled cross-platform wheel assets
├── src/
│   ├── lambda/
│   │   └── web_scraper.py              # Event-driven automated ingestion logic
│   ├── glue/
│   │   └── distributed_etl.py          # PySpark batch transformation routine
│   └── modeling/
│       ├── revenue_regression.py       # Random Forest ensemble predictive engine
│       └── time_series_forecast.py     # Weekly interval SARIMAX time-series script
└── reports/
    ├── README.md                       # Documentation index for analytical outputs
    ├── feature_importance.png          # Scikit-learn feature contribution metrics
    └── time_series_forecast.png        # Generated predictive valuation confidence plot
Execution & Reproducibility Guide
1. Infrastructure Deployment
Initialize and apply the configuration parameters to deploy AWS system architectures:

Bash
terraform init
terraform apply -auto-approve

2. Run Data Analytics Engines
To manually execute transformations or run local iterations of the predictive machine learning models:

Bash

python src/modeling/time_series_forecast.py
python src/modeling/revenue_regression.py

3. Review Analytical Performance
Visual plots, prediction tables, and analytical explanations are in the /reports directory.