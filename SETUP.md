# Setup Instructions

## Creating the .env File

Since the `.env` file contains sensitive credentials, you need to create it manually.

Create a file named `.env` in the project root directory with the following content:

```env
# Neo4j Aura Database Credentials
NEO4J_URI=neo4j+s://YOUR_INSTANCE_ID.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=YOUR_NEO4J_PASSWORD
NEO4J_DATABASE=neo4j
AURA_INSTANCEID=YOUR_INSTANCE_ID
AURA_INSTANCENAME=Instance01

# Google Gemini API Key
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=google/gemini-2.5-flash
```

**Note**: Replace `YOUR_INSTANCE_ID`, `YOUR_NEO4J_PASSWORD`, and `YOUR_GEMINI_API_KEY` with your actual credentials.

**Important Notes:**
- The `.env` file is already in `.gitignore` and will not be committed to version control
- Never share or commit your `.env` file
- All credentials are loaded from environment variables only - they are NOT hardcoded in the source code

## Quick Start

1. Create the `.env` file as described above
2. Install dependencies: `pip install -r requirements.txt`
3. Seed the database: `python utils/seed_data.py`
4. Start the backend: `python backend/main.py` (or `uvicorn backend.main:app --reload`)
5. Start the frontend: `streamlit run frontend/app.py`

