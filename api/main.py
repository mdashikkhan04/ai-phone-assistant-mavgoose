from fastapi import FastAPI
from api.webhooks.inbound_call import router as voice_router
from api.webhooks.gather import router as gather_router
from api.routes import router as extra_router

app = FastAPI(title="AI Voice Agent Backend")

# Register Routers
app.include_router(voice_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(gather_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(extra_router, tags=["general"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
