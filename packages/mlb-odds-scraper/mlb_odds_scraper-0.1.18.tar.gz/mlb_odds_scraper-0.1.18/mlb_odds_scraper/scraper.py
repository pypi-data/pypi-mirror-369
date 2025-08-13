"""MLB Odds Scraper for retrieving odds data from OddsPortal."""

import pandas as pd
import datetime
import sys
from typing import Optional


def _safe_click(driver, by, selector) -> bool:
    try:
        el = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((by, selector))
        )
        try:
            el.click()
        except Exception:
            driver.execute_script("arguments[0].click();", el)
        return True
    except Exception:
        return False


def _dismiss_overlays(driver) -> None:
    """Attempt to close cookie banners and promotional modals if present.

    Safe to call repeatedly. No-ops if nothing is present.
    """
    # Try cookie buttons (accept first, then reject)
    if _safe_click(driver, By.ID, "onetrust-accept-btn-handler"):
        print("Closed cookie accept button")
    elif _safe_click(driver, By.ID, "onetrust-reject-all-handler"):
        print("Closed cookie reject button")

    # Try common close buttons on modals/popups
    close_xpaths = [
        "//button[contains(@aria-label,'Close') or contains(@title,'Close')]",
        "//button[normalize-space(text())='×' or normalize-space(text())='X']",
        "//div[contains(@class,'modal') or contains(@class,'popup') or contains(@id,'modal') or contains(@id,'popup')]//button[contains(@class,'close') or contains(@aria-label,'Close') or normalize-space(text())='×' or normalize-space(text())='X']",
        "//div[@role='dialog']//button[contains(@class,'close') or contains(@aria-label,'Close') or normalize-space(text())='×' or normalize-space(text())='X']",
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'close')]",
    ]
    for xp in close_xpaths:
        try:
            els = driver.find_elements(By.XPATH, xp)
            if els:
                try:
                    els[0].click()
                except Exception:
                    driver.execute_script("arguments[0].click();", els[0])
                print("Closed a modal via XPath")
                break
        except Exception:
            continue

    # As a last resort, hide obvious overlays so content is clickable/visible
    try:
        driver.execute_script(
            """
            (function(){
              var sel = "[class*='modal'],[class*='overlay'],[id*='modal'],[id*='overlay']";
              document.querySelectorAll(sel).forEach(function(n){
                n.style.setProperty('display','none','important');
                n.style.setProperty('visibility','hidden','important');
                n.style.setProperty('pointer-events','none','important');
              });
            })();
            """
        )
    except Exception:
        pass
from selenium import webdriver
from stealthenium import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import time
import statsapi

