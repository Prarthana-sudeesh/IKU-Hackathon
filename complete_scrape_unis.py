import argparse
import os
import re
import time
from dotenv import load_dotenv
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. CONFIGURATION & CREDENTIALS ---
load_dotenv()

SNOWFLAKE_CONFIG = {
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "account": os.getenv("SNOWFLAKE_ACCOUNT")
}

CRITERIA = {
    "Ramped/Sloped Access, and/or Manual Doors": "RAMPED_SLOPED_ACCESS_MANUAL_DOORS",
    "Mobility Impaired Walker": "MOBILITY_IMPAIRED_WALKER",
    "On-Site Parking": "ON_SITE_PARKING",
    "Blue Badge/Accessible Parking Bays": "BLUE_BADGE_PARKING_BAYS",
    "Accessible Toilet": "ACCESSIBLE_TOILET",
    "Ambulant Toilet": "AMBULANT_TOILET",
    "Step Free Standard Toilet": "STEP_FREE_STANDARD_TOILET",
    "Seat(s) Available": "SEATS_AVAILABLE"
}

KNOWN_UNIVERSITIES = {
    "imperial": "imperial-college-london",
    "oxford": "university-of-oxford",
    "cambridge": "university-of-cambridge",
    "ucl": "university-college-london",
    "kcl": "king-s-college-london",
    "manchester": "university-of-manchester",
    "leeds": "university-of-leeds"
}


def validate_credentials():
    """Ensure required credentials exist before launching database operations."""
    missing = [k for k, v in SNOWFLAKE_CONFIG.items() if not v]
    if missing:
        raise ValueError(
            f"Missing required environment variables in your .env file: {', '.join(missing)}\n"
            f"Make sure your .env has: SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and SNOWFLAKE_PASSWORD"
        )


# --- 2. SNOWFLAKE DATABASE BOOTSTRAPPER ---
def initialize_snowflake():
    """Connects to Snowflake and automatically creates the warehouse, database, schema, and table."""
    validate_credentials()
    print("[Snowflake] Initializing warehouse, database, schema, and table...")

    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cur = conn.cursor()

    try:
        # Create warehouse (auto-suspends after 60s to protect trial credits)
        cur.execute("""
            CREATE WAREHOUSE IF NOT EXISTS ACCESSIBILITY_WH WITH
                WAREHOUSE_SIZE = 'XSMALL'
                AUTO_SUSPEND = 60
                AUTO_RESUME = TRUE;
        """)
        cur.execute("USE WAREHOUSE ACCESSIBILITY_WH;")

        # Create Database & Schema
        cur.execute("CREATE DATABASE IF NOT EXISTS CAMPUS_DB;")
        cur.execute("CREATE SCHEMA IF NOT EXISTS CAMPUS_DB.ACCESSIBILITY_SCHEMA;")
        cur.execute("USE SCHEMA CAMPUS_DB.ACCESSIBILITY_SCHEMA;")

        # Create Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS UNIVERSITY_ACCESSIBILITY (
                BUILDING_ID                       VARCHAR(64),
                BUILDING_NAME                     VARCHAR(255),
                ORGANISATION_SLUG                 VARCHAR(100),
                ACCESSABLE_URL                    VARCHAR(500),
                RAMPED_SLOPED_ACCESS_MANUAL_DOORS BOOLEAN,
                MOBILITY_IMPAIRED_WALKER          BOOLEAN,
                ON_SITE_PARKING                   BOOLEAN,
                BLUE_BADGE_PARKING_BAYS           BOOLEAN,
                ACCESSIBLE_TOILET                 BOOLEAN,
                AMBULANT_TOILET                   BOOLEAN,
                STEP_FREE_STANDARD_TOILET         BOOLEAN,
                SEATS_AVAILABLE                   BOOLEAN,
                LOADED_AT                         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            );
        """)
        print("[Snowflake] Infrastructure verified and ready!")
    finally:
        cur.close()
        conn.close()


# --- 3. ACCESSIBLE SCRAPER LOGIC (SELENIUM) ---
def get_chrome_driver():
    """Configures Chrome headless options compatible with macOS arm64."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    
    # Auto-downloads matching ChromeDriver for your Mac
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def extract_active_symbols_for_venue(driver):
    """Clicks 'View Accessibility Symbols' modal and reads only the granted symbols."""
    active_symbols = set()
    try:
        # Check if the modal button exists
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'View Accessibility Symbols')]")
        if buttons:
            driver.execute_script("arguments[0].click();", buttons[0])
            time.sleep(0.6)  # Wait for modal animation

            # Search inside the modal dialog
            modals = driver.find_elements(By.CSS_SELECTOR, ".modal, [role='dialog'], .symbols-modal, .swal2-modal")
            if modals:
                modal = modals[0]
                elements = modal.find_elements(By.CSS_SELECTOR, "img[alt], p, span, li")
                for el in elements:
                    alt = el.get_attribute("alt") or ""
                    txt = el.text or ""
                    active_symbols.add(f"{alt} {txt}".strip().lower())

                # Close modal
                close_btns = modal.find_elements(By.CSS_SELECTOR, "button.close, [aria-label='Close'], button")
                if close_btns:
                    driver.execute_script("arguments[0].click();", close_btns[0])
    except Exception:
        pass

    return " --- ".join(active_symbols)


