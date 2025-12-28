"""
Patient Service
Handles patient-related graph operations
"""
from backend.database import db
from backend.models import PatientCreate, PatientResponse, PatientGraphResponse
from typing import List, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)


class PatientService:
    """Service for patient graph operations"""
    
    @staticmethod
    def create_patient(patient_data: PatientCreate) -> PatientResponse:
        """
        Create a new patient node in Neo4j
        
        Args:
            patient_data: Patient creation data
            
        Returns:
            Created patient response
        """
        patient_id = str(uuid.uuid4())
        
        query = """
        CREATE (p:Patient {
            id: $patient_id,
            name: $name,
            age: $age,
            gender: $gender,
            medical_record_number: $medical_record_number
        })
        RETURN p.id as id, p.name as name, p.age as age, p.gender as gender, p.medical_record_number as medical_record_number
        """
        
        result = db.execute_query(
            query,
            {
                "patient_id": patient_id,
                "name": patient_data.name,
                "age": patient_data.age,
                "gender": patient_data.gender,
                "medical_record_number": patient_data.medical_record_number
            }
        )
        
        if result:
            record = result[0]
            return PatientResponse(
                id=record["id"],
                name=record["name"],
                age=record["age"],
                gender=record.get("gender"),
                medical_record_number=record.get("medical_record_number")
            )
        
        raise Exception("Failed to create patient")
    
    @staticmethod
    def get_patient(patient_id: str) -> PatientResponse:
        """Get patient by ID"""
        query = """
        MATCH (p:Patient {id: $patient_id})
        RETURN p.id as id, p.name as name, p.age as age, p.gender as gender, p.medical_record_number as medical_record_number
        """
        
        results = db.execute_query(query, {"patient_id": patient_id})
        
        if not results:
            raise Exception(f"Patient {patient_id} not found")
        
        record = results[0]
        return PatientResponse(
            id=record["id"],
            name=record["name"],
            age=record["age"],
            gender=record.get("gender"),
            medical_record_number=record.get("medical_record_number")
        )
    
    @staticmethod
    def get_all_patients() -> List[PatientResponse]:
        """Get all patients"""
        query = """
        MATCH (p:Patient)
        RETURN p.id as id, p.name as name, p.age as age, p.gender as gender, p.medical_record_number as medical_record_number
        ORDER BY p.name
        """
        
        try:
            # Ensure database connection is initialized
            if db.driver is None:
                db._connect()
            
            results = db.execute_query(query)
            
            if not results:
                return []
            
            return [
                PatientResponse(
                    id=record["id"],
                    name=record["name"],
                    age=record["age"],
                    gender=record.get("gender"),
                    medical_record_number=record.get("medical_record_number")
                )
                for record in results
            ]
        except Exception as e:
            logger.error(f"Error in get_all_patients: {e}")
            raise
    
    @staticmethod
    def get_patient_graph(patient_id: str) -> PatientGraphResponse:
        """Get complete patient clinical graph"""
        query = """
        MATCH (p:Patient {id: $patient_id})
        OPTIONAL MATCH (p)-[:HAS_SYMPTOM]->(s:Symptom)
        OPTIONAL MATCH (p)-[:HAS_DISEASE]->(d:Disease)
        OPTIONAL MATCH (p)-[:TAKES_DRUG]->(dr:Drug)
        OPTIONAL MATCH (p)-[:HAS_LAB_RESULT]->(lt:LabTest)
        OPTIONAL MATCH (d)-[:FOLLOW_PROTOCOL]->(tp:TreatmentProtocol)
        
        RETURN 
            p.id as patient_id,
            p.name as patient_name,
            p.age as patient_age,
            p.gender as patient_gender,
            collect(DISTINCT {
                id: s.id,
                name: s.name,
                severity: s.severity
            }) as symptoms,
            collect(DISTINCT {
                id: d.id,
                name: d.name,
                icd10_code: d.icd10_code
            }) as diseases,
            collect(DISTINCT {
                id: dr.id,
                name: dr.name,
                dosage: dr.dosage,
                frequency: dr.frequency
            }) as drugs,
            collect(DISTINCT {
                id: lt.id,
                name: lt.name,
                value: lt.value,
                unit: lt.unit
            }) as lab_tests,
            collect(DISTINCT {
                id: tp.id,
                name: tp.name,
                description: tp.description
            }) as treatment_protocols
        """
        
        results = db.execute_query(query, {"patient_id": patient_id})
        
        if not results:
            raise Exception(f"Patient {patient_id} not found")
        
        record = results[0]
        
        # Filter out None values from collections
        symptoms = [s for s in record.get("symptoms", []) if s.get("id")]
        diseases = [d for d in record.get("diseases", []) if d.get("id")]
        drugs = [d for d in record.get("drugs", []) if d.get("id")]
        lab_tests = [lt for lt in record.get("lab_tests", []) if lt.get("id")]
        protocols = [tp for tp in record.get("treatment_protocols", []) if tp.get("id")]
        
        return PatientGraphResponse(
            patient=PatientResponse(
                id=record["patient_id"],
                name=record["patient_name"],
                age=record["patient_age"],
                gender=record.get("patient_gender")
            ),
            symptoms=symptoms,
            diseases=diseases,
            drugs=drugs,
            lab_tests=lab_tests,
            treatment_protocols=protocols
        )
    
    @staticmethod
    def link_patient_to_symptom(patient_id: str, symptom_id: str) -> bool:
        """Link patient to a symptom"""
        query = """
        MATCH (p:Patient {id: $patient_id})
        MATCH (s:Symptom {id: $symptom_id})
        MERGE (p)-[:HAS_SYMPTOM]->(s)
        RETURN count(*) as count
        """
        
        result = db.execute_query(query, {"patient_id": patient_id, "symptom_id": symptom_id})
        return result[0]["count"] > 0
    
    @staticmethod
    def link_patient_to_disease(patient_id: str, disease_id: str) -> bool:
        """Link patient to a disease"""
        query = """
        MATCH (p:Patient {id: $patient_id})
        MATCH (d:Disease {id: $disease_id})
        MERGE (p)-[:HAS_DISEASE]->(d)
        RETURN count(*) as count
        """
        
        result = db.execute_query(query, {"patient_id": patient_id, "disease_id": disease_id})
        return result[0]["count"] > 0
    
    @staticmethod
    def link_patient_to_drug(patient_id: str, drug_id: str) -> bool:
        """Link patient to a drug"""
        query = """
        MATCH (p:Patient {id: $patient_id})
        MATCH (d:Drug {id: $drug_id})
        MERGE (p)-[:TAKES_DRUG]->(d)
        RETURN count(*) as count
        """
        
        result = db.execute_query(query, {"patient_id": patient_id, "drug_id": drug_id})
        return result[0]["count"] > 0

