import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("⚗️ LNP Formulation Calculator with 5th Component")

# ============================================================================
# SHARED FUNCTIONS
# ============================================================================

def calculate_np_ratio(nucleic_acid_mass_ug, ionizable_lipid_moles, amines_per_molecule=1.0):
    """
    Calculates the N/P ratio for LNP formulation.
    
    Parameters:
    - nucleic_acid_mass_ug: Mass of DNA/RNA in micrograms
    - ionizable_lipid_moles: Moles of ionizable lipid (μmol)
    - amines_per_molecule: Number of ionizable tertiary amine groups per lipid molecule (default=1.0)
    
    Returns:
    - N/P ratio: Molar ratio of amine groups (N) to phosphate groups (P)
    """
    nucleic_acid_mass_g = nucleic_acid_mass_ug * 1e-6
    phosphate_moles_mol = nucleic_acid_mass_g / 330.0
    phosphate_moles_umol = phosphate_moles_mol * 1e6
    
    amine_moles_umol = ionizable_lipid_moles * amines_per_molecule
    
    if phosphate_moles_umol > 0:
        np_ratio = amine_moles_umol / phosphate_moles_umol
    else:
        np_ratio = 0
    
    return np_ratio, amine_moles_umol, phosphate_moles_umol

def format_ratio_label(ratio_value):
    """Formats ratio values without trailing decimals when unnecessary."""
    if ratio_value == int(ratio_value):
        return f"{int(ratio_value)}:1"
    return f"{ratio_value:.1f}:1"

def make_lnp_formulation_5components(
    nucleic_acid_scale, nucleic_acid_stock_concentration, ionizable_lipid_to_na_ratio, 
    aqueous_to_ethanol_ratio, ionizable_lipid_mw, helper_lipid_mw, cholesterol_mw, 
    pegdmg2000_mw, additional_component_mw, ionizable_lipid_concentration, helper_lipid_concentration, 
    cholesterol_concentration, pegdmg2000_concentration, additional_component_concentration,
    ionizable_lipid_ratio, helper_lipid_ratio, cholesterol_ratio, pegdmg2000_ratio, 
    additional_component_ratio, na_type="Nucleic Acid"
):
    """
    Calculates the composition and prepares an LNP formulation with 5 components.
    """
    ionizable_lipid_moles = (nucleic_acid_scale * ionizable_lipid_to_na_ratio) / ionizable_lipid_mw
    
    helper_lipid_moles = ionizable_lipid_moles * helper_lipid_ratio / ionizable_lipid_ratio
    cholesterol_moles = ionizable_lipid_moles * cholesterol_ratio / ionizable_lipid_ratio
    pegdmg2000_moles = ionizable_lipid_moles * pegdmg2000_ratio / ionizable_lipid_ratio
    additional_component_moles = ionizable_lipid_moles * additional_component_ratio / ionizable_lipid_ratio

    ionizable_lipid_mass = ionizable_lipid_moles * ionizable_lipid_mw
    helper_lipid_mass = helper_lipid_moles * helper_lipid_mw
    cholesterol_mass = cholesterol_moles * cholesterol_mw
    pegdmg2000_mass = pegdmg2000_moles * pegdmg2000_mw
    additional_component_mass = additional_component_moles * additional_component_mw

    final_lnp_volume = nucleic_acid_scale / 0.1
    
    ionizable_lipid_volume = ionizable_lipid_mass / ionizable_lipid_concentration
    helper_lipid_volume = helper_lipid_mass / helper_lipid_concentration
    cholesterol_volume = cholesterol_mass / cholesterol_concentration
    pegdmg2000_volume = pegdmg2000_mass / pegdmg2000_concentration
    additional_component_volume = additional_component_mass / additional_component_concentration
    
    ethanol = final_lnp_volume / (aqueous_to_ethanol_ratio + 1) - ionizable_lipid_volume - helper_lipid_volume - cholesterol_volume - pegdmg2000_volume - additional_component_volume
    ethanol_phase_volume = ionizable_lipid_volume + helper_lipid_volume + cholesterol_volume + pegdmg2000_volume + additional_component_volume + ethanol

    aqueous_phase_volume = final_lnp_volume * (aqueous_to_ethanol_ratio / (aqueous_to_ethanol_ratio + 1))
    nucleic_acid_volume = nucleic_acid_scale / nucleic_acid_stock_concentration
    citrate_volume = 0.1 * aqueous_phase_volume
    water_volume = aqueous_phase_volume - nucleic_acid_volume - citrate_volume

    data = {
        'Component': ['Ionizable Lipid', 'Helper Lipid', 'Cholesterol', 'PEG-DMG2000', 'Additional Component', 'Ethanol', na_type, 'Citrate', 'Water'],
        'Volume (μL)': [ionizable_lipid_volume, helper_lipid_volume, cholesterol_volume, pegdmg2000_volume, additional_component_volume, ethanol, nucleic_acid_volume, citrate_volume, water_volume]
    }

    df = pd.DataFrame(data)
    
    volumes = {
        "Ionizable Lipid": ionizable_lipid_volume,
        "helper_lipid_volume": helper_lipid_volume,
        "cholesterol_volume": cholesterol_volume,
        "pegdmg2000_volume": pegdmg2000_volume,
        "additional_component_volume": additional_component_volume,
        "ethanol": ethanol,
        "ethanol_phase_volume": ethanol_phase_volume,
        "nucleic_acid_volume": nucleic_acid_volume,
        "citrate_volume": citrate_volume,
        "water_volume": water_volume,
        "aqueous_volume": aqueous_phase_volume,
        "ionizable_lipid_moles": ionizable_lipid_moles,
        "ethanol_phase_total_volume": ethanol_phase_volume,
        "aqueous_master_mix_volume": citrate_volume + water_volume,
        "ethanol_master_mix_volume": ionizable_lipid_volume + helper_lipid_volume + cholesterol_volume + pegdmg2000_volume + additional_component_volume,
    }

    return df, volumes

