"""
Similar Patient Discovery Service
Uses graph traversal to find patients with similar clinical profiles
"""
from backend.database import db
from backend.models import SimilarPatientResponse
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SimilarPatientService:
    """Service for finding similar patients using graph traversal"""
    
    @staticmethod
    def find_similar_patients(patient_id: str, limit: int = 5) -> List[SimilarPatientResponse]:
        """
        Find patients with similar clinical profiles based on symptoms, diseases, and drugs
        
        Args:
            patient_id: Patient ID to find similar patients for
            limit: Maximum number of similar patients to return
            
        Returns:
            List of similar patients with similarity scores
        """
        # Query to find similar patients based on overlapping symptoms, diseases, and drugs
        query = """
        MATCH (target:Patient {id: $patient_id})
        
        // Get target patient's clinical profile
        OPTIONAL MATCH (target)-[:HAS_SYMPTOM]->(target_symptom:Symptom)
        OPTIONAL MATCH (target)-[:HAS_DISEASE]->(target_disease:Disease)
        OPTIONAL MATCH (target)-[:TAKES_DRUG]->(target_drug:Drug)
        
        // Find other patients with overlapping profiles
        MATCH (similar:Patient)
        WHERE similar.id <> $patient_id
        
        OPTIONAL MATCH (similar)-[:HAS_SYMPTOM]->(similar_symptom:Symptom)
        WHERE similar_symptom.id IN [(target)-[:HAS_SYMPTOM]->(s:Symptom) | s.id]
        
        OPTIONAL MATCH (similar)-[:HAS_DISEASE]->(similar_disease:Disease)
        WHERE similar_disease.id IN [(target)-[:HAS_DISEASE]->(d:Disease) | d.id]
        
        OPTIONAL MATCH (similar)-[:TAKES_DRUG]->(similar_drug:Drug)
        WHERE similar_drug.id IN [(target)-[:TAKES_DRUG]->(dr:Drug) | dr.id]
        
        WITH similar,
             collect(DISTINCT similar_symptom.name) as common_symptoms,
             collect(DISTINCT similar_disease.name) as common_diseases,
             collect(DISTINCT similar_drug.name) as common_drugs,
             // Calculate similarity score
             size(collect(DISTINCT similar_symptom)) as symptom_matches,
             size(collect(DISTINCT similar_disease)) as disease_matches,
             size(collect(DISTINCT similar_drug)) as drug_matches
        
        WHERE symptom_matches > 0 OR disease_matches > 0 OR drug_matches > 0
        
        // Calculate weighted similarity score
        WITH similar,
             common_symptoms,
             common_diseases,
             common_drugs,
             (symptom_matches * 0.3 + disease_matches * 0.5 + drug_matches * 0.2) as similarity_score
        
        ORDER BY similarity_score DESC
        
        RETURN 
            similar.id as patient_id,
            similar.name as patient_name,
            similarity_score,
            common_symptoms,
            common_diseases,
            common_drugs
        
        LIMIT $limit
        """
        
        results = db.execute_query(query, {"patient_id": patient_id, "limit": limit})
        
        similar_patients = []
        for record in results:
            similar_patients.append(SimilarPatientResponse(
                patient_id=record["patient_id"],
                patient_name=record["patient_name"],
                similarity_score=round(record["similarity_score"], 2),
                common_symptoms=record.get("common_symptoms", []) or [],
                common_diseases=record.get("common_diseases", []) or [],
                common_drugs=record.get("common_drugs", []) or []
            ))
        
        return similar_patients
    
    @staticmethod
    def find_patients_by_disease(disease_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find all patients with a specific disease
        
        Args:
            disease_id: Disease ID
            limit: Maximum number of patients to return
            
        Returns:
            List of patients with the disease
        """
        query = """
        MATCH (d:Disease {id: $disease_id})<-[:HAS_DISEASE]-(p:Patient)
        RETURN 
            p.id as id,
            p.name as name,
            p.age as age,
            p.gender as gender
        LIMIT $limit
        """
        
        return db.execute_query(query, {"disease_id": disease_id, "limit": limit})
    
    @staticmethod
    def find_patients_by_symptom(symptom_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find all patients with a specific symptom
        
        Args:
            symptom_id: Symptom ID
            limit: Maximum number of patients to return
            
        Returns:
            List of patients with the symptom
        """
        query = """
        MATCH (s:Symptom {id: $symptom_id})<-[:HAS_SYMPTOM]-(p:Patient)
        RETURN 
            p.id as id,
            p.name as name,
            p.age as age,
            p.gender as gender
        LIMIT $limit
        """
        
        return db.execute_query(query, {"symptom_id": symptom_id, "limit": limit})

