import argparse
import asyncio
import re
from playwright.async_api import async_playwright
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
from dotenv import load_dotenv
import os

# The 8 target accessibility criteria
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

# Pre-defined common university slugs on AccessAble
KNOWN_UNIVERSITIES = {
    "imperial": "imperial-college-london",
    "oxford": "university-of-oxford",
    "cambridge": "university-of-cambridge",
    "ucl": "university-college-london",
    "kcl": "king-s-college-london",
    "manchester": "university-of-manchester",
    "birmingham": "university-of-birmingham",
    "leeds": "university-of-leeds",
    "edinburgh": "university-of-edinburgh",
    "bristol": "university-of-bristol",
    "nottingham-trent": "nottingham-trent-university",
    "birkbeck": "birkbeck-university-of-london"
}

async def extract_active_symbols_for_venue(page):
    """
    Safely opens the venue-specific 'View Accessibility Symbols' modal 
    and returns only the symbols actively granted to this venue.
    """
    venue_active_symbols = set()
    
    try:
        # 1. AccessAble has a dedicated button/link: 'View Accessibility Symbols'
        symbols_btn = page.locator("text=/View Accessibility Symbols/i").first
        
        if await symbols_btn.count() > 0 and await symbols_btn.is_visible():
            await symbols_btn.click(timeout=3000)
            await page.wait_for_timeout(600)  # wait for animation / modal to open

            # 2. Scope the query STRICTLY inside the open modal/dialog container
            modal = page.locator(".modal, [role='dialog'], .symbols-modal, .swal2-modal").first
            if await modal.count() > 0:
                # Extract text labels or alt tags of symbols inside the modal
                symbol_elements = await modal.locator("img[alt], p, span, li").all()
                for el in symbol_elements:
                    alt = await el.get_attribute("alt") or ""
                    txt = await el.inner_text() or ""
                    combined = f"{alt} {txt}".strip().lower()
                    if combined:
                        venue_active_symbols.add(combined)
                
                # Close the modal to keep DOM clean
                close_btn = modal.locator("button.close, [aria-label='Close'], button:has-text('Close')").first
                if await close_btn.count() > 0 and await close_btn.is_visible():
                    await close_btn.click()
            else:
                # Fallback if modal inline-expanded without a modal class
                symbols_section = page.locator("section:has-text('Accessibility Symbols')").first
                if await symbols_section.count() > 0:
                    text_content = (await symbols_section.inner_text()).lower()
                    venue_active_symbols.add(text_content)

        else:
            # 3. Direct badge icons in the venue header (without popup)
            badge_container = page.locator(".venue-symbols, .guide-symbols, .symbol-strip").first
            if await badge_container.count() > 0:
                icons = await badge_container.locator("img[alt]").all()
                for icon in icons:
                    alt = await icon.get_attribute("alt") or ""
                    venue_active_symbols.add(alt.strip().lower())

    except Exception as e:
        print(f"      [Warning] Could not extract modal symbols: {e}")

    return " --- ".join(venue_active_symbols)


async def scrape_university(uni_slug: str):
    base_org_url = f"https://www.accessable.co.uk/organisations/{uni_slug}"
    print(f"\n[1/3] Target University Directory: {base_org_url}")

    data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto(base_org_url, wait_until="networkidle", timeout=60000)
        except Exception:
            # Fallback if networkidle takes too long
            await page.goto(base_org_url, wait_until="domcontentloaded")

        # Accept cookie banner if present
        try:
            accept_btn = page.locator("button:has-text('Accept'), #aacookieconsent-accept").first
            if await accept_btn.count() > 0 and await accept_btn.is_visible():
                await accept_btn.click()
        except Exception:
            pass

        # Collect building/guide links
        venue_links = await page.locator("a[href*='/access-guides/']").all()
        venue_urls = set()
        for link in venue_links:
            href = await link.get_attribute("href")
            if href:
                full_url = href if href.startswith("http") else f"https://www.accessable.co.uk{href}"
                venue_urls.add(full_url)

        print(f"[2/3] Discovered {len(venue_urls)} building access guides. Scraping records...\n")

        for idx, url in enumerate(sorted(venue_urls), start=1):
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(500)

                # Extract building name
                title_elem = page.locator("h1").first
                building_name = (await title_elem.inner_text()).strip() if await title_elem.count() > 0 else "Unknown Building"

                # Extract strictly active symbols
                active_symbols_text = await extract_active_symbols_for_venue(page)

                record = {
                    "BUILDING_ID": re.sub(r"[^A-Z0-9]", "", building_name.upper())[:16],
                    "BUILDING_NAME": building_name,
                    "ORGANISATION_SLUG": uni_slug,
                    "ACCESSABLE_URL": url
                }

                # Strictly evaluate each of the 8 criteria
                for crit_label, col_name in CRITERIA.items():
                    # Exact or standardized keyword matching
                    search_term = crit_label.lower().replace("and/or ", "").strip()
                    record[col_name] = (search_term in active_symbols_text) or (crit_label.lower() in active_symbols_text)

                data.append(record)
                
                # Terminal progress indicator
                has_ramped = record["RAMPED_SLOPED_ACCESS_MANUAL_DOORS"]
                has_toilet = record["ACCESSIBLE_TOILET"]
                print(f"[{idx}/{len(venue_urls)}] {building_name[:40]:<40} | Ramped: {has_ramped!s:<5} | Acc Toilet: {has_toilet!s:<5}")

            except Exception as e:
                print(f"[{idx}/{len(venue_urls)}] Failed to scrape {url}: {e}")

        await browser.close()

    # Save output to CSV
    output_filename = f"{uni_slug}_accessibility_snowflake.csv"
    df = pd.DataFrame(data)
    df.columns = [col.upper() for col in df.columns]
    
    from dotenv import load_dotenv
    conn = snowflake.connector.connect(
        user=os.getenv("YOUR_SNOWFLAKE_USERNAME"),
        password=os.getenv("YOUR_SNOWFLAKE_PASSWORD"),
        account=os.getenv("YOUR_ACCOUNT_IDENTIFIER"),
        warehouse=os.getenv("ACCESSIBILITY_WH"),
        database=os.getenv("CAMPUS_DB"),
        schema=os.getenv("ACCESSIBILITY_SCHEMA"),
    )

    write_pandas(conn, df, "UNIVERSITY_ACCESSIBILITY")
    conn.close()
    print("Scraped and uploaded directly to Snowflake!")
    print(f"\n[3/3] Completed! File saved as: {output_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape university accessibility symbols from AccessAble.")
    parser.add_argument(
        "--uni", 
        type=str, 
        default="imperial-college-london",
        help="AccessAble organization slug or shortcut (e.g., 'imperial-college-london', 'university-of-oxford', 'oxford', 'ucl')"
    )
    args = parser.parse_args()

    # Map shortcut if provided, otherwise use verbatim slug
    slug = KNOWN_UNIVERSITIES.get(args.uni.lower(), args.uni.strip().lower())
    asyncio.run(scrape_university(slug))