def append_bulk_summary_rows_5components(
    df, volumes, times, ethanol_multiplier=1.5, aqueous_multiplier=1.2, bulk_multiplier=1.2
):
    """
    Appends bulk master mix summary rows to a formulation dataframe with 5 components.
    """
    ethanol_total = volumes["ethanol_master_mix_volume"] * times * ethanol_multiplier
    aqueous_total = volumes["aqueous_master_mix_volume"] * times * aqueous_multiplier
    column_total = df['Volume (μL)'].sum()
    bulk_total = column_total * times * bulk_multiplier
    bulk_rows = pd.DataFrame({
        'Component': [
            f"Ethanol Master Mix x{times} ({ethanol_multiplier}x)",
            f"Aqueous Master Mix x{times} ({aqueous_multiplier}x)"
        ],
        'Volume (μL)': [ethanol_total, aqueous_total]
    })
    total_row = pd.DataFrame({
        'Component': [f"Bulk Total x{times} ({bulk_multiplier}x)"],
        'Volume (μL)': [bulk_total]
    })
    df_with_bulk = pd.concat([df, bulk_rows, total_row], ignore_index=True)
    return df_with_bulk, ethanol_total, aqueous_total, bulk_total

# ============================================================================
# MAIN PAGE
# ============================================================================

st.header("5-Component LNP Formulation Calculator")
st.info("💡 This calculator extends the standard 4-component LNP formulation by adding a fifth component. Perfect for incorporating additional functionalized lipids, targeting ligands, or other bioactive molecules.")

# Initialize session state
if "five_comp_result_df" not in st.session_state:
    st.session_state.five_comp_result_df = None
    st.session_state.five_comp_volumes = None
    st.session_state.five_comp_history = []

# Input section
st.subheader("📋 5-Component LNP Formulation Parameters")

# Ratio input method selection
ratio_mode = st.radio(
    "Select Input Method",
    ["Mass Ratio", "N/P Ratio"],
    index=1,
    horizontal=True,
    key="five_ratio_mode",
    help="Choose whether to input Mass Ratio or N/P Ratio"
)

# ========== Nucleic Acid & Ratio Parameters ==========
st.markdown("### 🧬 Nucleic Acid & Basic Parameters")
col1, col2, col3, col4 = st.columns(4)
with col1:
    scale = st.number_input("Nucleic Acid Scale (μg)", min_value=0.0, step=1.0, value=5.0, key="five_scale")
with col2:
    stock_conc = st.number_input("Nucleic Acid Stock (μg/μL)", min_value=0.0, step=0.1, value=1.0, key="five_stock")