def scrape_page(year, page_num):
    """
    Scrape a single page of MLB odds data.
    
    Args:
        year (int): Year to scrape data for
        page_num (int): Page number to scrape
        
    Returns:
        list: List of dictionaries containing game data
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("start-maximized") 
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1400,6000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    
    stealth(driver,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform=("Linux x86_64" if sys.platform.startswith("linux") else "Win32"),
        webgl_vendor="Intel Inc.",
        renderer=("ANGLE (Intel(R) UHD Graphics)" if sys.platform.startswith("linux") else "Intel Iris OpenGL Engine"),
        fix_hairline=True,
    )
    
    games = []
    
    # For current year, use URL without year suffix
    current_year = datetime.datetime.now().year
    if year == current_year:
        url = f"https://www.oddsportal.com/baseball/usa/mlb/results/#/page/{page_num}/"
    else:
        url = f"https://www.oddsportal.com/baseball/usa/mlb-{year}/results/#/page/{page_num}/"
        
    print(f"Scraping {url}")
    
    try:
        driver.get(url)

        # Dismiss overlays/popups/cookies if present
        _dismiss_overlays(driver)
        
        # Wait for page to load
        time.sleep(2)
        
        # Try different selectors for event rows
        selectors = [
            "div.eventRow",
            "div[data-v-b8d70024].eventRow",
            "div[data-v-b8d70024][id][set]",
            "div.event__match",
            "div.table-main__tr",
            "div.result-table__row"
        ]
        
        events = []
        used_selector = None
        for selector in selectors:
            try:
                print(f"Trying selector: {selector}")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                events = driver.find_elements(By.CSS_SELECTOR, selector)
                if events:
                    print(f"Found {len(events)} events with selector: {selector}")
                    used_selector = selector
                    break
            except Exception as e:
                print(f"Selector {selector} failed: {str(e)}")
                _dismiss_overlays(driver)
        
        # If no events found with CSS selectors, try XPath
        if not events:
            try:
                print("Trying XPath selector")
                events = driver.find_elements(By.XPATH, "//div[contains(@class, 'event') and .//div[contains(@class, 'participant')]]")
                print(f"Found {len(events)} events with XPath selector")
            except Exception as e:
                print(f"XPath selector failed: {str(e)}")
        
        # Progressive scroll-and-refresh: keep scrolling until event count stable
        try:
            prev_height = -1
            last_count = 0
            stable_loops = 0
            for _ in range(15):
                # Re-capture events each loop
                try:
                    if used_selector:
                        events = driver.find_elements(By.CSS_SELECTOR, used_selector)
                    else:
                        # Try selectors in order each time
                        for sel in selectors:
                            events = driver.find_elements(By.CSS_SELECTOR, sel)
                            if events:
                                used_selector = sel
                                break
                        if not events:
                            events = driver.find_elements(By.XPATH, "//div[contains(@class, 'event') and .//div[contains(@class, 'participant')]]")
                except Exception:
                    events = []

                current_count = len(events)
                if current_count <= last_count:
                    stable_loops += 1
                else:
                    stable_loops = 0
                    last_count = current_count

                current_height = driver.execute_script("return document.body.scrollHeight")
                if current_height == prev_height and stable_loops >= 2:
                    break
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                prev_height = current_height

            # Final capture after scrolling
            if used_selector:
                events = driver.find_elements(By.CSS_SELECTOR, used_selector)
            elif not events:
                events = driver.find_elements(By.XPATH, "//div[contains(@class, 'event') and .//div[contains(@class, 'participant')]]")
        except Exception as e:
            print(f"Scrolling/reload events failed: {e}")
        
        print(f"Found {len(events)} events on page {page_num}")
        current_date = None
        
        # Find initial date
        date_selectors = [
            ".text-black-main",
            ".event__time",
            ".table-main__date",
            ".date"
        ]
        
        for event in events:
            for date_selector in date_selectors:
                try:
                    date_elements = event.find_elements(By.CSS_SELECTOR, date_selector)
                    for date_element in date_elements:
                        date_text = date_element.text
                        if len(date_text.split()) >= 2 and "Baseball" not in date_text:
                            if " - " in date_text:
                                current_date = date_text.split(' - ')[0].strip()
                            else:
                                current_date = date_text.strip()
                            break
                    if current_date:
                        break
                except:
                    continue
            if current_date:
                break
                
        # Process events
        seen = set()
        for event in events:
            try:
                # Try to get date for this event
                for date_selector in date_selectors:
                    try:
                        date_elements = event.find_elements(By.CSS_SELECTOR, date_selector)
                        for date_element in date_elements:
                            date_text = date_element.text
                            if len(date_text.split()) >= 2 and "Baseball" not in date_text:
                                if " - " in date_text:
                                    current_date = date_text.split(' - ')[0].strip()
                                else:
                                    current_date = date_text.strip()
                                break
                    except:
                        continue
                
                # Try different selectors for team names
                team_selectors = [
                    ".participant-name",
                    "p.participant-name",
                    ".event__participant",
                    ".table-main__participant",
                    ".participant"
                ]
                
                teams = []
                for team_selector in team_selectors:
                    try:
                        teams = event.find_elements(By.CSS_SELECTOR, team_selector)
                        if len(teams) >= 2:
                            break
                    except:
                        continue
                
                # Try different selectors for scores
                score_selectors = [
                    "div.text-gray-dark div.font-bold",
                    ".font-bold",
                    ".event__score",
                    ".table-main__score",
                    ".score"
                ]
                
                home_score = ''
                away_score = ''
                for score_selector in score_selectors:
                    try:
                        score_section = event.find_element(By.CSS_SELECTOR, score_selector)
                        score_text = score_section.text
                        if '–' in score_text:
                            scores = score_text.split('–')
                            home_score = scores[0].strip()
                            away_score = scores[1].strip()
                            break
                        elif ':' in score_text and score_text[0].isdigit():
                            scores = score_text.split(':')
                            home_score = scores[0].strip()
                            away_score = scores[1].strip()
                            break
                    except:
                        try:
                            score_elements = event.find_elements(By.CSS_SELECTOR, score_selector)
                            if len(score_elements) >= 2:
                                home_score = score_elements[0].text.strip()
                                away_score = score_elements[1].text.strip()
                                break
                        except:
                            continue
                    
                if len(teams) < 2:
                    continue

                # Try different selectors for time
                time_selectors = [
                    ".//p[contains(text(), ':')]",
                    ".//span[contains(text(), ':')]",
                    ".//div[contains(text(), ':') and string-length(.) <= 8]"
                ]
                
                game_time = None
                for time_selector in time_selectors:
                    try:
                        time_element = event.find_element(By.XPATH, time_selector)
                        time_text = time_element.text
                        if ':' in time_text and len(time_text) <= 8:
                            game_time = time_text
                            break
                    except:
                        continue
                
                # game_time is optional on results pages; do not drop the event solely due to missing time

                home_team = teams[0].text
                away_team = teams[1].text
                    
                # Try different selectors for odds
                odds_selectors = [
                    "[data-testid='add-to-coupon-button'] .height-content",
                    ".gradient-green-added-border",
                    ".event__odd",
                    ".table-main__odd",
                    ".odd"
                ]
                
                odds_elements = []
                for odds_selector in odds_selectors:
                    try:
                        odds_elements = event.find_elements(By.CSS_SELECTOR, odds_selector)
                        if len(odds_elements) >= 2:
                            break
                    except:
                        continue

                home_odds = ''
                away_odds = ''
                if len(odds_elements) >= 2:
                    home_odds = odds_elements[0].text
                    away_odds = odds_elements[1].text

                # Build game record if we have at least a date and both teams
                if all([current_date, away_team, home_team]):
                    # Deduplicate on key fields to stabilize counts
                    dedup_key = (current_date, home_team, away_team, home_score, away_score)
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)

                    game_data = {
                        'date': current_date,
                        'time': game_time if game_time else '',
                        'away_team': away_team,
                        'home_team': home_team,
                        'away_odds': away_odds,
                        'home_odds': home_odds,
                        'away_score': away_score,
                        'home_score': home_score
                    }
                    games.append(game_data)
                
            except Exception as e:
                print(f"Error processing event: {e}")
                continue
        
    except Exception as e:
        print(f"Error scraping page {page_num} for year {year}: {e}")
    finally:
        driver.quit()
        
    return games

def scrape_future_matches():
    """
    Scrape upcoming MLB matches from the main MLB page.
    
    Returns:
        list: List of dictionaries containing future game data
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("start-maximized") 
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1400,6000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    
    stealth(driver,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform=("Linux x86_64" if sys.platform.startswith("linux") else "Win32"),
        webgl_vendor="Intel Inc.",
        renderer=("ANGLE (Intel(R) UHD Graphics)" if sys.platform.startswith("linux") else "Intel Iris OpenGL Engine"),
        fix_hairline=True,
    )
    
    future_games = []
    url = "https://www.oddsportal.com/baseball/usa/mlb/"
    
    print(f"Scraping future matches from {url}")
    
    try:
        driver.get(url)
        
        # Handle cookie consent if it appears
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
            ).click()
            print("Clicked cookie reject button")
        except:
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Reject')]"))
                ).click()
                print("Clicked alternative cookie reject button")
            except:
                print("No cookie consent dialog found or couldn't be clicked")
        
        # Wait for page to load
        time.sleep(2)
        
        # Try different selectors for future events
        selectors = [
            "div.eventRow",
            "div[data-v-b8d70024].eventRow",
            "div.event__match",
            ".upcoming-event",
            "div.table-main__tr"
        ]
        
        events = []
        for selector in selectors:
            try:
                print(f"Trying selector for future events: {selector}")
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                events = driver.find_elements(By.CSS_SELECTOR, selector)
                if events:
                    print(f"Found {len(events)} future events with selector: {selector}")
                    break
            except Exception as e:
                print(f"Future selector {selector} failed: {str(e)}")
        
        # If no events found with CSS selectors, try XPath
        if not events:
            try:
                print("Trying XPath selector for future events")
                events = driver.find_elements(By.XPATH, "//div[contains(@class, 'event') and .//div[contains(@class, 'participant')]]")
                print(f"Found {len(events)} future events with XPath selector")
            except Exception as e:
                print(f"Future XPath selector failed: {str(e)}")
        
        # Progressive scroll for future page until stable
        try:
            prev_height = -1
            last_count = 0
            stable_loops = 0
            for _ in range(15):
                try:
                    # Re-capture each loop
                    for sel in selectors:
                        events = driver.find_elements(By.CSS_SELECTOR, sel)
                        if events:
                            break
                    if not events:
                        events = driver.find_elements(By.XPATH, "//div[contains(@class, 'event') and .//div[contains(@class, 'participant')]]")
                except Exception:
                    events = []

                current_count = len(events)
                if current_count <= last_count:
                    stable_loops += 1
                else:
                    stable_loops = 0
                    last_count = current_count

                current_height = driver.execute_script("return document.body.scrollHeight")
                if current_height == prev_height and stable_loops >= 2:
                    break
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                prev_height = current_height
        except Exception as e:
            print(f"Scrolling future page failed: {e}")
        
        # Process future events
        current_date = None
        seen = set()
        for event in events:
            try:
                # Try to get date for this event
                date_selectors = [
                    ".text-black-main",
                    ".event__time",
                    ".table-main__date",
                    ".date",
                    ".event-time"
                ]
                
                for date_selector in date_selectors:
                    try:
                        date_elements = event.find_elements(By.CSS_SELECTOR, date_selector)
                        for date_element in date_elements:
                            date_text = date_element.text
                            # For future events, date might be formatted differently
                            if len(date_text.split()) >= 2 and "Baseball" not in date_text:
                                current_date = date_text.strip()
                                break
                        if current_date:
                            break
                    except:
                        continue
                
                # Try different selectors for team names
                team_selectors = [
                    ".participant-name",
                    "p.participant-name",
                    ".event__participant",
                    ".table-main__participant",
                    ".participant"
                ]
                
                teams = []
                for team_selector in team_selectors:
                    try:
                        teams = event.find_elements(By.CSS_SELECTOR, team_selector)
                        if len(teams) >= 2:
                            break
                    except:
                        continue
                
                if len(teams) < 2:
                    continue

                # Try different selectors for time
                time_selectors = [
                    ".//p[contains(text(), ':')]",
                    ".//span[contains(text(), ':')]",
                    ".//div[contains(text(), ':') and string-length(.) <= 8]",
                    ".event-time"
                ]
                
                game_time = None
                for time_selector in time_selectors:
                    try:
                        time_element = event.find_element(By.XPATH, time_selector)
                        time_text = time_element.text
                        if ':' in time_text and len(time_text) <= 8:
                            game_time = time_text
                            break
                    except:
                        continue
                
                if not game_time:
                    # Try to extract time from date if it's combined
                    if current_date and ':' in current_date:
                        parts = current_date.split()
                        for part in parts:
                            if ':' in part and len(part) <= 8:
                                game_time = part
                                # Remove time from date
                                current_date = ' '.join([p for p in parts if p != part])
                                break
                # For future games, allow missing time as well

                home_team = teams[0].text
                away_team = teams[1].text
                    
                # Try different selectors for odds
                odds_selectors = [
                    "[data-testid='add-to-coupon-button'] .height-content",
                    ".gradient-green-added-border",
                    ".event__odd",
                    ".table-main__odd",
                    ".odd"
                ]
                
                odds_elements = []
                for odds_selector in odds_selectors:
                    try:
                        odds_elements = event.find_elements(By.CSS_SELECTOR, odds_selector)
                        if len(odds_elements) >= 2:
                            break
                    except:
                        continue

                home_odds = ''
                away_odds = ''
                if len(odds_elements) >= 2:
                    home_odds = odds_elements[0].text
                    away_odds = odds_elements[1].text

                if all([current_date, away_team, home_team]):
                    # For future games, scores are not available
                    dedup_key = (current_date, home_team, away_team)
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)
                    game_data = {
                        'date': current_date,
                        'time': game_time if game_time else '',
                        'away_team': away_team,
                        'home_team': home_team,
                        'away_odds': away_odds,
                        'home_odds': home_odds,
                        'away_score': '',  # Empty for future games
                        'home_score': '',  # Empty for future games
                    }
                    future_games.append(game_data)
                
            except Exception as e:
                print(f"Error processing future event: {e}")
                continue
        
    except Exception as e:
        print(f"Error scraping future matches: {e}")
    finally:
        driver.quit()
        
    print(f"Total future games collected: {len(future_games)}")
    return future_games

