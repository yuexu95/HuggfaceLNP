import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")



st.title("🧬 LNP Formulation Calculator (pDNA & mRNA)")

# ============================================================================
# SHARED FUNCTIONS
# ============================================================================

def calculate_np_ratio(nucleic_acid_mass_ug, ionizable_lipid_moles, amines_per_molecule=1.0):
    """
    Calculates the N/P ratio for LNP formulation (works for both pDNA and mRNA).
    
    Parameters:
    - nucleic_acid_mass_ug: Mass of DNA/RNA in micrograms
    - ionizable_lipid_moles: Moles of ionizable lipid (μmol)
    - amines_per_molecule: Number of ionizable tertiary amine groups per lipid molecule (default=1.0)
    
    Returns:
    - N/P ratio: Molar ratio of amine groups (N) to phosphate groups (P)
    
    Notes:
    - For dsDNA: P (μmol) = DNA mass (μg) / 330
    - For mRNA: P (μmol) = RNA mass (μg) / 330
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

def calculate_EtOH_master_mix_volume(ion_lipid_volume, helper_lipid_volume, cholesterol_volume, pegdmg2000_volume):
    """
    Calculates the total volume of ethanol master mix needed for LNP formulation.
    """
    ethanol_master_mix_volume = ion_lipid_volume + helper_lipid_volume + cholesterol_volume + pegdmg2000_volume
    return ethanol_master_mix_volume

def calculate_EtOH_phase_total_volume(ethanol_master_mix_volume, ethanol_volume):
    """
    Calculates the total ethanol phase volume including ethanol master mix and additional ethanol.
    """
    ethanol_phase_total_volume = ethanol_master_mix_volume + ethanol_volume
    return ethanol_phase_total_volume

def calculate_Aqueous_phase_total_volume(ethanol_phase_total_volume):
    """
    Calculates the total aqueous phase volume.
    """
    aqueous_phase_total_volume = ethanol_phase_total_volume * (3 / 1)  # Assuming a 3:1 aqueous to ethanol ratio 
    return aqueous_phase_total_volume

def calculate_25mM_for_DNA_citrate_volume(aqueous_phase_total_volume):
    """
    Calculates the volume of 25 mM citrate needed for the aqueous phase.
    """
    citrate_volume_25mM = aqueous_phase_total_volume * 0.1 # 10% of aqueous phase volume, stock is 250 mM citrate buffer.
    return citrate_volume_25mM

def calculate_water_volume(aqueous_phase_total_volume, nucleic_acid_volume, citrate_volume_25mM):
    """
    Calculates the volume of water needed for the aqueous phase.
    """
    water_volume = aqueous_phase_total_volume - nucleic_acid_volume - citrate_volume_25mM
    return water_volume

def calculate_Aqueous_master_mix_volume(citrate_volume_25mM, water_volume):
    """
    Calculates the total aqueous master mix volume.
    """
    aqueous_master_mix_volume = citrate_volume_25mM + water_volume
    return aqueous_master_mix_volume

def make_lnp_formulation(
    nucleic_acid_scale, nucleic_acid_stock_concentration, ionizable_lipid_to_na_ratio, 
    aqueous_to_ethanol_ratio, ionizable_lipid_mw, helper_lipid_mw, cholesterol_mw, 
    pegdmg2000_mw, ionizable_lipid_concentration, helper_lipid_concentration, 
    cholesterol_concentration, pegdmg2000_concentration, ionizable_lipid_ratio, 
    helper_lipid_ratio, cholesterol_ratio, pegdmg2000_ratio, na_type="pDNA"
):
    """
    Calculates the composition and prepares an LNP formulation (pDNA or mRNA).
    """
    ionizable_lipid_moles = (nucleic_acid_scale * ionizable_lipid_to_na_ratio) / ionizable_lipid_mw
    
    helper_lipid_moles = ionizable_lipid_moles * helper_lipid_ratio / ionizable_lipid_ratio
    cholesterol_moles = ionizable_lipid_moles * cholesterol_ratio / ionizable_lipid_ratio
    pegdmg2000_moles = ionizable_lipid_moles * pegdmg2000_ratio / ionizable_lipid_ratio

    ionizable_lipid_mass = ionizable_lipid_moles * ionizable_lipid_mw
    helper_lipid_mass = helper_lipid_moles * helper_lipid_mw
    cholesterol_mass = cholesterol_moles * cholesterol_mw
    pegdmg2000_mass = pegdmg2000_moles * pegdmg2000_mw

    final_lnp_volume = nucleic_acid_scale / 0.1
    
    ionizable_lipid_volume = ionizable_lipid_mass / ionizable_lipid_concentration
    helper_lipid_volume = helper_lipid_mass / helper_lipid_concentration
    cholesterol_volume = cholesterol_mass / cholesterol_concentration
    pegdmg2000_volume = pegdmg2000_mass / pegdmg2000_concentration
    ethanol = final_lnp_volume / (aqueous_to_ethanol_ratio + 1) - ionizable_lipid_volume - helper_lipid_volume - cholesterol_volume - pegdmg2000_volume
    ethanol_phase_volume = ionizable_lipid_volume + helper_lipid_volume + cholesterol_volume + pegdmg2000_volume + ethanol

    aqueous_phase_volume = final_lnp_volume * (aqueous_to_ethanol_ratio / (aqueous_to_ethanol_ratio + 1))
    nucleic_acid_volume = nucleic_acid_scale / nucleic_acid_stock_concentration
    citrate_volume = 0.1 * aqueous_phase_volume
    water_volume = aqueous_phase_volume - nucleic_acid_volume - citrate_volume

    na_label = na_type
    data = {
        'Component': ['Ionizable Lipid', 'Helper Lipid', 'Cholesterol', 'PEG-DMG2000', 'Ethanol', na_label, 'Citrate', 'Water'],
        'Volume (μL)': [ionizable_lipid_volume, helper_lipid_volume, cholesterol_volume, pegdmg2000_volume, ethanol, nucleic_acid_volume, citrate_volume, water_volume]
    }

    df = pd.DataFrame(data)
    
    volumes = {
        "Ionizable Lipid": ionizable_lipid_volume,
        "helper_lipid_volume": helper_lipid_volume,
        "cholesterol_volume": cholesterol_volume,
        "pegdmg2000_volume": pegdmg2000_volume,
        "ethanol": ethanol,
        "ethanol_phase_volume": ethanol_phase_volume,
        "nucleic_acid_volume": nucleic_acid_volume,
        "citrate_volume": citrate_volume,
        "water_volume": water_volume,
        "aqueous_volume": aqueous_phase_volume,
        "ionizable_lipid_moles": ionizable_lipid_moles,
        "ethanol_phase_total_volume": ethanol_phase_volume,
        "aqueous_master_mix_volume": citrate_volume + water_volume,
        "ethanol_master_mix_volume": ionizable_lipid_volume + helper_lipid_volume + cholesterol_volume + pegdmg2000_volume,
    }

    return df, volumes

def prepare_bulk_lnp_volumes(volumes, times):
    """
    Prepares the volumes for bulk LNP preparation with extra buffer.
    """
    get = lambda k: volumes.get(k, 0)
    bulk_volumes = {
        "Component": ['Ionizable Lipid', "Helper Lipid", "Cholesterol", "PEG-DMG2000", "Ethanol", "Nucleic Acid", "Citrate", "Water"],
        "Volume (μL)": [
            get("Ionizable Lipid") * times * 1.5,
            get("helper_lipid_volume") * times * 1.5,
            get("cholesterol_volume") * times * 1.5,
            get("pegdmg2000_volume") * times * 1.5,
            get("ethanol") * times * 1.5,
            get("nucleic_acid_volume") * times * 1.2,
            get("citrate_volume") * times * 1.2,
            get("water_volume") * times * 1.2,
        ]
    } 
    bulk_df = pd.DataFrame(bulk_volumes)
    return bulk_df

def append_bulk_summary_rows(
    df, volumes, times, ethanol_multiplier=1.5, aqueous_multiplier=1.2, bulk_multiplier=1.2
):
    """
    Appends bulk master mix summary rows to a formulation dataframe.
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
# PAGE TABS
# ============================================================================

