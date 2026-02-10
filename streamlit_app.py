import streamlit as st
import json
import os
from pathlib import Path
import time

# Page configuration
st.set_page_config(
    page_title="Displacement Volume Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #0a1929;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1e3a5f;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: white;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2196f3;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #132f4c 100%);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #2196f3;
        box-shadow: 0 4px 6px rgba(33, 150, 243, 0.3);
    }
    .result-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .result-unit {
        font-size: 1.2rem;
        color: #90caf9;
    }
    h1 {
        color: #66b2ff !important;
    }
    h2, h3 {
        color: #90caf9 !important;
    }
    .stButton>button {
        background-color: #2196f3;
        color: white;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        border-radius: 5px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1976d2;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.4);
    }
    .success-message {
        background-color: #1b5e20;
        color: #a5d6a7;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# Data management
DATA_FILE = 'dva_data.json'

def load_data():
    """Load sample data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(samples):
    """Save sample data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(samples, f, indent=2)

def initialize_data():
    """Initialize with sample data if file doesn't exist"""
    if not os.path.exists(DATA_FILE):
        sample_data = [
            {'id': 'Sample-001', 'weight': 150, 'unit': 'grams'},
            {'id': 'Sample-002', 'weight': 5.5, 'unit': 'ounces'},
            {'id': 'Sample-003', 'weight': 2.3, 'unit': 'pounds'},
            {'id': 'Sample-004', 'weight': 0.75, 'unit': 'kilograms'},
            {'id': 'Sample-005', 'weight': 250, 'unit': 'grams'}
        ]
        save_data(sample_data)

def calculate_volume(weight, unit):
    """Calculate volume conversions"""
    conversions = {
        'grams': {'mm³': 1000, 'cm³': 1, 'in³': 0.061023744},
        'ounces': {'mm³': 28316.8466, 'cm³': 28.3168466, 'in³': 1.7295904},
        'pounds': {'mm³': 453592.37, 'cm³': 453.59237, 'in³': 27.6806742},
        'kilograms': {'mm³': 1000000, 'cm³': 1000, 'in³': 61.023744}
    }
    
    results = conversions[unit]
    return {
        'mm³': weight * results['mm³'],
        'cm³': weight * results['cm³'],
        'in³': weight * results['in³']
    }

# Initialize session state
if 'samples' not in st.session_state:
    initialize_data()
    st.session_state.samples = load_data()

if 'show_success' not in st.session_state:
    st.session_state.show_success = False

# Header
col1, col2 = st.columns([1, 4])

with col1:
    # Display logo if available
    if os.path.exists('dva_logo.png'):
        st.image('dva_logo.png', width=120)
    else:
        st.markdown("# 🔬")

with col2:
    st.markdown("# Displacement Volume Analyzer")
    st.markdown("### Water Displacement Calculator")
    st.markdown("*Based on Archimedes' Principle - Water density at 4°C (1 g/mL)*")

st.markdown("---")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 Calculator", "📋 All Results", "⚙️ Data Manager"])

# TAB 1: Calculator
with tab1:
    st.markdown("## Volume Calculator")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("### Input")
        
        weight = st.number_input(
            "Weight of Water",
            min_value=0.0,
            value=100.0,
            step=0.1,
            format="%.2f"
        )
        
        unit = st.selectbox(
            "Unit",
            ["grams", "ounces", "pounds", "kilograms"],
            index=0
        )
        
        calculate_btn = st.button("🔬 Calculate Volume", use_container_width=True)
    
    with col2:
        st.markdown("### Results")
        
        if calculate_btn or weight:
            results = calculate_volume(weight, unit)
            
            # Display results in columns
            result_col1, result_col2, result_col3 = st.columns(3)
            
            with result_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="color: #ff6b6b; font-weight: bold; font-size: 1.1rem;">Cubic Millimeters</div>
                    <div class="result-value" style="color: #ff6b6b;">{results['mm³']:,.2f}</div>
                    <div class="result-unit">mm³</div>
                </div>
                """, unsafe_allow_html=True)
            
            with result_col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="color: #4ecdc4; font-weight: bold; font-size: 1.1rem;">Cubic Centimeters</div>
                    <div class="result-value" style="color: #4ecdc4;">{results['cm³']:,.2f}</div>
                    <div class="result-unit">cm³</div>
                </div>
                """, unsafe_allow_html=True)
            
            with result_col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="color: #95e1d3; font-weight: bold; font-size: 1.1rem;">Cubic Inches</div>
                    <div class="result-value" style="color: #95e1d3;">{results['in³']:,.3f}</div>
                    <div class="result-unit">in³</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Conversion reference
            st.markdown("---")
            st.markdown("### Conversion Reference")
            st.info(f"""
            **1 {unit}** of water equals:
            - {results['mm³']:,.2f} mm³
            - {results['cm³']:,.2f} cm³  
            - {results['in³']:,.3f} in³
            """)

