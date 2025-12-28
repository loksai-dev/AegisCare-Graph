"""
FastAPI Routes for AegisCare Graph API
Defines all API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from backend.models import (
    PatientCreate, PatientResponse, PatientGraphResponse,
    DrugInteractionResponse, SimilarPatientResponse,
    AIExplanationRequest, AIExplanationResponse,
    SymptomCreate, DiseaseCreate, DrugCreate, LabTestCreate, TreatmentProtocolCreate,
    DrugRiskAlert
)
from backend.services.patient_service import PatientService
from backend.services.drug_interaction_service import DrugInteractionService
from backend.services.similar_patient_service import SimilarPatientService
from backend.services.ai_explanation_service import AIExplanationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["AegisCare Graph API"])


# ============================================
# Patient Endpoints
# ============================================

@router.post("/patients", response_model=PatientResponse, status_code=201)
async def create_patient(patient: PatientCreate):
    """Create a new patient"""
    try:
        return PatientService.create_patient(patient)
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patients", response_model=List[PatientResponse])
async def get_all_patients():
    """Get all patients"""
    try:
        return PatientService.get_all_patients()
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str):
    """Get a specific patient by ID"""
    try:
        return PatientService.get_patient(patient_id)
    except Exception as e:
        logger.error(f"Error fetching patient: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/patients/{patient_id}/graph", response_model=PatientGraphResponse)
async def get_patient_graph(patient_id: str):
    """Get complete clinical graph for a patient"""
    try:
        return PatientService.get_patient_graph(patient_id)
    except Exception as e:
        logger.error(f"Error fetching patient graph: {e}")
        raise HTTPException(status_code=404, detail=str(e))


# ============================================
# Drug Interaction Endpoints
# ============================================

@router.get("/patients/{patient_id}/drug-interactions", response_model=List[DrugInteractionResponse])
async def check_drug_interactions(patient_id: str):
    """Check for drug interactions in a patient's medications"""
    try:
        interactions = DrugInteractionService.check_patient_drug_interactions(patient_id)
        return interactions
    except Exception as e:
        logger.error(f"Error checking drug interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drug-interactions", response_model=Optional[DrugInteractionResponse])
async def check_specific_drug_interaction(drug1_id: str, drug2_id: str):
    """Check interaction between two specific drugs"""
    try:
        interaction = DrugInteractionService.check_drug_interaction(drug1_id, drug2_id)
        return interaction
    except Exception as e:
        logger.error(f"Error checking drug interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patients/{patient_id}/drug-risk-alerts", response_model=List[DrugRiskAlert])
async def get_drug_risk_alerts(patient_id: str):
    """Get drug risk alerts for a patient (formatted for UI)"""
    try:
        interactions = DrugInteractionService.check_patient_drug_interactions(patient_id)
        
        alerts = []
        for interaction in interactions:
            alerts.append(DrugRiskAlert(
                drug_name=interaction.drug1,
                risk_level=interaction.risk_level,
                interacting_drugs=[interaction.drug2],
                alert_message=f"{interaction.drug1} and {interaction.drug2}: {interaction.description}",
                severity=interaction.severity
            ))
        
        return alerts
    except Exception as e:
        logger.error(f"Error getting drug risk alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patients/{patient_id}/safe-alternatives")
async def get_safe_alternatives(patient_id: str, drug_id: str):
    """Get safer alternative drugs for a patient"""
    try:
        alternatives = DrugInteractionService.get_safe_alternatives(patient_id, drug_id)
        return alternatives
    except Exception as e:
        logger.error(f"Error finding safe alternatives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Similar Patient Discovery Endpoints
# ============================================

@router.get("/patients/{patient_id}/similar", response_model=List[SimilarPatientResponse])
async def find_similar_patients(patient_id: str, limit: int = 5):
    """Find patients with similar clinical profiles"""
    try:
        similar = SimilarPatientService.find_similar_patients(patient_id, limit)
        return similar
    except Exception as e:
        logger.error(f"Error finding similar patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# AI Explanation Endpoints
# ============================================

@router.post("/explanations", response_model=AIExplanationResponse)
async def generate_explanation(request: AIExplanationRequest):
    """Generate AI-powered explanation for clinical decision"""
    try:
        explanation = AIExplanationService.generate_explanation(request)
        return explanation
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Health Check Endpoint
# ============================================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AegisCare Graph API",
        "version": "1.0.0"
    }

