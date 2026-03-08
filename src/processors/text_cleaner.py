import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.logger import get_logger

logger = get_logger(__name__)

class TextCleaner:
    """Clean and preprocess text data"""
    
    def __init__(self):
        logger.info("TextCleaner initialized")
    
    def clean_text(self, text):
        """
        Clean text for sentiment analysis
        
        Args:
            text: Raw text string
        
        Returns:
            Cleaned text string
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove special characters but keep sentence structure
        text = re.sub(r'[^\w\s\.\!\?]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text, top_n=5):
        """
        Extract important keywords from text
        
        Args:
            text: Text string
            top_n: Number of top keywords to return
        
        Returns:
            List of keywords
        """
        # Common stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'can', 'this', 'that', 'these', 'those', 'it', 'its', 'i',
            'you', 'he', 'she', 'we', 'they', 'what', 'which', 'who', 'when',
            'where', 'why', 'how', 'said', 'from', 'as', 'by'
        }
        
        # Clean and tokenize
        words = self.clean_text(text).split()
        
        # Filter stop words and short words
        keywords = [
            word for word in words 
            if len(word) > 3 and word not in stop_words
        ]
        
        # Count frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]
    
    def prepare_for_sentiment(self, title, description, content):
        """
        Prepare article text for sentiment analysis
        
        Args:
            title: Article title
            description: Article description
            content: Article content
        
        Returns:
            Combined cleaned text
        """
        # Combine all text (title is most important, then description, then content)
        texts = []
        
        if title:
            texts.append(title)
        if description:
            texts.append(description)
        if content and content != '[Removed]':  # News API sometimes returns [Removed]
            # Only use first 500 characters of content to avoid rate limits
            texts.append(content[:500])
        
        combined = ' '.join(texts)
        return self.clean_text(combined)

if __name__ == "__main__":
    # Test the cleaner
    cleaner = TextCleaner()
    
    # Test text
    sample_text = """
    Tesla Stock SURGES 15% After Earnings Beat! 🚀
    https://example.com/article
    CEO Elon Musk said <b>sales were strong</b> in Q4.
    Contact: news@example.com
    """
    
    cleaned = cleaner.clean_text(sample_text)
    print(f"Original: {sample_text}")
    print(f"\nCleaned: {cleaned}")
    
    keywords = cleaner.extract_keywords(sample_text)
    print(f"\nKeywords: {keywords}")