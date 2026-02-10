import streamlit as st
import json
import os
from pathlib import Path
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Displacement Volume Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, sophisticated engineering design
st.markdown("""
<style>
    /* Import distinctive fonts - DM Sans for precision + JetBrains Mono for technical */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;900&family=JetBrains+Mono:wght@400;600&display=swap');
    
    * {
        font-family: 'DM Sans', sans-serif;
    }
    
    /* Technical data uses monospace */
    .mono {
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Brighten all buttons by 5% in off state */
    button[kind="secondary"], button[kind="primary"] {
        filter: brightness(1.05) !important;
    }
    
    /* Extra brightness on hover */
    button[kind="secondary"]:hover, button[kind="primary"]:hover {
        filter: brightness(1.15) !important;
    }
    
    /* Sophisticated dark background with subtle depth */
    .main {
        background: #050b14;
        background-image: 
            radial-gradient(at 40% 20%, rgba(37, 99, 235, 0.05) 0px, transparent 50%),
            radial-gradient(at 80% 0%, rgba(16, 185, 129, 0.05) 0px, transparent 50%),
            radial-gradient(at 0% 50%, rgba(139, 92, 246, 0.05) 0px, transparent 50%);
        position: relative;
    }
    
    /* Noise texture overlay for depth */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0.02;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='3.5' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' /%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 1;
    }
    
    /* Refined glassmorphism cards with precision borders */
    .glass-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 20px;
        padding: 32px;
        box-shadow: 
            0 0 0 1px rgba(255, 255, 255, 0.05) inset,
            0 20px 60px rgba(0, 0, 0, 0.5);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    /* Subtle gradient border on hover */
    .glass-card::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 20px;
        padding: 1px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(139, 92, 246, 0.3));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .glass-card:hover::before {
        opacity: 1;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 
            0 0 0 1px rgba(255, 255, 255, 0.1) inset,
            0 30px 80px rgba(59, 130, 246, 0.15);
        border-color: rgba(96, 165, 250, 0.3);
    }
    
    /* Modern tab system with active indicators */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 16px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background: rgba(30, 41, 59, 0.4);  /* More visible inactive state */
        border-radius: 12px;
        padding: 12px 28px;
        color: #94a3b8;  /* Brighter text for better visibility */
        font-weight: 600;
        font-size: 14px;
        letter-spacing: 0.02em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(148, 163, 184, 0.2);  /* Visible border */
        position: relative;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(59, 130, 246, 0.15);  /* Stronger hover state */
        color: #cbd5e1;
        border-color: rgba(59, 130, 246, 0.4);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border-color: rgba(59, 130, 246, 0.5);
        box-shadow: 
            0 6px 20px rgba(59, 130, 246, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.15) inset;
        transform: translateY(-2px);
    }
    
    /* Sleeker buttons - shorter height */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 8px 20px;  /* Reduced from 14px 36px */
        font-weight: 700;
        border-radius: 10px;
        font-size: 13px;  /* Slightly smaller */
        letter-spacing: 0.02em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 3px 12px rgba(59, 130, 246, 0.35),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        position: relative;
        overflow: hidden;
        min-height: 38px;  /* Sleeker minimum height */
    }
    
    /* Secondary button style (for toggle buttons) */
    .stButton>button[kind="secondary"] {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.3);
        padding: 8px 20px;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.5);
    }
    
    /* Mobile responsiveness - keep buttons and columns side-by-side */
    @media (max-width: 768px) {
        /* Force columns to stay side-by-side on mobile */
        .row-widget.stHorizontalBlock {
            flex-wrap: nowrap !important;
            overflow-x: auto;
        }
        
        /* Keep buttons side-by-side */
        .stButton {
            min-width: fit-content;
            flex-shrink: 0;
        }
        
        .stButton>button {
            padding: 8px 16px;
            font-size: 12px;
            white-space: nowrap;
        }
        
        /* Responsive header */
        h1 {
            font-size: 1.5rem !important;
        }
        
        /* Tabs stay horizontal */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto;
            flex-wrap: nowrap;
        }
        
        .stTabs [data-baseweb="tab"] {
            min-width: fit-content;
            padding: 10px 20px;
            font-size: 13px;
        }
        
        /* Input fields stay side-by-side */
        .stNumberInput, .stTextInput, .stSelectbox {
            min-width: 120px;
        }
    }
    
    /* Precision metric cards with technical aesthetic */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.7) 100%);
        backdrop-filter: blur(15px);
        padding: 28px;
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.12);
        box-shadow: 
            0 0 0 1px rgba(255, 255, 255, 0.03) inset,
            0 12px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    /* Animated shine effect */
    .metric-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        bottom: -50%;
        left: -50%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
        transform: translateX(-100%) rotate(45deg);
        transition: transform 0.6s;
    }
    
    .metric-card:hover::after {
        transform: translateX(100%) rotate(45deg);
    }
    
    .metric-card:hover {
        transform: translateY(-4px) scale(1.01);
        border-color: rgba(96, 165, 250, 0.25);
        box-shadow: 
            0 0 0 1px rgba(255, 255, 255, 0.05) inset,
            0 20px 48px rgba(59, 130, 246, 0.2);
    }
    
    /* Technical result values with mono font */
    .result-value {
        font-size: 3.5rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        margin: 16px 0;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: countUp 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: -0.02em;
    }
    
    @keyframes countUp {
        from {
            opacity: 0;
            transform: translateY(30px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    .result-unit {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    
    /* Button hover effects */
    
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: 
            0 2px 8px rgba(59, 130, 246, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    }
    
    /* Refined input fields */
    .stNumberInput>div>div>input,
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 10px;
        color: #e2e8f0;
        padding: 14px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 15px;
        transition: all 0.25s ease;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.02) inset;
    }
    
    .stNumberInput>div>div>input:focus,
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        background: rgba(15, 23, 42, 0.8);
        border-color: #3b82f6;
        box-shadow: 
            0 0 0 3px rgba(59, 130, 246, 0.12),
            0 0 0 1px rgba(59, 130, 246, 0.3) inset;
        outline: none;
    }
    
    /* Modern select boxes */
    .stSelectbox>div>div {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 10px;
        transition: all 0.25s ease;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.02) inset;
    }
    
    .stSelectbox>div>div:hover {
        border-color: #3b82f6;
        background: rgba(15, 23, 42, 0.7);
    }
    
    /* Gradient headers with technical precision */
    h1 {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin-bottom: 8px;
    }
    
    h2 {
        color: #f1f5f9;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-top: 32px;
        margin-bottom: 16px;
    }
    
    h3 {
        color: #cbd5e1;
        font-weight: 600;
        letter-spacing: -0.01em;
        margin-top: 24px;
        margin-bottom: 12px;
    }
    
    /* Elegant info boxes */
    .stInfo, .stSuccess, .stWarning, .stError {
        background: rgba(15, 23, 42, 0.5);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border-left-width: 3px;
        border-right: 1px solid rgba(148, 163, 184, 0.1);
        border-top: 1px solid rgba(148, 163, 184, 0.1);
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        animation: slideInLeft 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Styled progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
    }
    
    /* Subtle dividers */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.15), transparent);
        margin: 48px 0;
    }
    
    /* Refined expanders */
    .streamlit-expanderHeader {
        background: rgba(15, 23, 42, 0.4);
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.12);
        font-weight: 600;
        transition: all 0.25s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(59, 130, 246, 0.08);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    /* Polished dataframes */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    /* Custom scrollbars */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.3);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.4), rgba(139, 92, 246, 0.4));
        border-radius: 6px;
        border: 2px solid rgba(15, 23, 42, 0.3);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.6), rgba(139, 92, 246, 0.6));
    }
    
    /* Smooth page animations */
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes fadeIn {
        from { 
            opacity: 0;
            transform: translateY(10px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Plotly chart refinements */
    .js-plotly-plot {
        border-radius: 16px;
        overflow: hidden;
    }
    
    /* Hover effects for interactive elements */
    .stCheckbox, .stRadio {
        transition: transform 0.2s ease;
    }
    
    .stCheckbox:hover, .stRadio:hover {
        transform: translateX(4px);
    }
    
    /* Label styling */
    label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        letter-spacing: 0.01em !important;
    }
    
    /* Section headers with accent */
    .section-header {
        position: relative;
        padding-left: 16px;
        margin: 32px 0 16px 0;
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #3b82f6, #8b5cf6);
        border-radius: 2px;
    }
    
    /* Navigation buttons - keep text on single line */
    button[kind="secondary"] p, button[kind="primary"] p {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    /* Ensure button containers don't wrap */
    .stButton > button {
        white-space: nowrap !important;
    }
</style>
""", unsafe_allow_html=True)

# Data management
DATA_FILE = 'dva_data.json'

