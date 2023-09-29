import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import json

folder_path = sys.argv[-1] if len(sys.argv) > 1 else './results'
index_name = os.path.basename(os.path.normpath(folder_path))

# Create a folder named 'results' if it does not exist
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Base URL of the documentation
base_url = 'https://gpt-index.readthedocs.io/en/latest/'

# Function to scrape the sidebar links
def get_sidebar_links(url, sidebar_class_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sidebar = soup.find('div', {'class': sidebar_class_name})
    links = [urljoin(base_url, a['href']) for a in sidebar.find_all('a') if a.get('href')]
    return links

# Function to scrape and store content
def scrape_and_store_content(url):
    # Initialize an empty list to store the scraped content
    content_list = []
    content_list.append(f"URL: {url}\n")  # Add the URL as the first line

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    main_section = soup.find(attrs={'role': 'main'})
    if not main_section:
        print(f"Main section not found for URL: {url}")
        return

    # Extract relevant text, headings and code snippets
    elements = main_section.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre'])
    if elements:
        for el in elements:
            if el.name == 'p':
                # Try to detect if this is a JSON-like object
                text = el.get_text().strip()
                if text.startswith('{') and text.endswith('}'):
                    try:
                        parsed_json = json.loads(text)
                        text = json.dumps(parsed_json, indent=0, separators=(',', ':'))
                    except json.JSONDecodeError:
                        pass  # Not a JSON object, use the text as-is
                content_list.append(text)
            else:
                content_list.append(f"{el.name.upper()}: {el.get_text()}")


        content = '\n'.join(el.get_text() if el.name == 'p' else f"{el.name.upper()}: {el.get_text()}" for el in elements)
        # Get the last part of the URL to use as a filename
        filename = url.split('/')[-1] or url.split('/')[-2]  # Handles trailing slashes
        filename.replace(".html", "")
        # Store the content in a text file within 'results' folder
        with open(f'{folder_path}/{filename}.txt', 'w', encoding='utf-8') as f:
            f.write(f"URL: {url}\n")  # Write the URL as the first line
            f.write(content)
    else:
        print(f"No elements found for URL: {url}")

# Get sidebar links
sidebar_links = get_sidebar_links(base_url, 'sidebar-container')

# Scrape and store content for each link
for link in sidebar_links:
    scrape_and_store_content(link)

print('Scraping and storing complete.')
