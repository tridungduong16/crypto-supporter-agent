import requests
from bs4 import BeautifulSoup
import pandas as pd

class CryptoAnalyzer:
    def __init__(self, symbol):
        """
        Initializes the CryptoAnalyzer with the symbol of the cryptocurrency.
        :param symbol: The symbol of the cryptocurrency (e.g., 'bitcoin', 'ethereum').
        """
        self.symbol = symbol
        self.base_url = f"https://coinmarketcap.com/currencies/{symbol}/"
        self.data = {}

    def crawl_data(self):
        """
        Crawls data from CoinMarketCap for the given cryptocurrency symbol.
        """
        # Make a request to the CoinMarketCap page for the cryptocurrency
        response = requests.get(self.base_url)
        
        if response.status_code != 200:
            raise Exception(f"Error: Unable to fetch data for {self.symbol}")
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extracting the data we need using appropriate CSS selectors
        try:
            price = soup.find("div", class_="priceValue___11gHJ").text.strip()
            market_cap = soup.find("div", class_="statsValue___2iaZk").text.strip()
            volume_24h = soup.find_all("div", class_="statsValue___2iaZk")[1].text.strip()
            circulating_supply = soup.find("div", class_="statsValue___2iaZk").find_next("div").text.strip()
            percent_change_1h = soup.find("span", class_="sc-16r8icm-0 cXDtnr").text.strip()
            percent_change_24h = soup.find("span", class_="sc-16r8icm-0 czVGfy").text.strip()
            
            # Storing the data in a dictionary
            self.data = {
                "Price": price,
                "Market Cap": market_cap,
                "Volume (24h)": volume_24h,
                "Circulating Supply": circulating_supply,
                "Change (1h)": percent_change_1h,
                "Change (24h)": percent_change_24h
            }

        except AttributeError as e:
            print(f"Error while parsing data for {self.symbol}: {e}")
            return None
    
    def display_data(self):
        """
        Display the data as a pandas DataFrame for easy reading.
        """
        if not self.data:
            print("No data found.")
            return
        
        # Create a DataFrame to show the data in tabular form
        df = pd.DataFrame(self.data, index=[0])
        print(df)
    
    def analyze_data(self):
        """
        Perform basic analysis on the data and print some insights.
        """
        if not self.data:
            print("No data to analyze.")
            return

        print(f"\nAnalysis for {self.symbol.upper()}:\n")
        print(f"Price: {self.data['Price']}")
        print(f"Market Cap: {self.data['Market Cap']}")
        print(f"24h Trading Volume: {self.data['Volume (24h)']}")
        print(f"Circulating Supply: {self.data['Circulating Supply']}")
        print(f"Change in the last hour: {self.data['Change (1h)']}")
        print(f"Change in the last 24 hours: {self.data['Change (24h)']}")
        
        # You can add more custom analysis logic here as needed

if __name__ == "__main__":
    # Example usage
    symbol = input("Enter the cryptocurrency symbol (e.g., 'bitcoin', 'ethereum'): ").lower()
    analyzer = CryptoAnalyzer(symbol)
    
    # Crawl data
    analyzer.crawl_data()
    
    # Display data
    analyzer.display_data()
    
    # Analyze data
    analyzer.analyze_data()
