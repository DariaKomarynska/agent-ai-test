import logging
from typing import Dict, Any, Optional

from app.api.models import BrandHero, PostContent
from app.services.openai_service import OpenAIService

# Configure logging
logger = logging.getLogger(__name__)

class DALLEService:
    """Service for generating images using DALL-E."""
    
    def __init__(self):
        """Initialize DALL-E service."""
        self.openai_service = OpenAIService()
    
    async def generate_brand_hero_image(
        self,
        brand_hero: BrandHero,
        post_content: PostContent,
        scene_description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate an image of the brand hero in a scene related to the post content.
        
        Args:
            brand_hero: Brand hero information
            post_content: Post content information
            scene_description: Optional specific scene description
            
        Returns:
            Generated image information
        """
        try:
            # Extract key elements from post content
            post_text = post_content.text
            hashtags = " ".join(post_content.hashtags) if post_content.hashtags else ""
            
            # Create base prompt from brand hero description
            base_prompt = f"""
            Create a photorealistic image of {brand_hero.name}, who is {brand_hero.appearance}.
            
            Character personality: {brand_hero.personality}
            
            Scene context: 
            """
            
            # Add scene description based on post content or provided description
            if scene_description:
                scene_prompt = scene_description
            else:
                # Generate scene description based on post content
                scene_prompt = f"The character is in a scene related to: {post_text} {hashtags}"
            
            # Combine prompts
            full_prompt = f"{base_prompt} {scene_prompt}"
            
            # Add guardrails to ensure appropriate content
            guardrails = """
            The image should be:
            - Professional and appropriate for business social media
            - Visually appealing with good composition
            - Well-lit with clear visibility of the character
            - Consistent with the brand hero's description
            - Relevant to the post content
            """
            
            final_prompt = f"{full_prompt}\n\n{guardrails}"
            
            # Generate image
            image_result = await self.openai_service.generate_image(
                prompt=final_prompt,
                size="1024x1024",  # Standard size for social media
            )
            
            return {
                "image_url": image_result["url"],
                "description": scene_prompt,
                "prompt_used": final_prompt,
            }
        
        except Exception as e:
            logger.error(f"Error generating brand hero image: {e}", exc_info=True)
            raise
    
    async def generate_scene_description(
        self, brand_hero: BrandHero, post_content: PostContent
    ) -> str:
        """
        Generate a detailed scene description for the image based on post content.
        
        Args:
            brand_hero: Brand hero information
            post_content: Post content information
            
        Returns:
            Generated scene description
        """
        try:
            # Construct system prompt
            system_prompt = """
            You are an expert visual director for social media content. Your task is to create 
            detailed scene descriptions for images that will accompany social media posts.
            The descriptions should be vivid, specific, and aligned with both the post content 
            and the brand hero character.
            """
            
            # Construct user prompt
            user_prompt = f"""
            Create a detailed scene description for an image featuring the brand hero character.
            
            Brand Hero:
            - Name: {brand_hero.name}
            - Appearance: {brand_hero.appearance}
            - Personality: {brand_hero.personality}
            
            Post Content:
            - Text: {post_content.text}
            - Hashtags: {' '.join(post_content.hashtags) if post_content.hashtags else 'None'}
            - Call to Action: {post_content.call_to_action if post_content.call_to_action else 'None'}
            
            The scene description should:
            1. Be specific about the setting, action, and mood
            2. Include relevant props or elements that connect to the post content
            3. Describe the character's pose, expression, and activity
            4. Suggest lighting, colors, and composition
            5. Be suitable for DALL-E to generate a compelling image
            
            Keep the description under 200 words and focus on visual elements.
            """
            
            # Generate scene description
            response = await self.openai_service.generate_text(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=300,
            )
            
            # Extract and return scene description
            scene_description = response.choices[0].message.content
            return scene_description
        
        except Exception as e:
            logger.error(f"Error generating scene description: {e}", exc_info=True)
            # Fallback to a simple description
            return f"A professional image of {brand_hero.name} related to {post_content.text}"
