"""
Streamlit Dashboard for AegisCare Graph
Explainable Clinical Decision Intelligence Platform
"""
import streamlit as st
import requests
import json
from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="AegisCare Graph",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high {
        background-color: #ff6b6b;
        color: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .risk-moderate {
        background-color: #ffd93d;
        color: black;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .risk-low {
        background-color: #6bcf7f;
        color: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .patient-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def get_api(endpoint: str, params: Dict = None) -> Any:
    """Make API request to backend"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params or {})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def post_api(endpoint: str, data: Dict) -> Any:
    """Make POST API request to backend"""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def format_risk_level(risk_level: str) -> str:
    """Format risk level with color"""
    risk_classes = {
        "high": "risk-high",
        "moderate": "risk-moderate",
        "low": "risk-low",
        "contraindicated": "risk-high"
    }
    css_class = risk_classes.get(risk_level.lower(), "risk-low")
    return f'<div class="{css_class}">{risk_level.upper()}</div>'


def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<div class="main-header">🏥 AegisCare Graph – Clinical Decision Intelligence</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Patient Dashboard", "Drug Interactions", "Similar Patients", "AI Explanations", "Patient Graph"]
        )
        
        st.markdown("---")
        st.header("Patient Selector")
        
        # Get all patients
        patients = get_api("/patients")
        if patients:
            patient_options = {f"{p['name']} ({p['id'][:8]})": p['id'] for p in patients}
            selected_patient = st.selectbox(
                "Select Patient",
                options=list(patient_options.keys()),
                key="patient_selector"
            )
            selected_patient_id = patient_options.get(selected_patient) if selected_patient else None
        else:
            selected_patient_id = None
            st.warning("No patients found. Please seed the database first.")
    
    # Main content based on selected page
    if page == "Patient Dashboard":
        show_patient_dashboard(selected_patient_id)
    elif page == "Drug Interactions":
        show_drug_interactions(selected_patient_id)
    elif page == "Similar Patients":
        show_similar_patients(selected_patient_id)
    elif page == "AI Explanations":
        show_ai_explanations(selected_patient_id)
    elif page == "Patient Graph":
        show_patient_graph(selected_patient_id)


def show_patient_dashboard(patient_id: str):
    """Display patient dashboard"""
    st.header("Patient Dashboard")
    
    if not patient_id:
        st.info("Please select a patient from the sidebar")
        return
    
    # Get patient information
    patient = get_api(f"/patients/{patient_id}")
    patient_graph = get_api(f"/patients/{patient_id}/graph")
    
    if not patient:
        st.error("Patient not found")
        return
    
    # Patient Information Card
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.subheader("Patient Information")
        st.write(f"**Name:** {patient['name']}")
        st.write(f"**Age:** {patient['age']}")
        st.write(f"**Gender:** {patient.get('gender', 'N/A')}")
        st.write(f"**MRN:** {patient.get('medical_record_number', 'N/A')}")
    
    with col2:
        st.subheader("Clinical Summary")
        if patient_graph:
            st.metric("Symptoms", len(patient_graph.get('symptoms', [])))
            st.metric("Diseases", len(patient_graph.get('diseases', [])))
            st.metric("Medications", len(patient_graph.get('drugs', [])))
            st.metric("Lab Tests", len(patient_graph.get('lab_tests', [])))
    
    with col3:
        st.subheader("Risk Assessment")
        interactions = get_api(f"/patients/{patient_id}/drug-interactions")
        if interactions:
            high_risk = len([i for i in interactions if i.get('risk_level') == 'high'])
            moderate_risk = len([i for i in interactions if i.get('risk_level') == 'moderate'])
            st.metric("High Risk", high_risk, delta=None, delta_color="inverse")
            st.metric("Moderate Risk", moderate_risk, delta=None)
        else:
            st.success("✅ No drug interactions")
    
    with col4:
        st.subheader("Quick Actions")
        if st.button("🔍 Check Interactions", use_container_width=True):
            st.session_state.page = "Drug Interactions"
        if st.button("👥 Similar Patients", use_container_width=True):
            st.session_state.page = "Similar Patients"
        if st.button("📊 View Graph", use_container_width=True):
            st.session_state.page = "Patient Graph"
    
    # Visualizations
    if patient_graph:
        st.markdown("---")
        st.subheader("📊 Clinical Overview Charts")
        
        # Clinical metrics pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            # Symptoms and Diseases distribution
            categories = ['Symptoms', 'Diseases', 'Medications', 'Lab Tests']
            counts = [
                len(patient_graph.get('symptoms', [])),
                len(patient_graph.get('diseases', [])),
                len(patient_graph.get('drugs', [])),
                len(patient_graph.get('lab_tests', []))
            ]
            
            fig = px.pie(
                values=counts,
                names=categories,
                title="Clinical Data Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Bar chart of clinical metrics
            fig = px.bar(
                x=categories,
                y=counts,
                title="Clinical Metrics Count",
                color=counts,
                color_continuous_scale="Blues",
                labels={'x': 'Category', 'y': 'Count'}
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Information with tabs
        st.markdown("---")
        tab1, tab2, tab3, tab4 = st.tabs(["Symptoms", "Diseases", "Medications", "Lab Tests"])
        
        with tab1:
            if patient_graph.get('symptoms'):
                symptoms_df = pd.DataFrame(patient_graph.get('symptoms', []))
                st.dataframe(symptoms_df, use_container_width=True)
                
                # Symptom severity visualization
                if 'severity' in symptoms_df.columns:
                    severity_counts = symptoms_df['severity'].value_counts()
                    fig = px.bar(
                        x=severity_counts.index,
                        y=severity_counts.values,
                        title="Symptom Severity Distribution",
                        labels={'x': 'Severity', 'y': 'Count'},
                        color=severity_counts.values,
                        color_continuous_scale="Reds"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No symptoms recorded")
        
        with tab2:
            if patient_graph.get('diseases'):
                diseases_df = pd.DataFrame(patient_graph.get('diseases', []))
                st.dataframe(diseases_df, use_container_width=True)
            else:
                st.info("No diseases recorded")
        
        with tab3:
            if patient_graph.get('drugs'):
                drugs_df = pd.DataFrame(patient_graph.get('drugs', []))
                st.dataframe(drugs_df, use_container_width=True)
                
                # Drug frequency chart
                if 'frequency' in drugs_df.columns:
                    freq_counts = drugs_df['frequency'].value_counts()
                    fig = px.pie(
                        values=freq_counts.values,
                        names=freq_counts.index,
                        title="Medication Frequency Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No medications recorded")
        
        with tab4:
            if patient_graph.get('lab_tests'):
                lab_df = pd.DataFrame(patient_graph.get('lab_tests', []))
                st.dataframe(lab_df, use_container_width=True)
            else:
                st.info("No lab tests recorded")


def show_drug_interactions(patient_id: str):
    """Display drug interaction alerts"""
    st.header("Drug Interaction Risk Assessment")
    
    if not patient_id:
        st.info("Please select a patient from the sidebar")
        return
    
    # Get drug interactions
    interactions = get_api(f"/patients/{patient_id}/drug-interactions")
    risk_alerts = get_api(f"/patients/{patient_id}/drug-risk-alerts")
    patient_graph = get_api(f"/patients/{patient_id}/graph")
    
    if not interactions or len(interactions) == 0:
        st.success("✅ No drug interactions detected for this patient")
        
        # Show patient medications
        if patient_graph and patient_graph.get('drugs'):
            st.subheader("Current Medications")
            drugs_df = pd.DataFrame(patient_graph.get('drugs', []))
            st.dataframe(drugs_df[['name', 'dosage', 'frequency']], use_container_width=True)
        return
    
    # Risk level distribution chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Risk level distribution
        risk_levels = [i.get('risk_level', 'unknown') for i in interactions]
        risk_counts = pd.Series(risk_levels).value_counts()
        
        colors = {
            'high': '#ff6b6b',
            'moderate': '#ffd93d',
            'low': '#6bcf7f',
            'contraindicated': '#dc3545'
        }
        
        fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            title="Drug Interaction Risk Distribution",
            labels={'x': 'Risk Level', 'y': 'Count'},
            color=risk_counts.index,
            color_discrete_map=colors
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Total Interactions", len(interactions))
        high_count = len([i for i in interactions if i.get('risk_level') in ['high', 'contraindicated']])
        moderate_count = len([i for i in interactions if i.get('risk_level') == 'moderate'])
        st.metric("High Risk", high_count, delta=None, delta_color="inverse")
        st.metric("Moderate Risk", moderate_count, delta=None)
    
    # Drug interaction network graph
    st.subheader("📊 Drug Interaction Network")
    
    # Create network graph
    G = nx.Graph()
    drug_colors = {'high': '#ff6b6b', 'moderate': '#ffd93d', 'low': '#6bcf7f'}
    
    for interaction in interactions:
        drug1 = interaction.get('drug1', 'Unknown')
        drug2 = interaction.get('drug2', 'Unknown')
        risk = interaction.get('risk_level', 'low')
        G.add_edge(drug1, drug2, risk=risk, description=interaction.get('description', ''))
    
    if G.number_of_nodes() > 0:
        # Calculate layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Create Plotly network graph
        edge_x = []
        edge_y = []
        edge_info = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            risk = G[edge[0]][edge[1]].get('risk', 'low')
            edge_info.append(f"{edge[0]} ↔ {edge[1]} ({risk})")
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='text',
            mode='lines'
        )
        
        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=30,
                color='lightblue',
                line=dict(width=2, color='black')
            )
        )
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Drug Interaction Network',
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=[dict(
                               text="Nodes represent drugs. Edges represent interactions.",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor='left', yanchor='bottom',
                               font=dict(size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           height=500
                       ))
        st.plotly_chart(fig, use_container_width=True)
    
    # Display risk alerts
    st.subheader("⚠️ Detailed Drug Interaction Alerts")
    
    # Group by risk level
    high_risk = [i for i in interactions if i.get('risk_level') in ['high', 'contraindicated']]
    moderate_risk = [i for i in interactions if i.get('risk_level') == 'moderate']
    low_risk = [i for i in interactions if i.get('risk_level') == 'low']
    
    if high_risk:
        st.markdown("### 🔴 High Risk Interactions")
        for interaction in high_risk:
            with st.expander(f"⚠️ {interaction.get('drug1', 'Unknown')} ↔ {interaction.get('drug2', 'Unknown')}", expanded=True):
                st.markdown(format_risk_level(interaction.get('risk_level', 'high')), unsafe_allow_html=True)
                st.write(f"**Severity:** {interaction.get('severity', 'N/A')}")
                st.write(f"**Description:** {interaction.get('description', 'N/A')}")
                if interaction.get('recommendation'):
                    st.write(f"**Recommendation:** {interaction.get('recommendation')}")
    
    if moderate_risk:
        st.markdown("### 🟡 Moderate Risk Interactions")
        for interaction in moderate_risk:
            with st.expander(f"⚠️ {interaction.get('drug1', 'Unknown')} ↔ {interaction.get('drug2', 'Unknown')}"):
                st.markdown(format_risk_level(interaction.get('risk_level', 'moderate')), unsafe_allow_html=True)
                st.write(f"**Severity:** {interaction.get('severity', 'N/A')}")
                st.write(f"**Description:** {interaction.get('description', 'N/A')}")
                if interaction.get('recommendation'):
                    st.write(f"**Recommendation:** {interaction.get('recommendation')}")
    
    if low_risk:
        st.markdown("### 🟢 Low Risk Interactions")
        for interaction in low_risk:
            with st.expander(f"ℹ️ {interaction.get('drug1', 'Unknown')} ↔ {interaction.get('drug2', 'Unknown')}"):
                st.markdown(format_risk_level(interaction.get('risk_level', 'low')), unsafe_allow_html=True)
                st.write(f"**Severity:** {interaction.get('severity', 'N/A')}")
                st.write(f"**Description:** {interaction.get('description', 'N/A')}")
                if interaction.get('recommendation'):
                    st.write(f"**Recommendation:** {interaction.get('recommendation')}")


def show_similar_patients(patient_id: str):
    """Display similar patients"""
    st.header("Similar Patient Discovery")
    
    if not patient_id:
        st.info("Please select a patient from the sidebar")
        return
    
    limit = st.slider("Number of similar patients to show", 1, 10, 5)
    
    # Get similar patients
    similar_patients = get_api(f"/patients/{patient_id}/similar", params={"limit": limit})
    
    if not similar_patients:
        st.info("No similar patients found")
        return
    
    st.subheader(f"Found {len(similar_patients)} Similar Patients")
    
    for similar in similar_patients:
        with st.expander(f"👤 {similar['patient_name']} (Similarity: {similar['similarity_score']:.2f})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Common Symptoms:**")
                for symptom in similar.get('common_symptoms', []):
                    st.write(f"- {symptom}")
            
            with col2:
                st.write("**Common Diseases:**")
                for disease in similar.get('common_diseases', []):
                    st.write(f"- {disease}")
            
            with col3:
                st.write("**Common Medications:**")
                for drug in similar.get('common_drugs', []):
                    st.write(f"- {drug}")


def show_ai_explanations(patient_id: str):
    """Display AI explanation interface"""
    st.header("AI-Powered Clinical Explanations")
    
    if not patient_id:
        st.info("Please select a patient from the sidebar")
        return
    
    # Get patient info
    patient = get_api(f"/patients/{patient_id}")
    
    st.subheader("Ask a Clinical Question")
    
    # Question input
    question = st.text_area(
        "Enter your clinical question:",
        placeholder="e.g., Why is this drug recommended? What are the risks?",
        height=100
    )
    
    # Optional drug selection
    patient_graph = get_api(f"/patients/{patient_id}/graph")
    drugs = [d['name'] for d in patient_graph.get('drugs', [])] if patient_graph else []
    selected_drug = st.selectbox("Related Drug (Optional):", ["None"] + drugs) if drugs else None
    
    if st.button("Generate Explanation", type="primary"):
        if not question:
            st.warning("Please enter a question")
            return
        
        with st.spinner("Generating AI explanation..."):
            request_data = {
                "patient_id": patient_id,
                "question": question
            }
            
            if selected_drug and selected_drug != "None":
                request_data["drug_name"] = selected_drug
            
            explanation = post_api("/explanations", request_data)
            
            if explanation:
                st.markdown("### 💡 AI Explanation")
                st.write(explanation['explanation'])
                
                st.markdown("### 🔍 Reasoning")
                st.write(explanation['reasoning'])
                
                st.markdown("### 📊 Evidence")
                for evidence in explanation.get('evidence', []):
                    st.write(f"- {evidence}")
                
                st.markdown("### ✅ Recommendations")
                for rec in explanation.get('recommendations', []):
                    st.write(f"- {rec}")
                
                st.markdown("---")
                st.caption("⚠️ This is an AI-generated explanation. Always verify with clinical judgment and consult specialists when needed.")


def show_patient_graph(patient_id: str):
    """Display patient clinical graph visualization"""
    st.header("Patient Clinical Graph Visualization")
    
    if not patient_id:
        st.info("Please select a patient from the sidebar")
        return
    
    # Get patient graph
    patient_graph = get_api(f"/patients/{patient_id}/graph")
    
    if not patient_graph:
        st.error("Could not load patient graph")
        return
    
    patient = patient_graph.get('patient', {})
    st.subheader(f"Clinical Graph for: {patient.get('name', 'Unknown Patient')}")
    
    # Create comprehensive network graph
    G = nx.DiGraph()
    
    # Add patient node (center)
    patient_name = patient.get('name', 'Patient')
    G.add_node(patient_name, node_type='patient', color='#4A90E2', size=50)
    
    # Add symptoms
    for symptom in patient_graph.get('symptoms', []):
        sym_name = symptom.get('name', 'Unknown')
        G.add_node(sym_name, node_type='symptom', color='#FF6B6B', size=20)
        G.add_edge(patient_name, sym_name, relationship='HAS_SYMPTOM')
    
    # Add diseases
    for disease in patient_graph.get('diseases', []):
        dis_name = disease.get('name', 'Unknown')
        G.add_node(dis_name, node_type='disease', color='#FFA500', size=30)
        G.add_edge(patient_name, dis_name, relationship='HAS_DISEASE')
    
    # Add drugs
    for drug in patient_graph.get('drugs', []):
        drug_name = drug.get('name', 'Unknown')
        G.add_node(drug_name, node_type='drug', color='#50C878', size=25)
        G.add_edge(patient_name, drug_name, relationship='TAKES_DRUG')
    
    # Add lab tests
    for test in patient_graph.get('lab_tests', []):
        test_name = test.get('name', 'Unknown')
        G.add_node(test_name, node_type='lab_test', color='#9370DB', size=20)
        G.add_edge(patient_name, test_name, relationship='HAS_LAB_RESULT')
    
    if G.number_of_nodes() > 1:
        # Calculate layout
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
        
        # Separate nodes by type
        patient_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'patient']
        symptom_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'symptom']
        disease_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'disease']
        drug_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'drug']
        lab_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'lab_test']
        
        # Create edge trace
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node traces for each type
        def create_node_trace(nodes, color, size, name):
            node_x = [pos[node][0] for node in nodes]
            node_y = [pos[node][1] for node in nodes]
            return go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                name=name,
                text=nodes,
                textposition="middle center",
                hoverinfo='text',
                marker=dict(
                    size=size,
                    color=color,
                    line=dict(width=2, color='black')
                )
            )
        
        traces = [
            edge_trace,
            create_node_trace(patient_nodes, '#4A90E2', 40, 'Patient'),
            create_node_trace(symptom_nodes, '#FF6B6B', 25, 'Symptoms'),
            create_node_trace(disease_nodes, '#FFA500', 30, 'Diseases'),
            create_node_trace(drug_nodes, '#50C878', 25, 'Drugs'),
            create_node_trace(lab_nodes, '#9370DB', 25, 'Lab Tests')
        ]
        
        fig = go.Figure(
            data=traces,
            layout=go.Layout(
                title='Patient Clinical Graph Network',
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[dict(
                    text="Interactive clinical graph showing patient relationships",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(size=12)
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=700
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Graph statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Nodes", G.number_of_nodes())
        with col2:
            st.metric("Total Edges", G.number_of_edges())
        with col3:
            st.metric("Symptoms", len(symptom_nodes))
        with col4:
            st.metric("Diseases", len(disease_nodes))
    
    # Detailed breakdown
    st.markdown("---")
    st.subheader("Graph Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Graph Structure:**")
        graph_data = {
            'Patient': 1,
            'Symptoms': len(patient_graph.get('symptoms', [])),
            'Diseases': len(patient_graph.get('diseases', [])),
            'Drugs': len(patient_graph.get('drugs', [])),
            'Lab Tests': len(patient_graph.get('lab_tests', []))
        }
        
        fig = px.bar(
            x=list(graph_data.keys()),
            y=list(graph_data.values()),
            title="Clinical Graph Node Distribution",
            labels={'x': 'Node Type', 'y': 'Count'},
            color=list(graph_data.values()),
            color_continuous_scale="Viridis"
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Patient Details:**")
        st.json({
            'Name': patient.get('name'),
            'Age': patient.get('age'),
            'Gender': patient.get('gender'),
            'MRN': patient.get('medical_record_number'),
            'Symptoms Count': len(patient_graph.get('symptoms', [])),
            'Diseases Count': len(patient_graph.get('diseases', [])),
            'Drugs Count': len(patient_graph.get('drugs', [])),
            'Lab Tests Count': len(patient_graph.get('lab_tests', []))
        })
    
    # Raw JSON view
    with st.expander("View Raw Graph Data"):
        st.json(patient_graph)


if __name__ == "__main__":
    main()

