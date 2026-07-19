from fastapi import FastAPI 
from src.api.routes import users, auth, servers

app = FastAPI(
    title = "Discord Clone API",
    description = "Backend for a real-time communication platform.",
    version = "0.1.0"
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(servers.router)

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "api_gateway"
    }

