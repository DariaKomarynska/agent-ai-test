import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.models import PostGenerationRequest, CompanyContext, BrandHero

# Create test client
client = TestClient(app)

# Load mock data
with open("tests/mock_data/company_context.json", "r") as f:
    company_context_data = json.load(f)

with open("tests/mock_data/brand_hero.json", "r") as f:
    brand_hero_data = json.load(f)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_generate_posts_validation():
    """Test validation of post generation request."""
    # Test with invalid request (missing required fields)
    invalid_request = {
        "company_context": {
            "name": "Test Company",
            # Missing required fields
        },
        "brand_hero": {
            "name": "Test Hero",
            # Missing required fields
        }
    }
    
    response = client.post("/api/generate-posts", json=invalid_request)
    assert response.status_code == 422  # Unprocessable Entity
    
    # Validation errors should be in the response
    errors = response.json().get("detail", [])
    assert len(errors) > 0

def test_generate_posts_request_structure():
    """Test structure of post generation request."""
    # Create valid request
    request = {
        "company_context": company_context_data,
        "brand_hero": brand_hero_data,
        "num_proposals": 2,  # Small number for testing
        "include_trends": True,
        "include_competitors": True
    }
    
    # Validate that the request can be parsed into the expected model
    try:
        PostGenerationRequest(**request)
        assert True
    except Exception as e:
        assert False, f"Failed to parse request: {e}"

@pytest.mark.asyncio
async def test_generate_posts_mock():
    """
    Test post generation with mock data.
    
    Note: This test doesn't actually call the API, but validates
    that the request and response models work as expected.
    """
    # Create company context and brand hero models
    company_context = CompanyContext(**company_context_data)
    brand_hero = BrandHero(**brand_hero_data)
    
    # Create request
    request = PostGenerationRequest(
        company_context=company_context,
        brand_hero=brand_hero,
        num_proposals=2,
        include_trends=True,
        include_competitors=True
    )
    
    # Validate request
    assert request.company_context.name == "EcoTech Solutions"
    assert request.brand_hero.name == "Eko Ekspert"
    assert request.num_proposals == 2
    assert request.include_trends is True
    assert request.include_competitors is True

# Note: The actual API test would be more complex and would require
# mocking the OpenAI API and other external services. This is just
# a basic example to demonstrate the structure of the tests.