# TAB 2: All Results
with tab2:
    st.markdown("## All Samples - Batch Conversion Results")
    
    if st.button("🔄 Refresh Results"):
        st.session_state.samples = load_data()
        st.rerun()
    
    if st.session_state.samples:
        # Create results table
        results_data = []
        
        for sample in st.session_state.samples:
            volumes = calculate_volume(sample['weight'], sample['unit'])
            results_data.append({
                'Sample ID': sample['id'],
                'Weight': f"{sample['weight']:.2f}",
                'Unit': sample['unit'],
                'Volume (mm³)': f"{volumes['mm³']:,.2f}",
                'Volume (cm³)': f"{volumes['cm³']:,.2f}",
                'Volume (in³)': f"{volumes['in³']:,.3f}"
            })
        
        # Display as dataframe
        st.dataframe(
            results_data,
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown(f"**Total Samples:** {len(results_data)}")
        
    else:
        st.warning("No samples available. Add samples in the Data Manager tab.")

# TAB 3: Data Manager
with tab3:
    st.markdown("## Sample Data Manager")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Add New Sample")
        
        with st.form("add_sample_form"):
            new_id = st.text_input("Sample ID", placeholder="e.g., Sample-006")
            new_weight = st.number_input("Weight", min_value=0.0, value=100.0, step=0.1)
            new_unit = st.selectbox("Unit", ["grams", "ounces", "pounds", "kilograms"])
            
            submitted = st.form_submit_button("➕ Add Sample", use_container_width=True)
            
            if submitted:
                if new_id.strip():
                    # Check for duplicate ID
                    if any(s['id'] == new_id for s in st.session_state.samples):
                        st.error(f"Sample ID '{new_id}' already exists!")
                    else:
                        st.session_state.samples.append({
                            'id': new_id,
                            'weight': new_weight,
                            'unit': new_unit
                        })
                        save_data(st.session_state.samples)
                        st.success(f"✅ Sample '{new_id}' added successfully!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("Please enter a Sample ID")
    
    with col2:
        st.markdown("### Existing Samples")
        
        if st.session_state.samples:
            st.markdown(f"**Total: {len(st.session_state.samples)} samples**")
            
            # Display samples with delete option
            for idx, sample in enumerate(st.session_state.samples):
                col_a, col_b = st.columns([4, 1])
                
                with col_a:
                    st.text(f"{sample['id']} - {sample['weight']:.2f} {sample['unit']}")
                
                with col_b:
                    if st.button("🗑️", key=f"delete_{idx}"):
                        st.session_state.samples.pop(idx)
                        save_data(st.session_state.samples)
                        st.success(f"Deleted {sample['id']}")
                        time.sleep(0.5)
                        st.rerun()
        else:
            st.info("No samples yet. Add your first sample!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #90caf9; padding: 20px;'>
    <p><strong>Displacement Volume Analyzer v1.0</strong></p>
    <p>Built with precision using Python and Streamlit | Where science meets simplicity 🔬</p>
</div>
""", unsafe_allow_html=True)
