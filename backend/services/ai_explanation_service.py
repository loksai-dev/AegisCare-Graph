"""
AI Explanation Service
Uses Google Gemini AI to generate explainable clinical decision explanations
"""
import google.generativeai as genai
from backend.config import settings
from backend.database import db
from backend.models import AIExplanationRequest, AIExplanationResponse
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Configure Gemini AI
# SECURITY: API key loaded from environment variable only - never hardcoded
genai.configure(api_key=settings.gemini_api_key)


class AIExplanationService:
    """Service for generating AI-powered clinical explanations"""
    
    @staticmethod
    def generate_explanation(request: AIExplanationRequest) -> AIExplanationResponse:
        """
        Generate an AI explanation for a clinical decision or drug interaction
        
        Args:
            request: Explanation request with patient context and question
            
        Returns:
            AI explanation response with reasoning and evidence
        """
        # Fetch patient clinical context from Neo4j
        context = AIExplanationService._get_patient_context(request.patient_id)
        
        # Build prompt for Gemini
        prompt = AIExplanationService._build_prompt(request, context)
        
        try:
            # Generate explanation using Gemini
            model = genai.GenerativeModel(settings.gemini_model)
            response = model.generate_content(prompt)
            
            explanation_text = response.text
            
            # Parse response and extract structured information
            explanation = AIExplanationService._parse_explanation(
                explanation_text, 
                request, 
                context
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating AI explanation: {e}")
            return AIExplanationService._get_fallback_explanation(request, context)
    
    @staticmethod
    def _get_patient_context(patient_id: str) -> Dict[str, Any]:
        """Fetch patient's clinical context from Neo4j"""
        query = """
        MATCH (p:Patient {id: $patient_id})
        OPTIONAL MATCH (p)-[:HAS_SYMPTOM]->(s:Symptom)
        OPTIONAL MATCH (p)-[:HAS_DISEASE]->(d:Disease)
        OPTIONAL MATCH (p)-[:TAKES_DRUG]->(dr:Drug)
        OPTIONAL MATCH (p)-[:HAS_LAB_RESULT]->(lt:LabTest)
        
        RETURN 
            p.name as patient_name,
            p.age as age,
            collect(DISTINCT s.name) as symptoms,
            collect(DISTINCT d.name) as diseases,
            collect(DISTINCT dr.name) as drugs,
            collect(DISTINCT lt.name) as lab_tests
        """
        
        results = db.execute_query(query, {"patient_id": patient_id})
        
        if results:
            return results[0]
        return {}
    
    @staticmethod
    def _build_prompt(request: AIExplanationRequest, context: Dict[str, Any]) -> str:
        """Build the prompt for Gemini AI"""
        
        prompt = f"""You are a clinical decision support AI assistant. Provide clear, evidence-based explanations for clinical questions.

PATIENT CONTEXT:
- Name: {context.get('patient_name', 'Unknown')}
- Age: {context.get('age', 'Unknown')}
- Symptoms: {', '.join(context.get('symptoms', []))}
- Diseases: {', '.join(context.get('diseases', []))}
- Current Medications: {', '.join(context.get('drugs', []))}
- Lab Tests: {', '.join(context.get('lab_tests', []))}
"""
        
        if request.drug_name:
            prompt += f"\nDRUG IN QUESTION: {request.drug_name}\n"
        
        if request.interaction_risk:
            prompt += f"\nDRUG INTERACTION RISK:\n"
            prompt += f"- Drugs: {request.interaction_risk.get('drug1', '')} and {request.interaction_risk.get('drug2', '')}\n"
            prompt += f"- Risk Level: {request.interaction_risk.get('risk_level', 'unknown')}\n"
            prompt += f"- Description: {request.interaction_risk.get('description', '')}\n"
        
        prompt += f"\nCLINICAL QUESTION: {request.question}\n"
        
        prompt += """
Please provide:
1. A clear, concise explanation answering the question
2. Evidence-based reasoning for your answer
3. Key evidence points from the patient's clinical profile
4. Actionable recommendations

Use language appropriate for healthcare professionals. Be transparent about limitations and always recommend consulting with a physician for final decisions.

Format your response clearly with sections for:
- Explanation
- Reasoning
- Evidence (bulleted list)
- Recommendations (bulleted list)
"""
        
        return prompt
    
    @staticmethod
    def _parse_explanation(
        text: str, 
        request: AIExplanationRequest, 
        context: Dict[str, Any]
    ) -> AIExplanationResponse:
        """Parse the AI response into structured format"""
        
        # Extract sections (simple parsing - could be enhanced)
        explanation = text
        reasoning = ""
        evidence = []
        recommendations = []
        
        # Try to parse structured sections
        sections = text.split("\n\n")
        for section in sections:
            if section.strip().lower().startswith("explanation"):
                explanation = section.replace("Explanation:", "").strip()
            elif section.strip().lower().startswith("reasoning"):
                reasoning = section.replace("Reasoning:", "").strip()
            elif section.strip().lower().startswith("evidence"):
                evidence = [
                    line.strip().replace("-", "").replace("*", "").strip()
                    for line in section.split("\n")
                    if line.strip() and not line.strip().lower().startswith("evidence")
                ]
            elif section.strip().lower().startswith("recommendation"):
                recommendations = [
                    line.strip().replace("-", "").replace("*", "").strip()
                    for line in section.split("\n")
                    if line.strip() and not line.strip().lower().startswith("recommendation")
                ]
        
        # If parsing didn't work well, use the full text
        if not reasoning:
            reasoning = explanation
        
        # Extract bullet points from the text
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("-") or line.startswith("*") or line.startswith("•"):
                content = line.lstrip("-*•").strip()
                if content:
                    if "evidence" in line.lower() or "evidence" in content.lower():
                        evidence.append(content)
                    elif "recommend" in line.lower() or "recommend" in content.lower():
                        recommendations.append(content)
        
        # Fallback: use key points from context as evidence
        if not evidence:
            if context.get('symptoms'):
                evidence.append(f"Patient presents with: {', '.join(context.get('symptoms', []))}")
            if context.get('diseases'):
                evidence.append(f"Diagnosed with: {', '.join(context.get('diseases', []))}")
        
        return AIExplanationResponse(
            explanation=explanation,
            reasoning=reasoning or explanation,
            evidence=evidence or ["Clinical context analyzed from patient graph"],
            recommendations=recommendations or ["Consult with treating physician for final decision"]
        )
    
    @staticmethod
    def _get_fallback_explanation(
        request: AIExplanationRequest, 
        context: Dict[str, Any]
    ) -> AIExplanationResponse:
        """Provide a fallback explanation if AI generation fails"""
        
        explanation = f"Based on the clinical profile for {context.get('patient_name', 'the patient')}, "
        
        if request.drug_name:
            explanation += f"regarding {request.drug_name}: {request.question}. "
        
        explanation += "Please review the patient's symptoms, diseases, and current medications for context."
        
        return AIExplanationResponse(
            explanation=explanation,
            reasoning="Graph-based analysis of patient clinical profile",
            evidence=[
                f"Symptoms: {', '.join(context.get('symptoms', []))}",
                f"Diseases: {', '.join(context.get('diseases', []))}",
                f"Current medications: {', '.join(context.get('drugs', []))}"
            ],
            recommendations=[
                "Review full patient chart",
                "Consider drug interactions",
                "Consult with specialist if needed"
            ]
        )

