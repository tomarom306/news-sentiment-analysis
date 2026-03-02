import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for the application"""
    
    # News API
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'news_sentiment')
    
    # Topics to track
    TOPICS = os.getenv('TOPICS', 'Tesla,Apple,Bitcoin').split(',')
    
    # Sources (empty = all sources)
    SOURCES = os.getenv('SOURCES', '').split(',') if os.getenv('SOURCES') else []
    
    # Collection settings
    MAX_ARTICLES_PER_REQUEST = int(os.getenv('MAX_ARTICLES_PER_REQUEST', 100))
    COLLECTION_INTERVAL_MINUTES = int(os.getenv('COLLECTION_INTERVAL_MINUTES', 60))
    
    # Sentiment thresholds
    POSITIVE_THRESHOLD = float(os.getenv('POSITIVE_THRESHOLD', 0.05))
    NEGATIVE_THRESHOLD = float(os.getenv('NEGATIVE_THRESHOLD', -0.05))
    
    @staticmethod
    def validate():
        """Validate that all required config is present"""
        if not Config.NEWS_API_KEY:
            raise ValueError("NEWS_API_KEY is required in .env file")
        
        if Config.NEWS_API_KEY == 'your_api_key_here':
            raise ValueError("Please replace NEWS_API_KEY with your actual API key")
        
        print("✓ Configuration validated successfully")
        return True

if __name__ == "__main__":
    Config.validate()
    print(f"Tracking topics: {Config.TOPICS}")
    print(f"Max articles per request: {Config.MAX_ARTICLES_PER_REQUEST}")