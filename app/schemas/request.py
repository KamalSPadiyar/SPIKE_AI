from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    """
    Request schema for the main query endpoint.
    
    Attributes:
        query: Natural language query string
        propertyId: GA4 property ID (required for analytics queries)
    """
    
    query: str = Field(
        ..., 
        description="Natural language query for analytics or SEO insights",
        example="Show me page views for the last 7 days"
    )
    
    propertyId: Optional[str] = Field(
        None,
        description="GA4 property ID (required for analytics queries)",
        example="123456789"
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "What are the top pages by traffic last week?",
                "propertyId": "123456789"
            }
        }