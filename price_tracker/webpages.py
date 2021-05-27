from flask import current_app

import requests
from selenium import webdriver
from urllib.parse import urlparse


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")


def get_response_text(url, method="requests"):
    if method == "requests":
        response = requests.get(url, headers=get_request_headers(url), timeout=5)
        return response.text

    if method == "selenium":
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        response = driver.page_source
        driver.quit()
        return response


def get_request_headers(url):
    parsed_url = urlparse(url)
    return {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Cache-Control": "no-cache", "Connection": "keep-alive", "DNT": "1", "Host": parsed_url.hostname, "Pragma": "no-cache", "Upgrade-Insecure-Requests": "1", "User-Agent": current_app.config["USER_AGENT"]}