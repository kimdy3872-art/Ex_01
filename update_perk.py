from __future__ import annotations

import argparse
import os
import re
import time
from datetime import date
from typing import Dict, List
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://owperks.com"
DEFAULT_LOCALE = "ko"
DEFAULT_OUTPUT = "overwatch_hero_perks.csv"

CATEGORY_TO_ROLE = {
    "tanks": "Tank",
    "damages": "Damage",
    "supports": "Support",
}

HERO_LINK_RE = re.compile(r"^https://owperks\.com/ko/(tanks|damages|supports)/([^/?#]+)$")


def create_driver(headless: bool = True) -> webdriver.Chrome:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            opts = Options()
            if headless:
                opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--disable-extensions")
            opts.add_argument("--remote-debugging-pipe")
            opts.add_argument("--window-size=1920,1080")
            return webdriver.Chrome(options=opts)
        except (SessionNotCreatedException, WebDriverException) as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(attempt * 2)
                continue
            break

    raise RuntimeError(f"Chrome 세션 생성 실패: {last_error}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape OW Perks hero perk name/image/pick-rate data."
    )
    parser.add_argument("--locale", default=DEFAULT_LOCALE, help="Site locale, default: ko")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output CSV path")
    parser.add_argument("--max-heroes", type=int, default=None, help="Limit hero count for quick test")
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser with visible window (default: headless)",
    )
    return parser.parse_args()


def normalize_url(href: str) -> str:
    if not href:
        return ""
    return urljoin(BASE_URL, href)


def extract_hero_links(driver: webdriver.Chrome, locale: str) -> List[str]:
    landing_url = f"{BASE_URL}/{locale}"
    driver.get(landing_url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
    time.sleep(1.5)

    hrefs = driver.execute_script(
        """
        const anchors = Array.from(document.querySelectorAll('a[href]'));
        return anchors.map(a => a.getAttribute('href')).filter(Boolean);
        """
    )

    links = set()
    for href in hrefs:
        absolute = normalize_url(href)
        match = HERO_LINK_RE.match(absolute)
        if match:
            links.add(absolute)

    ordered = sorted(links)
    print(f"Found {len(ordered)} hero pages from {landing_url}")
    return ordered


def extract_perk_slug(perk_image_url: str) -> str:
    if not perk_image_url:
        return ""

    parsed = urlparse(perk_image_url)
    query_path = parse_qs(parsed.query).get("url", [""])[0]
    if query_path:
        decoded = unquote(query_path)
        filename = os.path.basename(decoded)
    else:
        filename = os.path.basename(parsed.path)

    return os.path.splitext(filename)[0]


def extract_raw_perk_image_url(perk_image_url: str) -> str:
    if not perk_image_url:
        return ""

    parsed = urlparse(perk_image_url)
    query_path = parse_qs(parsed.query).get("url", [""])[0]
    if not query_path:
        return perk_image_url

    decoded = unquote(query_path)
    return urljoin(BASE_URL, decoded)


def scrape_hero_page(driver: webdriver.Chrome, hero_url: str) -> List[Dict]:
    driver.get(hero_url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".hero-card")))
    time.sleep(0.6)

    payload = driver.execute_script(
        """
        const card = document.querySelector('.hero-card');
        if (!card) {
            return { hero_name: '', rows: [] };
        }

        const heroName = (card.querySelector('h2')?.textContent || '').trim();
        const heroImage = card.querySelector('img[alt]')?.currentSrc || card.querySelector('img[alt]')?.src || '';

        const sections = Array.from(card.querySelectorAll('ul')).slice(0, 2);
        const sectionTypes = ['minor', 'major'];
        const rows = [];

        for (let i = 0; i < sections.length; i++) {
            const perkType = sectionTypes[i] || 'unknown';
            const items = Array.from(sections[i].querySelectorAll('li'));

            for (const li of items) {
                const text = (li.innerText || '').trim();
                const percentMatch = text.match(/(\d+(?:\.\d+)?)\s*%/);
                const pickRate = percentMatch ? Number(percentMatch[1]) : null;

                const img = li.querySelector('img');
                const perkImage = img?.currentSrc || img?.src || '';
                let perkName = (img?.alt || '').trim();

                if (!perkName) {
                    const candidate = li.querySelector('h2, h3, strong, [class*="font-bold"]');
                    perkName = (candidate?.textContent || '').trim();
                }

                if (!perkName) {
                    const lines = text
                        .split('\\n')
                        .map(v => v.trim())
                        .filter(Boolean)
                        .filter(v => !/^\d+(?:\.\d+)?%$/.test(v));
                    perkName = lines.length ? lines[0] : '';
                }

                rows.push({
                    perk_type: perkType,
                    perk_name: perkName,
                    pick_rate: pickRate,
                    perk_image_url: perkImage,
                });
            }
        }

        return {
            hero_name: heroName,
            hero_image_url: heroImage,
            rows,
        };
        """
    )

    category_match = re.match(r"^https://owperks\.com/ko/(tanks|damages|supports)/([^/?#]+)$", hero_url)
    if not category_match:
        return []

    category = category_match.group(1)
    hero_slug = category_match.group(2)
    role = CATEGORY_TO_ROLE.get(category, "Unknown")

    rows = []
    for row in payload.get("rows", []):
        perk_image_url = row.get("perk_image_url") or ""
        rows.append(
            {
                "hero": payload.get("hero_name") or hero_slug,
                "hero_slug": hero_slug,
                "role": role,
                "category": category,
                "perk_type": row.get("perk_type", ""),
                "perk_name": (row.get("perk_name") or "").strip(),
                "pick_rate": row.get("pick_rate"),
                "perk_slug": extract_perk_slug(perk_image_url),
                "perk_image_url": perk_image_url,
                "perk_image_raw_url": extract_raw_perk_image_url(perk_image_url),
                "hero_image_url": payload.get("hero_image_url", ""),
                "source_url": hero_url,
                "update_date": str(date.today()),
            }
        )

    return rows


