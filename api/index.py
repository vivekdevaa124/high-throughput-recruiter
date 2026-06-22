from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from rank import score_candidate
import os

app = FastAPI(title="Redrob AI Recruiter API")

# Allow CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/rank")
async def rank_candidates(file: UploadFile = File(None), use_bundled: bool = False):
    content = ""
    
    if use_bundled:
        if not os.path.exists("candidates.jsonl"):
            raise HTTPException(status_code=404, detail="Bundled dataset 'candidates.jsonl' not found.")
        with open("candidates.jsonl", "r", encoding="utf-8") as f:
            content = f.read()
    elif file:
        file_bytes = await file.read()
        content = file_bytes.decode('utf-8')
    else:
        raise HTTPException(status_code=400, detail="Must provide a file or set use_bundled=True")

    candidates_data = []
    try:
        # Try to parse the entire file as a standard JSON array/object
        parsed = json.loads(content)
        if isinstance(parsed, list):
            candidates_data = parsed
        else:
            candidates_data = [parsed]
    except json.JSONDecodeError:
        # Fallback to parsing line-by-line as JSONL
        for line in content.splitlines():
            if not line.strip(): continue
            try:
                candidates_data.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    candidates = []
    for cand in candidates_data:
        score, reasoning, details = score_candidate(cand)
        
        profile = cand.get("profile", {})
        title = profile.get("current_title", "Unknown Role")
        exp = profile.get("years_of_experience", 0.0)
        
        candidates.append({
            "id": cand.get("candidate_id", "UNKNOWN"),
            "title": title,
            "exp": exp,
            "score": score,
            "reasoning": reasoning,
            "details": details
        })
        
    # Sort and return
    candidates.sort(key=lambda x: (-x['score'], x['id']))
    return {"candidates": candidates}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
