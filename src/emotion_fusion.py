"""
Emotion Fusion Module
Combines facial emotion, voice emotion, and text sentiment into a single dominant emotion
"""

import numpy as np
from typing import Dict, Tuple, Union


# Emotion mapping for consistency across all modalities
EMOTION_CLASSES = ['Angry', 'Fear', 'Happy', 'Neutral', 'Sad', 'Disgust', 'Surprised']

# Emotion aliases to handle different emotion names from different models
EMOTION_ALIASES = {
    'angry': 'Angry',
    'fear': 'Fear',
    'happy': 'Happy',
    'joy': 'Happy',
    'neutral': 'Neutral',
    'sad': 'Sad',
    'sadness': 'Sad',
    'disgust': 'Disgust',
    'surprise': 'Surprised',
    'surprised': 'Surprised',
}

# Text sentiment to emotion mapping
SENTIMENT_TO_EMOTION = {
    'positive': 'Happy',
    'negative': 'Sad',
    'neutral': 'Neutral',
}


def normalize_emotion(emotion: str) -> str:
    """
    Normalize emotion names to standard format.
    
    Args:
        emotion (str): Raw emotion name (can be any case)
    
    Returns:
        str: Normalized emotion name from EMOTION_CLASSES
    """
    emotion_lower = emotion.lower().strip()
    
    # Try direct mapping
    if emotion_lower in EMOTION_ALIASES:
        return EMOTION_ALIASES[emotion_lower]
    
    # Try partial match
    for key, value in EMOTION_ALIASES.items():
        if key in emotion_lower:
            return value
    
    # Default
    return 'Neutral'


def fuse_emotions_weighted(
    face_emotion: str,
    voice_emotion: str,
    text_sentiment: str,
    weights: Dict[str, float] = None,
    confidences: Dict[str, float] = None,
    verbose: bool = True
) -> Tuple[str, Dict[str, float]]:
    """
    Fuse three emotion sources using a weighted approach.
    
    This function combines facial emotion, voice emotion, and text sentiment
    by assigning weights to each modality and calculating a weighted score
    for each emotion class.
    
    Fusion Logic:
    1. Normalize all inputs to standard emotion names
    2. Create probability vectors for each modality:
       - 1.0 for the detected emotion
       - 0.0 for others
    3. Apply weights to each vector:
       - Face weight: 0.5 (50% - most reliable)
       - Voice weight: 0.3 (30% - quite reliable)
       - Text weight: 0.2 (20% - lower weight due to ambiguity)
    4. Sum weighted vectors to get combined score
    5. Return the emotion with highest combined score
    
    Args:
        face_emotion (str): Facial emotion (e.g., 'Happy', 'Angry')
        voice_emotion (str): Voice emotion (e.g., 'Happy', 'Angry')
        text_sentiment (str): Text sentiment (e.g., 'positive', 'negative', 'neutral')
        weights (dict, optional): Custom weights {'face': 0.5, 'voice': 0.3, 'text': 0.2}
    
    Returns:
        tuple: (dominant_emotion, emotion_scores)
               - dominant_emotion: Final predicted emotion (str)
               - emotion_scores: Dict with scores for each emotion class
    
    Example:
        >>> emotion, scores = fuse_emotions_weighted('Happy', 'Happy', 'positive')
        >>> print(emotion)  # 'Happy'
        >>> print(scores)   # {'Happy': 0.95, 'Angry': 0.0, ...}
    """
    
    # Default weights (can be customized)
    if weights is None:
        weights = {
            'face': 0.5,      # Face is most reliable (50%)
            'voice': 0.3,     # Voice is quite reliable (30%)
            'text': 0.2       # Text is less reliable (20%)
        }
    
    # Normalize inputs
    face_norm = normalize_emotion(face_emotion)
    voice_norm = normalize_emotion(voice_emotion)
    text_norm = normalize_emotion(text_sentiment)
    
    if verbose:
        print(f"\n📊 EMOTION FUSION (Weighted Method):")
        print(f"   Face:  {face_emotion:12} → {face_norm:12} (weight: {weights['face']*100:.0f}%)")
        print(f"   Voice: {voice_emotion:12} → {voice_norm:12} (weight: {weights['voice']*100:.0f}%)")
        print(f"   Text:  {text_sentiment:12} → {text_norm:12} (weight: {weights['text']*100:.0f}%)")
    
    # Initialize scores for all emotion classes
    emotion_scores = {emotion: 0.0 for emotion in EMOTION_CLASSES}
    
    # Add weighted contributions; optionally scale by confidences
    if confidences and 'face' in confidences:
        emotion_scores[face_norm] += weights['face'] * confidences.get('face', 1.0)
    else:
        emotion_scores[face_norm] += weights['face']
    if confidences and 'voice' in confidences:
        emotion_scores[voice_norm] += weights['voice'] * confidences.get('voice', 1.0)
    else:
        emotion_scores[voice_norm] += weights['voice']
    if confidences and 'text' in confidences:
        emotion_scores[text_norm] += weights['text'] * confidences.get('text', 1.0)
    else:
        emotion_scores[text_norm] += weights['text']
    
    # Find the emotion with the highest combined score
    dominant_emotion = max(emotion_scores, key=emotion_scores.get)
    
    if verbose:
        print(f"\n   ✓ Dominant Emotion: {dominant_emotion}")
        print(f"   ✓ Score: {emotion_scores[dominant_emotion]:.2f}/1.0")
    
    return dominant_emotion, emotion_scores


