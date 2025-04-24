import logging
import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

def generate_unique_id() -> str:
    """
    Generate a unique ID.
    
    Returns:
        Unique ID
    """
    return str(uuid.uuid4())

def format_hashtags(hashtags: List[str]) -> List[str]:
    """
    Format hashtags to ensure they are valid.
    
    Args:
        hashtags: List of hashtags
        
    Returns:
        Formatted hashtags
    """
    formatted_hashtags = []
    
    for hashtag in hashtags:
        # Ensure hashtag starts with #
        if not hashtag.startswith("#"):
            hashtag = f"#{hashtag}"
        
        # Remove invalid characters
        hashtag = re.sub(r"[^a-zA-Z0-9#_]", "", hashtag)
        
        # Add to formatted hashtags
        formatted_hashtags.append(hashtag)
    
    return formatted_hashtags

def truncate_text(text: str, max_length: int = 280) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    Format a timestamp.
    
    Args:
        timestamp: Timestamp to format (default: current time)
        
    Returns:
        Formatted timestamp
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def sanitize_input(text: str) -> str:
    """
    Sanitize input text to prevent injection attacks.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove HTML tags
    text = re.sub(r"<[^>]*>", "", text)
    
    # Remove script tags and content
    text = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.DOTALL)
    
    # Remove other potentially dangerous patterns
    text = re.sub(r"javascript:", "", text)
    text = re.sub(r"on\w+\s*=", "", text)
    
    return text

def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of keywords
    """
    # Note: This is a simple implementation
    # In a real application, you would use NLP techniques
    
    # Remove punctuation and convert to lowercase
    text = re.sub(r"[^\w\s]", "", text.lower())
    
    # Split into words
    words = text.split()
    
    # Remove common stop words
    stop_words = {
        "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
        "when", "where", "how", "who", "which", "this", "that", "these", "those",
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "to", "at", "in", "on", "for", "with", "by", "about",
        "of", "from", "up", "down", "into", "over", "under", "again", "further",
        "then", "once", "here", "there", "all", "any", "both", "each", "few",
        "more", "most", "other", "some", "such", "no", "nor", "not", "only",
        "own", "same", "so", "than", "too", "very", "can", "will", "just", "should",
        "now",
    }
    
    filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
    
    # Count word frequencies
    word_counts = {}
    for word in filtered_words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    
    # Sort by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Extract top keywords
    keywords = [word for word, count in sorted_words[:max_keywords]]
    
    return keywords
