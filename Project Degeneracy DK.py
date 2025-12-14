from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd

def draftkings_scraper(sport = "basketball", league = "nba"):
    browser = webdriver.Chrome()
    browser.maximize_window()
    link = f"https://sportsbook.draftkings.com/leagues/{sport}/{league}"
    browser.get(link)
    time.sleep(5)

    page_source = browser.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    browser.quit()

    market = soup.find_all("div", {"data-testid": "market-template", "class": "cb-market__template cb-market__template--2-columns"})

    market_data = []

    for events in market:

        found_team_elements = events.find_all("span", {"class": "cb-market__label-inner cb-market__label-inner--parlay"})
        if found_team_elements:
            teams = []
            for found_team_element in found_team_elements:
                team = found_team_element.text.strip()
                teams.append(team)
            if len(teams) >= 2:
                event_name = f"{teams[0]} @ {teams[1]}"
            
        found_spread_total_moneyline_elements = events.find_all("button", {"data-testid": "component-builder-market-button"})
        if len(found_spread_total_moneyline_elements) < 6:
            continue
        try:
            # Spread
            market_data.append({
                "event_name": event_name,
                "market_type": "spread",
                "selection": teams[0] + " "+ found_spread_total_moneyline_elements[0].find("span", {"class": "cb-market__button-points"}).text.strip(),
                "odds": found_spread_total_moneyline_elements[0].find("span", {"class": "cb-market__button-odds"}).text.strip(),
                "sportbook": "DraftKings"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "spread",
                "selection": teams[1] + " " + found_spread_total_moneyline_elements[3].find("span", {"class": "cb-market__button-points"}).text.strip(),
                "odds": found_spread_total_moneyline_elements[3].find("span", {"class": "cb-market__button-odds"}).text.strip(),
                "sportbook": "DraftKings"
            })
            # Total
            market_data.append({
                "event_name": event_name,
                "market_type": "total",
                "selection": "Over" + " " + found_spread_total_moneyline_elements[1].find("span", {"class": "cb-market__button-points"}).text.strip(),
                "odds": found_spread_total_moneyline_elements[1].find("span", {"class": "cb-market__button-odds"}).text.strip(),
                "sportbook": "DraftKings"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "total",
                "selection": "Under" + " " + found_spread_total_moneyline_elements[4].find("span", {"class": "cb-market__button-points"}).text.strip(),
                "odds": found_spread_total_moneyline_elements[4].find("span", {"class": "cb-market__button-odds"}).text.strip(),
                "sportbook": "DraftKings"
            })
            # Moneyline
            market_data.append({
                "event_name": event_name,
                "market_type": "moneyline",
                "selection": teams[0],
                "odds": found_spread_total_moneyline_elements[2].find("span", {"class": "cb-market__button-odds"}).text.strip(),
                "sportbook": "DraftKings"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "moneyline",
                "selection": teams[1],
                "odds": found_spread_total_moneyline_elements[5].find("span", {"class": "cb-market__button-odds"}).text.strip(),
                "sportbook": "DraftKings"
            })
        except IndexError:
            continue

    df = pd.DataFrame(market_data)
    print(df)

draftkings_scraper()
