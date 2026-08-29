# Narrate IQ

### KPI Intelligence → Evidence → Decision → Action → Experiment → Learning

Narrate IQ is an evidence-grounded business intelligence and decision-support prototype that goes beyond showing KPI movement. It combines deterministic KPI computation, anomaly detection, driver analysis, ML-based attribution, business-event context, evidence validation, hypothesis ranking, recommendations, experiment tracking, historical learning, and a grounded AI Copilot.

> **Core principle:** compute and validate quantitative business truth first. Use the LLM to communicate that verified decision context—not to invent KPI values, causes, recommendations, or experiment outcomes.

---

## Table of Contents

- [Overview](#overview)
- [Why Narrate IQ](#why-narrate-iq)
- [End-to-End Architecture](#end-to-end-architecture)
- [Core Intelligence Pipeline](#core-intelligence-pipeline)
- [Analytics](#analytics)
- [Evidence and Confidence](#evidence-and-confidence)
- [Hypothesis and Decision Layer](#hypothesis-and-decision-layer)
- [Experiment and Learning Loop](#experiment-and-learning-loop)
- [AI Copilot](#ai-copilot)
- [Frontend](#frontend)
- [Backend](#backend)
- [Data](#data)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [API](#api)
- [Testing](#testing)
- [Technical Design Rationale](#technical-design-rationale)
- [Limitations](#limitations)
- [Evaluation / Demo Flow](#evaluation--demo-flow)

---

## Overview

Narrate IQ is designed around a complete business decision loop:

```text
                 ┌──────────────────────┐
                 │     BUSINESS DATA    │
                 │ Sales / Marketing /  │
                 │ Inventory / Events   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ INGESTION & QUALITY  │
                 │ Schema + date checks │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    KPI ENGINE        │
                 │ Revenue / Units /    │
                 │ ASP / Conversion /   │
                 │ Marketing / Stockout │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ MOVEMENT & ANOMALY   │
                 │ WoW / DoD / Rolling  │
                 │ Baselines / Z-score  │
                 │ Materiality          │
                 └──────────┬───────────┘
                            │
                            ▼
          ┌────────────────────────────────────┐
          │       DRIVER / EVIDENCE LAYER      │
          │ Volume + Price + ML attribution    │
          │ Segment drill-down + Event context │
          └──────────────────┬─────────────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │ EVIDENCE VALIDATION  │
                 │ Statistical + Event  │
                 │ + Segment evidence   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ HYPOTHESIS ENGINE    │
                 │ Rank + Confidence    │
                 │ + Historical signal  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ RECOMMENDATION       │
                 │ Structured actions   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ EXPERIMENT            │
                 │ Proposed → Running → │
                 │ Completed             │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ HISTORICAL LEARNING  │
                 │ Reliability by       │
                 │ hypothesis            │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ DECISION OBJECT      │
                 │ Canonical context    │
                 └──────────┬───────────┘
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
          Executive UI            AI Copilot
```

The important architectural boundary is between the analytical system and the language system. Quantitative calculations, evidence scores, hypotheses and recommendations are generated upstream; the Copilot consumes the resulting decision context.

---

## Why Narrate IQ

A conventional BI dashboard answers **what changed**. Narrate IQ is designed to answer the broader sequence:

1. **What changed?** — KPI movement and anomaly detection.
2. **How material is it?** — KPI-specific materiality thresholds.
3. **Why might it have changed?** — driver analysis and ranked hypotheses.
4. **What evidence supports that explanation?** — statistical, segment and business-event evidence.
5. **Where is the impact concentrated?** — region/product/channel drill-down.
6. **What should we do?** — structured recommendation engine.
7. **How can we test it?** — experiment lifecycle.
8. **What did we learn?** — historical reliability by hypothesis.
9. **How can a decision-maker ask questions?** — grounded AI Copilot.

This turns BI from a reporting surface into an inspectable decision-support workflow.

---

# End-to-End Architecture

Narrate IQ has four major execution boundaries:

### 1. Data and deterministic analytics

Raw source files are validated and transformed into canonical daily KPIs and analytical features.

### 2. Evidence and reasoning

Multiple signals are combined into driver evidence, segment evidence, business context, validation scores and hypotheses.

### 3. Decision loop

Hypotheses become recommendations and experiments. Experiment outcomes feed historical reliability.

### 4. Human interface

FastAPI exposes the analytical state and Streamlit presents it as an executive decision workflow. The AI Copilot uses the same structured decision object as its grounding context.

---

# Core Intelligence Pipeline

The source tree separates the intelligence engine into focused modules:

```text
src/
├── ingestion/       # Source contracts, loading and quality validation
├── kpi/             # Daily KPI calculation and movement metrics
├── anomaly/         # Material/anomaly detection
├── drivers/         # Driver evidence, decomposition and ML attribution
├── confidence/      # Evidence-based confidence scoring
├── hypotheses/      # Hypothesis generation and ranking
├── evidence/        # Evidence validation
├── drilldown/       # Sales dimension analysis
├── context/         # Business-event context
├── rootcause/       # Root-cause graph construction
├── recommendations/ # Structured recommendations
├── experiments/     # Experiment lifecycle
├── learning/        # Historical reliability
├── decision/        # Canonical decision object
└── llm/             # LLM client and business narrative
```

The frontend adds a presentation/API boundary:

```text
narrate_iq_frontend/
├── app.py
├── api_client.py
├── components.py
├── data_quality.py
├── theme.py
└── views/
    ├── executive.py
    ├── root_cause.py
    ├── experiments.py
    ├── learning.py
    ├── data.py
    └── copilot.py
```

---

# Analytics

## KPI layer

The canonical daily KPI table currently includes:

- Revenue
- Units sold
- Average selling price
- Marketing spend
- Conversion rate
- Stockout rate

The KPI implementation is deterministic and reproducible.

### Revenue

```text
Revenue = SUM(transaction revenue)
```

### Units sold

```text
Units Sold = SUM(transaction units)
```

### Average selling price

```text
ASP = Total Revenue / Total Units Sold
```

### Conversion rate

```text
Conversion Rate = Total Conversions / Total Clicks
```

### Stockout rate

```text
Stockout Rate = Total Stockout Hours
                 / (Inventory Observations × 24)
```

---

## Temporal movement

For each KPI, Narrate IQ computes:

- Day-over-day percentage change
- Week-over-week percentage change
- 7-day rolling mean
- 28-day rolling mean
- 28-day rolling standard deviation
- Rolling-baseline z-score

This provides both short-term movement and a longer historical baseline.

---

## Materiality

KPI-specific thresholds prevent the system from treating every small fluctuation as a business incident.

| KPI | Current WoW threshold |
|---|---:|
| Revenue | 5% |
| Units sold | 8% |
| Average selling price | 5% |
| Marketing spend | 10% |
| Conversion rate | 5% |
| Stockout rate | 3% |

Classification:

```text
abs(movement) >= 2 × threshold  → high
abs(movement) >= threshold      → medium
otherwise                        → low
missing history                  → insufficient_history
```

---

## Anomaly detection

The anomaly layer consumes KPI-engine output and flags a record when either:

- absolute rolling z-score ≥ 2.0, or
- materiality is `high`.

An anomaly record contains the date, KPI, observed value, z-score, WoW change, materiality and direction.

---

## Revenue driver analysis

Revenue is explicitly modeled as:

```text
Revenue = Units Sold × Average Selling Price
```

The revenue driver layer estimates:

- Volume effect
- Price effect
- Volume contribution percentage
- Price contribution percentage

This provides an interpretable explanation before the LLM is involved.

> The current decomposition is a volume/price decomposition. It should not be described as a full price-volume-mix decomposition because product-mix is not separately calculated in the current implementation.

---

## ML driver attribution

Narrate IQ also builds a common daily evidence table from sales, marketing and inventory signals.

Candidate driver features include:

- Sales units
- Marketing spend
- Marketing clicks
- Marketing conversions
- Marketing conversion rate
- Stockout hours
- Closing stock

The attribution implementation uses a **Random Forest regressor** with **permutation importance** and a time-ordered 80/20 train/test split.

A separate lagged-feature Random Forest implementation adds previous-day values, previous-seven-day values and a rolling revenue feature and reports MAE, R² and feature importance.

### Important interpretation

Random Forest feature importance indicates predictive association/usefulness. It is **not causal inference**. Narrate IQ therefore treats it as one evidence component rather than a causal proof.

---

# Evidence and Confidence

Narrate IQ deliberately keeps evidence components visible.

## Evidence validation

Hypotheses can receive evidence from:

### Statistical evidence

Observed directional changes and ML importance.

### Business-event evidence

Relevant events aligned with the KPI movement, including inventory, marketing or competitive context.

### Segment evidence

Concentration of negative unit movement across region, product and channel.

The validator records:

- Validation score
- Statistical score
- Event-context score
- Segment-evidence score
- Supporting evidence
- Contradicting evidence

---

## Confidence scoring

Driver confidence is calculated from multiple signals:

- ML importance
- Anomaly evidence
- KPI materiality
- Magnitude of driver movement

The result is bounded to 0–1 and labeled:

```text
>= 0.75  → high
>= 0.50  → medium
<  0.50  → low
```

This is a heuristic evidence score, not a calibrated probability.

---

# Hypothesis and Decision Layer

The current hypothesis engine evaluates three primary business explanations:

1. **Sales volume deterioration**
2. **Inventory constraint**
3. **Marketing efficiency deterioration**

Hypothesis ranking combines current evidence, validation and historical learning:

```text
Combined Score
= 0.45 × Current Confidence
+ 0.40 × Validation Score
+ 0.15 × Historical Reliability
```

Each hypothesis receives:

- Rank
- Confidence score
- Confidence label
- Validation score
- Historical reliability
- Status
- Supporting evidence

---

## Recommendations

The recommendation engine maps structured hypotheses to operational actions.

Current action families include:

- Investigating sales-volume decline by region, product and channel
- Investigating inventory availability and replenishment
- Reviewing campaign/channel efficiency before increasing marketing spend

Recommendation priority is derived from hypothesis confidence:

```text
>= 0.65 → high
>= 0.35 → medium
otherwise → low
```

Recommendations are therefore generated upstream of the LLM.

---

# Experiment and Learning Loop

Narrate IQ is designed to close the loop between analysis and action.

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

```text
proposed → running → completed
```

An experiment records:

- Experiment ID
- Hypothesis
- Target metric
- Expected direction
- Success threshold
- Baseline value
- Observed value
- Measured change
- Outcome

The API supports listing experiments, starting an experiment with a baseline and recording an outcome.

## Historical learning

Completed experiments are aggregated by hypothesis into:

- Attempts
- Successes
- Partials
- Failures
- Success rate
- Non-failure rate
- Historical reliability

Current reliability formula:

```text
Historical Reliability
= 0.7 × Success Rate
+ 0.3 × Non-failure Rate
```

Historical reliability contributes 15% of the combined hypothesis score.

---

# AI Copilot

The Copilot is intentionally a **business-analysis assistant**, not a general chatbot.

Example questions:

```text
Why did revenue decline?
Why not marketing?
Did the experiment work?
```

## Grounding architecture

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
Business answer
```

The prompt instructs the model to:

- Use only the supplied Narrate IQ context
- Preserve exact numbers
- Never invent facts, metrics, events, causes, recommendations or experiment outcomes
- Distinguish evidence from causation
- Explicitly acknowledge weak evidence
- Compare hypotheses using their confidence/validation evidence
- Reuse generated recommendations where appropriate
- Use experiment baseline, observed value, measured change and outcome when answering experiment questions
- State when information is unavailable

## LLM provider

The canonical implementation in `src/llm/client.py` uses the **Groq** client.

Configuration:

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=your_key
```

The repository also contains an alternate API-side chat implementation under `api/src/llm/chat.py` using the OpenAI client. The primary configuration and canonical client use Groq.

---

# Frontend

The frontend is a Streamlit application with a custom enterprise-style navigation shell.

## Executive

The main decision screen is organized as:

```text
WHAT → WHY → WHERE → DECISION → EXPERIMENT → LEARNING
```

It displays:

- Revenue movement
- Units sold
- Confidence
- Evidence strength
- Leading hypothesis
- Supporting evidence
- Top affected segments
- Recommendation
- Experiment state/outcome
- Historical reliability

## Root Cause

Provides ranked hypotheses and an interactive contribution explorer across available dimensions such as region, product and channel.

## Experiments

Provides the experiment lifecycle and outcome workflow.

## Learning

Displays historical hypothesis reliability and experiment history.

## Data

Provides:

- Dataset status
- CSV upload/replacement
- Quick local quality preview
- Column/data preview
- Pipeline execution UI
- Progress and failure logs

The local quality preview reports row count, missing percentage and duplicate percentage. It is explicitly a pre-validation convenience layer; backend ingestion still performs source validation.

## AI Copilot

Provides suggested questions, free-form chat and conversation state through the `/chat` API.

---

# Backend

The service layer is implemented with FastAPI.

The application registers routes for:

- Health
- KPI/analysis
- Experiments
- Learning
- Drill-down
- Root cause
- Decision
- Chat

The API reads generated analytical artifacts from `data/processed/` through a CSV repository abstraction.

---

# Data

Narrate IQ expects the following source contracts under `data/raw/`:

| Source | Purpose |
|---|---|
| `sales.csv` | Transaction-level commercial performance |
| `marketing.csv` | Campaign/channel performance |
| `inventory.csv` | Stock and availability evidence |
| `business_events.csv` | Business context and external events |
| `kpi_dictionary.csv` | KPI definitions, formulas, drivers, thresholds and owners |
| `source_metadata.csv` | Source grain, refresh, ownership, quality and security metadata |

The ingestion schemas define required columns and date parsing requirements for the time-aware sources.

## Raw vs processed data

```text
data/raw/
    ↓
validated source tables
    ↓
data/processed/
    ├── daily_kpis.csv
    ├── anomalies.csv
    ├── driver_evidence.csv
    ├── revenue_drivers.csv
    ├── revenue_driver_ranking.csv
    ├── driver_attribution.csv
    ├── ml_driver_importance.csv
    ├── confidence_scores.csv
    ├── sales_dimension_drilldown.csv
    ├── event_context.csv
    ├── evidence_validation.csv
    ├── hypotheses.csv
    ├── recommendations.csv
    ├── root_cause_graph.csv
    ├── experiments.csv
    ├── hypothesis_history.csv
    ├── decision_object.json
    └── business_narrative.txt
```

---

# Repository Structure

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

# Installation

## Prerequisites

- Python 3.11+
- Git
- pip
- Groq API key for the LLM features

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

## Install dependencies

```bash
pip install -r requirements.txt
pip install -r narrate_iq_frontend/requirements.txt
```

The root requirements cover analytics/ML, FastAPI, testing, plotting, Groq, Streamlit and HTTP clients. The frontend requirements add `streamlit-option-menu`.

---

# Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure:

```env
APP_ENV=development
DEBUG=true

LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_api_key

DATABASE_URL=
LOG_LEVEL=INFO
```

Never commit a real API key.

---

# Running Locally

Narrate IQ has two local processes:

```text
FastAPI :8000
     ↕
Streamlit :8501
```

## 1. Prepare data

Place the source files under:

```text
data/raw/
```

At minimum, the current Data workflow requires:

```text
data/raw/sales.csv
```

For the complete evidence workflow, provide marketing, inventory and business-event sources as well.

## 2. Validate ingestion

```bash
python -m src.ingestion.pipeline
```

This reports source row counts, column counts, duplicate rows, missing values and date ranges.

## 3. Build the KPI layer

```bash
python -m src.kpi.pipeline
```

This loads the sources, computes daily KPIs, adds movement metrics and materiality flags, and writes `data/processed/daily_kpis.csv`.

## 4. Run the remaining analytical modules

The source tree contains dedicated executable modules for anomaly detection, driver evidence/analysis, attribution, confidence, drill-down, event context, evidence validation, learning, hypotheses, recommendations, root cause, experiments, decision construction and narrative generation.

When reproducing the full pipeline from a clean checkout, execute the modules in dependency order, beginning with ingestion and KPI generation and ending with decision/narrative generation. The Streamlit Data screen provides the intended interactive pipeline workflow for the prototype.

## 5. Start FastAPI

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

## 6. Start Streamlit

In a second terminal:

```bash
cd narrate_iq_frontend
streamlit run app.py
```

Open the URL printed by Streamlit, normally:

```text
http://localhost:8501
```

---

# API

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

`/analysis` combines the latest KPI, anomalies, driver information, attribution, confidence, hypotheses, evidence validation, drill-down, recommendations and narrative.

## Decision

```http
GET /decision
```

Returns the consolidated decision object used by the executive interface and Copilot.

## Root cause

```http
GET /root-cause
```

Returns the hypothesis/segment root-cause graph.

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

Example start payload:

```json
{
  "baseline_value": 1000
}
```

Example outcome payload:

```json
{
  "observed_value": 1080
}
```

## Learning

```http
GET /learning
```

## AI Copilot

```http
POST /chat
```

Example request:

```json
{
  "question": "Why did revenue decline?",
  "conversation": []
}
```

---

# Testing

The repository includes API-level tests under `tests/test_api.py`.

The suite covers the health endpoint and major analysis, decision, experiment, learning, root-cause and sales-drilldown routes.

Run:

```bash
pytest -q
```

Recommended submission gate:

```text
1. Fresh virtual environment
2. Install dependencies
3. Configure environment
4. Validate data
5. Run analytical pipeline
6. Start API
7. Start frontend
8. Run pytest
9. Manually verify Executive + Root Cause + Experiments + Learning + Copilot
```

---

# Technical Design Rationale

## 1. Why deterministic KPI computation?

Business metrics must be reproducible. Revenue, units, ASP, conversion and stockout metrics are computed directly from structured data rather than asking an LLM to calculate them.

## 2. Why separate materiality from anomaly detection?

A statistical deviation and a business-significant movement are related but not identical. The system keeps KPI-specific materiality thresholds separate from the z-score anomaly signal.

## 3. Why multiple evidence sources?

A single model feature should not automatically become a business explanation. Narrate IQ combines statistical movement, predictive driver evidence, segment concentration and business events before ranking hypotheses.

## 4. Why a decision object?

`decision_object.json` provides a stable structured contract between the intelligence engine and user-facing language interface. It prevents the Copilot from needing to independently rediscover the business state.

## 5. Why experiments?

A recommendation without outcome measurement is incomplete. Experiments turn hypotheses into testable actions and create historical evidence for future ranking.

## 6. Why historical learning?

Different organizations and situations may repeatedly exhibit different patterns. Recording experiment outcomes allows the system to incorporate empirical reliability into future hypothesis ranking.

## 7. Why not call the ML attribution causal inference?

Random Forest feature importance measures predictive usefulness. Without a causal identification strategy or controlled experiment, it cannot establish that a variable caused the KPI movement. Narrate IQ therefore uses experiments as the mechanism for validating actions rather than overstating model importance as causality.

---

# Limitations

Narrate IQ is a **functional decision-intelligence prototype** rather than a production enterprise platform.

Current boundaries include:

- CSV-based persistence rather than a production database
- Prototype-level local deployment
- No enterprise identity provider / SSO implementation
- Heuristic confidence scoring rather than calibrated probabilities
- Predictive attribution rather than causal inference
- Bounded hypothesis library
- Localhost-oriented frontend/API configuration
- Copilot quality depends on the completeness of the generated decision context

These limitations are explicit design boundaries for the prototype and should be considered when evaluating production readiness.

---

# Evaluation / Demo Flow

The strongest way to evaluate Narrate IQ is to follow one business situation through the complete loop.

```text
                 BUSINESS QUESTION
                        │
                        ▼
                KPI movement detected
                        │
                        ▼
                  Anomaly flagged
                        │
                        ▼
                 Drivers identified
                        │
                        ▼
                Evidence validated
                        │
                        ▼
                Hypotheses ranked
                        │
                        ▼
                  Root cause view
                        │
                        ▼
                  Recommendation
                        │
                        ▼
                    Experiment
                        │
                        ▼
                     Outcome
                        │
                        ▼
               Historical learning
                        │
                        ▼
                Decision object
                        │
                        ▼
                    AI Copilot
```

### Suggested demo questions

**Executive:**

> What is happening to revenue?

**Root Cause:**

> Which hypothesis has the strongest evidence, and where is the impact concentrated?

**Decision:**

> What action should the business take?

**Experiment:**

> How would we test that action?

**Learning:**

> Has this type of hypothesis worked before?

**Copilot:**

> Why did revenue decline?

Then verify that the Copilot answer uses the same numbers and evidence already visible in the decision context.

---

# Security

- Keep secrets in `.env` or the deployment secret manager.
- Never commit API keys.
- Do not place production credentials in example files.
- Treat uploaded business data as potentially sensitive in a real deployment.
- The current prototype's `security_scope` metadata is descriptive; it is not a substitute for production authorization controls.

---

# Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv

### Analytics / ML

- Pandas
- NumPy
- SciPy
- Statsmodels
- scikit-learn

### Frontend

- Streamlit
- Plotly
- Requests
- Streamlit Option Menu

### LLM

- Groq API
- `llama-3.3-70b-versatile` by default

---

# Final Principle

> **Compute and validate business truth first. Package it into an inspectable decision context. Then use AI to make that verified context easier for people to understand and act on.**

That separation is the foundation of Narrate IQ's reliability, traceability and extensibility.
