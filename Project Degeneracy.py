from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import requests

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

    return pd.DataFrame(market_data)

def standardize_team_name_TSB(team):
    team_name_mapping = {
        "PHX Suns": "PHO Suns",
        "WSH Wizards": "WAS Wizards"
    }
    return team_name_mapping.get(team, team)

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
                team = standardize_team_name_TSB(team)
                if team:
                    teams.append(team)
            if len(teams) >= 2:
                event_name = f"{teams[0]} @ {teams[1]}"

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

    return pd.DataFrame(market_data)

# ChatGPT suggested code to combine both scrapers using threading for concurrency
def market_scrapers():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_dk = executor.submit(draftkings_scraper)
        future_tsb = executor.submit(tsb_scraper)

        df_draftkings = future_dk.result()
        df_thescorebet = future_tsb.result()

    df_market = pd.concat([df_draftkings, df_thescorebet], ignore_index=True)
    return df_market

# Find opposite market selection
def market_opposites(row):
    if row["market_type"] == "spread":
        team1, team2 = row["event_name"].split(" @ ")
        selected_team = row["selection"].rsplit(" ", 1)[0]
        if selected_team == team1:
            spread_value = row["selection"].rsplit(" ", 1)[1]
            if spread_value.startswith("+"):
                spread_value = spread_value.replace("+", "-")
            elif spread_value.startswith("-"):
                spread_value = spread_value.replace("-", "+")
            return team2 + " " + spread_value
        elif selected_team == team2:
            spread_value = row["selection"].rsplit(" ", 1)[1]
            if spread_value.startswith("+"):
                spread_value = spread_value.replace("+", "-")
            elif spread_value.startswith("-"):
                spread_value = spread_value.replace("-", "+")
            return team1 + " " + spread_value

    elif row["market_type"] == "total":
        if "Over" in row["selection"]:
            return "Under" + " " + row["selection"].rsplit(" ", 1)[1]
        elif "Under" in row["selection"]:
            return "Over" + " " + row["selection"].rsplit(" ", 1)[1]

    elif row["market_type"] == "moneyline":
        team1, team2 = row["event_name"].split(" @ ")
        selected_team = row["selection"]
        if selected_team == team1:
            return team2
        elif selected_team == team2:
            return team1

def cnm_api(leg1_odds, leg2_odds, final_odds):
    url = "http://api.crazyninjaodds.com/api/devigger/v1/sportsbook_devigger.aspx?api=open"
    
    leg1_odds_str = ",".join(str(x).replace("−", "-") for x in leg1_odds)
    leg2_odds_str = ",".join(str(x).replace("−", "-") for x in leg2_odds)
    final_odds_str = str(final_odds).replace("−", "-")

    params = {
        "LegOdds": f"AVG({leg1_odds_str})/AVG({leg2_odds_str})",
        "FinalOdds": f"{final_odds_str}",
        "DevigMethod": 2, 
        "Args": "ev_p,fo_o"
        }

    response = requests.get(url, params=params)
    response_text = response.json()
    fv = response_text["Final"]["FairValue_Odds"]
    ev = round(((response_text["Final"]["EV_Percentage"] * 100)), 1)
    return {"fv": fv, "ev%": ev}

def market_spreadsheet():
    df = market_scrapers()
    # Replace "Even" with +100 in odds column
    df.loc[df['odds'].str.contains("even", case=False, na=False), 'odds'] = "+100"

    all_odds_keys = ['event_name', 'market_type', 'selection']
    df['books'] = df.groupby(all_odds_keys)['odds'].transform('count')

    # Creates a "lookup" table and then merges it back to the original dataframe with a left join based on the keys
    all_odds_map = (df.groupby(all_odds_keys)['odds'].apply(lambda x: list(x.astype(str))))
    df = df.merge(
        all_odds_map.rename('all_odds'), 
        on=all_odds_keys, 
        how='left'
    )

    # Adds opposite market selection column to main dataframe
    df['opposite_market_selection'] = df.apply(market_opposites, axis=1)

    # Creates a "lookup" table for opposite market odds and then merges it back to the original dataframe with a left join based on the keys
    all_opposite_odds_map = (df.groupby(all_odds_keys)['odds'].apply(lambda x: list(x.astype(str))))
    df = df.merge(
        all_opposite_odds_map.rename('all_opposite_market_odds'), 
        left_on=["event_name", "market_type", "opposite_market_selection"],
        right_index=True,
        how='left'
    )

    # Calculate EV% using the cnm_api function
    df[["fv", "ev%"]] = df.apply(lambda row: pd.Series(cnm_api(
        leg1_odds=(row['all_odds']),
        leg2_odds=(row['all_opposite_market_odds']),
        final_odds=row['odds'])), axis=1)
    
    # Format the 'fv' column to include '+' for positive values
    df["fv"] = df["fv"].astype(int).apply(lambda x: f"+{x}" if x >= 100 else str(x))
    
    # Displays the dataframe with selected columns where there is more than 1 book for that market
    cols_to_show = [
        "event_name",
        "market_type",
        "selection",
        "odds",
        "sportbook",
        "fv",
        "ev%",
        "books"
        ]

    pd.set_option('display.max_rows', None)
    df = df[df['books'] > 1][cols_to_show]
    df = df.sort_values(by=["ev%"], ascending=False).reset_index(drop=True)
    print(df)

market_spreadsheet()