with col3:
    if ratio_mode == "N/P Ratio":
        np_ratio_input = st.number_input("N/P Ratio", min_value=0.0, step=0.5, value=8.0, key="five_np_input")
    else:
        ion_na_ratio = st.number_input("Ionizable Lipid to NA Mass Ratio", min_value=0.0, step=1.0, value=17.0, key="five_ratio")
        
with col4:
    aq_eth_ratio = st.number_input("Aqueous to Ethanol Ratio", min_value=0.0, step=0.1, value=3.0, key="five_aq_eth")

with col1:
    amines = st.number_input("Amines per Ionizable Lipid", min_value=0.0, step=1.0, value=1.0, key="five_amines")

# ========== Molecular Weights ==========
st.markdown("### ⚖️ Molecular Weights (μg/μmol)")
col5, col6, col7, col8, col9 = st.columns(5)
with col5:
    ion_mw = st.number_input("Ionizable Lipid MW", min_value=0.0, step=1.0, value=710.182, key="five_ion_mw", help="SM-102 MW = 710.182")
with col6:
    helper_mw = st.number_input("Helper Lipid MW", min_value=0.0, step=1.0, value=790.147, key="five_helper_mw", help="DSPC MW = 790.147")
with col7:
    chol_mw = st.number_input("Cholesterol MW", min_value=0.0, step=1.0, value=386.654, key="five_chol_mw")
with col8:
    peg_mw = st.number_input("PEG-DMG2000 MW", min_value=0.0, step=1.0, value=2509.2, key="five_peg_mw")
with col9:
    add_mw = st.number_input("Additional Component MW", min_value=0.0, step=1.0, value=500.0, key="five_add_mw", placeholder="e.g., 500")

# ========== Concentrations ==========
st.markdown("### 🧪 Stock Concentrations (μg/μL)")
col10, col11, col12, col13, col14 = st.columns(5)
with col10:
    ion_conc = st.number_input("Ionizable Lipid Conc", min_value=0.0, step=1.0, value=10.0, key="five_ion_conc")
with col11:
    helper_conc = st.number_input("Helper Lipid Conc", min_value=0.0, step=1.0, value=10.0, key="five_helper_conc")
with col12:
    chol_conc = st.number_input("Cholesterol Conc", min_value=0.0, step=1.0, value=10.0, key="five_chol_conc")
with col13:
    peg_conc = st.number_input("PEG-DMG2000 Conc", min_value=0.0, step=1.0, value=10.0, key="five_peg_conc")
with col14:
    add_conc = st.number_input("Additional Component Conc", min_value=0.0, step=1.0, value=10.0, key="five_add_conc")

# ========== Molar Ratios ==========
st.markdown("### 📊 Molar Ratios (%)")
col15, col16, col17, col18, col19 = st.columns(5)
with col15:
    ion_ratio = st.number_input("Ionizable Lipid %", min_value=0.0, step=1.0, value=50.0, key="five_ion_ratio")
with col16:
    helper_ratio = st.number_input("Helper Lipid %", min_value=0.0, step=1.0, value=10.0, key="five_helper_ratio")
with col17:
    chol_ratio = st.number_input("Cholesterol %", min_value=0.0, step=0.5, value=35.0, key="five_chol_ratio")
with col18:
    peg_ratio = st.number_input("PEG-DMG2000 %", min_value=0.0, step=0.1, value=2.0, key="five_peg_ratio")
with col19:
    add_ratio = st.number_input("Additional Component %", min_value=0.0, step=0.1, value=3.0, key="five_add_ratio")

# ========== Additional Options ==========
col20, col21 = st.columns(2)
with col20:
    bulk_times = st.number_input("Bulk Preparation Times", min_value=1, step=1, value=1, key="five_bulk")
with col21:
    add_comp_name = st.text_input("5th Component Name", value="Target Ligand", placeholder="e.g., Targeting Peptide, Ionizable Surfactant", key="five_comp_name")

# Nucleic acid type
na_type = st.selectbox("Nucleic Acid Type", ["pDNA", "mRNA", "siRNA", "Other"], key="five_na_type")

formulation_name = st.text_input("Formulation Name", value="", placeholder="Enter name for this formulation", key="five_name")

# Calculate Mass Ratio from N/P if needed
if ratio_mode == "N/P Ratio":
    ion_na_ratio = (np_ratio_input * ion_mw) / (amines * 330)
    st.info(f"📊 Calculated Mass Ratio: {ion_na_ratio:.2f}:1 (from N/P ratio {np_ratio_input:.2f})")

