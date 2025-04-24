import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any

from app.api.models import StreamResponse, PostResponse

# Configure logging
logger = logging.getLogger(__name__)

async def format_sse_event(data: Dict[str, Any]) -> str:
    """
    Format data as a Server-Sent Event (SSE).
    
    Args:
        data: Data to format
        
    Returns:
        Formatted SSE event
    """
    try:
        json_data = json.dumps(data)
        return f"data: {json_data}\n\n"
    except Exception as e:
        logger.error(f"Error formatting SSE event: {e}", exc_info=True)
        return f"data: {json.dumps({'error': str(e)})}\n\n"

async def stream_generator(
    generator: AsyncGenerator[PostResponse, None],
    delay: float = 0.1,
) -> AsyncGenerator[str, None]:
    """
    Generate a stream of SSE events from an async generator.
    
    Args:
        generator: Async generator of post responses
        delay: Delay between events in seconds
        
    Yields:
        SSE events
    """
    try:
        # Send initial event
        yield await format_sse_event(
            StreamResponse(
                status="started",
                message="Starting post generation process",
            ).dict()
        )
        
        # Stream post responses
        count = 0
        async for post in generator:
            count += 1
            
            # Add a small delay to simulate processing time
            await asyncio.sleep(delay)
            
            # Send post event
            yield await format_sse_event(
                StreamResponse(
                    status="in_progress",
                    post=post,
                ).dict()
            )
        
        # Send completion event
        yield await format_sse_event(
            StreamResponse(
                status="completed",
                message=f"Generated {count} post proposals",
            ).dict()
        )
    
    except Exception as e:
        logger.error(f"Error in stream generator: {e}", exc_info=True)
        yield await format_sse_event(
            StreamResponse(
                status="error",
                error=str(e),
            ).dict()
        )
