import streamlit as st
import pandas as pd
import math
import numpy as np

st.set_page_config(page_title="General Information & Methods", page_icon="🔬", layout="wide")


st.title("🔬 LNP Fundamentals & Operating Protocol")

# ============================================================================
# SECTION 1: INTRODUCTION
# ============================================================================

st.markdown("""
## What are Lipid Nanoparticles (LNPs)?

Lipid nanoparticles (LNPs) are nanoscale delivery vehicles designed to encapsulate and protect nucleic acids 
(such as mRNA or plasmid DNA) for therapeutic applications. LNPs enable efficient cellular uptake and 
intracellular delivery of genetic material while protecting it from degradation by nucleases.

This comprehensive guide covers both the fundamental principles and the standard operating protocol for 
preparing and characterizing high-quality LNP formulations.
""")

st.divider()

# ============================================================================
# SECTION 2: COMPOSITION
# ============================================================================

st.header("📋 LNP Composition & Components")

st.markdown("""
A typical LNP formulation consists of four main lipid components:

1. **Ionizable/Cationic Lipid (40-50 mol%)**: The primary component that complexes with negatively charged 
   nucleic acids through electrostatic interactions. It remains neutral or slightly positive at physiological 
   pH but becomes positively charged at acidic pH to facilitate endosomal escape.

2. **Helper Lipid/Phospholipid (9-15 mol%)**: Usually phosphatidylcholine (e.g., DSPC, DOPE), which 
   provides structural stability and helps form the lipid bilayer.

3. **Cholesterol (38-48 mol%)**: Enhances membrane stability, rigidity, and fusion properties, improving 
   the overall integrity of the nanoparticle.

4. **PEG-Lipid (1-3 mol%)**: Polyethylene glycol (PEG)-conjugated lipid that provides steric stabilization, 
   reduces aggregation, and increases circulation time by minimizing protein adsorption and immune recognition.
""")

st.subheader("FDA-Approved LNP Formulations")
st.markdown("""
| Ionizable Lipid | Ionizable % | Helper % | Cholesterol % | PEG-Lipid % | Carrier Lipid |
|---|---|---|---|---|---|
| **D-Lin-MC3-DMA** | 50% | 10% (DSPC) | 38.5% | 1.5% (DMG-PEG 2000) | mRNA |
| **SM-102** | 50% | 10% (DSPC) | 38.5% | 1.5% (DMG-PEG 2000) | mRNA |
| **ALC-0315** | 46.3% | 9.4% (DSPC) | 42.7% | 1.6% (ALC-0159) | mRNA |

*Note: Formulations vary based on cargo type (mRNA vs pDNA) and therapeutic target*
""")

st.divider()

# ============================================================================
# SECTION 3: DESIGN CONSIDERATIONS FOR pDNA vs mRNA
# ============================================================================

st.header("🧬 Design Considerations: pDNA vs mRNA")

