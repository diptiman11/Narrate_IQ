from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.analysis import router as analysis_router
from api.routes.chat import router as chat_router
from api.routes.decision import router as decision_router
from api.routes.drilldown import router as drilldown_router
from api.routes.experiments import router as experiments_router
from api.routes.health import router as health_router
from api.routes.learning import router as learning_router
from api.routes.rootcause import router as rootcause_router


app = FastAPI(
    title="Narrate IQ",
    description="KPI Intelligence-to-Action Engine",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router
)

app.include_router(
    analysis_router
)

app.include_router(
    experiments_router
)

app.include_router(
    learning_router
)

app.include_router(
    drilldown_router
)

app.include_router(
    rootcause_router
)

app.include_router(
    decision_router
)

app.include_router(
    chat_router
)