def scrape_oddsportal_mlb(year, max_pages=None, include_future=True):
    """
    Scrape MLB odds data for a specific year.
    
    Args:
        year (int): Year to scrape data for
        max_pages (int, optional): Maximum number of pages to scrape
        include_future (bool, optional): Whether to include future matches
        
    Returns:
        list: List of dictionaries containing game data
    """
    # Get total pages
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    
    total_pages = 1
    try:
        # For current year, use URL without year suffix
        current_year = datetime.datetime.now().year
        if year == current_year:
            url = f"https://www.oddsportal.com/baseball/usa/mlb/results/#/page/1/"
        else:
            url = f"https://www.oddsportal.com/baseball/usa/mlb-{year}/results/#/page/1/"
            
        print(f"Getting pagination info from {url}")
        driver.get(url)
        
        # Handle cookie consent if it appears
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
            ).click()
        except:
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Reject')]"))
                ).click()
            except:
                print("No cookie consent dialog found or couldn't be clicked")
        
        # Wait for page to load - reduced from 5 to 2 seconds
        time.sleep(2)
        
        # Try different selectors for pagination
        pagination_selectors = [
            "div.pagination",
            "ul.pagination",
            ".pagination-container",
            ".pagination-wrapper"
        ]
        
        for selector in pagination_selectors:
            try:
                pagination = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                page_links = pagination.find_elements(By.CSS_SELECTOR, "a.pagination-link, a[data-number]")
                
                if page_links:
                    page_numbers = []
                    for link in page_links:
                        data_number = link.get_attribute('data-number')
                        if data_number and data_number.isdigit():
                            page_numbers.append(int(data_number))
                        elif link.text and link.text.isdigit():
                            page_numbers.append(int(link.text))
                    
                    if page_numbers:
                        total_pages = max(page_numbers)
                        break
            except:
                continue
        
        # If pagination not found, check if there's any indication of multiple pages
        if total_pages == 1:
            try:
                next_page = driver.find_element(By.XPATH, "//a[contains(text(), 'Next') or contains(@class, 'next')]")
                if next_page:
                    total_pages = 2  # At least 2 pages
            except:
                pass
    except Exception as e:
        print(f"Error determining total pages for year {year}: {e}")
    finally:
        driver.quit()
    
    if max_pages:
        total_pages = min(max_pages, total_pages)
    
    print(f"Will scrape {total_pages} pages")
    
    # Scrape pages concurrently - increase workers from 5 to 8
    all_games = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(scrape_page, year, page) for page in range(1, total_pages + 1)]
        for future in futures:
            all_games.extend(future.result())
    
    # Add future games if requested and if we're scraping the current year
    if include_future and year == datetime.datetime.now().year:
        future_games = scrape_future_matches()
        if future_games:
            all_games.extend(future_games)
            
    print(f"Total games collected: {len(all_games)}")
    return all_games

