# SPIKE AI Backend - Copilot Instructions

This workspace contains a production-ready SPIKE AI backend with FastAPI, GA4 analytics integration, and SEO analysis capabilities.

## Project Structure
- `/app/` - Main application code
- `/app/agents/` - GA4 and SEO agents
- `/app/schemas/` - Request/response models
- `/app/utils/` - Utility functions and validation
- `credentials.json` - GA4 service account credentials (replaced by evaluators)

## Key Components
- **Orchestrator**: Intent detection and routing
- **GA4 Agent**: Analytics data retrieval with strict validation
- **SEO Agent**: SEO analysis from CSV data
- **LLM Integration**: Natural language query parsing

## Development Guidelines
- Follow the allowlist validation for GA4 metrics/dimensions
- Handle empty data gracefully
- Keep agents focused on specific tasks
- Use the orchestrator for routing logic only