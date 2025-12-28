// AegisCare Graph - Neo4j Schema Initialization
// This script creates constraints and indexes for the medical graph database

// ============================================
// CONSTRAINTS AND INDEXES
// ============================================

// Patient constraints
CREATE CONSTRAINT patient_id_unique IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE;
CREATE INDEX patient_name_index IF NOT EXISTS FOR (p:Patient) ON (p.name);
CREATE INDEX patient_age_index IF NOT EXISTS FOR (p:Patient) ON (p.age);

// Symptom constraints
CREATE CONSTRAINT symptom_id_unique IF NOT EXISTS FOR (s:Symptom) REQUIRE s.id IS UNIQUE;
CREATE INDEX symptom_name_index IF NOT EXISTS FOR (s:Symptom) ON (s.name);

// Disease constraints
CREATE CONSTRAINT disease_id_unique IF NOT EXISTS FOR (d:Disease) REQUIRE d.id IS UNIQUE;
CREATE INDEX disease_name_index IF NOT EXISTS FOR (d:Disease) ON (d.name);
CREATE INDEX disease_code_index IF NOT EXISTS FOR (d:Disease) ON (d.icd10_code);

// Drug constraints
CREATE CONSTRAINT drug_id_unique IF NOT EXISTS FOR (dr:Drug) REQUIRE dr.id IS UNIQUE;
CREATE INDEX drug_name_index IF NOT EXISTS FOR (dr:Drug) ON (dr.name);
CREATE INDEX drug_code_index IF NOT EXISTS FOR (dr:Drug) ON (dr.rxnorm_code);

// LabTest constraints
CREATE CONSTRAINT labtest_id_unique IF NOT EXISTS FOR (lt:LabTest) REQUIRE lt.id IS UNIQUE;
CREATE INDEX labtest_name_index IF NOT EXISTS FOR (lt:LabTest) ON (lt.name);

// TreatmentProtocol constraints
CREATE CONSTRAINT protocol_id_unique IF NOT EXISTS FOR (tp:TreatmentProtocol) REQUIRE tp.id IS UNIQUE;
CREATE INDEX protocol_name_index IF NOT EXISTS FOR (tp:TreatmentProtocol) ON (tp.name);

// ============================================
// SAMPLE DATA (Optional - can be loaded via Python script)
// ============================================

// Note: Sample data will be inserted via the Python seeding script
// This schema file only defines the structure and constraints

