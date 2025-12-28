"""
Drug-Drug Interaction Detection Service
Uses Neo4j graph queries to detect unsafe drug combinations
"""
from backend.database import db
from backend.models import RiskLevel, DrugInteractionResponse
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DrugInteractionService:
    """Service for detecting drug-drug interactions"""
    
    @staticmethod
    def check_patient_drug_interactions(patient_id: str) -> List[DrugInteractionResponse]:
        """
        Check for drug interactions in a patient's current medications
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of drug interaction alerts
        """
        query = """
        MATCH (p:Patient {id: $patient_id})-[:TAKES_DRUG]->(d1:Drug)
        MATCH (p)-[:TAKES_DRUG]->(d2:Drug)
        WHERE d1.id < d2.id
        OPTIONAL MATCH (d1)-[interaction:INTERACTS_WITH]->(d2)
        WHERE interaction IS NOT NULL
        RETURN 
            d1.name as drug1,
            d1.id as drug1_id,
            d2.name as drug2,
            d2.id as drug2_id,
            interaction.severity as severity,
            interaction.description as description,
            interaction.risk_level as risk_level
        """
        
        results = db.execute_query(query, {"patient_id": patient_id})
        
        interactions = []
        for record in results:
            if record.get("severity"):  # Only include if interaction exists
                risk_level = RiskLevel(record.get("risk_level", "moderate").lower())
                interactions.append(DrugInteractionResponse(
                    drug1=record["drug1"],
                    drug2=record["drug2"],
                    risk_level=risk_level,
                    severity=record.get("severity", "unknown"),
                    description=record.get("description", "Interaction detected"),
                    recommendation=DrugInteractionService._get_recommendation(risk_level)
                ))
        
        return interactions
    
    @staticmethod
    def check_drug_interaction(drug1_id: str, drug2_id: str) -> Optional[DrugInteractionResponse]:
        """
        Check for interaction between two specific drugs
        
        Args:
            drug1_id: First drug ID
            drug2_id: Second drug ID
            
        Returns:
            Drug interaction response or None
        """
        query = """
        MATCH (d1:Drug {id: $drug1_id})
        MATCH (d2:Drug {id: $drug2_id})
        OPTIONAL MATCH (d1)-[interaction:INTERACTS_WITH]->(d2)
        RETURN 
            d1.name as drug1,
            d2.name as drug2,
            interaction.severity as severity,
            interaction.description as description,
            interaction.risk_level as risk_level
        """
        
        results = db.execute_query(query, {"drug1_id": drug1_id, "drug2_id": drug2_id})
        
        if results and results[0].get("severity"):
            record = results[0]
            risk_level = RiskLevel(record.get("risk_level", "moderate").lower())
            return DrugInteractionResponse(
                drug1=record["drug1"],
                drug2=record["drug2"],
                risk_level=risk_level,
                severity=record.get("severity", "unknown"),
                description=record.get("description", "Interaction detected"),
                recommendation=DrugInteractionService._get_recommendation(risk_level)
            )
        
        return None
    
    @staticmethod
    def _get_recommendation(risk_level: RiskLevel) -> str:
        """Get recommendation text based on risk level"""
        recommendations = {
            RiskLevel.LOW: "Monitor patient closely. Interaction is mild and may not require action.",
            RiskLevel.MODERATE: "Consider alternative medication or adjust dosages. Regular monitoring recommended.",
            RiskLevel.HIGH: "Avoid combination if possible. Consider alternative medications or close supervision.",
            RiskLevel.CONTRAINDICATED: "DO NOT prescribe together. This combination is contraindicated."
        }
        return recommendations.get(risk_level, "Please consult with a pharmacist or drug interaction database.")
    
    @staticmethod
    def get_safe_alternatives(patient_id: str, drug_id: str) -> List[Dict[str, Any]]:
        """
        Find safer alternative drugs that don't interact with patient's current medications
        
        Args:
            patient_id: Patient ID
            drug_id: Drug ID to find alternatives for
            
        Returns:
            List of alternative drugs
        """
        query = """
        MATCH (p:Patient {id: $patient_id})-[:TAKES_DRUG]->(currentDrug:Drug)
        MATCH (targetDrug:Drug {id: $drug_id})
        MATCH (disease:Disease)<-[:HAS_DISEASE]-(p)
        MATCH (disease)-[:TREATED_BY]->(alternative:Drug)
        WHERE alternative.id <> $drug_id
        AND NOT EXISTS {
            MATCH (currentDrug)-[:INTERACTS_WITH]->(alternative)
        }
        AND NOT EXISTS {
            MATCH (alternative)-[:INTERACTS_WITH]->(currentDrug)
        }
        RETURN DISTINCT
            alternative.id as id,
            alternative.name as name,
            alternative.rxnorm_code as rxnorm_code
        LIMIT 10
        """
        
        results = db.execute_query(query, {"patient_id": patient_id, "drug_id": drug_id})
        return results