def scrape_oddsportal_mlb_years(start_year=2006, end_year=2025, max_pages=None, include_future=True):
    """
    Scrape MLB odds data for multiple years.
    
    Args:
        start_year (int): First year to scrape (inclusive)
        end_year (int): Last year to scrape (exclusive)
        max_pages (int, optional): Maximum number of pages to scrape per year
        include_future (bool, optional): Whether to include future matches
        
    Returns:
        pd.DataFrame: DataFrame containing all scraped games
    """
    all_games = []
    for year in range(start_year, end_year):
        print(f"\nScraping year {year}...")
        games = scrape_oddsportal_mlb(year, max_pages, include_future)
        
        if games:
            all_games.extend(games)
        else:
            print(f"No games found for year {year}")
        
    return pd.DataFrame(all_games) if all_games else pd.DataFrame()

def process_game_data(df):
    """
    Process raw MLB game data by cleaning and transforming fields.
    
    Args:
        df (pd.DataFrame): Raw dataframe containing MLB game data
        
    Returns:
        pd.DataFrame: Processed dataframe with team IDs in 'home_team' and 'away_team' columns.
    """
    if df.empty:
        print("DataFrame is empty, not processing")
        return df
    
    processed_df = df.copy()
    
    # Temporarily mark future games for processing but don't include in final output
    if 'is_future' not in processed_df.columns:
        # Identify future games by empty scores
        has_score = processed_df['home_score'].astype(str).str.strip() != ''
        processed_df['is_future'] = ~has_score
    
    # Convert date to datetime with appropriate handling
    try:
        # Get current date for reference
        today = pd.Timestamp.now().normalize()
        current_year = today.year
        
        # Process all dates - both historical and future
        for idx, row in processed_df.iterrows():
            date_str = row['date']
            time_str = row['time']
            is_future = row['is_future']
            
            try:
                game_date = None
                
                # Handle "Today", "Tomorrow", "Yesterday" format
                if 'Today' in date_str:
                    game_date = today
                elif 'Tomorrow' in date_str:
                    game_date = today + pd.Timedelta(days=1)
                elif 'Yesterday' in date_str:
                    game_date = today - pd.Timedelta(days=1)
                
                # Handle standard date format like "19 Mar 2025"
                elif len(date_str.split()) == 3 and date_str.split()[2].isdigit():
                    day = int(date_str.split()[0])
                    month_abbr = date_str.split()[1]
                    year = int(date_str.split()[2])
                    
                    month_map = {
                        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                    }
                    month = month_map.get(month_abbr, 1)
                    game_date = pd.Timestamp(year, month, day)
                
                # Handle date formats like "Thursday, 27 Mar" or "Friday, 28 Mar" 
                elif ',' in date_str and len(date_str.split(',')) >= 2:
                    date_parts = date_str.split(',')
                    day_month = date_parts[1].strip()
                    
                    # Extract day and month
                    try:
                        day = int(day_month.split()[0])
                        month_abbr = day_month.split()[1]
                        month_map = {
                            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                            'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                            'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                        }
                        month = month_map.get(month_abbr, 1)
                        year = current_year
                        
                        # For historical games (with scores), we want to use the exact date
                        # For future games, we need to check if the date might be next year
                        if is_future and pd.Timestamp(year, month, day) < today - pd.Timedelta(days=7):
                            # For future games with dates that seem past, they're likely for next year
                            year += 1
                            
                        game_date = pd.Timestamp(year, month, day)
                    except Exception as e:
                        print(f"Error parsing day/month from '{day_month}': {e}")
                        # Try standard parsing as fallback
                        try:
                            game_date = pd.to_datetime(date_str)
                        except:
                            game_date = today
                # Standard date format - try direct parsing
                else:
                    try:
                        game_date = pd.to_datetime(date_str)
                    except:
                        # Last resort - use today's date
                        print(f"Could not parse date '{date_str}', using today")
                        game_date = today
                
                # Parse time and create datetime
                if game_date is not None:
                    try:
                        if ':' in time_str:
                            hour, minute = map(int, time_str.split(':'))
                            game_datetime = game_date.replace(hour=hour, minute=minute)
                        else:
                            game_datetime = game_date
                        
                        # Update the dataframe
                        processed_df.loc[idx, 'game_date'] = game_date
                        processed_df.loc[idx, 'game_datetime'] = game_datetime
                    except Exception as e:
                        print(f"Error processing time '{time_str}': {e}")
                        processed_df.loc[idx, 'game_date'] = game_date
                        processed_df.loc[idx, 'game_datetime'] = game_date
            except Exception as e:
                print(f"Error processing date/time for row {idx}: {e}")
                # Fallback to original string parsing
                try:
                    processed_df.loc[idx, 'game_date'] = pd.to_datetime(date_str)
                    processed_df.loc[idx, 'game_datetime'] = pd.to_datetime(date_str + ' ' + time_str)
                except:
                    processed_df.loc[idx, 'game_date'] = date_str
                    processed_df.loc[idx, 'game_datetime'] = date_str + ' ' + time_str
    except Exception as e:
        print(f"Error in date processing: {e}")
        processed_df['game_date'] = processed_df['date']
        processed_df['game_datetime'] = processed_df['date'] + ' ' + processed_df['time']
    
    # Drop rows containing All Star Game matchups
    processed_df = processed_df[~(processed_df['away_team'].isin(['American League', 'National League']) | 
                                processed_df['home_team'].isin(['American League', 'National League']))]
    
    # Clean team names and store original abbreviations
    processed_df['home_team_abbr'] = processed_df['home_team'].str.replace('St.Louis', 'St. Louis')
    processed_df['away_team_abbr'] = processed_df['away_team'].str.replace('St.Louis', 'St. Louis')
    
    # Get unique team names
    all_teams = processed_df['away_team_abbr'].tolist() + processed_df['home_team_abbr'].tolist()
    teams = []
    for team in all_teams:
        if team not in teams and team is not None:
            teams.append(team)

    # Create mapping of team names to IDs
    team_mapping = {}
    for team in teams:
        try:
            team_info = statsapi.lookup_team(team)
            if team_info:
                team_mapping[team] = team_info[0]['id']
            else:
                print(f"Could not find ID for team: {team}")
                team_mapping[team] = None
        except Exception as e:
            print(f"Error looking up team {team}: {e}")
            team_mapping[team] = None

    # Map team names to IDs in new columns
    processed_df['home_team_id_mapped'] = processed_df['home_team_abbr'].map(team_mapping)
    processed_df['away_team_id_mapped'] = processed_df['away_team_abbr'].map(team_mapping)

    # Overwrite original team columns with IDs and rename
    processed_df['home_team'] = processed_df['home_team_id_mapped']
    processed_df['away_team'] = processed_df['away_team_id_mapped']
    
    # Drop the temporary ID columns
    processed_df.drop(columns=['home_team_id_mapped', 'away_team_id_mapped'], inplace=True)

    # Convert odds columns - replace + with empty string and convert to numeric
    try:
        processed_df['away_odds'] = pd.to_numeric(processed_df['away_odds'].str.replace('+', ''), errors='coerce')
        processed_df['home_odds'] = pd.to_numeric(processed_df['home_odds'].str.replace('+', ''), errors='coerce')
    except Exception as e:
        print(f"Error converting odds: {e}")

    # Convert score columns to numeric - only for historical games
    try:
        historical_mask = ~processed_df['is_future']
        if historical_mask.any():
            processed_df.loc[historical_mask, 'away_score'] = pd.to_numeric(processed_df.loc[historical_mask, 'away_score'], errors='coerce')
            processed_df.loc[historical_mask, 'home_score'] = pd.to_numeric(processed_df.loc[historical_mask, 'home_score'], errors='coerce')
    except Exception as e:
        print(f"Error converting scores: {e}")
    
    # Drop rows with missing scores if they exist - but only for historical games
    if 'away_score' in processed_df.columns and 'home_score' in processed_df.columns:
        historical_mask = ~processed_df['is_future']
        if historical_mask.any():
            # Only filter out missing scores for historical games
            missing_scores = processed_df.loc[historical_mask, ['home_score', 'away_score']].isna().any(axis=1)
            drop_indices = processed_df.loc[historical_mask][missing_scores].index
            processed_df = processed_df.drop(drop_indices)
    
    # Remove is_future column as it's not needed in output
    if 'is_future' in processed_df.columns:
        processed_df = processed_df.drop(columns=['is_future'])
    
    # Select final columns - now home_team and away_team contain IDs
    final_columns = ['game_date', 'game_datetime', 'home_team', 'away_team', 
                     'home_odds', 'away_odds', 'home_score', 'away_score', 
                     'home_team_abbr', 'away_team_abbr']
    
    # Only keep columns that exist
    final_columns = [col for col in final_columns if col in processed_df.columns]
    processed_df = processed_df[final_columns]
    
    return processed_df 