tab_pdna, tab_mrna = st.tabs(["🧬 pDNA Formulation", "〰️ mRNA Formulation"])

# ============================================================================
# TAB 1: pDNA FORMULATION
# ============================================================================

with tab_pdna:
    st.header("pDNA LNP Formulation Calculator")
    st.info("Note: This calculator is designed for double-stranded plasmid DNA (dsDNA). For single-stranded DNA (ssDNA), please adjust the calculations accordingly. For pDNA delivery, the citrate buffer concentration is typically 25 mM.")
    
    # Initialize session state for pDNA
    if "pdna_result_df" not in st.session_state:
        st.session_state.pdna_result_df = None
        st.session_state.pdna_volumes = None
        st.session_state.pdna_history = []
    
    # Input section
    st.subheader("📋 pDNA Formulation Parameters")
    
    # Ratio input method selection
    pdna_ratio_mode = st.radio(
        "Select Input Method",
        ["Mass Ratio", "N/P Ratio"],
        index=1,
        horizontal=True,
        key="pdna_ratio_mode",
        help="Choose whether to input Mass Ratio or N/P Ratio"
    )
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pdna_scale = st.number_input("DNA Scale (μg)", min_value=0.0, step=1.0, value=5.0, key="pdna_scale", help="Minimum DNA amount for each LNP formation is typically around 3 μg")
    with col2:
        pdna_stock_conc = st.number_input("DNA Stock (μg/μL)", min_value=0.0, step=0.1, value=1.0, key="pdna_stock", help="Concentration of the DNA stock solution")
    with col3:
        if pdna_ratio_mode == "N/P Ratio":
            pdna_np_ratio_input = st.number_input("N/P Ratio", min_value=0.0, step=0.5, value=8.0, key="pdna_np_input", help="N/P ratio of 8 is equivalent to Mass Ratio ~17:1 for SM-102")
        else:
            pdna_ion_dna_ratio = st.number_input("Ionizable Lipid to DNA Mass Ratio", min_value=0.0, step=1.0, value=17.0, key="pdna_ratio")
            
    with col4:
        pdna_aq_eth_ratio = st.number_input("Aqueous to Ethanol Ratio", min_value=0.0, step=0.1, value=3.0, key="pdna_aq_eth", help="Common ratio is 3:1")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        pdna_ion_mw = st.number_input("Ionizable Lipid MW (μg/μmol)", min_value=0.0, step=1.0, value=710.182, key="pdna_ion_mw", help="SM-102 MW = 710.182")
    with col6:
        pdna_helper_mw = st.number_input("Helper Lipid MW (μg/μmol)", min_value=0.0, step=1.0, value=790.147, key="pdna_helper_mw", help="DSPC MW = 790.147")
    with col7:
        pdna_chol_mw = st.number_input("Cholesterol MW (μg/μmol)", min_value=0.0, step=1.0, value=386.654, key="pdna_chol_mw", help="Cholesterol MW = 386.654")
    with col8:
        pdna_peg_mw = st.number_input("PEG-DMG2000 MW (μg/μmol)", min_value=0.0, step=1.0, value=2509.2, key="pdna_peg_mw", help="PEG-DMG2000 MW = 2509.2")

    col9, col10, col11, col12 = st.columns(4)
    with col9:
        pdna_ion_conc = st.number_input("Ionizable Lipid Conc (μg/μL)", min_value=0.0, step=1.0, value=10.0, key="pdna_ion_conc", help="Suggested ionizable lipid concentration is 40 μg/μL")
    with col10:
        pdna_helper_conc = st.number_input("Helper Lipid Conc (μg/μL)", min_value=0.0, step=1.0, value=10.0, key="pdna_helper_conc", help="Suggested helper lipid concentration is 10 μg/μL")
    with col11:
        pdna_chol_conc = st.number_input("Cholesterol Conc (μg/μL)", min_value=0.0, step=1.0, value=10.0, key="pdna_chol_conc", help="Suggested cholesterol concentration is 10 μg/μL")
    with col12:
        pdna_peg_conc = st.number_input("PEG-DMG2000 Conc (μg/μL)", min_value=0.0, step=1.0, value=10.0, key="pdna_peg_conc", help="Suggested PEG-DMG2000 concentration is 10 μg/μL")
    
    col13, col14, col15, col16 = st.columns(4)
    with col13:
        pdna_ion_ratio = st.number_input("Ionizable Lipid Molar % ", min_value=0.0, step=1.0, value=50.0, key="pdna_ion_ratio")
    with col14:
        pdna_helper_ratio = st.number_input("Helper Lipid Molar %", min_value=0.0, step=1.0, value=10.0, key="pdna_helper_ratio")
    with col15:
        pdna_chol_ratio = st.number_input("Cholesterol Molar %", min_value=0.0, step=0.5, value=38.5, key="pdna_chol_ratio")
    with col16:
        pdna_peg_ratio = st.number_input("PEG-DMG2000 Molar %", min_value=0.0, step=0.1, value=1.5, key="pdna_peg_ratio")
    
    col17, col18 = st.columns(2)
    with col17:
        pdna_bulk_times = st.number_input("Bulk Preparation Times", min_value=1, step=1, value=1, key="pdna_bulk", help="Prepare extra volume for bulk LNP formulation")
    with col18:
        pdna_amines = st.number_input("Amines per Ionizable Lipid", min_value=0.0, step=1.0, value=1.0, key="pdna_amines", help="Number of ionizable tertiary amine groups per lipid molecule (default=1.0)")
    
    # Calculate Mass Ratio from N/P if needed
    if pdna_ratio_mode == "N/P Ratio":
        # Mass Ratio = (N/P × MW) / (Amines × 330)
        pdna_ion_dna_ratio = (pdna_np_ratio_input * pdna_ion_mw) / (pdna_amines * 330)
        st.info(f"📊 Calculated Mass Ratio: {pdna_ion_dna_ratio:.2f}:1 (from N/P ratio {pdna_np_ratio_input:.2f})")
    
    pdna_name = st.text_input("Formulation Name", value="", placeholder="Enter name for this pDNA formulation", key="pdna_name")
    
    # Calculate button
    if st.button("📊 Calculate pDNA Formulation", key="pdna_calc_btn"):
        if pdna_stock_conc <= 0 or pdna_ion_mw <= 0 or pdna_ion_conc <= 0:
            st.error("All concentrations and MWs must be positive values!")
        else:
            pdna_result_df, pdna_volumes = make_lnp_formulation(
                pdna_scale, pdna_stock_conc, pdna_ion_dna_ratio, pdna_aq_eth_ratio,
                pdna_ion_mw, pdna_helper_mw, pdna_chol_mw, pdna_peg_mw,
                pdna_ion_conc, pdna_helper_conc, pdna_chol_conc, pdna_peg_conc,
                pdna_ion_ratio, pdna_helper_ratio, pdna_chol_ratio, pdna_peg_ratio,
                na_type="pDNA"
            )
            pdna_display_df, pdna_bulk_ethanol, pdna_bulk_aqueous, pdna_bulk_total = append_bulk_summary_rows(
                pdna_result_df, pdna_volumes, pdna_bulk_times
            )
            st.session_state.pdna_result_df = pdna_display_df
            st.session_state.pdna_volumes = pdna_volumes
            
            # Calculate N/P ratio
            np_ratio, n_moles, p_moles = calculate_np_ratio(
                pdna_scale, pdna_volumes["ionizable_lipid_moles"], pdna_amines
            )
            
            # Save to history
            record = {
                "Name": pdna_name if pdna_name else "Unnamed",
                "Ion Lipid (MW)": f"{pdna_ion_mw:.2f}",
                "DNA (μg)": f"{pdna_scale:.2f}",
                "Ion:DNA Ratio": format_ratio_label(pdna_ion_dna_ratio),
                "N/P Ratio": f"{np_ratio:.3f}",
                "Ion%": f"{pdna_ion_ratio:.1f}%",
                "Helper%": f"{pdna_helper_ratio:.1f}%",
                "Chol%": f"{pdna_chol_ratio:.1f}%",
                "PEG%": f"{pdna_peg_ratio:.2f}%",
                "Ion Lipid (μL)": f"{pdna_volumes['Ionizable Lipid']:.2f}",
                "Helper (μL)": f"{pdna_volumes['helper_lipid_volume']:.2f}",
                "Cholesterol (μL)": f"{pdna_volumes['cholesterol_volume']:.2f}",
                "PEG (μL)": f"{pdna_volumes['pegdmg2000_volume']:.2f}",
                "Ethanol (μL)": f"{pdna_volumes['ethanol']:.2f}",
                "Ethanol Phase Total (μL)": f"{pdna_volumes['ethanol_phase_total_volume']:.2f}",
                "250mM Citrate (μL)": f"{pdna_volumes['citrate_volume']:.2f}",
                "Water (μL)": f"{pdna_volumes['water_volume']:.2f}",
                "Nucleic Acid (μL)": f"{pdna_volumes['nucleic_acid_volume']:.2f}",
                "Aqueous Phase Total (μL)": f"{pdna_volumes['aqueous_volume']:.2f}",
                "LNP total (μL)": f"{pdna_volumes['ethanol_phase_total_volume'] + pdna_volumes['aqueous_volume']:.2f}",
            }
         
            st.session_state.pdna_history.append(record)
            st.success(f"✅ pDNA formulation '{record['Name']}' calculated!")
    

        
    # History display
    if len(st.session_state.pdna_history) > 0:
        st.markdown("---")
        st.subheader("📋 pDNA Formulation History")
        history_df = pd.DataFrame(st.session_state.pdna_history)
        
        # Display with full width and scrolling
        st.dataframe(history_df, use_container_width=True, height=300)
        
        # Show Bulk View details option
        with st.expander("📊 Bulk View details"):
            hint = st.info("If you prepare the multiple LNPs with the same ratio between each components, you can use bulk volumes include extra buffer: Lipids and Ethanol x1.5, Aqueous components x1.2")
            bulk_multipliers = {
                "Ion Lipid (μL)": 1.5,
                "Helper (μL)": 1.5,
                "Cholesterol (μL)": 1.5,
                "PEG (μL)": 1.5,
                "Ethanol Master Mix (μL)*1.5": 1.0,
                "Aqueous Master Mix (μL)*1.2": 1.0,
                "Bulk Total (μL)*1.2": 1.0,
                "Ethanol (μL)": 1.5,
                "250mM Citrate (μL)": 1.2,
                "Water (μL)": 1.2,
                "Nucleic Acid (μL)": 1.2,
                "Ethanol Phase Total (μL)": 1.5,
                "Aqueous Phase Total (μL)": 1.2,
            }

            bulk_summary = []
            for column, multiplier in bulk_multipliers.items():
                if column not in history_df:
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
            else:
                st.info("No bulk data available yet.")
        
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            csv_data = history_df.to_csv(index=False)
            st.download_button("📥 Download pDNA History (CSV)", csv_data, file_name="pdna_history.csv", mime="text/csv", key="pdna_download")
        with col_h2:
            if st.button("🗑️ Clear pDNA History", key="pdna_clear"):
                st.session_state.pdna_history = []
                st.rerun()


