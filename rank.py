import argparse
import json
import csv
from datetime import datetime

# --- Constants & Keywords ---
PRODUCT_COMPANIES = ["google", "meta", "amazon", "redrob", "stripe", "uber", "netflix", "apple", "microsoft", "flipkart", "swiggy", "zomato", "atlassian", "airbnb"]
CONSULTING_COMPANIES = ["tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini", "ibm", "deloitte", "pwc", "kpmg", "ey", "mindtree", "l&t", "tech mahindra"]

VECTOR_DBS = ["pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss", "chroma", "vespa"]
EMBEDDINGS = ["sentence-transformers", "openai embeddings", "bge", "e5", "embeddings", "dense retrieval", "embedding"]
EVAL_METRICS = ["ndcg", "mrr", "map", "a/b test", "ab test", "evaluation", "offline-to-online correlation", "offline benchmark"]
LLM_FINE_TUNING = ["llm fine-tuning", "lora", "qlora", "peft", "fine-tuning"]
LTR_MODELS = ["learning-to-rank", "xgboost", "lightgbm", "catboost"]
HR_TECH = ["hr-tech", "recruiting", "marketplace"]

CV_SPEECH_ROBOTICS = ["computer vision", "image classification", "object detection", "speech recognition", "tts", "robotics", "opencv", "yolo", "gans"]
NLP_IR = ["nlp", "ir", "information retrieval", "llms", "language modeling", "text classification"] + VECTOR_DBS + EMBEDDINGS

def is_honeypot(candidate):
    profile = candidate.get("profile", {})
    total_exp = profile.get("years_of_experience", 0.0)
    for skill in candidate.get("skills", []):
        prof = skill.get("proficiency", "").lower()
        duration_months = skill.get("duration_months", 12)
        years = duration_months / 12.0
        name = skill.get("name", "").lower()
        if prof == "expert" and years <= 1.0: return True
        if name in ["qlora", "langchain", "peft", "fine-tuning llms"] and years > 4.0: return True
        if name in ["lora"] and years > 5.0: return True
        if years > total_exp + 6.0: return True
    if total_exp > 40.0: return True
    return False

