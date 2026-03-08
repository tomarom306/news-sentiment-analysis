import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MongoDBClient:
    """MongoDB client for storing and retrieving articles"""
    
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.MONGO_DB_NAME]
        self.articles_collection = self.db['articles']
        
        # Create indexes for better query performance
        self._create_indexes()
        
        logger.info(f"MongoDB connected to {Config.MONGO_DB_NAME}")
    
    def _create_indexes(self):
        """Create database indexes"""
        try:
            # Index on URL (unique identifier for articles)
            self.articles_collection.create_index([('url', ASCENDING)], unique=True)
            
            # Index on published date
            self.articles_collection.create_index([('publishedAt', DESCENDING)])
            
            # Index on search topic
            self.articles_collection.create_index([('search_topic', ASCENDING)])
            
            # Index on sentiment
            self.articles_collection.create_index([('sentiment_label', ASCENDING)])
            
            # Compound index for queries
            self.articles_collection.create_index([
                ('search_topic', ASCENDING),
                ('publishedAt', DESCENDING)
            ])
            
            logger.info("Database indexes created")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
    
    def insert_article(self, article):
        """
        Insert a single article
        
        Args:
            article: Dictionary with article data
        
        Returns:
            Inserted document ID or None if duplicate
        """
        try:
            result = self.articles_collection.insert_one(article)
            return result.inserted_id
        except Exception as e:
            if 'duplicate key' in str(e).lower():
                logger.debug(f"Article already exists: {article.get('url', 'unknown')}")
                return None
            else:
                logger.error(f"Error inserting article: {e}")
                return None
    
    def insert_articles_batch(self, articles):
        """
        Insert multiple articles (ignores duplicates)
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            Number of articles inserted
        """
        if not articles:
            return 0
        
        inserted_count = 0
        for article in articles:
            if self.insert_article(article):
                inserted_count += 1
        
        logger.info(f"Inserted {inserted_count} new articles (duplicates skipped)")
        return inserted_count
    
    def get_articles_by_topic(self, topic, limit=100):
        """Get articles for a specific topic"""
        articles = self.articles_collection.find(
            {'search_topic': topic}
        ).sort('publishedAt', DESCENDING).limit(limit)
        
        return list(articles)
    
    def get_articles_by_sentiment(self, sentiment_label, limit=100):
        """Get articles by sentiment (positive/negative/neutral)"""
        articles = self.articles_collection.find(
            {'sentiment_label': sentiment_label}
        ).sort('publishedAt', DESCENDING).limit(limit)
        
        return list(articles)
    
    def get_sentiment_stats(self, topic=None):
        """
        Get sentiment statistics
        
        Args:
            topic: Optional topic filter
        
        Returns:
            Dictionary with sentiment counts
        """
        match_stage = {}
        if topic:
            match_stage = {'search_topic': topic}
        
        pipeline = [
            {'$match': match_stage},
            {'$group': {
                '_id': '$sentiment_label',
                'count': {'$sum': 1},
                'avg_compound': {'$avg': '$vader_compound'}
            }}
        ]
        
        results = list(self.articles_collection.aggregate(pipeline))
        
        stats = {
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'total': 0
        }
        
        for result in results:
            sentiment = result['_id']
            count = result['count']
            stats[sentiment] = count
            stats['total'] += count
        
        return stats
    
    def get_recent_articles(self, hours=24, limit=100):
        """Get articles from the last N hours"""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        articles = self.articles_collection.find(
            {'fetched_at': {'$gte': cutoff_time.isoformat()}}
        ).sort('publishedAt', DESCENDING).limit(limit)
        
        return list(articles)
    
    def get_total_count(self):
        """Get total number of articles"""
        return self.articles_collection.count_documents({})
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        logger.info("MongoDB connection closed")

if __name__ == "__main__":
    # Test MongoDB connection
    db = MongoDBClient()
    
    print(f"Total articles in database: {db.get_total_count()}")
    
    stats = db.get_sentiment_stats()
    print(f"\nSentiment distribution:")
    print(f"  Positive: {stats['positive']}")
    print(f"  Negative: {stats['negative']}")
    print(f"  Neutral: {stats['neutral']}")
    print(f"  Total: {stats['total']}")
    
    db.close()