import logging
import uuid
from typing import Any, Dict, List, Optional, AsyncGenerator

from openai import OpenAI
from openai.types.beta.threads import Run
from openai.types.beta.threads.thread_message import ThreadMessage
from openai_agents import Agent, AgentConfig, Message, Thread, ThreadConfig

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all agents using OpenAI Agent SDK."""
    
    def __init__(self, agent_name: str = "BaseAgent"):
        """
        Initialize base agent.
        
        Args:
            agent_name: Name of the agent
        """
        self.agent_name = agent_name
        self.agent_id = str(uuid.uuid4())
        self.client = OpenAI(api_key=settings.openai_api_key)
        
        # Initialize agent configuration
        self.agent_config = AgentConfig(
            name=agent_name,
            description=f"A {agent_name} that helps with generating Facebook posts",
            model=settings.openai_model,
            tools=[],  # Will be overridden by subclasses
            instructions=self._get_default_instructions(),
        )
        
        # Create agent instance
        self.agent = Agent(config=self.agent_config)
    
    def _get_default_instructions(self) -> str:
        """
        Get default instructions for the agent.
        
        Returns:
            Default instructions
        """
        return f"""
        You are a {self.agent_name} that helps with generating Facebook posts.
        
        GUARDRAILS:
        - Always provide accurate and helpful information
        - Maintain a professional tone
        - Respect user privacy and data security
        - Avoid generating harmful or inappropriate content
        """
    
    async def create_thread(self) -> Thread:
        """
        Create a new thread for the agent.
        
        Returns:
            New thread
        """
        thread_config = ThreadConfig()
        return Thread(config=thread_config)
    
    async def add_message_to_thread(self, thread: Thread, content: str, role: str = "user") -> None:
        """
        Add a message to a thread.
        
        Args:
            thread: Thread to add message to
            content: Message content
            role: Message role (user or assistant)
        """
        message = Message(role=role, content=content)
        await thread.add_message(message)
    
    async def run_thread(self, thread: Thread) -> Run:
        """
        Run a thread with the agent.
        
        Args:
            thread: Thread to run
            
        Returns:
            Run object
        """
        return await self.agent.run_thread(thread)
    
    async def get_response(self, thread: Thread, run: Run) -> List[ThreadMessage]:
        """
        Get response messages from a run.
        
        Args:
            thread: Thread that was run
            run: Run object
            
        Returns:
            List of response messages
        """
        return await thread.get_messages(run=run)
    
    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a response using the agent.
        
        Args:
            system_prompt: System prompt for the agent
            user_prompt: User prompt for the agent
            temperature: Temperature for generation
            
        Returns:
            Generated response
        """
        try:
            # Log agent activity
            logger.info(f"Agent {self.agent_name} ({self.agent_id}) generating response")
            
            # Update agent instructions with system prompt
            self.agent_config.instructions = system_prompt
            
            # Create thread
            thread = await self.create_thread()
            
            # Add user message to thread
            await self.add_message_to_thread(thread, user_prompt)
            
            # Run thread
            run = await self.run_thread(thread)
            
            # Get response
            messages = await self.get_response(thread, run)
            
            # Extract response content
            if messages and len(messages) > 0:
                response_content = messages[-1].content[0].text.value
                return response_content
            else:
                return "No response generated"
        
        except Exception as e:
            logger.error(f"Error in agent {self.agent_name}: {e}", exc_info=True)
            raise
    
    def create_system_prompt(self, base_prompt: str, guardrails: List[str]) -> str:
        """
        Create a system prompt with guardrails.
        
        Args:
            base_prompt: Base system prompt
            guardrails: List of guardrail instructions
            
        Returns:
            System prompt with guardrails
        """
        guardrails_text = "\n".join([f"- {guardrail}" for guardrail in guardrails])
        
        system_prompt = f"""
        {base_prompt}
        
        GUARDRAILS:
        {guardrails_text}
        """
        
        return system_prompt
    
    def log_handoff(self, to_agent: str, context: Dict[str, Any]) -> None:
        """
        Log a handoff to another agent.
        
        Args:
            to_agent: Name of the agent to hand off to
            context: Context information for the handoff
        """
        logger.info(f"Handoff from {self.agent_name} to {to_agent}")
        logger.debug(f"Handoff context: {context}")
