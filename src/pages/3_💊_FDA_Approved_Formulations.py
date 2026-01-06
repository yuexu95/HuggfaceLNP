import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("💊 FDA-Approved LNP Formulations")

# ============================================================================
# SHARED FUNCTIONS
# ============================================================================

def calculate_np_ratio(nucleic_acid_mass_ug, ionizable_lipid_moles, amines_per_molecule=1.0):
    """Calculates the N/P ratio for LNP formulation."""
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

def get_fda_formulations():
    """Returns FDA-approved LNP formulations with preset parameters."""
    formulations = {
        "D-Lin-MC3-DMA (Onpattro)": {
            "name": "D-Lin-MC3-DMA",
            "full_name": "D-Lin-MC3-DMA (Onpattro - Alnylam)",
            "ionizable_lipid": "D-Lin-MC3-DMA",
            "ion_mw": 642.1,
            "ion_ratio": 50.0,
            "helper_lipid": "DSPC",
            "helper_mw": 790.147,
            "helper_ratio": 10.0,
            "cholesterol": "Cholesterol",
            "chol_mw": 386.654,
            "chol_ratio": 38.5,
            "peg_lipid": "DMG-PEG 2000",
            "peg_mw": 2509.2,
            "peg_ratio": 1.5,
            "np_ratio": 6.0,
            "mass_ratio": 11.5,
            "description": "First FDA-approved RNAi therapeutic for hereditary transthyretin amyloidosis"
        },
        "SM-102 (Moderna)": {
            "name": "SM-102",
            "full_name": "SM-102 (Spikevax - Moderna)",
            "ionizable_lipid": "SM-102",
            "ion_mw": 710.182,
            "ion_ratio": 50.0,
            "helper_lipid": "DSPC",
            "helper_mw": 790.147,
            "helper_ratio": 10.0,
            "cholesterol": "Cholesterol",
            "chol_mw": 386.654,
            "chol_ratio": 38.5,
            "peg_lipid": "DMG-PEG 2000",
            "peg_mw": 2509.2,
            "peg_ratio": 1.5,
            "np_ratio": 6.0,
            "mass_ratio": 13.0,
            "description": "Moderna COVID-19 mRNA vaccine formulation"
        },
        "ALC-0315 (Pfizer-BioNTech)": {
            "name": "ALC-0315",
            "full_name": "ALC-0315 (Comirnaty - Pfizer-BioNTech)",
            "ionizable_lipid": "ALC-0315",
            "ion_mw": 766.0,
            "ion_ratio": 46.3,
            "helper_lipid": "DSPC",
            "helper_mw": 790.147,
            "helper_ratio": 9.4,
            "cholesterol": "Cholesterol",
            "chol_mw": 386.654,
            "chol_ratio": 42.7,
            "peg_lipid": "ALC-0159",
            "peg_mw": 2332.0,
            "peg_ratio": 1.6,
            "np_ratio": 6.0,
            "mass_ratio": 14.0,
            "description": "Pfizer-BioNTech COVID-19 mRNA vaccine formulation"
        }
    }
    return formulations

def make_lnp_formulation(
    nucleic_acid_scale, nucleic_acid_stock_concentration, ionizable_lipid_to_na_ratio, 
    aqueous_to_ethanol_ratio, ionizable_lipid_mw, helper_lipid_mw, cholesterol_mw, 
    pegdmg2000_mw, ionizable_lipid_concentration, helper_lipid_concentration, 
    cholesterol_concentration, pegdmg2000_concentration, ionizable_lipid_ratio, 
    helper_lipid_ratio, cholesterol_ratio, pegdmg2000_ratio, na_type="mRNA"
):
    """Calculates the composition and prepares an LNP formulation."""
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
        'Component': ['Ionizable Lipid', 'Helper Lipid', 'Cholesterol', 'PEG-Lipid', 'Ethanol', na_label, 'Citrate Buffer', 'Water'],
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

# ============================================================================
# MAIN INTERFACE
# ============================================================================

st.info("💡 **Quick Start**: Select an FDA-approved formulation below and enter your RNA/DNA amount. All other parameters are pre-configured with clinically validated values.")

