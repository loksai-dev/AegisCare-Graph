"""
Data Seeding Script for AegisCare Graph
Creates sample synthetic medical data in Neo4j
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import db
from backend.config import settings, validate_settings
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database():
    """Seed the Neo4j database with sample medical data"""
    
    logger.info("Starting database seeding...")
    
    # First, run schema initialization
    logger.info("Initializing schema...")
    with open("neo4j_schema.cypher", "r") as f:
        schema = f.read()
        # Note: Neo4j doesn't support IF NOT EXISTS for constraints in all versions
        # We'll handle errors gracefully
    
    try:
        # Try to create constraints (may fail if they exist)
        db.execute_query("""
        CREATE CONSTRAINT patient_id_unique IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE
        """)
    except:
        pass  # Constraint may already exist
    
    # Clear existing data (optional - comment out if you want to preserve data)
    logger.info("Clearing existing data...")
    clear_query = """
    MATCH (n)
    DETACH DELETE n
    """
    db.execute_write(clear_query)
    
    # Create Sample Data
    logger.info("Creating sample medical entities...")
    
    # Create Symptoms
    symptoms = [
        {"id": "sym_001", "name": "Chest Pain", "severity": "Moderate"},
        {"id": "sym_002", "name": "Shortness of Breath", "severity": "Moderate"},
        {"id": "sym_003", "name": "Headache", "severity": "Mild"},
        {"id": "sym_004", "name": "Fever", "severity": "Moderate"},
        {"id": "sym_005", "name": "Cough", "severity": "Mild"},
        {"id": "sym_006", "name": "Fatigue", "severity": "Mild"},
        {"id": "sym_007", "name": "Joint Pain", "severity": "Moderate"},
        {"id": "sym_008", "name": "Nausea", "severity": "Mild"},
    ]
    
    for symptom in symptoms:
        query = """
        CREATE (s:Symptom {
            id: $id,
            name: $name,
            severity: $severity
        })
        """
        db.execute_write(query, symptom)
    
    logger.info(f"Created {len(symptoms)} symptoms")
    
    # Create Diseases
    diseases = [
        {"id": "dis_001", "name": "Hypertension", "icd10_code": "I10"},
        {"id": "dis_002", "name": "Type 2 Diabetes", "icd10_code": "E11"},
        {"id": "dis_003", "name": "Coronary Artery Disease", "icd10_code": "I25"},
        {"id": "dis_004", "name": "Chronic Obstructive Pulmonary Disease", "icd10_code": "J44"},
        {"id": "dis_005", "name": "Osteoarthritis", "icd10_code": "M19"},
        {"id": "dis_006", "name": "Depression", "icd10_code": "F32"},
    ]
    
    for disease in diseases:
        query = """
        CREATE (d:Disease {
            id: $id,
            name: $name,
            icd10_code: $icd10_code
        })
        """
        db.execute_write(query, disease)
    
    logger.info(f"Created {len(diseases)} diseases")
    
    # Create Drugs
    drugs = [
        {"id": "drug_001", "name": "Lisinopril", "rxnorm_code": "314076", "dosage": "10mg", "frequency": "Daily"},
        {"id": "drug_002", "name": "Metformin", "rxnorm_code": "6809", "dosage": "500mg", "frequency": "Twice daily"},
        {"id": "drug_003", "name": "Atorvastatin", "rxnorm_code": "83367", "dosage": "20mg", "frequency": "Daily"},
        {"id": "drug_004", "name": "Aspirin", "rxnorm_code": "1191", "dosage": "81mg", "frequency": "Daily"},
        {"id": "drug_005", "name": "Warfarin", "rxnorm_code": "11289", "dosage": "5mg", "frequency": "Daily"},
        {"id": "drug_006", "name": "Ibuprofen", "rxnorm_code": "5640", "dosage": "400mg", "frequency": "As needed"},
        {"id": "drug_007", "name": "Albuterol", "rxnorm_code": "435", "dosage": "90mcg", "frequency": "As needed"},
        {"id": "drug_008", "name": "Sertraline", "rxnorm_code": "36437", "dosage": "50mg", "frequency": "Daily"},
        {"id": "drug_009", "name": "Amlodipine", "rxnorm_code": "17767", "dosage": "5mg", "frequency": "Daily"},
    ]
    
    for drug in drugs:
        query = """
        CREATE (d:Drug {
            id: $id,
            name: $name,
            rxnorm_code: $rxnorm_code,
            dosage: $dosage,
            frequency: $frequency
        })
        """
        db.execute_write(query, drug)
    
    logger.info(f"Created {len(drugs)} drugs")
    
    # Create Drug Interactions
    interactions = [
        {
            "drug1_id": "drug_005",  # Warfarin
            "drug2_id": "drug_004",  # Aspirin
            "severity": "High",
            "risk_level": "high",
            "description": "Increased risk of bleeding when taken together"
        },
        {
            "drug1_id": "drug_005",  # Warfarin
            "drug2_id": "drug_006",  # Ibuprofen
            "severity": "High",
            "risk_level": "high",
            "description": "Increased risk of bleeding and gastrointestinal complications"
        },
        {
            "drug1_id": "drug_001",  # Lisinopril
            "drug2_id": "drug_009",  # Amlodipine
            "severity": "Moderate",
            "risk_level": "moderate",
            "description": "Both are antihypertensives - monitor blood pressure closely"
        },
    ]
    
    for interaction in interactions:
        query = """
        MATCH (d1:Drug {id: $drug1_id})
        MATCH (d2:Drug {id: $drug2_id})
        CREATE (d1)-[r:INTERACTS_WITH {
            severity: $severity,
            risk_level: $risk_level,
            description: $description
        }]->(d2)
        """
        db.execute_write(query, interaction)
    
    logger.info(f"Created {len(interactions)} drug interactions")
    
    # Create Disease-Drug Treatment Relationships
    treatments = [
        {"disease_id": "dis_001", "drug_id": "drug_001"},  # Hypertension -> Lisinopril
        {"disease_id": "dis_001", "drug_id": "drug_009"},  # Hypertension -> Amlodipine
        {"disease_id": "dis_002", "drug_id": "drug_002"},  # Diabetes -> Metformin
        {"disease_id": "dis_003", "drug_id": "drug_004"},  # CAD -> Aspirin
        {"disease_id": "dis_003", "drug_id": "drug_003"},  # CAD -> Atorvastatin
        {"disease_id": "dis_006", "drug_id": "drug_008"},  # Depression -> Sertraline
    ]
    
    for treatment in treatments:
        query = """
        MATCH (d:Disease {id: $disease_id})
        MATCH (dr:Drug {id: $drug_id})
        CREATE (d)-[:TREATED_BY]->(dr)
        """
        db.execute_write(query, treatment)
    
    logger.info(f"Created {len(treatments)} disease-drug treatment relationships")
    
    # Create Lab Tests
    lab_tests = [
        {"id": "lab_001", "name": "Hemoglobin A1C", "value": "7.2", "unit": "%", "reference_range": "<7.0"},
        {"id": "lab_002", "name": "Total Cholesterol", "value": "220", "unit": "mg/dL", "reference_range": "<200"},
        {"id": "lab_003", "name": "Blood Pressure", "value": "145/92", "unit": "mmHg", "reference_range": "<120/80"},
    ]
    
    for test in lab_tests:
        query = """
        CREATE (lt:LabTest {
            id: $id,
            name: $name,
            value: $value,
            unit: $unit,
            reference_range: $reference_range
        })
        """
        db.execute_write(query, test)
    
    logger.info(f"Created {len(lab_tests)} lab tests")
    
    # Create Treatment Protocols
    protocols = [
        {"id": "proto_001", "name": "Hypertension Management", "description": "ACE inhibitor or ARB as first-line"},
        {"id": "proto_002", "name": "Diabetes Management", "description": "Metformin as first-line, lifestyle modifications"},
    ]
    
    for protocol in protocols:
        query = """
        CREATE (tp:TreatmentProtocol {
            id: $id,
            name: $name,
            description: $description
        })
        """
        db.execute_write(query, protocol)
    
    # Link protocols to diseases
    db.execute_write("""
        MATCH (d:Disease {id: 'dis_001'})
        MATCH (tp:TreatmentProtocol {id: 'proto_001'})
        CREATE (d)-[:FOLLOW_PROTOCOL]->(tp)
    """)
    
    db.execute_write("""
        MATCH (d:Disease {id: 'dis_002'})
        MATCH (tp:TreatmentProtocol {id: 'proto_002'})
        CREATE (d)-[:FOLLOW_PROTOCOL]->(tp)
    """)
    
    logger.info(f"Created {len(protocols)} treatment protocols")
    
    # Create Sample Patients
    patients = [
        {
            "id": "pat_001",
            "name": "John Smith",
            "age": 65,
            "gender": "Male",
            "medical_record_number": "MRN001",
            "symptoms": ["sym_001", "sym_002"],
            "diseases": ["dis_001", "dis_003"],
            "drugs": ["drug_001", "drug_004", "drug_003"],
            "lab_tests": ["lab_003"]
        },
        {
            "id": "pat_002",
            "name": "Mary Johnson",
            "age": 58,
            "gender": "Female",
            "medical_record_number": "MRN002",
            "symptoms": ["sym_006", "sym_008"],
            "diseases": ["dis_002", "dis_006"],
            "drugs": ["drug_002", "drug_008"],
            "lab_tests": ["lab_001"]
        },
        {
            "id": "pat_003",
            "name": "Robert Williams",
            "age": 72,
            "gender": "Male",
            "medical_record_number": "MRN003",
            "symptoms": ["sym_001"],
            "diseases": ["dis_003"],
            "drugs": ["drug_005", "drug_004", "drug_006"],  # High risk interaction
            "lab_tests": []
        },
        {
            "id": "pat_004",
            "name": "Sarah Davis",
            "age": 55,
            "gender": "Female",
            "medical_record_number": "MRN004",
            "symptoms": ["sym_007", "sym_003"],
            "diseases": ["dis_005"],
            "drugs": ["drug_006"],
            "lab_tests": []
        },
        {
            "id": "pat_005",
            "name": "James Brown",
            "age": 68,
            "gender": "Male",
            "medical_record_number": "MRN005",
            "symptoms": ["sym_001", "sym_002"],
            "diseases": ["dis_001", "dis_003"],
            "drugs": ["drug_001", "drug_009"],  # Moderate interaction
            "lab_tests": ["lab_002", "lab_003"]
        },
    ]
    
    for patient in patients:
        # Create patient
        query = """
        CREATE (p:Patient {
            id: $id,
            name: $name,
            age: $age,
            gender: $gender,
            medical_record_number: $medical_record_number
        })
        """
        db.execute_write(query, patient)
        
        # Link symptoms
        for symptom_id in patient.get("symptoms", []):
            query = """
            MATCH (p:Patient {id: $patient_id})
            MATCH (s:Symptom {id: $symptom_id})
            CREATE (p)-[:HAS_SYMPTOM]->(s)
            """
            db.execute_write(query, {"patient_id": patient["id"], "symptom_id": symptom_id})
        
        # Link diseases
        for disease_id in patient.get("diseases", []):
            query = """
            MATCH (p:Patient {id: $patient_id})
            MATCH (d:Disease {id: $disease_id})
            CREATE (p)-[:HAS_DISEASE]->(d)
            """
            db.execute_write(query, {"patient_id": patient["id"], "disease_id": disease_id})
        
        # Link drugs
        for drug_id in patient.get("drugs", []):
            query = """
            MATCH (p:Patient {id: $patient_id})
            MATCH (dr:Drug {id: $drug_id})
            CREATE (p)-[:TAKES_DRUG]->(dr)
            """
            db.execute_write(query, {"patient_id": patient["id"], "drug_id": drug_id})
        
        # Link lab tests
        for lab_id in patient.get("lab_tests", []):
            query = """
            MATCH (p:Patient {id: $patient_id})
            MATCH (lt:LabTest {id: $lab_id})
            CREATE (p)-[:HAS_LAB_RESULT]->(lt)
            """
            db.execute_write(query, {"patient_id": patient["id"], "lab_id": lab_id})
    
    logger.info(f"Created {len(patients)} patients with clinical relationships")
    
    logger.info("✅ Database seeding completed successfully!")
    logger.info(f"Created:")
    logger.info(f"  - {len(symptoms)} symptoms")
    logger.info(f"  - {len(diseases)} diseases")
    logger.info(f"  - {len(drugs)} drugs")
    logger.info(f"  - {len(interactions)} drug interactions")
    logger.info(f"  - {len(lab_tests)} lab tests")
    logger.info(f"  - {len(protocols)} treatment protocols")
    logger.info(f"  - {len(patients)} patients")


if __name__ == "__main__":
    try:
        validate_settings()
        seed_database()
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise

