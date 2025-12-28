# AegisCare Graph – Explainable Clinical Decision Intelligence Platform

![AegisCare Graph](https://img.shields.io/badge/Version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-teal)
![Neo4j](https://img.shields.io/badge/Neo4j-Aura-purple)

## 🏥 Overview

AegisCare Graph is an end-to-end medical decision intelligence system designed to prevent unsafe drug interactions and recommend explainable treatments using Neo4j as the core graph database. The platform provides doctor-trustable explanations through AI-powered clinical reasoning.

### Key Features

- ✅ **Drug-Drug Interaction Detection**: Real-time detection of unsafe drug combinations using graph-based Cypher queries
- ✅ **Similar Patient Discovery**: Find patients with similar clinical profiles using graph traversal
- ✅ **Explainable AI Recommendations**: AI-powered explanations for clinical decisions using Google Gemini
- ✅ **Interactive Dashboard**: Streamlit-based UI with patient selector, risk alerts, and graph visualization
- ✅ **Clinical Graph Database**: Neo4j Aura-based graph storage for complex medical relationships

## 🏗️ Architecture

### System Components

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│  Streamlit UI   │────────▶│  FastAPI Backend │────────▶│  Neo4j Aura  │
│   (Frontend)    │  HTTP   │   (Python API)   │ Cypher  │   Database   │
└─────────────────┘         └──────────────────┘         └──────────────┘
                                      │
                                      │ HTTP
                                      ▼
                            ┌──────────────────┐
                            │  Google Gemini   │
                            │      AI API      │
                            └──────────────────┘
```

### Technology Stack

- **Backend**: Python 3.8+, FastAPI
- **Database**: Neo4j Aura (Cloud)
- **Frontend**: Streamlit
- **AI/ML**: Google Gemini 2.5 Flash
- **API Documentation**: Swagger/OpenAPI (FastAPI)

## 📊 Data Model

### Neo4j Graph Schema

The system uses the following node types and relationships:

#### Nodes
- **Patient**: Patient demographics and identifiers
- **Symptom**: Patient symptoms with severity
- **Disease**: Diagnosed conditions with ICD-10 codes
- **Drug**: Medications with RxNorm codes, dosage, frequency
- **LabTest**: Laboratory test results
- **TreatmentProtocol**: Clinical treatment guidelines

#### Relationships
- `(Patient)-[:HAS_SYMPTOM]->(Symptom)`
- `(Patient)-[:HAS_DISEASE]->(Disease)`
- `(Patient)-[:TAKES_DRUG]->(Drug)`
- `(Patient)-[:HAS_LAB_RESULT]->(LabTest)`
- `(Disease)-[:TREATED_BY]->(Drug)`
- `(Drug)-[:INTERACTS_WITH]->(Drug)` (with severity, risk_level, description)
- `(Disease)-[:FOLLOW_PROTOCOL]->(TreatmentProtocol)`

See `diagrams/data_model_diagram.puml` for a visual representation.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Neo4j Aura account (or local Neo4j instance)
- Google Gemini API key
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "AegisCare Graph"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**
   
   Create a `.env` file in the project root with your credentials:
   ```env
   # Neo4j Aura Database Credentials
   NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-password
   NEO4J_DATABASE=neo4j
   AURA_INSTANCEID=your-instance-id
   AURA_INSTANCENAME=Instance01
   
   # Google Gemini API Key
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_MODEL=google/gemini-2.5-flash
   ```

   ⚠️ **IMPORTANT**: Never commit the `.env` file to version control. All credentials must remain in `.env` only.

5. **Initialize Neo4j Schema**
   
   The schema will be automatically initialized when you run the seed script. You can also manually run `neo4j_schema.cypher` in Neo4j Browser.

6. **Seed Sample Data**
   ```bash
   python utils/seed_data.py
   ```
   
   This will create sample patients, symptoms, diseases, drugs, and relationships for testing.

### Running the Application

1. **Start the FastAPI Backend**
   ```bash
   cd backend
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

2. **Start the Streamlit Frontend**
   ```bash
   streamlit run frontend/app.py
   ```
   
   The dashboard will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Using the Streamlit Dashboard

1. **Patient Dashboard**
   - Select a patient from the sidebar
   - View patient demographics, symptoms, diseases, medications, and lab tests
   - Access quick actions for drug interactions and similar patients

2. **Drug Interactions**
   - View all drug interaction alerts for the selected patient
   - Interactions are color-coded by risk level:
     - 🔴 **Red**: High risk / Contraindicated
     - 🟡 **Yellow**: Moderate risk
     - 🟢 **Green**: Low risk
   - Each alert includes severity, description, and recommendations

3. **Similar Patients**
   - Discover patients with similar clinical profiles
   - View similarity scores and common symptoms, diseases, and medications
   - Useful for comparative analysis and treatment insights

4. **AI Explanations**
   - Enter a clinical question about the patient
   - Optionally select a related drug
   - Receive AI-powered explanations with:
     - Clear explanation
     - Evidence-based reasoning
     - Supporting evidence points
     - Actionable recommendations

5. **Patient Graph Visualization**
   - View the complete clinical graph for a patient
   - See all relationships between symptoms, diseases, drugs, and tests

### Using the API Directly

#### Get All Patients
```bash
curl http://localhost:8000/api/v1/patients
```

#### Check Drug Interactions
```bash
curl http://localhost:8000/api/v1/patients/pat_001/drug-interactions
```

#### Find Similar Patients
```bash
curl http://localhost:8000/api/v1/patients/pat_001/similar?limit=5
```

#### Generate AI Explanation
```bash
curl -X POST http://localhost:8000/api/v1/explanations \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "pat_001",
    "question": "Why is this drug recommended?",
    "drug_name": "Lisinopril"
  }'
```

See the full API documentation at `http://localhost:8000/docs` for all available endpoints.

## 🔒 Security Best Practices

- ✅ All credentials stored in `.env` file (not in source code)
- ✅ `.env` file is gitignored
- ✅ No credentials logged or printed
- ✅ Environment variables loaded securely using `python-dotenv`
- ⚠️ In production, use proper secret management (e.g., AWS Secrets Manager, Azure Key Vault)

## 📁 Project Structure

```
AegisCare Graph/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── routes.py            # API endpoints
│   ├── config.py            # Configuration & env vars
│   ├── database.py          # Neo4j connection
│   ├── models.py            # Pydantic schemas
│   └── services/
│       ├── patient_service.py
│       ├── drug_interaction_service.py
│       ├── similar_patient_service.py
│       └── ai_explanation_service.py
├── frontend/
│   └── app.py               # Streamlit dashboard
├── utils/
│   └── seed_data.py         # Database seeding script
├── diagrams/
│   ├── class_diagram.puml
│   ├── sequence_diagram.puml
│   ├── component_diagram.puml
│   └── data_model_diagram.puml
├── neo4j_schema.cypher      # Neo4j schema definitions
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in repo)
├── .gitignore
└── README.md
```

## 🧪 Testing

### Manual Testing Steps

1. **Test Database Connection**
   ```bash
   python -c "from backend.database import db; print('Connected!')"
   ```

2. **Test API Endpoints**
   - Visit `http://localhost:8000/docs` for interactive API testing
   - Use the Swagger UI to test all endpoints

3. **Test Streamlit Dashboard**
   - Ensure backend is running
   - Start Streamlit and verify all pages load correctly
   - Test patient selection and interaction checks

## 🎯 Key Use Cases

### 1. Prevent Unsafe Drug Interactions
When a doctor prescribes a new medication, the system automatically checks for interactions with existing medications and provides risk alerts.

### 2. Explainable Treatment Recommendations
Doctors can ask "Why is this drug recommended?" and receive AI-powered explanations based on the patient's clinical graph.

### 3. Similar Patient Analysis
Find patients with similar profiles to understand treatment outcomes and comparative effectiveness.

### 4. Clinical Decision Support
The graph-based approach allows complex queries like "Find all patients with diabetes and hypertension taking both ACE inhibitors and statins."

## 🔧 Troubleshooting

### Common Issues

1. **Neo4j Connection Error**
   - Verify `.env` file has correct credentials
   - Check Neo4j Aura instance is running
   - Verify network connectivity

2. **Gemini API Error**
   - Verify `GEMINI_API_KEY` in `.env`
   - Check API quota/limits
   - Ensure model name is correct

3. **Streamlit Can't Connect to API**
   - Ensure FastAPI backend is running on port 8000
   - Check `API_BASE_URL` in `frontend/app.py`

4. **Import Errors**
   - Ensure virtual environment is activated
   - Verify all dependencies are installed: `pip install -r requirements.txt`

## 📚 API Reference

### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/patients` | GET | Get all patients |
| `/api/v1/patients/{id}` | GET | Get patient by ID |
| `/api/v1/patients/{id}/graph` | GET | Get complete patient graph |
| `/api/v1/patients/{id}/drug-interactions` | GET | Check drug interactions |
| `/api/v1/patients/{id}/similar` | GET | Find similar patients |
| `/api/v1/explanations` | POST | Generate AI explanation |
| `/api/v1/health` | GET | Health check |

Full interactive documentation available at `/docs` when the API is running.

## 🎨 UML Diagrams

The project includes PlantUML diagrams in the `diagrams/` directory:

- **Class Diagram**: System architecture and class relationships
- **Sequence Diagram**: Drug interaction check workflow
- **Component Diagram**: System component interactions
- **Data Model Diagram**: Neo4j graph schema

To view these diagrams:
1. Install PlantUML: `pip install plantuml`
2. Or use an online viewer: http://www.plantuml.com/plantuml/uml/

## 🤝 Contributing

1. Follow PEP 8 Python style guidelines
2. Add comments for complex logic
3. Update documentation for new features
4. Ensure all credentials remain in `.env` only

## ⚠️ Disclaimer

**This is a demonstration system for educational purposes.**

- ⚠️ NOT FOR CLINICAL USE: This system is not FDA-approved or intended for real patient care
- ⚠️ SYNTHETIC DATA: All medical data is synthetic and for demonstration only
- ⚠️ AI LIMITATIONS: AI explanations should always be verified by qualified medical professionals
- ⚠️ NO MEDICAL ADVICE: This system does not provide medical advice or replace professional judgment

Always consult with qualified healthcare professionals for medical decisions.

## 📝 License

This project is provided as-is for educational and demonstration purposes.

## 👥 Author

Developed as part of the AegisCare Graph project for explainable clinical decision intelligence.

---

**For questions or issues, please check the troubleshooting section or review the API documentation.**

