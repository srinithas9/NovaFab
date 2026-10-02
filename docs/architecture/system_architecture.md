# NovaFab System Architecture

## 1. Project Overview

NovaFab is a factory intelligence and predictive operations platform designed to bring
production, machine, maintenance, quality, computer vision, and operational knowledge
into one system.

The platform is designed to answer four levels of business questions:

1. Descriptive — What is happening?
2. Diagnostic — Why is it happening?
3. Predictive — What is likely to happen?
4. Decision Support — What should be investigated or acted on?

---

## 2. High-Level Architecture

```text
                    ┌─────────────────────────┐
                    │     Factory Sources     │
                    │                         │
                    │ Production Data         │
                    │ Machine Sensors         │
                    │ Maintenance Records     │
                    │ Quality Inspections     │
                    │ Defect Images           │
                    │ Manuals / SOPs / Reports │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Data Ingestion Layer  │
                    │                         │
                    │ Validation              │
                    │ Cleaning                │
                    │ Transformation          │
                    │ Loading                 │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      PostgreSQL         │
                    │                         │
                    │ Production              │
                    │ Machines                │
                    │ Sensors                 │
                    │ Maintenance             │
                    │ Quality                 │
                    │ Alerts                  │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │  Analytics  │    │     ML      │    │ Computer    │
       │             │    │             │    │   Vision    │
       │ KPI / Trends│    │ Failure Risk│    │ Defect      │
       │ Diagnostics │    │ Prediction  │    │ Detection   │
       └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │    Intelligence Layer   │
                    │                         │
                    │ RAG / Knowledge Search  │
                    │ Evidence Retrieval      │
                    │ AI Assessment            │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       Django API        │
                    │      / Backend          │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       NovaFab UI        │
                    │                         │
                    │ Command Center           │
                    │ Factory Digital Twin     │
                    │ Machine Intelligence     │
                    │ Quality Vision           │
                    │ Analytics Studio         │
                    │ AI Factory Copilot       │
                    │ Investigation Workspace  │
                    └─────────────────────────┘



| Layer               | Technology                                  |
| ------------------- | ------------------------------------------- |
| Backend             | Django                                      |
| API                 | Django REST Framework                       |
| Database            | PostgreSQL                                  |
| Data Processing     | Python, Pandas                              |
| Machine Learning    | Scikit-learn, XGBoost                       |
| Computer Vision     | PyTorch                                     |
| Knowledge Retrieval | Embeddings + Vector Database                |
| Frontend            | Django Templates, HTML, CSS, JavaScript     |
| Visualization       | Interactive charts + SVG-based factory view |
| Testing             | Pytest + Django tests                       |
| Containerization    | Docker                                      |
| Version Control     | Git + GitHub                                |
4. Design Principles
4.1 Business-first design

Every major technical component should solve a defined factory
operations problem.

Technology should not be added simply because it is popular.

4.2 Evidence-based AI

AI-generated conclusions should be supported by available data,
retrieved documents, model outputs, or other traceable evidence.

4.3 Separation of concerns

Data ingestion, analytics, machine learning, retrieval, backend APIs,
and presentation should remain logically separated.

4.4 Reproducibility

Data transformations, model training, evaluation, and application
configuration should be reproducible.

4.5 Production-style engineering

The project should include appropriate validation, testing, logging,
error handling, configuration management, security considerations,
and deployment practices.

5. Major Data Flow

Factory source data enters the ingestion layer and is validated,
cleaned, transformed, and stored in PostgreSQL.

The stored data supports analytical queries and machine learning
workflows.

Machine learning models generate predictions such as machine failure
risk.

Quality images are processed by computer vision models to identify
potential defects.

Operational documents such as manuals, SOPs, and incident reports are
processed through the knowledge retrieval pipeline.

The Django backend combines these outputs and exposes them to the
NovaFab user interface.

6. Architecture Decisions

Architecture decisions will be documented separately as the project
develops.

Each significant decision should explain:

Problem
Decision
Why this approach was selected
Alternatives considered
Trade-offs
Limitations