def clean_game_data(cleaned_schedule, processed_odds, tz='US/Eastern', tolerance_hrs=12):
    import pandas as pd
    import numpy as np

    schedule = cleaned_schedule.copy()
    odds = processed_odds.replace('', np.nan).copy()

    schedule.rename(columns={'home_team_score': 'home_score', 'away_team_score': 'away_score'}, inplace=True)
    schedule['game_datetime'] = pd.to_datetime(schedule['game_datetime'], utc=True).dt.tz_convert(tz).dt.tz_localize(None).astype('datetime64[us]')
    schedule['home_score'] = schedule['home_score'].astype(int, errors='ignore')
    schedule['away_score'] = schedule['away_score'].astype(int, errors='ignore')
    odds['home_score'] = odds['home_score'].astype(int, errors='ignore')
    odds['away_score'] = odds['away_score'].astype(int, errors='ignore')
    schedule = schedule.sort_values('game_datetime')

    odds['game_datetime'] = pd.to_datetime(odds['game_datetime']).dt.tz_localize(tz).dt.tz_localize(None).astype('datetime64[us]')
    odds = odds.sort_values('game_datetime')

    merged = pd.merge_asof(
        schedule.drop(['game_date', 'home_score', 'away_score'], axis=1),
        odds,
        on='game_datetime',
        by=['home_team', 'away_team'],
        direction='nearest',
        tolerance=pd.Timedelta(f'{tolerance_hrs}hr')
    )
    merged.dropna(subset=['home_odds', 'away_odds'], inplace=True) 
    merged['game_datetime'] = merged['game_datetime'].dt.tz_localize(tz)
    return merged

