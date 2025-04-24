import json
import logging
import uuid
from typing import AsyncGenerator, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.api.models import PostGenerationRequest, PostResponse, StreamResponse
from app.agents.orchestrator import OrchestratorAgent
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

async def generate_posts_stream(
    request: PostGenerationRequest,
) -> AsyncGenerator[str, None]:
    """Generate a stream of post proposals."""
    try:
        # Initialize orchestrator agent
        orchestrator = OrchestratorAgent()
        
        # Send initial response
        yield json.dumps(
            StreamResponse(
                status="started",
                message="Starting post generation process",
            ).dict()
        ) + "\n"
        
        # Process request and stream results
        async for post in orchestrator.process_request(request):
            yield json.dumps(
                StreamResponse(
                    status="in_progress",
                    post=post,
                ).dict()
            ) + "\n"
        
        # Send completion response
        yield json.dumps(
            StreamResponse(
                status="completed",
                message=f"Generated {request.num_proposals} post proposals",
            ).dict()
        ) + "\n"
    
    except Exception as e:
        logger.error(f"Error generating posts: {e}", exc_info=True)
        yield json.dumps(
            StreamResponse(
                status="error",
                error=str(e),
            ).dict()
        ) + "\n"

@router.post("/generate-posts", tags=["Posts"])
async def generate_posts(request: PostGenerationRequest):
    """
    Generate Facebook post proposals based on company context and brand hero.
    
    Returns a stream of Server-Sent Events (SSE) with post proposals.
    """
    return StreamingResponse(
        generate_posts_stream(request),
        media_type="text/event-stream",
    )

@router.get("/posts/{post_id}", tags=["Posts"], response_model=PostResponse)
async def get_post(post_id: str):
    """
    Get a specific post by ID.
    
    This is a placeholder endpoint for retrieving previously generated posts.
    In a real implementation, this would fetch from a database.
    """
    # This is a placeholder - in a real implementation, you would fetch from a database
    raise HTTPException(status_code=404, detail="Post not found")