with st.expander("Core Differences and Implications"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **mRNA-LNPs (Cytoplasmic Delivery)**
        - Translates directly in cytoplasm
        - Only needs cytoplasmic release
        - Typical N/P ratio: 3-8
        - Shorter action duration
        - Examples: Comirnaty, Spikevax
        """)
    
    with col2:
        st.markdown("""
        **pDNA-LNPs (Nuclear Delivery)**
        - Must cross nuclear envelope
        - Requires transcription in nucleus
        - Typical N/P ratio: 4-10
        - Longer action duration
        - Additional immune challenges
        - Often requires NOA for STING inhibition
        """)
    
    st.markdown("""
    ### Phosphate Group Calculation
    - **mRNA**: 1 phosphate per nucleotide → P(mol) ≈ mass(g) / 330
    - **dsDNA**: 2 phosphates per base pair → P(mol) ≈ mass(g) / 330
    - Both use same denominator due to base pair MW (~660) vs individual MW (~330)
    """)

st.divider()

# ============================================================================
# SECTION 4: CALCULATION PRINCIPLES
# ============================================================================

st.header("🧮 Calculation Principles")

st.markdown("""
### Molar Calculations

LNP formulations are defined by **molar ratios** of the four lipid components:

**1. Moles Determination:**
- Moles = Mass (g) / Molecular Weight (g/mol)
- For stock solutions: Moles = Concentration (M) × Volume (L)

**2. Molar Percentages:**
- Molar % = (Moles of Component / Total Moles of All Lipids) × 100

**3. N/P Ratio:**
The N/P ratio represents the molar ratio of positively charged amine groups (N) from ionizable lipids to 
negatively charged phosphate groups (P) on nucleic acids:

**N/P = (moles of amine groups) / (moles of phosphate groups)**

**4. Phosphate Calculation:**
- **DNA/RNA**: P (μmol) ≈ mass (μg) × 3.03 × 10⁻³
- Alternatively: P (mol) ≈ mass (g) / 330 g/mol

**5. Volume Calculations:**
- Volume (μL) = [Mass (μg) / Stock Concentration (μg/μL)] 
- Or: Volume (μL) = [Moles (μmol) / Stock Concentration (mM)] × 1000
""")

st.divider()

# ============================================================================
# SECTION 5: FORMULATION PROTOCOL
# ============================================================================

st.header("⚙️ Standard Operating Protocol: LNP Formulation")

st.markdown("""
The LNP formulation process involves careful control of each step to ensure reproducible, high-quality nanoparticles.
""")

with st.expander("Step 1: Preparation of Lipid Phase (Organic Phase)", expanded=True):
    st.markdown("""
    1. **Weigh** individual lipid components according to predetermined molar ratios
    2. **Dissolve** completely in **absolute ethanol** (ACS grade or higher)
    3. **Mix** according to ratios (e.g., 50:10:38.5:1.5 for SM-102:DSPC:Chol:PEG-DMG2K)
    4. **Verify** complete dissolution and homogeneity
    5. **Store** at 2-8°C if not used immediately
    """)

with st.expander("Step 2: Preparation of Aqueous Phase", expanded=True):
    st.markdown("""
    **For pDNA-LNPs:**
    1. Dissolve high-purity **plasmid DNA in Citrate Buffer (50 mM, pH 3.0-4.0)**
    2. Gently mix until fully dissolved (target: e.g., 1 mg/mL)
    3. ⚠️ **Avoid vigorous vortexing** - can fragment large plasmid DNA molecules
    4. Maintain pH 4.0 to ensure ionizable lipids are protonated
    
    **For mRNA-LNPs:**
    1. Dissolve mRNA in **Acetate Buffer (25 mM, pH ~4)**
    2. Keep temperature controlled (2-8°C preferred)
    3. Avoid freeze-thaw cycles if possible
    """)

    st.markdown("""
    Step 2b: Citrate Buffer Preparation (pH 4.0)
    
    For pDNA-LNP formulations, prepare fresh or use pre-made citrate buffer.
    
    Reagents:
    - Sodium citrate dihydrate (Na3C6H5O7·2H2O)
    - Citric acid (C6H8O7)
    - Ultrapure water (RNase/DNase free)
    
    Stock Solution Preparation (0.5 M, pH 4.0):
    1. Dissolve 14.7 g sodium citrate dihydrate in 80-90 mL water
    2. Titrate with 1 M citric acid slowly to pH 4.0
    3. Bring to 100 mL total volume
    4. Filter sterilize through 0.22 μm filter
    5. Store at room temperature (≤6 months) or 4°C (≤1 year)
    
    Working Solution (50 mM, pH 4.0):
    - Dilute 1:9 ratio (stock:water)
    - Example: 20 mL of 0.5 M stock + 180 mL sterile water = 100 mL
    - Final pH typically 4.0 ± 0.2 (minimal adjustment needed)
    - Use immediately or store at 4°C for up to 1 week
    """)

with st.expander("Step 3: Nanoparticle Assembly via Rapid Mixing", expanded=True):
    tab1, tab2 = st.tabs(["Manual Rapid Injection", "Microfluidic Mixing"])
    
    with tab1:
        st.markdown("""
        **Procedure:**
        1. Draw lipid-ethanol solution into syringe
        2. **Rapidly inject** into stirring aqueous solution
        3. **Shake or pipette vigorously** for 10-30 seconds
        4. **Incubate** for 10 minutes at room temperature
        
        **Advantages:** Simple, low equipment cost  
        **Disadvantages:** Higher batch-to-batch variability, less reproducible
        """)
    
    with tab2:
        st.markdown("""
        **Procedure:**
        1. Load phases into syringes on syringe pumps
        2. Set **Flow Rate Ratio (FRR)**: typically 3:1 (aqueous:ethanol)
        3. Set **Total Flow Rate (TFR)**: e.g., 10-12 mL/min
        4. Infuse through microfluidic chip
        5. Discard first/last drops, collect main product
        
        **Advantages:** Superior control, narrow size distribution, high reproducibility  
        **Disadvantages:** Requires specialized equipment  
        **Recommended for:** Therapeutic development and regulatory submissions
        """)

with st.expander("Step 4: Downstream Processing & Purification", expanded=True):
    st.markdown("""
    **4.1 Dialysis (Buffer Exchange)**
    - Transfer to dialysis cassette (20-100 kDa MWCO)
    - Dialyze against **1× PBS (pH 7.4)** for ≥2 hours
    - Change buffer 1-2 times
    - **Purpose**: Remove ethanol + neutralize pH to 7.4 (reduces toxicity)
    
    **4.2 Sterilization**
    - Filter through **0.22 μm sterile filter**
    - **Mandatory** for in vitro/in vivo applications
    - Removes particulates and microorganisms
    
    **4.3 Concentration** (if needed)
    - Use centrifugal ultrafiltration devices
    - Achieve desired target concentration
    - Minimize mechanical stress during concentration
    """)

with st.expander("Step 5: Quality Control & Characterization", expanded=True):
    qc_data = {
        "Parameter": [
            "Size & Polydispersity",
            "Surface Charge",
            "pDNA Encapsulation",
            "Surface Ionization (pKa)",
            "Morphology"
        ],
        "Technique": [
            "Dynamic Light Scattering (DLS)",
            "Zeta Potential",
            "RiboGreen Assay",
            "TNS Fluorescence Assay",
            "TEM/Cryo-EM"
        ],
        "Target Specification": [
            "30-150 nm, PDI <0.2",
            "±15 mV typical",
            "80-95% encapsulation",
            "pKa 6.0-7.0",
            "Spherical, homogeneous"
        ]
    }
    st.table(pd.DataFrame(qc_data))

st.divider()

# ============================================================================
# SECTION 6: SAFETY & OPTIMIZATION
# ============================================================================

st.header("🛡️ Safety Considerations for pDNA-LNPs")

with st.expander("Addressing Innate Immune Activation", expanded=True):
    st.markdown("""
    **Challenge:** pDNA-LNPs trigger acute inflammation via cGAS-STING pathway activation
    - Massive cytokine release (IFN-β, IL-6, TNF-α)
    - Can lead to systemic toxicity and lethality at high doses
    
    **Solution: Incorporate Nitro-Oleic Acid (NOA)**
    - STING pathway inhibitor naturally present in oxidized lipids
    - **Optimal ratio**: 0.2-0.8 mole ratio of NOA:Total Lipids
    - **Effect**: Suppresses cytokine storm by 80-90%
    - **Result**: Transforms lethal formulations (1 mg/kg) into viable therapeutic candidates
    
    ⚠️ **Critical for Clinical Translation** of pDNA-LNP therapies
    """)

with st.expander("Physical Enhancement Methods for Improved Delivery", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Sonoporation (Ultrasound Enhancement)**
        - Uses therapeutic ultrasound (1 MHz, 2 W·cm⁻²)
        - Co-administered microbubbles create cavitation bubbles
        - Transient membrane pores allow LNP entry
        - **Application**: In vivo tissue-targeted delivery
        """)
    
    with col2:
        st.markdown("""
        **Electroporation**
        - Applies short, intense electric pulses
        - Transiently permeabilizes cell membrane
        - High-efficiency LNP uptake (80-95%)
        - **Application**: Ex vivo cell modification
        """)

