import json
import random
import uuid
from datetime import datetime, timedelta

def generate_mock_data(filename="candidates.jsonl", num_candidates=200):
    locations = ["Pune", "Noida", "Hyderabad", "Mumbai", "Delhi NCR", "Bangalore", "Chennai", "San Francisco"]
    companies_product = ["Google", "Meta", "Amazon", "Redrob", "Stripe", "Uber"]
    companies_service = ["TCS", "Infosys", "Wipro", "Accenture", "Cognizant", "Capgemini"]
    titles = ["Software Engineer", "Senior AI Engineer", "Machine Learning Engineer", "Data Scientist", "Marketing Manager", "Research Scientist", "AI Architect"]
    skills_pool = ["Python", "C++", "Java", "Embeddings", "RAG", "Pinecone", "Milvus", "Weaviate", "OpenSearch", "Elasticsearch", "FAISS", "Sentence-Transformers", "LLMs", "LangChain", "OpenAI", "LoRA", "QLoRA", "PEFT", "NDCG", "A/B Testing", "Computer Vision", "Robotics"]
    
    with open(filename, 'w') as f:
        for i in range(num_candidates):
            candidate_id = f"CAND_{str(i).zfill(7)}"
            
            is_honeypot = random.random() < 0.05
            
            if is_honeypot:
                experience_years = 15.0
                company = "StartupXYZ"
                skills = [{"name": "Python", "proficiency": "expert", "endorsements": 0, "duration_months": 0}] * 10
                exp = [{
                    "company": company, 
                    "title": "Senior Engineer", 
                    "start_date": "2009-01-01",
                    "end_date": None,
                    "is_current": True,
                    "duration_months": experience_years * 12
                }]
            else:
                experience_years = float(random.randint(1, 15))
                exp = []
                remaining_years = experience_years
                while remaining_years > 0:
                    y = min(remaining_years, random.randint(1, 5))
                    is_service = random.random() < 0.3
                    comp = random.choice(companies_service if is_service else companies_product)
                    exp.append({
                        "company": comp,
                        "title": random.choice(titles),
                        "start_date": "2020-01-01",
                        "end_date": "2021-01-01",
                        "duration_months": int(y * 12),
                        "is_current": False
                    })
                    remaining_years -= y
                
                num_skills = random.randint(3, 10)
                skills = []
                for sk in random.sample(skills_pool, num_skills):
                    skills.append({
                        "name": sk,
                        "proficiency": random.choice(["beginner", "intermediate", "advanced", "expert"]),
                        "endorsements": random.randint(0, 50),
                        "duration_months": random.randint(12, int(max(1, experience_years) * 12))
                    })

            last_active = (datetime.now() - timedelta(days=random.randint(0, 200))).strftime("%Y-%m-%d")

            candidate = {
                "candidate_id": candidate_id,
                "profile": {
                    "location": random.choice(locations),
                    "years_of_experience": experience_years,
                    "current_title": exp[0]["title"] if exp else "Unknown"
                },
                "career_history": exp,
                "skills": skills,
                "redrob_signals": {
                    "notice_period_days": random.choice([0, 15, 30, 60, 90, 120]),
                    "last_active_date": last_active,
                    "recruiter_response_rate": round(random.uniform(0, 1), 2)
                }
            }
            f.write(json.dumps(candidate) + '\n')

if __name__ == "__main__":
    generate_mock_data()
    print("Mock data generated matching real schema.")
