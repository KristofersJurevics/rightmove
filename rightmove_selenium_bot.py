# rightmove_selenium_bot.py
import json
import ssl
import time
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

SEARCH_URLS = {
    "Kent": "https://www.rightmove.co.uk/property-for-sale/find.html?searchLocation=Kent&useLocationIdentifier=true&locationIdentifier=REGION%5E61307&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=Kent",
    "West Sussex":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E61399&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=West-Sussex&index=0",
    "East Sussex":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E61534&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=East-Sussex&index=0",
    "Hampshire":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E61303&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=Hampshire&index=0",
    "Wiltshire":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E61328&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=Wiltshire&index=0",
    "Somerset":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E61322&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=Somerset&index=0",
    "Dorset":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E61298&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=Dorset&index=0",
    "Devon":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E61297&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=Devon&index=0",
    "Cotswolds":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E91995&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=Cotswolds&index=0",
    "Cornwall":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E61294&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=Cornwall&index=0",
    "Gloucestershire":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E61302&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=Gloucestershire&index=0",
    "South Wales":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E91990&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=South-Wales&index=0",
    "Mid Wales":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E92206&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=Mid-Wales&index=0",
    "North Wales":"https://www.rightmove.co.uk/property-for-sale/find.html?useLocationIdentifier=true&locationIdentifier=REGION%5E92050&radius=0.0&propertyTypes=land&_includeSSTC=on&sortType=6&channel=BUY&transactionType=BUY&displayLocationIdentifier=North-Wales&index=0",
}

EMAIL_SENDER = "kristofers@almora.com"
EMAIL_PASSWORD = os.environ.get("RIGHTMOVE_EMAIL_APP_PASSWORD", "")  # Set in environment, never commit secrets
EMAIL_RECEIVER = "kristofers.jurevics15@gmail.com"

DATA_FILE = "seen_listings.json"

# ---------------------
# HELPERS
# ---------------------
def load_seen():
    """Load set of already seen listing IDs"""
    try:
        with open(DATA_FILE, "r") as f:
            return {item['id'] for item in json.load(f)}
    except FileNotFoundError:
        return set()

def append_listing_to_json(listing):
    """Append a new listing to the JSON file"""
    try:
        data = []
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(listing)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def fetch_listings(url, region):
    """Scrape listings from Rightmove using Selenium"""
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # wait for JS to load

    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div[data-testid^='propertyCard']")
    for card in cards:
        try:
            # Skip featured properties
            classes = card.get_attribute("class")
            if "featured" in classes.lower():
                continue

            link_elem = card.find_element(By.CSS_SELECTOR, "a[data-test='property-details']")
            href = link_elem.get_attribute("href")
            if href.startswith("/"):
                url_full = "https://www.rightmove.co.uk" + href
            else:
                url_full = href

            # Extract listing ID before any fragment (#) or query parameters
            listing_id = url_full.split("/properties/")[-1].split("#")[0].split("?")[0]

            # Short title
            title_elem = card.find_element(By.CSS_SELECTOR, "address")
            title = title_elem.text if title_elem else "No title"

            listings.append({
                "id": listing_id,
                "title": f"{region}: {title}",
                "url": url_full,
                "region": region
            })
        except Exception as e:
            print("Skipping card due to error:", e)
            continue

    driver.quit()
    return listings

def send_email(new_listings):
    """Send email notification with all new listings"""
    if not new_listings:
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Rightmove new listings – {date.today()}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    html_list = "".join([f"<li><a href='{item['url']}'>{item['title']}</a></li>" for item in new_listings])
    html = f"<h3>New listings found:</h3><ul>{html_list}</ul>"

    msg.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()
    if not EMAIL_PASSWORD:
        raise RuntimeError("Set RIGHTMOVE_EMAIL_APP_PASSWORD in the environment before sending emails")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

# ---------------------
# MAIN SCRIPT
# ---------------------
def main():
    seen_ids = load_seen()
    new_items = []

    for region, url in SEARCH_URLS.items():
        print(f"Checking {region}...")
        listings = fetch_listings(url, region)
        for listing in listings:
            if listing['id'] not in seen_ids:
                append_listing_to_json(listing)
                seen_ids.add(listing['id'])
                new_items.append(listing)
                print(f"Saved listing: {listing['title']}")

    if new_items:
        send_email(new_items)
        print(f"{len(new_items)} new listings found! Email sent.")
    else:
        print("No new listings found.")

if __name__ == "__main__":
    main()

