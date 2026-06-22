# Redrob AI Recruiter - Hackathon v4 Submission

This repository contains our top-tier heuristic ranking engine for the Redrob Hackathon v4. 
Our ranking algorithm operates strictly on a CPU, evaluating the 100K+ candidate pool completely within the 5-minute compute limit without making any external API calls.

## Architecture

We use a high-performance, rule-based heuristic scoring engine (`rank.py`) that calculates scores dynamically. 
The score is composed of:
1. **Technical Merit**: A base score up to 1.0 evaluating the candidate's career history, recent titles, matching skills (Vector DBs, Embeddings, Evaluation frameworks like NDCG), and NLP/IR background.
2. **Behavioral Multipliers**: A compounding multiplier based on the 23 `redrob_signals` (such as Recruiter Response Rate, Inactivity, Offer Acceptance Rate).
3. **Authenticity Check**: Impossible profiles (honeypots) are identified using algorithmic date boundary checking and assigned an authenticity score of 0.0, instantly dropping them out of the rankings.

## Setup Instructions

This codebase requires standard Python 3. No external packages are needed to run the core ranking step, meaning no `pip install` is necessary to reproduce the CSV.

*(Optional: The repository also includes a FastAPI backend `api.py` and a Vite React `frontend` application for visualizing the engine, but they are not required to generate the submission CSV).*

## Generating the Submission

To reproduce our submission CSV (`team_001.csv`), place the 100K `candidates.jsonl` file in the root directory and run:

```bash
python rank.py --candidates ./candidates.jsonl --out ./team_001.csv
```

The script processes the JSONL file in a single memory-efficient pass and outputs exactly 100 rows formatted perfectly according to the hackathon specifications.
