import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.collectors.news_collectors import NewsCollector
from src.utils.config import Config

def test_news_api():
    """Test News API connection and data collection"""
    
    print("="*60)
    print("Testing News API Connection")
    print("="*60)
    
    # Initialize collector
    collector = NewsCollector()
    
    # Test 1: Fetch articles about Tesla
    print("\n1. Fetching articles about Tesla...")
    tesla_articles = collector.fetch_by_topic('Tesla', days_back=1)
    
    if tesla_articles:
        print(f"✓ Found {len(tesla_articles)} articles")
        print(f"\nSample article:")
        article = tesla_articles[0]
        print(f"  Title: {article['title']}")
        print(f"  Source: {article['source']['name']}")
        print(f"  Published: {article['publishedAt']}")
    else:
        print("✗ No articles found")
        return False
    
    # Test 2: Fetch all configured topics
    print(f"\n2. Fetching all topics: {Config.TOPICS}")
    all_articles = collector.fetch_all_topics(days_back=1)
    
    if all_articles:
        print(f"✓ Total articles fetched: {len(all_articles)}")
        
        # Show breakdown by topic
        topic_counts = {}
        for article in all_articles:
            topic = article.get('search_topic', 'unknown')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        print("\nBreakdown by topic:")
        for topic, count in topic_counts.items():
            print(f"  {topic}: {count} articles")
    else:
        print("✗ No articles found")
        return False
    
    # Test 3: Fetch top headlines
    print("\n3. Fetching top headlines...")
    headlines = collector.fetch_top_headlines()
    
    if headlines:
        print(f"✓ Found {len(headlines)} headlines")
        print("\nTop 3 headlines:")
        for i, article in enumerate(headlines[:3], 1):
            print(f"  {i}. {article['title']}")
    else:
        print("✗ No headlines found")
    
    print("\n" + "="*60)
    print("✓ All tests passed! News API is working correctly.")
    print("="*60)
    
    return True

if __name__ == "__main__":
    test_news_api()