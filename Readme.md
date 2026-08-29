# Narrate IQ

### KPI Intelligence → Evidence → Decision → Action → Experiment → Learning

**Narrate IQ** is an evidence-grounded business intelligence and decision-support system designed to move beyond static dashboards. It turns multi-source business data into a structured decision flow: compute trusted KPIs, detect material movement, identify and rank plausible drivers, validate those hypotheses against multiple evidence sources, recommend an action, define an experiment, learn from outcomes, and expose the complete decision context through an executive interface and a grounded AI Copilot.

> **Core design principle:** quantitative truth is established by deterministic analytics and validated data pipelines. The LLM is used as a natural-language interface over the resulting decision context—not as the source of KPI calculations, statistical values, or business facts.

---

## Table of Contents

- [Problem](#1-problem)
- [Solution](#2-solution)
- [Architecture](#3-architecture)
- [Intelligence Pipeline](#4-intelligence-pipeline)
- [Analytics and Decisioning](#5-analytics-and-decisioning)
- [Evidence and Uncertainty](#6-evidence-and-uncertainty)
- [Experiment and Learning Loop](#7-experiment-and-learning-loop)
- [AI Copilot](#8-ai-copilot)
- [Frontend](#9-frontend)
- [Backend API](#10-backend-api)
- [Data Model and Outputs](#11-data-model-and-outputs)
- [Repository Structure](#12-repository-structure)
- [Data Ingestion and Validation](#13-data-ingestion-and-validation)
- [Setup](#14-setup)
- [Running the System](#15-running-the-system)
- [API Reference](#16-api-reference)
- [Testing](#17-testing)
- [Design Decisions](#18-design-decisions)
- [Scope and Limitations](#19-scope-and-limitations)
- [Submission / Evaluation Guide](#20-submission--evaluation-guide)

---

# 1. Problem

Traditional BI systems are good at answering what happened, how much a metric moved, and which dashboard or segment changed. They are less effective at taking a user through the complete analytical decision cycle:

**What changed → Why might it have changed → What evidence supports that explanation → Where is the impact concentrated → What should we do → How do we test it → What did we learn?**

Narrate IQ is built around that complete loop.

---

# 2. Solution

Narrate IQ converts raw business data into an inspectable decision object through a sequence of deterministic and ML-assisted analytical stages, then exposes that decision object through an executive UI and conversational Copilot.

```text
Raw Business Data
        │
        ▼
Data Ingestion + Schema Validation
        │
        ▼
Canonical Daily KPI Layer
        │
        ├── Temporal Movement Analysis
        ├── Materiality Classification
        └── Anomaly Detection
        │
        ▼
Driver Evidence + Attribution
        │
        ├── Volume / Price decomposition
        ├── Driver importance modeling
        └── Dimension-level drill-down
        │
        ▼
Confidence + Evidence Validation
        │
        ├── Statistical evidence
        ├── Business event context
        └── Segment evidence
        │
        ▼
Learning-aware Hypothesis Ranking
        │
        ▼
Recommendation Engine
        │
        ▼
Experiment Engine
        │
        ▼
Historical Learning
        │
        ▼
Decision Object
        │
        ├───────────────┐
        ▼               ▼
Executive UI       Grounded AI Copilot
                        │
                        ▼
                Natural-language answers
                over verified decision context
```

The architecture deliberately separates measurement, analytical reasoning, decisioning, and language generation.

---

# 3. Architecture

| Layer | Responsibility | Implementation |
|---|---|---|
| Data | Load and validate source datasets | `src/ingestion/` |
| KPI / Analytics | Compute KPIs, movement, materiality and anomalies | `src/kpi/`, `src/anomaly/` |
| Evidence / Reasoning | Drivers, attribution, drill-down, context, validation and hypotheses | `src/drivers/`, `src/drilldown/`, `src/context/`, `src/evidence/`, `src/hypotheses/` |
| Decision | Recommendations, experiments, historical learning and decision object | `src/recommendations/`, `src/experiments/`, `src/learning/`, `src/decision/` |
| Language | Narrative generation and conversational Q&A | `src/llm/` |
| Service / Presentation | FastAPI service + Streamlit interface | `api/`, `narrate_iq_frontend/` |

The FastAPI application registers health, analysis, experiment, learning, drill-down, root-cause, decision and chat routers. fileciteturn5file0L2-L2

---

# 4. Intelligence Pipeline

The frontend Data view exposes the ordered intelligence pipeline:

```text
1. src.kpi.engine
2. src.anomaly.engine
3. src.drivers.engine
4. src.attribution.engine
5. src.confidence.engine
6. src.drilldown.sales
7. src.context.events
8. src.evidence.validator
9. src.learning.history
10. src.learning.engine
11. src.hypotheses.engine
12. src.recommendations.engine
13. src.rootcause.engine
14. src.experiments.engine
15. src.decision.engine
16. src.llm.narrative
```

The Data screen runs these modules sequentially, shows progress, captures module logs, and stops on the first failed process. `sales.csv` is the required dataset for the current frontend pipeline; inventory, marketing and business-event data are supported as additional sources. fileciteturn47file0L2-L2

The processed-data reset logic maintains generated analytical artifacts separately from raw source files. fileciteturn45file0L2-L2

---

# 5. Analytics and Decisioning

## 5.1 Canonical KPI layer

The KPI engine creates a daily canonical KPI table from sales, marketing and inventory data.

Current core KPIs:

- Revenue
- Units sold
- Average selling price
- Marketing spend
- Conversion rate
- Stockout rate

The calculations are deterministic. Revenue is aggregated from sales transactions; ASP is total revenue divided by total units; conversion rate is total conversions divided by total clicks; and stockout rate is total stockout hours divided by theoretical available hours represented by inventory observations. fileciteturn10file0L2-L2

## 5.2 Temporal movement analysis

For each KPI the movement layer calculates day-over-day percentage change, week-over-week percentage change, 7-day rolling mean, 28-day rolling mean, 28-day rolling standard deviation, and rolling-baseline z-score. fileciteturn11file0L2-L2

## 5.3 Materiality classification

| KPI | WoW threshold |
|---|---:|
| Revenue | 5% |
| Units sold | 8% |
| Average selling price | 5% |
| Marketing spend | 10% |
| Conversion rate | 5% |
| Stockout rate | 3% |

A movement at or above 2× the threshold is `high`; a movement at or above the threshold is `medium`; smaller movement is `low`; unavailable movement history is `insufficient_history`. fileciteturn12file0L2-L2

## 5.4 Anomaly detection

The anomaly detector consumes KPI-engine outputs and flags an observation when its absolute z-score is at least 2.0 or when the KPI has `high` materiality. Each anomaly contains the date, KPI, value, z-score, WoW movement, materiality and direction. fileciteturn24file0L2-L2

## 5.5 Revenue driver decomposition

Narrate IQ explicitly models:

```text
Revenue = Units Sold × Average Selling Price
```

The driver analysis compares the current period with the prior comparable period and estimates volume and price effects, including relative contribution. fileciteturn26file0L2-L2

## 5.6 Multi-factor driver evidence

Daily sales, marketing and inventory signals are joined into a common driver-evidence table containing sales revenue and units, marketing spend/clicks/conversions, marketing conversion rate, stockout hours and closing stock. fileciteturn55file0L2-L2

## 5.7 ML-based driver attribution

The current attribution implementation uses a **Random Forest regression model with permutation importance** to estimate relative predictive importance of changes in candidate business drivers for revenue movement. It uses a time-ordered 80/20 train/test split and exports driver importance, direction and latest-period change. fileciteturn25file0L2-L2

A separate lagged-feature Random Forest model is also implemented for revenue prediction and reports MAE, R² and feature importance. fileciteturn27file0L2-L2

> **Interpretation:** model importance is predictive evidence / association, not causal proof.

## 5.8 Dimension-level drill-down

Sales-volume deterioration can be investigated across region, product and channel. The root-cause graph retains the most negative segments and estimates each segment's share of total negative unit movement. fileciteturn32file0L2-L2

## 5.9 Business-event context

Business events are aligned with KPI dates and categorized into analytical contexts such as marketing, inventory and competitive events. The context output also calculates revenue and unit movement against a preceding seven-day baseline. fileciteturn54file0L2-L2

## 5.10 Evidence-backed hypothesis ranking

The current hypothesis engine evaluates:

1. **Sales volume deterioration**
2. **Inventory constraint**
3. **Marketing efficiency deterioration**

Hypotheses are combined using:

```text
Combined score
= 0.45 × current confidence
+ 0.40 × evidence validation
+ 0.15 × historical reliability
```

The hypotheses are ranked by the resulting score and assigned confidence/status labels. fileciteturn34file0L2-L2

## 5.11 Recommendation engine

Recommendations are derived from structured hypotheses and their confidence, not invented by the LLM. Priority is `high` at ≥0.65, `medium` at ≥0.35, and `low` otherwise. fileciteturn53file0L2-L2

## 5.12 Decision object

The decision engine consolidates the latest state into `decision_object.json`, including current KPI state, leading hypothesis, confidence and validation, affected segments, business events, recommendation, experiment state/outcome and historical learning. fileciteturn30file0L2-L2

---

# 6. Evidence and Uncertainty

Narrate IQ avoids treating a single analytical signal as sufficient proof.

The evidence-validation layer combines:

- **Statistical evidence** — directional driver movement and model importance
- **Business context** — relevant events around the KPI movement
- **Segment evidence** — concentration of deterioration across dimensions

The resulting validation record includes component scores, supporting evidence and contradicting evidence. fileciteturn35file0L2-L2

The confidence layer separately scores driver evidence using model importance, anomaly evidence, materiality and magnitude of change, producing a bounded score and `high` / `medium` / `low` label. fileciteturn33file0L2-L2

### Evidence ≠ causation

Random Forest importance is not presented as proof that a driver caused a KPI movement. The Copilot is explicitly instructed to preserve the distinction between evidence and causation. fileciteturn25file0L2-L2 fileciteturn15file0L2-L2

---

# 7. Experiment and Learning Loop

```text
Hypothesis
    ↓
Recommendation
    ↓
Experiment
    ↓
Outcome
    ↓
Historical Reliability
    ↓
Future Hypothesis Ranking
```

## Experiment lifecycle

Experiments support:

```text
proposed → running → completed
```

Each experiment records a hypothesis, target metric, expected direction, success threshold, baseline, observed value, measured change and outcome. Existing running/completed experiment state is preserved when the experiment layer is regenerated. fileciteturn37file0L2-L2

The API exposes listing, start and outcome operations. fileciteturn57file0L2-L2

## Historical learning

Completed experiments are aggregated by hypothesis into attempts, successes, partials, failures, success rate, non-failure rate and historical reliability.

```text
Historical reliability
= 0.7 × success rate
+ 0.3 × non-failure rate
```

Historical reliability becomes a smaller component of future hypothesis ranking. fileciteturn42file0L2-L2

---

# 8. AI Copilot

The AI Copilot is deliberately **not a general-purpose chatbot**. It is a conversational interface over Narrate IQ's current structured decision context.

Suggested questions include:

- `Why did revenue decline?`
- `Why not marketing?`
- `Did the experiment work?`

The frontend maintains conversation state and sends questions to `/chat`. fileciteturn39file0L2-L2

## Grounding flow

```text
User question
     ↓
POST /chat
     ↓
Load decision_object.json
     ↓
Build evidence-grounded prompt
     ↓
LLM
     ↓
Concise business answer
```

The prompt instructs the model to use only supplied context, preserve exact numbers, never invent facts/metrics/events/causes/recommendations/outcomes, distinguish evidence from causation, acknowledge weak evidence, and state when information is unavailable. fileciteturn15file0L2-L2

## LLM provider

The canonical provider implementation in `src/llm/client.py` uses the **Groq** Python client and `GROQ_API_KEY`; the default model is `llama-3.3-70b-versatile`, configurable through `LLM_MODEL`. fileciteturn28file0L2-L2

The repository also contains an alternate API-side implementation under `api/src/llm/chat.py` using the OpenAI client. The root `.env.example` and canonical `src/llm/client.py` configure the primary project path around Groq. fileciteturn31file0L2-L2

---

# 9. Frontend

The prototype frontend is built with **Streamlit** and lives in `narrate_iq_frontend/`.

Navigation:

```text
Executive | Root Cause | Experiments | Learning | Data | AI Copilot
```

The entry point handles page configuration, session state, sidebar navigation and view dispatch. fileciteturn13file0L2-L2

### Executive

Presents the decision loop as **WHAT → WHY → WHERE → DECISION → EXPERIMENT → LEARNING**, including revenue movement, units, confidence, evidence strength, hypothesis, supporting evidence, affected segments, recommendation, experiment state/outcome and historical reliability. fileciteturn38file0L2-L2

### Root Cause

Shows ranked hypotheses and a contribution explorer across dimensions such as region, product and channel. fileciteturn56file0L2-L2

### Experiments

Exposes experiment lifecycle and outcome tracking.

### Learning

Surfaces historical hypothesis reliability and experiment history.

### Data

Provides dataset status, CSV upload/replacement, preview quality scoring, column/data preview, pipeline execution, module progress and failure logs. fileciteturn47file0L2-L2

### AI Copilot

Provides suggested questions, free-form business questions, conversation history and the grounded `/chat` integration. fileciteturn39file0L2-L2

---

# 10. Backend API

The backend is implemented with **FastAPI**. It registers health, analysis, experiments, learning, drill-down, root-cause, decision and chat routers. fileciteturn5file0L2-L2

The API reads processed artifacts through a CSV repository abstraction and returns explicit errors when required processed outputs are missing. fileciteturn8file0L2-L2

---

# 11. Data Model and Outputs

## Raw source contracts

The ingestion schema defines contracts for:

- `sales.csv`
- `marketing.csv`
- `inventory.csv`
- `business_events.csv`
- `kpi_dictionary.csv`
- `source_metadata.csv`

Each source specifies required columns and, for time-aware sources, date parsing requirements. fileciteturn23file0L2-L2

| Source | Purpose |
|---|---|
| `sales.csv` | Transaction-level commercial performance |
| `marketing.csv` | Campaign/channel efficiency |
| `inventory.csv` | Availability and stockout evidence |
| `business_events.csv` | Business context and external events |
| `kpi_dictionary.csv` | KPI definitions, formulas, drivers, thresholds, source and owner |
| `source_metadata.csv` | Source grain, refresh, ownership, quality and security metadata |

## Processed artifacts

| Artifact | Purpose |
|---|---|
| `daily_kpis.csv` | Canonical daily KPI layer |
| `anomalies.csv` | Material/anomalous KPI movements |
| `revenue_drivers.csv` | Volume/price decomposition |
| `revenue_driver_ranking.csv` | Ranked revenue-driver view |
| `driver_evidence.csv` | Joined sales/marketing/inventory evidence |
| `driver_attribution.csv` | Driver importance and latest changes |
| `ml_driver_importance.csv` | Lagged-feature ML importance |
| `confidence_scores.csv` | Driver confidence scores |
| `sales_dimension_drilldown.csv` | Region/product/channel evidence |
| `event_context.csv` | Business-event alignment |
| `evidence_validation.csv` | Hypothesis evidence validation |
| `hypotheses.csv` | Ranked explanations |
| `recommendations.csv` | Structured actions |
| `root_cause_graph.csv` | Hypothesis and segment graph |
| `experiments.csv` | Experiment state |
| `experiment_history.csv` | Experiment history |
| `hypothesis_history.csv` | Historical reliability |
| `decision_object.json` | Canonical decision context |
| `business_narrative.txt` | Business narrative |

The pipeline reset logic explicitly maintains these generated outputs in `data/processed/`. fileciteturn45file0L2-L2

---

# 12. Repository Structure

```text
Narrate_IQ/
│
├── .env.example
├── .gitignore
├── Readme.md
├── requirements.txt
├── requirements-lock.txt
│
├── api/
│   ├── main.py
│   ├── dependencies.py
│   ├── schemas.py
│   ├── serializers.py
│   ├── chat_schemas.py
│   ├── experiment_schemas.py
│   ├── routes/
│   │   ├── analysis.py
│   │   ├── chat.py
│   │   ├── decision.py
│   │   ├── drilldown.py
│   │   ├── experiments.py
│   │   ├── health.py
│   │   ├── learning.py
│   │   └── rootcause.py
│   └── src/llm/
│       └── chat.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── ingestion/
│   ├── kpi/
│   ├── anomaly/
│   ├── drivers/
│   ├── confidence/
│   ├── hypotheses/
│   ├── evidence/
│   ├── drilldown/
│   ├── context/
│   ├── rootcause/
│   ├── recommendations/
│   ├── experiments/
│   ├── learning/
│   ├── decision/
│   └── llm/
│
├── narrate_iq_frontend/
│   ├── app.py
│   ├── api_client.py
│   ├── components.py
│   ├── data_quality.py
│   ├── theme.py
│   ├── requirements.txt
│   └── views/
│       ├── executive.py
│       ├── root_cause.py
│       ├── experiments.py
│       ├── learning.py
│       ├── data.py
│       └── copilot.py
│
└── tests/
    └── test_api.py
```

---

# 13. Data Ingestion and Validation

For each declared source, the ingestion layer checks:

1. File existence
2. Required columns
3. Date parsing
4. Invalid dates
5. Basic quality statistics

The ingestion pipeline produces a quality report containing row count, column count, duplicate rows, missing values and date range. fileciteturn36file0L2-L2

The frontend's local quality score is intentionally only a preview and does not replace backend ingestion validation. fileciteturn47file0L2-L2

---

# 14. Setup

## Prerequisites

Recommended:

- Python 3.11+
- Git
- pip
- Groq API key for the LLM layer

## Clone

```bash
git clone https://github.com/diptiman11/Narrate_IQ.git
cd Narrate_IQ
```

## Virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install

```bash
pip install -r requirements.txt
pip install -r narrate_iq_frontend/requirements.txt
```

## Environment

Copy `.env.example` to `.env` and configure:

```env
APP_ENV=development
DEBUG=true
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=
LOG_LEVEL=INFO
```

The configuration shape reflects the current repository example. fileciteturn31file0L2-L2

**Never commit a real API key.**

---

# 15. Running the System

Narrate IQ runs as two cooperating processes:

```text
FastAPI backend  ←→  Streamlit frontend
```

The frontend currently targets `http://127.0.0.1:8000`. fileciteturn14file0L2-L2

## A. Prepare raw data

Place source files under:

```text
data/raw/
```

At minimum, the current frontend workflow requires:

```text
data/raw/sales.csv
```

The richer pipeline uses marketing, inventory and business-event sources as well. fileciteturn47file0L2-L2

## B. Validate / ingest

```bash
python -m src.ingestion.pipeline
```

## C. Build the KPI layer

```bash
python -m src.kpi.pipeline
```

This loads sources, calculates daily KPIs, adds movement metrics and materiality flags, and writes `data/processed/daily_kpis.csv`. fileciteturn9file0L2-L2

## D. Run the complete intelligence pipeline

The recommended prototype workflow is the **Data → Run Narrate IQ Analysis** action because it executes the ordered modules with visible progress and failure logs. fileciteturn47file0L2-L2

## E. Start the API

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

## F. Start the frontend

In another terminal:

```bash
cd narrate_iq_frontend
streamlit run app.py
```

The frontend entry point is designed for `streamlit run app.py`. fileciteturn13file0L2-L2

Open the Streamlit URL printed by the terminal, normally `http://localhost:8501`.

---

# 16. API Reference

## Health

```http
GET /health
```

## Analysis

```http
GET /kpis
GET /anomalies
GET /drivers
GET /attribution
GET /confidence
GET /recommendations
GET /narrative
GET /analysis
```

The combined `/analysis` endpoint returns the latest KPI, anomalies, drivers, attribution, confidence, hypotheses, evidence validation, drill-down, recommendations and narrative. fileciteturn6file0L2-L2

## Decision

```http
GET /decision
```

Returns the canonical decision object consumed by the executive experience and Copilot. fileciteturn41file0L2-L2

## Root cause

```http
GET /root-cause
```

Returns the hypothesis and segment graph. fileciteturn56file0L2-L2

## Sales drill-down

```http
GET /drilldown/sales
```

## Experiments

```http
GET /experiments
POST /experiments/{experiment_id}/start
POST /experiments/{experiment_id}/outcome
```

The start operation records a baseline; the outcome operation records an observed value and advances experiment state. fileciteturn57file0L2-L2

## Learning

```http
GET /learning
```

## AI Copilot

```http
POST /chat
```

Example:

```json
{
  "question": "Why did revenue decline?",
  "conversation": []
}
```

The chat layer loads `decision_object.json`, constructs a grounded prompt, and returns the LLM answer. fileciteturn15file0L2-L2

---

# 17. Testing

The repository contains API tests in `tests/test_api.py` covering health and major analysis, decision, experiment, learning, root-cause and drill-down routes. The tests assert successful HTTP responses and key response structures. fileciteturn43file0L2-L2

Run:

```bash
pytest -q
```

Use this as the minimum smoke-test gate before submission.

---

# 18. Design Decisions

### Deterministic analytics before LLM

The system computes and validates quantitative outputs before language generation. fileciteturn10file0L2-L2

### Evidence composition

Statistical movement, model evidence, business context and segment evidence remain separately visible before hypotheses are ranked. fileciteturn35file0L2-L2

### Association is not causation

Random Forest importance is predictive evidence, not a causal estimate. The Copilot is explicitly instructed to preserve this distinction. fileciteturn25file0L2-L2 fileciteturn15file0L2-L2

### Recommendations are structured upstream

Operational recommendations are generated from structured hypotheses and confidence before the LLM is invoked. fileciteturn53file0L2-L2

### Decision object as the interface contract

`decision_object.json` is the structured hand-off between the analytical stack and conversational interface. fileciteturn30file0L2-L2

### Frontend / backend separation

Streamlit handles presentation, FastAPI exposes service endpoints, and intelligence logic remains in reusable Python modules. fileciteturn13file0L2-L2

---

# 19. Scope and Limitations

Narrate IQ is a **functional decision-intelligence prototype**, not a production enterprise deployment.

### Current capabilities

- Multi-source CSV ingestion
- Schema/date validation
- Deterministic KPI computation
- Temporal movement analysis
- Materiality classification
- Z-score anomaly detection
- Revenue volume/price decomposition
- Random Forest driver attribution
- Dimension-level drill-down
- Business-event context
- Evidence validation
- Confidence scoring
- Hypothesis ranking
- Structured recommendations
- Experiment lifecycle
- Historical learning
- Canonical decision object
- Executive Streamlit interface
- Grounded LLM Copilot

### Current limitations

- Persistence is CSV-based rather than a production database.
- Enterprise identity/authentication is not implemented in the current prototype.
- Confidence is a heuristic evidence score rather than a calibrated probability.
- Driver importance establishes predictive association, not causal identification.
- The frontend defaults to the local backend URL `127.0.0.1:8000`. fileciteturn14file0L2-L2
- The hypothesis library is bounded to the explanations implemented in the current engine.
- Copilot responses depend on the completeness and freshness of generated `decision_object.json`.

These boundaries are intentionally disclosed.

---

# 20. Submission / Evaluation Guide

## Recommended evaluation flow

```text
1. Inspect data contracts
2. Run ingestion validation
3. Build daily KPIs
4. Detect material movement / anomalies
5. Inspect driver evidence and attribution
6. Inspect evidence validation
7. Review ranked hypotheses
8. Inspect root-cause segments
9. Review the recommendation
10. Start / complete an experiment
11. Observe historical learning
12. Open the Executive view
13. Ask the Copilot: “Why did revenue decline?”
14. Verify that the answer stays within the structured decision context
```

## What makes the architecture defensible

- **Quantitative truth is not delegated to the LLM.** KPI and analytical layers produce the numbers first. fileciteturn10file0L2-L2
- **The system reasons from multiple evidence sources.** Statistical, event-context and segment evidence are retained separately. fileciteturn35file0L2-L2
- **Recommendations connect analysis to action.** Hypotheses become structured next actions and experiments. fileciteturn53file0L2-L2 fileciteturn37file0L2-L2
- **Experiments create a learning loop.** Outcomes feed historical reliability, which becomes a component of future hypothesis ranking. fileciteturn42file0L2-L2
- **The UI reflects the analytical model.** The Executive screen is organized around WHAT → WHY → WHERE → DECISION → EXPERIMENT → LEARNING. fileciteturn38file0L2-L2

## Security

Do not commit API keys, `.env` files containing secrets, or other credentials. Use `.env.example` as the configuration template. fileciteturn31file0L2-L2

---

## Technology Stack

**Backend:** Python, FastAPI, Uvicorn, Pydantic, python-dotenv  
**Analytics / ML:** Pandas, NumPy, SciPy, Statsmodels, scikit-learn  
**Frontend:** Streamlit, Plotly, Requests, Streamlit Option Menu  
**LLM:** Groq API, `llama-3.3-70b-versatile` by default

The dependency and provider configuration reflect the repository's current implementation. fileciteturn7file0L2-L2 fileciteturn28file0L2-L2

---

## Final Principle

> **Compute and validate business truth first. Package it into an inspectable decision context. Then use AI to make that verified context easier for people to understand and act on.**