def main() -> None:
    args = parse_args()
    started_at = time.time()

    driver = create_driver(headless=not args.headed)
    try:
        hero_links = extract_hero_links(driver, args.locale)
        if args.max_heroes is not None:
            hero_links = hero_links[: max(0, args.max_heroes)]

        if not hero_links:
            print("No hero links found. Nothing to scrape.")
            return

        all_rows: List[Dict] = []
        total = len(hero_links)
        for idx, hero_url in enumerate(hero_links, start=1):
            print(f"[{idx}/{total}] scraping {hero_url}")
            try:
                rows = scrape_hero_page(driver, hero_url)
                if rows:
                    all_rows.extend(rows)
                else:
                    print(f"  warning: no perk rows parsed: {hero_url}")
            except Exception as exc:
                print(f"  error: {hero_url} -> {exc}")

        if not all_rows:
            print("No perk rows scraped.")
            return

        df = pd.DataFrame(all_rows)
        df["pick_rate"] = pd.to_numeric(df["pick_rate"], errors="coerce")
        df = df.drop_duplicates(
            subset=["hero_slug", "perk_type", "perk_slug", "update_date"],
            keep="last",
        ).reset_index(drop=True)

        df = df.sort_values(
            by=["role", "hero", "perk_type", "pick_rate"],
            ascending=[True, True, True, False],
        ).reset_index(drop=True)

        columns = [
            "hero",
            "hero_slug",
            "role",
            "category",
            "perk_type",
            "perk_name",
            "pick_rate",
            "perk_slug",
            "perk_image_url",
            "perk_image_raw_url",
            "hero_image_url",
            "source_url",
            "update_date",
        ]
        df = df.reindex(columns=columns)
        df.to_csv(args.output, index=False, encoding="utf-8-sig")

        elapsed = int(time.time() - started_at)
        print(
            f"Done. Saved {len(df)} rows to {args.output} "
            f"(heroes={df['hero_slug'].nunique()}, elapsed={elapsed}s)"
        )
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
