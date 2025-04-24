# Agent AI Test - Facebook Post Generator

This repository demonstrates the use of OpenAI's Agents library to create a system that generates Facebook post proposals based on company context, current trends, and competitor analysis.

## Features

- FastAPI application with streaming agent responses
- Agent delegation with handoffs between specialized agents using OpenAI Agents
- Context-aware post generation based on company information
- Integration with OpenAI's search capabilities for trend and competitor research
- DALL-E 3 integration for generating Brand Hero images
- Configurable number of post proposals (10-20 by default)
- Guardrails for content appropriateness and brand consistency
- Tool-based agent architecture for modular and extensible functionality

## Architecture

The system consists of several specialized agents built with OpenAI Agents:

1. **Main Agent Orchestrator**: Coordinates the work of other agents using tools for research, content generation, and image creation
2. **Context Research Agent**: Analyzes company context and researches trends/competitors using specialized tools
3. **Content Creation Agent**: Generates post content based on research and Brand Hero persona
4. **Image Generation Agent**: Creates images of the Brand Hero in scenarios matching the posts

### Agents Implementation

Each agent in the system is implemented using OpenAI's Agents library:

- **BaseAgent**: A foundational class that wraps the Agents library functionality, providing thread management and response generation
- **Tool-based Architecture**: Each agent exposes functionality through tools defined with the SDK's `FunctionTool` and `ToolConfig`
- **Thread Management**: Agents communicate through threads, allowing for stateful conversations and context preservation
- **Guardrails**: System prompts include guardrails to ensure content quality and brand consistency

## Setup

### Prerequisites

- Python 3.9+
- OpenAI API key with access to GPT-4 and DALL-E 3

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/riposta/agent-ai-test.git
   cd agent-ai-test
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and add your OpenAI API key:
   ```
   cp .env.example .env
   # Edit .env to add your API key
   ```

### Running the Application

Start the FastAPI server:
```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Usage

### Generate Facebook Post Proposals

```
POST /api/generate-posts
```

Request body:
```json
{
  "company_context": {
    "name": "EcoTech Solutions",
    "description": "Firma zajmująca się rozwiązaniami ekologicznymi dla biznesu i domu",
    "values": ["zrównoważony rozwój", "innowacyjność", "odpowiedzialność społeczna"],
    "target_audience": ["świadomi ekologicznie konsumenci", "małe i średnie firmy", "instytucje publiczne"],
    "tone_of_voice": "profesjonalny, ale przystępny, inspirujący do działania",
    "industry": "technologie ekologiczne",
    "additional_info": {
      "flagship_products": ["EcoHome Smart System", "BusinessGreen Solutions", "EcoAudit"],
      "recent_achievements": ["Nagroda Eco Innovation 2024", "Redukcja śladu węglowego o 30% w ostatnim roku"]
    }
  },
  "brand_hero": {
    "name": "Eko Ekspert",
    "appearance": "Postać w wieku 30-35 lat, ubrana w nowoczesny, ale ekologiczny strój w odcieniach zieleni i błękitu. Ma krótkie, zadbane włosy i przyjazny uśmiech. Często pokazywana w otoczeniu natury lub z gadżetami ekologicznymi.",
    "personality": "Entuzjastyczny, pomocny, kompetentny. Łączy wiedzę eksperta z przystępnym podejściem.",
    "backstory": "Były naukowiec, który postanowił wykorzystać swoją wiedzę do promowania ekologicznych rozwiązań w codziennym życiu.",
    "values": ["edukacja", "praktyczne rozwiązania", "pozytywny wpływ"],
    "tone_of_voice": "Przyjazny, entuzjastyczny, ale merytoryczny. Używa prostego języka do wyjaśniania złożonych koncepcji."
  },
  "num_proposals": 10,
  "include_trends": true,
  "include_competitors": true
}
```

Response:
The endpoint returns a stream of Server-Sent Events (SSE) with post proposals.

## Testing

Run the test suite:
```
pytest
```

## Docker

Build and run with Docker Compose:
```
docker-compose up --build
