from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd

def standardize_team_name_CZR(team):
    team_name_mapping = {
        "Cleveland Cavaliers": "CLE Cavaliers",
        "Chicago Bulls": "CHI Bulls",
        "Memphis Grizzlies": "MEM Grizzlies",
        "Minnesota Timberwolves": "MIN Timberwolves",
        "New York Knicks": "NY Knicks",
        "Indiana Pacers": "IND Pacers",
        "Atlanta Hawks": "ATL Hawks",
        "Charlotte Hornets": "CHA Hornets",
        "Miami Heat": "MIA Heat",
        "Brooklyn Nets": "BKN Nets",
        "Toronto Raptors": "TOR Raptors",
        "Milwaukee Bucks": "MIL Bucks",
        "Washington Wizards": "WAS Wizards",
        "San Antonio Spurs": "SA Spurs",
        "Houston Rockets": "HOU Rockets",
        "New Orleans Pelicans": "NO Pelicans",
        "Los Angeles Clippers": "LA Clippers",
        "Oklahoma City Thunder": "OKC Thunder",
        "Detroit Pistons": "DET Pistons",
        "Dallas Mavericks": "DAL Mavericks",
        "Orlando Magic": "ORL Magic",
        "Denver Nuggets": "DEN Nuggets",
        "Los Angeles Lakers": "LA Lakers",
        "Utah Jazz": "UTA Jazz",
        "Golden State Warriors": "GS Warriors",
        "Phoenix Suns": "PHO Suns",
        "Sacramento Kings": "SAC Kings",
        "Portland Trail Blazers": "POR Trail Blazers"
    }
    return team_name_mapping.get(team, team)

def czr_scraper(sport = "basketball"):
    browser = webdriver.Chrome()
    browser.maximize_window()

    # Remove webdriver property
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })

    link = f"https://sportsbook.caesars.com/us/ny/bet/{sport}"
    browser.get(link)
    time.sleep(3)

    browser.execute_script("""
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    """)
    time.sleep(3)

    page_source = browser.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    browser.quit()

    # Find all EventCard containers
    market = soup.find_all("div", class_="EventCard")

    market_data = []

    for events in market:
        try:
            # Find the two team rows (Cleveland Cavaliers and Chicago Bulls in the example)
            team_rows = events.find_all("div", attrs={"data-filter-group": True})

            if len(team_rows) < 2:
                continue

            # Extract team names
            away_team_elem = team_rows[0].find("div", class_="cui__competitor_wrapper")
            home_team_elem = team_rows[1].find("div", class_="cui__competitor_wrapper")

            if not away_team_elem or not home_team_elem:
                continue

            # Get full team names from the longest span (hidden @[240px]:cui-block)
            away_team_spans = away_team_elem.find_all("span", class_=lambda x: x and "heading-md" in x)
            home_team_spans = home_team_elem.find_all("span", class_=lambda x: x and "heading-md" in x)

            away_team = away_team_spans[-1].text.strip() if away_team_spans else "Unknown"
            away_team = standardize_team_name_CZR(away_team)
            home_team = home_team_spans[-1].text.strip() if home_team_spans else "Unknown"
            home_team = standardize_team_name_CZR(home_team)

            event_name = f"{away_team} @ {home_team}"

            # Extract odds for away team (first row)
            away_buttons = team_rows[0].find_all("button", attrs={"data-cy": "market-button-btn"})
            # Extract odds for home team (second row)
            home_buttons = team_rows[1].find_all("button", attrs={"data-cy": "market-button-btn"})

            if len(away_buttons) < 3 or len(home_buttons) < 3:
                continue

            # Away team data (Spread, Moneyline, Total Over)
            away_spread_line = away_buttons[0].find("span", class_="cui__market-button-line")
            away_spread_odds = away_buttons[0].find("span", attrs={"data-cy": "market-button-odds"})
            away_ml_odds = away_buttons[1].find("span", attrs={"data-cy": "market-button-odds"})
            away_total_line = away_buttons[2].find("span", class_="cui__market-button-line")
            away_total_odds = away_buttons[2].find("span", attrs={"data-cy": "market-button-odds"})

            # Home team data (Spread, Moneyline, Total Under)
            home_spread_line = home_buttons[0].find("span", class_="cui__market-button-line")
            home_spread_odds = home_buttons[0].find("span", attrs={"data-cy": "market-button-odds"})
            home_ml_odds = home_buttons[1].find("span", attrs={"data-cy": "market-button-odds"})
            home_total_line = home_buttons[2].find("span", class_="cui__market-button-line")
            home_total_odds = home_buttons[2].find("span", attrs={"data-cy": "market-button-odds"})

            market_data.append({
                "event_name": event_name,
                "market_type": "spread",
                "selection": f"{away_team} {away_spread_line.text.strip()}",
                "odds": away_spread_odds.text.strip(),
                "sportbook": "Caesars"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "spread",
                "selection": f"{home_team} {home_spread_line.text.strip()}",
                "odds": home_spread_odds.text.strip(),
                "sportbook": "Caesars"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "total",
                "selection": f"Over {away_total_line.text.strip()}",
                "odds": away_total_odds.text.strip(),
                "sportbook": "Caesars"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "total",
                "selection": f"Under {home_total_line.text.strip()}",
                "odds": home_total_odds.text.strip(),
                "sportbook": "Caesars"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "moneyline",
                "selection": away_team,
                "odds": away_ml_odds.text.strip(),
                "sportbook": "Caesars"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "moneyline",
                "selection": home_team,
                "odds": home_ml_odds.text.strip(),
                "sportbook": "Caesars"
            })
        except IndexError:
            continue

    # Create Dataframe
    df = pd.DataFrame(market_data)
    print(df)

czr_scraper()
