import logging
import json
import uuid
import asyncio
from typing import Dict, List, Any, AsyncGenerator

from openai_agents import Tool, ToolConfig
from openai_agents.tools import FunctionTool

from app.agents.base import BaseAgent
from app.api.models import BrandHero, PostContent, PostResponse

# Configure logging
logger = logging.getLogger(__name__)

class ContentAgent(BaseAgent):
    """Agent for generating Facebook post content using OpenAI Agent SDK."""
    
    def __init__(self):
        """Initialize content agent."""
        super().__init__(agent_name="ContentAgent")
        
        # Define tools for the content agent
        self.agent_config.tools = [
            FunctionTool(
                function=self._generate_post_tool,
                config=ToolConfig(
                    name="generate_post",
                    description="Generate a Facebook post based on content brief and brand hero",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "content_brief": {
                                "type": "string",
                                "description": "Content brief for the post"
                            },
                            "brand_hero_name": {
                                "type": "string",
                                "description": "Name of the brand hero"
                            },
                            "brand_hero_tone": {
                                "type": "string",
                                "description": "Tone of voice of the brand hero"
                            },
                            "proposal_num": {
                                "type": "integer",
                                "description": "Proposal number"
                            }
                        },
                        "required": ["content_brief", "brand_hero_name", "brand_hero_tone", "proposal_num"]
                    }
                )
            )
        ]
        
        # Update agent with tools
        self.agent = self.agent.update_config(self.agent_config)
    
    async def _generate_post_tool(
        self, content_brief: str, brand_hero_name: str, brand_hero_tone: str, proposal_num: int
    ) -> Dict[str, Any]:
        """
        Tool function to generate a Facebook post.
        
        Args:
            content_brief: Content brief for the post
            brand_hero_name: Name of the brand hero
            brand_hero_tone: Tone of voice of the brand hero
            proposal_num: Proposal number
            
        Returns:
            Generated post content
        """
        try:
            # Create post content
            post_content = {
                "text": f"This is a Facebook post by {brand_hero_name} with {brand_hero_tone} tone (proposal #{proposal_num})",
                "hashtags": [f"#{brand_hero_name.lower().replace(' ', '')}", "#facebook", "#post"],
                "call_to_action": "Learn more about our products!"
            }
            
            return post_content
        except Exception as e:
            logger.error(f"Error in generate_post_tool: {e}", exc_info=True)
            return {
                "error": str(e),
                "text": f"Error generating post content for proposal #{proposal_num}",
                "hashtags": ["#error"]
            }
    
    async def generate_post_proposals(
        self,
        context_report: Dict[str, Any],
        brand_hero: BrandHero,
        num_proposals: int = 10,
    ) -> AsyncGenerator[PostResponse, None]:
        """
        Generate Facebook post proposals based on context report and brand hero.
        
        Args:
            context_report: Context report from research agent
            brand_hero: Brand hero information
            num_proposals: Number of post proposals to generate
            
        Yields:
            Post proposals
        """
        try:
            logger.info(f"Generating {num_proposals} post proposals")
            
            # Create content brief
            content_brief = await self._create_content_brief(context_report, brand_hero)
            
            # Generate post proposals in batches to avoid overwhelming the API
            batch_size = 3
            for batch_start in range(0, num_proposals, batch_size):
                batch_end = min(batch_start + batch_size, num_proposals)
                batch_tasks = []
                
                for i in range(batch_start, batch_end):
                    proposal_num = i + 1
                    task = self._generate_post_proposal(content_brief, brand_hero, proposal_num)
                    batch_tasks.append(task)
                
                # Wait for all tasks in the batch to complete
                batch_results = await asyncio.gather(*batch_tasks)
                
                # Yield results
                for post_response in batch_results:
                    yield post_response
        
        except Exception as e:
            logger.error(f"Error generating post proposals: {e}", exc_info=True)
            raise
    
    async def _create_content_brief(
        self, context_report: Dict[str, Any], brand_hero: BrandHero
    ) -> str:
        """
        Create a content brief based on context report and brand hero.
        
        Args:
            context_report: Context report from research agent
            brand_hero: Brand hero information
            
        Returns:
            Content brief
        """
        try:
            # Prepare brand hero information
            brand_hero_dict = brand_hero.dict()
            brand_hero_json = json.dumps(brand_hero_dict, indent=2)
            
            # Prepare context report
            context_report_json = json.dumps(context_report, indent=2, default=str)
            
            # Define guardrails
            guardrails = [
                "Focus on creating actionable content guidelines",
                "Ensure alignment with brand values and tone of voice",
                "Incorporate insights from research",
                "Provide specific direction for content creation",
                "Structure the brief in a way that facilitates content generation",
                "Format your response as a comprehensive content brief, not as JSON",
            ]
            
            # Create system prompt
            system_prompt = self.create_system_prompt(
                base_prompt="""
                You are an expert social media content strategist. Your task is to create
                a comprehensive content brief that will guide the creation of engaging
                Facebook posts for a brand hero character.
                """,
                guardrails=guardrails,
            )
            
            # Create user prompt
            user_prompt = f"""
            Please create a content brief for Facebook posts based on the following information:
            
            BRAND HERO:
            {brand_hero_json}
            
            RESEARCH INSIGHTS:
            {context_report_json}
            
            In your content brief, include:
            1. Key themes and topics to address
            2. Tone and style guidelines aligned with the brand hero's personality
            3. Content structure recommendations
            4. Hashtag strategy
            5. Call-to-action approaches
            6. Content variation suggestions to maintain audience interest
            
            Create a comprehensive and detailed brief that can be used to generate multiple unique Facebook posts.
            """
            
            # Generate content brief
            content_brief = await self.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
            )
            
            return content_brief
        
        except Exception as e:
            logger.error(f"Error creating content brief: {e}", exc_info=True)
            raise
    
    async def _generate_post_proposal(
        self, content_brief: str, brand_hero: BrandHero, proposal_num: int
    ) -> PostResponse:
        """
        Generate a Facebook post proposal.
        
        Args:
            content_brief: Content brief
            brand_hero: Brand hero information
            proposal_num: Proposal number
            
        Returns:
            Post response
        """
        try:
            # Define guardrails
            guardrails = [
                f"Write in the voice of {brand_hero.name}, with {brand_hero.tone_of_voice} tone",
                "Create engaging content that resonates with the target audience",
                "Include relevant hashtags (2-5) that enhance discoverability",
                "Keep the main post text under 280 characters for optimal engagement",
                "Include a clear call-to-action when appropriate",
                "Ensure content aligns with brand values and messaging",
                "Avoid controversial or potentially offensive content",
                "Format your response as a JSON object with text, hashtags, and call_to_action fields",
            ]
            
            # Create system prompt
            system_prompt = self.create_system_prompt(
                base_prompt=f"""
                You are {brand_hero.name}, a brand hero for a company. 
                {brand_hero.backstory}
                
                Your personality is {brand_hero.personality}
                
                Your values are: {', '.join(brand_hero.values)}
                
                You communicate with a {brand_hero.tone_of_voice} tone.
                
                Your task is to create engaging Facebook posts that represent the brand
                and connect with the audience.
                """,
                guardrails=guardrails,
            )
            
            # Create user prompt
            user_prompt = f"""
            Please create Facebook post #{proposal_num} based on the following content brief:
            
            {content_brief}
            
            Make this post unique and different from other proposals. Focus on a specific
            aspect of the brief to ensure variety across all posts.
            
            Format your response as a JSON object with:
            1. "text": The main post text (under 280 characters)
            2. "hashtags": An array of 2-5 relevant hashtags
            3. "call_to_action": An optional call-to-action
            """
            
            # Generate post content
            response = await self.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.8,  # Higher temperature for more creativity
            )
            
            # Parse JSON response
            try:
                content_json = json.loads(response)
                post_content = PostContent(
                    text=content_json.get("text", ""),
                    hashtags=content_json.get("hashtags", []),
                    call_to_action=content_json.get("call_to_action"),
                )
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning(f"Failed to parse JSON response: {response}")
                post_content = PostContent(
                    text=f"Post proposal #{proposal_num}",
                    hashtags=["#fallback"],
                )
            
            # Create post response
            post_response = PostResponse(
                id=str(uuid.uuid4()),
                content=post_content,
                inspiration={
                    "source": f"Proposal {proposal_num}",
                    "brief_excerpt": content_brief[:100] + "..." if len(content_brief) > 100 else content_brief,
                },
            )
            
            return post_response
        
        except Exception as e:
            logger.error(f"Error generating post proposal: {e}", exc_info=True)
            # Return fallback content in case of error
            post_content = PostContent(
                text=f"Error generating post content for proposal #{proposal_num}",
                hashtags=["#error"],
            )
            
            return PostResponse(
                id=str(uuid.uuid4()),
                content=post_content,
                inspiration={
                    "source": f"Error in proposal {proposal_num}",
                    "error": str(e),
                },
            )
