"""
Job Web Scraper Module
=======================
Web scraping functionality for collecting job market data.
Uses BeautifulSoup for HTML parsing.

Note: For live demos, this module uses simulated data to avoid
rate limiting and blocking by job portals.

Dataset Sources: Indeed, LinkedIn (scraped format), Kaggle Job Datasets
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class JobScraper:
    """
    Web scraper for collecting job posting data from job portals.
    Includes respectful scraping policies with rate limiting.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        })
        self.rate_limit_seconds = 2  # Respectful scraping

    def scrape_job_listing(self, url):
        """
        Scrape a single job listing page.

        Args:
            url: URL of the job listing

        Returns:
            Dict with title, company, description, skills, etc.
        """
        try:
            time.sleep(self.rate_limit_seconds)
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract common fields (generic selectors)
            title = self._extract_text(soup, ["h1", ".job-title", ".posting-title"])
            company = self._extract_text(soup, [".company-name", ".employer-name"])
            description = self._extract_text(soup, [".job-description", ".description", "article"])

            return {
                "title": title,
                "company": company,
                "description": description,
                "url": url,
                "scraped_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "url": url}

    def _extract_text(self, soup, selectors):
        """Try multiple CSS selectors to find text."""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return ""

    def parse_job_description_html(self, html_content):
        """
        Parse HTML job description to extract structured data.

        Args:
            html_content: Raw HTML string

        Returns:
            Dict with parsed sections
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract text
        text = soup.get_text(separator="\n", strip=True)

        # Extract bullet points (common in JDs)
        bullets = []
        for li in soup.find_all("li"):
            bullets.append(li.get_text(strip=True))

        return {
            "full_text": text,
            "bullet_points": bullets,
            "word_count": len(text.split())
        }

    def get_scraped_data_stats(self):
        """Get statistics about stored scraped data."""
        csv_path = DATA_DIR / "job_market_data.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            return {
                "total_records": len(df),
                "unique_roles": df["title"].nunique() if "title" in df else 0,
                "unique_companies": df["company"].nunique() if "company" in df else 0,
                "status": "data_available"
            }
        return {"status": "no_data", "total_records": 0}


# ====================================
# SINGLETON
# ====================================
_scraper = None

def get_scraper():
    global _scraper
    if _scraper is None:
        _scraper = JobScraper()
    return _scraper
