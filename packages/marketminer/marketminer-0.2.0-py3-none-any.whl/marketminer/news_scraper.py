'''
Module for scraping news articles from various sources.
'''

import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd
from datetime import datetime, timedelta, date
from .utils import date_to_excel_serial
import re
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/120.0.0.0 Safari/537.36"
}
_BASE = "https://economictimes.indiatimes.com"


def scrape_economic_times(start_date: str | datetime | date, end_date: str | datetime | date) -> pd.DataFrame:
    """
    Scrape news articles from Economic Times within a date range.

    Parameters:
    start_date (str): Start date in the format 'YYYY-MM-DD'.
    end_date (str): End date in the format 'YYYY-MM-DD'.

    Returns:
        pd.DataFrame: DataFrame containing news articles.
    """
    results = []
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    if start_dt > end_dt:
        raise ValueError("Start date must be before end date.")

    curr_date = start_dt

    session = requests.Session()
    session.headers.update(HEADERS)

    while curr_date <= end_dt:
        logger.info(f"Scraping archive for {curr_date.date()}...")
        year = int(curr_date.year)
        month = int(curr_date.month)
        starttime = date_to_excel_serial(curr_date.date())

        archive_url = f"https://economictimes.indiatimes.com/archivelist/year-{year},month-{month},starttime-{starttime}.cms"
        r = session.get(archive_url)
        if r.status_code != 200:
            logger.warning(f"Failed to fetch archive for {curr_date.date()}")
            curr_date += timedelta(days=1)
            continue

        soup = BeautifulSoup(r.content, "html.parser")

        articles = soup.select("a[href*='/industry/'], a[href*='/markets/'], a[href*='/tech/']")
        # count = 0
        # skip = 0
        def process_article(article, curr_date, session):
            # nonlocal count, skip
            # count += 1
            headline = article.text.strip()
            link = article.get('href', '')
            if link.startswith("/"):
                link = urljoin(_BASE, link)
            # Remove whitespace and ensure link is valid
            link = link.strip()

            # if count < 4 or 'live' in link or 'articleshow' not in link:
            #     # Skip the first 3 articles which contain market data
            #     skip += 1
            #     return None
            if 'live' in link or 'articleshow' not in link:
                # Skip articles that are live updates or not in the articleshow format
                return None


            # Access link to get the full article body and more details
            r = session.get(link)
            if r.status_code != 200:
                logger.warning(f"Failed to fetch article {link}")
                return None

            article_soup = BeautifulSoup(r.content, "html.parser")
            match = re.search(r'/(?:amp_)?articleshow/(\d+)\.cms', link)
            article_id = match.group(1) if match else None
            body = ' '.join([p.get_text() for p in article_soup.select('.artText, .Normal')])
            return {
                "article_id": article_id,
                "headline": headline,
                "link": link,
                "date": curr_date.strftime("%Y-%m-%d"),
                "body": body
            }

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_article, article, curr_date, session) for article in articles]
            # Drop None results and collect valid ones
            futures = [future for future in futures if future is not None]
            for future in futures:
                result = future.result()
                if result:
                    results.append(result)

        logger.info(f"Found {len(futures)} articles for {curr_date.date()}.")
        curr_date += timedelta(days=1)

    logging.info(f"Dropping duplicate articles based on headline and link.")
    df = pd.DataFrame(results)
    if df.empty:
        logger.info("No articles found in the specified date range.")
        return pd.DataFrame(columns=["headline", "link", "category", "date", "body"])
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)
    logger.info(f"Scraped {len(df)} articles from Economic Times.")
    return df
