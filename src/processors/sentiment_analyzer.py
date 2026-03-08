import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SentimentAnalyzer:
    """Analyze sentiment of text using multiple methods"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        logger.info("SentimentAnalyzer initialized")
    
    def analyze_vader(self, text):
        """
        Analyze sentiment using VADER
        
        VADER is specifically tuned for social media and news text.
        Returns scores from -1 (most negative) to +1 (most positive)
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment scores
        """
        if not text:
            return {
                'compound': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 1
            }
        
        scores = self.vader.polarity_scores(text)
        return scores
    
    def analyze_textblob(self, text):
        """
        Analyze sentiment using TextBlob
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with polarity and subjectivity
        """
        if not text:
            return {
                'polarity': 0,
                'subjectivity': 0
            }
        
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
    
    def get_sentiment_label(self, compound_score):
        """
        Convert compound score to sentiment label
        
        Args:
            compound_score: VADER compound score (-1 to +1)
        
        Returns:
            String label: 'positive', 'negative', or 'neutral'
        """
        if compound_score >= Config.POSITIVE_THRESHOLD:
            return 'positive'
        elif compound_score <= Config.NEGATIVE_THRESHOLD:
            return 'negative'
        else:
            return 'neutral'
    
    def analyze_comprehensive(self, text):
        """
        Perform comprehensive sentiment analysis
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with all sentiment metrics
        """
        # VADER analysis
        vader_scores = self.analyze_vader(text)
        
        # TextBlob analysis
        textblob_scores = self.analyze_textblob(text)
        
        # Get sentiment label
        sentiment_label = self.get_sentiment_label(vader_scores['compound'])
        
        # Combine results
        result = {
            'sentiment_label': sentiment_label,
            'vader_compound': vader_scores['compound'],
            'vader_positive': vader_scores['pos'],
            'vader_negative': vader_scores['neg'],
            'vader_neutral': vader_scores['neu'],
            'textblob_polarity': textblob_scores['polarity'],
            'textblob_subjectivity': textblob_scores['subjectivity'],
            'confidence': abs(vader_scores['compound'])  # How confident is the sentiment
        }
        
        return result

if __name__ == "__main__":
    # Test the analyzer
    analyzer = SentimentAnalyzer()
    
    # Test texts
    test_cases = [
        "Tesla stock surges 15% on amazing earnings! Investors are thrilled!",
        "Company faces massive losses and disappointing results. Stock plummets.",
        "The company reported quarterly earnings today.",
    ]
    
    print("Sentiment Analysis Results:\n")
    for text in test_cases:
        result = analyzer.analyze_comprehensive(text)
        print(f"Text: {text}")
        print(f"Sentiment: {result['sentiment_label'].upper()}")
        print(f"VADER Compound: {result['vader_compound']:.3f}")
        print(f"Confidence: {result['confidence']:.3f}")
        print("-" * 60)