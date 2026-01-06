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
st.markdown("Designed for quick, accurate lipid nanoparticle (LNP) formulation workflows for pDNA and mRNA.")
st.markdown("Developed by **Yue Xu**, YongLi Lab @ BCM — more at https://yuexu95.github.io/")
st.markdown("Have feedback or feature requests? Email: **yue.xu@bcm.edu**.")
st.markdown("---")
# Description of the features. 
with st.container():
    st.markdown("""
    ### Explore in the left sidebar

    - **General info**: Overview of LNP formulation concepts and calculation principles.
    - **pDNA Formulation**: Calculator for plasmid DNA, with N/P ratio and detailed volumes.
    - **mRNA Formulation**: Calculator for mRNA, mirroring the pDNA workflow and outputs.
    - **Formulation Optimization**: Design and optimize LNP formulations based on desired properties.
    - **References**: Key literature and resources for LNP formulation knowledge.
    """)             




st.markdown(
    """
    ### Key features
    - **N/P ratio metrics** for quick quality checks.
    - **Bulk volumes**: auto-summed master mixes (ethanol ×1.5, aqueous ×1.2) and totals for multi-batch prep.
    - **History & export**: each run saved; download CSV for record-keeping.


    ### Enjoy the app!
    """
)

