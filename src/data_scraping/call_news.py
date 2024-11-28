import os
from dotenv import load_dotenv
from src.tools.news import CryptoNewsAggregator
import pandas as pd
from tqdm import tqdm 

class NewsAggregatorCaller:
    def __init__(self):
        """
        Initialize the NewsAggregatorCaller with environment variables and CryptoNewsAggregator instance.
        """
        # Load environment variables
        load_dotenv()

        # Load configuration
        self.collection_name = os.getenv("COLLECTION_NAME")
        self.data_path = os.getenv("DATA_PATH")
        self.model_name = os.getenv("MODEL_NAME")
        self.binance_api_key = os.getenv("BINANCE_API_KEY")
        self.binance_api_secret = os.getenv("BINANCE_API_SECRET")
        self.news_api_key = os.getenv("news_api_key")
        self.reddit_client_id = os.getenv("reddit_client_id")
        self.reddit_client_secret = os.getenv("reddit_client_secret")
        self.reddit_user_agent = os.getenv("reddit_user_agent", "default-agent")
        self.openai_api_key = os.getenv("openai_api_key")
        self.APIKEY_GPT4 = os.getenv("APIKEY_GPT4")
        self.AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
        self.API_VERSION = os.getenv("API_VERSION")
        self.OPENAI_ENGINE = os.getenv("OPENAI_ENGINE")
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )

        # Initialize CryptoNewsAggregator
        print(            self.news_api_key,
            self.reddit_client_id,
            self.reddit_client_secret,
            self.reddit_user_agent)
        self.aggregator = CryptoNewsAggregator(
            self.news_api_key,
            self.reddit_client_id,
            self.reddit_client_secret,
            self.reddit_user_agent,
        )

    def fetch_news_for_keywords(self, keywords):
        """
        Fetch and aggregate news for each keyword in the list.

        Args:
            keywords (list): List of keywords to fetch news for.

        Returns:
            dict: A dictionary where each key is a keyword and the value is the aggregated news.
        """
        aggregated_results = {}
        for keyword in tqdm(keywords):
            print(f"Fetching news for keyword: {keyword}")
            aggregated_results[keyword] = self.aggregator.aggregate_news(keyword)
        return aggregated_results

    def save_to_dataframe(self, keywords):
        """
        Fetch and save the aggregated news into a pandas DataFrame.

        Args:
            keywords (list): List of keywords to fetch news for.

        Returns:
            pandas.DataFrame: DataFrame containing aggregated news.
        """
        news_data = []
        aggregated_results = self.fetch_news_for_keywords(keywords)
        for keyword, articles in aggregated_results.items():
            for article in articles:
                news_data.append({
                    "keyword": keyword,
                    "title": article['title'],
                    "description": article.get('description', 'No description available'),
                    "source": article.get('source', 'Unknown source'),
                    "url": article['url'],
                })

        # Convert to DataFrame
        news_df = pd.DataFrame(news_data)
        print(news_df)
        return news_df

if __name__ == "__main__":
    # Instantiate the NewsAggregatorCaller
    caller = NewsAggregatorCaller()
    # Define the list of keywords
    keywords = [
        "bitcoin", "cryptocurrency", "blockchain", "ethereum", "dogecoin", 
        "litecoin", "ripple", "cardano", "polkadot", "solana", 
        "avalanche", "chainlink", "stellar", "vechain", "tron", 
        "monero", "tezos", "iota", "zilliqa", "pepecoin", 
        "shibainu", "floki", "safemoon", "babyDoge", "kishu", 
        "akita", "nft", "defi", "yield", "staking", 
        "liquidity", "uniswap", "sushiswap", "pancakeswap", "aave", 
        "compound", "curve", "matic", "arbitrum", "optimism", 
        "zkSync", "hedera", "algorand", "cosmos", "luna", 
        "terra", "phantom", "anchor", "synthetix", "maker", 
        "near", "hedera", "theta", "harmony", "qtum", 
        "neo", "dash", "zcash", "bat", "chiliz", 
        "elrond", "filecoin", "eos", "holo", "omg", 
        "sushi", "one", "btt", "waves", "ontology", 
        "ravencoin", "gala", "render", "enjin", "wax", 
        "flow", "sandbox", "axie", "mana", "decentraland", 
        "nexo", "celsius", "3ac", "arweave", "storj", 
        "matic", "quant", "loopring", "yearn", "hive", 
        "verge", "dogelon", "moonbeam", "mina", "nervos", 
        "audius", "dydx", "serum", "ellipsis", "radix"
    ]
    # Fetch news and save it into a DataFrame
    news_df = caller.save_to_dataframe(keywords)
    # Save to a CSV file (optional)
    news_df.to_csv("dataset/aggregated_news.csv", index=False)