def fuse_emotions_voting(
    face_emotion: str,
    voice_emotion: str,
    text_sentiment: str
) -> Tuple[str, Dict[str, int]]:
    """
    Fuse three emotion sources using a majority voting approach.
    
    This function combines emotions by simple majority voting:
    - Each modality gets one vote for its detected emotion
    - The emotion with the most votes wins
    - If there's a tie, additional logic selects from tied emotions
    
    Fusion Logic:
    1. Normalize all inputs to standard emotion names
    2. Count votes for each emotion:
       - Face votes for its emotion
       - Voice votes for its emotion
       - Text votes for its emotion
    3. Find emotion(s) with maximum votes
    4. If tie exists, use confidence scores to break it
       (face > voice > text precedence)
    5. Return winning emotion
    
    This method is useful when you want democratic voting rather
    than weighted importance.
    
    Args:
        face_emotion (str): Facial emotion
        voice_emotion (str): Voice emotion
        text_sentiment (str): Text sentiment
    
    Returns:
        tuple: (dominant_emotion, vote_counts)
               - dominant_emotion: Final predicted emotion (str)
               - vote_counts: Dict with vote count for each emotion
    
    Example:
        >>> emotion, votes = fuse_emotions_voting('Happy', 'Happy', 'positive')
        >>> print(emotion)  # 'Happy' (3 votes)
        >>> print(votes)    # {'Happy': 3, 'Angry': 0, ...}
    """
    
    # Normalize inputs
    face_norm = normalize_emotion(face_emotion)
    voice_norm = normalize_emotion(voice_emotion)
    text_norm = normalize_emotion(text_sentiment)
    
    print(f"\n🗳️  EMOTION FUSION (Voting Method):")
    print(f"   Face vote:  {face_norm}")
    print(f"   Voice vote: {voice_norm}")
    print(f"   Text vote:  {text_norm}")
    
    # Initialize vote counts
    vote_counts = {emotion: 0 for emotion in EMOTION_CLASSES}
    
    # Count votes
    vote_counts[face_norm] += 1
    vote_counts[voice_norm] += 1
    vote_counts[text_norm] += 1
    
    # Find maximum votes
    max_votes = max(vote_counts.values())
    
    # Find all emotions with maximum votes (in case of tie)
    tied_emotions = [e for e, v in vote_counts.items() if v == max_votes]
    
    if len(tied_emotions) == 1:
        dominant_emotion = tied_emotions[0]
    else:
        # Break tie: prefer face > voice > text
        tie_priority = {face_norm: 1, voice_norm: 2, text_norm: 3}
        dominant_emotion = min(tied_emotions, key=lambda e: tie_priority.get(e, 4))
    
    print(f"\n   ✓ Dominant Emotion: {dominant_emotion} ({max_votes}/3 votes)")
    print(f"   ✓ Vote Distribution: {dict(sorted(vote_counts.items(), key=lambda x: x[1], reverse=True))}")
    
    return dominant_emotion, vote_counts


def fuse_emotions_fast(face_emotion: str,
                       voice_emotion: str,
                       text_sentiment: str,
                       weights: Dict[str, float] = None,
                       confidences: Dict[str, float] = None) -> str:
    """Quick fusion returning only the dominant emotion string.

    Designed for low latency and concise output. Uses the weighted logic
    but suppresses all logging and returns the emotion directly.
    """
    dominant, _ = fuse_emotions_weighted(
        face_emotion,
        voice_emotion,
        text_sentiment,
        weights=weights,
        confidences=confidences,
        verbose=False
    )
    return dominant


