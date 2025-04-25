import logging
import openai
from typing import Dict
from agents import Agent, Runner, function_tool

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@function_tool(
    strict_mode=False,
    name_override='scene_description',
    description_override='Generate a one-sentence scene description for image based on post content'
)
async def scene_description(content: str) -> dict:
    agent = Agent(          # Can be just agent - later transformed to tool
        name='SceneDescTool',
        instructions='You are SceneDescTool. Given post content, return a one-sentence scene description.'
    )
    res = await Runner.run(agent, content)
    logger.debug("scene_description_tool → %s", res.final_output)
    # expect res.final_output to be {"description": "..."}
    return res.final_output



@function_tool(
    strict_mode=False,
    name_override='generate_image',
    description_override='Generate an image from prompt using DALL·E'
)
async def generate_image(prompt: str) -> dict:
    # Consider making this async with aiohttp if available
    img_resp = openai.Image.create(prompt=prompt, n=1, size="512x512")
    url = img_resp.data[0].url
    logger.debug("generate_image_tool → %s", url)
    return {"url": url}



class ImageAgent:
    def __init__(self):
        self.agent = Agent(
            name='ImageAgent',
            instructions="""Follow these steps:
                1. Get a scene description from the post content
                2. Generate an image from that description
                3. Return a dict with scene_description and image_url
            """,
            tools=[scene_description, generate_image]
                # self.agentScene.as_tool(
                #     tool_name="translate_to_spanish",
                #     tool_description="Translate the user's message to Spanish",),         # another way 
           
        )

    async def run(self, content: str) -> Dict[str, str]:
        logger.info("Starting image generation for: %s", content)
        try:
            result = await Runner.run(self.agent, content)
            output = result.final_output

            # Handle different output formats
            if isinstance(output, dict):
                return {
                    'scene_description': output.get('scene_description') or output.get('description', ''),
                    'image_url': output.get('image_url') or output.get('url', '')
                }
            elif isinstance(output, str):
                # If we got a string, try to split it into parts
                parts = output.split('\n')
                return {
                    'scene_description': parts[0] if parts else '',
                    'image_url': parts[1] if len(parts) > 1 else ''
                }
            
            raise ValueError("Invalid output format from agent")

        except Exception as e:
            logger.exception("Error in image generation")
            raise