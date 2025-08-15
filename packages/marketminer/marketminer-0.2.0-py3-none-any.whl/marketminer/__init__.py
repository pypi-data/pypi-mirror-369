'''
MarketMiner: A Python library for scraping financial data from various sources.
'''

__version__ = '0.2.0'

from .news_scraper import scrape_economic_times
from .utils import date_to_excel_serial

__all__ = [
    'scrape_economic_times',
    'date_to_excel_serial'
]