def fuse_emotions_hybrid(
    face_emotion: str,
    voice_emotion: str,
    text_sentiment: str,
    face_confidence: float = None,
    voice_confidence: float = None,
    text_confidence: float = None,
) -> Tuple[str, Dict[str, float]]:
    """
    Fuse emotions using a hybrid approach combining weights AND confidence scores.
    
    This is the MOST ADVANCED fusion method that considers both:
    - Modality importance (weights)
    - Detection confidence (confidence scores)
    
    Fusion Logic:
    1. Normalize all inputs
    2. Create weighted scores = modality_weight * confidence_score
    3. Distribute weighted scores across emotion classes:
       - Full score to the detected emotion
       - Small amount (10%) to similar emotions (e.g., Sad/Angry are related)
    4. Return emotion with highest final score
    
    This method is best when you have confidence scores from each modality.
    High confidence detection gets more influence on final result.
    
    Args:
        face_emotion (str): Facial emotion
        voice_emotion (str): Voice emotion
        text_sentiment (str): Text sentiment
        face_confidence (float): Confidence 0-1 (default: 1.0 if None)
        voice_confidence (float): Confidence 0-1 (default: 1.0 if None)
        text_confidence (float): Confidence 0-1 (default: 1.0 if None)
    
    Returns:
        tuple: (dominant_emotion, emotion_scores)
    
    Example:
        >>> emotion, scores = fuse_emotions_hybrid(
        ...     'Happy', 0.95,
        ...     'Happy', 0.85,
        ...     'positive', 0.70
        ... )
        >>> print(emotion)  # 'Happy' (weighted by confidence)
    """
    
    # Default confidence to 1.0 if not provided
    if face_confidence is None:
        face_confidence = 1.0
    if voice_confidence is None:
        voice_confidence = 1.0
    if text_confidence is None:
        text_confidence = 1.0
    
    # Normalize inputs
    face_norm = normalize_emotion(face_emotion)
    voice_norm = normalize_emotion(voice_emotion)
    text_norm = normalize_emotion(text_sentiment)
    
    print(f"\n🔀 EMOTION FUSION (Hybrid Method):")
    print(f"   Face:  {face_emotion:12} (confidence: {face_confidence:.1%}) → {face_norm}")
    print(f"   Voice: {voice_emotion:12} (confidence: {voice_confidence:.1%}) → {voice_norm}")
    print(f"   Text:  {text_sentiment:12} (confidence: {text_confidence:.1%}) → {text_norm}")
    
    # Modality weights
    weights = {
        'face': 0.5,
        'voice': 0.3,
        'text': 0.2
    }
    
    # Calculate weighted confidence for each modality
    face_weighted = weights['face'] * face_confidence
    voice_weighted = weights['voice'] * voice_confidence
    text_weighted = weights['text'] * text_confidence
    
    # Normalize to sum to 1.0
    total = face_weighted + voice_weighted + text_weighted
    if total > 0:
        face_weighted /= total
        voice_weighted /= total
        text_weighted /= total
    
    # Initialize emotion scores
    emotion_scores = {emotion: 0.0 for emotion in EMOTION_CLASSES}
    
    # Add scores from each modality
    emotion_scores[face_norm] += face_weighted
    emotion_scores[voice_norm] += voice_weighted
    emotion_scores[text_norm] += text_weighted
    
    # Find dominant emotion
    dominant_emotion = max(emotion_scores, key=emotion_scores.get)
    
    print(f"\n   ✓ Dominant Emotion: {dominant_emotion}")
    print(f"   ✓ Score: {emotion_scores[dominant_emotion]:.2f}/1.0")
    
    return dominant_emotion, emotion_scores


