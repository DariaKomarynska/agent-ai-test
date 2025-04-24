import logging
import uuid
import asyncio
from typing import Dict, List, Any, AsyncGenerator

from openai_agents import Tool, ToolConfig
from openai_agents.tools import FunctionTool

from app.agents.base import BaseAgent
from app.agents.research import ResearchAgent
from app.agents.content import ContentAgent
from app.agents.image import ImageAgent
from app.api.models import PostGenerationRequest, PostResponse, CompanyContext, BrandHero, PostContent, PostImage
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class OrchestratorAgent(BaseAgent):
    """Agent for orchestrating the work of other agents using OpenAI Agent SDK."""
    
    def __init__(self):
        """Initialize orchestrator agent."""
        super().__init__(agent_name="OrchestratorAgent")
        self.research_agent = ResearchAgent()
        self.content_agent = ContentAgent()
        self.image_agent = ImageAgent()
        
        # Define tools for the orchestrator agent
        self.agent_config.tools = [
            FunctionTool(
                function=self._research_context_tool,
                config=ToolConfig(
                    name="research_context",
                    description="Research context for post generation",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "company_name": {
                                "type": "string",
                                "description": "Name of the company"
                            },
                            "company_description": {
                                "type": "string",
                                "description": "Description of the company"
                            },
                            "industry": {
                                "type": "string",
                                "description": "Industry of the company"
                            },
                            "include_trends": {
                                "type": "boolean",
                                "description": "Whether to include trend research"
                            },
                            "include_competitors": {
                                "type": "boolean",
                                "description": "Whether to include competitor research"
                            }
                        },
                        "required": ["company_name", "company_description", "industry"]
                    }
                )
            ),
            FunctionTool(
                function=self._generate_post_proposals_tool,
                config=ToolConfig(
                    name="generate_post_proposals",
                    description="Generate post proposals based on context report and brand hero",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "context_report_json": {
                                "type": "string",
                                "description": "JSON string of the context report"
                            },
                            "brand_hero_json": {
                                "type": "string",
                                "description": "JSON string of the brand hero information"
                            },
                            "num_proposals": {
                                "type": "integer",
                                "description": "Number of post proposals to generate"
                            }
                        },
                        "required": ["context_report_json", "brand_hero_json", "num_proposals"]
                    }
                )
            ),
            FunctionTool(
                function=self._generate_image_tool,
                config=ToolConfig(
                    name="generate_image",
                    description="Generate an image for a post",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "brand_hero_json": {
                                "type": "string",
                                "description": "JSON string of the brand hero information"
                            },
                            "post_content_json": {
                                "type": "string",
                                "description": "JSON string of the post content"
                            }
                        },
                        "required": ["brand_hero_json", "post_content_json"]
                    }
                )
            ),
            FunctionTool(
                function=self._apply_guardrails_tool,
                config=ToolConfig(
                    name="apply_guardrails",
                    description="Apply guardrails to a post",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "post_json": {
                                "type": "string",
                                "description": "JSON string of the post"
                            }
                        },
                        "required": ["post_json"]
                    }
                )
            )
        ]
        
        # Update agent with tools
        self.agent = self.agent.update_config(self.agent_config)
    
    async def _research_context_tool(
        self,
        company_name: str,
        company_description: str,
        industry: str,
        include_trends: bool = True,
        include_competitors: bool = True,
    ) -> Dict[str, Any]:
        """
        Tool function to research context.
        
        Args:
            company_name: Name of the company
            company_description: Description of the company
            industry: Industry of the company
            include_trends: Whether to include trend research
            include_competitors: Whether to include competitor research
            
        Returns:
            Context report
        """
        try:
            # Create a simplified CompanyContext for the research agent
            company_context = CompanyContext(
                name=company_name,
                description=company_description,
                industry=industry,
                values=["value1", "value2"],  # Placeholder values
                target_audience=["audience1", "audience2"],  # Placeholder audience
                tone_of_voice="professional",  # Placeholder tone
            )
            
            # Generate context report
            context_report = await self.research_agent.generate_context_report(
                company_context=company_context,
                include_trends=include_trends,
                include_competitors=include_competitors,
            )
            
            return context_report
        except Exception as e:
            logger.error(f"Error in research_context_tool: {e}", exc_info=True)
            return {
                "error": str(e),
                "company_analysis": {
                    "analysis": "Error analyzing company context",
                    "source": "company_context",
                },
                "trends": None,
                "competitors": None,
                "insights": {
                    "insights": "Error generating insights",
                    "source": "research_synthesis",
                },
            }
    
    async def _generate_post_proposals_tool(
        self,
        context_report_json: str,
        brand_hero_json: str,
        num_proposals: int,
    ) -> Dict[str, Any]:
        """
        Tool function to generate post proposals.
        
        Args:
            context_report_json: JSON string of the context report
            brand_hero_json: JSON string of the brand hero information
            num_proposals: Number of post proposals to generate
            
        Returns:
            List of post proposals
        """
        try:
            # Parse JSON strings
            context_report = json.loads(context_report_json)
            brand_hero_dict = json.loads(brand_hero_json)
            
            # Create BrandHero object
            brand_hero = BrandHero(**brand_hero_dict)
            
            # Generate post proposals
            post_proposals = []
            async for post_proposal in self.content_agent.generate_post_proposals(
                context_report=context_report,
                brand_hero=brand_hero,
                num_proposals=num_proposals,
            ):
                post_proposals.append(post_proposal.dict())
            
            return {
                "post_proposals": post_proposals,
            }
        except Exception as e:
            logger.error(f"Error in generate_post_proposals_tool: {e}", exc_info=True)
            return {
                "error": str(e),
                "post_proposals": [],
            }
    
    async def _generate_image_tool(
        self,
        brand_hero_json: str,
        post_content_json: str,
    ) -> Dict[str, Any]:
        """
        Tool function to generate an image for a post.
        
        Args:
            brand_hero_json: JSON string of the brand hero information
            post_content_json: JSON string of the post content
            
        Returns:
            Generated image information
        """
        try:
            # Parse JSON strings
            brand_hero_dict = json.loads(brand_hero_json)
            post_content_dict = json.loads(post_content_json)
            
            # Create objects
            brand_hero = BrandHero(**brand_hero_dict)
            post_content = PostContent(**post_content_dict)
            
            # Generate image
            post_image = await self.image_agent.generate_image(
                brand_hero=brand_hero,
                post_content=post_content,
            )
            
            return post_image.dict()
        except Exception as e:
            logger.error(f"Error in generate_image_tool: {e}", exc_info=True)
            return {
                "error": str(e),
                "image_url": "https://via.placeholder.com/1024x1024?text=Image+Generation+Error",
                "description": "Error generating image",
            }
    
    async def _apply_guardrails_tool(
        self,
        post_json: str,
    ) -> Dict[str, Any]:
        """
        Tool function to apply guardrails to a post.
        
        Args:
            post_json: JSON string of the post
            
        Returns:
            Validated post
        """
        try:
            # Parse JSON string
            post_dict = json.loads(post_json)
            
            # Create PostResponse object
            post = PostResponse(**post_dict)
            
            # Apply guardrails
            validated_post = self._apply_post_guardrails(post)
            
            return validated_post.dict()
        except Exception as e:
            logger.error(f"Error in apply_guardrails_tool: {e}", exc_info=True)
            return {
                "error": str(e),
                "post": post_dict,
            }
    
    async def process_request(
        self, request: PostGenerationRequest
    ) -> AsyncGenerator[PostResponse, None]:
        """
        Process a post generation request.
        
        Args:
            request: Post generation request
            
        Yields:
            Post responses
        """
        try:
            logger.info(f"Processing request for {request.company_context.name}")
            
            # Apply guardrails to request
            validated_request = self._apply_request_guardrails(request)
            
            # Step 1: Research context
            self.log_handoff(
                to_agent="ResearchAgent",
                context={
                    "company_name": validated_request.company_context.name,
                    "include_trends": validated_request.include_trends,
                    "include_competitors": validated_request.include_competitors,
                },
            )
            
            context_report = await self.research_agent.generate_context_report(
                company_context=validated_request.company_context,
                include_trends=validated_request.include_trends,
                include_competitors=validated_request.include_competitors,
            )
            
            # Step 2: Generate post proposals
            self.log_handoff(
                to_agent="ContentAgent",
                context={
                    "brand_hero_name": validated_request.brand_hero.name,
                    "num_proposals": validated_request.num_proposals,
                },
            )
            
            async for post_proposal in self.content_agent.generate_post_proposals(
                context_report=context_report,
                brand_hero=validated_request.brand_hero,
                num_proposals=validated_request.num_proposals,
            ):
                # Step 3: Generate image for each post
                self.log_handoff(
                    to_agent="ImageAgent",
                    context={
                        "post_id": post_proposal.id,
                        "brand_hero_name": validated_request.brand_hero.name,
                    },
                )
                
                post_image = await self.image_agent.generate_image(
                    brand_hero=validated_request.brand_hero,
                    post_content=post_proposal.content,
                )
                
                # Update post proposal with image
                post_proposal.image = post_image
                
                # Apply guardrails to post
                validated_post = self._apply_post_guardrails(post_proposal)
                
                yield validated_post
        
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            raise
    
    def _apply_request_guardrails(self, request: PostGenerationRequest) -> PostGenerationRequest:
        """
        Apply guardrails to the request.
        
        Args:
            request: Post generation request
            
        Returns:
            Validated request
        """
        # Ensure num_proposals is within acceptable range
        if request.num_proposals < settings.min_proposals:
            logger.warning(
                f"Requested {request.num_proposals} proposals, which is below the minimum of {settings.min_proposals}. "
                f"Using minimum value."
            )
            request.num_proposals = settings.min_proposals
        
        if request.num_proposals > settings.max_proposals:
            logger.warning(
                f"Requested {request.num_proposals} proposals, which is above the maximum of {settings.max_proposals}. "
                f"Using maximum value."
            )
            request.num_proposals = settings.max_proposals
        
        return request
    
    def _apply_post_guardrails(self, post: PostResponse) -> PostResponse:
        """
        Apply guardrails to the post.
        
        Args:
            post: Post response
            
        Returns:
            Validated post
        """
        # Ensure post text is not too long
        if len(post.content.text) > 280:
            logger.warning(
                f"Post text is too long ({len(post.content.text)} characters). Truncating to 280 characters."
            )
            post.content.text = post.content.text[:277] + "..."
        
        # Ensure post has hashtags
        if not post.content.hashtags or len(post.content.hashtags) == 0:
            logger.warning("Post has no hashtags. Adding default hashtag.")
            post.content.hashtags = ["#post"]
        
        # Ensure post has at most 5 hashtags
        if len(post.content.hashtags) > 5:
            logger.warning(
                f"Post has too many hashtags ({len(post.content.hashtags)}). Limiting to 5."
            )
            post.content.hashtags = post.content.hashtags[:5]
        
        return post
