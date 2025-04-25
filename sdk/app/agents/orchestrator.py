import logging
from typing import List
from agents import Agent, Runner, handoff
from app.schemas import PostProposal, ResearchReport, PostDraft
from app.agents.research_agent import ResearchAgent
from app.agents.content_agent import ContentAgent
from app.agents.image_agent import ImageAgent

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    def __init__(self):
        logger.info("Initializing OrchestratorAgent")
        self.research = ResearchAgent()
        self.content = ContentAgent()
        self.image = ImageAgent()

        # Orchestrator without input_guardrails, manual validation instead
        self.agent = Agent(
            name='OrchestratorAgent',
            instructions=(
                'Orchestrate research, content, and image steps in sequence.'
            ),
            handoffs=[
                handoff(self.research.agent),
                handoff(self.content.agent),
                handoff(self.image.agent)
            ]
        )

    async def generate(self, req: dict) -> List[PostProposal]:
        logger.info("generate() called with request: %s", req)
        # Manual validation
        num = req.get('num_posts')
        if not isinstance(num, int) or num < 0:
            logger.error("Invalid num_posts value: %s", num)
            raise ValueError('`num_posts` must be a non-negative integer')

        # 1. Research
        logger.info("Running ResearchAgent")
        try:
            report: ResearchReport = await self.research.run(req)
            logger.debug("Research report: %s", report)
        except Exception as e:
            logger.exception("Error during research step")
            raise

        # 2. Content drafts
        logger.info("Running ContentAgent with report and brand_hero: %s", req.get('brand_hero'))
        try:
            drafts: List[PostDraft] = await self.content.run(report, req['brand_hero'], num)
            logger.debug("Drafts received: %s", drafts)
        except Exception as e:
            logger.exception("Error during content drafting step")
            raise

        # 3. Generate image proposals
        proposals: List[PostProposal] = []
        for idx, d in enumerate(drafts, start=1):
            content_text = d.content or ''
            logger.info("Processing draft #%d: %s", idx, content_text)
            if not content_text.strip():
                logger.error("Empty draft content at index %d", idx)
                raise ValueError('Draft content cannot be empty')

            logger.info("Running ImageAgent for draft #%d", idx)
            try:
                img = await self.image.run(content_text)
                logger.info("Image result for draft #%d: %s", idx, img)
            except Exception as e:
                logger.exception("Error during image generation for draft #%d", idx)
                raise

            proposal = PostProposal(
                content=content_text,
                hashtags=d.hashtags,
                call_to_action=d.call_to_action,
                scene_description=img['scene_description'],
                image_url=img['image_url']
            )
            proposals.append(proposal)

        logger.info("Generation complete, returning %d proposals", len(proposals))
        return proposals