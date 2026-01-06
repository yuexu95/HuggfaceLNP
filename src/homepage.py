"""

This is the main page, that you have to run with "streamlit run" to launch the app locally.
Streamlit automatically create the tabs in the left sidebar from the .py files located in /pages
Here we just have the home page, with a short description of the tabs, and some images

"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

st.set_page_config(
    page_title="Home page",
    page_icon="👋",
    layout="centered")


# Main Description
st.title("👋 LNP Formulation Calculator")
st.markdown("**Comprehensive toolkit for lipid nanoparticle (LNP) formulation design, calculation, and optimization.**")
st.markdown("From basic calculations to high-throughput DOE screening — streamline your LNP workflows for pDNA, mRNA, and complex multi-component systems.")
st.markdown("Developed by **Yue Xu**, YongLi Lab @ BCM — more at https://yuexu95.github.io/")
st.markdown("Have feedback or feature requests? Email: **yue.xu@bcm.edu**.")
st.markdown("---")

# Description of the features. 
with st.container():
    st.markdown("""
    ### 📑 Explore the Tools
    
    Navigate through the sidebar to access different modules:

    #### 🔬 **General Info**
    Overview of LNP fundamentals, formulation concepts, and calculation principles for both pDNA and mRNA.

    #### 🧬 **LNP Formulation Calculator**
    Standard calculator for pDNA and mRNA formulations with N/P ratio calculations, detailed volume breakdowns, and batch scaling.

    #### 💊 **FDA-Approved Formulations**
    Pre-configured formulations based on FDA-approved LNP products (Onpattro®, Comirnaty®, Spikevax®, etc.) for reference and replication.

    #### 🀄 **LNP-Flow: Professional DOE Designer**
    High-throughput Design of Experiments (DOE) tool for systematic LNP optimization:
    - Multi-factor screening (lipid ratios, N/P, flow rates, etc.)
    - Full factorial and fractional designs
    - Lab-ready run sheets with randomization
    - Batch generation for 96-well formats

    #### 📚 **References**
    Key literature, protocols, and resources for LNP formulation knowledge.

    #### ⚗️ **5th Component Calculator**
    Advanced calculator for LNP formulations with an additional lipid or functional component beyond the standard 4-component system.

    #### 🔬 **Multi-step LNP with DNA-Binding Compounds**
    Specialized calculator for pre-complexing DNA with binding compounds (protamine, peptides, polymers) before LNP formation.
    """)             




st.markdown(
    """
    ### ✨ Key Features
    
    - **🎯 N/P Ratio Calculations**: Automatic nitrogen-to-phosphate ratio computation for quality control
    - **📊 Dual Input Modes**: Switch between mass ratio and N/P ratio inputs
    - **⚗️ Bulk Volume Generation**: Auto-scaled master mixes with overage (ethanol ×1.5, aqueous ×1.2)
    - **📈 Batch Scaling**: Generate multi-batch protocols for high-throughput experiments
    - **📁 History & Export**: Save calculation history and download CSV files for record-keeping
    - **🔄 Real-time Validation**: Instant feedback on formulation parameters and ratios
    - **🧪 Pre-configured Templates**: FDA-approved formulations and common research protocols
    - **🀄 DOE Integration**: Professional Design of Experiments for systematic optimization


    ### 🚀 Getting Started
    
    1. Start with **General Info** to understand LNP basics
    2. Use the **LNP Formulation Calculator** for your first formulation
    3. Explore **FDA-Approved Formulations** for validated protocols
    4. Scale up with **LNP-Flow DOE Designer** for optimization studies

    ### 💡 Tips
    
    - All calculators include tooltips (ℹ️) for parameter guidance
    - Export your data regularly for lab notebook integration
    - Check N/P ratios against literature benchmarks (typically 3-20)
    - Use the DOE tool for systematic multi-parameter optimization

    ---
    
    ### 🎉 Enjoy the app!
    
    *Version 2.0 | Last updated: January 2026*
    """
)

