import os
import re
import requests
from urllib.parse import urljoin
from tqdm import tqdm  # optional, for progress bar
import zipfile
import csv
import glob
import math
import time
import pandas as pd
import polars as pl
import aiohttp
import asyncio

# URL of the page to scrape
BASE_URL = 'https://noaaocm.blob.core.windows.net/ais/csv2/csv2025/index.html' #change to link to desired year
DOWNLOAD_FOLDER = 'extracted_files'

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def get_zst_links(session):
    async with session.get(BASE_URL) as response:
        html = await response.text()

    links = [
        urljoin(BASE_URL, match)
        for match in re.findall(r'href="([^"]+\.zst)"', html)
        if match.startswith("ais-2025-01-0")
    ]

    return links

async def download_file(session, url):
    filename = os.path.basename(url)
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    if os.path.exists(filepath):
        print(f"Already downloaded: {filename}")
        return

    print(f"Downloading {filename}...")

    async with session.get(url) as response:
        response.raise_for_status()

        with open(filepath, "wb") as f:
            async for chunk in response.content.iter_chunked(8192):
                f.write(chunk)


async def main():
    async with aiohttp.ClientSession() as session:

        # Scrape the page
        links = await get_zst_links(session)

        print(f"Found {len(links)} files.")

        # Download everything simultaneously
        await asyncio.gather(
            *(download_file(session, url) for url in links)
        )

start = time.perf_counter()
asyncio.run(main())
end = time.perf_counter()

print(f"Total runtime: {end - start:.2f} seconds")