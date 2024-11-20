import requests
from bs4 import BeautifulSoup
import pandas as pd

class BitcoinS2FModel:
    def __init__(self, url):
        """
        Initializes the Bitcoin S2F Model scraper with the URL of the chart.
        :param url: URL of the Stock-to-Flow chart or data page
        """
        self.url = url
        self.data = {}

    def crawl_data(self):
        """
        Scrapes data from the webpage that contains the Bitcoin Stock-to-Flow chart.
        Assumes the data is available in HTML elements.
        """
        # Send GET request to the URL
        response = requests.get(self.url)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error: Unable to fetch data from {self.url}")
            return None

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example of scraping the data (you need to adjust this based on the actual structure of the page)
        try:
            # This part will depend on the specific HTML structure of the Stock-to-Flow chart page
            # For example, you could find the data inside specific divs or script tags
            # Here, we will just look for specific data points as an example
            s2f_data = soup.find_all('script', {'type': 'application/json'})  # This may vary
            # You would now need to inspect the structure of s2f_data to extract the required values
            # Let's assume you found relevant data in JSON-like format
            
            # Example: If you have found the data in a <script> tag, you might need to extract it:
            # data_json = json.loads(s2f_data[0].string)
            # But this step depends on how the data is structured on the page.

            # Dummy data to demonstrate structure (replace with actual data scraping logic)
            self.data = {
                'Date': ['2021-01-01', '2021-02-01', '2021-03-01'],  # Example Dates
                'Price': [30000, 35000, 40000],  # Example prices from the S2F chart
                'Stock-to-Flow': [56, 60, 65]  # Example Stock-to-Flow values
            }

        except Exception as e:
            print(f"Error parsing the data: {e}")
            return None

    def display_data(self):
        """
        Displays the scraped data in a tabular format using pandas DataFrame.
        """
        if not self.data:
            print("No data available to display.")
            return
        
        # Create a DataFrame to show the data
        df = pd.DataFrame(self.data)
        print(df)

    def plot_data(self):
        """
        Plots the Bitcoin Stock-to-Flow data using matplotlib.
        """
        import matplotlib.pyplot as plt

        if not self.data:
            print("No data available to plot.")
            return
        
        df = pd.DataFrame(self.data)
        
        plt.figure(figsize=(10, 6))
        plt.plot(df['Date'], df['Price'], label="Bitcoin Price", color='blue', marker='o')
        plt.plot(df['Date'], df['Stock-to-Flow'], label="Stock-to-Flow", color='red', linestyle='--')

        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.title('Bitcoin Stock-to-Flow Model')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

# Example usage
if __name__ == "__main__":
    url = 'https://www.lookintobitcoin.com/charts/stock-to-flow/'
    analyzer = BitcoinS2FModel(url)
    analyzer.crawl_data()
    analyzer.display_data()
    analyzer.plot_data()