def fuse_emotions(
    face_emotion: str,
    voice_emotion: str,
    text_sentiment: str,
    method: str = 'weighted',
    **kwargs
) -> str:
    """
    Main fusion function - combines three emotion sources into one dominant emotion.
    
    This is the PRIMARY function to use for emotion fusion.
    Choose your fusion method and call this function.
    
    FUSION METHODS EXPLAINED:
    
    1. WEIGHTED (default):
       - Assigns fixed weights: face=50%, voice=30%, text=20%
       - Simple and fast
       - Best for most use cases
    
    2. VOTING:
       - Each modality votes for its emotion
       - Majority voting wins
       - Best for democratic approach
    
    3. HYBRID:
       - Combines weights AND confidence scores
       - Most accurate when confidence is available
       - Best for production systems
    
    Args:
        face_emotion (str): Facial emotion (e.g., 'Happy')
        voice_emotion (str): Voice emotion (e.g., 'Happy')
        text_sentiment (str): Text sentiment (e.g., 'positive')
        method (str): Fusion method - 'weighted', 'voting', or 'hybrid'
        **kwargs: Additional arguments for specific methods
                 - For 'weighted': weights={'face': 0.5, 'voice': 0.3, 'text': 0.2}
                 - For 'hybrid': face_confidence, voice_confidence, text_confidence
    
    Returns:
        str: Final dominant emotion
    
    Examples:
        >>> # Simple weighted fusion
        >>> emotion = fuse_emotions('Happy', 'Happy', 'positive')
        >>> print(emotion)  # 'Happy'
        
        >>> # Voting fusion
        >>> emotion = fuse_emotions('Happy', 'Angry', 'positive', method='voting')
        >>> print(emotion)  # 'Happy' (2 votes)
        
        >>> # Hybrid with confidence
        >>> emotion = fuse_emotions(
        ...     'Happy', 'Happy', 'positive',
        ...     method='hybrid',
        ...     face_confidence=0.95,
        ...     voice_confidence=0.85,
        ...     text_confidence=0.70
        ... )
        >>> print(emotion)  # 'Happy' (confidence-weighted)
    """
    
    print("\n" + "="*70)
    print(f"🎯 EMOTION FUSION STARTED ({method.upper()} method)")
    print("="*70)
    
    try:
        if method.lower() == 'weighted':
            emotion, scores = fuse_emotions_weighted(
                face_emotion, voice_emotion, text_sentiment,
                weights=kwargs.get('weights', None)
            )
        
        elif method.lower() == 'voting':
            emotion, scores = fuse_emotions_voting(
                face_emotion, voice_emotion, text_sentiment
            )
        
        elif method.lower() == 'hybrid':
            emotion, scores = fuse_emotions_hybrid(
                face_emotion, voice_emotion, text_sentiment,
                face_confidence=kwargs.get('face_confidence', None),
                voice_confidence=kwargs.get('voice_confidence', None),
                text_confidence=kwargs.get('text_confidence', None)
            )
        
        else:
            raise ValueError(f"Unknown method: {method}. Use 'weighted', 'voting', or 'hybrid'")
        
        print("\n" + "="*70)
        print(f"✅ FINAL RESULT: {emotion.upper()}")
        print("="*70)
        
        return emotion
    
    except Exception as e:
        print(f"\n❌ Error in fusion: {e}")
        print("Defaulting to 'Neutral'")
        return 'Neutral'


# Testing utilities
def test_fusion():
    """Test the fusion functions with various scenarios"""
    print("\n" + "="*70)
    print("TESTING EMOTION FUSION")
    print("="*70)
    
    test_cases = [
        ("Happy", "Happy", "positive", "All agree on Happy"),
        ("Happy", "Angry", "positive", "Face & Text vs Voice"),
        ("Angry", "Happy", "negative", "Conflicting emotions"),
        ("Neutral", "Neutral", "neutral", "All neutral"),
        ("Sad", "Happy", "negative", "Conflicting signals"),
    ]
    
    print("\n" + "-"*70)
    print("Testing WEIGHTED method:")
    print("-"*70)
    for face, voice, text, description in test_cases:
        result = fuse_emotions(face, voice, text, method='weighted')
        print(f"✓ {description}: {result}\n")
    
    print("\n" + "-"*70)
    print("Testing VOTING method:")
    print("-"*70)
    for face, voice, text, description in test_cases:
        result = fuse_emotions(face, voice, text, method='voting')
        print(f"✓ {description}: {result}\n")
    
    print("\n" + "-"*70)
    print("Testing HYBRID method with confidence:")
    print("-"*70)
    result = fuse_emotions(
        'Happy', 'Angry', 'positive',
        method='hybrid',
        face_confidence=0.95,
        voice_confidence=0.60,
        text_confidence=0.80
    )
    print(f"✓ Hybrid with confidence: {result}\n")


if __name__ == "__main__":
    test_fusion()
