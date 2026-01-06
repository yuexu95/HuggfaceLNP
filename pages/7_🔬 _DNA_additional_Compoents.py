import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("🔬 Multi-step LNP Formulation with DNA-Binding Compound")

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.info("💡 Design LNP formulations where a custom compound (peptide, protein, polymer, etc.) is pre-complexed with DNA before mixing with lipid components. Adjust molecular weight and ratio for your specific compound.")

# Initialize session state
if "compound_results" not in st.session_state:
    st.session_state.compound_results = None
if "compound_history" not in st.session_state:
    st.session_state.compound_history = []

# ========== Preset Compounds ==========
st.subheader("⚡ Quick Preset Selection")

# Define preset compounds with their properties
preset_compounds = {
    "Custom": {"mw": 500.0, "conc": 10.0, "solvent": "Water"},
    "Protamine Sulfate (Full)": {"mw": 4150.0, "conc": 10.0, "solvent": "Water", "info": "MW ≈ 4.15 kDa, 49 amino acids, typical stock 10-50 mg/ml"},
    "Low Molecular Weight Protamine (LMWP)": {"mw": 1880.18, "conc": 10.0, "solvent": "Water", "info": "MW = 1880.18 Da, 14 amino acids, CPP, solubility ≥100 mg/ml"},
    "Poly-L-Lysine (PLL) 10kDa": {"mw": 10000.0, "conc": 10.0, "solvent": "Water", "info": "Common DNA binding polymer, typical stock 10-50 mg/ml"},
    "Poly-L-Arginine 5kDa": {"mw": 5000.0, "conc": 10.0, "solvent": "Water", "info": "Positively charged polymer, typical stock 10-50 mg/ml"},
    "Histone H1": {"mw": 21000.0, "conc": 10.0, "solvent": "Water", "info": "DNA-binding protein, typical stock 5-20 mg/ml"},
    "Spermidine": {"mw": 145.24, "conc": 100.0, "solvent": "Water", "info": "Small DNA condensing agent, very soluble"},
    "Spermine": {"mw": 202.34, "conc": 100.0, "solvent": "Water", "info": "Polyamine DNA condensing agent, very soluble"},
}

col_preset1, col_preset2 = st.columns([3, 1])
with col_preset1:
    preset_select = st.selectbox(
        "Select a Preset Compound",
        list(preset_compounds.keys()),
        key="preset_compound",
        help="Choose from common DNA-binding compounds or select 'Custom' to enter your own values"
    )
with col_preset2:
    if preset_select in preset_compounds:
        preset_data = preset_compounds[preset_select]
        if "info" in preset_data:
            st.caption(f"📝 {preset_data['info']}")

# Auto-apply preset values when selected
preset_data = preset_compounds[preset_select]

# Check if preset changed and update session state values
if "last_preset_select" not in st.session_state:
    st.session_state.last_preset_select = preset_select
    # Initialize with default values
    st.session_state.compound_name = preset_select if preset_select != "Custom" else "Custom Compound"
    st.session_state.compound_mw = preset_data["mw"]
    st.session_state.compound_stock_conc = preset_data["conc"]
    st.session_state.compound_solvent = preset_data["solvent"]

if st.session_state.last_preset_select != preset_select:
    # Preset changed, update the widget values in session state
    st.session_state.compound_name = preset_select if preset_select != "Custom" else "Custom Compound"
    st.session_state.compound_mw = preset_data["mw"]
    st.session_state.compound_stock_conc = preset_data["conc"]
    st.session_state.compound_solvent = preset_data["solvent"]
    st.session_state.last_preset_select = preset_select
    st.rerun()

# ========== Step 1: DNA-Compound Complex Formation ==========
st.subheader("📋 Step 1: DNA-Compound Complex Formation")
st.markdown("**Protocol:** Mix DNA solution with your compound at specified w/w ratio, incubate at room temperature")

