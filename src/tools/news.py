import requests
import praw
from datetime import datetime
import pdb

class CryptoNewsAggregator:
    def __init__(self, news_api_key, reddit_client_id, reddit_client_secret, reddit_user_agent):
        """
        Initializes the news aggregator with API keys and Reddit client credentials.
        
        Args:
            news_api_key (str): The API key for NewsAPI (Google News).
            reddit_client_id (str): The Reddit API client ID.
            reddit_client_secret (str): The Reddit API client secret.
            reddit_user_agent (str): The user agent for Reddit API requests.
        """
        self.news_api_key = news_api_key
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret
        self.reddit_user_agent = reddit_user_agent

    def get_reddit_news(self, keyword):
        """Fetch crypto-related news from Reddit (using PRAW), filtered by keyword."""
        reddit = praw.Reddit(client_id=self.reddit_client_id, 
                             client_secret=self.reddit_client_secret, 
                             user_agent=self.reddit_user_agent)
        
        # Fetch the top posts in the 'CryptoCurrency' subreddit
        subreddit = reddit.subreddit('CryptoCurrency')
        top_posts = subreddit.search(keyword, limit=10)

        news = []
        for post in top_posts:
            news.append({
                'title': post.title,
                'description': post.selftext,  # The content of the post
                'url': post.url,
                'created_at': datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
            })
        return news

    def get_google_news(self, keyword):
        """Fetch crypto-related news from Google News using NewsAPI, filtered by keyword."""
        url = f'https://newsapi.org/v2/everything?q={keyword}&apiKey={self.news_api_key}'
        response = requests.get(url)
        
        if response.status_code == 200:
            articles = response.json()['articles']
            news = []
            for article in articles:
                news.append({
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'published_at': article['publishedAt']
                })
            return news
        else:
            print(f"Failed to fetch Google News. Status code: {response.status_code}")
            return []

    def aggregate_news(self, keyword):
        """Aggregate news from both Reddit and Google News based on the input keyword."""
        reddit_news = self.get_reddit_news(keyword)
        google_news = self.get_google_news(keyword)

        # pdb.set_trace()
        # Combine both news sources
        all_news = reddit_news + google_news

        # Filter and format news (for now just return the combined news)
        return self.format_news(all_news)

    def format_news(self, news):
        """Format and display the aggregated news."""
        formatted_news = []
        for article in news:
            formatted_news.append({
                'title': article['title'],
                'description': article.get('description', 'No description available'),
                'source': article.get('source', 'Unknown source'),
                'url': article['url'],
                # 'published_at': article['published_at'],
            })
        return formatted_news

# Example usage:
# if __name__ == "__main__":
#     news_api_key = 'xx'
#     reddit_client_id = 'xx'
#     reddit_client_secret = 'xx'
#     reddit_user_agent = 'your_reddit_user_agent_here'
#     aggregator = CryptoNewsAggregator(news_api_key, reddit_client_id, reddit_client_secret, reddit_user_agent)
#     keyword = input("Enter a keyword to search for crypto news: ")
#     aggregated_news = aggregator.aggregate_news('bitcoin')
#     for article in aggregated_news:
#         print(f"Title: {article['title']}")
#         print(f"Source: {article['source']}")
#         print(f"Description: {article['description']}")
#         print(f"URL: {article['url']}")
#         print("-" * 80)
