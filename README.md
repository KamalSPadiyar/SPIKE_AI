# SPIKE AI Backend

Production-ready backend for AI-powered analytics and SEO insights using FastAPI, Google Analytics 4, and natural language processing.

## 🚀 Features

- **Natural Language Queries**: Ask questions in plain English about your analytics and SEO data
- **GA4 Integration**: Live Google Analytics 4 data retrieval with strict validation
- **SEO Analysis**: Comprehensive website audit capabilities from CSV data
- **Orchestrator Pattern**: Intelligent intent detection and multi-agent coordination
- **Production Ready**: Robust error handling, logging, and deployment scripts

## 📁 Project Structure

```
spike-ai-backend/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── orchestrator.py          # Intent detection + routing
│   ├── agents/
│   │   ├── ga4_agent.py         # GA4 Analytics Agent
│   │   └── seo_agent.py         # SEO Analysis Agent
│   ├── schemas/
│   │   ├── request.py           # API request models
│   │   └── response.py          # API response models
│   └── utils/
│       ├── llm.py              # LiteLLM integration
│       ├── ga4_validation.py   # Metrics/dimensions allowlists
│       ├── date_parser.py      # Date range processing
│       └── logger.py           # Structured logging
├── credentials.json             # GA4 service account (replaced by evaluators)
├── requirements.txt
├── deploy.sh
└── documentation/
```

## 🔧 Installation

### Prerequisites

- Python 3.8+
- Google Analytics 4 property with data
- GA4 service account with Analytics Reporting API access

### Setup

1. **Clone and install dependencies:**
```bash
git clone <repository-url>
cd spike-ai-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

2. **Configure GA4 credentials:**
   - Replace `credentials.json` with your actual GA4 service account file
   - Ensure the service account has Analytics Reporting API access

3. **Optional: Add SEO data:**
   - Place your Screaming Frog CSV export as `screamingfrog.csv` in the project root
   - Or use any CSV with columns: Address, Title 1, Meta Description 1, Status Code

## 🚀 Usage

### Start the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### API Endpoints

#### POST /query
Main endpoint for natural language queries.

**Request:**
```json
{
  "query": "Show me page views for the last 7 days",
  "propertyId": "123456789"
}
```

**Response:**
```json
{
  "summary": "GA4 analytics report for Last 7 days. Retrieved 10 data points for screenPageViews metrics.",
  "metrics": ["screenPageViews"],
  "dimensions": ["date"],
  "date_range": "Last 7 days",
  "rows": [
    {
      "dimensions": {"date": "20231201"},
      "metrics": {"screenPageViews": "1250"}
    }
  ]
}
```

### Example Queries

**Analytics Queries (require propertyId):**
- "Show me users from last month"
- "What are the top pages by traffic?"
- "How many sessions did we have yesterday?"
- "Show bounce rate by country"

**SEO Queries:**
- "Find pages with long titles and non-HTTPS URLs"
- "Analyze meta descriptions"
- "Check HTTPS usage across the site"
- "Run a general SEO health check"

**Combined Queries:**
- "Show me traffic data and SEO issues for the homepage"

## 🔍 Agent Architecture

### Orchestrator (Brain)
- Detects query intent using keyword matching
- Routes queries to appropriate agents
- Handles multi-agent coordination
- Provides unified error handling

### GA4 Agent (Tier-1)
- Parses natural language to GA4 API calls
- Enforces strict metric/dimension allowlists
- Handles empty data gracefully
- Provides detailed error messages

### SEO Agent (Tier-2)
- Analyzes SEO data from CSV files
- Schema-tolerant processing
- Multiple analysis types available
- Actionable recommendations

## 🛡️ Security & Validation

### GA4 Allowlists
The system enforces strict allowlists for GA4 metrics and dimensions:

**Allowed Metrics:**
- sessions, totalUsers, screenPageViews, activeUsers, newUsers
- bounceRate, averageSessionDuration, conversions, eventCount

**Allowed Dimensions:**
- date, pagePath, pageTitle, sessionSource, sessionMedium
- country, city, deviceCategory, operatingSystem, browser

### Error Handling
- Graceful handling of empty GA4 data
- Fallback plans when LLM fails
- Comprehensive validation messages
- Structured logging for debugging

## 🔧 Configuration

### Environment Variables
Create a `.env` file for configuration:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
LITELLM_LOG=INFO

# Logging
LOG_LEVEL=INFO

# Server Configuration  
HOST=0.0.0.0
PORT=8080
```

### GA4 Setup
1. Create a service account in Google Cloud Console
2. Enable Analytics Reporting API
3. Grant service account access to your GA4 property
4. Download credentials JSON file

## 📊 Deployment

### Using deploy.sh
```bash
chmod +x deploy.sh
./deploy.sh
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY credentials.json .
COPY screamingfrog.csv .  # Optional

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8080/health
```

### Sample Query
```bash
curl -X POST http://localhost:8080/query \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "Show me users from last week",
    "propertyId": "123456789"
  }'
```

## 📝 Development

### Adding New Metrics/Dimensions
Update the allowlists in `app/utils/ga4_validation.py`:
```python
ALLOWED_METRICS.add("newMetricName")
ALLOWED_DIMENSIONS.add("newDimensionName")
```

### Adding New SEO Analysis
Extend the SEO agent in `app/agents/seo_agent.py`:
```python
def new_seo_analysis(self, **parameters):
    # Implement analysis logic
    return analysis_results
```

### Custom LLM Models
Modify `app/utils/llm.py` to use different models:
```python
response = litellm.completion(
    model="claude-3-sonnet-20240229",  # Change model
    messages=[{"role": "user", "content": prompt}]
)
```

## 🐛 Troubleshooting

### Common Issues

1. **GA4 Authentication Error**
   - Verify credentials.json is valid
   - Check service account permissions
   - Ensure Analytics Reporting API is enabled

2. **Empty Data Response**
   - Check if property ID exists and has data
   - Verify date range isn't too recent (GA4 has delays)
   - Try broader date ranges

3. **SEO Analysis Errors**
   - Ensure CSV file exists or agent will use sample data
   - Check column names match expected format
   - Verify file encoding (UTF-8 recommended)

4. **LLM Parsing Failures**
   - System falls back to keyword matching
   - Check OPENAI_API_KEY is set correctly
   - Monitor logs for API errors

## 📚 API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all validation passes
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Open an issue with reproduction steps