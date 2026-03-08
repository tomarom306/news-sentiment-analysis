import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.collectors.news_collectors import NewsCollector
from src.processors.text_cleaner import TextCleaner
from src.processors.sentiment_analyzer import SentimentAnalyzer
from src.storage.mongodb_client import MongoDBClient
from src.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

class NewsSentimentPipeline:
    """Complete pipeline: Collect → Process → Analyze → Store"""
    
    def __init__(self):
        self.collector = NewsCollector()
        self.cleaner = TextCleaner()
        self.analyzer = SentimentAnalyzer()
        self.db = MongoDBClient()
        
        logger.info("Pipeline initialized")
    
    def process_article(self, article):
        """
        Process a single article through the pipeline
        
        Args:
            article: Raw article from News API
        
        Returns:
            Processed article with sentiment
        """
        # Extract text fields
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        
        # Clean and combine text
        clean_text = self.cleaner.prepare_for_sentiment(title, description, content)
        
        # Perform sentiment analysis
        sentiment = self.analyzer.analyze_comprehensive(clean_text)
        
        # Extract keywords
        keywords = self.cleaner.extract_keywords(clean_text, top_n=5)
        
        # Add processed data to article
        article['processed_text'] = clean_text
        article['keywords'] = keywords
        article['sentiment_label'] = sentiment['sentiment_label']
        article['vader_compound'] = sentiment['vader_compound']
        article['vader_positive'] = sentiment['vader_positive']
        article['vader_negative'] = sentiment['vader_negative']
        article['vader_neutral'] = sentiment['vader_neutral']
        article['textblob_polarity'] = sentiment['textblob_polarity']
        article['textblob_subjectivity'] = sentiment['textblob_subjectivity']
        article['sentiment_confidence'] = sentiment['confidence']
        article['processed_at'] = datetime.now().isoformat()
        
        return article
    
    def run(self, days_back=1):
        """
        Run the complete pipeline
        
        Args:
            days_back: How many days back to fetch articles
        
        Returns:
            Dictionary with pipeline statistics
        """
        logger.info("="*60)
        logger.info("Starting News Sentiment Analysis Pipeline")
        logger.info("="*60)
        
        # Step 1: Collect articles
        logger.info("Step 1: Collecting articles...")
        articles = self.collector.fetch_all_topics(days_back=days_back)
        logger.success(f"Collected {len(articles)} articles")
        
        if not articles:
            logger.warning("No articles collected. Pipeline stopped.")
            return {'collected': 0, 'processed': 0, 'stored': 0}
        
        # Step 2: Process and analyze
        logger.info("Step 2: Processing and analyzing sentiment...")
        processed_articles = []
        
        for i, article in enumerate(articles, 1):
            try:
                processed = self.process_article(article)
                processed_articles.append(processed)
                
                if i % 10 == 0:
                    logger.info(f"Processed {i}/{len(articles)} articles...")
                    
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue
        
        logger.success(f"Processed {len(processed_articles)} articles")
        
        # Step 3: Store in database
        logger.info("Step 3: Storing in database...")
        stored_count = self.db.insert_articles_batch(processed_articles)
        logger.success(f"Stored {stored_count} new articles")
        
        # Get statistics
        stats = self.db.get_sentiment_stats()
        
        logger.info("="*60)
        logger.info("Pipeline Summary")
        logger.info("="*60)
        logger.info(f"Articles collected: {len(articles)}")
        logger.info(f"Articles processed: {len(processed_articles)}")
        logger.info(f"New articles stored: {stored_count}")
        logger.info(f"\nDatabase totals:")
        logger.info(f"  Positive: {stats['positive']}")
        logger.info(f"  Negative: {stats['negative']}")
        logger.info(f"  Neutral: {stats['neutral']}")
        logger.info(f"  Total: {stats['total']}")
        logger.info("="*60)
        
        return {
            'collected': len(articles),
            'processed': len(processed_articles),
            'stored': stored_count,
            'sentiment_stats': stats
        }
    
    def close(self):
        """Close all connections"""
        self.db.close()

if __name__ == "__main__":
    # Run the pipeline
    pipeline = NewsSentimentPipeline()
    
    try:
        results = pipeline.run(days_back=1)
        print(f"\n✓ Pipeline completed successfully!")
        print(f"Collected: {results['collected']}")
        print(f"Processed: {results['processed']}")
        print(f"Stored: {results['stored']}")
        
    finally:
        pipeline.close()