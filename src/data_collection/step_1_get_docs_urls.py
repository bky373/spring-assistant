from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def get_docs_urls(base_url):
    response = requests.get(base_url)
    nav_links = BeautifulSoup(response.content, 'lxml').select('nav ul .nav-link')
    full_urls = [urljoin(base_url, link.get('href')) for link in nav_links if link.get('href')]

    urls = []
    for url in full_urls:
        if not url.endswith('wiki') and "api/java" not in url:
            urls.append(url)
    return urls
