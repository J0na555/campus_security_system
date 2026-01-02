"""
Campus Security System - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_db_and_tables, init_db
from routers import auth, scan, violations, visitors, vehicles_public, vehicles_dashboard
from websocket_alerts import alert_broadcaster

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Campus Security System API...")
    create_db_and_tables()
    init_db()  # Initialize with sample data
    yield
    # Shutdown
    print("Shutting down Campus Security System API...")


# Create FastAPI application
app = FastAPI(
    title="Campus Security System API",
    description="Backend API for campus gate security management with QR scanning and face verification",
    version="1.1.0",
    lifespan=lifespan
)

# CORS middleware configuration
# In production, replace "*" with specific frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(scan.router, prefix="/api/v1")
app.include_router(violations.router, prefix="/api/v1")
app.include_router(visitors.router, prefix="/api/v1")
app.include_router(vehicles_public.router, prefix="/api/v1")
app.include_router(vehicles_dashboard.router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Campus Security System API",
        "version": "1.1.0",
        "status": "operational",
        "endpoints": {
            "authentication": "/api/v1/auth",
            "scanning": "/api/v1/scan",
            "violations": "/api/v1/violations",
            "visitors": "/api/v1/visitors",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2026-01-02T00:00:00Z"
    }


# API info endpoint
@app.get("/api/v1")
async def api_info():
    """API version information"""
    return {
        "version": "1.1.0",
        "baseUrl": "/api/v1",
        "authentication": "JWT Bearer Token",
        "documentation": "/docs"
    }


# WebSocket endpoint for real-time alerts
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for real-time violation and vehicle alerts
    
    Public endpoint - no authentication required (for hackathon/demo simplicity)
    Broadcasts all new violations and vehicle alerts in real-time
    
    Message format:
    - violation_alert: New security violation detected
    - vehicle_alert: Unknown/mismatched vehicle detected
    - heartbeat: Keep-alive message
    
    Clients should respond to heartbeat with {"type": "pong"}
    """
    await alert_broadcaster.connect(websocket)
    try:
        while True:
            # Receive messages from client (e.g., pong responses)
            data = await websocket.receive_text()
            # Could process client messages here if needed
    except WebSocketDisconnect:
        alert_broadcaster.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
