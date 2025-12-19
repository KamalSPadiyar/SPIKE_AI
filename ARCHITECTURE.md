# SPIKE AI Backend Architecture

## System Overview

SPIKE AI Backend is a production-ready system that provides natural language access to analytics and SEO data through a microservices architecture pattern.

## Architecture Patterns

### 1. Orchestrator Pattern (Brain)
The orchestrator acts as the central coordinator that:
- Receives natural language queries
- Detects intent through keyword analysis
- Routes requests to appropriate specialized agents
- Handles multi-agent coordination for complex queries
- Provides unified error handling and response formatting

### 2. Agent-Based Architecture
Specialized agents handle specific domains:

#### GA4 Agent (Tier-1 Analytics)
- **Purpose**: Live Google Analytics 4 data retrieval
- **Validation**: Enforces strict allowlists for security
- **Error Handling**: Graceful empty data responses
- **API Integration**: Direct GA4 Reporting API calls

#### SEO Agent (Tier-2 Analysis)  
- **Purpose**: Website audit and SEO health analysis
- **Data Source**: CSV files (Screaming Frog, custom exports)
- **Schema Tolerance**: Handles varying CSV structures
- **Analysis Types**: Multiple SEO health checks available

### 3. Three-Tier Processing Model

```
┌─────────────────────────────────────────────────────────────┐
│                        Tier-3: Fusion                      │
│                    (Orchestrator)                          │
│  • Intent Detection   • Multi-agent Coordination          │
│  • Response Merging   • Error Aggregation                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼────────┐         ┌───────▼────────┐
│   Tier-1: GA4  │         │  Tier-2: SEO   │
│   (Real-time)  │         │  (Batch)       │
│                │         │                │
│ • Live API     │         │ • CSV Analysis │
│ • Validation   │         │ • Health Checks│ 
│ • Allowlists   │         │ • Recommendations│
└────────────────┘         └────────────────┘
```

## Data Flow

### 1. Request Processing
```
User Query → FastAPI → Orchestrator → Intent Detection → Agent Routing
```

### 2. Agent Execution  
```
Agent → LLM Parsing → Validation → Data Processing → Response Formation
```

### 3. Response Assembly
```
Agent Results → Orchestrator → Response Merging → Client Response
```

## Component Interactions

### Natural Language Processing Flow

1. **Query Reception**: FastAPI receives structured request
2. **Intent Analysis**: Orchestrator analyzes query keywords
3. **LLM Parsing**: Selected agents use LiteLLM for query structure
4. **Validation Layer**: Strict allowlists prevent unauthorized access
5. **Data Retrieval**: Agents execute domain-specific data operations
6. **Response Formatting**: Standardized response schemas
7. **Error Handling**: Graceful degradation with informative messages

### Security Model

#### GA4 Security (Tier-1)
- **Allowlist Enforcement**: Only approved metrics/dimensions
- **Credentials Management**: Service account isolation
- **API Validation**: Input sanitization and bounds checking
- **Error Sanitization**: No sensitive data in error messages

#### SEO Security (Tier-2)
- **File System Isolation**: CSV processing in sandboxed environment
- **Schema Validation**: Safe DataFrame operations
- **Resource Limits**: Bounded processing to prevent DoS

## Scalability Considerations

### Horizontal Scaling
- **Stateless Design**: All agents are stateless for easy scaling
- **Agent Isolation**: Independent agent scaling based on demand
- **Database Independence**: No shared state between requests

### Performance Optimizations
- **LLM Caching**: Repeated query pattern caching
- **Response Streaming**: Large result set streaming
- **Async Processing**: FastAPI async support for I/O operations
- **Connection Pooling**: GA4 client connection reuse

## Error Handling Strategy

### Layered Error Handling
1. **Validation Layer**: Pre-execution validation with detailed messages
2. **Agent Layer**: Domain-specific error handling with fallbacks  
3. **Orchestrator Layer**: Error aggregation and user-friendly formatting
4. **API Layer**: HTTP status code mapping and response standardization

### Graceful Degradation
- **Empty Data**: Informative responses with troubleshooting guidance
- **LLM Failures**: Keyword-based fallback query parsing
- **API Failures**: Cached responses or alternative data sources
- **Partial Failures**: Successful agent results still returned

## Monitoring and Observability

### Logging Strategy
- **Structured Logging**: JSON format for automated processing  
- **Performance Metrics**: Request duration and throughput tracking
- **Error Tracking**: Detailed error context and stack traces
- **Audit Logging**: All GA4 queries logged for compliance

### Health Monitoring
- **Health Endpoints**: Service and dependency health checks
- **Metrics Collection**: Custom metrics for business logic
- **Alert Integration**: Automated alerting for critical failures

## Deployment Architecture

### Production Deployment
```
Load Balancer → FastAPI Instances → Agent Pool → Data Sources
                     │
                     ├── GA4 API
                     └── CSV Storage
```

### Container Strategy  
- **Base Container**: Python runtime with dependencies
- **Config Management**: Environment-based configuration
- **Secret Management**: External secret store integration
- **Resource Limits**: CPU and memory constraints

## Extension Points

### Adding New Agents
1. Implement agent interface in `app/agents/`
2. Register with orchestrator intent detection
3. Add request/response schemas
4. Update documentation and tests

### Custom Analysis Types
1. Extend existing agents with new methods
2. Add LLM parsing support for new query types
3. Update validation rules as needed
4. Document new capabilities

### Integration Endpoints
1. Add new data source connectors
2. Implement agent interface
3. Configure security and validation
4. Test end-to-end workflows

## Security Architecture

### Authentication & Authorization
- **Service Account**: GA4 access via service account credentials
- **API Security**: Request validation and rate limiting
- **Data Access**: Principle of least privilege

### Data Protection
- **Encryption**: TLS for all external communications
- **Credential Management**: Secure credential storage
- **Audit Trails**: Comprehensive request logging
- **Data Minimization**: Only necessary data processed

## Quality Assurance

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing  
- **Load Testing**: Performance under scale
- **Security Testing**: Vulnerability assessment

### Code Quality
- **Type Hints**: Full type annotation
- **Documentation**: Comprehensive inline documentation
- **Linting**: Automated code quality checks
- **Dependency Management**: Pinned dependency versions