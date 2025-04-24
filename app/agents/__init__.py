"""
Agents package for Facebook post generation using OpenAI Agent SDK.

This package contains specialized agents for different tasks:
- BaseAgent: Foundation class for all agents
- ResearchAgent: Researches company context, trends, and competitors
- ContentAgent: Generates Facebook post content
- ImageAgent: Creates images of the brand hero
- OrchestratorAgent: Coordinates the work of other agents
"""

from app.agents.base import BaseAgent
from app.agents.research import ResearchAgent
from app.agents.content import ContentAgent
from app.agents.image import ImageAgent
from app.agents.orchestrator import OrchestratorAgent

__all__ = [
    "BaseAgent",
    "ResearchAgent",
    "ContentAgent",
    "ImageAgent",
    "OrchestratorAgent",
]