def score_candidate(candidate):
    details = {
        "components": {"Career": 0.0, "Narrative": 0.0, "Semantic": 0.0, "Skills": 0.0, "Title": 0.0},
        "metrics": {"Merit (Base)": 0.0, "Availability Mult": 1.0, "Disqualifier Mult": 1.0, "Authenticity (Honeypot)": 1.0, "Composite (Final)": 0.0}
    }
    reason_parts = []
    
    if is_honeypot(candidate):
        details["metrics"]["Authenticity (Honeypot)"] = 0.0
        details["metrics"]["Disqualifier Mult"] = 0.0
        details["metrics"]["Composite (Final)"] = 0.001
        return 0.001, "Detected impossible profile signals (honeypot).", details

    profile = candidate.get("profile", {})
    exp_years = profile.get("years_of_experience", 0.0)
    
    c_score = 0
    if 6 <= exp_years <= 8:
        c_score += 25
        reason_parts.append(f"{exp_years} yrs exp in core sweet spot")
    elif 5 <= exp_years <= 9:
        c_score += 15
        reason_parts.append(f"{exp_years} yrs exp")
    elif 4 <= exp_years <= 12:
        c_score += 5
    else:
        c_score -= 10
    
    exp_history = candidate.get("career_history", [])
    product_stints = 0
    consulting_stints = 0
    swe_ml_stints = 0
    research_stints = 0
    architect_only_recent = True
    
    total_companies = len(set(stint.get("company", "") for stint in exp_history))
    if exp_years > 3 and total_companies / exp_years >= 0.66: 
        c_score -= 50
        reason_parts.append("title-chaser / frequent job hopper")

    recent_stints = exp_history[:2] if exp_history else []
    for stint in recent_stints:
        title = stint.get("title", "").lower()
        if "engineer" in title or "developer" in title or "scientist" in title:
            architect_only_recent = False
            
    t_score = 0
    if architect_only_recent and recent_stints:
        title = recent_stints[0].get("title", "").lower()
        if "architect" in title or "manager" in title or "lead" in title:
            t_score -= 30
            reason_parts.append("hands-off architect/manager recently")
    
    for stint in exp_history:
        comp = stint.get("company", "").lower()
        title = stint.get("title", "").lower()
        desc = stint.get("description", "").lower()
        
        if any(c in comp for c in PRODUCT_COMPANIES) or any(c in desc for c in PRODUCT_COMPANIES):
            product_stints += 1
        elif any(c in comp for c in CONSULTING_COMPANIES):
            consulting_stints += 1
            
        if "software engineer" in title or "machine learning engineer" in title or "ai engineer" in title or "backend" in title:
            swe_ml_stints += 1
        elif "research" in title or "data scientist" in title:
            research_stints += 1
            
    if product_stints > 0:
        c_score += 20
        reason_parts.append("product company experience")
    elif consulting_stints > 0 and product_stints == 0:
        c_score -= 30
        reason_parts.append("pure consulting background without product experience")

    if research_stints > 0 and swe_ml_stints == 0:
        t_score -= 30
        reason_parts.append("pure research background without engineering roles")
    elif swe_ml_stints > 0:
        t_score += 20

    skills_text = " ".join([s.get("name", "").lower() for s in candidate.get("skills", [])])
    title_text = " ".join([s.get("title", "").lower() for s in exp_history])
    desc_text = " ".join([s.get("description", "").lower() for s in exp_history])
    full_text = skills_text + " " + title_text + " " + desc_text + " " + profile.get("summary", "").lower()
    
    has_vector = any(db in full_text for db in VECTOR_DBS)
    has_embedding = any(emb in full_text for emb in EMBEDDINGS)
    has_evals = any(ev in full_text for ev in EVAL_METRICS)
    has_python = "python" in full_text
    
    s_score = 0
    if has_vector:
        s_score += 30
        reason_parts.append("shipped vector db / hybrid search")
    elif has_embedding:
        s_score += 20
        reason_parts.append("embedding-based retrieval experience")
        
    if has_evals:
        s_score += 15
        reason_parts.append("eval frameworks (ndcg/mrr/a-b)")
        
    if has_python:
        s_score += 10
    else:
        s_score -= 30
        details["metrics"]["Disqualifier Mult"] = 0.8
        reason_parts.append("missing Python core requirement")
        
    n_score = 0
    if any(ft in full_text for ft in LLM_FINE_TUNING):
        n_score += 10
    if any(ltr in full_text for ltr in LTR_MODELS):
        n_score += 10
    if any(hr in full_text for hr in HR_TECH):
        n_score += 10
        
    if "langchain" in full_text and not has_vector and not has_embedding and exp_years < 2:
        s_score -= 40
        reason_parts.append("langchain wrapper without pre-LLM ML foundations")
        
    has_cv_speech = any(cv in full_text for cv in CV_SPEECH_ROBOTICS)
    has_nlp = any(nlp in full_text for nlp in NLP_IR)
    if has_cv_speech and not has_nlp:
        s_score -= 30
        reason_parts.append("pure CV/Speech background without NLP/IR")
        
    if "marketing" in title_text or "sales" in title_text:
        t_score -= 50

    # Behavioral Signals Overhaul
    signals = candidate.get("redrob_signals", {})
    a_mult = 1.0
    
    # 1. Engagement
    if signals.get("profile_completeness_score", 0) > 80: a_mult *= 1.05
    if signals.get("saved_by_recruiters_30d", 0) > 0: a_mult *= 1.10
    if signals.get("applications_submitted_30d", 0) > 5: a_mult *= 1.05
    
    # 2. Responsiveness
    last_active = signals.get("last_active_date", "")
    days_ago = 0
    if last_active:
        try:
            d = datetime.strptime(last_active, "%Y-%m-%d")
            days_ago = (datetime.now() - d).days
        except Exception:
            pass
            
    if days_ago > 180:
        a_mult *= 0.5
        reason_parts.append("inactive for >6 months")
    elif days_ago <= 30:
        a_mult *= 1.05
        
    response_rate = signals.get("recruiter_response_rate", 1.0)
    if response_rate < 0: response_rate = 0.0
    if response_rate < 0.2:
        a_mult *= 0.2
        reason_parts.append("virtually 0 response rate")
    elif response_rate > 0.8:
        a_mult *= 1.2
        
    avg_resp_time = signals.get("avg_response_time_hours", 48)
    if avg_resp_time < 24: a_mult *= 1.05
    
    # 3. Validation
    if signals.get("linkedin_connected") and signals.get("verified_email") and signals.get("verified_phone"):
        a_mult *= 1.05
        
    if signals.get("endorsements_received", 0) > 10: a_mult *= 1.05
    
    assessments = signals.get("skill_assessment_scores", {})
    if assessments:
        avg_score = sum(assessments.values()) / len(assessments)
        if avg_score > 80: a_mult *= 1.10
        
    github_score = signals.get("github_activity_score", -1)
    if github_score > 50: a_mult *= 1.10
    
    # 4. Follow-Through
    interview_rate = signals.get("interview_completion_rate", 1.0)
    if interview_rate > 0.8: a_mult *= 1.10
    
    offer_rate = signals.get("offer_acceptance_rate", 1.0)
    if 0 <= offer_rate < 0.3:
        a_mult *= 0.8
        reason_parts.append("history of declining offers")
        
    # 5. Availability
    if signals.get("open_to_work_flag", False): a_mult *= 1.10
    
    np = signals.get("notice_period_days", 30)
    if np <= 30:
        a_mult *= 1.10
        reason_parts.append("sub-30 notice")
    elif np > 60:
        a_mult *= 0.90
        reason_parts.append(f"long notice ({np} days)")

    # Construct details
    details["components"]["Career"] = max(0.0, min(1.0, (c_score + 50) / 100.0))
    details["components"]["Title"] = max(0.0, min(1.0, (t_score + 50) / 100.0))
    details["components"]["Skills"] = max(0.0, min(1.0, (s_score + 50) / 100.0))
    details["components"]["Narrative"] = max(0.0, min(1.0, (n_score + 50) / 100.0))
    details["components"]["Semantic"] = max(0.0, min(1.0, (s_score + n_score + 50) / 100.0))
    
    raw_score = c_score + t_score + s_score + n_score
    merit = max(0.01, min(1.0, (raw_score + 100) / 200.0))
    details["metrics"]["Merit (Base)"] = round(merit, 3)
    details["metrics"]["Availability Mult"] = round(min(2.5, a_mult), 3)
    
    final_score = merit * details["metrics"]["Availability Mult"] * details["metrics"]["Disqualifier Mult"] * details["metrics"]["Authenticity (Honeypot)"]
    details["metrics"]["Composite (Final)"] = max(0.001, round(final_score, 3))

    if details["metrics"]["Composite (Final)"] > 0.4:
        pos_reasons = [r for r in reason_parts if "missing" not in r and "chaser" not in r and "pure" not in r and "inactive" not in r and "rate" not in r and "long notice" not in r]
        reasoning = "; ".join(pos_reasons[:3]).capitalize() + "."
        if not reasoning or reasoning == ".":
            reasoning = "Solid baseline engineering skills and positive behavioral signals."
    else:
        neg_reasons = [r for r in reason_parts if "missing" in r or "chaser" in r or "pure" in r or "inactive" in r or "rate" in r or "long notice" in r or "hands-off" in r]
        reasoning = "Not a strong fit: " + ", ".join(neg_reasons[:2]) + "."
        if not reasoning or reasoning == "Not a strong fit: .":
            reasoning = "Does not meet technical or behavioral criteria for the role."
            
    return details["metrics"]["Composite (Final)"], reasoning, details

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", required=True, help="Path to output csv")
    args = parser.parse_args()

    scored_candidates = []
    
    with open(args.candidates, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            cand = json.loads(line)
            score, reasoning, _ = score_candidate(cand)
            scored_candidates.append({
                "candidate_id": cand["candidate_id"],
                "score": score,
                "reasoning": reasoning
            })
            
    # Sort strictly by score, then candidate ID for deterministic tie-breaking
    scored_candidates.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    top_100 = scored_candidates[:100]
    
    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for i, cand in enumerate(top_100):
            rank = i + 1
            writer.writerow([cand["candidate_id"], rank, f"{cand['score']:.4f}", cand["reasoning"]])

if __name__ == "__main__":
    main()
