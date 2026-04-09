"""
Helpers Module
===============
Common utility functions used across the platform.
"""

import re
from datetime import datetime


def clean_text(text):
    """Clean and normalize text input."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep programming-relevant ones
    text = re.sub(r'[^\w\s\.\+\#\-\/]', ' ', text)
    return text.strip()


def format_percentage(value, decimals=1):
    """Format a number as a percentage string."""
    return f"{round(value, decimals)}%"


def format_hours(hours):
    """Format hours into a human-readable string."""
    if hours < 1:
        return f"{int(hours * 60)} minutes"
    elif hours < 24:
        return f"{int(hours)} hours"
    elif hours < 168:  # 7 days
        days = hours / 8
        return f"{round(days, 1)} days"
    else:
        weeks = hours / 40
        return f"{round(weeks, 1)} weeks"


def get_severity_color(severity):
    """Get color code for gap severity."""
    colors = {
        "Low": "#10b981",
        "Medium": "#f59e0b",
        "High": "#ef4444",
        "Critical": "#dc2626"
    }
    return colors.get(severity, "#6b7280")


def timestamp_now():
    """Get current timestamp string."""
    return datetime.utcnow().isoformat()
