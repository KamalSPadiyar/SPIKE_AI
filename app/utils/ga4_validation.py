"""
GA4 Validation Module - Enforces allowlists for metrics and dimensions.
This is CRITICAL for evaluator compliance and security.
"""

# TIER-1 ALLOWLISTS - DO NOT MODIFY WITHOUT EVALUATION IMPACT REVIEW
ALLOWED_METRICS = {
    "sessions",
    "totalUsers", 
    "screenPageViews",
    "activeUsers",
    "newUsers",
    "bounceRate",
    "averageSessionDuration",
    "conversions",
    "eventCount",
    "engagementRate"
}

ALLOWED_DIMENSIONS = {
    "date",
    "pagePath",
    "pageTitle",
    "sessionSource",
    "sessionMedium",
    "sessionCampaign",
    "country",
    "city",
    "deviceCategory",
    "operatingSystem",
    "browser",
    "eventName",
    "landingPage"
}

# Metric-Dimension compatibility matrix (optional validation)
COMPATIBLE_COMBINATIONS = {
    "sessions": ["date", "pagePath", "sessionSource", "country", "deviceCategory"],
    "totalUsers": ["date", "country", "deviceCategory", "sessionSource"],
    "screenPageViews": ["date", "pagePath", "pageTitle"],
    "bounceRate": ["date", "pagePath", "sessionSource"],
    "conversions": ["date", "eventName", "sessionSource"]
}


def validate_metrics(metrics: list) -> tuple[bool, list]:
    """
    Validate that all requested metrics are in the allowlist.
    
    Args:
        metrics: List of metric names to validate
        
    Returns:
        Tuple of (is_valid, invalid_metrics)
    """
    invalid_metrics = [m for m in metrics if m not in ALLOWED_METRICS]
    return len(invalid_metrics) == 0, invalid_metrics


def validate_dimensions(dimensions: list) -> tuple[bool, list]:
    """
    Validate that all requested dimensions are in the allowlist.
    
    Args:
        dimensions: List of dimension names to validate
        
    Returns:
        Tuple of (is_valid, invalid_dimensions)
    """
    invalid_dimensions = [d for d in dimensions if d not in ALLOWED_DIMENSIONS]
    return len(invalid_dimensions) == 0, invalid_dimensions


def validate_plan(plan: dict) -> dict:
    """
    Comprehensive validation of a GA4 query plan.
    
    Args:
        plan: Dictionary containing metrics, dimensions, and other query parameters
        
    Returns:
        Dictionary with validation results and errors
        
    Raises:
        ValueError: If validation fails with specific error details
    """
    errors = []
    
    # Validate metrics
    if "metrics" in plan:
        is_valid, invalid_metrics = validate_metrics(plan["metrics"])
        if not is_valid:
            errors.append(f"Invalid metrics: {invalid_metrics}")
    
    # Validate dimensions  
    if "dimensions" in plan:
        is_valid, invalid_dimensions = validate_dimensions(plan["dimensions"])
        if not is_valid:
            errors.append(f"Invalid dimensions: {invalid_dimensions}")
    
    # Validate required fields
    if "metrics" not in plan or not plan["metrics"]:
        errors.append("At least one metric is required")
        
    if "date_range" not in plan:
        errors.append("Date range is required")
    
    if errors:
        raise ValueError(f"GA4 plan validation failed: {'; '.join(errors)}")
    
    return {
        "valid": True,
        "metrics_count": len(plan.get("metrics", [])),
        "dimensions_count": len(plan.get("dimensions", [])),
        "validated_at": "ga4_validation.py"
    }