with st.expander("Storage and Handling Guidelines", expanded=True):
    st.markdown("""
    📦 **Storage Conditions**
    - Temperature: 2-8°C (refrigerated)
    - Container: Glass vials with nitrogen headspace
    - Light protection: Store in amber bottles
    
    ⏱️ **Shelf Life**
    - At 2-8°C: 3-6 months (typical)
    - Depends on formulation stability and payload
    
    🧊 **Long-Term Storage**
    - Lyophilization + cryopreservation for extended storage
    - Stabilizers (trehalose, sucrose) recommended
    - Reconstitute by gentle resuspension before use
    
    ⚠️ **Handling Precautions**
    - Avoid freeze-thaw cycles (causes aggregation)
    - Minimize exposure to light and oxygen
    - Keep sterile until use
    """)

st.divider()

# ============================================================================
# SECTION 7: SURFACE MODIFICATION
# ============================================================================

st.header("🎯 Surface Modification for Targeted Delivery")

with st.expander("Ligand-Mediated Targeting"):
    st.markdown("""
    ### Targeting Strategies
    
    Surface modification with targeting ligands enhances therapeutic potential by improving tissue specificity:
    
    **1. Folate Receptor Targeting**
    - Folate-conjugated PEGylated lipids on surface
    - Binds to folate receptor (FR) on cancer cells
    - **Use case**: Ovarian cancer, breast cancer
    
    **2. Antibody-Mediated Targeting**
    - Herceptin (trastuzumab) for HER2+ tumors
    - Anti-CD33 for acute myeloid leukemia
    - **Method**: Thiol-maleimide conjugation to PEG-lipid
    
    **3. Peptide Targeting**
    - RGD peptides for integrin-expressing tumors
    - Transferrin for iron metabolism-dependent cells
    - **Method**: Click chemistry or direct conjugation
    """)

