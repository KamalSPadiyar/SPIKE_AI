"""
SEO Agent - Tier-2 SEO Analysis Agent.
Handles SEO data analysis from CSV files with flexible schema tolerance.
"""

import pandas as pd
import os
import time
from typing import Dict, Any, List
from urllib.parse import urlparse

from app.utils.llm import parse_seo_query
from app.utils.logger import log_agent_call, log_error, log_performance


class SEOAgent:
    """
    Tier-2 SEO Analysis Agent for website audit data processing.
    
    Responsibilities:
    - Load and analyze SEO data from CSV files (e.g., Screaming Frog exports)
    - Perform various SEO health checks
    - Handle schema variations gracefully
    - Provide actionable SEO recommendations
    - Support multiple analysis types based on query intent
    """
    
    def __init__(self, csv_file: str = "screamingfrog.csv"):
        """
        Initialize SEO agent with data file.
        
        Args:
            csv_file: Path to SEO data CSV file
        """
        
        self.csv_file = csv_file
        self.df = None
        self._load_data()

    def _load_data(self):
        """Load SEO data with graceful error handling"""
        
        try:
            if os.path.exists(self.csv_file):
                self.df = pd.read_csv(self.csv_file)
                log_agent_call("SEOAgent", f"Loaded {len(self.df)} rows from {self.csv_file}", True)
            else:
                # Create sample data for demonstration
                self.df = self._create_sample_data()
                log_agent_call("SEOAgent", "Using sample data (no CSV file found)", True)
                
        except Exception as e:
            log_error(e, "SEOAgent data loading")
            self.df = self._create_sample_data()

    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample SEO data for demonstration purposes"""
        
        sample_data = {
            "Address": [
                "http://example.com/",
                "https://example.com/about",
                "http://example.com/contact",
                "https://example.com/services",
                "http://example.com/blog/post-1"
            ],
            "Title 1": [
                "Example Website - Your trusted partner for digital solutions and services",
                "About Us - Example Company",
                "Contact Us Today for More Information About Our Services",
                "Our Services",
                "Blog Post 1 - Detailed analysis of modern web development trends and best practices"
            ],
            "Meta Description 1": [
                "Welcome to Example.com - providing quality services since 2020",
                "Learn more about our company history and mission",
                "",  # Missing meta description
                "Comprehensive services for your business needs",
                "Read our latest insights on web development"
            ],
            "Status Code": [200, 200, 200, 200, 404],
            "Content Type": [
                "text/html", "text/html", "text/html", "text/html", "text/html"
            ]
        }
        
        return pd.DataFrame(sample_data)

    def run(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for SEO analysis queries.
        
        Args:
            query: Natural language SEO query
            
        Returns:
            SEO analysis results with recommendations
        """
        
        start_time = time.time()
        
        try:
            # Parse query to determine analysis type
            analysis_plan = parse_seo_query(query)
            log_agent_call("SEOAgent", f"Query parsed: {query}", True)
            
            # Route to appropriate analysis method
            analysis_type = analysis_plan.get("analysis_type", "general_seo_health")
            parameters = analysis_plan.get("parameters", {})
            
            if analysis_type == "non_https_long_titles":
                result = self.analyze_non_https_long_titles(**parameters)
            elif analysis_type == "title_analysis":
                result = self.analyze_titles(**parameters)
            elif analysis_type == "meta_description_analysis":
                result = self.analyze_meta_descriptions(**parameters)
            elif analysis_type == "https_analysis":
                result = self.analyze_https_usage(**parameters)
            else:
                result = self.general_seo_health(**parameters)
            
            # Add query context
            result["query"] = query
            result["analysis_type"] = analysis_type
            
            # Log performance
            duration = (time.time() - start_time) * 1000
            log_performance("SEOAgent.run", duration)
            
            return result
            
        except Exception as e:
            log_error(e, "SEOAgent execution")
            return {
                "error": f"SEO analysis failed: {str(e)}",
                "query": query
            }

    def analyze_non_https_long_titles(self, title_length_threshold: int = 60) -> Dict[str, Any]:
        """
        Find pages with non-HTTPS URLs and long titles.
        
        Args:
            title_length_threshold: Maximum recommended title length
            
        Returns:
            Analysis results with affected URLs
        """
        
        if self.df is None:
            return {"error": "No SEO data available"}
        
        # Filter for non-HTTPS URLs with long titles
        try:
            non_https = ~self.df["Address"].str.startswith("https://", na=False)
            long_titles = self.df["Title 1"].str.len() > title_length_threshold
            
            result_df = self.df[non_https & long_titles]
            
            findings = []
            for _, row in result_df.iterrows():
                findings.append({
                    "url": row.get("Address", ""),
                    "title": row.get("Title 1", "")[:100] + "..." if len(str(row.get("Title 1", ""))) > 100 else row.get("Title 1", ""),
                    "title_length": len(str(row.get("Title 1", ""))),
                    "issues": ["Non-HTTPS URL", f"Title exceeds {title_length_threshold} characters"]
                })
            
            return {
                "summary": f"Found {len(findings)} pages with non-HTTPS URLs and long titles",
                "analysis_type": "non_https_long_titles",
                "total_issues": len(findings),
                "findings": findings,
                "recommendations": [
                    "Migrate all URLs to HTTPS for better security and SEO",
                    f"Optimize page titles to be under {title_length_threshold} characters",
                    "Ensure titles are descriptive but concise",
                    "Implement proper SSL certificates across the domain"
                ]
            }
            
        except KeyError as e:
            return {
                "error": f"Required column not found in SEO data: {str(e)}",
                "available_columns": list(self.df.columns) if self.df is not None else []
            }

    def analyze_titles(self, length_threshold: int = 60) -> Dict[str, Any]:
        """
        Analyze page titles for length and missing titles.
        
        Args:
            length_threshold: Recommended maximum title length
            
        Returns:
            Title analysis results
        """
        
        if self.df is None:
            return {"error": "No SEO data available"}
        
        try:
            title_col = "Title 1"
            
            # Missing titles
            missing_titles = self.df[self.df[title_col].isna() | (self.df[title_col] == "")]
            
            # Long titles
            long_titles = self.df[self.df[title_col].str.len() > length_threshold]
            
            # Short titles (potentially under-optimized)
            short_titles = self.df[self.df[title_col].str.len() < 30]
            
            findings = {
                "missing_titles": len(missing_titles),
                "long_titles": len(long_titles),
                "short_titles": len(short_titles),
                "total_pages": len(self.df)
            }
            
            issues = []
            
            # Add specific examples
            if len(missing_titles) > 0:
                issues.extend([{
                    "url": row.get("Address", ""),
                    "issue": "Missing title tag",
                    "recommendation": "Add descriptive title tag"
                } for _, row in missing_titles.head(5).iterrows()])
            
            if len(long_titles) > 0:
                issues.extend([{
                    "url": row.get("Address", ""),
                    "title": str(row.get(title_col, ""))[:100] + "...",
                    "length": len(str(row.get(title_col, ""))),
                    "issue": f"Title exceeds {length_threshold} characters",
                    "recommendation": "Shorten title while maintaining descriptiveness"
                } for _, row in long_titles.head(5).iterrows()])
            
            return {
                "summary": f"Title analysis complete. Found {len(issues)} issues across {len(self.df)} pages.",
                "analysis_type": "title_analysis",
                "statistics": findings,
                "issues": issues,
                "recommendations": [
                    "Ensure all pages have unique, descriptive titles",
                    f"Keep titles between 30-{length_threshold} characters",
                    "Include target keywords naturally in titles",
                    "Avoid duplicate titles across pages"
                ]
            }
            
        except Exception as e:
            return {"error": f"Title analysis failed: {str(e)}"}

    def analyze_meta_descriptions(self, length_threshold: int = 160) -> Dict[str, Any]:
        """
        Analyze meta descriptions for optimization opportunities.
        
        Args:
            length_threshold: Recommended maximum meta description length
            
        Returns:
            Meta description analysis results
        """
        
        if self.df is None:
            return {"error": "No SEO data available"}
        
        try:
            meta_col = "Meta Description 1"
            
            # Missing meta descriptions
            missing_meta = self.df[self.df[meta_col].isna() | (self.df[meta_col] == "")]
            
            # Long meta descriptions
            long_meta = self.df[self.df[meta_col].str.len() > length_threshold]
            
            issues = []
            
            # Process missing meta descriptions
            for _, row in missing_meta.head(10).iterrows():
                issues.append({
                    "url": row.get("Address", ""),
                    "issue": "Missing meta description",
                    "recommendation": "Add compelling meta description to improve click-through rates"
                })
            
            # Process long meta descriptions
            for _, row in long_meta.head(10).iterrows():
                issues.append({
                    "url": row.get("Address", ""),
                    "meta_description": str(row.get(meta_col, ""))[:100] + "...",
                    "length": len(str(row.get(meta_col, ""))),
                    "issue": f"Meta description exceeds {length_threshold} characters",
                    "recommendation": "Shorten meta description to avoid truncation in search results"
                })
            
            return {
                "summary": f"Meta description analysis: {len(missing_meta)} missing, {len(long_meta)} too long",
                "analysis_type": "meta_description_analysis",
                "statistics": {
                    "missing_meta_descriptions": len(missing_meta),
                    "long_meta_descriptions": len(long_meta),
                    "total_pages": len(self.df)
                },
                "issues": issues,
                "recommendations": [
                    f"Keep meta descriptions under {length_threshold} characters",
                    "Write compelling, action-oriented descriptions",
                    "Include target keywords naturally",
                    "Make each meta description unique and relevant to page content"
                ]
            }
            
        except Exception as e:
            return {"error": f"Meta description analysis failed: {str(e)}"}

    def analyze_https_usage(self) -> Dict[str, Any]:
        """
        Analyze HTTPS usage across the website.
        
        Returns:
            HTTPS usage analysis results
        """
        
        if self.df is None:
            return {"error": "No SEO data available"}
        
        try:
            # Check HTTPS usage
            https_urls = self.df[self.df["Address"].str.startswith("https://", na=False)]
            http_urls = self.df[self.df["Address"].str.startswith("http://", na=False)]
            
            non_https_issues = []
            for _, row in http_urls.head(20).iterrows():
                non_https_issues.append({
                    "url": row.get("Address", ""),
                    "issue": "Using HTTP instead of HTTPS",
                    "recommendation": "Redirect to HTTPS version"
                })
            
            https_percentage = (len(https_urls) / len(self.df)) * 100 if len(self.df) > 0 else 0
            
            return {
                "summary": f"HTTPS adoption: {https_percentage:.1f}% of pages use HTTPS",
                "analysis_type": "https_analysis",
                "statistics": {
                    "https_urls": len(https_urls),
                    "http_urls": len(http_urls),
                    "https_percentage": round(https_percentage, 1),
                    "total_urls": len(self.df)
                },
                "issues": non_https_issues,
                "recommendations": [
                    "Implement HTTPS across all pages",
                    "Set up proper SSL certificates",
                    "Redirect all HTTP URLs to HTTPS versions",
                    "Update internal links to use HTTPS"
                ]
            }
            
        except Exception as e:
            return {"error": f"HTTPS analysis failed: {str(e)}"}

    def general_seo_health(self) -> Dict[str, Any]:
        """
        Perform general SEO health check across multiple factors.
        
        Returns:
            Comprehensive SEO health report
        """
        
        if self.df is None:
            return {"error": "No SEO data available"}
        
        try:
            health_score = 100
            issues = []
            
            # Check HTTPS usage
            http_urls = len(self.df[self.df["Address"].str.startswith("http://", na=False)])
            if http_urls > 0:
                health_score -= 20
                issues.append(f"{http_urls} pages not using HTTPS")
            
            # Check for missing titles
            missing_titles = len(self.df[self.df["Title 1"].isna() | (self.df["Title 1"] == "")])
            if missing_titles > 0:
                health_score -= 15
                issues.append(f"{missing_titles} pages missing titles")
            
            # Check for long titles
            long_titles = len(self.df[self.df["Title 1"].str.len() > 60])
            if long_titles > 0:
                health_score -= 10
                issues.append(f"{long_titles} pages have titles over 60 characters")
            
            # Check for missing meta descriptions
            missing_meta = len(self.df[self.df["Meta Description 1"].isna() | (self.df["Meta Description 1"] == "")])
            if missing_meta > 0:
                health_score -= 10
                issues.append(f"{missing_meta} pages missing meta descriptions")
            
            # Check for error pages
            if "Status Code" in self.df.columns:
                error_pages = len(self.df[self.df["Status Code"] != 200])
                if error_pages > 0:
                    health_score -= 15
                    issues.append(f"{error_pages} pages returning error status codes")
            
            health_score = max(0, health_score)  # Ensure score doesn't go below 0
            
            return {
                "summary": f"SEO Health Score: {health_score}/100",
                "analysis_type": "general_seo_health",
                "health_score": health_score,
                "total_pages_analyzed": len(self.df),
                "issues_found": len(issues),
                "issues": issues,
                "recommendations": [
                    "Prioritize fixing HTTPS issues for security and ranking benefits",
                    "Ensure all pages have unique, optimized titles",
                    "Add compelling meta descriptions to improve click-through rates",
                    "Fix any technical errors affecting page accessibility",
                    "Regularly monitor and maintain SEO health metrics"
                ]
            }
            
        except Exception as e:
            return {"error": f"SEO health check failed: {str(e)}"}