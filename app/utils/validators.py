import logging
import re
from typing import Dict, List, Any, Optional

from app.api.models import PostGenerationRequest, PostContent, PostImage
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

def validate_post_generation_request(request: PostGenerationRequest) -> Dict[str, Any]:
    """
    Validate a post generation request.
    
    Args:
        request: Post generation request
        
    Returns:
        Validation results
    """
    errors = []
    warnings = []
    
    # Validate company context
    if not request.company_context.name:
        errors.append("Company name is required")
    
    if not request.company_context.description:
        errors.append("Company description is required")
    
    if not request.company_context.values or len(request.company_context.values) == 0:
        errors.append("Company values are required")
    
    if not request.company_context.target_audience or len(request.company_context.target_audience) == 0:
        errors.append("Target audience is required")
    
    if not request.company_context.industry:
        errors.append("Industry is required")
    
    # Validate brand hero
    if not request.brand_hero.name:
        errors.append("Brand hero name is required")
    
    if not request.brand_hero.appearance:
        errors.append("Brand hero appearance is required")
    
    if not request.brand_hero.personality:
        errors.append("Brand hero personality is required")
    
    if not request.brand_hero.backstory:
        errors.append("Brand hero backstory is required")
    
    if not request.brand_hero.values or len(request.brand_hero.values) == 0:
        errors.append("Brand hero values are required")
    
    # Validate num_proposals
    if request.num_proposals < settings.min_proposals:
        warnings.append(
            f"Requested {request.num_proposals} proposals, which is below the minimum of {settings.min_proposals}. "
            f"Will use minimum value."
        )
    
    if request.num_proposals > settings.max_proposals:
        warnings.append(
            f"Requested {request.num_proposals} proposals, which is above the maximum of {settings.max_proposals}. "
            f"Will use maximum value."
        )
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }

def validate_post_content(content: PostContent) -> Dict[str, Any]:
    """
    Validate post content.
    
    Args:
        content: Post content
        
    Returns:
        Validation results
    """
    errors = []
    warnings = []
    
    # Validate text
    if not content.text:
        errors.append("Post text is required")
    
    if len(content.text) > 280:
        warnings.append(
            f"Post text is too long ({len(content.text)} characters). "
            f"Will be truncated to 280 characters."
        )
    
    # Validate hashtags
    if not content.hashtags or len(content.hashtags) == 0:
        warnings.append("Post has no hashtags. Will add default hashtag.")
    
    if content.hashtags and len(content.hashtags) > 5:
        warnings.append(
            f"Post has too many hashtags ({len(content.hashtags)}). "
            f"Will limit to 5."
        )
    
    # Validate hashtag format
    if content.hashtags:
        for i, hashtag in enumerate(content.hashtags):
            if not hashtag.startswith("#"):
                warnings.append(
                    f"Hashtag '{hashtag}' does not start with #. "
                    f"Will add # prefix."
                )
            
            # Check for invalid characters
            if re.search(r"[^a-zA-Z0-9#_]", hashtag):
                warnings.append(
                    f"Hashtag '{hashtag}' contains invalid characters. "
                    f"Will remove invalid characters."
                )
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }

def validate_post_image(image: PostImage) -> Dict[str, Any]:
    """
    Validate post image.
    
    Args:
        image: Post image
        
    Returns:
        Validation results
    """
    errors = []
    warnings = []
    
    # Validate image URL
    if not image.image_url:
        errors.append("Image URL is required")
    
    # Validate description
    if not image.description:
        warnings.append("Image has no description")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