col_p1, col_p2, col_p3, col_p4 = st.columns(4)
with col_p1:
    comp_exp_name = st.text_input(
        "Experiment Name",
        value="",
        placeholder="e.g., Peptide-DNA-LNP",
        key="comp_exp_name"
    )
with col_p2:
    comp_dna_amount = st.number_input(
        "DNA Amount (μg)",
        min_value=1.0,
        step=1.0,
        value=10.0,
        key="comp_dna_amount",
        help="Total DNA used per LNP batch"
    )
with col_p3:
    comp_dna_stock = st.number_input(
        "DNA Stock (μg/μL)",
        min_value=0.1,
        step=0.1,
        value=1.0,
        key="comp_dna_stock"
    )
with col_p4:
    comp_dna_buffer = st.selectbox(
        "DNA Buffer",
        ["TE", "PBS", "Citrate", "Water"],
        key="comp_dna_buffer"
    )

# Custom compound parameters
st.markdown("**Custom DNA-Binding Compound Parameters**")
col_p5, col_p6, col_p7, col_p8 = st.columns(4)
with col_p5:
    compound_name = st.text_input(
        "Compound Name",
        placeholder="e.g., Protamine, Peptide, Polymer",
        key="compound_name"
    )
with col_p6:
    compound_mw = st.number_input(
        "Compound Molecular Weight (Da)",
        min_value=50.0,
        step=50.0,
        key="compound_mw",
        help="Molecular weight of your compound in Daltons (Da)"
    )
with col_p7:
    compound_stock_conc = st.number_input(
        "Compound Stock (mg/ml)",
        min_value=0.1,
        step=0.5,
        key="compound_stock_conc",
        help="Stock concentration of your compound (mg/ml = μg/μL)"
    )
with col_p8:
    solvent_options = ["Water", "PBS", "Ethanol", "DMSO", "Other"]
    compound_solvent = st.selectbox(
        "Compound Solvent",
        solvent_options,
        key="compound_solvent"
    )

col_p9, col_p10, col_p11 = st.columns(3)
with col_p9:
    compound_w_w_ratio = st.number_input(
        f"{compound_name}:DNA w/w Ratio",
        min_value=0.1,
        step=0.1,
        value=1.0,
        key="compound_w_w_ratio",
        help="Weight ratio of compound to DNA"
    )
with col_p10:
    compound_incubation = st.number_input(
        "Incubation Time (min)",
        min_value=1,
        step=1,
        value=10,
        key="compound_incubation",
        help="Complex formation incubation time"
    )
with col_p11:
    compound_temp = st.selectbox(
        "Incubation Temperature",
        ["Room Temperature (RT)", "4°C", "37°C", "Custom"],
        key="compound_temp"
    )

# Calculate DNA-Compound complex
comp_dna_volume = comp_dna_amount / comp_dna_stock
compound_amount = comp_dna_amount * compound_w_w_ratio
compound_volume = compound_amount / compound_stock_conc
comp_dna_complex_volume = comp_dna_volume + compound_volume

with st.expander("📊 DNA-Compound Complex Summary"):
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("DNA Volume", f"{comp_dna_volume:.2f} μL")
        st.metric(f"{compound_name} Amount", f"{compound_amount:.2f} μg")
        st.metric(f"{compound_name} Volume", f"{compound_volume:.2f} μL")
    with col_s2:
        st.metric("Total Complex Volume", f"{comp_dna_complex_volume:.2f} μL")
        # Calculate molar ratio
        dna_moles = comp_dna_amount * 1000 / 330  # nmol
        compound_moles = compound_amount * 1000 / compound_mw  # nmol
        molar_ratio = compound_moles / dna_moles if dna_moles > 0 else 0
        st.metric(f"Molar Ratio ({compound_name}:DNA)", f"{molar_ratio:.3f}")

# ========== Step 2: Lipid Formulation ==========
st.markdown("---")
st.subheader("📋 Step 2: Lipid Formulation Parameters")
st.markdown(f"**After DNA-{compound_name} complex formation, add the lipid components. The complex solution acts as the aqueous phase.**")

