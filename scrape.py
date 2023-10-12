import os
import requests

from cs50 import SQL
from flask import flash, redirect
from bs4 import BeautifulSoup as bs

# Constants
URL = 'https://gpro.net/'
URL_BASE = 'https://gpro.net/gb/'
URL_BRANDS = 'https://gpro.net/gb/Suppliers.asp'
URL_ELITE = 'https://gpro.net/gb/Standings.asp?Group=Elite'
LOGIN_ROUTE = 'https://gpro.net/Login.asp?Redirect=gpro.asp'
HEADERS = {'User-Agent': 'GPRO Tyres Prediction Game', 'origin': URL, 'referer': URL + LOGIN_ROUTE}


# Create session object
s = requests.session()


def scrape_brands(db):
    """ Scrapes the suppliers page looking for the brands for the season"""

    # Build credentials dictionary, as login is required to access this page
    # Beware the account needs to not be retired
    credentials = {
            # Get user from environment variable
            'textLogin': os.getenv("textLogin"),
            # Get password from environment variable
            'textPassword': os.getenv("textPassword"),
            'Logon': 'Login',
            }

    # Login post request
    login_return = s.post(LOGIN_ROUTE, headers=HEADERS, data=credentials)

    # If the account is inactive, use the link to re-activate it
    if "Your game account is inactive!" in login_return.text:
        s.get(URL_BASE + "ActivateAccount.asp?reactivate=1&source=office")

    # Get text form the suppliers page
    soup = bs(s.get(URL_BRANDS).text, 'html.parser')
    suppliers = list()
    # Get div for the chosen tyre, append to list
    divsel = soup.find('div', class_='column left chosen')
    suppliers.append(divsel.h2.text)
    # Get all divs for the not chosen brands, append to list
    divs = soup.find_all('div', class_='column left')
    for div in divs:
        suppliers.append(div.h2.text)

    # Check for the current season
    current = db.execute("SELECT season FROM status WHERE current = 'True'")[0]["season"]

    # Insert this season's brands to the db
    for brand in suppliers:
            db.execute("INSERT INTO tyres (brand, season, league) VALUES (?, ?, 'Elite')", brand, current)

    flash(f"Tyres for the season {current} updated. ")
    return redirect("/adminpanel")


def scrape_names(db):
    """ Scrapes manager's names and profile's URLs and saves them to the db """

    names = list()
    soup = bs(s.get(URL_ELITE).text, 'html.parser')
    table = soup.find_all('table')[1]
    table_rows = table.find_all('tr')[1:]
    for row in table_rows:
        man_dict = dict()
        manager = row.find_all('td')[4:5][0]
        try:
            # Trophies for GPRO champs
            trophy = manager.span.text
            if trophy.isnumeric():
                trophy = int(trophy) * '🏆'
                name = manager.a.text + ' ' + trophy
            else:
                name = manager.a.text
        except:
            name = manager.a.text
        man_dict['name'] = name
        man_dict['link'] = URL_BASE + manager.a.get('href')
        names.append(man_dict)

    # Check for the current season
    current = db.execute("SELECT season FROM status WHERE current = 'True'")[0]["season"]

    # Log names and links into the db
    for manager in names:
        db.execute("INSERT INTO selection (season, league, fullname, hyperlink) VALUES (?, 'Elite', ?, ?)", current, manager['name'], manager['link'])

    flash(f"Managers for season {current} added!! ")
    return redirect("/adminpanel")


def scrape_managers_tyres(db):
    """ Scrapes for the actual tyres choices for the assets and saves those to the db """

    names = list()
    soup = bs(s.get(URL_ELITE).text, 'html.parser')
    table = soup.find_all('table')[1]
    table_rows = table.find_all('tr')[1:]
    for row in table_rows:
        man_dict = dict()
        manager = row.find_all('td')[2:5]
        del manager[1]
        try:
            trophy = manager[1].span.text
            if trophy.isnumeric():
                trophy = int(trophy) * '🏆'
                name = manager[1].a.text + ' ' + trophy
            else:
                name = manager[1].a.text
        except:
            name = manager[1].a.text
        man_dict['name'] = name
        try:
            man_dict['tyre'] = manager[0].img.get('title')
        except:
            man_dict['tyre'] = None
        names.append(man_dict)

    # Check for the current season
    current = db.execute("SELECT season FROM status WHERE current = 'True'")[0]["season"]

    for manager in names:
        # Retrieve ids for tyres and replace in managers dictionaries
        try:
            manager['tyre'] = db.execute("SELECT tyres_id FROM tyres WHERE season = ? and brand = ?", current, manager['tyre'])[0]["tyres_id"]
        except:
            manager['tyre'] = None
        # Retrieve selection id for this season and add to dictionary
        manager['id'] = db.execute("SELECT selection_id FROM selection WHERE season = ? AND league = 'Elite' AND fullname = ?", current, manager['name'])[0]["selection_id"]

   # Updated the tyres in the db
    for manager in names:
        db.execute("UPDATE selection SET tyres_id = ? WHERE selection_id = ?", manager['tyre'], manager['id'])

    flash(f"Managers tyres picks for season {current} updated!! ")
    return redirect("/adminpanel")
    
