import requests
from bs4 import BeautifulSoup
import pandas as pd

crypto_date_list = []
crypto_name_list = []
crypto_symbol_list = []
crypto_market_cap_list = []
crypto_price_list = []
crypto_circulating_supply_list = []
crypto_voulume_24hr_list = []
crypto_pct_1hr_list = []
crypto_pct_24hr_list = []
crypto_pct_7day_list = []

df = pd.DataFrame()

scrape_date_list = []

def scrape_date():
    url = 'https://coinmarketcap.com/historical/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    a_tags = soup.find_all('a', class_='historical-link cmc-link')
    for tag in a_tags:
        href = tag.get('href')
        scrape_date_list.append(href)

scrape_date()
print('There are ' + str(len(scrape_date_list)) + ' dates(Sundays) available for scraping from CoinMarketCap historical data.')


def scrape_data(date):
    url = 'https://coinmarketcap.com' + date
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    tr = soup.find_all('tr', attrs={'class': 'cmc-table-row'})
    count = 0
    for row in tr:
        if count == 10:
            break
        count += 1

        try:
            crypto_date = date
        except AttributeError:
            crypto_date = None

        try:
            name_column = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__name'})
            crypto_name = name_column.find('a', attrs={'class': 'cmc-table__column-name--name cmc-link'}).text.strip()
        except AttributeError:
            crypto_name = None

        try:
            crypto_symbol = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__symbol'}).text.strip()
        except AttributeError:
            crypto_symbol = None

        try:
            crypto_market_cap = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__market-cap'}).text.strip()
        except AttributeError:
            crypto_market_cap = None

        try:
            crypto_price = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__price'}).text.strip()
        except AttributeError:
            crypto_price = None

        try:
            crypto_circulating_supply = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__circulating-supply'}).text.strip().split(' ')[0]
        except AttributeError:
            crypto_circulating_supply = None

        try:
            crypto_voulume_24hr_td = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__volume-24-h'})
            crypto_voulume_24hr = crypto_voulume_24hr_td.find('a', attrs={'class': 'cmc-link'}).text.strip()
        except AttributeError:
            crypto_voulume_24hr = None

        try:
            crypto_pct_1hr = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__percent-change-1-h'}).text.strip()
        except AttributeError:
            crypto_pct_1hr = None

        try:
            crypto_pct_24hr = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__percent-change-24-h'}).text.strip()
        except AttributeError:
            crypto_pct_24hr = None

        try:
            crypto_pct_7day = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__percent-change-7-d'}).text.strip()
        except AttributeError:
            crypto_pct_7day = None

        crypto_date_list.append(crypto_date)
        crypto_name_list.append(crypto_name)
        crypto_symbol_list.append(crypto_symbol)
        crypto_market_cap_list.append(crypto_market_cap)
        crypto_price_list.append(crypto_price)
        crypto_circulating_supply_list.append(crypto_circulating_supply)
        crypto_voulume_24hr_list.append(crypto_voulume_24hr)
        crypto_pct_1hr_list.append(crypto_pct_1hr)
        crypto_pct_24hr_list.append(crypto_pct_24hr)
        crypto_pct_7day_list.append(crypto_pct_7day)

from datetime import datetime

date_format = "%Y%m%d"

# Split and convert the start date and end date
start_date = datetime.strptime(scrape_date_list[0].split('/')[-2], date_format).strftime('%Y-%m-%d')
end_date = datetime.strptime(scrape_date_list[-1].split('/')[-2], date_format).strftime('%Y-%m-%d')
print('There are ' + str(len(scrape_date_list)) + ' dates(Sundays) between ' + start_date + ' and ' + end_date)


for i in range(len(scrape_date_list)):
    scrape_data(scrape_date_list[i])
    print("completed: " + str(i+1) + " out of " + str(len(scrape_date_list)))


df['Date'] = crypto_date_list
df['Name'] = crypto_name_list
df['Symbol'] = crypto_symbol_list
df['Market Cap'] = crypto_market_cap_list
df['Price'] = crypto_price_list
df['Circulating Supply'] = crypto_circulating_supply_list
df['Volume (24hr)'] = crypto_voulume_24hr_list
df['1h'] = crypto_pct_1hr_list
df['24h'] = crypto_pct_24hr_list
df['7d'] = crypto_pct_7day_list

# Extract the date component from the 'Date' column and convert it to a datetime data type
df['Date'] = pd.to_datetime(df['Date'].str.split('/').str[-2], format='%Y%m%d')

# Replace the dollar signs ($) and commas (,) from the 'Market Cap' and 'Price' columns
df['Market Cap'] = df['Market Cap'].str.replace('[$,]', '', regex=True)
df['Price'] = df['Price'].str.replace('[$,]', '', regex=True)

# Replace the commas (,) from the 'Circulating Supply' column
df['Circulating Supply'] = df['Circulating Supply'].str.replace(',', '')

# Replace the dollar signs ($) and commas (,) from the 'Volume (24hr)' columns
df['Volume (24hr)'] = df['Volume (24hr)'].str.replace('[$,]', '', regex=True)

# Replace the unchange sign (--), the smaller sign (<), the larger sign (>) and percentage sign (%) from the '% 1h', '% 24h', and '% 7d' columns
df['1h'] = df['1h'].str.replace('--', '0').str.lstrip('>').str.lstrip('<').str.rstrip('%')
df['24h'] = df['24h'].str.replace('--', '0').str.lstrip('>').str.lstrip('<').str.rstrip('%')
df['7d'] = df['7d'].str.replace('--', '0').str.lstrip('>').str.lstrip('<').str.rstrip('%')

# Convert the numeric columns to appropriate data types, replacing invalid values with NaN
numeric_cols = ['Market Cap', 'Price', 'Circulating Supply', 'Volume (24hr)', '1h', '24h', '7d']
df[numeric_cols] = df[numeric_cols].apply(lambda x: pd.to_numeric(x))

# Handle specific case of "<0.01" by replacing it with a small non-zero value, e.g., 0.005
df.loc[df['1h'] < 0, '1h'] = 0.005

df.to_csv("coinmarketcap.csv", index=False)