col_l1, col_l2, col_l3, col_l4 = st.columns(4)
with col_l1:
    ion_lipid_mw = st.number_input(
        "Ionizable Lipid MW (Da)",
        min_value=100.0,
        step=1.0,
        value=710.182,
        key="prot_ion_mw",
        help="SM-102 MW = 710.182"
    )
with col_l2:
    helper_lipid_mw = st.number_input(
        "Helper Lipid MW (Da)",
        min_value=100.0,
        step=1.0,
        value=790.147,
        key="prot_helper_mw",
        help="DSPC MW = 790.147"
    )
with col_l3:
    chol_mw = st.number_input(
        "Cholesterol MW (Da)",
        min_value=100.0,
        step=1.0,
        value=386.654,
        key="prot_chol_mw"
    )
with col_l4:
    peg_mw = st.number_input(
        "PEG-DMG2000 MW (Da)",
        min_value=1000.0,
        step=1.0,
        value=2509.2,
        key="prot_peg_mw"
    )

col_l5, col_l6, col_l7, col_l8 = st.columns(4)
with col_l5:
    ion_stock_conc = st.number_input(
        "Ionizable Lipid Conc (mg/ml)",
        min_value=0.1,
        step=1.0,
        value=40.0,
        key="prot_ion_conc"
    )
with col_l6:
    helper_stock_conc = st.number_input(
        "Helper Lipid Conc (mg/ml)",
        min_value=0.1,
        step=1.0,
        value=10.0,
        key="prot_helper_conc"
    )
with col_l7:
    chol_stock_conc = st.number_input(
        "Cholesterol Conc (mg/ml)",
        min_value=0.1,
        step=1.0,
        value=10.0,
        key="prot_chol_conc"
    )
with col_l8:
    peg_stock_conc = st.number_input(
        "PEG-DMG2000 Conc (mg/ml)",
        min_value=0.1,
        step=1.0,
        value=10.0,
        key="prot_peg_conc"
    )

col_l9, col_l10, col_l11, col_l12 = st.columns(4)
with col_l9:
    ion_ratio = st.number_input(
        "Ionizable Lipid %",
        min_value=0.0,
        step=1.0,
        value=50.0,
        key="prot_ion_ratio"
    )
with col_l10:
    helper_ratio = st.number_input(
        "Helper Lipid %",
        min_value=0.0,
        step=1.0,
        value=10.0,
        key="prot_helper_ratio"
    )
with col_l11:
    chol_ratio = st.number_input(
        "Cholesterol %",
        min_value=0.0,
        step=0.1,
        value=38.5,
        key="prot_chol_ratio"
    )
with col_l12:
    peg_ratio = st.number_input(
        "PEG-DMG2000 %",
        min_value=0.0,
        step=0.1,
        value=1.5,
        key="prot_peg_ratio"
    )

# ===== Ratio Input Method Selection =====
st.markdown("**Lipid-to-DNA Ratio Specification**")
prot_ratio_mode = st.radio(
    "Select Input Method",
    ["Mass Ratio (Ion Lipid:DNA)", "N/P Ratio (Ion/pDNA)"],
    index=0,
    horizontal=True,
    key="prot_ratio_mode",
    help="Choose whether to input Mass Ratio or N/P Ratio (requires ionizable lipid MW and amines per molecule)"
)

col_l13_ratio, col_l14_ratio = st.columns(2)
with col_l13_ratio:
    if prot_ratio_mode == "N/P Ratio (Ion/pDNA)":
        prot_np_ratio = st.number_input(
            "N/P Ratio (Ion/pDNA)",
            min_value=0.0,
            step=0.5,
            value=8.0,
            key="prot_np_ratio",
            help="N/P ratio (similar to Page 2 pDNA formulation). For SM-102, N/P=8 is equivalent to ~Mass Ratio 17:1"
        )
    else:
        prot_np_ratio = 0.0  # Placeholder
        
