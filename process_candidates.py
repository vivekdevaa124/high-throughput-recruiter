import json
import pandas as pd  # pyrefly: ignore [missing-import]
import random

input_path = r"c:\Users\nairv\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\sample_candidates.json"
output_path = r"c:\Users\nairv\redrob project\candidates_scored.xlsx"

with open(input_path, 'r', encoding='utf-8') as f:
    candidates = json.load(f)

ai_skills_keywords = ["ai", "ml", "nlp", "image classification", "fine-tuning llms", "speech recognition", "tts", "lora", "bentoml", "milvus", "gans", "statistical modeling", "machine learning", "deep learning", "computer vision", "tensorflow", "pytorch", "keras", "huggingface", "llm", "generative ai", "neural networks"]

rows = []
for c in candidates:
    cid = c.get("candidate_id")
    if not cid:
        continue
    prof = c.get("profile", {})
    title = prof.get("current_title", "Unknown")
    exp = prof.get("years_of_experience", 0.0)
    
    skills = c.get("skills", [])
    ai_count = 0
    for s in skills:
        s_name = s.get("name", "").lower()
        if any(k in s_name for k in ai_skills_keywords):
            ai_count += 1
            
    signals = c.get("redrob_signals", {})
    resp_rate = signals.get("recruiter_response_rate", 0.0)
    if resp_rate < 0:
        resp_rate = 0.0
        
    base_score = 0.5
    score_exp = min(0.2, (exp / 15.0) * 0.2)
    score_ai = min(0.2, (ai_count / 10.0) * 0.2)
    score_resp = resp_rate * 0.1
    
    score = base_score + score_exp + score_ai + score_resp + random.uniform(0.0, 0.05)
    score = min(0.999, round(score, 3))
    
    # Format reasoning string exactly as shown in photo
    reasoning = f"{title} with {exp} yrs; {ai_count} AI core skills; response rate {resp_rate}."
    
    rows.append({
        "candidate_id": cid,
        "score": score,
        "reasoning": reasoning
    })

# Sort descending by score
rows.sort(key=lambda x: x["score"], reverse=True)

# Add rank
for i, r in enumerate(rows):
    r["rank"] = i + 1

df = pd.DataFrame(rows)[["candidate_id", "rank", "score", "reasoning"]]
df.to_excel(output_path, index=False)
print("Successfully generated candidates_scored.xlsx")
