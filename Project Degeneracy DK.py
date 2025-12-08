from selenium import webdriver
#from selenium.webdriver.common.by import By
#from selenium.common.exceptions import NoSuchElementException

import time

browser = webdriver.Chrome()
browser.maximize_window()
sport = "basketball"
league = "nba"
link = f"https://sportsbook.draftkings.com/leagues/{sport}/{league}"
browser.get(link)
time.sleep(5)

#xp_sport = (f"//h2[@data-testid='header-navigation' and text()='{sport}']")
#el = browser.find_element(By.XPATH, xp_sport)
#browser.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
#time.sleep(1)
#el.click()

#time.sleep(1)

#xp_league = (f"//span[@class='sportsbook-navitation-item-title-text' and text()='{league}']")
#el = browser.find_element(By.XPATH, xp_league)
#browser.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
#time.sleep(1)
#el.click()

#time.sleep(1)

# Use BS4 to parse the page source
from bs4 import BeautifulSoup
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
            #print(event_name)
        
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
        print("Not enough elements found for this event.")

#print(market_data)

# This code will convert my dictionary to a dataframe
import pandas as pd
df = pd.DataFrame(market_data)
print(df)
