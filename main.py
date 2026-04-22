from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import pandas as pd

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "MIRRA backend running"}

def detect_bias(data: List[Dict]):
    if not data:
        return {"bias": False, "male_rate": 0, "female_rate": 0, "bias_gap": 0}

    males = [d for d in data if d.get("gender") == "Male"]
    females = [d for d in data if d.get("gender") == "Female"]

    if not males or not females:
        return {"bias": False, "male_rate": 0, "female_rate": 0, "bias_gap": 0}

    male_rate = sum(1 for d in males if d.get("approved", False)) / len(males)
    female_rate = sum(1 for d in females if d.get("approved", False)) / len(females)

    gap = abs(male_rate - female_rate)

    return {
        "male_rate": male_rate,
        "female_rate": female_rate,
        "bias_gap": gap,
        "bias": gap > 0.15
    }

def fair_decision(user: Dict):
    income = user.get("income", 0)
    credit_score = user.get("credit_score", 0)
    if income > 40000 and credit_score > 650:
        return "Approved"
    return "Rejected"

@app.post("/analyze")
def analyze(data: List[Dict]):
    bias = detect_bias(data)

    results = []
    for user in data:
        fair = fair_decision(user)
        original = "Approved" if user.get("approved", False) else "Rejected"

        results.append({
            "original": original,
            "fair": fair,
            "suggestion": "Use income instead of gender" if bias["bias"] else "No bias detected"
        })

    return {
        "bias_report": bias,
        "results": results
    }