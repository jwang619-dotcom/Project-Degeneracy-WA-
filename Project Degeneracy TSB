from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd

def tsb_scraper(sport = "basketball", league = "nba"):
    browser = webdriver.Chrome()
    browser.maximize_window()
    link = f"https://sportsbook.thescore.bet/sport/{sport}/organization/united-states/competition/{league}#lines"
    browser.get(link)
    time.sleep(5)

    xp_close_button = f"//button[@aria-label='Close']"
    try:
        close_button = browser.find_element(By.XPATH, xp_close_button)
        close_button.click()
        time.sleep(2)
    except:
        pass

    page_source = browser.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    browser.quit()

    market = soup.find_all("div", {"class": "relative flex flex-col gap-2"})

    market_data = []    

    for events in market:

        found_team_elements = events.find_all("div", {"class": "text-style-s-medium text-primary text-cosmetic-gradient-stroke"})
        if found_team_elements:
            teams = []
            for found_team_element in found_team_elements:
                team = found_team_element.text.strip()
                teams.append(team)
                if len(teams) >= 2:
                    event_name = f"{teams[0]} @ {teams[1]}"
                    print(event_name)

        found_spread_total_moneyline_elements = events.find_all("button", {"aria-hidden": "false"})
        if len(found_spread_total_moneyline_elements) < 6:
            continue
        try:
            # Spread
            market_data.append({
                "event_name": event_name,
                "market_type": "spread",
                "selection": teams[0] + " " + found_spread_total_moneyline_elements[0].find("span", {"class": "text-selector-label-deselected group-data-[selected=true]:text-selector-label-selected [&]:group-disabled:text-disabled"}).text.strip(),
                "odds": found_spread_total_moneyline_elements[0].find("span", {"class": "text-style-xs-bold text-selector-deselected group-data-[selected=true]:text-selector-selected [&]:group-disabled:text-disabled -mt-ao-025"}).text.strip(),
                "sportbook": "TheScoreBet"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "spread",
                "selection": teams[1] + " " + found_spread_total_moneyline_elements[3].find("span", {"class": "text-selector-label-deselected group-data-[selected=true]:text-selector-label-selected [&]:group-disabled:text-disabled"}).text.strip(),
                "odds": found_spread_total_moneyline_elements[3].find("span", {"class": "text-style-xs-bold text-selector-deselected group-data-[selected=true]:text-selector-selected [&]:group-disabled:text-disabled -mt-ao-025"}).text.strip(),
                "sportbook": "TheScoreBet"
            })
            # Total
            market_data.append({
                "event_name": event_name,
                "market_type": "total",
                "selection": "Over" + " " + found_spread_total_moneyline_elements[1].find("span", {"class": "text-selector-label-deselected group-data-[selected=true]:text-selector-label-selected [&]:group-disabled:text-disabled"}).text.lstrip("O "),
                "odds": found_spread_total_moneyline_elements[1].find("span", {"class": "text-style-xs-bold text-selector-deselected group-data-[selected=true]:text-selector-selected [&]:group-disabled:text-disabled -mt-ao-025"}).text.strip(),
                "sportbook": "TheScoreBet"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "total",
                "selection": "Under" + " " + found_spread_total_moneyline_elements[4].find("span", {"class": "text-selector-label-deselected group-data-[selected=true]:text-selector-label-selected [&]:group-disabled:text-disabled"}).text.lstrip("U "),
                "odds": found_spread_total_moneyline_elements[4].find("span", {"class": "text-style-xs-bold text-selector-deselected group-data-[selected=true]:text-selector-selected [&]:group-disabled:text-disabled -mt-ao-025"}).text.strip(),
                "sportbook": "TheScoreBet"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "moneyline",
                "selection": teams[0],
                "odds": found_spread_total_moneyline_elements[2].find("span", {"class": "text-style-xs-bold text-selector-deselected group-data-[selected=true]:text-selector-selected [&]:group-disabled:text-disabled"}).text.strip(),
                "sportbook": "TheScoreBet"
            })
            market_data.append({
                "event_name": event_name,
                "market_type": "moneyline",
                "selection": teams[1],
                "odds": found_spread_total_moneyline_elements[5].find("span", {"class": "text-style-xs-bold text-selector-deselected group-data-[selected=true]:text-selector-selected [&]:group-disabled:text-disabled"}).text.strip(),
                "sportbook": "TheScoreBet"
            })
        except IndexError:
            continue
    
    df = pd.DataFrame(market_data)
    print(df)

tsb_scraper()