from fastapi import FastAPI

app = FastAPI(
    title="Narrate IQ",
    description="KPI Intelligence-to-Action Engine",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "narrate-iq",
        "version": "0.1.0",
    }