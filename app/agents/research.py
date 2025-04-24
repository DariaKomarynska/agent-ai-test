import logging
import json
from typing import Dict, List, Any, Optional

from openai_agents import Tool, ToolConfig, ToolCallResult
from openai_agents.tools import FunctionTool

from app.agents.base import BaseAgent
from app.api.models import CompanyContext
from app.services.search_service import SearchService

# Configure logging
logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    """Agent for researching context, trends, and competitors using OpenAI Agent SDK."""
    
    def __init__(self):
        """Initialize research agent."""
        super().__init__(agent_name="ResearchAgent")
        self.search_service = SearchService()
        
        # Define tools for the research agent
        self.agent_config.tools = [
            FunctionTool(
                function=self._search_trends_tool,
                config=ToolConfig(
                    name="search_trends",
                    description="Search for current trends in a specific industry",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "industry": {
                                "type": "string",
                                "description": "The industry to search trends for"
                            },
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Keywords to include in the search"
                            }
                        },
                        "required": ["industry", "keywords"]
                    }
                )
            ),
            FunctionTool(
                function=self._search_competitors_tool,
                config=ToolConfig(
                    name="search_competitors",
                    description="Search for competitor information",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "company_name": {
                                "type": "string",
                                "description": "Name of the company"
                            },
                            "industry": {
                                "type": "string",
                                "description": "Industry of the company"
                            },
                            "competitors": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of known competitors (optional)"
                            }
                        },
                        "required": ["company_name", "industry"]
                    }
                )
            )
        ]
        
        # Update agent with tools
        self.agent = self.agent.update_config(self.agent_config)
    
    async def _search_trends_tool(self, industry: str, keywords: List[str]) -> Dict[str, Any]:
        """
        Tool function to search for trends.
        
        Args:
            industry: Industry to search trends for
            keywords: Keywords to include in the search
            
        Returns:
            Trend search results
        """
        try:
            # Search for trends
            trend_results = await self.search_service.search_trends(
                industry=industry,
                keywords=keywords,
            )
            
            return {
                "results": trend_results,
                "source": "trend_research",
            }
        except Exception as e:
            logger.error(f"Error in search_trends_tool: {e}", exc_info=True)
            return {
                "error": str(e),
                "source": "trend_research",
            }
    
    async def _search_competitors_tool(
        self, company_name: str, industry: str, competitors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Tool function to search for competitors.
        
        Args:
            company_name: Name of the company
            industry: Industry of the company
            competitors: List of known competitors (optional)
            
        Returns:
            Competitor search results
        """
        try:
            # Search for competitor information
            competitor_results = await self.search_service.search_competitors(
                company_name=company_name,
                industry=industry,
                competitors=competitors,
            )
            
            return {
                "results": competitor_results,
                "source": "competitor_research",
            }
        except Exception as e:
            logger.error(f"Error in search_competitors_tool: {e}", exc_info=True)
            return {
                "error": str(e),
                "source": "competitor_research",
            }
    
    async def generate_context_report(
        self,
        company_context: CompanyContext,
        include_trends: bool = True,
        include_competitors: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a context report based on company information, trends, and competitors.
        
        Args:
            company_context: Company context information
            include_trends: Whether to include trend research
            include_competitors: Whether to include competitor research
            
        Returns:
            Context report
        """
        try:
            logger.info(f"Generating context report for {company_context.name}")
            
            # Prepare company context for analysis
            context_dict = company_context.dict()
            context_json = json.dumps(context_dict, indent=2)
            
            # Define guardrails
            guardrails = [
                "Focus on extracting actionable insights for social media content",
                "Identify key themes and values that should be emphasized",
                "Determine appropriate tone and style based on company values and target audience",
                "Use the search_trends and search_competitors tools to gather additional information",
                "Structure your analysis in a way that can be easily used for content creation",
                "Format your final response as a structured JSON object with company_analysis, trends, competitors, and insights sections",
            ]
            
            # Create system prompt
            system_prompt = self.create_system_prompt(
                base_prompt="""
                You are an expert business analyst specializing in social media strategy.
                Your task is to analyze company information and research trends and competitors
                to create a comprehensive context report for social media content creation.
                
                Use the search_trends tool to find current trends in the company's industry.
                Use the search_competitors tool to find information about the company's competitors.
                
                Analyze all the information and provide actionable insights for social media content creation.
                """,
                guardrails=guardrails,
            )
            
            # Create user prompt
            user_prompt = f"""
            Please analyze the following company information and create a comprehensive context report:
            
            {context_json}
            
            Include the following in your analysis:
            1. Company analysis: Key brand values, target audience, tone and style, unique selling points
            2. Trends analysis: Current trends in the industry (if include_trends is {include_trends})
            3. Competitor analysis: What competitors are doing on social media (if include_competitors is {include_competitors})
            4. Insights: Key themes, content opportunities, recommended approaches, specific content ideas
            
            Format your response as a structured JSON object with these sections.
            """
            
            # Generate context report
            response = await self.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.5,
            )
            
            # Parse JSON response
            try:
                report = json.loads(response)
            except json.JSONDecodeError:
                # If response is not valid JSON, return it as-is
                report = {
                    "raw_response": response,
                    "error": "Failed to parse JSON response",
                }
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating context report: {e}", exc_info=True)
            raise
