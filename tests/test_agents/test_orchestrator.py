import json
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from app.agents.orchestrator import OrchestratorAgent
from app.api.models import PostGenerationRequest, CompanyContext, BrandHero, PostContent, PostImage, PostResponse

# Load mock data
with open("tests/mock_data/company_context.json", "r") as f:
    company_context_data = json.load(f)

with open("tests/mock_data/brand_hero.json", "r") as f:
    brand_hero_data = json.load(f)

@pytest.fixture
def mock_research_agent():
    """Create a mock research agent."""
    mock_agent = MagicMock()
    mock_agent.generate_context_report.return_value = {
        "company_analysis": {
            "analysis": "Mock company analysis",
            "source": "company_context",
        },
        "trends": {
            "results": [],
            "analysis": "Mock trend analysis",
            "source": "trend_research",
        },
        "competitors": {
            "results": [],
            "analysis": "Mock competitor analysis",
            "source": "competitor_research",
        },
        "insights": {
            "insights": "Mock insights",
            "source": "research_synthesis",
        },
    }
    return mock_agent

@pytest.fixture
def mock_content_agent():
    """Create a mock content agent."""
    mock_agent = MagicMock()
    
    async def mock_generate_post_proposals(*args, **kwargs):
        """Mock implementation of generate_post_proposals."""
        for i in range(2):  # Generate 2 mock proposals
            yield PostResponse(
                id=f"mock-post-{i}",
                content=PostContent(
                    text=f"Mock post content {i}",
                    hashtags=[f"#mock{i}", "#test"],
                ),
            )
    
    mock_agent.generate_post_proposals = mock_generate_post_proposals
    return mock_agent

@pytest.fixture
def mock_image_agent():
    """Create a mock image agent."""
    mock_agent = MagicMock()
    mock_agent.generate_image.return_value = PostImage(
        image_url="https://example.com/mock-image.jpg",
        description="Mock image description",
    )
    return mock_agent

@pytest.mark.asyncio
async def test_orchestrator_process_request(mock_research_agent, mock_content_agent, mock_image_agent):
    """Test orchestrator process_request method."""
    # Create request
    company_context = CompanyContext(**company_context_data)
    brand_hero = BrandHero(**brand_hero_data)
    request = PostGenerationRequest(
        company_context=company_context,
        brand_hero=brand_hero,
        num_proposals=2,
        include_trends=True,
        include_competitors=True,
    )
    
    # Create orchestrator with mock agents
    orchestrator = OrchestratorAgent()
    orchestrator.research_agent = mock_research_agent
    orchestrator.content_agent = mock_content_agent
    orchestrator.image_agent = mock_image_agent
    
    # Process request
    posts = []
    async for post in orchestrator.process_request(request):
        posts.append(post)
    
    # Validate results
    assert len(posts) == 2
    
    # Check that research agent was called
    mock_research_agent.generate_context_report.assert_called_once_with(
        company_context=company_context,
        include_trends=True,
        include_competitors=True,
    )
    
    # Check that image agent was called for each post
    assert mock_image_agent.generate_image.call_count == 2
    
    # Check post structure
    for post in posts:
        assert post.id is not None
        assert post.content is not None
        assert post.content.text is not None
        assert post.content.hashtags is not None
        assert post.image is not None
        assert post.image.image_url is not None
        assert post.image.description is not None

@pytest.mark.asyncio
async def test_orchestrator_guardrails():
    """Test orchestrator guardrails."""
    # Create request with values outside acceptable range
    company_context = CompanyContext(**company_context_data)
    brand_hero = BrandHero(**brand_hero_data)
    request = PostGenerationRequest(
        company_context=company_context,
        brand_hero=brand_hero,
        num_proposals=100,  # Too many proposals
        include_trends=True,
        include_competitors=True,
    )
    
    # Create orchestrator
    orchestrator = OrchestratorAgent()
    
    # Apply request guardrails
    validated_request = orchestrator._apply_request_guardrails(request)
    
    # Check that num_proposals was limited
    assert validated_request.num_proposals < 100
    
    # Test post guardrails
    post = PostResponse(
        id="test-post",
        content=PostContent(
            text="A" * 300,  # Too long
            hashtags=["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"],  # Too many hashtags
        ),
    )
    
    # Apply post guardrails
    validated_post = orchestrator._apply_post_guardrails(post)
    
    # Check that text was truncated
    assert len(validated_post.content.text) <= 280
    
    # Check that hashtags were limited
    assert len(validated_post.content.hashtags) <= 5
