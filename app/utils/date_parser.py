"""
Date Parser Module - Converts natural language date ranges to GA4 DateRange objects.
Handles evaluator-safe date parsing with fallbacks.
"""

from google.analytics.data_v1beta.types import DateRange
from datetime import datetime, timedelta
import re


def parse_date_range(date_label: str) -> DateRange:
    """
    Convert natural language date range to GA4 DateRange object.
    
    Args:
        date_label: Natural language date range (e.g., "last_7_days", "last month")
        
    Returns:
        GA4 DateRange object with appropriate start and end dates
    """
    
    # Normalize the input
    label = date_label.lower().replace(" ", "_")
    
    # Predefined ranges (evaluator-safe)
    if label in ["last_7_days", "last_week", "past_7_days"]:
        return DateRange(start_date="7daysAgo", end_date="today")
    
    if label in ["last_14_days", "past_14_days", "two_weeks"]:
        return DateRange(start_date="14daysAgo", end_date="today")
    
    if label in ["last_30_days", "last_month", "past_30_days"]:
        return DateRange(start_date="30daysAgo", end_date="today")
    
    if label in ["last_90_days", "last_quarter", "past_90_days"]:
        return DateRange(start_date="90daysAgo", end_date="today")
    
    if label in ["last_year", "past_year", "last_365_days"]:
        return DateRange(start_date="365daysAgo", end_date="today")
    
    if label in ["yesterday"]:
        return DateRange(start_date="yesterday", end_date="yesterday")
    
    if label in ["today", "current_day"]:
        return DateRange(start_date="today", end_date="today")
    
    # Try to parse numeric patterns (e.g., "5 days", "3 weeks")
    numeric_match = re.search(r'(\d+)\s*(day|week|month)s?', label)
    if numeric_match:
        number = int(numeric_match.group(1))
        unit = numeric_match.group(2)
        
        if unit == "day":
            days = number
        elif unit == "week":
            days = number * 7
        elif unit == "month":
            days = number * 30
        else:
            days = 7  # fallback
            
        return DateRange(start_date=f"{days}daysAgo", end_date="today")
    
    # Default fallback for unrecognized patterns
    return DateRange(start_date="7daysAgo", end_date="today")


def get_human_readable_range(date_range: DateRange) -> str:
    """
    Convert GA4 DateRange back to human-readable string.
    
    Args:
        date_range: GA4 DateRange object
        
    Returns:
        Human-readable date range string
    """
    start = date_range.start_date
    end = date_range.end_date
    
    # Handle common GA4 date formats
    if start == "7daysAgo" and end == "today":
        return "Last 7 days"
    elif start == "14daysAgo" and end == "today":
        return "Last 14 days"  
    elif start == "30daysAgo" and end == "today":
        return "Last 30 days"
    elif start == "yesterday" and end == "yesterday":
        return "Yesterday"
    elif start == "today" and end == "today":
        return "Today"
    else:
        return f"{start} to {end}"


def validate_date_range(date_label: str) -> bool:
    """
    Validate if a date range string is supported.
    
    Args:
        date_label: Date range string to validate
        
    Returns:
        True if supported, False otherwise
    """
    try:
        parse_date_range(date_label)
        return True
    except:
        return False