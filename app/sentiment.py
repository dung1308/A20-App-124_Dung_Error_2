"""
Sentiment analysis model.
Classifies user sentiment for better advisor responses.
"""

import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)


class SentimentModel:
    """
    Simple sentiment classifier using TF-IDF + Logistic Regression.
    
    Classifies messages as:
    - 0: Negative
    - 1: Neutral
    - 2: Positive
    """
    
    def __init__(self):
        """Initialize sentiment model with simple training data."""
        try:
            # Simple training data
            texts = ["tốt", "tuyệt vời", "rất thích", "tệ", "không ổn", "thất vọng", "bình thường", "OK"]
            labels = [2, 2, 2, 0, 0, 0, 1, 1]  # 0=negative, 1=neutral, 2=positive
            
            # Vectorizer
            self.vectorizer = TfidfVectorizer(max_features=100)
            X = self.vectorizer.fit_transform(texts)
            
            # Model
            self.model = LogisticRegression(random_state=42)
            self.model.fit(X, labels)
            
            logger.info("Sentiment model initialized")
        except Exception as e:
            logger.error(f"Error initializing sentiment model: {e}")
            raise

    def predict(self, text: str) -> int:
        """
        Predict sentiment of text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Sentiment score: 0 (negative), 1 (neutral), or 2 (positive)
        """
        try:
            X = self.vectorizer.transform([text])
            sentiment = int(self.model.predict(X)[0])
            return sentiment
        except Exception as e:
            logger.error(f"Error predicting sentiment: {e}")
            return 1  # Default to neutral
    
    def get_sentiment_label(self, text: str) -> str:
        """
        Get human-readable sentiment label.
        
        Args:
            text: Input text
            
        Returns:
            Label: 'negative', 'neutral', or 'positive'
        """
        score = self.predict(text)
        labels = {0: "negative", 1: "neutral", 2: "positive"}
        return labels.get(score, "neutral")