with col_l14_ratio:
    if prot_ratio_mode == "N/P Ratio (Ion/pDNA)":
        prot_amines_per_molecule = st.number_input(
            "Amines per Ionizable Lipid",
            min_value=0.1,
            step=0.1,
            value=1.0,
            key="prot_amines_per_molecule",
            help="Number of tertiary amine groups per ionizable lipid molecule (typically 1.0 for SM-102)"
        )
    else:
        ion_lipid_to_dna_mass_ratio = st.number_input(
            "Ionizable Lipid to DNA Mass Ratio",
            min_value=0.1,
            step=0.5,
            value=10.0,
            key="prot_ion_to_dna_mass_ratio",
            help="Mass ratio of ionizable lipid to DNA (e.g., 10:1 means 10 μg lipid per 1 μg DNA)"
        )
        prot_amines_per_molecule = 1.0  # Placeholder

col_l13, col_l14, col_l15 = st.columns(3)
with col_l13:
    aq_eth_ratio = st.number_input(
        "Aqueous to Ethanol Ratio",
        min_value=0.5,
        step=0.1,
        value=3.0,
        key="prot_aq_eth_ratio",
        help="Ratio of aqueous phase (DNA-Compound complex) to ethanol phase"
    )
with col_l14:
    # Display selected ratio mode
    if prot_ratio_mode == "N/P Ratio (Ion/pDNA)":
        st.metric("Selected Mode", "N/P Ratio")
    else:
        st.metric("Selected Mode", "Mass Ratio")
with col_l15:
    # Auto-calculate based on Page 2 logic: final_lnp_volume = nucleic_acid_scale / 0.1
    # nucleic_acid_scale is comp_dna_amount (in μg)
    suggested_final_volume = comp_dna_amount / 0.1
    st.metric(
        "Target Final LNP Volume (μL)",
        f"{suggested_final_volume:.2f}",
        help=f"Auto-calculated: {comp_dna_amount:.2f} μg ÷ 0.1 = {suggested_final_volume:.2f} μL"
    )
    final_lnp_volume_target = suggested_final_volume