with st.expander("Conjugation Chemistries"):
    linkage_data = {
        "Method": [
            "Avidin-Biotin",
            "Electrostatic Bonds",
            "Disulfide Bonds",
            "Maleimide-Thiol",
            "SPAAC (Azide-DBCO)"
        ],
        "Stability": [
            "Very stable (non-covalent)",
            "pH/salt dependent",
            "Reversible in reducing environment",
            "Stable covalent",
            "Highly stable covalent"
        ],
        "Application": [
            "High-affinity targeting",
            "Ligand attachment",
            "Intracellular release",
            "Cancer targeting",
            "Bioorthogonal coupling"
        ]
    }
    st.table(pd.DataFrame(linkage_data))

st.divider()

# ============================================================================
# SECTION 8: CALCULATORS
# ============================================================================

st.header("🧮 Interactive LNP Calculators")

tab_calc1, tab_calc2, tab_calc3 = st.tabs(["N/P Ratio", "Volume Calculator", "Recipe Generator"])

# TAB 1: N/P RATIO CALCULATOR
with tab_calc1:
    st.subheader("N/P Ratio Calculator")
    st.markdown("Calculate N/P ratio from nucleic acid mass and ionizable lipid parameters.")
    
    # Input mode selector
    input_mode = st.radio("Lipid Input Method", ["Direct Moles (μmol)", "Mass + MW"], horizontal=True)
    
    with st.form("np_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Nucleic Acid**")
            na_type = st.selectbox("Type", ["pDNA (dsDNA)", "mRNA (ssRNA)"])
            na_mass_ug = st.number_input("Mass (μg)", value=3.0, min_value=0.1, step=1.0, help="Nucleic acid mass in micrograms")
        
        with col2:
            st.markdown("**Ionizable Lipid**")
            if input_mode == "Direct Moles (μmol)":
                lipid_umol = st.number_input("Lipid amount (μmol)", value=0.0423, min_value=0.0001, step=0.001, format="%.4f", help="Direct input of ionizable lipid moles")
            else:
                lipid_mass_ug = st.number_input("Lipid mass (μg)", value=30.0, min_value=0.1, step=1.0, help="Ionizable lipid mass in micrograms")
                lipid_mw = st.number_input("Molecular weight (μg/μmol)", value=710.18, min_value=100.0, step=10.0, help="MW of ionizable lipid (e.g., SM-102: 710.18)")
            
            amines_per_mol = st.number_input("Amines per molecule", value=1.0, min_value=1.0, step=1.0, help="Number of ionizable amine groups per lipid")
        
        submit_np = st.form_submit_button("📊 Calculate N/P Ratio")
    
    if submit_np:
        # Calculate lipid moles if mass+MW mode
        if input_mode == "Mass + MW":
            # Convert μg to μmol using MW (μg/μmol)
            lipid_umol = lipid_mass_ug / lipid_mw
        
        # Phosphate calculation (matching page 2 logic)
        # P (μmol) = mass(μg) × 10^-6 (to g) / 330 (g/mol) × 10^6 (to μmol)
        # Simplified: P (μmol) = mass(μg) / 330
        nucleic_acid_mass_g = na_mass_ug * 1e-6
        phosphate_moles_mol = nucleic_acid_mass_g / 330.0
        P_umol = phosphate_moles_mol * 1e6
        
        # Nitrogen calculation
        N_umol = lipid_umol * amines_per_mol
        
        # N/P ratio
        np_ratio = N_umol / P_umol if P_umol > 0 else 0
        
        st.markdown("---")
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("N/P Ratio", f"{np_ratio:.2f}", help="Molar ratio of amine groups to phosphate groups")
        with col_res2:
            st.metric("N (Nitrogen, μmol)", f"{N_umol:.4f}", help="Total amine groups from ionizable lipid")
        with col_res3:
            st.metric("P (Phosphate, μmol)", f"{P_umol:.4f}", help="Total phosphate groups from nucleic acid")
        
        # Detailed calculation breakdown
        with st.expander("📝 Calculation Details"):
            st.markdown(f"""
            **Nucleic Acid:** {na_type}
            - Mass: {na_mass_ug} μg
            - Conversion: {na_mass_ug} μg × 10⁻⁶ = {nucleic_acid_mass_g:.6f} g
            - Phosphate moles: {nucleic_acid_mass_g:.6f} g ÷ 330 g/mol = {phosphate_moles_mol:.9f} mol
            - Phosphate moles: {phosphate_moles_mol:.9f} mol × 10⁶ = **{P_umol:.4f} μmol**
            
            **Ionizable Lipid:**
            """)
            if input_mode == "Mass + MW":
                st.markdown(f"""
                - Mass: {lipid_mass_ug} μg
                - Molecular weight: {lipid_mw} μg/μmol
                - Lipid moles: {lipid_mass_ug} μg ÷ {lipid_mw} μg/μmol = **{lipid_umol:.4f} μmol**
                - Amines per molecule: {amines_per_mol}
                - Nitrogen moles: {lipid_umol:.4f} μmol × {amines_per_mol} = **{N_umol:.4f} μmol**
                """)
            else:
                st.markdown(f"""
                - Lipid moles: {lipid_umol:.4f} μmol
                - Amines per molecule: {amines_per_mol}
                - Nitrogen moles: {lipid_umol:.4f} μmol × {amines_per_mol} = **{N_umol:.4f} μmol**
                """)
            
            st.markdown(f"""
            **N/P Ratio = {N_umol:.4f} ÷ {P_umol:.4f} = {np_ratio:.2f}**
            """)
            
            # Interpretation
            if na_type == "pDNA (dsDNA)":
                if 4 <= np_ratio <= 10:
                    st.success(f"✅ N/P ratio {np_ratio:.2f} is within typical pDNA range (4-10)")
                else:
                    st.warning(f"⚠️ N/P ratio {np_ratio:.2f} is outside typical pDNA range (4-10)")
            else:  # mRNA
                if 3 <= np_ratio <= 8:
                    st.success(f"✅ N/P ratio {np_ratio:.2f} is within typical mRNA range (3-8)")
                else:
                    st.warning(f"⚠️ N/P ratio {np_ratio:.2f} is outside typical mRNA range (3-8)")

