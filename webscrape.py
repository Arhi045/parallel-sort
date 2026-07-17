import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm  # optional, for progress bar
import zipfile
import csv
import glob
import math
import pandas as pd
import polars as pl

# URL of the page to scrape
BASE_URL = 'https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2024/index.html' #change to link to desired year
DOWNLOAD_FOLDER = 'extracted_files'

# Step 1: Fetch the page
response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Step 2: Find all links to .zip files
zip_links = [
    urljoin(BASE_URL, a['href'])
    for a in soup.find_all('a', href=True)
    if a['href'].endswith('.zip')
    if a['href'].startswith('AIS_2024_07')
]
'''change a['href'].startswith to desired month, or comment for entire year'''

# Step 3: Create download folder if not exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Step 4: Download each .zip file
for url in tqdm(zip_links, desc='Downloading ZIP files'):
    filename = os.path.basename(url)
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        print(f"Downloading {filename}...")
        r = requests.get(url, stream=True)
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        print(f"Already downloaded: {filename}")

# Step 5 (Optional): Extract ZIP files
for filename in os.listdir(DOWNLOAD_FOLDER):
    if filename.endswith('.zip'):
        zip_path = os.path.join(DOWNLOAD_FOLDER, filename)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.join(DOWNLOAD_FOLDER))