import json
import asyncio
from api import rank_candidates

async def test():
    res = await rank_candidates(use_bundled=True)
    scores = [c['score'] for c in res['candidates']]
    print("ALL SCORES:")
    print(scores)

asyncio.run(test())