# ============================================================================
# TAB 2: mRNA FORMULATION
# ============================================================================

with tab_mrna:
    st.header("mRNA LNP Formulation Calculator")
    st.info("Note: This calculator is designed for messenger RNA (mRNA). For mRNA delivery, the citrate buffer concentration is typically 10 mM.")
    
    # Initialize session state for mRNA
    if "mrna_result_df" not in st.session_state:
        st.session_state.mrna_result_df = None
        st.session_state.mrna_volumes = None
        st.session_state.mrna_history = []
    
    # Input section
    st.subheader("📋 mRNA Formulation Parameters")
    
    # Ratio input method selection
    mrna_ratio_mode = st.radio(
        "Select Input Method",
        ["Mass Ratio", "N/P Ratio"],
        index=1,
        horizontal=True,
        key="mrna_ratio_mode",
        help="Choose whether to input Mass Ratio or N/P Ratio"
    )
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        mrna_scale = st.number_input("RNA Scale (μg)", min_value=0.0, step=1.0, value=3.0, key="mrna_scale")
    with col2:
        mrna_stock_conc = st.number_input("RNA Stock (μg/μL)", min_value=0.0, step=0.1, value=1.0, key="mrna_stock")
    with col3:
        if mrna_ratio_mode == "Mass Ratio":
            mrna_ion_rna_ratio = st.number_input("Ionizable Lipid to RNA Mass Ratio", min_value=0.0, step=0.1, value=10.0, key="mrna_ratio")
        else:
            mrna_np_ratio_input = st.number_input("N/P Ratio", min_value=0.0, step=0.5, value=6.0, key="mrna_np_input", help="N/P ratio of 6 is equivalent to Mass Ratio ~10:1 for SM-102")
    with col4:
        mrna_aq_eth_ratio = st.number_input("Aqueous to Ethanol Ratio", min_value=0.0, step=0.1, value=3.0, key="mrna_aq_eth")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        mrna_ion_mw = st.number_input("Ionizable Lipid MW (μg/μmol)", min_value=0.0, step=1.0, value=710.18, key="mrna_ion_mw")
    with col6:
        mrna_helper_mw = st.number_input("Helper Lipid MW (μg/μmol)", min_value=0.0, step=1.0, value=799.15, key="mrna_helper_mw")
    with col7:
        mrna_chol_mw = st.number_input("Cholesterol MW (μg/μmol)", min_value=0.0, step=1.0, value=386.65, key="mrna_chol_mw")
    with col8:
        mrna_peg_mw = st.number_input("PEG-DMG2000 MW (μg/μmol)", min_value=0.0, step=1.0, value=2509.2, key="mrna_peg_mw")

    col9, col10, col11, col12 = st.columns(4)
    with col9:
        mrna_ion_conc = st.number_input("Ionizable Lipid Conc (μg/μL)", min_value=0.0, step=1.0, value=10.0, key="mrna_ion_conc")
    with col10:
        mrna_helper_conc = st.number_input("Helper Lipid Conc (μg/μL)", min_value=0.0, step=1.0, value=10.0, key="mrna_helper_conc")
    with col11:
        mrna_chol_conc = st.number_input("Cholesterol Conc (μg/μL)", min_value=0.0, step=1.0, value=10.0, key="mrna_chol_conc")
    with col12:
        mrna_peg_conc = st.number_input("PEG-DMG2000 Conc (μg/μL)", min_value=0.0, step=1.0, value=10.0, key="mrna_peg_conc")
    
    col13, col14, col15, col16 = st.columns(4)
    with col13:
        mrna_ion_ratio = st.number_input("Ionizable Lipid Molar %", min_value=0.0, step=0.1, value=35.0, key="mrna_ion_ratio")
    with col14:
        mrna_helper_ratio = st.number_input("Helper Lipid Molar %", min_value=0.0, step=0.1, value=16.0, key="mrna_helper_ratio")
    with col15:
        mrna_chol_ratio = st.number_input("Cholesterol Molar %", min_value=0.0, step=0.1, value=46.5, key="mrna_chol_ratio")
    with col16:
        mrna_peg_ratio = st.number_input("PEG-DMG2000 Molar %", min_value=0.0, step=0.1, value=2.5, key="mrna_peg_ratio")
    
    col17, col18 = st.columns(2)
    with col17:
        mrna_bulk_times = st.number_input("Bulk Preparation Times", min_value=1, step=1, value=1, key="mrna_bulk")
    with col18:
        mrna_amines = st.number_input("Amines per Ionizable Lipid", min_value=0.0, step=0.1, value=1.0, key="mrna_amines")
    
    # Calculate Mass Ratio from N/P if needed
    if mrna_ratio_mode == "N/P Ratio":
        # Mass Ratio = (N/P × MW) / (Amines × 330)
        mrna_ion_rna_ratio = (mrna_np_ratio_input * mrna_ion_mw) / (mrna_amines * 330)
        st.info(f"📊 Calculated Mass Ratio: {mrna_ion_rna_ratio:.2f}:1 (from N/P ratio {mrna_np_ratio_input:.2f})")
    
    mrna_name = st.text_input("Formulation Name", value="", placeholder="Enter name for this mRNA formulation", key="mrna_name")
    
    # Calculate button
    if st.button("📊 Calculate mRNA Formulation", key="mrna_calc_btn"):
        if mrna_stock_conc <= 0 or mrna_ion_mw <= 0 or mrna_ion_conc <= 0:
            st.error("All concentrations and MWs must be positive values!")
        else:
            mrna_result_df, mrna_volumes = make_lnp_formulation(
                mrna_scale, mrna_stock_conc, mrna_ion_rna_ratio, mrna_aq_eth_ratio,
                mrna_ion_mw, mrna_helper_mw, mrna_chol_mw, mrna_peg_mw,
                mrna_ion_conc, mrna_helper_conc, mrna_chol_conc, mrna_peg_conc,
                mrna_ion_ratio, mrna_helper_ratio, mrna_chol_ratio, mrna_peg_ratio,
                na_type="mRNA"
            )
            mrna_display_df, mrna_bulk_ethanol, mrna_bulk_aqueous, mrna_bulk_total = append_bulk_summary_rows(
                mrna_result_df, mrna_volumes, mrna_bulk_times
            )
            st.session_state.mrna_result_df = mrna_display_df
            st.session_state.mrna_volumes = mrna_volumes
            
            # Calculate N/P ratio
            np_ratio, n_moles, p_moles = calculate_np_ratio(
                mrna_scale, mrna_volumes["ionizable_lipid_moles"], mrna_amines
            )
            
            # Save to history
            record = {
                "Name": mrna_name if mrna_name else "Unnamed",
                "RNA (μg)": f"{mrna_scale:.2f}",
                "Ion Lipid (μL)": f"{mrna_volumes['Ionizable Lipid']:.2f}",
                "Helper (μL)": f"{mrna_volumes['helper_lipid_volume']:.2f}",
                "Cholesterol (μL)": f"{mrna_volumes['cholesterol_volume']:.2f}",
                "PEG (μL)": f"{mrna_volumes['pegdmg2000_volume']:.2f}",
                "Ethanol (μL)": f"{mrna_volumes['ethanol']:.2f}",
                "Ethanol Phase Total (μL)": f"{mrna_volumes['ethanol_phase_total_volume']:.2f}",
                "10mM Citrate (μL)": f"{mrna_volumes['citrate_volume']:.2f}",
                "Water (μL)": f"{mrna_volumes['water_volume']:.2f}",
                "Nucleic Acid (μL)": f"{mrna_volumes['nucleic_acid_volume']:.2f}",
                "Aqueous Phase Total (μL)": f"{mrna_volumes['aqueous_volume']:.2f}",
                "N/P Ratio": f"{np_ratio:.3f}",
                "Ion:RNA Ratio": format_ratio_label(mrna_ion_rna_ratio),
                "Ion%": f"{mrna_ion_ratio:.1f}%",
                "Helper%": f"{mrna_helper_ratio:.1f}%",
                "Chol%": f"{mrna_chol_ratio:.1f}%",
                "PEG%": f"{mrna_peg_ratio:.2f}%",
                "Target LNP Volume (μL)": f"{mrna_volumes['ethanol_phase_total_volume'] + mrna_volumes['aqueous_volume']:.2f}",
            }
            st.session_state.mrna_history.append(record)
            st.success(f"✅ mRNA formulation '{record['Name']}' calculated!")
    
    # History display
    if len(st.session_state.mrna_history) > 0:
        st.markdown("---")
        st.subheader("📋 mRNA Formulation History")
        history_df = pd.DataFrame(st.session_state.mrna_history)
        
        # Display with full width and scrolling
        st.dataframe(history_df, use_container_width=True, height=300)
        
        # Show Bulk View details option
        with st.expander("📊 Bulk View details"):
            hint = st.info("If you prepare multiple LNPs with the same component ratios, you can use bulk volumes with extra buffer: Lipids and Ethanol x1.5, Aqueous components x1.2")
            bulk_multipliers = {
                "Ion Lipid (μL)": 1.5,
                "Helper (μL)": 1.5,
                "Cholesterol (μL)": 1.5,
                "PEG (μL)": 1.5,
                "Ethanol Master Mix (μL)*1.5": 1.0,
                "Aqueous Master Mix (μL)*1.2": 1.0,
                "Bulk Total (μL)*1.2": 1.0,
                "Ethanol (μL)": 1.5,
                "10mM Citrate (μL)": 1.2,
                "Water (μL)": 1.2,
                "Nucleic Acid (μL)": 1.2,
                "Ethanol Phase Total (μL)": 1.5,
                "Aqueous Phase Total (μL)": 1.2,
            }

            bulk_summary = []
            for column, multiplier in bulk_multipliers.items():
                if column not in history_df:
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
            else:
                st.info("No bulk data available yet.")
        
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            csv_data = history_df.to_csv(index=False)
            st.download_button("📥 Download mRNA History (CSV)", csv_data, file_name="mrna_history.csv", mime="text/csv", key="mrna_download")
        with col_h2:
            if st.button("🗑️ Clear mRNA History", key="mrna_clear"):
                st.session_state.mrna_history = []
                st.rerun()