# Get FDA formulations
fda_formulations = get_fda_formulations()

# Formulation selection
selected_formulation = st.selectbox(
    "🔬 Select FDA-Approved Formulation",
    options=list(fda_formulations.keys()),
    help="Choose from FDA-approved LNP formulations"
)

preset = fda_formulations[selected_formulation]

# Lipid option libraries
helper_lipid_options = {
    "DSPC": {"name": "DSPC (Distearoylphosphatidylcholine)", "mw": 790.147},
    "DOPE": {"name": "DOPE (Dioleoylphosphatidylethanolamine)", "mw": 744.034},
    "DOTAP": {"name": "DOTAP (1,2-dioleoyl-3-trimethylammonium-propane)", "mw": 698.542}
}

cholesterol_options = {
    "Cholesterol": {"name": "Cholesterol", "mw": 386.654},
    "Cho-Arg": {"name": "Cho-Arg (trifluoroacetate salt)", "mw": 884.1},
    "β-Sitosterol": {"name": "β-Sitosterol (Plant sterol)", "mw": 414.71}
}

# Current ratios from session (defaults: N/P=6, amines=1)
np_ratio_state = float(st.session_state.get("fda_np_ratio", 6.0))
amines_state = float(st.session_state.get("fda_amines", 1.0))
mass_ratio_state = (np_ratio_state * preset['ion_mw']) / (amines_state * 330)

# Respect previously selected lipid types if present
selected_helper_key = st.session_state.get(
    "fda_helper_type", preset['helper_lipid'] if preset['helper_lipid'] in helper_lipid_options else "DSPC"
)
selected_chol_key = st.session_state.get(
    "fda_chol_type", preset['cholesterol'] if preset['cholesterol'] in cholesterol_options else "Cholesterol"
)

helper_mw_display = helper_lipid_options.get(selected_helper_key, {}).get("mw", preset['helper_mw'])
chol_mw_display = cholesterol_options.get(selected_chol_key, {}).get("mw", preset['chol_mw'])

# Display formulation information
st.markdown(f"### 📋 {preset['full_name']}")
st.caption(preset['description'])