# TAB 2: VOLUME CALCULATOR
with tab_calc2:
    st.subheader("Required Volume for Target N/P")
    st.markdown("Calculate required lipid volume to achieve target N/P ratio.")
    
    with st.form("vol_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            target_np = st.number_input("Target N/P", value=5.0, min_value=1.0, step=0.5)
            dna_mass_t = st.number_input("DNA mass (μg)", value=100.0, min_value=1.0, step=10.0)
        
        with col2:
            stock_mM_t = st.number_input("Stock concentration (mM)", value=100.0, min_value=1.0, step=10.0)
            amines_t = st.number_input("Amines per molecule", value=1.0, min_value=0.5, step=0.5)
        
        submit_vol = st.form_submit_button("Calculate Volume")
    
    if submit_vol:
        P_mol_t = (dna_mass_t * 1e-6) / 330.0
        N_needed = target_np * P_mol_t
        V_L = N_needed / ((stock_mM_t * 1e-3) * amines_t)
        V_uL = V_L * 1e6
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Required Volume (μL)", f"{V_uL:.2f}")
        with col_res2:
            st.metric("Phosphate Moles (μmol)", f"{P_mol_t*1e6:.2f}")

# TAB 3: RECIPE GENERATOR
with tab_calc3:
    st.subheader("LNP Formulation Recipe Generator")
    st.markdown("Generate complete pipetting recipe based on target DNA mass and N/P ratio.")
    
    with st.form("recipe_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Target Parameters**")
            pdna_mass = st.number_input("pDNA required (μg)", value=100.0, min_value=0.0, step=0.1)
            target_np_r = st.number_input("N/P Ratio", value=4.0, min_value=1.0, step=1.0)
        
        with col2:
            st.markdown("**Molar Ratios (%)**")
            mol_ion = st.number_input("Ionizable %", value=50.0, min_value=5.0, max_value=70.0, step=1.0)
            mol_chol = st.number_input("Cholesterol %", value=38.5, min_value=15.0, max_value=50.0, step=0.5)
            mol_helper = st.number_input("Helper %", value=10.0, min_value=5.0, max_value=50.0, step=0.5)
            mol_peg = st.number_input("PEG %", value=1.5, min_value=0.5, max_value=5.0, step=0.1)
        
        with col3:
            st.markdown("**Stock Concentrations (mg/mL)**")
            c_ion = st.number_input("Ion stock", value=10.0, min_value=1.0, step=0.5)
            c_chol = st.number_input("Chol stock", value=10.0, min_value=1.0, step=0.5)
            c_helper = st.number_input("Helper stock", value=10.0, min_value=1.0, step=0.5)
            c_peg = st.number_input("PEG stock", value=5.0, min_value=1.0, step=0.1)
        
        submit_recipe = st.form_submit_button("Generate Recipe")
    
    if submit_recipe:
        # Molecular weights (g/mol converted to mg/μmol)
        mw_ion, mw_chol, mw_helper, mw_peg = 710.17, 386.65, 790.15, 2507.64
        
        # Check molar percentages sum to 100
        total_mol = mol_ion + mol_chol + mol_helper + mol_peg
        
        if abs(total_mol - 100.0) > 0.1:
            st.error(f"Molar percentages sum to {total_mol:.1f}%. Must equal 100%!")
        else:
            # Calculate phosphate moles
            P_mol_r = (pdna_mass * 1e-6) / 330.0
            
            # Calculate ionizable lipid moles needed
            N_mol_r = target_np_r * P_mol_r
            moles_ion = N_mol_r / 1.0  # Assuming 1 amine per molecule
            
            # Total moles from ionizable lipid percentage
            total_moles = moles_ion / (mol_ion / 100.0)
            
            # Calculate masses
            mass_ion = (total_moles * (mol_ion/100.0) * mw_ion) * 1e6  # to μg
            mass_chol = (total_moles * (mol_chol/100.0) * mw_chol) * 1e6
            mass_helper = (total_moles * (mol_helper/100.0) * mw_helper) * 1e6
            mass_peg = (total_moles * (mol_peg/100.0) * mw_peg) * 1e6
            
            # Calculate volumes
            vol_ion = (mass_ion / c_ion)
            vol_chol = (mass_chol / c_chol)
            vol_helper = (mass_helper / c_helper)
            vol_peg = (mass_peg / c_peg)
            
            # Display recipe
            recipe_df = pd.DataFrame({
                "Component": ["Ionizable Lipid", "Cholesterol", "Helper Lipid", "PEG Lipid"],
                "Mass (μg)": [f"{mass_ion:.2f}", f"{mass_chol:.2f}", f"{mass_helper:.2f}", f"{mass_peg:.2f}"],
                "Stock (mg/mL)": [c_ion, c_chol, c_helper, c_peg],
                "Volume (μL)": [f"{vol_ion:.2f}", f"{vol_chol:.2f}", f"{vol_helper:.2f}", f"{vol_peg:.2f}"]
            })
            
            st.success("✅ Recipe Generated!")
            st.dataframe(recipe_df, use_container_width=True)
            
            total_lipid_vol = vol_ion + vol_chol + vol_helper + vol_peg
            st.markdown(f"""
            ### Preparation Steps:
            1. **Mix lipids in ethanol**: Combine {total_lipid_vol:.1f} μL of lipid stock solutions
            2. **Prepare aqueous phase**: Dissolve {pdna_mass:.0f} μg pDNA in Citrate buffer pH 4.0-4.5
            3. **Rapid mixing**: Mix lipid phase into aqueous phase at 3:1 ratio (aqueous:organic)
            4. **Incubation**: Allow 10 minutes at room temperature for self-assembly
            5. **Dialysis**: Transfer to dialysis cassette, dialyze against PBS pH 7.4 for ≥2 hours
            """)

st.divider()

# ============================================================================
# SECTION 9: TIPS & REFERENCES
# ============================================================================

st.header("💡 Best Practices & Tips")

st.markdown("""
✅ **Do:**
- Use fresh, high-purity lipids (avoid oxidized stocks)
- Maintain strict sterile technique for therapeutic applications
- Document all batch parameters (ratios, flow rates, times)
- Characterize each batch thoroughly (size, PDI, zeta potential)
- Store at 2-8°C in nitrogen-sealed vials
- Optimize N/P ratio systematically for your specific cargo

❌ **Don't:**
- Vigorous vortex during aqueous phase preparation (breaks DNA)
- Freeze-thaw LNP suspensions (causes aggregation)
- Exceed 25°C during formulation
- Skip dialysis (ethanol toxicity)
- Mix lipids at room temperature for extended periods
""")

st.divider()

st.info("""
**📚 Key References:**
- Gilleron et al. (2013) "Image-based analysis of complex fluids in microfluidic systems"
- Pardi et al. (2018) "mRNA vaccines — a new era in vaccinology"
- Akinc et al. (2019) "The Onpattro story and the clinical translation of nanomedicines"
- Witzigmann et al. (2022) "Lipid nanoparticles for gene therapy and immunotherapy"
""")
