import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
print(os.getenv('COURTLISTENER_API_KEY'))
# Add project root to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.external_apis.courtlistener_api import CourtListenerAPI

async def test_search():
    api = CourtListenerAPI()
    query = "Fourth Amendment digital privacy"
    court = "scotus"
    try:
        results = await api.search_courtlistener(query, court=court)
        print(f"Search results for query '{query}' in court '{court}':")
        for result in results:
            print(result)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_search())