# ========== Calculate Button ==========
col_calc1, col_calc2 = st.columns([3, 1])
with col_calc1:
    pass
with col_calc2:
    if st.button("📊 Calculate 5-Component Formulation", key="five_calc_btn", use_container_width=True):
        if stock_conc <= 0 or ion_mw <= 0 or ion_conc <= 0:
            st.error("❌ All concentrations and MWs must be positive values!")
        else:
            result_df, volumes = make_lnp_formulation_5components(
                scale, stock_conc, ion_na_ratio, aq_eth_ratio,
                ion_mw, helper_mw, chol_mw, peg_mw, add_mw,
                ion_conc, helper_conc, chol_conc, peg_conc, add_conc,
                ion_ratio, helper_ratio, chol_ratio, peg_ratio, add_ratio,
                na_type=na_type
            )
            display_df, bulk_ethanol, bulk_aqueous, bulk_total = append_bulk_summary_rows_5components(
                result_df, volumes, bulk_times
            )
            st.session_state.five_comp_result_df = display_df
            st.session_state.five_comp_volumes = volumes
            
            # Calculate N/P ratio
            np_ratio, n_moles, p_moles = calculate_np_ratio(
                scale, volumes["ionizable_lipid_moles"], amines
            )
            
            # Save to history
            record = {
                "Name": formulation_name if formulation_name else "Unnamed",
                "NA Type": na_type,
                "NA (μg)": f"{scale:.2f}",
                "Ion:NA Ratio": format_ratio_label(ion_na_ratio),
                "N/P Ratio": f"{np_ratio:.3f}",
                "Ion%": f"{ion_ratio:.1f}%",
                "Helper%": f"{helper_ratio:.1f}%",
                "Chol%": f"{chol_ratio:.1f}%",
                "PEG%": f"{peg_ratio:.2f}%",
                f"{add_comp_name}%": f"{add_ratio:.2f}%",
                "Ion Lipid (μL)": f"{volumes['Ionizable Lipid']:.2f}",
                "Helper (μL)": f"{volumes['helper_lipid_volume']:.2f}",
                "Cholesterol (μL)": f"{volumes['cholesterol_volume']:.2f}",
                "PEG (μL)": f"{volumes['pegdmg2000_volume']:.2f}",
                f"{add_comp_name} (μL)": f"{volumes['additional_component_volume']:.2f}",
                "Ethanol (μL)": f"{volumes['ethanol']:.2f}",
                "Ethanol Phase Total (μL)": f"{volumes['ethanol_phase_total_volume']:.2f}",
                "Citrate (μL)": f"{volumes['citrate_volume']:.2f}",
                "Water (μL)": f"{volumes['water_volume']:.2f}",
                "NA (μL)": f"{volumes['nucleic_acid_volume']:.2f}",
                "Aqueous Phase Total (μL)": f"{volumes['aqueous_volume']:.2f}",
                "Total LNP (μL)": f"{volumes['ethanol_phase_total_volume'] + volumes['aqueous_volume']:.2f}",
            }
         
            st.session_state.five_comp_history.append(record)
            st.success(f"✅ 5-component formulation '{record['Name']}' calculated!")

# ========== Results Display ==========
if st.session_state.five_comp_result_df is not None:
    st.markdown("---")
    st.subheader("📊 Formulation Results")
    
    # Display the calculation results
    tab1, tab2, tab3 = st.tabs(["Composition", "Detailed Volumes", "Summary"])
    
    with tab1:
        st.dataframe(st.session_state.five_comp_result_df, use_container_width=True)
    
    with tab2:
        if st.session_state.five_comp_volumes:
            volumes_df = pd.DataFrame(
                list(st.session_state.five_comp_volumes.items()),
                columns=["Parameter", "Value"]
            )
            volumes_df["Value"] = pd.to_numeric(volumes_df["Value"], errors='coerce')
            volumes_df["Value"] = volumes_df["Value"].round(3)
            st.dataframe(volumes_df, use_container_width=True)
    
    with tab3:
        st.write(f"**Total LNP Volume:** {st.session_state.five_comp_volumes['ethanol_phase_total_volume'] + st.session_state.five_comp_volumes['aqueous_volume']:.2f} μL")
        st.write(f"**Ethanol Phase Volume:** {st.session_state.five_comp_volumes['ethanol_phase_total_volume']:.2f} μL")
        st.write(f"**Aqueous Phase Volume:** {st.session_state.five_comp_volumes['aqueous_volume']:.2f} μL")
        
        # Calculate N/P ratio if volumes exist
        if 'ionizable_lipid_moles' in st.session_state.five_comp_volumes:
            np_ratio, _, _ = calculate_np_ratio(
                scale, st.session_state.five_comp_volumes["ionizable_lipid_moles"], amines
            )
            st.write(f"**N/P Ratio:** {np_ratio:.3f}")

