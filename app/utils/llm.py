"""
LLM Module - LiteLLM wrapper for natural language query parsing.
Handles query-to-GA4-plan conversion with structured output.
"""

import litellm
import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Configure LiteLLM API key
litellm.api_key = "sk-yX_dfo0dxuvO3UtqNRMd5A"
# litellm.set_verbose = True  # Uncomment for debugging


def parse_analytics_query(query: str) -> Dict[str, Any]:
    """
    Convert natural language query to structured GA4 query plan.
    
    Args:
        query: Natural language analytics query
        
    Returns:
        Dictionary with metrics, dimensions, date_range, and optional filters
        
    Raises:
        Exception: If LLM call fails or returns invalid JSON
    """
    
    prompt = f"""You are a GA4 analytics query planner. Convert the natural language query into a structured plan.

Return STRICT JSON only with these fields:
- "metrics": Array of GA4 metric names (e.g., ["sessions", "totalUsers"])
- "dimensions": Array of GA4 dimension names (e.g., ["date", "pagePath"])  
- "date_range": String like "last_7_days", "last_30_days", etc.
- "filters": Optional object with dimension filters (e.g., {{"pagePath": "/contact"}})

Use these GA4 API names for metrics:
- sessions, totalUsers, screenPageViews, activeUsers, newUsers, bounceRate

Use these GA4 API names for dimensions:  
- date, pagePath, pageTitle, sessionSource, sessionMedium, country, deviceCategory

Query: {query}

Example output:
{{"metrics": ["sessions", "screenPageViews"], "dimensions": ["date", "pagePath"], "date_range": "last_7_days"}}
"""

    try:
        response = litellm.completion(
            model="gpt-4o-mini",  # Use cost-effective model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for consistent structured output
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        logger.info(f"LLM response: {content}")
        
        # Parse JSON response
        plan = json.loads(content)
        
        # Validate required fields
        if "metrics" not in plan:
            plan["metrics"] = ["sessions"]  # Default fallback
        if "dimensions" not in plan:
            plan["dimensions"] = ["date"]  # Default fallback  
        if "date_range" not in plan:
            plan["date_range"] = "last_7_days"  # Default fallback
            
        return plan
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        return _fallback_plan(query)
        
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return _fallback_plan(query)


def _fallback_plan(query: str) -> Dict[str, Any]:
    """
    Generate a fallback query plan when LLM fails.
    Uses keyword matching for basic intent detection.
    
    Args:
        query: Original query string
        
    Returns:
        Basic GA4 query plan
    """
    logger.warning(f"Using fallback plan for query: {query}")
    
    query_lower = query.lower()
    
    # Default plan
    plan = {
        "metrics": ["sessions"],
        "dimensions": ["date"],
        "date_range": "last_7_days"
    }
    
    # Keyword-based metric detection
    if any(word in query_lower for word in ["user", "visitor", "audience"]):
        plan["metrics"] = ["totalUsers", "activeUsers"]
    
    if any(word in query_lower for word in ["page view", "pageview", "views"]):
        plan["metrics"] = ["screenPageViews"]
        
    if any(word in query_lower for word in ["bounce", "engagement"]):
        plan["metrics"] = ["bounceRate"]
    
    # Keyword-based dimension detection
    if any(word in query_lower for word in ["page", "url", "path"]):
        if "date" not in plan["dimensions"]:
            plan["dimensions"].append("pagePath")
        else:
            plan["dimensions"] = ["date", "pagePath"]
            
    if any(word in query_lower for word in ["country", "location", "geo"]):
        plan["dimensions"].append("country")
        
    if any(word in query_lower for word in ["device", "mobile", "desktop"]):
        plan["dimensions"].append("deviceCategory")
    
    # Date range detection
    if any(word in query_lower for word in ["yesterday"]):
        plan["date_range"] = "yesterday"
    elif any(word in query_lower for word in ["month", "30 days"]):
        plan["date_range"] = "last_30_days"
    elif any(word in query_lower for word in ["week", "14 days"]):
        plan["date_range"] = "last_14_days"
        
    return plan


def parse_seo_query(query: str) -> Dict[str, Any]:
    """
    Parse natural language SEO queries into structured analysis plan.
    
    Args:
        query: Natural language SEO query
        
    Returns:
        Dictionary with analysis_type and parameters
    """
    
    query_lower = query.lower()
    
    # SEO analysis type detection
    if "title" in query_lower and "https" in query_lower:
        return {
            "analysis_type": "non_https_long_titles",
            "parameters": {"title_length_threshold": 60}
        }
    
    if "title" in query_lower:
        return {
            "analysis_type": "title_analysis", 
            "parameters": {"length_threshold": 60}
        }
        
    if "meta" in query_lower:
        return {
            "analysis_type": "meta_description_analysis",
            "parameters": {"length_threshold": 160}
        }
        
    if "https" in query_lower:
        return {
            "analysis_type": "https_analysis",
            "parameters": {}
        }
    
    # Default analysis
    return {
        "analysis_type": "general_seo_health",
        "parameters": {}
    }