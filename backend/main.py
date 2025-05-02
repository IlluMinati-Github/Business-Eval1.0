from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import requests
import os
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

app = FastAPI()

# Configure CORS with more permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class BusinessIdea(BaseModel):
    businessName: str
    description: str
    targetMarket: str
    revenueModel: str
    costStructure: str
    distributionChannels: str
    industry: str

def get_ai_analysis(idea: BusinessIdea) -> dict:
    """Get AI analysis from Hugging Face API with timeout"""
    API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
    
    prompt = f"""Analyze this business idea and provide a detailed analysis in JSON format:

Business Name: {idea.businessName}
Description: {idea.description}
Target Market: {idea.targetMarket}
Revenue Model: {idea.revenueModel}
Cost Structure: {idea.costStructure}
Distribution Channels: {idea.distributionChannels}
Industry: {idea.industry}

Provide analysis in this exact JSON format:
{{
    "swot_analysis": {{
        "strengths": ["point1", "point2", "point3"],
        "weaknesses": ["point1", "point2", "point3"],
        "opportunities": ["point1", "point2", "point3"],
        "threats": ["point1", "point2", "point3"]
    }},
    "viability_score": number_between_0_and_100,
    "risk_factors": ["risk1", "risk2", "risk3"],
    "summary": ["point1", "point2", "point3"]
}}"""

    try:
        # Set timeout to 10 seconds
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        # Extract the generated text and parse it as JSON
        analysis_text = result[0]['generated_text']
        # Find the JSON part in the response
        json_start = analysis_text.find('{')
        json_end = analysis_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            analysis_json = json.loads(analysis_text[json_start:json_end])
            return analysis_json
        else:
            raise ValueError("No valid JSON found in AI response")
            
    except (requests.Timeout, requests.RequestException) as e:
        print(f"API request failed: {str(e)}")
        return analyze_business_idea(idea)
    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        return analyze_business_idea(idea)

def analyze_business_idea(idea: BusinessIdea) -> dict:
    """Basic analysis as fallback"""
    # Simple scoring system
    score = 0
    strengths = []
    weaknesses = []
    opportunities = []
    threats = []
    risk_factors = []
    
    # Analyze description length
    if len(idea.description) > 100:
        score += 20
        strengths.append("Detailed business description")
    else:
        weaknesses.append("Business description could be more detailed")
    
    # Analyze target market
    if "global" in idea.targetMarket.lower():
        score += 15
        opportunities.append("Global market potential")
        risk_factors.append("International market challenges")
    elif "local" in idea.targetMarket.lower():
        score += 10
        strengths.append("Focused local market approach")
    
    # Analyze revenue model
    if "subscription" in idea.revenueModel.lower():
        score += 20
        strengths.append("Recurring revenue model")
    elif "one-time" in idea.revenueModel.lower():
        score += 10
        weaknesses.append("One-time revenue may limit growth")
    
    # Analyze cost structure
    if "low" in idea.costStructure.lower():
        score += 15
        strengths.append("Low cost structure")
    elif "high" in idea.costStructure.lower():
        score += 5
        risk_factors.append("High operational costs")
    
    # Analyze distribution channels
    if "online" in idea.distributionChannels.lower():
        score += 15
        strengths.append("Online distribution capability")
        opportunities.append("Digital market reach")
    elif "physical" in idea.distributionChannels.lower():
        score += 10
        risk_factors.append("Physical distribution costs")
    
    # Industry-specific analysis
    if idea.industry == "SaaS":
        score += 15
        opportunities.append("Growing SaaS market")
        strengths.append("Scalable business model")
    elif idea.industry == "E-commerce":
        score += 10
        threats.append("High competition in e-commerce")
    elif idea.industry == "Services":
        score += 12
        strengths.append("Service-based business stability")
    
    # Ensure score is between 0 and 100
    score = min(max(score, 0), 100)
    
    # Generate summary
    summary = [
        f"{idea.businessName} shows {'strong' if score > 70 else 'moderate' if score > 40 else 'weak'} market potential",
        f"Key strength: {strengths[0] if strengths else 'Need to identify core strengths'}",
        f"Main challenge: {threats[0] if threats else 'Need to assess market risks'}"
    ]
    
    return {
        "swot_analysis": {
            "strengths": strengths[:3],  # Top 3 strengths
            "weaknesses": weaknesses[:3],  # Top 3 weaknesses
            "opportunities": opportunities[:3],  # Top 3 opportunities
            "threats": threats[:3]  # Top 3 threats
        },
        "viability_score": score,
        "risk_factors": risk_factors[:3],  # Top 3 risk factors
        "summary": summary
    }

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/evaluateIdea")
async def evaluate_idea(idea: BusinessIdea):
    try:
        # Try AI analysis first with timeout
        try:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(get_ai_analysis, idea)
                analysis = future.result(timeout=15)  # 15 seconds total timeout
        except Exception as e:
            print(f"AI analysis failed, falling back to basic analysis: {str(e)}")
            analysis = analyze_business_idea(idea)
        
        # Return the analysis
        return {
            "status": "success",
            "message": "Business idea evaluated successfully",
            "data": {
                "businessName": idea.businessName,
                "industry": idea.industry,
                "analysis": json.dumps(analysis)
            }
        }

    except Exception as e:
        print(f"Error in evaluate_idea: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluating business idea: {str(e)}"
        ) 