# ========== History Section ==========
if len(st.session_state.five_comp_history) > 0:
    st.markdown("---")
    st.subheader("📋 Formulation History")
    history_df = pd.DataFrame(st.session_state.five_comp_history)
    
    # Display with full width and scrolling
    st.dataframe(history_df, use_container_width=True, height=300)
    
    # Bulk View details
    with st.expander("📊 Bulk Preparation Summary"):
        st.info("💡 **Buffer Strategy:** Lipids and Ethanol ×1.5, Aqueous components ×1.2 to account for handling and evaporation losses")
        
        # Define which columns to include in bulk calculations
        bulk_multipliers = {
            "Ion Lipid (μL)": 1.5,
            "Helper (μL)": 1.5,
            "Cholesterol (μL)": 1.5,
            "PEG (μL)": 1.5,
            "Ethanol (μL)": 1.5,
            "Citrate (μL)": 1.2,
            "Water (μL)": 1.2,
            "NA (μL)": 1.2,
        }
        
        # Add the additional component if it exists
        for col in history_df.columns:
            if "μL)" in col and col not in bulk_multipliers and "Total" not in col:
                bulk_multipliers[col] = 1.5

        bulk_summary = []
        for column, multiplier in bulk_multipliers.items():
            if column not in history_df.columns:
                continue
            numeric_series = pd.to_numeric(history_df[column], errors="coerce")
            base_total = numeric_series.sum()
            bulk_total = base_total * multiplier
            bulk_summary.append({
                "Component": column,
                "Sum": base_total,
                "Bulk Volume": bulk_total
            })

        if bulk_summary:
            bulk_df = pd.DataFrame(bulk_summary)
            bulk_df["Sum"] = bulk_df["Sum"].round(2)
            bulk_df["Bulk Volume"] = bulk_df["Bulk Volume"].round(2)
            st.dataframe(bulk_df, use_container_width=True)
    
    # Download and Clear buttons
    col_h1, col_h2, col_h3 = st.columns([1, 1, 2])
    with col_h1:
        csv_data = history_df.to_csv(index=False)
        st.download_button(
            "📥 Download History (CSV)",
            csv_data,
            file_name="five_component_lnp_history.csv",
            mime="text/csv",
            key="five_download"
        )
    with col_h2:
        if st.button("🗑️ Clear History", key="five_clear"):
            st.session_state.five_comp_history = []
            st.session_state.five_comp_result_df = None
            st.rerun()
    with col_h3:
        st.info("💾 Use 'Download History' to save your formulations as CSV for future reference")

# ========== Tips Section ==========
with st.expander("💡 Tips for 5-Component LNP Formulations"):
    st.markdown("""
    ### Common 5th Component Options:
    
    1. **Targeting Ligands**
       - Aptamers, peptides, or antibody fragments
       - MW range: 3-15 kDa
       - Typical molar %: 1-5%
    
    2. **Ionizable Surfactants**
       - Additional pH-dependent surface molecules
       - MW range: 300-1000 Da
       - Typical molar %: 2-5%
    
    3. **Functional Lipids**
       - Stimuli-responsive lipids
       - Photocleavable lipids
       - MW range: 500-2000 Da
       - Typical molar %: 3-10%
    
    4. **Reporter Lipids**
       - Fluorescent lipids for tracking
       - MW range: 400-1000 Da
       - Typical molar %: 0.5-2%
    
    ### Key Parameters to Adjust:
    - **Molar %:** Must total 100% across all components
    - **Stock Concentration:** Use appropriate solvent (ethanol for lipophilic, aqueous for hydrophilic)
    - **Aqueous:Ethanol Ratio:** Standard 3:1, adjust for your specific component solubility
    
    ### Calculation Notes:
    - Total lipid composition must sum to 100%
    - Adjust aqueous phase volume if 5th component is hydrophilic
    - Consider interactions between 5th component and other lipids
    """)