# Show formulation details in an expandable section
with st.expander("📊 View Complete Formulation Details", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Lipid Composition:**")
        composition_data = pd.DataFrame({
            "Component": ["Ionizable Lipid", "Helper Lipid", "Cholesterol", "PEG-Lipid"],
            "Type": [
                preset['ionizable_lipid'],
                helper_lipid_options.get(selected_helper_key, {}).get("name", preset['helper_lipid']),
                cholesterol_options.get(selected_chol_key, {}).get("name", preset['cholesterol']),
                preset['peg_lipid']
            ],
            "Molar %": [f"{preset['ion_ratio']}%", f"{preset['helper_ratio']}%", f"{preset['chol_ratio']}%", f"{preset['peg_ratio']}%"],
            "MW (g/mol)": [preset['ion_mw'], helper_mw_display, chol_mw_display, preset['peg_mw']]
        })
        st.dataframe(composition_data, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**Default Parameters:**")
        params_data = pd.DataFrame({
            "Parameter": ["N/P Ratio", "Mass Ratio", "Aqueous:Ethanol", "Total Molar %"],
            "Value": [np_ratio_state, f"{mass_ratio_state:.2f}:1", "3:1", "100%"]
        })
        st.dataframe(params_data, use_container_width=True, hide_index=True)

st.markdown("---")

# Initialize session state
if "fda_result_df" not in st.session_state:
    st.session_state.fda_result_df = None
    st.session_state.fda_volumes = None
    st.session_state.fda_history = []

# User inputs
st.subheader("⚙️ Formulation Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    rna_scale = st.number_input(
        "RNA/DNA Amount (μg)", 
        min_value=0.1, 
        step=0.5, 
        value=5.0, 
        key="fda_rna_scale",
        help="Amount of RNA/DNA to be formulated"
    )

with col2:
    rna_stock_conc = st.number_input(
        "RNA/DNA Stock Conc (μg/μL)", 
        min_value=0.1, 
        step=0.1, 
        value=1.0, 
        key="fda_rna_stock",
        help="Concentration of your nucleic acid stock solution"
    )

with col3:
    np_options = list(range(3, 11))
    np_default = int(st.session_state.get("fda_np_ratio", 6))
    np_default = np_default if np_default in np_options else 6
    np_ratio_input = st.selectbox(
        "N/P Ratio",
        options=np_options,
        index=np_options.index(np_default),
        key="fda_np_ratio",
        help="Nitrogen to Phosphate molar ratio; defaults to 6 and allows 3-10"
    )

# Advanced options (collapsible)
with st.expander("🔧 Advanced Options"):
    st.caption("These parameters have validated default values. Modify only if needed.")
    
    # Lipid type selections
    st.markdown("**Lipid Component Selection:**")
    col_lipid1, col_lipid2 = st.columns(2)
    
    with col_lipid1:
        # Find default helper lipid
        default_helper = selected_helper_key if selected_helper_key in helper_lipid_options else "DSPC"
        selected_helper = st.selectbox(
            "Helper Lipid Type",
            options=list(helper_lipid_options.keys()),
            index=list(helper_lipid_options.keys()).index(default_helper),
            format_func=lambda x: helper_lipid_options[x]["name"],
            key="fda_helper_type",
            help="Select the helper/structural lipid type"
        )
        helper_mw_custom = helper_lipid_options[selected_helper]["mw"]
    
    with col_lipid2:
        # Find default cholesterol
        default_chol = selected_chol_key if selected_chol_key in cholesterol_options else "Cholesterol"
        selected_chol = st.selectbox(
            "Cholesterol Type",
            options=list(cholesterol_options.keys()),
            index=list(cholesterol_options.keys()).index(default_chol),
            format_func=lambda x: cholesterol_options[x]["name"],
            key="fda_chol_type",
            help="Select the cholesterol/sterol type"
        )
        chol_mw_custom = cholesterol_options[selected_chol]["mw"]
    
    st.markdown("**Lipid Concentrations:**")
    col4, col5, col6, col7 = st.columns(4)
    
    with col4:
        ion_conc = st.number_input(
            "Ionizable Lipid Conc (μg/μL)", 
            min_value=1.0, 
            step=1.0, 
            value=40.0, 
            key="fda_ion_conc"
        )
    
    with col5:
        helper_conc = st.number_input(
            "Helper Lipid Conc (μg/μL)", 
            min_value=1.0, 
            step=1.0, 
            value=10.0, 
            key="fda_helper_conc"
        )
    
    with col6:
        # Set default cholesterol concentration based on type
        chol_default_conc = 20.0 if selected_chol == "Cho-Arg" else 10.0
        chol_conc = st.number_input(
            "Cholesterol Conc (μg/μL)", 
            min_value=1.0, 
            step=1.0, 
            value=chol_default_conc, 
            key="fda_chol_conc"
        )
    
    with col7:
        peg_conc = st.number_input(
            "PEG-Lipid Conc (μg/μL)", 
            min_value=1.0, 
            step=1.0, 
            value=10.0, 
            key="fda_peg_conc"
        )
    
    col8, col9 = st.columns(2)
    
    with col8:
        aq_eth_ratio = st.number_input(
            "Aqueous:Ethanol Ratio", 
            min_value=1.0, 
            step=0.5, 
            value=3.0, 
            key="fda_aq_eth"
        )
    
    with col9:
        amines = st.number_input(
            "Amines per Lipid", 
            min_value=0.5, 
            step=0.5, 
            value=1.0, 
            key="fda_amines"
        )

formulation_name = st.text_input(
    "Formulation Name (Optional)", 
    value="", 
    placeholder=f"e.g., {preset['name']} Batch 001", 
    key="fda_name"
)

# Calculate button
if st.button("🧪 Calculate Formulation", type="primary", key="fda_calc_btn", use_container_width=True):
    if rna_stock_conc <= 0:
        st.error("⚠️ Stock concentration must be positive!")
    else:
        # Calculate mass ratio from N/P ratio
        mass_ratio = (np_ratio_input * preset['ion_mw']) / (amines * 330)
        
        # Perform calculation (use custom MW if selected in advanced options)
        result_df, volumes = make_lnp_formulation(
            rna_scale, rna_stock_conc, mass_ratio, aq_eth_ratio,
            preset['ion_mw'], helper_mw_custom, chol_mw_custom, preset['peg_mw'],
            ion_conc, helper_conc, chol_conc, peg_conc,
            preset['ion_ratio'], preset['helper_ratio'], preset['chol_ratio'], preset['peg_ratio'],
            na_type="RNA/DNA"
        )
        
        st.session_state.fda_result_df = result_df
        st.session_state.fda_volumes = volumes
        
        # Calculate actual N/P ratio
        actual_np, n_moles, p_moles = calculate_np_ratio(
            rna_scale, volumes["ionizable_lipid_moles"], amines
        )
        
        # Display results
        st.success(f"✅ Formulation calculated successfully!")
        
        st.markdown("### 📊 Formulation Recipe")
        
        col_res1, col_res2 = st.columns([2, 1])
        
        with col_res1:
            st.dataframe(result_df.style.format({"Volume (μL)": "{:.2f}"}), use_container_width=True, hide_index=True)
        
        with col_res2:
            st.markdown("**Summary:**")
            st.metric("Total LNP Volume", f"{volumes['ethanol_phase_total_volume'] + volumes['aqueous_volume']:.2f} μL")
            st.metric("Ethanol Phase", f"{volumes['ethanol_phase_total_volume']:.2f} μL")
            st.metric("Aqueous Phase", f"{volumes['aqueous_volume']:.2f} μL")
            st.metric("Actual N/P Ratio", f"{actual_np:.2f}")
            st.metric("Mass Ratio", f"{mass_ratio:.2f}:1")
        
        # Save to history
        record = {
            "Date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            "Formulation": preset['name'],
            "Name": formulation_name if formulation_name else "Unnamed",
            "Helper Type": helper_lipid_options[selected_helper]["name"],
            "Cholesterol Type": cholesterol_options[selected_chol]["name"],
            "RNA/DNA (μg)": f"{rna_scale:.2f}",
            "N/P Ratio": f"{actual_np:.2f}",
            "Mass Ratio": f"{mass_ratio:.2f}:1",
            "Total Volume (μL)": f"{volumes['ethanol_phase_total_volume'] + volumes['aqueous_volume']:.2f}",
            "Ion Lipid (μL)": f"{volumes['Ionizable Lipid']:.2f}",
            "Helper (μL)": f"{volumes['helper_lipid_volume']:.2f}",
            "Cholesterol (μL)": f"{volumes['cholesterol_volume']:.2f}",
            "PEG (μL)": f"{volumes['pegdmg2000_volume']:.2f}",
            "Ethanol (μL)": f"{volumes['ethanol']:.2f}",
            "RNA/DNA (μL)": f"{volumes['nucleic_acid_volume']:.2f}",
            "Citrate (μL)": f"{volumes['citrate_volume']:.2f}",
            "Water (μL)": f"{volumes['water_volume']:.2f}",
        }
        
        st.session_state.fda_history.append(record)
        
        # Download recipe
        st.download_button(
            label="📥 Download Recipe (CSV)",
            data=result_df.to_csv(index=False),
            file_name=f"{preset['name']}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# History section
if len(st.session_state.fda_history) > 0:
    st.markdown("---")
    st.subheader("📚 Formulation History")
    
    history_df = pd.DataFrame(st.session_state.fda_history)
    st.dataframe(history_df, use_container_width=True, height=300)
    
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        csv_data = history_df.to_csv(index=False)
        st.download_button(
            "📥 Download History (CSV)", 
            csv_data, 
            file_name=f"FDA_LNP_history_{pd.Timestamp.now().strftime('%Y%m%d')}.csv", 
            mime="text/csv",
            use_container_width=True
        )
    
    with col_h2:
        if st.button("🗑️ Clear History", key="fda_clear", use_container_width=True):
            st.session_state.fda_history = []
            st.rerun()

# Footer
st.markdown("---")
st.caption("⚠️ **Note:** These formulations are based on publicly available information about FDA-approved products. Actual manufacturing processes may vary. Always follow GMP guidelines and regulatory requirements for therapeutic production.")
