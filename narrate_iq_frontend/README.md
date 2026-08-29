# Narrate IQ — Frontend Redesign

A production-grade rebuild of your Streamlit frontend's *presentation layer*.
Your backend, intelligence engine, API routes, request/response shapes, and
the Groq chat integration are untouched — every `requests.get` / `requests.post`
call below hits the exact same endpoint with the exact same payload as your
original `app.py`.

## 1. What you're getting

```
narrate_iq_frontend/
├── app.py                 # entry point: page config, session state, sidebar nav, routing
├── theme.py                # design tokens + all CSS (edit this file to retheme the whole app)
├── components.py           # reusable UI: KPI tiles, badges, evidence meters, hero banner, etc.
├── api_client.py           # your original get_json / post_json / refresh_data / money / pct / signed_* — verbatim
├── data_quality.py         # new: quick local CSV quality score shown on the Data page
├── requirements.txt
├── README.md               # this file
└── views/
    ├── executive.py         # Executive dashboard (WHAT → WHY → WHERE → DECISION → EXPERIMENT → LEARNING)
    ├── root_cause.py         # ranked hypotheses + contribution explorer
    ├── experiments.py        # proposed → running → completed lifecycle
    ├── learning.py            # hypothesis reliability + experiment history
    ├── data.py                # dataset status, upload, quality check, pipeline runner
    └── copilot.py             # AI Copilot chat (your existing /chat + Groq backend)
```

`views/` is named that deliberately — **not** `pages/`, because Streamlit
auto-generates its own multipage navigation from a folder literally named
`pages/`, which would collide with the custom sidebar navigation built here.

## 2. Exact replacement instructions

1. Back up your current `app.py` (rename it, e.g. `app.py.bak`) — you don't need
   it, but keep it until you've confirmed the new app runs against your backend.
2. Copy every file above into the **same directory** your current `app.py` lives in
   (the directory that already contains your `data/` folder and can import `src.*`).
3. Install the one new dependency:
   ```
   pip install -r requirements.txt
   ```
4. Start your FastAPI backend exactly as you do today (unchanged — still expected
   at `http://127.0.0.1:8000`, see `api_client.py` if you need to change `API_URL`).
5. Run the new frontend:
   ```
   streamlit run app.py
   ```

That's it — no other files, no backend changes, no migration steps.

## 3. New dependency — why

**`streamlit-option-menu`** (~small, single-purpose, no transitive dependency
bloat) replaces the plain `st.sidebar.radio(...)` navigation with a proper
icon-led sidebar nav (Executive / Root Cause / Experiments / Learning / Data /
AI Copilot). This is the single highest-leverage visual change for making the
app read as a persistent enterprise nav rather than a form control, so it's
worth the one extra package. If you'd rather not add it, everything else in
this redesign works independently — swap `option_menu(...)` in `app.py` back
for `st.sidebar.radio(...)` and remove the import block at the top of `app.py`.

`streamlit`, `requests`, `pandas`, and `plotly` are the same dependencies you
already had — only the minimum Streamlit version is pinned up slightly
(1.32+) to guarantee `st.column_config.ProgressColumn` is available for the
reliability/confidence progress bars on the Root Cause and Learning pages.

## 4. What actually changed vs. what didn't

**Unchanged (verified line-by-line against your original code):**
- Every endpoint: `/decision`, `/root-cause`, `/experiments`, `/experiments/{id}/start`,
  `/experiments/{id}/outcome`, `/learning`, `/chat`.
- Every request payload shape (`{baseline_value}`, `{observed_value}`,
  `{question, conversation}`) and every response field your UI reads.
- The `@st.cache_data(ttl=20)` caching behavior and `refresh_data()` semantics.
- The pipeline module list and subprocess execution order on the Data page,
  including "sales.csv is required" and stop-on-first-failure behavior.
- `money()`, `pct()`, `signed_pct()`, `signed_number()` — identical formatting rules.
- Your Groq-backed `/chat` integration and multi-turn conversation payload.

**New / redesigned (all purely presentational or additive):**
- Full dark enterprise visual system: token-based palette, Inter + JetBrains
  Mono pairing (mono for every number, so figures line up like a terminal),
  restrained color use (green = positive, red = negative, amber = partial/
  warning, blue = interactive-only accent, gray = neutral) — see `theme.py`.
- Information architecture on the Executive page now literally walks the
  DATA → INSIGHT → EVIDENCE → DECISION → ACTION → EXPERIMENT → LEARNING loop,
  each stage numbered and labeled, instead of ad hoc section dividers.
- Confidence/validation/segment/context scores are now progress meters, not
  bare percentages.
- The segment/contribution bar charts are colored by sign (green = growth,
  red = decline) with direct value labels, instead of a single flat color.
- Experiments show an actual proposed → running → completed stepper.
- The Data page's file existence checks now sit next to **real upload
  controls** — your original code only ever *checked* for
  `data/raw/*.csv`, it had no way to provide them. Uploading writes straight
  to the same `data/raw/<filename>` paths your pipeline already reads, so
  nothing downstream needed to change.
- A quick, local, frontend-only data quality score (row count / missing % /
  duplicate %) shown on upload, clearly labeled as a preview check — not a
  replacement for your real backend validation.
- Consistent empty states and error states (a dashed panel with an icon and a
  plain-language explanation) everywhere a `requests.RequestException` or an
  empty payload can occur, instead of a bare `st.error(str(exc))`.
- **Bug fix:** the original Data page called `Path("data/raw") / filename`
  without importing `pathlib.Path` anywhere in the file — that would raise
  `NameError` the moment you opened that tab. `views/data.py` now imports it.

**Deliberately not touched:** column-mapping is intentionally left as a
"preview only" step (`views/data.py`, inside the upload expander) rather than
enforcing a hard-coded expected schema, because your real schema lives in
your ingestion/validation modules and guessing it here risked silently
rejecting valid files. If you want strict mapping in the UI, tell me your
expected columns per dataset and I'll wire real mapping controls against them.

## 5. If something doesn't run

- `ModuleNotFoundError: streamlit_option_menu` → `pip install -r requirements.txt`.
- Sidebar shows no icons → the icon names used (`speedometer2`, `search`,
  `flask`, `graph-up-arrow`, `database`, `chat-dots`) are Bootstrap Icons
  names bundled with `streamlit-option-menu`; if you're on an old pinned
  version of that package, upgrade it.
- Everything loads but the Executive page shows a red "Unable to load Narrate
  IQ decision" panel → that's the new error state doing its job: your FastAPI
  backend isn't reachable at `API_URL` in `api_client.py`. This is the same
  failure your original code hit, just presented more clearly.