def scrape_university(uni_slug: str):
    base_org_url = f"https://www.accessable.co.uk/organisations/{uni_slug}"
    print(f"\n[Scraper] Visiting: {base_org_url}")
    records = []

    driver = get_chrome_driver()
    try:
        driver.get(base_org_url)
        time.sleep(2)

        # Accept cookies if banner appears
        try:
            accept_btn = driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept')]")
            if accept_btn:
                driver.execute_script("arguments[0].click();", accept_btn[0])
        except Exception:
            pass

        # Collect building guide URLs
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/access-guides/']")
        venue_urls = set()
        for link in links:
            href = link.get_attribute("href")
            if href:
                venue_urls.add(href)

        print(f"[Scraper] Found {len(venue_urls)} guides. Extracting attributes...")

        for idx, url in enumerate(sorted(venue_urls), start=1):
            try:
                driver.get(url)
                time.sleep(1)

                # Get building name
                h1_elements = driver.find_elements(By.TAG_NAME, "h1")
                name = h1_elements[0].text.strip() if h1_elements else "Unknown"

                # Extract scoped symbols
                active_symbols = extract_active_symbols_for_venue(driver)

                row = {
                    "BUILDING_ID": re.sub(r"[^A-Z0-9]", "", name.upper())[:16],
                    "BUILDING_NAME": name,
                    "ORGANISATION_SLUG": uni_slug,
                    "ACCESSABLE_URL": url
                }

                for label, col in CRITERIA.items():
                    clean_kw = label.lower().replace("and/or ", "").strip()
                    row[col] = (clean_kw in active_symbols) or (label.lower() in active_symbols)

                records.append(row)
                print(f"  [{idx}/{len(venue_urls)}] {name[:35]:<35} | Ramped: {row['RAMPED_SLOPED_ACCESS_MANUAL_DOORS']!s:<5}")

            except Exception as e:
                print(f"  [{idx}/{len(venue_urls)}] Error scraping {url}: {e}")

    finally:
        driver.quit()

    return records


# --- 4. DATA UPLOADER ---
def upload_to_snowflake(records):
    """Streams the records directly into Snowflake using write_pandas."""
    if not records:
        print("[Upload] No records found to upload.")
        return

    validate_credentials()

    df = pd.DataFrame(records)
    df.columns = [col.upper() for col in df.columns]

    print(f"\n[Snowflake] Connecting to upload {len(df)} records...")
    conn = snowflake.connector.connect(
        **SNOWFLAKE_CONFIG,
        warehouse="ACCESSIBILITY_WH",
        database="CAMPUS_DB",
        schema="ACCESSIBILITY_SCHEMA"
    )

    try:
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name="UNIVERSITY_ACCESSIBILITY",
            auto_create_table=False
        )
        if success:
            print(f" Successfully inserted {nrows} rows into CAMPUS_DB.ACCESSIBILITY_SCHEMA.UNIVERSITY_ACCESSIBILITY!")
        else:
            print("❌ Upload failed.")
    finally:
        conn.close()


# --- 5. MAIN ENTRY POINT ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uni", type=str, default="imperial-college-london")
    args = parser.parse_args()

    slug = KNOWN_UNIVERSITIES.get(args.uni.lower(), args.uni.strip().lower())

    # 1. Initialize Snowflake DB/Warehouse/Table
    initialize_snowflake()

    # 2. Scrape with Selenium
    data = scrape_university(slug)

    # 3. Stream data to Snowflake
    upload_to_snowflake(data)