# ========== Calculate Multi-step LNP ==========
if st.button("🧬 Calculate Multi-step LNP Formulation", key="calc_protamine", use_container_width=True):
    try:
        # ===== Use Page 2 Logic =====
        # Convert N/P ratio to Mass ratio if needed
        if prot_ratio_mode == "N/P Ratio (Ion/pDNA)":
            # Formula: Mass Ratio = (N/P × MW) / (Amines × 330)
            ion_lipid_to_dna_mass_ratio = (prot_np_ratio * ion_lipid_mw) / (prot_amines_per_molecule * 330)
            st.info(f"📊 Calculated Mass Ratio: {ion_lipid_to_dna_mass_ratio:.2f}:1 (from N/P ratio {prot_np_ratio:.2f})")
        
        # Validation: Check lipid molar percentages sum to 100%
        total_lipid_molar_percent = ion_ratio + helper_ratio + chol_ratio + peg_ratio
        
        if total_lipid_molar_percent != 100:
            st.warning(f"⚠️ Warning: Lipid molar % sum = {total_lipid_molar_percent}% (recommended: 100%)")
        
        # Step 1: Calculate final LNP volume (DNA represents 10% of total volume)
        final_lnp_volume_target = comp_dna_amount / 0.1
        
        # Step 2: Calculate phase volumes
        ethanol_phase_volume = final_lnp_volume_target / (aq_eth_ratio + 1)
        aqueous_phase_volume = final_lnp_volume_target * (aq_eth_ratio / (aq_eth_ratio + 1))
        
        # Step 3: Calculate lipid moles based on Page 2 logic
        # Use mass ratio: ion_lipid_mass = comp_dna_amount * ion_lipid_to_dna_mass_ratio
        ion_lipid_mass = comp_dna_amount * ion_lipid_to_dna_mass_ratio
        ion_lipid_moles = ion_lipid_mass / ion_lipid_mw
        
        # Calculate other lipid moles based on molar ratio percentages (from ion_ratio)
        helper_lipid_moles = ion_lipid_moles * helper_ratio / ion_ratio if ion_ratio > 0 else 0
        chol_moles = ion_lipid_moles * chol_ratio / ion_ratio if ion_ratio > 0 else 0
        peg_moles = ion_lipid_moles * peg_ratio / ion_ratio if ion_ratio > 0 else 0
        
        # Step 4: Calculate other lipid masses
        helper_lipid_mass = helper_lipid_moles * helper_lipid_mw
        chol_mass = chol_moles * chol_mw
        peg_mass = peg_moles * peg_mw
        
        # Step 5: Calculate lipid volumes
        ion_lipid_vol = ion_lipid_mass / ion_stock_conc
        helper_lipid_vol = helper_lipid_mass / helper_stock_conc if helper_stock_conc > 0 else 0
        chol_vol = chol_mass / chol_stock_conc if chol_stock_conc > 0 else 0
        peg_vol = peg_mass / peg_stock_conc if peg_stock_conc > 0 else 0
        
        # Step 6: Calculate ethanol volume (remaining after lipid components)
        ethanol_vol = ethanol_phase_volume - ion_lipid_vol - helper_lipid_vol - chol_vol - peg_vol
        
        # Step 7: Calculate aqueous phase components
        citrate_volume = 0.1 * aqueous_phase_volume
        water_volume = aqueous_phase_volume - comp_dna_complex_volume - citrate_volume
        
        # Create results dataframe
        results_data = {
            'Component': [
                'DNA (in buffer)',
                f'{compound_name}',
                'Ionizable Lipid (in EtOH)',
                'Helper Lipid (in EtOH)',
                'Cholesterol (in EtOH)',
                'PEG-DMG2000 (in EtOH)',
                'Ethanol',
                'Citrate Buffer',
                'Water'
            ],
            'Volume (μL)': [
                comp_dna_volume,
                compound_volume,
                ion_lipid_vol,
                helper_lipid_vol,
                chol_vol,
                peg_vol,
                max(0, ethanol_vol),
                citrate_volume,
                max(0, water_volume)
            ],
            'Mass (μg)': [
                comp_dna_amount,
                compound_amount,
                ion_lipid_mass,
                helper_lipid_mass,
                chol_mass,
                peg_mass,
                '-',
                '-',
                '-'
            ]
        }
        
        results_df = pd.DataFrame(results_data)
        st.session_state.compound_results = results_df
        
        # Add to history
        history_record = {
            "Experiment": comp_exp_name if comp_exp_name else "Unnamed",
            "Compound": compound_name,
            "DNA (μg)": comp_dna_amount,
            f"{compound_name}:DNA w/w": f"{compound_w_w_ratio:.2f}:1",
            "Total LNP (μL)": f"{final_lnp_volume_target:.2f}",
            "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.compound_history.append(history_record)
        
        st.success(f"✅ Multi-step {compound_name}-DNA-LNP formulation calculated!")
        
    except Exception as e:
        st.error(f"❌ Error calculating formulation: {str(e)}")

# ========== Display Results ==========
if st.session_state.compound_results is not None:
    st.markdown("---")
    st.subheader("📊 Formulation Composition")
    
    tab_comp, tab_protocol = st.tabs(["Composition", "Protocol"])
    
    with tab_comp:
        st.dataframe(st.session_state.compound_results, use_container_width=True)
        
        # Summary metrics
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        with col_m1:
            st.metric("Total Volume", f"{final_lnp_volume_target:.2f} μL")
        with col_m2:
            st.metric(f"DNA-{compound_name} Complex", f"{comp_dna_complex_volume:.2f} μL")
        with col_m3:
            dna_moles = comp_dna_amount * 1000 / 330
            ion_lipid_moles = (comp_dna_amount * ion_lipid_to_dna_mass_ratio) / ion_lipid_mw
            st.metric(f"Mass Ratio (Ion:DNA)", f"{ion_lipid_to_dna_mass_ratio:.2f}:1")
        with col_m4:
            # Calculate N/P ratio
            np_ratio = (ion_lipid_moles * prot_amines_per_molecule * 1e6) / (dna_moles * 1e3) if dna_moles > 0 else 0
            st.metric("N/P Ratio", f"{np_ratio:.2f}")
        with col_m5:
            compound_moles = compound_amount * 1000 / compound_mw
            st.metric(f"Molar Ratio ({compound_name}:DNA)", f"{compound_moles/dna_moles:.3f}")
    
    with tab_protocol:
        st.markdown(f"""
        ### 📋 Experimental Protocol: Multi-step LNP with {compound_name}
        
        **Step 1: Complex Formation**
        
        1. Prepare DNA solution: {comp_dna_amount:.2f} μg DNA in {comp_dna_buffer}
           - Volume: {comp_dna_volume:.2f} μL (from {comp_dna_stock:.1f} μg/μL stock)

        2. Prepare {compound_name} solution: {compound_amount:.2f} μg
           - Volume: {compound_volume:.2f} μL (from {compound_stock_conc:.1f} mg/ml stock)
           - w/w ratio to DNA: {compound_w_w_ratio:.2f}:1

        3. Mix DNA and {compound_name} solutions
           - Add {compound_name} to DNA slowly with mixing
           - Total volume: {comp_dna_complex_volume:.2f} μL

        4. Incubate at {compound_temp} for {compound_incubation} minutes
           - This allows DNA-{compound_name} complex formation
        
        **Step 2: Lipid Mixing (Rapid)**
        
        1. Prepare ethanol phase and aqueous phase as shown in composition table
        2. Mix ethanol phase into aqueous phase rapidly
        3. Optional dialysis or buffer exchange for 2-4 hours
        """)
    
    # Download options
    st.markdown("---")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        csv_data = st.session_state.compound_results.to_csv(index=False)
        st.download_button(
            "📥 Download Formulation (CSV)",
            csv_data,
            file_name=f"{compound_name.lower()}_lnp_{comp_exp_name or 'formulation'}.csv",
            mime="text/csv",
            key="download_compound"
        )
    with col_d2:
        if st.button("🗑️ Clear Results", key="clear_compound"):
            st.session_state.compound_results = None
            st.rerun()

# ========== History ==========
if len(st.session_state.compound_history) > 0:
    st.markdown("---")
    st.subheader("📋 Formulation History")
    history_df = pd.DataFrame(st.session_state.compound_history)
    st.dataframe(history_df, use_container_width=True)
    
    if st.button("🗑️ Clear History", key="clear_comp_history"):
        st.session_state.compound_history = []
        st.rerun()

# ========== Best Practices ==========
with st.expander(f"💡 Best Practices for DNA-Compound-Lipid LNPs"):
    st.markdown(f"""
    ### Advantages of DNA-Compound-LNP:
    - **DNA interaction:** Custom compound interacts with and modifies DNA structure
    - **Cellular uptake:** Compound may improve cellular uptake properties
    - **Improved formulation:** Pre-complexation may enhance complex stability
    - **Tunable properties:** Adjust w/w ratio to optimize performance
    
    ### Key Optimization Parameters:
    
    **1. Compound:DNA Ratio (w/w)**
    - Typical range: 0.5:1 to 10:1
    - Start with 1:1 and adjust based on results
    
    **2. Incubation Time**
    - Minimum: 5 minutes
    - Standard: 10-15 minutes
    - Can extend to 30+ minutes
    
    **3. Buffer Conditions**
    - Use appropriate pH (physiological: 6.5-8.0)
    - Match ionic strength to prevent aggregation
    
    **4. Quality Control**
    - Size: 50-300 nm
    - Encapsulation: > 70-80%
    - Zeta potential: Varies by compound
    """)



