import json
import logging
from typing import List, Dict
from agents import Agent, Runner, function_tool, handoff
from app.schemas import *

logger = logging.getLogger(__name__)

@function_tool(
    strict_mode=False,
    name_override='generate_brief',
    description_override='Generate a concise content brief based on context and brand hero'
)
async def generate_brief(data: str) -> dict:
    agent = Agent(
        name='BriefTool',
        instructions='Produce a brief for social media posts based on JSON input.'
    )
    res = await Runner.run(agent, data)  # Changed to await
    return {'brief': res.final_output}


@function_tool(
    strict_mode=False,
    name_override='generate_posts',
    description_override='Generate post drafts matching the brief and brand hero style'
)
async def generate_posts(data: str) -> List[dict]:
    agent = Agent(
        name='PostPropositionTool',
        instructions='Produce a list of post drafts given a brief, brand hero, and count in JSON.'
    )
    result = await Runner.run(agent, data)
    if isinstance(result.final_output, str):
        try:
            return json.loads(result.final_output)
        except json.JSONDecodeError:
            return [{'content': result.final_output, 'hashtags': [], 'call_to_action': ''}]
    return result.final_output


class ContentAgent:
    def __init__(self):
        self.agent = Agent(
            name='ContentAgent',
            instructions=(
                "You are ContentAgent.  Input: a single JSON string with keys "
                "`context` (the research report), `brand_hero`, and `num_posts`.  "
                "**Output: exactly and only** the JSON **array** of post drafts—no markdown “```”, "
                "no code fences, no extra text.  Each element must be an object with keys "
                "`content` (string), `hashtags` (array of strings), and `call_to_action` (string)."
            ),
            tools=[generate_brief, generate_posts]
        )

    async def run(self, context: Dict[str, any], brand_hero: str, num_posts: int) -> List[PostDraft]:
        if not isinstance(context, dict):
            context = context.dict()  # convert ResearchReport → dict
            payload = json.dumps({
            "context": context,
            "brand_hero": brand_hero,
            "num_posts": num_posts
           })
        result = await Runner.run(self.agent, payload)
        raw = result.final_output

        # Simplest parse: if string, try JSON; otherwise assume list
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("Could not parse ContentAgent output as JSON; got %r", raw)
                raw = []

        # Build PostDrafts; let Pydantic catch any missing fields
        drafts: List[PostDraft] = []
        for item in raw or []:
            try:
                drafts.append(PostDraft(**item))
            except Exception as ex:
                logger.warning("Skipping invalid draft item %r: %s", item, ex)

        if not drafts:
            logger.error("ContentAgent returned no valid drafts")
            # Optional fallback or raise
            drafts = [PostDraft(content="Default content", hashtags=[], call_to_action="")]

        return drafts