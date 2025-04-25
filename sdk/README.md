##
Links: 
https://openai.github.io/openai-agents-python/ - Official Docs

useful colabs: 
https://github.com/aurelio-labs/cookbook/blob/main/gen-ai/openai/agents-sdk-intro.ipynb 
https://colab.research.google.com/drive/17XLmT81pBxHHf6zONgcCatTjpgzHKvae?usp=sharing 

## Installation
1. Clone the repository
2. Create a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

## Add your .env
Same as .env.example

## Start the FastAPI server:
source venv/bin/activate
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000


## Request body, example:

### Basic – No trends, no competition
```
{
  "company_name": "Acme Corp",
  "company_description": "Leading provider of innovative widget solutions.",
  "company_values": "Quality, reliability, cutting-edge technology",
  "target_audience": "Tech enthusiasts, B2B clients",
  "brand_hero": "Widget Wizard",
  "num_posts": 3,
  "include_trends": true,
  "trend_region": "Europe",
  "include_competition": false
}
```

### Trends only
```
{
  "company_name": "Acme Corp",
  "company_description": "Leading provider of innovative widget solutions.",
  "company_values": "Quality, reliability, cutting-edge technology",
  "target_audience": "Tech enthusiasts, B2B clients",
  "brand_hero": "Widget Wizard",
  "num_posts": 3,
  "include_trends": true,
  "include_competition": false
}

```


### Response: 
```
[
    {
        "content": "🎬 Exciting news, tech enthusiasts! Acme Corp's innovative spirit meets Hollywood! We’re thrilled about the \"Coyote vs. Acme\" film acquisition! Stay tuned for cutting-edge insights and solutions inspired by this epic showdown!",
        "hashtags": [
            "#AcmeInnovates",
            "#CoyoteVsAcme"
        ],
        "call_to_action": "Stay tuned for insights!",
        "scene_description": "It seems there was an issue generating the image. However, here's the scene description:",
        "image_url": ""
    },
    {
        "content": "📽️ Big moves! 🤝 Acme Corp partners with Ketchup Entertainment for the distribution of \"Coyote vs. Acme.\" Discover the synergy between groundbreaking tech and entertainment. 🍿✨",
        "hashtags": [
            "#TechMeetsCinema",
            "#AcmeCorp",
            "#KetchupEntertainment"
        ],
        "call_to_action": "Discover more!",
        "scene_description": "It seems there was an issue generating the image. Here is the scene description based on the content:",
        "image_url": ""
    },
    {
        "content": "🚀 As Warner Bros. navigates new challenges, Acme Corp stands firm on a foundation of quality and reliability. Explore how we power through industry trends with innovative widget solutions.",
        "hashtags": [
            "#AcmeQuality",
            "#IndustryInsights",
            "#B2BTech"
        ],
        "call_to_action": "Explore solutions!",
        "scene_description": "It seems there was an issue generating the image. Unfortunately, this is due to a version-related constraint. However, here's the scene description based on your content:",
        "image_url": ""
    }
]
```