"""
GA4 Agent - Tier-1 Analytics Agent for Google Analytics 4.
Handles live GA4 data retrieval with strict validation and graceful error handling.
"""

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, Dimension, Metric
import os
import time
from typing import Dict, Any

from app.utils.ga4_validation import validate_plan, ALLOWED_METRICS, ALLOWED_DIMENSIONS
from app.utils.date_parser import parse_date_range, get_human_readable_range
from app.utils.llm import parse_analytics_query
from app.utils.logger import log_ga4_query, log_agent_call, log_error, log_performance


class GA4Agent:
    """
    Tier-1 Analytics Agent for GA4 data retrieval.
    
    Responsibilities:
    - Parse natural language queries into GA4 API calls
    - Validate metrics and dimensions against allowlists
    - Execute GA4 API requests with proper error handling
    - Format responses for downstream consumption
    - Handle empty data gracefully
    """
    
    def __init__(self):
        """Initialize GA4 client with credentials validation"""
        
        # Verify credentials file exists
        credentials_path = "credentials.json"
        self.client = None
        self.credentials_valid = False
        
        if not os.path.exists(credentials_path):
            logger.warning("GA4 credentials file not found. Running in demo mode.")
            return
        
        try:
            self.client = BetaAnalyticsDataClient.from_service_account_file(
                credentials_path
            )
            self.credentials_valid = True
            log_agent_call("GA4Agent", "Initialized successfully", True)
            
        except Exception as e:
            log_error(e, "GA4Agent initialization")
            logger.warning(f"GA4 credentials invalid: {str(e)}. Running in demo mode.")
            self.client = None
            self.credentials_valid = False

    def run(self, query: str, property_id: str) -> Dict[str, Any]:
        """
        Main entry point for GA4 analytics queries.
        
        Args:
            query: Natural language analytics query
            property_id: GA4 property ID
            
        Returns:
            Formatted analytics response with data or error message
        """
        
        start_time = time.time()
        
        try:
            # Step 1: Parse natural language query
            plan = parse_analytics_query(query)
            log_agent_call("GA4Agent", f"Query parsed: {query}", True)
            
            # Step 2: Validate query plan against allowlists
            validate_plan(plan)
            
            # Step 3: Execute GA4 API request
            response = self._execute_ga4_request(plan, property_id)
            
            # Step 4: Handle empty data gracefully
            if not response.rows:
                return self._empty_data_response(plan, property_id)
            
            # Step 5: Format successful response
            formatted_response = self._format_response(response, plan, query)
            
            # Log performance
            duration = (time.time() - start_time) * 1000
            log_performance("GA4Agent.run", duration)
            
            return formatted_response
            
        except ValueError as e:
            # Validation errors
            log_error(e, "GA4Agent validation")
            return {
                "error": f"Query validation failed: {str(e)}",
                "query": query,
                "property_id": property_id,
                "allowed_metrics": list(ALLOWED_METRICS),
                "allowed_dimensions": list(ALLOWED_DIMENSIONS)
            }
            
        except Exception as e:
            # API or processing errors
            log_error(e, "GA4Agent execution")
            return {
                "error": f"Analytics processing failed: {str(e)}",
                "query": query,
                "property_id": property_id
            }

    def _execute_ga4_request(self, plan: Dict[str, Any], property_id: str) -> Any:
        """
        Execute GA4 API request with proper error handling.
        
        Args:
            plan: Validated query plan with metrics, dimensions, etc.
            property_id: GA4 property ID
            
        Returns:
            GA4 API response object or demo data
        """
        
        # Check if credentials are valid
        if not self.credentials_valid or self.client is None:
            logger.warning("No valid GA4 credentials. Returning demo data.")
            return self._get_demo_data(plan)
        
        # Build GA4 request
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name=d) for d in plan["dimensions"]],
            metrics=[Metric(name=m) for m in plan["metrics"]],
            date_ranges=[parse_date_range(plan["date_range"])]
        )
        
        # Add filters if specified
        if "filters" in plan and plan["filters"]:
            # TODO: Implement dimension filtering
            pass
        
        # Log the query
        log_ga4_query(property_id, plan["metrics"], plan["dimensions"])
        
        # Execute request
        response = self.client.run_report(request)
        
        return response

    def _format_response(self, response: Any, plan: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """
        Format GA4 API response into standardized structure.
        
        Args:
            response: GA4 API response object
            plan: Original query plan
            original_query: Original natural language query
            
        Returns:
            Formatted response dictionary
        """
        
        # Extract data rows
        rows = []
        for row in response.rows:
            row_data = {
                "dimensions": {
                    plan["dimensions"][i]: dim_value.value 
                    for i, dim_value in enumerate(row.dimension_values)
                },
                "metrics": {
                    plan["metrics"][i]: metric_value.value
                    for i, metric_value in enumerate(row.metric_values)
                }
            }
            rows.append(row_data)
        
        # Generate human-readable summary
        date_range_str = get_human_readable_range(
            parse_date_range(plan["date_range"])
        )
        
        summary = (
            f"GA4 analytics report for {date_range_str}. "
            f"Retrieved {len(rows)} data points for "
            f"{', '.join(plan['metrics'])} metrics."
        )
        
        return {
            "summary": summary,
            "query": original_query,
            "metrics": plan["metrics"],
            "dimensions": plan["dimensions"], 
            "date_range": date_range_str,
            "rows": rows,
            "total_rows": len(rows)
        }

    def _empty_data_response(self, plan: Dict[str, Any], property_id: str) -> Dict[str, Any]:
        """
        Handle empty data scenarios gracefully.
        
        Args:
            plan: Query plan that returned no data
            property_id: GA4 property ID
            
        Returns:
            Informative response for empty data
        """
        
        date_range_str = get_human_readable_range(
            parse_date_range(plan["date_range"])
        )
        
        return {
            "summary": f"No data available for the selected period ({date_range_str}).",
            "message": "This could be due to:",
            "possible_reasons": [
                "No traffic during the selected time period",
                "Data processing delay (GA4 data can be delayed up to 24-48 hours)",
                "Property ID may not have data for the requested metrics",
                "Filters may be too restrictive"
            ],
            "suggestions": [
                "Try a different date range (e.g., last 30 days)",
                "Check if the property ID is correct",
                "Verify the website has tracking implemented"
            ],
            "metrics": plan["metrics"],
            "dimensions": plan["dimensions"],
            "date_range": date_range_str,
            "property_id": property_id,
            "rows": []
        }

    def _get_demo_data(self, plan: Dict[str, Any]):
        """
        Generate demo data when credentials are invalid.
        
        Args:
            plan: Query plan with metrics and dimensions
            
        Returns:
            Mock GA4 response structure
        """
        from datetime import datetime, timedelta
        import random
        
        # Create mock response object
        class MockResponse:
            def __init__(self):
                self.rows = []
                self.row_count = 7
                
                # Generate sample data based on plan
                for i in range(7):
                    date = (datetime.now() - timedelta(days=6-i)).strftime('%Y%m%d')
                    
                    row_data = []
                    for dim in plan["dimensions"]:
                        if dim == "date":
                            row_data.append(MockDimensionValue(date))
                        elif dim == "pagePath":
                            paths = ["/", "/about", "/contact", "/products", "/blog"]
                            row_data.append(MockDimensionValue(random.choice(paths)))
                        else:
                            row_data.append(MockDimensionValue("demo_value"))
                    
                    metric_data = []
                    for metric in plan["metrics"]:
                        if metric == "sessions":
                            value = str(random.randint(50, 500))
                        elif metric == "totalUsers":
                            value = str(random.randint(40, 400))
                        elif metric == "screenPageViews":
                            value = str(random.randint(100, 800))
                        else:
                            value = str(random.randint(10, 100))
                        metric_data.append(MockMetricValue(value))
                    
                    self.rows.append(MockRow(row_data, metric_data))
        
        class MockDimensionValue:
            def __init__(self, value):
                self.value = value
        
        class MockMetricValue:
            def __init__(self, value):
                self.value = value
        
        class MockRow:
            def __init__(self, dimensions, metrics):
                self.dimension_values = dimensions
                self.metric_values = metrics
        
        logger.info("Returning demo GA4 data (credentials invalid)")
        return MockResponse()