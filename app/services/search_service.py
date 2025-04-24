import logging
from typing import Dict, List, Any, Optional

from app.services.openai_service import OpenAIService
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class SearchService:
    """Service for searching trends and competitor information."""
    
    def __init__(self):
        """Initialize search service."""
        self.openai_service = OpenAIService()
        self.max_results = settings.max_search_results
    
    async def search_trends(self, industry: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Search for current trends in the specified industry.
        
        Args:
            industry: Industry to search trends for
            keywords: List of keywords to include in the search
            
        Returns:
            List of trend search results
        """
        try:
            # Construct search query
            query = f"current trends in {industry} " + " ".join(keywords)
            
            # Search for trends
            results = await self.openai_service.search(
                query=query,
                max_results=self.max_results,
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching trends: {e}", exc_info=True)
            raise
    
    async def search_competitors(
        self, company_name: str, industry: str, competitors: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for competitor information.
        
        Args:
            company_name: Name of the company
            industry: Industry of the company
            competitors: List of known competitors (optional)
            
        Returns:
            List of competitor search results
        """
        try:
            # Construct search query
            if competitors and len(competitors) > 0:
                competitor_names = " ".join(competitors)
                query = f"latest social media posts from {competitor_names} in {industry}"
            else:
                query = f"competitors of {company_name} in {industry} social media posts"
            
            # Search for competitor information
            results = await self.openai_service.search(
                query=query,
                max_results=self.max_results,
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching competitors: {e}", exc_info=True)
            raise
    
    async def analyze_search_results(
        self, results: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze search results using OpenAI.
        
        Args:
            results: List of search results to analyze
            context: Context information for analysis
            
        Returns:
            Analysis of search results
        """
        try:
            # Prepare search results for analysis
            results_text = "\n\n".join(
                [
                    f"Title: {result['title']}\nURL: {result['url']}\nSnippet: {result['snippet']}"
                    for result in results
                ]
            )
            
            # Construct system prompt
            system_prompt = """
            You are an expert social media analyst. Your task is to analyze search results and extract 
            key insights that would be valuable for creating engaging social media content.
            Focus on identifying trends, popular topics, content strategies, and audience engagement patterns.
            Provide a structured analysis that can be used to inform social media post creation.
            """
            
            # Construct user prompt
            user_prompt = f"""
            Please analyze these search results in the context of {context.get('industry', 'the industry')}
            for a company named {context.get('company_name', 'the company')}.
            
            Search Results:
            {results_text}
            
            Provide insights on:
            1. Current trending topics
            2. Content strategies that seem to be working
            3. Audience engagement patterns
            4. Potential content ideas based on these results
            
            Format your response as a structured JSON object with these sections.
            """
            
            # Generate analysis
            response = await self.openai_service.generate_text(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.5,
            )
            
            # Extract and return analysis
            analysis = response.choices[0].message.content
            
            # Note: In a real implementation, you would parse the JSON response
            # For now, we'll return a simplified structure
            return {
                "analysis": analysis,
                "source": "search_results",
                "query_context": context,
            }
        
        except Exception as e:
            logger.error(f"Error analyzing search results: {e}", exc_info=True)
            raise
