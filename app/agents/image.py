import logging
from typing import Dict, Any

from openai_agents import Tool, ToolConfig
from openai_agents.tools import FunctionTool

from app.agents.base import BaseAgent
from app.api.models import BrandHero, PostContent, PostImage
from app.services.dalle_service import DALLEService

# Configure logging
logger = logging.getLogger(__name__)

class ImageAgent(BaseAgent):
    """Agent for generating images of the brand hero using OpenAI Agent SDK."""
    
    def __init__(self):
        """Initialize image agent."""
        super().__init__(agent_name="ImageAgent")
        self.dalle_service = DALLEService()
        
        # Define tools for the image agent
        self.agent_config.tools = [
            FunctionTool(
                function=self._generate_scene_description_tool,
                config=ToolConfig(
                    name="generate_scene_description",
                    description="Generate a scene description for an image based on brand hero and post content",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "brand_hero_name": {
                                "type": "string",
                                "description": "Name of the brand hero"
                            },
                            "brand_hero_appearance": {
                                "type": "string",
                                "description": "Appearance of the brand hero"
                            },
                            "brand_hero_personality": {
                                "type": "string",
                                "description": "Personality of the brand hero"
                            },
                            "post_text": {
                                "type": "string",
                                "description": "Text of the post"
                            },
                            "post_hashtags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Hashtags of the post"
                            }
                        },
                        "required": ["brand_hero_name", "brand_hero_appearance", "brand_hero_personality", "post_text"]
                    }
                )
            ),
            FunctionTool(
                function=self._generate_image_tool,
                config=ToolConfig(
                    name="generate_image",
                    description="Generate an image based on scene description",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "scene_description": {
                                "type": "string",
                                "description": "Description of the scene to generate"
                            },
                            "brand_hero_name": {
                                "type": "string",
                                "description": "Name of the brand hero"
                            },
                            "brand_hero_appearance": {
                                "type": "string",
                                "description": "Appearance of the brand hero"
                            }
                        },
                        "required": ["scene_description", "brand_hero_name", "brand_hero_appearance"]
                    }
                )
            )
        ]
        
        # Update agent with tools
        self.agent = self.agent.update_config(self.agent_config)
    
    async def _generate_scene_description_tool(
        self,
        brand_hero_name: str,
        brand_hero_appearance: str,
        brand_hero_personality: str,
        post_text: str,
        post_hashtags: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Tool function to generate a scene description.
        
        Args:
            brand_hero_name: Name of the brand hero
            brand_hero_appearance: Appearance of the brand hero
            brand_hero_personality: Personality of the brand hero
            post_text: Text of the post
            post_hashtags: Hashtags of the post
            
        Returns:
            Scene description
        """
        try:
            # Create a simplified BrandHero and PostContent for the DALLE service
            brand_hero = BrandHero(
                name=brand_hero_name,
                appearance=brand_hero_appearance,
                personality=brand_hero_personality,
                backstory="",  # Not needed for scene description
                values=[],  # Not needed for scene description
                tone_of_voice="",  # Not needed for scene description
            )
            
            post_content = PostContent(
                text=post_text,
                hashtags=post_hashtags or [],
            )
            
            # Generate scene description
            scene_description = await self.dalle_service.generate_scene_description(
                brand_hero=brand_hero,
                post_content=post_content,
            )
            
            return {
                "scene_description": scene_description,
            }
        except Exception as e:
            logger.error(f"Error in generate_scene_description_tool: {e}", exc_info=True)
            return {
                "error": str(e),
                "scene_description": f"A professional image of {brand_hero_name} related to {post_text}",
            }
    
    async def _generate_image_tool(
        self,
        scene_description: str,
        brand_hero_name: str,
        brand_hero_appearance: str,
    ) -> Dict[str, Any]:
        """
        Tool function to generate an image.
        
        Args:
            scene_description: Description of the scene to generate
            brand_hero_name: Name of the brand hero
            brand_hero_appearance: Appearance of the brand hero
            
        Returns:
            Generated image information
        """
        try:
            # Create a simplified BrandHero and PostContent for the DALLE service
            brand_hero = BrandHero(
                name=brand_hero_name,
                appearance=brand_hero_appearance,
                personality="",  # Not needed for image generation
                backstory="",  # Not needed for image generation
                values=[],  # Not needed for image generation
                tone_of_voice="",  # Not needed for image generation
            )
            
            post_content = PostContent(
                text=scene_description,
                hashtags=[],
            )
            
            # Generate image
            image_result = await self.dalle_service.generate_brand_hero_image(
                brand_hero=brand_hero,
                post_content=post_content,
                scene_description=scene_description,
            )
            
            return {
                "image_url": image_result["image_url"],
                "description": image_result["description"],
                "prompt_used": image_result["prompt_used"],
            }
        except Exception as e:
            logger.error(f"Error in generate_image_tool: {e}", exc_info=True)
            return {
                "error": str(e),
                "image_url": "https://via.placeholder.com/1024x1024?text=Image+Generation+Error",
                "description": "Error generating image",
            }
    
    async def generate_image(
        self, brand_hero: BrandHero, post_content: PostContent
    ) -> PostImage:
        """
        Generate an image of the brand hero for a Facebook post.
        
        Args:
            brand_hero: Brand hero information
            post_content: Post content information
            
        Returns:
            Generated image
        """
        try:
            logger.info(f"Generating image for post: {post_content.text[:30]}...")
            
            # Define guardrails
            guardrails = [
                "Create a detailed scene description based on the post content and brand hero",
                "Ensure the scene description is appropriate for image generation",
                "Generate an image that matches the scene description and brand hero",
                "Ensure the image is appropriate for social media",
                "Use the generate_scene_description and generate_image tools in sequence",
            ]
            
            # Create system prompt
            system_prompt = self.create_system_prompt(
                base_prompt="""
                You are an expert visual director for social media content. Your task is to create
                compelling images featuring a brand hero character for Facebook posts.
                
                First, use the generate_scene_description tool to create a detailed scene description
                based on the brand hero and post content.
                
                Then, use the generate_image tool to create an image based on the scene description.
                """,
                guardrails=guardrails,
            )
            
            # Create user prompt
            user_prompt = f"""
            Please generate an image for a Facebook post with the following information:
            
            Brand Hero:
            - Name: {brand_hero.name}
            - Appearance: {brand_hero.appearance}
            - Personality: {brand_hero.personality}
            
            Post Content:
            - Text: {post_content.text}
            - Hashtags: {' '.join(post_content.hashtags) if post_content.hashtags else 'None'}
            - Call to Action: {post_content.call_to_action if post_content.call_to_action else 'None'}
            
            First, create a detailed scene description, then generate an image based on that description.
            """
            
            # Generate image
            response = await self.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
            )
            
            # Parse response to extract image information
            # Note: In a real implementation, we would extract the image URL from the response
            # For now, we'll use the DALLE service directly
            
            # Generate scene description
            scene_description = await self.dalle_service.generate_scene_description(
                brand_hero=brand_hero,
                post_content=post_content,
            )
            
            # Generate image
            image_result = await self.dalle_service.generate_brand_hero_image(
                brand_hero=brand_hero,
                post_content=post_content,
                scene_description=scene_description,
            )
            
            # Create post image
            post_image = PostImage(
                image_url=image_result["image_url"],
                description=image_result["description"],
                prompt_used=image_result["prompt_used"],
            )
            
            return post_image
        
        except Exception as e:
            logger.error(f"Error generating image: {e}", exc_info=True)
            # Return fallback image in case of error
            return PostImage(
                image_url="https://via.placeholder.com/1024x1024?text=Image+Generation+Error",
                description="Error generating image",
            )
    
    async def validate_image_content(self, image_url: str) -> Dict[str, Any]:
        """
        Validate that the image content is appropriate and matches the brand hero.
        
        Args:
            image_url: URL of the image to validate
            
        Returns:
            Validation results
        """
        # Note: This is a placeholder for image content validation
        # In a real implementation, you would use computer vision APIs or
        # other methods to validate the image content
        
        logger.info(f"Validating image content: {image_url}")
        
        # Simulated validation results
        return {
            "is_valid": True,
            "confidence": 0.95,
            "issues": [],
        }
