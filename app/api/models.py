from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

class CompanyContext(BaseModel):
    """Company context information."""
    name: str
    description: str
    values: List[str]
    target_audience: List[str]
    tone_of_voice: str
    industry: str
    additional_info: Optional[Dict[str, Any]] = None

class BrandHero(BaseModel):
    """Brand hero information."""
    name: str
    appearance: str
    personality: str
    backstory: str
    values: List[str]
    tone_of_voice: str

class PostGenerationRequest(BaseModel):
    """Request model for post generation."""
    company_context: CompanyContext
    brand_hero: BrandHero
    num_proposals: Optional[int] = 10
    include_trends: Optional[bool] = True
    include_competitors: Optional[bool] = True
    
    @validator('num_proposals')
    def validate_num_proposals(cls, v):
        """Validate that num_proposals is within acceptable range."""
        if v < 1 or v > 20:
            raise ValueError('num_proposals must be between 1 and 20')
        return v

class PostContent(BaseModel):
    """Content of a Facebook post."""
    text: str
    hashtags: List[str]
    call_to_action: Optional[str] = None

class PostImage(BaseModel):
    """Image for a Facebook post."""
    image_url: str
    description: str
    prompt_used: Optional[str] = None

class PostResponse(BaseModel):
    """Response model for a generated post."""
    id: str
    content: PostContent
    image: Optional[PostImage] = None
    inspiration: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)

class StreamResponse(BaseModel):
    """Response model for streaming updates."""
    status: str  # "started", "in_progress", "completed", "error"
    message: Optional[str] = None
    post: Optional[PostResponse] = None
    error: Optional[str] = None
