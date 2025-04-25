import os
from dotenv import load_dotenv
import uvicorn

# Load .env from project root
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

if __name__ == '__main__':
    uvicorn.run('app.api.routes:app', host='0.0.0.0', port=8000, reload=True)