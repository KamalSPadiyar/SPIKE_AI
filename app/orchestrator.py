from app.agents.ga4_agent import GA4Agent
from app.agents.seo_agent import SEOAgent
import logging

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Brain of the system - handles intent detection and routing.
    Does NOT perform actual data processing, only coordination.
    """
    
    def __init__(self):
        self.ga4_agent = GA4Agent()
        self.seo_agent = SEOAgent()

    def handle(self, req):
        """
        Main handler that detects intent and routes to appropriate agents.
        
        Args:
            req: QueryRequest with query string and optional propertyId
            
        Returns:
            Response from agent(s) or error message
        """
        query = req.query.lower()
        
        # Intent detection based on keywords
        needs_ga4 = self._detect_ga4_intent(query)
        needs_seo = self._detect_seo_intent(query)
        
        logger.info(f"Query intent - GA4: {needs_ga4}, SEO: {needs_seo}")
        
        responses = {}
        
        # Route to GA4 agent
        if needs_ga4:
            if not req.propertyId:
                return {
                    "error": "propertyId is required for GA4 analytics queries",
                    "query": req.query
                }
            
            try:
                responses["analytics"] = self.ga4_agent.run(
                    query=req.query,
                    property_id=req.propertyId
                )
            except Exception as e:
                logger.error(f"GA4 agent error: {str(e)}")
                responses["analytics"] = {
                    "error": f"Analytics processing failed: {str(e)}"
                }
        
        # Route to SEO agent
        if needs_seo:
            try:
                responses["seo"] = self.seo_agent.run(query=req.query)
            except Exception as e:
                logger.error(f"SEO agent error: {str(e)}")
                responses["seo"] = {
                    "error": f"SEO processing failed: {str(e)}"
                }
        
        # Handle no intent detected
        if not responses:
            return {
                "error": "Could not determine query intent. Please specify analytics or SEO related questions.",
                "query": req.query,
                "supported_intents": [
                    "Analytics: page views, users, sessions, traffic",
                    "SEO: titles, meta tags, indexing, HTTPS status"
                ]
            }
        
        # Tier-3 fusion for combined queries
        if len(responses) > 1:
            return self._merge_responses(responses, req.query)
        
        return list(responses.values())[0]

    def _detect_ga4_intent(self, query: str) -> bool:
        """Detect if query requires GA4 analytics data"""
        ga4_keywords = [
            "page view", "pageview", "users", "sessions", "traffic", "views",
            "bounce rate", "conversion", "goal", "event", "audience",
            "acquisition", "behavior", "demographic", "geographic",
            "device", "browser", "source", "medium", "campaign"
        ]
        
        return any(keyword in query for keyword in ga4_keywords)

    def _detect_seo_intent(self, query: str) -> bool:
        """Detect if query requires SEO analysis"""
        seo_keywords = [
            "title", "meta", "index", "https", "seo", "crawl",
            "heading", "alt text", "schema", "sitemap", "robot",
            "canonical", "redirect", "broken link", "duplicate",
            "page speed", "mobile friendly", "structured data"
        ]
        
        return any(keyword in query for keyword in seo_keywords)

    def _merge_responses(self, responses: dict, query: str) -> dict:
        """
        Combine multiple agent responses into unified insights.
        Tier-3 fusion logic for cross-domain analysis.
        """
        return {
            "query": query,
            "summary": "Combined analytics and SEO insights",
            "insights": self._generate_combined_insights(responses),
            "data": responses
        }

    def _generate_combined_insights(self, responses: dict) -> list:
        """Generate cross-domain insights from multiple agent responses"""
        insights = []
        
        # Extract key metrics for correlation analysis
        if "analytics" in responses and "seo" in responses:
            insights.append("Cross-referencing traffic data with SEO health indicators")
            
            # Add specific correlation insights based on available data
            if "error" not in responses["analytics"] and "error" not in responses["seo"]:
                insights.append("Both analytics and SEO data available for comprehensive analysis")
        
        return insights