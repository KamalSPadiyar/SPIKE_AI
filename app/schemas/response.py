from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union


class AnalyticsResponse(BaseModel):
    """Response schema for GA4 analytics data"""
    
    summary: str = Field(..., description="Human-readable summary of the data")
    metrics: List[str] = Field(..., description="GA4 metrics included in the report")
    dimensions: List[str] = Field(..., description="GA4 dimensions included in the report")
    rows: List[Dict[str, Any]] = Field(..., description="Raw data rows from GA4")
    date_range: Optional[str] = Field(None, description="Date range of the data")


class SEOResponse(BaseModel):
    """Response schema for SEO analysis data"""
    
    summary: str = Field(..., description="Human-readable summary of SEO findings")
    analysis_type: str = Field(..., description="Type of SEO analysis performed")
    findings: List[Dict[str, Any]] = Field(..., description="SEO findings and recommendations")
    count: Optional[int] = Field(None, description="Count of items analyzed or found")


class ErrorResponse(BaseModel):
    """Response schema for error cases"""
    
    error: str = Field(..., description="Error message")
    query: Optional[str] = Field(None, description="Original query that caused the error")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class CombinedResponse(BaseModel):
    """Response schema for queries requiring multiple agents"""
    
    query: str = Field(..., description="Original query")
    summary: str = Field(..., description="Combined analysis summary")
    insights: List[str] = Field(..., description="Cross-domain insights")
    data: Dict[str, Union[AnalyticsResponse, SEOResponse]] = Field(
        ..., 
        description="Individual responses from each agent"
    )


# Union type for all possible response types
QueryResponse = Union[
    AnalyticsResponse, 
    SEOResponse, 
    CombinedResponse, 
    ErrorResponse,
    Dict[str, Any]  # Fallback for custom responses
]