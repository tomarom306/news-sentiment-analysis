from newsapi import NewsApiClient
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.config import Config
from src.utils.logger import get_logger
logger = get_logger(__name__)

class NewsCollector:
    """Collect news articles from News API"""
    
    def __init__(self):
        Config.validate()
        self.newsapi = NewsApiClient(api_key=Config.NEWS_API_KEY)
        logger.info("NewsCollector initialized")
    
    def fetch_by_topic(self, topic, days_back=7):
        """
        Fetch articles about a specific topic
        
        Args:
            topic: Search keyword (e.g., 'Tesla', 'Bitcoin')
            days_back: How many days back to search
        
        Returns:
            List of article dictionaries
        """
        logger.info(f"Fetching articles about '{topic}'")
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        try:
            # Fetch articles
            response = self.newsapi.get_everything(
                q=topic,
                from_param=from_date.strftime('%Y-%m-%d'),
                to=to_date.strftime('%Y-%m-%d'),
                language='en',
                sort_by='publishedAt',
                page_size=Config.MAX_ARTICLES_PER_REQUEST
            )
            
            if response['status'] == 'ok':
                articles = response['articles']
                logger.success(f"Fetched {len(articles)} articles about '{topic}'")
                
                # Add metadata
                for article in articles:
                    article['search_topic'] = topic
                    article['fetched_at'] = datetime.now().isoformat()
                
                return articles
            else:
                logger.error(f"API error: {response.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            return []
    
    def fetch_all_topics(self, days_back=7):
        """Fetch articles for all configured topics"""
        all_articles = []
        
        for topic in Config.TOPICS:
            articles = self.fetch_by_topic(topic.strip(), days_back)
            all_articles.extend(articles)
        
        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def fetch_top_headlines(self, country='us'):
        """Fetch top headlines"""
        logger.info(f"Fetching top headlines for {country}")
        
        try:
            response = self.newsapi.get_top_headlines(
                country=country,
                page_size=Config.MAX_ARTICLES_PER_REQUEST
            )
            
            if response['status'] == 'ok':
                articles = response['articles']
                logger.success(f"Fetched {len(articles)} top headlines")
                
                for article in articles:
                    article['search_topic'] = 'top_headlines'
                    article['fetched_at'] = datetime.now().isoformat()
                
                return articles
            else:
                logger.error(f"API error: {response.get('message')}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching headlines: {e}")
            return []

if __name__ == "__main__":
    # Test the collector
    collector = NewsCollector()
    
    # Fetch articles about Tesla
    articles = collector.fetch_by_topic('Tesla', days_back=1)
    
    if articles:
        print(f"\n✓ Successfully fetched {len(articles)} articles!")
        print(f"\nFirst article:")
        print(f"Title: {articles[0]['title']}")
        print(f"Source: {articles[0]['source']['name']}")
        print(f"Published: {articles[0]['publishedAt']}")
        print(f"URL: {articles[0]['url']}")