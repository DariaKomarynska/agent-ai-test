import json
import logging
from typing import Any, Dict

from agents import Agent, Runner, WebSearchTool, handoff, function_tool
from app.schemas import ResearchReport

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@function_tool(
    strict_mode=False,
    name_override='search_trends',
    description_override='Search for trending keywords'
)
async def search_trends(topic: str) -> dict:
    agent = Agent(
        name='TrendTool',
        instructions=(
            "You are TrendSearchTool.  Using the WebSearchTool, look up the last 7 days of activity "
            f"and extract the top 5 trending keywords or phrases related to “{topic}”.  "
            "Consider news sites, social media chatter, and blog headlines.  "
            "Return exactly a JSON object with key “trends” and an array of those keywords."
        ),
        tools=[WebSearchTool()]
    )
    result = await Runner.run(agent, topic)
    return {'trends': result.final_output}

@function_tool(
    strict_mode=False,
    name_override='search_competitors',
    description_override='Search for competitors'
)
async def search_competitors(company: str) -> dict:
    agent = Agent(
        name='CompetitorTool',
       instructions=(
            "You are CompetitorAnalysisTool.  Use the WebSearchTool to identify the top 5 most relevant "
            f"competitors of “{company}”.  For each, gather its name and a one-sentence description of its business focus.  "
            "Return exactly a JSON object with keys “competitors” (array of names) and “analysis” (semicolon-separated summary)."
        ),
        tools=[WebSearchTool()]
    )
    result = await Runner.run(agent, company)
    return {'competitors': result.final_output}

class ResearchAgent:
    def __init__(self):
        self.agent = Agent(
            name="ResearchAgent",
             instructions=(
                "You are ResearchAgent.  1) Summarize the provided company info into “company_analysis”.  "
                "2) If include_trends is true, call transfer_to_search_trends with the company name.  "
                "3) If include_competition is true, call transfer_to_search_competitors with the company name.  "
                "4) Return strictly a JSON matching the ResearchReport schema: "
                "{company_analysis: str, trends: [str], competition: [str]}."
            ),
            tools=[search_trends, search_competitors]
        )

    async def run(self, req: Dict[str, Any]) -> ResearchReport:
        logger.info("Starting research for: %s", req)
        payload = {
            "company_name": req["company_name"],
            "company_description": req["company_description"],
            "company_values": req["company_values"],
            "target_audience": req["target_audience"],
            "include_trends": req["include_trends"],
            "include_competition": req["include_competition"],
            "trend_region": req.get("trend_region", "global"),
        }
        try:
            # Simple string input
            result = await Runner.run(self.agent, json.dumps(payload))
            logger.info("Completed research with result: %s", result)
            return ResearchReport(
                company_analysis=result.final_output,
                trends=[],
                competition={'competitors': [], 'analysis': ''}
            )
            
        except Exception as e:
            logger.exception("Research error")
            raise