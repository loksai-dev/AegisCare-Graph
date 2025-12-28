"""
Pydantic models for request/response schemas
Defines the data structures for API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Drug interaction risk levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CONTRAINDICATED = "contraindicated"


class PatientCreate(BaseModel):
    """Schema for creating a new patient"""
    name: str
    age: int = Field(ge=0, le=150)
    gender: Optional[str] = None
    medical_record_number: Optional[str] = None


class SymptomCreate(BaseModel):
    """Schema for creating a symptom"""
    name: str
    severity: Optional[str] = None
    onset_date: Optional[str] = None


class DiseaseCreate(BaseModel):
    """Schema for creating a disease"""
    name: str
    icd10_code: Optional[str] = None
    diagnosis_date: Optional[str] = None


class DrugCreate(BaseModel):
    """Schema for creating a drug"""
    name: str
    rxnorm_code: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None


class LabTestCreate(BaseModel):
    """Schema for creating a lab test"""
    name: str
    value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    test_date: Optional[str] = None


class TreatmentProtocolCreate(BaseModel):
    """Schema for creating a treatment protocol"""
    name: str
    description: Optional[str] = None
    guidelines: Optional[str] = None


class PatientResponse(BaseModel):
    """Schema for patient response"""
    id: str
    name: str
    age: int
    gender: Optional[str] = None
    medical_record_number: Optional[str] = None


class DrugInteractionResponse(BaseModel):
    """Schema for drug interaction response"""
    drug1: str
    drug2: str
    risk_level: RiskLevel
    severity: str
    description: str
    recommendation: str


class SimilarPatientResponse(BaseModel):
    """Schema for similar patient response"""
    patient_id: str
    patient_name: str
    similarity_score: float
    common_symptoms: List[str]
    common_diseases: List[str]
    common_drugs: List[str]


class AIExplanationRequest(BaseModel):
    """Schema for AI explanation request"""
    patient_id: str
    drug_name: Optional[str] = None
    interaction_risk: Optional[Dict[str, Any]] = None
    question: str


class AIExplanationResponse(BaseModel):
    """Schema for AI explanation response"""
    explanation: str
    reasoning: str
    evidence: List[str]
    recommendations: List[str]


class PatientGraphResponse(BaseModel):
    """Schema for patient graph response"""
    patient: PatientResponse
    symptoms: List[Dict[str, Any]]
    diseases: List[Dict[str, Any]]
    drugs: List[Dict[str, Any]]
    lab_tests: List[Dict[str, Any]]
    treatment_protocols: List[Dict[str, Any]]


class DrugRiskAlert(BaseModel):
    """Schema for drug risk alert"""
    drug_name: str
    risk_level: RiskLevel
    interacting_drugs: List[str]
    alert_message: str
    severity: str

