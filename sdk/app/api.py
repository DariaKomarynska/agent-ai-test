import os
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from app.schemas import GeneratePostsRequest, PostProposal
from app.agents.orchestrator import OrchestratorAgent

# Load .env at module import
base_dir = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)

router = APIRouter()
ag = OrchestratorAgent()

@router.post('/generate-posts', response_model=list[PostProposal])
async def generate_posts(req: GeneratePostsRequest):
    try:
        return await ag.generate(req.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app = FastAPI()
app.include_router(router, prefix='/api')