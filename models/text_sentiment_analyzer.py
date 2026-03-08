"""
Text Sentiment Analysis Module
Detects sentiment/emotion from text input
"""

import os
import warnings
warnings.filterwarnings('ignore')


def analyze_text_sentiment(text: str, verbose=True):
    """
    Analyze sentiment of input text.
    
    Uses VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analyzer.
    VADER is optimized for social media and mixed case text.
    
    Args:
        text (str): Input text to analyze
        verbose (bool): Print detailed sentiment analysis
    
    Returns:
        dict: Sentiment analysis results
              {
                'sentiment': 'positive'/'negative'/'neutral',
                'score': 0.0-1.0 (compound score)
              }
    
    Example:
        >>> result = analyze_text_sentiment("I am very happy!")
        >>> print(result)
        >>> # {'sentiment': 'positive', 'score': 0.87}
    """
    
    try:
        from nltk.sentiment import SentimentIntensityAnalyzer
        import nltk
        
        # Download required NLTK data (runs once)
        try:
            nltk.data.find('sentiment/vader_lexicon')
        except LookupError:
            print(" Downloading VADER sentiment lexicon...")
            nltk.download('vader_lexicon', quiet=True)
        
        # Initialize analyzer
        analyzer = SentimentIntensityAnalyzer()
        
        # Get sentiment scores
        scores = analyzer.polarity_scores(text)
        
        # Extract scores
        compound = scores['compound']  # Range: -1 (most negative) to 1 (most positive)
        pos = scores['pos']
        neg = scores['neg']
        neu = scores['neu']
        
        # Classify sentiment based on compound score
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        result = {
            'sentiment': sentiment,
            'score': (compound + 1) / 2,  # Normalize to 0-1 range
            'confidence': max(pos, neg, neu),
            'breakdown': {
                'positive': pos,
                'negative': neg,
                'neutral': neu
            }
        }
        
        if verbose:
            print(f"\n📝 TEXT SENTIMENT ANALYSIS:")
            print(f"   Text: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
            print(f"   Sentiment: {sentiment.upper()}")
            print(f"   Score: {result['score']:.1%}")
            print(f"   Breakdown: Pos={pos:.1%}, Neg={neg:.1%}, Neu={neu:.1%}")
        
        return result
    
    except ImportError:
        print(" NLTK not installed. Using fallback sentiment analyzer.")
        return analyze_text_sentiment_fallback(text, verbose)


def analyze_text_sentiment_fallback(text: str, verbose=True):
    """
    Fallback sentiment analyzer using simple keyword-based approach.
    Used when NLTK is not available.
    
    Args:
        text (str): Input text
        verbose (bool): Print analysis
    
    Returns:
        dict: Sentiment analysis results
    """
    
    # Simple keyword lists
    positive_words = {
        'happy', 'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'love', 'awesome', 'best', 'perfect', 'beautiful', 'brilliant', 'wonderful',
        'terrific', 'superb', 'outstanding', 'glad', 'delighted', 'pleased'
    }
    
    negative_words = {
        'sad', 'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'angry',
        'upset', 'furious', 'disappointed', 'disgusted', 'distressed', 'frustrated',
        'miserable', 'pathetic', 'useless', 'annoyed', 'irritated', 'mad'
    }
    
    import string
    
    text_lower = text.lower()
    words = text_lower.split()
    
    # Strip punctuation from words for matching
    words_clean = [word.strip(string.punctuation) for word in words]
    total = len(words_clean)
    
    # Count sentiment words
    pos_count = sum(1 for word in words_clean if word in positive_words)
    neg_count = sum(1 for word in words_clean if word in negative_words)
    
    if pos_count > neg_count:
        sentiment = 'positive'
        score = min(1.0, pos_count / max(1, total))
    elif neg_count > pos_count:
        sentiment = 'negative'
        score = min(1.0, neg_count / max(1, total))
    else:
        sentiment = 'neutral'
        score = 0.5
    
    result = {
        'sentiment': sentiment,
        'score': score,
        'confidence': max(pos_count, neg_count) / max(1, total),
        'breakdown': {
            'positive': pos_count / max(1, total),
            'negative': neg_count / max(1, total),
            'neutral': 1 - (pos_count + neg_count) / max(1, total)
        }
    }
    
    if verbose:
        print(f"\n📝 TEXT SENTIMENT ANALYSIS (Fallback):")
        print(f"   Text: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
        print(f"   Sentiment: {sentiment.upper()}")
        print(f"   Score: {result['score']:.1%}")
    
    return result


def convert_sentiment_to_emotion(sentiment: str) -> str:
    """
    Convert sentiment label to emotion label.
    
    Maps:
    - positive → Happy
    - negative → Sad
    - neutral → Neutral
    
    Args:
        sentiment (str): Sentiment ('positive', 'negative', 'neutral')
    
    Returns:
        str: Emotion label
    """
    mapping = {
        'positive': 'Happy',
        'negative': 'Sad',
        'neutral': 'Neutral'
    }
    return mapping.get(sentiment.lower(), 'Neutral')


if __name__ == "__main__":
    # Test the sentiment analyzer
    test_texts = [
        "I am so happy and excited!",
        "This is terrible and awful",
        "The weather is okay",
        "I love this amazing product!",
        "I hate this completely"
    ]
    
    print("="*70)
    print("TEXT SENTIMENT ANALYSIS TESTS")
    print("="*70)
    
    for text in test_texts:
        result = analyze_text_sentiment(text)
        emotion = convert_sentiment_to_emotion(result['sentiment'])
        print(f"  → Emotion: {emotion}\n")
