from fastapi import FastAPI
from app.orchestrator import Orchestrator
from app.schemas.request import QueryRequest

app = FastAPI(
    title="SPIKE AI Backend",
    description="Production-ready backend for AI-powered analytics and SEO insights",
    version="1.0.0"
)

orchestrator = Orchestrator()


@app.post("/query")
def query_handler(req: QueryRequest):
    """
    Handle natural language queries for analytics and SEO insights.
    
    Args:
        req: QueryRequest containing the query string and optional propertyId
        
    Returns:
        Response from the appropriate agent(s) based on query intent
    """
    return orchestrator.handle(req)


@app.get("/health")
def health_check():
    """Health check endpoint for deployment verification"""
    return {"status": "healthy", "service": "spike-ai-backend"}


@app.get("/")
def root():
    """Root endpoint with service information"""
    return {
        "service": "SPIKE AI Backend",
        "version": "1.0.0",
        "endpoints": {
            "query": "POST /query - Main query handler",
            "health": "GET /health - Health check"
        }
    }