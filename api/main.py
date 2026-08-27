from fastapi import FastAPI

from api.routes.analysis import router as analysis_router
from api.routes.experiments import router as experiments_router
from api.routes.health import router as health_router
from api.routes.learning import router as learning_router


app = FastAPI(
    title="Narrate IQ",
    description="KPI Intelligence-to-Action Engine",
    version="0.1.0",
)


app.include_router(health_router)
app.include_router(analysis_router)
app.include_router(experiments_router)
app.include_router(learning_router)