def load_data():
    """Load sample data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return []
        except (json.JSONDecodeError, ValueError):
            # If JSON is corrupted, return empty list
            return []
    return []

def save_data(samples):
    """Save sample data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(samples, f, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

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

def create_efficiency_gauge(efficiency_percentage):
    """Create animated gauge chart for volume efficiency"""
    # Determine color and status
    if efficiency_percentage >= 95:
        color = "#10b981"  # Emerald green
        status = "OPTIMAL"
    elif efficiency_percentage >= 85:
        color = "#3b82f6"  # Blue
        status = "EXCELLENT"
    elif efficiency_percentage >= 75:
        color = "#8b5cf6"  # Purple
        status = "GOOD"
    elif efficiency_percentage >= 60:
        color = "#f59e0b"  # Amber
        status = "MODERATE"
    elif efficiency_percentage >= 40:
        color = "#f97316"  # Orange
        status = "POOR"
    else:
        color = "#ef4444"  # Red
        status = "CRITICAL"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = efficiency_percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>{status}</b>", 'font': {'size': 24, 'color': color}},
        number = {
            'suffix': "%",
            'font': {'size': 48, 'color': color},
            'valueformat': '.1f'
        },
        delta = {
            'reference': 85,
            'increasing': {'color': "#10b981"},
            'decreasing': {'color': "#ef4444"}
        },
        gauge = {
            'axis': {
                'range': [None, 100],
                'tickwidth': 2,
                'tickcolor': "rgba(148, 163, 184, 0.3)",
                'tickfont': {'color': '#94a3b8', 'size': 12}
            },
            'bar': {'color': color, 'thickness': 0.7},
            'bgcolor': "rgba(255,255,255,0.05)",
            'borderwidth': 2,
            'bordercolor': "rgba(148, 163, 184, 0.2)",
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [40, 60], 'color': 'rgba(249, 115, 22, 0.1)'},
                {'range': [60, 75], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [75, 85], 'color': 'rgba(139, 92, 246, 0.1)'},
                {'range': [85, 95], 'color': 'rgba(59, 130, 246, 0.1)'},
                {'range': [95, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
            ],
            'threshold': {
                'line': {'color': "#60a5fa", 'width': 3},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#e2e8f0"},
        height=300,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def create_3d_box_visualization(length, width, height, product_volume_pct, dimension_unit='inches'):
    """Create interactive 3D box with dimension labels"""
    
    # Determine color based on efficiency
    if product_volume_pct >= 85:
        box_color = '#10b981'  # Green
        fill_color = 'rgba(16, 185, 129, 0.3)'
    elif product_volume_pct >= 75:
        box_color = '#3b82f6'  # Blue
        fill_color = 'rgba(59, 130, 246, 0.3)'
    elif product_volume_pct >= 60:
        box_color = '#f59e0b'  # Orange
        fill_color = 'rgba(245, 158, 11, 0.3)'
    else:
        box_color = '#ef4444'  # Red
        fill_color = 'rgba(239, 68, 68, 0.3)'
    
    # Define vertices of box (centered at origin)
    l, w, h = length/2, width/2, height/2
    vertices = [
        [-l, -w, -h], [l, -w, -h], [l, w, -h], [-l, w, -h],  # Bottom
        [-l, -w, h], [l, -w, h], [l, w, h], [-l, w, h]   # Top
    ]
    
    # Define edges
    edges = [
        [0,1], [1,2], [2,3], [3,0],  # Bottom
        [4,5], [5,6], [6,7], [7,4],  # Top
        [0,4], [1,5], [2,6], [3,7]   # Vertical
    ]
    
    fig = go.Figure()
    
    # Draw edges
    for edge in edges:
        v1, v2 = vertices[edge[0]], vertices[edge[1]]
        fig.add_trace(go.Scatter3d(
            x=[v1[0], v2[0]],
            y=[v1[1], v2[1]],
            z=[v1[2], v2[2]],
            mode='lines',
            line=dict(color=box_color, width=6),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add semi-transparent faces
    faces_i = [0, 0, 0, 0, 4, 4]
    faces_j = [1, 3, 4, 1, 5, 7]
    faces_k = [2, 7, 5, 5, 6, 6]
    
    fig.add_trace(go.Mesh3d(
        x=[v[0] for v in vertices],
        y=[v[1] for v in vertices],
        z=[v[2] for v in vertices],
        i=faces_i,
        j=faces_j,
        k=faces_k,
        color=box_color,
        opacity=0.15,
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add dimension annotations
    # Length arrow (along X-axis, bottom front)
    fig.add_trace(go.Scatter3d(
        x=[-l, l],
        y=[-w-0.3*w, -w-0.3*w],
        z=[-h, -h],
        mode='lines+text',
        line=dict(color='white', width=3),
        text=['', f'{length:.1f} {dimension_unit}'],
        textposition='top center',
        textfont=dict(size=12, color='white'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Width arrow (along Y-axis, bottom right)
    fig.add_trace(go.Scatter3d(
        x=[l+0.3*l, l+0.3*l],
        y=[-w, w],
        z=[-h, -h],
        mode='lines+text',
        line=dict(color='white', width=3),
        text=['', f'{width:.1f} {dimension_unit}'],
        textposition='top center',
        textfont=dict(size=12, color='white'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Height arrow (along Z-axis, back left)
    fig.add_trace(go.Scatter3d(
        x=[-l-0.3*l, -l-0.3*l],
        y=[w, w],
        z=[-h, h],
        mode='lines+text',
        line=dict(color='white', width=3),
        text=['', f'{height:.1f} {dimension_unit}'],
        textposition='middle right',
        textfont=dict(size=12, color='white'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add efficiency label
    fig.add_trace(go.Scatter3d(
        x=[0],
        y=[0],
        z=[h+0.4*h],
        mode='text',
        text=[f'{product_volume_pct:.1f}% Efficient'],
        textfont=dict(size=14, color=box_color),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(visible=False, showgrid=False, zeroline=False, showticklabels=False),
            zaxis=dict(visible=False, showgrid=False, zeroline=False, showticklabels=False),
            bgcolor='rgba(15, 23, 42, 0.4)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2),
                up=dict(x=0, y=0, z=1)
            ),
            aspectmode='data'
        ),
        height=486,  # Reduced by 19% total for better fit
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig

def create_3d_volume_preview(length, width, height, product_volume_pct, dimension_unit='inches', 
                            product_volume=None, product_weight=None, product_quantity=1):
    """Create clean 3D Volume Preview with liquid fill - ONLY measurement numbers on graphic"""
    
    # Colors
    box_color = '#3b82f6'  # Blue for box
    liquid_color = '#10b981'  # Green for liquid/product
    
    # Calculate liquid fill height based on volume percentage
    fill_height = height * (product_volume_pct / 100)
    
    # Define vertices for SECONDARY PACKAGING BOX (full size, centered at origin)
    l, w, h = length/2, width/2, height/2
    box_vertices = [
        [-l, -w, -h], [l, -w, -h], [l, w, -h], [-l, w, -h],  # Bottom
        [-l, -w, h], [l, -w, h], [l, w, h], [-l, w, h]   # Top
    ]
    
    # Define edges for box
    edges = [
        [0,1], [1,2], [2,3], [3,0],  # Bottom
        [4,5], [5,6], [6,7], [7,4],  # Top
        [0,4], [1,5], [2,6], [3,7]   # Vertical
    ]
    
    fig = go.Figure()
    
    # === DRAW SECONDARY PACKAGING BOX (BLUE WIREFRAME) ===
    for edge in edges:
        v1, v2 = box_vertices[edge[0]], box_vertices[edge[1]]
        fig.add_trace(go.Scatter3d(
            x=[v1[0], v2[0]],
            y=[v1[1], v2[1]],
            z=[v1[2], v2[2]],
            mode='lines',
            line=dict(color=box_color, width=6),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add semi-transparent box faces
    faces_i = [0, 0, 0, 0, 4, 4]
    faces_j = [1, 3, 4, 1, 5, 7]
    faces_k = [2, 7, 5, 5, 6, 6]
    
    fig.add_trace(go.Mesh3d(
        x=[v[0] for v in box_vertices],
        y=[v[1] for v in box_vertices],
        z=[v[2] for v in box_vertices],
        i=faces_i,
        j=faces_j,
        k=faces_k,
        color=box_color,
        opacity=0.08,
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # === DRAW LIQUID FILL (GREEN) - Product volume as liquid ===
    if product_volume_pct > 0:
        liquid_vertices = [
            [-l, -w, -h], [l, -w, -h], [l, w, -h], [-l, w, -h],  # Bottom (same as box)
            [-l, -w, -h + fill_height], [l, -w, -h + fill_height],  # Top of liquid
            [l, w, -h + fill_height], [-l, w, -h + fill_height]
        ]
        
        # Draw liquid as solid mesh (semi-transparent green)
        fig.add_trace(go.Mesh3d(
            x=[v[0] for v in liquid_vertices],
            y=[v[1] for v in liquid_vertices],
            z=[v[2] for v in liquid_vertices],
            i=faces_i,
            j=faces_j,
            k=faces_k,
            color=liquid_color,
            opacity=0.4,
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add liquid surface line (top edge of liquid)
        liquid_surface_edges = [[4,5], [5,6], [6,7], [7,4]]  # Top edges
        for edge in liquid_surface_edges:
            v1, v2 = liquid_vertices[edge[0]], liquid_vertices[edge[1]]
            fig.add_trace(go.Scatter3d(
                x=[v1[0], v2[0]],
                y=[v1[1], v2[1]],
                z=[v1[2], v2[2]],
                mode='lines',
                line=dict(color=liquid_color, width=5),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # === MEASUREMENT SCALES WITH INCREMENTAL NUMBERS ONLY ===
    
    # HEIGHT scale (left side, back)
    offset_x = -l - 0.3 * l
    offset_y = w + 0.2 * w
    
    # Vertical measurement line
    fig.add_trace(go.Scatter3d(
        x=[offset_x, offset_x],
        y=[offset_y, offset_y],
        z=[-h, h],
        mode='lines',
        line=dict(color='white', width=4),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Height ticks with NUMBERS (increments based on height)
    num_ticks = 5
    height_increment = height / num_ticks
    for i in range(num_ticks + 1):
        tick_z = -h + (2*h * i / num_ticks)
        tick_value = i * height_increment
        
        # Tick mark
        fig.add_trace(go.Scatter3d(
            x=[offset_x - 0.05*l, offset_x + 0.05*l],
            y=[offset_y, offset_y],
            z=[tick_z, tick_z],
            mode='lines',
            line=dict(color='white', width=3),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # NUMBER label (offset left from line)
        fig.add_trace(go.Scatter3d(
            x=[offset_x - 0.15*l],
            y=[offset_y],
            z=[tick_z],
            mode='text',
            text=[f'<b>{tick_value:.1f}"</b>'],
            textfont=dict(size=14, color='white'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # LENGTH scale (bottom front)
    offset_z = -h - 0.3 * h
    offset_y_len = -w - 0.2 * w
    
    # Horizontal measurement line
    fig.add_trace(go.Scatter3d(
        x=[-l, l],
        y=[offset_y_len, offset_y_len],
        z=[offset_z, offset_z],
        mode='lines',
        line=dict(color='white', width=4),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Length ticks with NUMBERS
    length_increment = length / num_ticks
    for i in range(num_ticks + 1):
        tick_x = -l + (2*l * i / num_ticks)
        tick_value = i * length_increment
        
        # Tick mark
        fig.add_trace(go.Scatter3d(
            x=[tick_x, tick_x],
            y=[offset_y_len, offset_y_len],
            z=[offset_z - 0.05*h, offset_z + 0.05*h],
            mode='lines',
            line=dict(color='white', width=3),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # NUMBER label (offset below line)
        fig.add_trace(go.Scatter3d(
            x=[tick_x],
            y=[offset_y_len],
            z=[offset_z - 0.18*h],
            mode='text',
            text=[f'<b>{tick_value:.1f}"</b>'],
            textfont=dict(size=14, color='white'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # WIDTH scale (bottom right)
    offset_x_wid = l + 0.3 * l
    
    # Depth measurement line
    fig.add_trace(go.Scatter3d(
        x=[offset_x_wid, offset_x_wid],
        y=[-w, w],
        z=[offset_z, offset_z],
        mode='lines',
        line=dict(color='white', width=4),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Width ticks with NUMBERS
    width_increment = width / num_ticks
    for i in range(num_ticks + 1):
        tick_y = -w + (2*w * i / num_ticks)
        tick_value = i * width_increment
        
        # Tick mark
        fig.add_trace(go.Scatter3d(
            x=[offset_x_wid - 0.05*l, offset_x_wid + 0.05*l],
            y=[tick_y, tick_y],
            z=[offset_z, offset_z],
            mode='lines',
            line=dict(color='white', width=3),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # NUMBER label (offset right from line)
        fig.add_trace(go.Scatter3d(
            x=[offset_x_wid + 0.15*l],
            y=[tick_y],
            z=[offset_z],
            mode='text',
            text=[f'<b>{tick_value:.1f}"</b>'],
            textfont=dict(size=14, color='white'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # NO OTHER TEXT - Clean graphic with only measurement numbers!
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(visible=False, showgrid=False, zeroline=False, showticklabels=False),
            zaxis=dict(visible=False, showgrid=False, zeroline=False, showticklabels=False),
            bgcolor='rgba(15, 23, 42, 0.4)',
            camera=dict(
                eye=dict(x=1.7, y=1.7, z=1.4),
                up=dict(x=0, y=0, z=1)
            ),
            aspectmode='data'
        ),
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig


def create_volume_comparison_chart(box_volume, product_volume, unit='cubic inches'):
    """Create horizontal stacked bar chart for volume comparison"""
    efficiency = (product_volume / box_volume * 100) if box_volume > 0 else 0
    remaining = box_volume - product_volume
    
    fig = go.Figure()
    
    # Product volume bar
    fig.add_trace(go.Bar(
        y=['Utilization'],
        x=[product_volume],
        name='Product Volume',
        orientation='h',
        marker=dict(
            color='#3b82f6',
            line=dict(color='#2563eb', width=2)
        ),
        text=f'{product_volume:.2f} {unit}<br>({efficiency:.1f}%)',
        textposition='inside',
        textfont=dict(color='white', size=14),
        hovertemplate=f'Product: {product_volume:.2f} {unit}<br>Efficiency: {efficiency:.1f}%<extra></extra>'
    ))
    
    # Remaining space bar
    fig.add_trace(go.Bar(
        y=['Utilization'],
        x=[remaining],
        name='Remaining Space',
        orientation='h',
        marker=dict(
            color='#10b981' if remaining > 0 else '#ef4444',
            line=dict(color='#059669' if remaining > 0 else '#dc2626', width=2)
        ),
        text=f'{remaining:.2f} {unit}<br>({100-efficiency:.1f}%)',
        textposition='inside',
        textfont=dict(color='white', size=14),
        hovertemplate=f'Remaining: {remaining:.2f} {unit}<br>Free: {100-efficiency:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        xaxis=dict(
            title=dict(text=f'Volume ({unit})', font=dict(color='#94a3b8')),
            gridcolor='rgba(148, 163, 184, 0.2)',
            zerolinecolor='rgba(148, 163, 184, 0.3)'
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False
        ),
        height=150,
        margin=dict(l=0, r=0, t=30, b=40),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=12)
        ),
        hovermode='closest'
    )
    
    return fig

def create_donut_chart(efficiency_percentage):
    """Create donut chart for space distribution"""
    remaining_pct = 100 - efficiency_percentage
    
    # Determine colors based on efficiency
    if efficiency_percentage >= 85:
        product_color = '#10b981'
    elif efficiency_percentage >= 75:
        product_color = '#3b82f6'
    elif efficiency_percentage >= 60:
        product_color = '#f59e0b'
    else:
        product_color = '#ef4444'
    
    remaining_color = '#94a3b8' if remaining_pct > 0 else '#ef4444'
    
    fig = go.Figure(data=[go.Pie(
        labels=['Product Volume', 'Free Space'],
        values=[efficiency_percentage, remaining_pct],
        hole=.6,
        marker=dict(
            colors=[product_color, remaining_color],
            line=dict(color='rgba(10, 25, 41, 0.8)', width=3)
        ),
        textinfo='label+percent',
        textfont=dict(size=13, color='white'),
        hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>',
        pull=[0.05, 0]
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5,
            font=dict(size=12)
        ),
        height=300,
        margin=dict(l=20, r=20, t=40, b=60),
        annotations=[dict(
            text=f'<b>{efficiency_percentage:.1f}%</b><br><span style="font-size:12px">Filled</span>',
            x=0.5, y=0.5,
            font=dict(size=24, color=product_color),
            showarrow=False
        )]
    )
    
    return fig

def create_mini_efficiency_bar(efficiency_pct):
    """Create mini horizontal bar chart for project efficiency"""
    # Determine color based on efficiency
    if efficiency_pct >= 85:
        color = '#10b981'
        label = 'Excellent'
    elif efficiency_pct >= 75:
        color = '#3b82f6'
        label = 'Good'
    elif efficiency_pct >= 60:
        color = '#f59e0b'
        label = 'Fair'
    else:
        color = '#ef4444'
        label = 'Poor'
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=[efficiency_pct],
        y=[''],
        orientation='h',
        marker=dict(
            color=color,
            line=dict(color='rgba(255,255,255,0.2)', width=1)
        ),
        hovertemplate=f'<b>{efficiency_pct:.1f}% Filled</b><br>{label} Efficiency<extra></extra>',
        showlegend=False,
        hoverlabel=dict(
            bgcolor=color,
            font=dict(color='white', size=14, family='DM Sans')
        )
    ))
    
    fig.update_layout(
        xaxis=dict(
            range=[0, 100],
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False
        ),
        height=35,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='closest'
    )
    
    return fig

def create_volume_breakdown_bar(product_volume, remaining_volume, unit):
    """Create volume breakdown stacked bar chart showing product vs remaining"""
    total = product_volume + remaining_volume
    product_pct = (product_volume / total * 100) if total > 0 else 0
    remaining_pct = (remaining_volume / total * 100) if total > 0 else 0
    
    fig = go.Figure()
    
    # Product volume (filled portion) - GREEN (always green for product)
    fig.add_trace(go.Bar(
        x=[product_volume],
        y=['Volume'],
        orientation='h',
        name='Product Volume',
        marker=dict(color='#10b981'),  # Green for product
        text=f'{product_volume:.2f} {unit}',
        textposition='inside',
        textfont=dict(size=18),  # 50% larger (was 12, now 18)
        hovertemplate=f'<b>Product Volume</b><br>{product_volume:.2f} {unit}<br>{product_pct:.1f}%<extra></extra>',
        showlegend=True
    ))
    
    # Remaining volume (empty space) - BLUE
    fig.add_trace(go.Bar(
        x=[remaining_volume],
        y=['Volume'],
        orientation='h',
        name='Remaining Space',
        marker=dict(color='#3b82f6'),  # Blue for remaining
        text=f'{remaining_volume:.2f} {unit}' if remaining_volume > 0 else '',
        textposition='inside',
        textfont=dict(size=18),  # 50% larger (was 12, now 18)
        hovertemplate=f'<b>Remaining Space</b><br>{remaining_volume:.2f} {unit}<br>{remaining_pct:.1f}%<extra></extra>',
        showlegend=True
    ))
    
    fig.update_layout(
        barmode='stack',
        height=78,  # Increased by 30% from 60px for better legibility
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=15)  # 50% larger legend (was 10, now 15)
        ),
        hovermode='closest'
    )
    
    return fig

def create_2d_box_illustration(length, width, height, unit='inches'):
    """Create dynamic 2D box illustration with dimension callouts"""
    if length <= 0 or width <= 0 or height <= 0:
        return """
        <div style="text-align: center; padding: 100px 0; color: #64748b;">
            <p style="font-size: 1.2rem;">📦</p>
            <p>Enter dimensions to see preview</p>
        </div>
        """
    
    # Scale for visualization (keeping proportions)
    max_dim = max(length, width, height)
    scale = 300 / max_dim
    
    l_scaled = length * scale
    w_scaled = width * scale * 0.6  # Perspective effect
    h_scaled = height * scale
    
    # SVG dimensions
    svg_width = 500
    svg_height = 450
    
    # Center the box
    offset_x = (svg_width - l_scaled - w_scaled) / 2
    offset_y = (svg_height - h_scaled) / 2 + 50
    
    # Create SVG
    svg = f"""
    <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg" style="background: transparent;">
        <defs>
            <linearGradient id="boxGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0.3" />
                <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:0.5" />
            </linearGradient>
            <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        
        <!-- Back face -->
        <polygon points="{offset_x + w_scaled},{offset_y} {offset_x + w_scaled + l_scaled},{offset_y} {offset_x + w_scaled + l_scaled},{offset_y + h_scaled} {offset_x + w_scaled},{offset_y + h_scaled}"
                 fill="url(#boxGradient)" stroke="#60a5fa" stroke-width="2" opacity="0.4"/>
        
        <!-- Left face -->
        <polygon points="{offset_x},{offset_y + w_scaled * 0.5} {offset_x + w_scaled},{offset_y} {offset_x + w_scaled},{offset_y + h_scaled} {offset_x},{offset_y + h_scaled + w_scaled * 0.5}"
                 fill="url(#boxGradient)" stroke="#60a5fa" stroke-width="2" opacity="0.6"/>
        
        <!-- Front face -->
        <polygon points="{offset_x},{offset_y + w_scaled * 0.5} {offset_x + l_scaled},{offset_y + w_scaled * 0.5} {offset_x + l_scaled},{offset_y + h_scaled + w_scaled * 0.5} {offset_x},{offset_y + h_scaled + w_scaled * 0.5}"
                 fill="url(#boxGradient)" stroke="#60a5fa" stroke-width="3" filter="url(#glow)"/>
        
        <!-- Top face -->
        <polygon points="{offset_x},{offset_y + w_scaled * 0.5} {offset_x + w_scaled},{offset_y} {offset_x + w_scaled + l_scaled},{offset_y} {offset_x + l_scaled},{offset_y + w_scaled * 0.5}"
                 fill="url(#boxGradient)" stroke="#60a5fa" stroke-width="2" opacity="0.7"/>
        
        <!-- Length dimension line (bottom) -->
        <line x1="{offset_x}" y1="{offset_y + h_scaled + w_scaled * 0.5 + 30}" 
              x2="{offset_x + l_scaled}" y2="{offset_y + h_scaled + w_scaled * 0.5 + 30}" 
              stroke="#10b981" stroke-width="2"/>
        <line x1="{offset_x}" y1="{offset_y + h_scaled + w_scaled * 0.5 + 25}" 
              x2="{offset_x}" y2="{offset_y + h_scaled + w_scaled * 0.5 + 35}" 
              stroke="#10b981" stroke-width="2"/>
        <line x1="{offset_x + l_scaled}" y1="{offset_y + h_scaled + w_scaled * 0.5 + 25}" 
              x2="{offset_x + l_scaled}" y2="{offset_y + h_scaled + w_scaled * 0.5 + 35}" 
              stroke="#10b981" stroke-width="2"/>
        <text x="{offset_x + l_scaled/2}" y="{offset_y + h_scaled + w_scaled * 0.5 + 55}" 
              fill="#10b981" font-size="16" font-weight="bold" text-anchor="middle" font-family="JetBrains Mono, monospace">
            L: {length:.1f} {unit}
        </text>
        
        <!-- Height dimension line (left side) -->
        <line x1="{offset_x - 30}" y1="{offset_y + w_scaled * 0.5}" 
              x2="{offset_x - 30}" y2="{offset_y + h_scaled + w_scaled * 0.5}" 
              stroke="#f59e0b" stroke-width="2"/>
        <line x1="{offset_x - 35}" y1="{offset_y + w_scaled * 0.5}" 
              x2="{offset_x - 25}" y2="{offset_y + w_scaled * 0.5}" 
              stroke="#f59e0b" stroke-width="2"/>
        <line x1="{offset_x - 35}" y1="{offset_y + h_scaled + w_scaled * 0.5}" 
              x2="{offset_x - 25}" y2="{offset_y + h_scaled + w_scaled * 0.5}" 
              stroke="#f59e0b" stroke-width="2"/>
        <text x="{offset_x - 45}" y="{offset_y + h_scaled/2 + w_scaled * 0.5}" 
              fill="#f59e0b" font-size="16" font-weight="bold" text-anchor="end" font-family="JetBrains Mono, monospace"
              transform="rotate(-90 {offset_x - 45} {offset_y + h_scaled/2 + w_scaled * 0.5})">
            H: {height:.1f} {unit}
        </text>
        
        <!-- Width dimension line (top right) -->
        <line x1="{offset_x + l_scaled}" y1="{offset_y + w_scaled * 0.5 - 30}" 
              x2="{offset_x + l_scaled + w_scaled}" y2="{offset_y - 30}" 
              stroke="#8b5cf6" stroke-width="2"/>
        <line x1="{offset_x + l_scaled - 5}" y1="{offset_y + w_scaled * 0.5 - 25}" 
              x2="{offset_x + l_scaled + 5}" y2="{offset_y + w_scaled * 0.5 - 35}" 
              stroke="#8b5cf6" stroke-width="2"/>
        <line x1="{offset_x + l_scaled + w_scaled - 5}" y1="{offset_y - 25}" 
              x2="{offset_x + l_scaled + w_scaled + 5}" y2="{offset_y - 35}" 
              stroke="#8b5cf6" stroke-width="2"/>
        <text x="{offset_x + l_scaled + w_scaled/2 + 20}" y="{offset_y + w_scaled * 0.25 - 35}" 
              fill="#8b5cf6" font-size="16" font-weight="bold" text-anchor="middle" font-family="JetBrains Mono, monospace">
            W: {width:.1f} {unit}
        </text>
        
        <!-- Title -->
        <text x="{svg_width/2}" y="30" 
              fill="#e2e8f0" font-size="18" font-weight="bold" text-anchor="middle">
            📦 Box Dimensions Preview
        </text>
    </svg>
    """
    
    return svg

def ensure_valid_json_file(filename, default_data=None):
    """Ensure JSON file exists and is valid"""
    if default_data is None:
        default_data = []
    
    if not os.path.exists(filename):
        # Create file with default data
        try:
            with open(filename, 'w') as f:
                json.dump(default_data, f, indent=2)
        except:
            pass
    else:
        # Validate existing file
        try:
            with open(filename, 'r') as f:
                content = f.read().strip()
                if not content:
                    # Empty file, write default
                    with open(filename, 'w') as f:
                        json.dump(default_data, f, indent=2)
                else:
                    # Try to parse
                    json.loads(content)
        except (json.JSONDecodeError, ValueError):
            # Corrupted file, backup and recreate
            try:
                if os.path.exists(filename):
                    os.rename(filename, f"{filename}.backup")
            except:
                pass
            with open(filename, 'w') as f:
                json.dump(default_data, f, indent=2)

# Initialize session state
if 'samples' not in st.session_state:
    initialize_data()
    st.session_state.samples = load_data()

if 'show_success' not in st.session_state:
    st.session_state.show_success = False

# Header - Mobile-friendly horizontal layout
header_col1, header_col2 = st.columns([1, 6])

with header_col1:
    # Display logo if available
    if os.path.exists('dva_logo.png'):
        st.image('dva_logo.png', width=100)
    else:
        st.markdown("# 🔬")

with header_col2:
    st.markdown("""
    <div style="display: flex; align-items: center; height: 100px;">
        <div>
            <h1 style="margin: 0; padding: 0; line-height: 1.2;">Displacement Volume Analyzer</h1>
            <p style="margin: 0; padding: 0; font-size: 0.75rem; color: #94a3b8; font-style: italic;">
                Archimedes' Principle | Water at 4°C (1 g/mL)
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Initialize session state for projects
if 'projects' not in st.session_state:
    st.session_state.projects = []
    
    # Ensure JSON file is valid before trying to load
    ensure_valid_json_file('dva_projects.json', [])
    
    # Load projects from file if exists
    if os.path.exists('dva_projects.json'):
        try:
            with open('dva_projects.json', 'r') as f:
                content = f.read().strip()
                if content:  # Check if file is not empty
                    st.session_state.projects = json.loads(content)
                else:
                    st.session_state.projects = []
        except (json.JSONDecodeError, ValueError) as e:
            # If JSON is corrupted, start with empty list and backup bad file
            st.session_state.projects = []
            # Optionally backup the corrupted file
            if os.path.exists('dva_projects.json'):
                try:
                    os.rename('dva_projects.json', 'dva_projects.json.backup')
                except:
                    pass

if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = None

def get_next_project_number():
    """Get the next available unique project number"""
    if not st.session_state.projects:
        return 1000
    
    # Get all existing project numbers
    existing_numbers = [p['project_number'] for p in st.session_state.projects]
    
    # Find the maximum and add 1
    return max(existing_numbers) + 1

if 'project_counter' not in st.session_state:
    # Initialize counter from existing projects or start at 1000
    st.session_state.project_counter = get_next_project_number()

# Initialize current project number to match counter
if 'current_project_number' not in st.session_state:
    st.session_state.current_project_number = st.session_state.project_counter

# Initialize with default values on first load
if 'app_initialized' not in st.session_state:
    st.session_state.app_initialized = True
    st.session_state.project_name = 'New Project'
    st.session_state.project_date = datetime.now().date()
    st.session_state.designer = 'Designer Name'
    st.session_state.project_description = 'Project description here'
    st.session_state.contact_info = 'contact@email.com'
    st.session_state.primary_weight = 100.0
    st.session_state.primary_unit = 'grams'
    st.session_state.box_length = 10.0
    st.session_state.box_width = 10.0
    st.session_state.box_height = 10.0
    st.session_state.dimension_unit = 'cm'
    st.session_state.box_result_unit = 'cubic cm'

def save_projects():
    """Save projects to JSON file"""
    try:
        with open('dva_projects.json', 'w') as f:
            json.dump(st.session_state.projects, f, indent=2)
    except Exception as e:
        st.error(f"Error saving projects: {str(e)}")

def create_new_project():
    """Create a new project and reset form with default values"""
    # Clear the current project ID to force new project mode
    st.session_state.current_project_id = None
    
    # Force recalculation of project number by clearing it temporarily
    if 'current_project_number' in st.session_state:
        del st.session_state['current_project_number']
    
    # Get next unique project number (checks against all existing projects)
    next_number = get_next_project_number()
    st.session_state.project_counter = next_number
    st.session_state.current_project_number = next_number
    
    # Set default values for project info
    st.session_state.project_name = 'New Project'
    st.session_state.project_date = datetime.now().date()
    st.session_state.designer = 'Designer Name'
    st.session_state.project_description = 'Project description here'
    st.session_state.contact_info = 'contact@email.com'
    
    # Clear/reset calculator input fields to 0
    st.session_state.product_weight = 0.0  # Reset to 0 instead of delete
    st.session_state.product_quantity = 1  # Reset to 1 (default)
    
    # Clear calculated values
    if 'primary_volume_mm3' in st.session_state:
        del st.session_state.primary_volume_mm3
    if 'total_product_volume_mm3' in st.session_state:
        del st.session_state.total_product_volume_mm3
    
    # Clear box dimension fields to 0
    st.session_state.box_length = 0.0
    st.session_state.box_width = 0.0
    st.session_state.box_height = 0.0
    
    # Clear box volume
    if 'box_volume_mm3' in st.session_state:
        del st.session_state.box_volume_mm3
    
    # Clear ALL saved section data
    if 'saved_primary_data' in st.session_state:
        del st.session_state.saved_primary_data
    if 'saved_secondary_data' in st.session_state:
        del st.session_state.saved_secondary_data
    if 'saved_analysis_data' in st.session_state:
        del st.session_state.saved_analysis_data
    
    # Delete persistent data files
    if os.path.exists('dva_analysis_data.json'):
        try:
            os.remove('dva_analysis_data.json')
        except Exception:
            pass  # Silent fail
    
    if os.path.exists('dva_secondary_data.json'):
        try:
            os.remove('dva_secondary_data.json')
        except Exception:
            pass  # Silent fail
    
    # Rerun to refresh display
    st.rerun()

def save_current_project():
    """Save or update current project"""
    
    # Gather all project data
    # Use stored project_date or current date
    project_date = st.session_state.get('project_date', datetime.now().date())
    # Convert date to string if it's a date object
    if hasattr(project_date, 'strftime'):
        project_date_str = project_date.strftime('%Y-%m-%d')
    else:
        project_date_str = str(project_date)
    
    current_number = st.session_state.get('current_project_number', st.session_state.project_counter)
    
    # Check for duplicate project numbers (only for new projects)
    if st.session_state.current_project_id is None:
        # This is a new project, check if number already exists
        existing_numbers = [p['project_number'] for p in st.session_state.projects]
        if current_number in existing_numbers:
            # Number exists! Get next unique number
            st.error(f"⚠️ Project #{current_number} already exists! Assigning new number...")
            current_number = get_next_project_number()
            st.session_state.current_project_number = current_number
            st.session_state.project_counter = current_number
            st.warning(f"✅ Assigned new project number: {current_number}")
    
    project_data = {
        'project_number': current_number,
        'project_name': st.session_state.get('project_name', ''),
        'date': project_date_str,
        'designer': st.session_state.get('designer', ''),
        'description': st.session_state.get('project_description', ''),
        'contact': st.session_state.get('contact_info', ''),
        # Primary product data
        'weight': st.session_state.get('primary_weight', 0.0),
        'weight_unit': st.session_state.get('primary_unit', 'grams'),
        'primary_volume_mm3': st.session_state.get('primary_volume_mm3', 0.0),
        'product_quantity': st.session_state.get('product_quantity', 1),
        'total_product_volume_mm3': st.session_state.get('total_product_volume_mm3', st.session_state.get('primary_volume_mm3', 0.0)),
        # Box data
        'box_length': st.session_state.get('box_length', 0.0),
        'box_width': st.session_state.get('box_width', 0.0),
        'box_height': st.session_state.get('box_height', 0.0),
        'dimension_unit': st.session_state.get('dimension_unit', 'cm'),
        'box_result_unit': st.session_state.get('box_result_unit', 'cubic cm'),
        'box_volume_mm3': st.session_state.get('box_volume_mm3', 0.0),
        'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Update existing or add new
    if st.session_state.current_project_id is not None:
        # Update existing project
        for i, p in enumerate(st.session_state.projects):
            if p['project_number'] == st.session_state.current_project_id:
                st.session_state.projects[i] = project_data
                break
    else:
        # Add new project
        st.session_state.projects.append(project_data)
        st.session_state.current_project_id = project_data['project_number']
        # Counter already incremented in create_new_project()
    
    save_projects()
    return True

def load_project(project_number):
    """Load a project's data into the form"""
    for project in st.session_state.projects:
        if project['project_number'] == project_number:
            st.session_state.current_project_id = project_number
            st.session_state.current_project_number = project['project_number']
            st.session_state.project_name = project['project_name']
            # Convert date string to date object
            try:
                st.session_state.project_date = datetime.strptime(project['date'], '%Y-%m-%d').date()
            except:
                st.session_state.project_date = datetime.now().date()
            st.session_state.designer = project['designer']
            st.session_state.project_description = project['description']
            st.session_state.contact_info = project['contact']
            st.session_state.primary_weight = project['weight']
            st.session_state.primary_unit = project['weight_unit']
            st.session_state.primary_volume_mm3 = project['primary_volume_mm3']
            st.session_state.box_length = project['box_length']
            st.session_state.box_width = project['box_width']
            st.session_state.box_height = project['box_height']
            st.session_state.dimension_unit = project['dimension_unit']
            st.session_state.box_result_unit = project['box_result_unit']
            st.session_state.box_volume_mm3 = project['box_volume_mm3']
            st.rerun()
            break

# ========== GLOBAL INITIALIZATION (BEFORE TABS) ==========
# Initialize unit preferences (always, even if not showing)
if 'pref_dimension_unit' not in st.session_state:
    st.session_state.pref_dimension_unit = 'inches'
if 'pref_weight_unit' not in st.session_state:
    st.session_state.pref_weight_unit = 'ounces'
if 'pref_volume_unit' not in st.session_state:
    st.session_state.pref_volume_unit = 'cubic inches'

# DO NOT initialize input fields here - let them start empty
# Streamlit will handle them via widget keys

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔬 Analyzer", "📁 Project Results", "📋 Primary Results", "⚙️ Primary Data"])

# TAB 1: Analyzer
with tab1:
    # ========== INITIALIZE NAVIGATION STATE ==========
    if 'analyzer_section' not in st.session_state:
        st.session_state.analyzer_section = 'primary'  # primary, secondary, analysis
    
    if 'show_project_info' not in st.session_state:
        st.session_state.show_project_info = False
    
    if 'show_unit_prefs' not in st.session_state:
        st.session_state.show_unit_prefs = False
    
    # ========== TOP NAVIGATION BUTTONS ==========
    top_col1, top_col2, top_spacer = st.columns([1, 1, 2])
    
    with top_col1:
        if st.button("📋 Project Info" if not st.session_state.show_project_info else "📋 Hide Info", 
                     use_container_width=True, 
                     type="secondary",
                     key="toggle_project_info"):
            st.session_state.show_project_info = not st.session_state.show_project_info
            st.rerun()
    
    with top_col2:
        if st.button("⚙️ Units" if not st.session_state.show_unit_prefs else "⚙️ Hide", 
                     use_container_width=True,
                     type="secondary",
                     key="toggle_unit_prefs"):
            st.session_state.show_unit_prefs = not st.session_state.show_unit_prefs
            st.rerun()
    
    # ========== COLLAPSIBLE PROJECT INFORMATION ==========
    if st.session_state.show_project_info:
        with st.container():
            st.markdown("### 📋 Project Information")
            
            col_new, col_save = st.columns([1, 1])
            
            with col_new:
                if st.button("🆕 New", use_container_width=True, key="new_proj_btn"):
                    create_new_project()
            
            with col_save:
                if st.button("💾 Save", use_container_width=True, key="save_proj_btn"):
                    if save_current_project():
                        st.success("✅ Project saved successfully!")
                        time.sleep(1)
                        st.rerun()
            
            # Project number verification
            if st.session_state.current_project_id is None:
                next_num = get_next_project_number()
                st.session_state.current_project_number = next_num
                st.session_state.project_counter = next_num
                
                if st.session_state.projects:
                    existing_nums = [p['project_number'] for p in st.session_state.projects]
                    st.info(f"ℹ️ Existing projects: {sorted(existing_nums)} | Next: **{next_num}**")
                else:
                    st.info(f"ℹ️ No existing projects | Starting at: **{next_num}**")
            else:
                st.info(f"✏️ Editing Project #{st.session_state.current_project_id}")
            
            # Project info fields
            col1, col2 = st.columns([1, 1])
            
            with col1:
                project_number_display = st.text_input(
                    "Project Number",
                    value=str(st.session_state.current_project_number),
                    disabled=True,
                    key="project_number_display"
                )
                
                if 'project_name' not in st.session_state:
                    st.session_state.project_name = 'New Project'
                
                project_name = st.text_input(
                    "Project Name",
                    placeholder="Enter project name",
                    key="project_name"
                )
                
                if 'project_date' not in st.session_state:
                    st.session_state.project_date = datetime.now().date()
                
                st.text_input(
                    "Date",
                    value=st.session_state.project_date.strftime('%Y-%m-%d'),
                    disabled=True,
                    key="project_date_display"
                )
            
            with col2:
                if 'designer' not in st.session_state:
                    st.session_state.designer = 'Designer Name'
                if 'project_description' not in st.session_state:
                    st.session_state.project_description = 'Project description here'
                if 'contact_info' not in st.session_state:
                    st.session_state.contact_info = 'contact@email.com'
                
                designer = st.text_input(
                    "Designer",
                    placeholder="Enter designer name",
                    key="designer"
                )
                
                description = st.text_area(
                    "Description",
                    placeholder="Enter project description",
                    height=100,
                    key="project_description"
                )
                
                contact = st.text_input(
                    "Contact Info",
                    placeholder="Email or phone",
                    key="contact_info"
                )
        
        st.markdown("---")
    
    # ========== COLLAPSIBLE UNIT PREFERENCES ==========
    if st.session_state.show_unit_prefs:
        with st.container():
            st.markdown("### ⚙️ Unit Preferences")
            st.markdown("*Set default units for all calculations in this project*")
            
            # Initialize unit preferences with Imperial/English defaults
            if 'pref_dimension_unit' not in st.session_state:
                st.session_state.pref_dimension_unit = 'inches'
            if 'pref_weight_unit' not in st.session_state:
                st.session_state.pref_weight_unit = 'ounces'
            if 'pref_volume_unit' not in st.session_state:
                st.session_state.pref_volume_unit = 'cubic inches'
            
            pref_col1, pref_col2, pref_col3 = st.columns(3)
            
            with pref_col1:
                dimension_pref = st.selectbox(
                    "📏 Dimension Unit",
                    ['inches', 'feet', 'cm', 'mm'],
                    key="pref_dimension_unit",
                    help="Default unit for length/width/height measurements"
                )
            
            with pref_col2:
                weight_pref = st.selectbox(
                    "⚖️ Weight Unit",
                    ['ounces', 'pounds', 'grams', 'kilograms'],
                    key="pref_weight_unit",
                    help="Default unit for weight measurements"
                )
            
            with pref_col3:
                volume_pref = st.selectbox(
                    "📦 Volume Unit",
                    ['cubic inches', 'cubic feet', 'cubic cm', 'cubic mm'],
                    key="pref_volume_unit",
                    help="Default unit for volume display"
                )
        
        st.markdown("---")
    
    
    
    # SECTION 1: PRIMARY PRODUCT CALCULATOR
    if st.session_state.analyzer_section == 'primary':
        # Scroll to top of page
        st.markdown("""
        <script>
        window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
        """, unsafe_allow_html=True)
        
        # Auto-load saved primary data if available
        if 'saved_primary_data' in st.session_state and st.session_state.saved_primary_data:
            saved = st.session_state.saved_primary_data
            if 'product_weight' not in st.session_state or st.session_state.product_weight == 0.0:
                st.session_state.product_weight = saved.get('product_weight', 0.0)
            if 'product_quantity' not in st.session_state or st.session_state.product_quantity == 1:
                st.session_state.product_quantity = saved.get('product_quantity', 1)
            if 'primary_volume_mm3' not in st.session_state:
                st.session_state.primary_volume_mm3 = saved.get('primary_volume_mm3', 0)
            if 'total_product_volume_mm3' not in st.session_state:
                st.session_state.total_product_volume_mm3 = saved.get('total_product_volume_mm3', 0)
        
        st.markdown("## 🔬 Primary Product Volume Calculator")
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown("### Input")
            weight_unit = st.session_state.pref_weight_unit
            
            weight = st.number_input(
                f"Weight of Water ({weight_unit})",
                min_value=0.0,
                value=st.session_state.get('product_weight', 0.0),
                step=0.1,
                format="%.2f",
                help=f"Enter weight in {weight_unit}",
                key="product_weight"
            )
            st.info(f"ℹ️ Using **{weight_unit}** (set in Unit Preferences)")
            
            # Conversion Reference - Moved here, same width as input
            with st.expander("📐 Conversion Reference", expanded=False):
                st.markdown("""
                <div style="font-size: 0.85rem;">
                <strong>1 US Fluid Ounce =</strong><br>
                29,574 mm³ | 29.57 cm³ | 1.804 in³<br>
                <em style="font-size: 0.75rem; color: #64748b;">Water at 4°C (1 g/mL)</em>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Results")
            if weight > 0:
                dimension_unit = st.session_state.pref_dimension_unit
                result_unit = st.session_state.pref_volume_unit
                
                # Weight is already in session_state via key="product_weight"
                # Store the unit separately
                if 'product_weight_unit' not in st.session_state or st.session_state.product_weight_unit != weight_unit:
                    st.session_state.product_weight_unit = weight_unit
                
                weight_to_mm3 = {
                    'grams': 1000,
                    'ounces': 28316.8466,
                    'pounds': 453592.37,
                    'kilograms': 1000000
                }
                
                volume_mm3 = weight * weight_to_mm3[weight_unit]
                st.session_state.primary_volume_mm3 = volume_mm3
                
                mm3_to_display = {
                    'cubic mm': 1,
                    'cubic cm': 0.001,
                    'cubic inches': 0.000061023744,
                    'cubic feet': 0.000000035315
                }
                
                result_value = volume_mm3 * mm3_to_display[result_unit]
                
                st.markdown(f"""
                <div class="metric-card">
                    <div style="color: #60a5fa; font-weight: bold; font-size: 1.2rem;">{result_unit.title()}</div>
                    <div class="result-value">{result_value:.2f}</div>
                    <div class="result-unit">{result_unit}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.info(f"ℹ️ Displaying in **{result_unit}** (set in Unit Preferences)")
            else:
                # Show placeholder when no input
                st.markdown("""
                <div class="metric-card" style="opacity: 0.5;">
                    <div style="color: #64748b; font-weight: bold; font-size: 1.2rem;">Volume Result</div>
                    <div style="font-size: 3rem; font-weight: 700; color: #475569; margin: 16px 0;">--</div>
                    <div style="color: #64748b;">Enter weight to calculate</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Total Product Volume section
        if 'primary_volume_mm3' in st.session_state and st.session_state.primary_volume_mm3 > 0:
            st.markdown("---")
            st.markdown("### Total Product Volume")
            
            # New layout: Single Unit | Quantity | Total Volume (all in one row)
            total_col1, total_col2, total_col3 = st.columns([2, 1.5, 2])
            
            with total_col1:
                result_unit = st.session_state.pref_volume_unit
                mm3_to_display = {
                    'cubic mm': 1,
                    'cubic cm': 0.001,
                    'cubic inches': 0.000061023744,
                    'cubic feet': 0.000000035315
                }
                single_volume = st.session_state.primary_volume_mm3 * mm3_to_display[result_unit]
                
                # Compact inline display
                st.markdown(f"""
                <div style="padding: 12px; background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(167, 139, 250, 0.3); border-radius: 8px; height: 70px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="color: #a78bfa; font-size: 0.75rem; font-weight: 600; margin-bottom: 4px;">Single Unit</div>
                    <div style="font-size: 1.4rem; font-weight: bold; color: #a78bfa; font-family: 'JetBrains Mono', monospace;">
                        {single_volume:.2f} <span style="font-size: 0.9rem; opacity: 0.8;">{result_unit}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with total_col2:
                # Quantity input with label above
                st.markdown("""
                <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 600; margin-bottom: 4px;">
                    Quantity (max 999)
                </div>
                """, unsafe_allow_html=True)
                
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=999,
                    value=st.session_state.get('product_quantity', 1),
                    step=1,
                    key="product_quantity",
                    label_visibility="collapsed"
                )
            
            with total_col3:
                total_volume = single_volume * quantity
                total_volume_mm3 = st.session_state.primary_volume_mm3 * quantity
                st.session_state.total_product_volume_mm3 = total_volume_mm3
                
                # Compact inline display
                st.markdown(f"""
                <div style="padding: 12px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(248, 113, 113, 0.3); border-radius: 8px; height: 70px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="color: #f87171; font-size: 0.75rem; font-weight: 600; margin-bottom: 4px;">Total Volume (×{quantity})</div>
                    <div style="font-size: 1.4rem; font-weight: bold; color: #f87171; font-family: 'JetBrains Mono', monospace;">
                        {total_volume:.2f} <span style="font-size: 0.9rem; opacity: 0.8;">{result_unit}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Save Primary Data Button
            st.markdown("")  # Small spacing
            if st.button("💾 Save Primary Data", use_container_width=True, type="secondary", key="save_primary_data"):
                # Save all primary calculator data to session state persistence
                st.session_state.saved_primary_data = {
                    'product_weight': st.session_state.get('product_weight', 0.0),
                    'product_quantity': st.session_state.get('product_quantity', 1),
                    'primary_volume_mm3': st.session_state.get('primary_volume_mm3', 0),
                    'total_product_volume_mm3': st.session_state.get('total_product_volume_mm3', 0),
                    'pref_weight_unit': st.session_state.pref_weight_unit,
                    'pref_volume_unit': st.session_state.pref_volume_unit
                }
                st.success("✅ Primary data saved!")
                time.sleep(0.5)
                st.rerun()
        
        # Persistent Bottom Navigation - All 3 Sections
        st.markdown("---")
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        
        with nav_col1:
            st.button(
                "📊 Primary Calculator",
                use_container_width=True,
                disabled=True,  # Current section
                type="primary"
            )
        
        with nav_col2:
            if st.button("📦 Secondary Packaging", use_container_width=True, type="secondary", key="nav_to_secondary"):
                st.session_state.analyzer_section = 'secondary'
                st.rerun()
        
        with nav_col3:
            if st.button("📈 Volume Analysis", use_container_width=True, type="secondary", key="nav_to_analysis"):
                if 'box_volume_mm3' in st.session_state:
                    st.session_state.analyzer_section = 'analysis'
                    st.rerun()
                else:
                    st.warning("⚠️ Calculate box volume first")
    
    # SECTION 2: SECONDARY PACKAGING
    elif st.session_state.analyzer_section == 'secondary':
        # Scroll to top of page
        st.markdown("""
        <script>
        window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
        """, unsafe_allow_html=True)
        
        # Auto-load saved secondary data - ONLY ONCE per session entry
        if 'secondary_loaded_this_session' not in st.session_state:
            st.session_state.secondary_loaded_this_session = False
        
        if not st.session_state.secondary_loaded_this_session:
            loaded_from_storage = False
            
            # Priority 1: Load from saved_secondary_data in session state
            if 'saved_secondary_data' in st.session_state and st.session_state.saved_secondary_data:
                saved = st.session_state.saved_secondary_data
                if 'box_length' in saved and saved['box_length'] > 0:
                    st.session_state.box_length = saved['box_length']
                if 'box_width' in saved and saved['box_width'] > 0:
                    st.session_state.box_width = saved['box_width']
                if 'box_height' in saved and saved['box_height'] > 0:
                    st.session_state.box_height = saved['box_height']
                if 'box_volume_mm3' in saved:
                    st.session_state.box_volume_mm3 = saved['box_volume_mm3']
                loaded_from_storage = True
            
            # Priority 2: Try to load from persistent dva_secondary_data.json file
            if not loaded_from_storage and os.path.exists('dva_secondary_data.json'):
                try:
                    with open('dva_secondary_data.json', 'r') as f:
                        file_data = json.load(f)
                        if file_data.get('box_length', 0) > 0:
                            st.session_state.box_length = file_data.get('box_length', 0.0)
                            st.session_state.box_width = file_data.get('box_width', 0.0)
                            st.session_state.box_height = file_data.get('box_height', 0.0)
                            st.session_state.box_volume_mm3 = file_data.get('box_volume_mm3', 0)
                            st.session_state.saved_secondary_data = file_data
                            loaded_from_storage = True
                except Exception as e:
                    pass
            
            # Priority 3: Check dva_analysis_data.json as fallback
            if not loaded_from_storage and os.path.exists('dva_analysis_data.json'):
                try:
                    with open('dva_analysis_data.json', 'r') as f:
                        file_data = json.load(f)
                        if file_data.get('box_length', 0) > 0:
                            st.session_state.box_length = file_data.get('box_length', 0.0)
                            st.session_state.box_width = file_data.get('box_width', 0.0)
                            st.session_state.box_height = file_data.get('box_height', 0.0)
                            st.session_state.box_volume_mm3 = file_data.get('box_volume_mm3', 0)
                            if 'product_weight' in file_data:
                                st.session_state.product_weight = file_data.get('product_weight', 0.0)
                            if 'product_quantity' in file_data:
                                st.session_state.product_quantity = file_data.get('product_quantity', 1)
                            if 'primary_volume_mm3' in file_data:
                                st.session_state.primary_volume_mm3 = file_data.get('primary_volume_mm3', 0)
                            if 'total_product_volume_mm3' in file_data:
                                st.session_state.total_product_volume_mm3 = file_data.get('total_product_volume_mm3', 0)
                            loaded_from_storage = True
                except Exception as e:
                    pass
            
            # Mark as loaded for this session entry
            st.session_state.secondary_loaded_this_session = True
        
        st.markdown("## 📦 Secondary Packaging Calculator")
        
        st.markdown("### Box Dimensions Calculator")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Input Box Dimensions")
            dimension_unit = st.session_state.pref_dimension_unit
            st.info(f"ℹ️ All dimensions in **{dimension_unit}**")
            
            box_length = st.number_input(
                f"Length ({dimension_unit})",
                min_value=0.0,
                value=st.session_state.get('box_length', 0.0),
                step=0.1,
                format="%.2f",
                key="box_length"
            )
            
            box_width = st.number_input(
                f"Width ({dimension_unit})",
                min_value=0.0,
                value=st.session_state.get('box_width', 0.0),
                step=0.1,
                format="%.2f",
                key="box_width"
            )
            
            box_height = st.number_input(
                f"Height ({dimension_unit})",
                min_value=0.0,
                value=st.session_state.get('box_height', 0.0),
                step=0.1,
                format="%.2f",
                key="box_height"
            )
            
            if st.button("🧮 Calculate", use_container_width=True, type="primary"):
                if box_length > 0 and box_width > 0 and box_height > 0:
                    dim_to_mm = {
                        'mm': 1,
                        'cm': 10,
                        'inches': 25.4,
                        'feet': 304.8
                    }
                    
                    length_mm = box_length * dim_to_mm[dimension_unit]
                    width_mm = box_width * dim_to_mm[dimension_unit]
                    height_mm = box_height * dim_to_mm[dimension_unit]
                    
                    box_volume_mm3 = length_mm * width_mm * height_mm
                    st.session_state.box_volume_mm3 = box_volume_mm3
                    
                    # Prepare data to save (widget keys auto-save: box_length, box_width, box_height)
                    secondary_data = {
                        'box_length': box_length,
                        'box_width': box_width,
                        'box_height': box_height,
                        'box_volume_mm3': box_volume_mm3,
                        'pref_dimension_unit': st.session_state.pref_dimension_unit,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Save to session state for in-session persistence
                    st.session_state.saved_secondary_data = secondary_data
                    
                    # Save to persistent file
                    try:
                        with open('dva_secondary_data.json', 'w') as f:
                            json.dump(secondary_data, f, indent=2)
                        st.success("✅ Box volume calculated and saved to file!")
                    except Exception as e:
                        st.warning(f"⚠️ Calculated but file save failed: {e}")
                    
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("⚠️ Please enter all dimensions")
        
        with col2:
            st.markdown("#### 3D Box Preview")
            
            # Get current values - handle 0 properly
            curr_length = st.session_state.get('box_length', 0)
            curr_width = st.session_state.get('box_width', 0)
            curr_height = st.session_state.get('box_height', 0)
            
            if curr_length > 0 and curr_width > 0 and curr_height > 0:
                # Calculate efficiency if we have product volume
                if 'primary_volume_mm3' in st.session_state and st.session_state.primary_volume_mm3 > 0:
                    # Calculate box volume in mm3
                    dim_to_mm = {
                        'mm': 1,
                        'cm': 10,
                        'inches': 25.4,
                        'feet': 304.8
                    }
                    box_vol_mm3 = (curr_length * dim_to_mm[dimension_unit]) * \
                                 (curr_width * dim_to_mm[dimension_unit]) * \
                                 (curr_height * dim_to_mm[dimension_unit])
                    
                    product_vol_mm3 = st.session_state.get('total_product_volume_mm3', 
                                                           st.session_state['primary_volume_mm3'])
                    efficiency_pct = (product_vol_mm3 / box_vol_mm3 * 100) if box_vol_mm3 > 0 else 0
                else:
                    efficiency_pct = 50  # Default preview
                
                # Create 3D preview using the existing function
                preview_fig = create_3d_box_visualization(
                    curr_length,
                    curr_width,
                    curr_height,
                    efficiency_pct,
                    dimension_unit
                )
                
                # Match height to input section
                preview_fig.update_layout(height=400)
                st.plotly_chart(preview_fig, use_container_width=True, key="box_preview_3d")
            else:
                # Placeholder when no dimensions
                st.markdown("""
                <div style="height: 400px; display: flex; align-items: center; justify-content: center; 
                            background: rgba(15, 23, 42, 0.4); border-radius: 12px; border: 1px solid rgba(148, 163, 184, 0.2);">
                    <div style="text-align: center; color: #64748b;">
                        <div style="font-size: 3rem; margin-bottom: 16px;">📦</div>
                        <div style="font-size: 1.1rem;">Enter dimensions to see 3D preview</div>
                        <div style="font-size: 0.9rem; margin-top: 8px; opacity: 0.7;">Interactive • Rotate • Zoom</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Box Volume Results (below the preview)
        if 'box_volume_mm3' in st.session_state:
            st.markdown("---")
            st.markdown("### Box Volume Results")
            
            result_unit = st.session_state.pref_volume_unit
            mm3_to_result = {
                'cubic mm': 1,
                'cubic cm': 0.001,
                'cubic inches': 0.000061023744,
                'cubic feet': 0.000000035315
            }
            
            box_result = st.session_state.box_volume_mm3 * mm3_to_result[result_unit]
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="color: #10b981; font-weight: bold; font-size: 1.2rem;">Box Volume</div>
                <div class="result-value">{box_result:,.2f}</div>
                <div class="result-unit">{result_unit}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info(f"ℹ️ Results in **{result_unit}** (set in Unit Preferences)")
            
            if 'primary_volume_mm3' in st.session_state:
                st.markdown("---")
                st.markdown("#### Remaining Volume Analysis")
                
                product_volume_to_use = st.session_state.get('total_product_volume_mm3', 
                                                              st.session_state['primary_volume_mm3'])
                
                box_volume_mm3 = st.session_state['box_volume_mm3']
                remaining_volume_mm3 = box_volume_mm3 - product_volume_to_use
                
                remaining_unit = st.session_state.pref_volume_unit
                
                box_volume_result = box_volume_mm3 * mm3_to_result[remaining_unit]
                product_volume_result = product_volume_to_use * mm3_to_result[remaining_unit]
                remaining_volume_result = remaining_volume_mm3 * mm3_to_result[remaining_unit]
                
                quantity = st.session_state.get('product_quantity', 1)
                product_label = f"Product Volume (×{quantity})" if quantity > 1 else "Product Volume"
                
                vol_col1, vol_col2, vol_col3 = st.columns(3)
                
                with vol_col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #10b981; font-weight: bold;">Box Volume</div>
                        <div style="font-size: 1.8rem; font-weight: bold; color: #10b981; margin: 10px 0;">
                            {box_volume_result:,.2f}
                        </div>
                        <div class="result-unit">{remaining_unit}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with vol_col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #3b82f6; font-weight: bold;">{product_label}</div>
                        <div style="font-size: 1.8rem; font-weight: bold; color: #3b82f6; margin: 10px 0;">
                            {product_volume_result:,.2f}
                        </div>
                        <div class="result-unit">{remaining_unit}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with vol_col3:
                    remaining_color = "#10b981" if remaining_volume_result >= 0 else "#ef4444"
                    st.markdown(f"""
                    <div class="metric-card" style="border-color: {remaining_color};">
                        <div style="color: {remaining_color}; font-weight: bold;">Remaining Volume</div>
                        <div style="font-size: 1.8rem; font-weight: bold; color: {remaining_color}; margin: 10px 0;">
                            {remaining_volume_result:,.2f}
                        </div>
                        <div class="result-unit">{remaining_unit}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Persistent Bottom Navigation - All 3 Sections
        st.markdown("---")
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        
        with nav_col1:
            if st.button("📊 Primary Calculator", use_container_width=True, type="secondary", key="sec_to_primary"):
                st.session_state.analyzer_section = 'primary'
                st.session_state.secondary_loaded_this_session = False  # Reset flag
                st.rerun()
        
        with nav_col2:
            st.button(
                "📦 Secondary Packaging",
                use_container_width=True,
                disabled=True,  # Current section
                type="primary"
            )
        
        with nav_col3:
            if st.button("📈 Volume Analysis", use_container_width=True, type="secondary", key="sec_to_analysis"):
                if 'box_volume_mm3' in st.session_state:
                    st.session_state.analyzer_section = 'analysis'
                    st.session_state.secondary_loaded_this_session = False  # Reset flag
                    st.rerun()
                else:
                    st.warning("⚠️ Calculate box volume first")
    
    # SECTION 3: VOLUME ANALYSIS (FULL SCREEN VISUALIZATIONS!)
    elif st.session_state.analyzer_section == 'analysis':
        # Scroll to top of page
        st.markdown("""
        <script>
        window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
        """, unsafe_allow_html=True)
        
        # Auto-load saved analysis data if available (comprehensive restore)
        if 'saved_analysis_data' in st.session_state and st.session_state.saved_analysis_data:
            saved = st.session_state.saved_analysis_data
            # Restore all calculation data
            if 'primary_volume_mm3' not in st.session_state:
                st.session_state.primary_volume_mm3 = saved.get('primary_volume_mm3', 0)
            if 'box_volume_mm3' not in st.session_state:
                st.session_state.box_volume_mm3 = saved.get('box_volume_mm3', 0)
            if 'total_product_volume_mm3' not in st.session_state:
                st.session_state.total_product_volume_mm3 = saved.get('total_product_volume_mm3', 0)
            # Restore box dimensions (for Secondary recall)
            if 'box_length' not in st.session_state or st.session_state.box_length == 0.0:
                st.session_state.box_length = saved.get('box_length', 0.0)
            if 'box_width' not in st.session_state or st.session_state.box_width == 0.0:
                st.session_state.box_width = saved.get('box_width', 0.0)
            if 'box_height' not in st.session_state or st.session_state.box_height == 0.0:
                st.session_state.box_height = saved.get('box_height', 0.0)
            # Restore primary data (for Primary recall)
            if 'product_weight' not in st.session_state or st.session_state.product_weight == 0.0:
                st.session_state.product_weight = saved.get('product_weight', 0.0)
            if 'product_quantity' not in st.session_state or st.session_state.product_quantity == 1:
                st.session_state.product_quantity = saved.get('product_quantity', 1)
        # Also save current data when entering section (for auto-save)
        elif 'primary_volume_mm3' in st.session_state and 'box_volume_mm3' in st.session_state:
            st.session_state.saved_analysis_data = {
                'primary_volume_mm3': st.session_state.get('primary_volume_mm3', 0),
                'box_volume_mm3': st.session_state.get('box_volume_mm3', 0),
                'total_product_volume_mm3': st.session_state.get('total_product_volume_mm3', 0),
                'box_length': st.session_state.get('box_length', 0.0),
                'box_width': st.session_state.get('box_width', 0.0),
                'box_height': st.session_state.get('box_height', 0.0),
                'product_weight': st.session_state.get('product_weight', 0.0),
                'product_quantity': st.session_state.get('product_quantity', 1),
            }
        
        st.markdown("## 📊 Volume Efficiency Analysis")
        
        if 'primary_volume_mm3' not in st.session_state or 'box_volume_mm3' not in st.session_state:
            st.warning("⚠️ Please calculate primary volume and box volume first")
            
            if st.button("← Back to Primary", use_container_width=True):
                st.session_state.analyzer_section = 'primary'
                st.rerun()
        else:
            product_volume_to_use = st.session_state.get('total_product_volume_mm3', 
                                                          st.session_state['primary_volume_mm3'])
            box_volume_mm3 = st.session_state['box_volume_mm3']
            volume_efficiency_percentage = (product_volume_to_use / box_volume_mm3 * 100) if box_volume_mm3 > 0 else 0
            
            # ROW 1: Gauge and Donut (LARGE, Side by Side)
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                gauge_fig = create_efficiency_gauge(volume_efficiency_percentage)
                st.plotly_chart(gauge_fig, use_container_width=True, key="efficiency_gauge_fullscreen")
            
            with viz_col2:
                donut_fig = create_donut_chart(volume_efficiency_percentage)
                st.plotly_chart(donut_fig, use_container_width=True, key="space_donut_fullscreen")
            
            # ROW 2: Volume Comparison Bar (FULL WIDTH)
            st.markdown("### 📦 Volume Breakdown")
            
            remaining_unit = st.session_state.pref_volume_unit
            mm3_to_remaining = {
                'cubic mm': 1,
                'cubic cm': 0.001,
                'cubic inches': 0.000061023744,
                'cubic feet': 0.000000035315
            }
            
            comparison_fig = create_volume_comparison_chart(
                box_volume_mm3 * mm3_to_remaining[remaining_unit],
                product_volume_to_use * mm3_to_remaining[remaining_unit],
                remaining_unit
            )
            st.plotly_chart(comparison_fig, use_container_width=True, key="volume_comparison_fullscreen")
            
            # ROW 3: 3D Volume Preview (FULL WIDTH, LARGE)
            if all(k in st.session_state for k in ['box_length', 'box_width', 'box_height']):
                st.markdown("### 📊 3D Volume Preview")
                
                # Calculate product volume in display units
                product_vol_display = product_volume_to_use * mm3_to_remaining[remaining_unit]
                box_volume = st.session_state['box_length'] * st.session_state['box_width'] * st.session_state['box_height']
                
                # Create two columns: info panel (left) and 3D graphic (right)
                info_col, graphic_col = st.columns([1, 3], gap="large")
                
                with info_col:
                    # Floating info panel with all text information
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%); 
                                border-left: 4px solid #3b82f6; 
                                padding: 20px; 
                                border-radius: 10px;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                                margin-bottom: 20px;
                                position: relative;
                                z-index: 1;'>
                        <h4 style='color: #3b82f6; margin-top: 0;'>📦 SECONDARY PACKAGING</h4>
                        <p style='font-size: 18px; font-weight: bold; color: #3b82f6; margin: 5px 0;'>
                            {box_volume:.2f} {st.session_state.pref_dimension_unit}³
                        </p>
                        <p style='font-size: 14px; color: #94a3b8; margin: 5px 0;'>
                            {st.session_state['box_length']:.1f}" × {st.session_state['box_width']:.1f}" × {st.session_state['box_height']:.1f}"
                        </p>
                        <hr style='border: none; border-top: 1px solid rgba(148, 163, 184, 0.3); margin: 15px 0;'>
                        <h4 style='color: #10b981; margin-top: 0;'>🎁 PRIMARY PRODUCT</h4>
                        <p style='font-size: 18px; font-weight: bold; color: #10b981; margin: 5px 0;'>
                            {product_vol_display:.2f} {st.session_state.pref_dimension_unit}³
                        </p>
                        <p style='font-size: 14px; color: #94a3b8; margin: 5px 0;'>
                            Quantity: {st.session_state.get('product_quantity', 1)} units
                        </p>
                        <hr style='border: none; border-top: 1px solid rgba(148, 163, 184, 0.3); margin: 15px 0;'>
                        <h4 style='color: white; margin-top: 0;'>📊 EFFICIENCY</h4>
                        <p style='font-size: 28px; font-weight: bold; color: white; margin: 5px 0;'>
                            {volume_efficiency_percentage:.1f}%
                        </p>
                        <p style='font-size: 14px; color: #94a3b8; margin: 5px 0;'>
                            Volume Utilization
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with graphic_col:
                    # Add container for 3D graphic to prevent overlap
                    st.markdown('<div style="position: relative; z-index: 2;">', unsafe_allow_html=True)
                    # 3D graphic with ONLY measurement numbers
                    box_3d_fig = create_3d_volume_preview(
                        st.session_state['box_length'],
                        st.session_state['box_width'],
                        st.session_state['box_height'],
                        volume_efficiency_percentage,
                        st.session_state.pref_dimension_unit,
                        product_volume=product_vol_display,
                        product_weight=st.session_state.get('product_weight', None),
                        product_quantity=st.session_state.get('product_quantity', 1)
                    )
                    st.plotly_chart(box_3d_fig, use_container_width=True, key="box_3d_fullscreen")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            remaining_volume_result = (box_volume_mm3 - product_volume_to_use) * mm3_to_remaining[remaining_unit]
            
            if remaining_volume_result < 0:
                st.error("⚠️ Warning: Product volume exceeds box capacity!")
            else:
                st.success(f"✅ Box has sufficient space with {remaining_volume_result:,.2f} {remaining_unit} remaining")
            
            # Save Analysis Data Button
            st.markdown("")  # Small spacing
            if st.button("💾 Save Analysis Data", use_container_width=True, type="secondary", key="save_analysis_data"):
                # Save complete analysis data including box dimensions
                analysis_data = {
                    'primary_volume_mm3': st.session_state.get('primary_volume_mm3', 0),
                    'box_volume_mm3': st.session_state.get('box_volume_mm3', 0),
                    'total_product_volume_mm3': st.session_state.get('total_product_volume_mm3', 0),
                    'box_length': st.session_state.get('box_length', 0.0),
                    'box_width': st.session_state.get('box_width', 0.0),
                    'box_height': st.session_state.get('box_height', 0.0),
                    'product_weight': st.session_state.get('product_weight', 0.0),
                    'product_quantity': st.session_state.get('product_quantity', 1),
                    'volume_efficiency': volume_efficiency_percentage,
                    'pref_dimension_unit': st.session_state.pref_dimension_unit,
                    'pref_volume_unit': st.session_state.pref_volume_unit,
                    'pref_weight_unit': st.session_state.pref_weight_unit,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Save to session state
                st.session_state.saved_analysis_data = analysis_data
                
                # Save to persistent file
                try:
                    with open('dva_analysis_data.json', 'w') as f:
                        json.dump(analysis_data, f, indent=2)
                    st.success("✅ Analysis data saved to file and session!")
                except Exception as e:
                    st.warning(f"⚠️ Saved to session but file save failed: {e}")
                
                time.sleep(0.5)
                st.rerun()
            
            # Persistent Bottom Navigation - All 3 Sections
            st.markdown("---")
            nav_col1, nav_col2, nav_col3 = st.columns(3)
            
            with nav_col1:
                if st.button("📊 Primary Calculator", use_container_width=True, type="secondary", key="ana_to_primary"):
                    st.session_state.analyzer_section = 'primary'
                    st.rerun()
            
            with nav_col2:
                if st.button("📦 Secondary Packaging", use_container_width=True, type="secondary", key="ana_to_secondary"):
                    st.session_state.analyzer_section = 'secondary'
                    st.rerun()
            
            with nav_col3:
                st.button(
                    "📈 Volume Analysis",
                    use_container_width=True,
                    disabled=True,  # Current section
                    type="primary"
                )

# END OF SECTION NAVIGATION
# TAB 2: Project Results
with tab2:
    st.markdown("## Project Results")
    
    # Load Project button at top
    col_button1, col_button2 = st.columns([3, 1])
    
    with col_button2:
        delete_btn = st.button("🗑️ Delete Selected", use_container_width=True)
    
    if st.session_state.projects:
        st.markdown("---")
        st.markdown("### Project Summary Table")
        
        # Add CSS for larger font (20% increase) and properly sized checkboxes
        st.markdown("""
        <style>
        /* Larger font size (20% increase from default) */
        .stDataFrame table {
            border-color: rgba(148, 163, 184, 0.2) !important;
            font-size: 1.2rem !important; /* 20% larger */
        }
        .stDataFrame th {
            border-color: rgba(148, 163, 184, 0.15) !important;
            font-size: 1.2rem !important; /* 20% larger */
            font-weight: 600;
        }
        .stDataFrame td {
            border-color: rgba(148, 163, 184, 0.15) !important;
            font-size: 1.2rem !important; /* 20% larger */
            padding: 12px 8px !important; /* More padding for larger text */
        }
        /* Make checkboxes SMALLER to match form row height */
        div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stCheckbox"]) {
            display: flex;
            align-items: center;
            height: 52px; /* Match row height */
            padding: 0;
            margin: 0;
        }
        /* Smaller checkbox */
        div[data-testid="stCheckbox"] {
            display: flex;
            align-items: center;
            height: 52px;
            padding: 0;
            margin: 0;
        }
        div[data-testid="stCheckbox"] > label {
            margin: 0 !important;
            padding: 0 !important;
            display: flex;
            align-items: center;
            height: 100%;
        }
        /* Scale down checkbox size */
        div[data-testid="stCheckbox"] input[type="checkbox"] {
            transform: scale(0.8); /* Smaller checkbox */
            margin: 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize selected projects list in session state
        if 'selected_project_indices' not in st.session_state:
            st.session_state.selected_project_indices = []
        
        # Create columns for checkboxes and table
        col_select, col_table = st.columns([0.5, 9.5])
        
        with col_select:
            st.markdown("**Select**")
            # Create checkbox for each project
            for idx in range(len(st.session_state.projects)):
                # Check if this index is in selection
                is_checked = idx in st.session_state.selected_project_indices
                
                # Use unique key for each checkbox
                checkbox_key = f"select_project_{idx}"
                
                # Checkbox without value parameter - let Streamlit handle state
                checked = st.checkbox(
                    "",
                    key=checkbox_key,
                    label_visibility="collapsed"
                )
                
                # Update selection list based on checkbox state
                if checked and idx not in st.session_state.selected_project_indices:
                    st.session_state.selected_project_indices.append(idx)
                elif not checked and idx in st.session_state.selected_project_indices:
                    st.session_state.selected_project_indices.remove(idx)
        
        with col_table:
            # Display project info as table with optimized column widths
            display_df = []
            for project in st.session_state.projects:
                display_df.append({
                    'Project #': project['project_number'],
                    'Project Name': project['project_name'],
                    'Designer': project['designer'],
                    'Description': project['description'][:50] + '...' if len(project['description']) > 50 else project['description'],
                    'Date': project['date']
                })
            
            # Display with column configuration for optimized widths
            st.dataframe(
                display_df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Project #": st.column_config.NumberColumn(
                        "Project #",
                        width=80,  # Fixed pixel width to fit project number
                    ),
                    "Project Name": st.column_config.TextColumn(
                        "Project Name",
                        width="medium",
                    ),
                    "Designer": st.column_config.TextColumn(
                        "Designer",
                        width="small",
                    ),
                    "Description": st.column_config.TextColumn(
                        "Description",
                        width="large",
                    ),
                    "Date": st.column_config.TextColumn(
                        "Date",
                        width="small",
                    ),
                }
            )
        
        # Show how many projects are selected
        if st.session_state.selected_project_indices:
            st.info(f"📌 {len(st.session_state.selected_project_indices)} project(s) selected")
        
        st.markdown("---")
        
        # Add to overview button (right justified)
        col_add1, col_add2 = st.columns([3, 1])
        
        with col_add2:
            if st.button("➕ Add Selected to Overview", use_container_width=True):
                if st.session_state.selected_project_indices:
                    # Add all selected projects to overview
                    if 'loaded_projects_overview' not in st.session_state:
                        st.session_state.loaded_projects_overview = []
                    
                    added_count = 0
                    for idx in st.session_state.selected_project_indices:
                        project = st.session_state.projects[idx]
                        if not any(p['project_number'] == project['project_number'] for p in st.session_state.loaded_projects_overview):
                            st.session_state.loaded_projects_overview.append(project)
                            added_count += 1
                    
                    if added_count > 0:
                        st.success(f"Added {added_count} project(s) to overview")
                        st.rerun()
                    else:
                        st.info("All selected projects are already in overview")
                else:
                    st.warning("⚠️ Please select at least one project")
        
        # Handle Delete button
        if delete_btn:
            if st.session_state.selected_project_indices:
                # Sort in reverse to delete from end first (avoid index shifting)
                for idx in sorted(st.session_state.selected_project_indices, reverse=True):
                    deleted_project = st.session_state.projects[idx]
                    st.session_state.projects.pop(idx)
                    st.success(f"✅ Deleted project {deleted_project['project_number']}")
                
                save_projects()
                st.session_state.selected_project_indices = []  # Clear selection
                time.sleep(1)
                st.rerun()
            else:
                st.warning("⚠️ Please select at least one project to delete")
        
        # Project Overview Section
        st.markdown("---")
        
        # Header with Output Report button
        col_header, col_button = st.columns([3, 1])
        
        with col_header:
            st.markdown("## Project Overview")
            st.markdown("### Detailed Project Information")
        
        with col_button:
            if st.button("📄 Output Report", use_container_width=True, type="primary"):
                if st.session_state.loaded_projects_overview:
                    # Generate PDF report
                    try:
                        from reportlab.lib.pagesizes import letter
                        from reportlab.lib import colors
                        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                        from reportlab.lib.units import inch
                        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
                        from reportlab.lib.enums import TA_CENTER, TA_LEFT
                        from io import BytesIO
                        
                        # Create PDF in memory
                        buffer = BytesIO()
                        doc = SimpleDocTemplate(buffer, pagesize=letter)
                        elements = []
                        styles = getSampleStyleSheet()
                        
                        # Custom styles
                        title_style = ParagraphStyle(
                            'CustomTitle',
                            parent=styles['Heading1'],
                            fontSize=24,
                            textColor=colors.HexColor('#2196f3'),
                            spaceAfter=30,
                            alignment=TA_CENTER
                        )
                        
                        heading_style = ParagraphStyle(
                            'CustomHeading',
                            parent=styles['Heading2'],
                            fontSize=16,
                            textColor=colors.HexColor('#1976d2'),
                            spaceAfter=12
                        )
                        
                        # Title
                        elements.append(Paragraph("Displacement Volume Analyzer", title_style))
                        elements.append(Paragraph("Project Analysis Report", styles['Heading2']))
                        elements.append(Spacer(1, 0.3*inch))
                        
                        # Report info
                        report_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
                        elements.append(Paragraph(f"Report Generated: {report_date}", styles['Normal']))
                        elements.append(Paragraph(f"Total Projects: {len(st.session_state.loaded_projects_overview)}", styles['Normal']))
                        elements.append(Spacer(1, 0.3*inch))
                        
                        # Individual project details
                        for idx, project in enumerate(st.session_state.loaded_projects_overview):
                            if idx > 0:
                                elements.append(PageBreak())
                            
                            # Project header
                            elements.append(Paragraph(f"Project {project['project_number']}: {project['project_name']}", heading_style))
                            elements.append(Spacer(1, 0.2*inch))
                            
                            # Project information table
                            proj_data = [
                                ['Project Number:', str(project['project_number'])],
                                ['Project Name:', project['project_name']],
                                ['Designer:', project['designer']],
                                ['Date:', project['date']],
                                ['Contact:', project['contact']],
                                ['Description:', project['description']]
                            ]
                            
                            proj_table = Table(proj_data, colWidths=[2*inch, 4.5*inch])
                            proj_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
                                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ]))
                            elements.append(proj_table)
                            elements.append(Spacer(1, 0.3*inch))
                            
                            # Calculation results
                            elements.append(Paragraph("Primary Product Volume", heading_style))
                            results = calculate_volume(project['weight'], project['weight_unit'])
                            
                            calc_data = [
                                ['Weight:', f"{project['weight']} {project['weight_unit']}"],
                                ['Volume (mm³):', f"{results['mm³']:,.2f} mm³"],
                                ['Volume (cm³):', f"{results['cm³']:,.2f} cm³"],
                                ['Volume (in³):', f"{results['in³']:,.3f} in³"]
                            ]
                            
                            calc_table = Table(calc_data, colWidths=[2*inch, 4.5*inch])
                            calc_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
                                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ]))
                            elements.append(calc_table)
                            elements.append(Spacer(1, 0.3*inch))
                            
                            # Box volume if available
                            if project.get('box_volume_mm3', 0) > 0:
                                elements.append(Paragraph("Secondary Packaging", heading_style))
                                
                                box_data = [
                                    ['Dimensions:', f"{project['box_length']} × {project['box_width']} × {project['box_height']} {project['dimension_unit']}"],
                                    ['Box Volume:', f"{project['box_volume_mm3']:,.2f} mm³"],
                                    ['Product Volume:', f"{project['primary_volume_mm3']:,.2f} mm³"],
                                ]
                                
                                # Calculate remaining and efficiency
                                remaining_mm3 = project['box_volume_mm3'] - project['primary_volume_mm3']
                                efficiency_pct = (project['primary_volume_mm3'] / project['box_volume_mm3']) * 100 if project['box_volume_mm3'] > 0 else 0
                                remaining_pct = (remaining_mm3 / project['box_volume_mm3']) * 100 if project['box_volume_mm3'] > 0 else 0
                                
                                box_data.extend([
                                    ['Remaining Volume:', f"{remaining_mm3:,.2f} mm³"],
                                    ['Volume Efficiency:', f"{efficiency_pct:.1f}%"],
                                    ['Remaining Space:', f"{remaining_pct:.1f}%"],
                                ])
                                
                                box_table = Table(box_data, colWidths=[2*inch, 4.5*inch])
                                box_table.setStyle(TableStyle([
                                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3e0')),
                                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                ]))
                                elements.append(box_table)
                        
                        # Comparison section if multiple projects
                        if len(st.session_state.loaded_projects_overview) > 1:
                            projects_with_boxes = [p for p in st.session_state.loaded_projects_overview if p.get('box_volume_mm3', 0) > 0]
                            
                            if projects_with_boxes:
                                elements.append(PageBreak())
                                elements.append(Paragraph("Volume Comparison Summary", heading_style))
                                elements.append(Spacer(1, 0.2*inch))
                                
                                # Comparison table
                                comp_data = [['Project', 'Box Volume\n(cm³)', 'Product Volume\n(cm³)', 'Remaining\n(cm³)', 'Efficiency\n(%)']]
                                
                                for project in projects_with_boxes:
                                    box_cm3 = project['box_volume_mm3'] * 0.001
                                    prod_cm3 = project['primary_volume_mm3'] * 0.001
                                    remaining_cm3 = (project['box_volume_mm3'] - project['primary_volume_mm3']) * 0.001
                                    efficiency = (project['primary_volume_mm3'] / project['box_volume_mm3']) * 100 if project['box_volume_mm3'] > 0 else 0
                                    
                                    comp_data.append([
                                        project['project_name'],
                                        f"{box_cm3:,.2f}",
                                        f"{prod_cm3:,.2f}",
                                        f"{remaining_cm3:,.2f}",
                                        f"{efficiency:.1f}%"
                                    ])
                                
                                comp_table = Table(comp_data, colWidths=[2*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch])
                                comp_table.setStyle(TableStyle([
                                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196f3')),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
                                ]))
                                elements.append(comp_table)
                        
                        # Build PDF
                        doc.build(elements)
                        
                        # Prepare for download
                        buffer.seek(0)
                        pdf_bytes = buffer.getvalue()
                        
                        # Create download button
                        filename = f"DVA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        st.download_button(
                            label="⬇️ Download PDF Report",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        st.success("✅ PDF report generated successfully!")
                        
                    except ImportError:
                        st.error("❌ PDF generation requires the 'reportlab' library. Please install it: pip install reportlab")
                    except Exception as e:
                        st.error(f"❌ Error generating PDF: {str(e)}")
                else:
                    st.warning("⚠️ No projects in overview. Add projects to generate a report.")
        
        # Initialize overview list
        if 'loaded_projects_overview' not in st.session_state:
            st.session_state.loaded_projects_overview = []
        
        # Display all loaded projects in overview
        if st.session_state.loaded_projects_overview:
            st.info(f"📊 Showing {len(st.session_state.loaded_projects_overview)} project(s) in overview")
            
            # Show quick summary list
            st.markdown("**Projects in Overview:**")
            project_list = ", ".join([f"**{p['project_name']}** (#{p['project_number']})" for p in st.session_state.loaded_projects_overview])
            st.markdown(project_list)
            st.markdown("---")
            
            for idx, project in enumerate(st.session_state.loaded_projects_overview):
                with st.expander(f"📋 Project {project['project_number']} - {project['project_name']}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Project Information")
                        st.info(f"""
                        **Project Number:** {project['project_number']}  
                        **Project Name:** {project['project_name']}  
                        **Designer:** {project['designer']}  
                        **Date:** {project['date']}  
                        **Contact:** {project['contact']}  
                        **Description:** {project['description']}
                        """)
                    
                    with col2:
                        st.markdown("#### Calculation Results")
                        
                        # Primary product volume
                        results = calculate_volume(project['weight'], project['weight_unit'])
                        
                        st.success(f"""
                        **Primary Product:**  
                        Weight: {project['weight']} {project['weight_unit']}  
                        
                        **Volumes:**  
                        • {results['mm³']:,.2f} mm³  
                        • {results['cm³']:,.2f} cm³  
                        • {results['in³']:,.3f} in³
                        """)
                        
                        # Box volume if available
                        if project.get('box_volume_mm3', 0) > 0:
                            st.info(f"""
                            **Secondary Packaging:**  
                            Dimensions: {project['box_length']} × {project['box_width']} × {project['box_height']} {project['dimension_unit']}  
                            Box Volume: {project['box_volume_mm3']:,.2f} mm³
                            """)
                    
                    # Remove button for this project
                    if st.button(f"Remove from Overview", key=f"remove_overview_{idx}"):
                        st.session_state.loaded_projects_overview.pop(idx)
                        st.rerun()
            
            # Clear all button
            if st.button("🗑️ Clear All from Overview"):
                st.session_state.loaded_projects_overview = []
                st.rerun()
            
            # Comparison Section - Remaining Volume Analysis
            st.markdown("---")
            st.markdown("## 📊 Remaining Volume Comparison")
            
            # Filter projects that have box volume data
            projects_with_boxes = [p for p in st.session_state.loaded_projects_overview if p.get('box_volume_mm3', 0) > 0]
            
            if projects_with_boxes:
                # Use global unit preference instead of dropdown
                comparison_unit = st.session_state.pref_volume_unit
                st.info(f"ℹ️ Using **{comparison_unit}** (set in Unit Preferences)")
                
                # Conversion factors from mm³
                mm3_to_unit = {
                    "cubic mm": 1,
                    "cubic cm": 0.001,
                    "cubic inches": 0.000061023744,
                    "cubic feet": 0.000000035315
                }
                
                conversion_factor = mm3_to_unit[comparison_unit]
                
                # Display each project with all data in compact format
                for project in projects_with_boxes:
                    box_volume_mm3 = project.get('box_volume_mm3', 0)
                    # Use total product volume (with quantity) if available, otherwise primary
                    product_volume_mm3 = project.get('total_product_volume_mm3', project.get('primary_volume_mm3', 0))
                    remaining_volume_mm3 = box_volume_mm3 - product_volume_mm3
                    
                    # Convert to selected unit
                    box_volume = box_volume_mm3 * conversion_factor
                    product_volume = product_volume_mm3 * conversion_factor
                    remaining_volume = remaining_volume_mm3 * conversion_factor
                    
                    # Calculate percentage
                    if box_volume_mm3 > 0:
                        percentage_remaining = (remaining_volume_mm3 / box_volume_mm3) * 100
                        percentage_used = (product_volume_mm3 / box_volume_mm3) * 100
                    else:
                        percentage_remaining = 0
                        percentage_used = 0
                    
                    # Display project card with all info
                    with st.container():
                        # Determine efficiency level
                        if percentage_used >= 85:
                            eff_label = "Excellent"
                        elif percentage_used >= 75:
                            eff_label = "Good"
                        elif percentage_used >= 60:
                            eff_label = "Fair"
                        else:
                            eff_label = "Poor"
                        
                        # Show quantity and efficiency in header
                        quantity_info = f" (Qty: {project.get('product_quantity', 1)})" if project.get('product_quantity', 1) > 1 else ""
                        efficiency_info = f" - {percentage_used:.1f}% {eff_label}"
                        st.markdown(f"### 📦 {project['project_name']} (Project #{project['project_number']}){quantity_info}{efficiency_info}")
                        
                        # Row 1: Volume metrics
                        vol_col1, vol_col2, vol_col3 = st.columns(3)
                        
                        with vol_col1:
                            st.metric("Box Volume", f"{box_volume:,.2f}", delta=None)
                            st.caption(comparison_unit)
                        
                        with vol_col2:
                            st.metric("Product Volume", f"{product_volume:,.2f}", delta=f"{percentage_used:.1f}% used")
                            st.caption(comparison_unit)
                        
                        with vol_col3:
                            st.metric("Remaining Volume", f"{remaining_volume:,.2f}", 
                                     delta=f"{percentage_remaining:.1f}% free" if remaining_volume >= 0 else "Overflow!")
                            st.caption(comparison_unit)
                        
                        # Volume Breakdown Bar Chart (removed efficiency bar above)
                        st.markdown("#### Volume Breakdown")
                        st.caption("Goal: Maximize product volume, minimize empty space")
                        breakdown_fig = create_volume_breakdown_bar(product_volume, remaining_volume, comparison_unit)
                        st.plotly_chart(breakdown_fig, use_container_width=True, key=f"breakdown_bar_{project['project_number']}")
                        
                        st.markdown("---")
            else:
                st.info("💡 No projects with box volume data in overview. Add projects with complete calculations to see comparison.")
        else:
            st.info("📋 No projects in overview. Click 'Add Selected to Overview' to analyze projects.")
    
    else:
        st.info("📋 No projects saved yet. Create a project in the Calculator tab!")

# TAB 3: Primary Results
with tab3:
    st.markdown("## Primary Results - Batch Conversion Results")
    
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
        st.warning("No samples available. Add samples in the Primary Data tab.")

# TAB 4: Primary Data
with tab4:
    st.markdown("## Primary Data Manager")
    
    # CSV Upload Section
    st.markdown("### 📤 Import Data from CSV")
    st.info("Upload a CSV file with columns: Sample ID, Weight, Unit")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            import pandas as pd
            df = pd.read_csv(uploaded_file)
            
            # Expected column names (case-insensitive)
            expected_cols = ['sample id', 'weight', 'unit']
            df.columns = df.columns.str.lower().str.strip()
            
            # Validate columns
            if all(col in df.columns for col in expected_cols):
                st.success(f"✅ CSV file loaded successfully! Found {len(df)} samples.")
                
                # Preview data
                st.markdown("**Preview:**")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("📥 Import These Samples", use_container_width=True):
                    imported_count = 0
                    skipped_count = 0
                    
                    for _, row in df.iterrows():
                        sample_id = str(row['sample id']).strip()
                        
                        # Skip if ID already exists
                        if any(s['id'] == sample_id for s in st.session_state.samples):
                            skipped_count += 1
                            continue
                        
                        # Validate unit
                        unit = str(row['unit']).lower().strip()
                        if unit not in ['grams', 'ounces', 'pounds', 'kilograms']:
                            skipped_count += 1
                            continue
                        
                        try:
                            weight = float(row['weight'])
                            st.session_state.samples.append({
                                'id': sample_id,
                                'weight': weight,
                                'unit': unit
                            })
                            imported_count += 1
                        except (ValueError, TypeError):
                            skipped_count += 1
                            continue
                    
                    save_data(st.session_state.samples)
                    st.success(f"✅ Imported {imported_count} samples! Skipped {skipped_count} (duplicates or invalid data).")
                    time.sleep(1.5)
                    st.rerun()
            else:
                st.error(f"❌ Invalid CSV format. Expected columns: 'Sample ID', 'Weight', 'Unit'. Found: {', '.join(df.columns)}")
                st.info("Please ensure your CSV has these exact column headers (case-insensitive).")
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
    
    st.markdown("---")
    
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
<div style='text-align: left; color: #90caf9; padding: 10px; line-height: 1.2;'>
    <p style='margin: 0 0 4px 0;'><strong>Displacement Volume Analyzer v1.0</strong></p>
    <p style='margin: 0 0 4px 0;'>Developed by <strong>Yuttana Chiaravalloti</strong>. All rights reserved.</p>
    <p style='margin: 0;'>Built with precision using Python and Streamlit | Where science meets simplicity 🔬</p>
</div>
""", unsafe_allow_html=True)
