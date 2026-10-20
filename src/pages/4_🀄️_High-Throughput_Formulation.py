import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import itertools
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="LNP-Flow: Professional DOE Designer", page_icon="🀄", layout="wide")

st.title("🀄 LNP-Flow: Professional DOE Designer")
st.markdown("""
Design, optimize, and generate lab-ready run sheets for multi-component LNP formulations using 
professional Design of Experiments (DOE) principles based on systematic workflow:
**Planning → Screening → Optimization → Verification**
""")

st.markdown("---")

# ============================================================================
# DOE WORKFLOW MANAGEMENT
# ============================================================================

# Initialize DOE workflow stages
if "doe_stage" not in st.session_state:
    st.session_state.doe_stage = "Planning"

if "planning_complete" not in st.session_state:
    st.session_state.planning_complete = False

# ============================================================================
# SECTION 1: STAGE 1 - PLANNING (问题定义、响应变量、关键因子识别)
# ============================================================================

st.header("📋 STAGE 1: PLANNING - Problem Definition & Factor Identification")

nucleic_acid_type = st.radio(
    "Nucleic Acid",
    ["mRNA", "pDNA"],
    horizontal=True,
    key="nucleic_acid_type",
    help="Changes labels and the citrate stock (mRNA: 100 mM, pDNA: 250 mM; both added at 1/10 of the aqueous phase). The volume calculation is the same."
)
na = "RNA" if nucleic_acid_type == "mRNA" else "DNA"
citrate_stock_mM = 100 if nucleic_acid_type == "mRNA" else 250
ION_RATIO_COL = f"Ion_{na}_Ratio"

st.markdown(f"""
### DOE Planning Phase
**Objective**: Systematic optimization of LNP formulation through Design of Experiments

**Steps**: Define objectives → Identify response variables → Determine key factors

#### Key Paper Insights:
⚠️ **In vitro ≠ In vivo efficacy** - Build separate models for each
- Ionizable Lipid %: 30-50% (primary driver)
- Helper Lipid % (DOPE/DOPC): 10-20%
- Cholesterol %: 35-50% (stability critical)
- PEG-Lipid %: 1-5% (**1% optimal**)
- Ionizable:{na} Ratio: 5-15

**Constraint**: Ionizable + Helper + Cholesterol + PEG = 100%
""")

response_variable = st.selectbox(
    "Response Variable:",
    options=[
        "Transfection Efficiency (%)",
        "Gene Expression Level (fold-change)",
        "Cell Viability (%)",
        "Particle Size (nm)",
        "Cellular Uptake (%)",
        "Protein Production (ng/mL)",
        "Other (custom)"
    ]
)

if response_variable == "Other (custom)":
    response_variable = st.text_input("Enter custom response variable name:")
objective = "Response Surface"  # Default objective

st.markdown("---")

st.subheader("🧪 Component Database Configuration")
st.write("*Preset as Moderna SM-102 formulation - Adjust as needed*")

with st.expander("📦 Lipid Components Configuration", expanded=False):
    st.subheader("Lipid Component Properties - Molecular Weights")
    
    col_mw1, col_mw2, col_mw3, col_mw4 = st.columns(4)
    with col_mw1:
        mw_ionizable = st.number_input(
            "Ionizable Lipid MW (g/mol)",
            value=710.182,
            step=0.1,
            key="mw_ion"
        )
    with col_mw2:
        mw_helper = st.number_input(
            "Helper Lipid MW (g/mol)",
            value=790.147,
            step=0.1,
            key="mw_helper"
        )
    with col_mw3:
        mw_chol = st.number_input(
            "Cholesterol MW (g/mol)",
            value=386.654,
            step=0.1,
            key="mw_chol"
        )
    with col_mw4:
        mw_peg = st.number_input(
            "PEG-DMG2000 MW (g/mol)",
            value=2509.2,
            step=0.1,
            key="mw_peg"
        )
    
    st.subheader("Stock Concentrations (μg/μL)")
    col_conc1, col_conc2, col_conc3, col_conc4 = st.columns(4)
    with col_conc1:
        conc_ionizable = st.number_input(
            "Ionizable Lipid (μg/μL)",
            value=40.0,
            step=0.1,
            key="conc_ion"
        )
    with col_conc2:
        conc_helper = st.number_input(
            "Helper Lipid (μg/μL)",
            value=4.0,
            step=0.1,
            key="conc_helper"
        )
    with col_conc3:
        conc_chol = st.number_input(
            "Cholesterol (μg/μL)",
            value=10.0,
            step=0.1,
            key="conc_chol"
        )
    with col_conc4:
        conc_peg = st.number_input(
            "PEG-DMG2000 (μg/μL)",
            value=4.0,
            step=0.1,
            key="conc_peg"
        )
    
    st.subheader(f"{na} Parameters")
    dna_col1, dna_col2 = st.columns(2)
    
    with dna_col1:
        dna_mass_ug = st.number_input(
            f"{na} Scale (μg)",
            value=5.0,
            step=0.1,
            key="dna_mass_ug"
        )
    
    with dna_col2:
        dna_concentration = st.number_input(
            f"{na} Stock (μg/μL)",
            value=1.0,
            step=0.01,
            key="dna_conc"
        )

st.markdown("---")

st.subheader("Molar Ratios (%)")
col_ratio1, col_ratio2, col_ratio3, col_ratio4 = st.columns(4)
with col_ratio1:
    ionizable_lipid_ratio = st.number_input(
        "Ionizable Lipid (%)",
        value=50.0,
        step=0.1,
        key="ion_ratio"
    )
with col_ratio2:
    helper_lipid_ratio = st.number_input(
        "Helper Lipid (%)",
        value=10.0,
        step=0.1,
        key="helper_ratio"
    )
with col_ratio3:
    cholesterol_ratio = st.number_input(
        "Cholesterol (%)",
        value=38.5,
        step=0.1,
        key="chol_ratio"
    )
with col_ratio4:
    pegdmg2000_ratio = st.number_input(
        "PEG-DMG2000 (%)",
        value=1.5,
        step=0.1,
        key="peg_ratio"
    )

baseline_total = ionizable_lipid_ratio + helper_lipid_ratio + cholesterol_ratio + pegdmg2000_ratio
st.caption("Baseline composition: used for any lipid % that is not a DOE factor. PEG % is always fixed at this value. "
           "So that every run sums to 100%, one lipid is calculated as the remainder: Cholesterol % when Helper % is a factor, otherwise Helper %.")
if abs(baseline_total - 100.0) > 0.01:
    st.warning(f"⚠️ Molar ratios sum to {baseline_total:.1f}%, not 100%. The remainder lipid will be recalculated in each run.")

st.markdown("---")

st.subheader("Additional Parameters")
col_add1, col_add2, col_add3, col_add4 = st.columns(4)
with col_add1:
    ionizable_lipid_to_dna_ratio = st.number_input(
        f"Ion:{na} Mass Ratio",
        value=10.0,
        step=0.1,
        key="ion_dna_ratio_param"
    )
with col_add2:
    aqueous_to_ethanol_ratio = st.number_input(
        "Aqueous:Ethanol",
        value=3.0,
        step=0.1,
        key="aqueous_ethanol_ratio"
    )
with col_add3:
    amines_per_molecule = st.number_input(
        "Amines/Lipid",
        value=1.0,
        step=0.1,
        key="amines_per_molecule"
    )
with col_add4:
    min_pipette_volume = st.number_input(
        "Min Pipettable Volume (μL)",
        value=0.5,
        min_value=0.0,
        step=0.1,
        key="min_pipette_volume",
        help="Runs needing a smaller volume of any component are flagged (most P2/P10 pipettes are inaccurate below ~0.5 μL)"
    )


st.markdown("---")

# ============================================================================
# SECTION 2: STAGE 2 - SCREENING (因子筛选 - 识别关键因子)
# ============================================================================

st.header("🔍 STAGE 2: SCREENING - Factor Selection & Range Definition")

st.markdown("""
**Steps**: (1) Select factors → (2) Define ranges → (3) Choose design
- 2-4 factors: Full Factorial | 5+ factors: Screening Design | Mixture: Mixture Design
""")

with st.expander("🎛️ Select Factors to Study", expanded=True):
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        study_ionizable = st.checkbox("Ionizable Lipid %", value=True, key="study_ionizable")
    with col_f2:
        study_helper = st.checkbox("Helper Lipid %", value=True, key="study_helper")
    with col_f3:
        study_cholesterol = st.checkbox("Cholesterol %", value=True, key="study_cholesterol")
    with col_f4:
        study_ion_dna = st.checkbox(f"Ion:{na} Ratio", value=True, key="study_ion_dna")
    
    # One lipid is the remainder so Ionizable + Helper + Cholesterol + PEG = 100%
    remainder_component = "Cholesterol_%" if study_helper else "Helper_%"
    study_flags = {
        "Ionizable_%": study_ionizable,
        "Helper_%": study_helper,
        "Cholesterol_%": study_cholesterol and remainder_component != "Cholesterol_%",
        ION_RATIO_COL: study_ion_dna,
    }
    num_factors = sum(study_flags.values())
    if remainder_component == "Cholesterol_%":
        st.caption("Cholesterol % = 100 − Ionizable − Helper − PEG in every run"
                   + (" (its range below is applied as a constraint)." if study_cholesterol else "."))
    # --- Customized Factors ---
    # Initialize store
    if "custom_factors" not in st.session_state:
        st.session_state.custom_factors = {}

    st.markdown("**Customized Factors:**")
    custom_col1, custom_col2 = st.columns([3, 1])
    with custom_col1:
        new_factor = st.text_input(
            "Add custom factor:",
            placeholder="e.g., Temperature (°C), pH",
            key="new_custom_factor_input"
        )
    with custom_col2:
        if st.button("➕ Add", key="add_custom_factor_btn"):
            if new_factor and new_factor not in st.session_state.custom_factors:
                st.session_state.custom_factors[new_factor] = {"active": True}
                st.rerun()

    # List current custom factors with toggle + delete
    if st.session_state.custom_factors:
        for factor_name in list(st.session_state.custom_factors.keys()):
            col_c1, col_c2 = st.columns([3, 1])
            with col_c1:
                is_checked = st.checkbox(
                    factor_name,
                    value=st.session_state.custom_factors[factor_name]["active"],
                    key=f"custom_{factor_name}"
                )
                st.session_state.custom_factors[factor_name]["active"] = is_checked
            with col_c2:
                if st.button("🗑️", key=f"del_{factor_name}"):
                    del st.session_state.custom_factors[factor_name]
                    st.rerun()

    # Recompute factor count including active customized factors
    custom_active = sum(
        1 for f in st.session_state.custom_factors.values() if f.get("active")
    )
    num_factors = sum(study_flags.values()) + custom_active
    if num_factors < 2:
        st.warning("⚠️ Select at least 2 factors")
    st.info(f"📊 Independent factors: {num_factors}")

st.markdown("---")

with st.expander("📏 Define Factor Ranges", expanded=True):
    factor_ranges = {}
    factor_steps = {}
    constraint_ranges = {}
    
    # (label, slider bounds, default range, recommended step, why)
    # Default ranges are centred on SM-102 (50 / 10 / 38.5 / 1.5 mol%) and extended equally on both sides
    range_specs = {
        "Ionizable_%": ("Ionizable Lipid %", (20.0, 70.0), (40.0, 60.0), 5.0, "Primary driver: 5% steps give 5 levels centred on SM-102's 50%"),
        "Helper_%": ("Helper Lipid %", (0.0, 40.0), (5.0, 15.0), 5.0, "5% steps give 3 levels (5/10/15%) centred on SM-102's 10%"),
        "Cholesterol_%": ("Cholesterol %", (20.0, 60.0), (28.5, 48.5), 5.0, "5% steps give 5 levels centred on SM-102's 38.5%"),
        ION_RATIO_COL: (f"Ion:{na} Ratio", (1.0, 30.0), (5.0, 15.0), 5.0, "Steps of 5 give 3 levels for screening; refine with 2.5 later"),
    }
    studied = {
        "Ionizable_%": study_ionizable, "Helper_%": study_helper,
        "Cholesterol_%": study_cholesterol, ION_RATIO_COL: study_ion_dna,
    }
    range_cols = st.columns(4)
    for col, (factor, (label, bounds, default, rec_step, why)) in zip(range_cols, range_specs.items()):
        if not studied[factor]:
            continue
        key = {"Ionizable_%": "ion", "Helper_%": "helper", "Cholesterol_%": "chol", ION_RATIO_COL: "ion_dna"}[factor]
        with col:
            st.markdown(f"**{label}**")
            f_range = st.slider("Range", min_value=bounds[0], max_value=bounds[1], value=default, step=0.5,
                                label_visibility="collapsed", key=f"{key}_range")
            if factor == remainder_component:
                constraint_ranges[factor] = f_range
                st.caption("Calculated as remainder; range used as a constraint")
                continue
            f_step = st.number_input("Step", min_value=0.5, value=rec_step, step=0.5, key=f"{key}_step",
                                     help=f"Recommended: {rec_step:g}. {why}. Used by the Grid design.")
            factor_ranges[factor] = f_range
            factor_steps[factor] = f_step
            levels = np.arange(f_range[0], f_range[1] + 1e-9, f_step)
            st.caption("Levels: " + ", ".join(f"{v:g}" for v in levels))

    # Customized factor ranges (numeric)
    if "custom_factors" in st.session_state and st.session_state.custom_factors:
        st.markdown("**Custom Factor Ranges**")
        for factor_name, meta in st.session_state.custom_factors.items():
            if not meta.get("active"):
                continue
            cmin = st.number_input(f"{factor_name} - Min", value=0.0, step=0.1, key=f"{factor_name}_min")
            cmax = st.number_input(f"{factor_name} - Max", value=1.0, step=0.1, key=f"{factor_name}_max")
            if cmin >= cmax:
                st.warning(f"⚠️ {factor_name}: Min should be less than Max")
            factor_ranges[factor_name] = (float(cmin), float(cmax))
            factor_steps[factor_name] = st.number_input(f"{factor_name} - Step", min_value=0.001, value=max((cmax - cmin) / 2, 0.001), key=f"{factor_name}_step")
    
    st.markdown("**📌 Default ranges are centred on SM-102** (Ionizable 50 / Helper 10 / Cholesterol 38.5 / PEG 1.5 mol%): "
                "Ionizable 40–60% | Helper 5–15% | Cholesterol 28.5–48.5%")
st.markdown("---")

st.subheader("🎯 DOE Design Selection")
st.markdown("Every design respects Ionizable + Helper + Cholesterol + PEG = 100%: the remainder lipid is calculated per run and runs outside its constraint are removed.")

with st.container():
    col_design, col_params = st.columns([1.2, 1])
    
    with col_design:
        # Recommend design based on number of factors
        if num_factors <= 2:
            recommended_designs = ["Grid (Step-Based)", "Full Factorial (2-Level)", "Full Factorial (3-Level)", "Central Composite"]
            design_help = "With 2 or fewer factors, you can afford detailed exploration (Full Factorial or response surface)"
        elif num_factors == 3:
            recommended_designs = ["Grid (Step-Based)", "Full Factorial (2-Level)", "Box-Behnken", "Central Composite", "Full Factorial (3-Level)"]
            design_help = "With 3 factors, Full Factorial (8 runs) or response surface designs work well"
        elif num_factors == 4:
            recommended_designs = ["Grid (Step-Based)", "Fractional Factorial", "Box-Behnken", "Plackett-Burman", "Central Composite"]
            design_help = "With 4 factors, consider fractional or response surface designs to manage run count"
        else:
            recommended_designs = ["Plackett-Burman", "Fractional Factorial"]
            design_help = "With 5+ factors, use screening designs to identify the most important ones first"
        
        if study_ionizable and study_helper:
            # Ion + Helper (+ Cholesterol remainder) is a constrained mixture: box-corner designs lose most points
            recommended_designs = ["Grid (Step-Based)", "Mixture Design"] + [d for d in recommended_designs if d != "Grid (Step-Based)"][:2]
            design_help = ("Ionizable + Helper + Cholesterol must sum to 100% − PEG, so many factorial corners are infeasible. "
                           "Grid (step-based) or Mixture Design cover the feasible region evenly.")
        
        st.markdown("**Recommended Designs** 🌟")
        design_type = st.radio(
            "Select DOE design method:",
            options=recommended_designs,
            help=design_help
        )
        
        st.markdown("**Other Available Designs**")
        all_designs = [
            "Grid (Step-Based)",
            "Full Factorial (2-Level)",
            "Full Factorial (3-Level)",
            "Fractional Factorial",
            "Plackett-Burman",
            "Box-Behnken",
            "Central Composite",
            "Mixture Design"
        ]
        other_designs = [d for d in all_designs if d not in recommended_designs]
        if other_designs:
            design_type_other = st.selectbox("Or choose from other designs:", options=["None"] + other_designs)
            if design_type_other != "None":
                design_type = design_type_other
    
    with col_params:
        st.markdown("**Experimental Parameters**")
        num_replicates = st.number_input(
            "Replicates:",
            value=1,
            min_value=1,
            max_value=10
        )
        num_blocks = st.number_input(
            "Blocks:",
            value=1,
            min_value=1,
            max_value=4
        )
        
        st.markdown("**Design Statistics**")

st.markdown("---")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

COMPOSITION_COLUMNS = ["Ionizable_%", "Helper_%", "Cholesterol_%", "PEG_%"]


def valid_design_mask(design_df, constraint_ranges, min_pct=0.5):
    """Runs where every lipid is at least min_pct and constrained lipids stay inside their ranges."""
    mask = (design_df[COMPOSITION_COLUMNS] >= min_pct - 1e-9).all(axis=1)
    for column, (low, high) in constraint_ranges.items():
        mask &= design_df[column].between(low - 1e-9, high + 1e-9)
    return mask


def filter_valid_design_points(design_df, constraint_ranges, min_pct=0.5):
    """Drop runs whose remainder lipid is negative or outside its constraint range."""
    filtered_df = design_df[valid_design_mask(design_df, constraint_ranges, min_pct)].reset_index(drop=True)
    n_removed = len(design_df) - len(filtered_df)
    
    if n_removed > 0:
        st.warning(f"⚠️ {n_removed} points removed (composition cannot sum to 100% within the ranges). {len(filtered_df)} valid points remain.")
    
    return filtered_df


def generate_grid(ranges_dict, steps_dict):
    """Generate a full grid: every factor from min to max in its step size."""
    factor_names = list(ranges_dict.keys())
    levels = [
        [round(v, 6) for v in np.arange(ranges_dict[f][0], ranges_dict[f][1] + 1e-9, steps_dict[f])]
        for f in factor_names
    ]
    return pd.DataFrame([dict(zip(factor_names, combo)) for combo in itertools.product(*levels)])


def generate_2level_factorial(ranges_dict):
    """Generate 2-level full factorial design."""
    design_points = list(itertools.product([-1, 1], repeat=len(ranges_dict)))
    factor_names = list(ranges_dict.keys())
    scaled_points = []
    
    for point in design_points:
        scaled_point = {}
        for i, factor in enumerate(factor_names):
            min_val, max_val = ranges_dict[factor]
            scaled_point[factor] = min_val + (point[i] + 1) / 2 * (max_val - min_val)
        scaled_points.append(scaled_point)
    
    return pd.DataFrame(scaled_points)


def generate_3level_factorial(ranges_dict):
    """Generate 3-level full factorial design."""
    factor_names = list(ranges_dict.keys())
    levels = {}
    
    for factor, (min_val, max_val) in ranges_dict.items():
        levels[factor] = [min_val, (min_val + max_val) / 2, max_val]
    
    all_combos = itertools.product(*[levels[f] for f in factor_names])
    design_data = [{factor_names[i]: val for i, val in enumerate(combo)} for combo in all_combos]
    
    return pd.DataFrame(design_data)


def generate_fractional_factorial(ranges_dict):
    """Generate a 2^(k-1) half-fraction: last factor = product of the others (resolution k)."""
    factor_names = list(ranges_dict.keys())
    n_factors = len(factor_names)
    if n_factors < 3:
        raise ValueError("Fractional Factorial needs at least 3 factors; use Full Factorial instead.")
    
    scaled_points = []
    for base in itertools.product([-1, 1], repeat=n_factors - 1):
        point = list(base) + [int(np.prod(base))]
        scaled_points.append({
            factor: ranges_dict[factor][0] + (point[i] + 1) / 2 * (ranges_dict[factor][1] - ranges_dict[factor][0])
            for i, factor in enumerate(factor_names)
        })
    return pd.DataFrame(scaled_points)


def generate_plackett_burman(ranges_dict):
    """Generate 12-run Plackett-Burman screening design (up to 11 factors)."""
    factor_names = list(ranges_dict.keys())
    n_factors = len(factor_names)
    if n_factors > 11:
        raise ValueError("12-run Plackett-Burman supports at most 11 factors.")
    
    # Standard N=12 generator row; rows 1-11 are its cyclic shifts, row 12 is all -1
    generator = [1, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1]
    pb_matrix = [generator[-i:] + generator[:-i] for i in range(11)] + [[-1] * 11]
    
    design_points = []
    for point in pb_matrix:
        design_points.append({
            factor: ranges_dict[factor][0] + (point[i] + 1) / 2 * (ranges_dict[factor][1] - ranges_dict[factor][0])
            for i, factor in enumerate(factor_names)
        })
    return pd.DataFrame(design_points)


def generate_box_behnken(ranges_dict, n_center=3):
    """Generate Box-Behnken design: each factor pair at (±1, ±1) with the rest at center, plus center points."""
    factor_names = list(ranges_dict.keys())
    n_factors = len(factor_names)
    if n_factors < 3:
        raise ValueError("Box-Behnken needs at least 3 factors.")
    
    coded_points = []
    for i, j in itertools.combinations(range(n_factors), 2):
        for a, b in itertools.product([-1, 1], repeat=2):
            point = [0] * n_factors
            point[i], point[j] = a, b
            coded_points.append(point)
    coded_points += [[0] * n_factors] * n_center
    
    design_data = [
        {factor: np.mean(ranges_dict[factor]) + point[i] * (ranges_dict[factor][1] - ranges_dict[factor][0]) / 2
         for i, factor in enumerate(factor_names)}
        for point in coded_points
    ]
    return pd.DataFrame(design_data)


def generate_central_composite(ranges_dict):
    """
    Generate face-centered Central Composite Design (alpha = 1): 2^k factorial + 2k axial + center.
    Axial points sit on the range limits so no run falls outside the user-defined ranges.
    """
    factor_names = list(ranges_dict.keys())
    
    design_points = generate_2level_factorial(ranges_dict).to_dict("records")
    center = {factor: np.mean(ranges_dict[factor]) for factor in factor_names}
    
    for factor in factor_names:
        for bound in ranges_dict[factor]:
            point = center.copy()
            point[factor] = bound
            design_points.append(point)
    
    design_points.append(center.copy())
    return pd.DataFrame(design_points)


def _clip_polygon(polygon, a, b, limit):
    """Keep the part of a convex polygon where a*x + b*y <= limit (Sutherland-Hodgman, one edge)."""
    clipped = []
    for i, current in enumerate(polygon):
        previous = polygon[i - 1]
        cur_in = a * current[0] + b * current[1] <= limit + 1e-9
        prev_in = a * previous[0] + b * previous[1] <= limit + 1e-9
        if cur_in != prev_in:
            t = (limit - a * previous[0] - b * previous[1]) / (a * (current[0] - previous[0]) + b * (current[1] - previous[1]))
            clipped.append((previous[0] + t * (current[0] - previous[0]), previous[1] + t * (current[1] - previous[1])))
        if cur_in:
            clipped.append(current)
    return clipped


def generate_mixture_design(ranges_dict, free_total, remainder_bounds, steps_dict=None):
    """
    Extreme-vertices mixture design over the studied lipids; the remainder lipid = free_total - sum(studied)
    must stay within remainder_bounds. Uses vertices, edge midpoints and centroid of the feasible region.
    Non-composition factors (e.g. Ion:RNA/DNA ratio) are crossed at their step levels (or low/high without steps).
    """
    composition = [f for f in COMPOSITION_COLUMNS if f in ranges_dict]
    process = [f for f in ranges_dict if f not in composition]
    if not composition or len(composition) > 2:
        raise ValueError("Mixture Design needs one or two independent lipid factors.")
    
    # Remainder bounds -> bounds on the sum of the studied lipids
    sum_low, sum_high = free_total - remainder_bounds[1], free_total - remainder_bounds[0]
    if len(composition) == 1:
        lo = max(ranges_dict[composition[0]][0], sum_low)
        hi = min(ranges_dict[composition[0]][1], sum_high)
        if lo > hi:
            raise ValueError("No feasible composition within the ranges.")
        mixture_points = [{composition[0]: v} for v in sorted({lo, (lo + hi) / 2, hi})]
    else:
        (x_lo, x_hi), (y_lo, y_hi) = ranges_dict[composition[0]], ranges_dict[composition[1]]
        polygon = [(x_lo, y_lo), (x_hi, y_lo), (x_hi, y_hi), (x_lo, y_hi)]
        polygon = _clip_polygon(polygon, 1, 1, sum_high)
        polygon = _clip_polygon(polygon, -1, -1, -sum_low)
        vertices = list(dict.fromkeys((round(x, 6), round(y, 6)) for x, y in polygon))
        if not vertices:
            raise ValueError("No feasible composition within the ranges.")
        
        cx, cy = np.mean([v[0] for v in vertices]), np.mean([v[1] for v in vertices])
        edge_midpoints = [
            ((vertices[i][0] + vertices[i - 1][0]) / 2, (vertices[i][1] + vertices[i - 1][1]) / 2)
            for i in range(len(vertices))
        ] if len(vertices) > 2 else [((vertices[0][0] + vertices[-1][0]) / 2, (vertices[0][1] + vertices[-1][1]) / 2)]
        mixture_points = [
            {composition[0]: x, composition[1]: y}
            for x, y in vertices + edge_midpoints + [(cx, cy)]
        ]
    
    design_points = []
    steps_dict = steps_dict or {}
    process_levels = [
        np.arange(ranges_dict[f][0], ranges_dict[f][1] + 1e-9, steps_dict[f]) if f in steps_dict else ranges_dict[f]
        for f in process
    ]
    for levels in itertools.product(*process_levels):
        for point in mixture_points:
            design_points.append({**point, **dict(zip(process, levels))})
    return pd.DataFrame(design_points).drop_duplicates().reset_index(drop=True)


def feasible_composition_polygon(ranges_dict, remainder, constraint_ranges, peg_pct):
    """
    Corners of the feasible Ionizable / Helper / Cholesterol region (PEG fixed), as dicts of the three
    lipids in drawing order. None when fewer than two lipids are independent factors.
    """
    lipids = ["Ionizable_%", "Helper_%", "Cholesterol_%"]
    independent = [c for c in lipids if c in ranges_dict and c != remainder]
    if len(independent) != 2:
        return None
    free_total = 100.0 - peg_pct
    rem_low, rem_high = constraint_ranges.get(remainder, (0.5, 100.0))
    (x_lo, x_hi), (y_lo, y_hi) = ranges_dict[independent[0]], ranges_dict[independent[1]]
    polygon = [(x_lo, y_lo), (x_hi, y_lo), (x_hi, y_hi), (x_lo, y_hi)]
    polygon = _clip_polygon(polygon, 1, 1, free_total - rem_low)
    polygon = _clip_polygon(polygon, -1, -1, -(free_total - rem_high))
    return [
        {independent[0]: x, independent[1]: y, remainder: free_total - x - y}
        for x, y in polygon
    ] or None


def build_design(design_type, ranges_dict, baseline_pct, remainder, steps_dict, constraint_ranges):
    """
    Generates the design over the independent factors, fills lipids that are not studied with
    baseline values, and sets the remainder lipid so each run sums to 100%.
    """
    fixed = [c for c in COMPOSITION_COLUMNS if c not in ranges_dict and c != remainder]
    generators = {
        "Full Factorial (2-Level)": generate_2level_factorial,
        "Full Factorial (3-Level)": generate_3level_factorial,
        "Fractional Factorial": generate_fractional_factorial,
        "Plackett-Burman": generate_plackett_burman,
        "Box-Behnken": generate_box_behnken,
        "Central Composite": generate_central_composite,
    }
    if design_type == "Grid (Step-Based)":
        design_df = generate_grid(ranges_dict, steps_dict)
    elif design_type == "Mixture Design":
        free_total = 100.0 - sum(baseline_pct[c] for c in fixed)
        design_df = generate_mixture_design(ranges_dict, free_total, constraint_ranges.get(remainder, (0.5, 100.0)), steps_dict)
    else:
        design_df = generators[design_type](ranges_dict)
    
    for column in fixed:
        design_df[column] = baseline_pct[column]
    others = [c for c in COMPOSITION_COLUMNS if c != remainder]
    design_df[others] = design_df[others].round(2)
    design_df[remainder] = (100.0 - design_df[others].sum(axis=1)).round(2)
    return design_df[COMPOSITION_COLUMNS + [c for c in design_df.columns if c not in COMPOSITION_COLUMNS]]


def fit_response_surface(data, factors, ranges_dict, response="Response"):
    """
    Least-squares quadratic response-surface model on coded factors (-1..1):
    intercept + main effects + two-factor interactions + squared terms.
    Terms the data cannot support are dropped (squares need 3+ levels; fewer runs -> simpler model).
    Returns None when there are not enough runs for even a main-effects model.
    """
    data = data.dropna(subset=[response] + factors)
    usable = [f for f in factors if data[f].nunique() >= 2]
    if not usable:
        return None
    
    def code(f, values):
        low, high = ranges_dict[f]
        return (np.asarray(values, dtype=float) - (low + high) / 2) / ((high - low) / 2)
    
    main = [((f,), f) for f in usable]
    inter = [((a, b), f"{a} × {b}") for a, b in itertools.combinations(usable, 2)]
    square = [((f, f), f"{f}²") for f in usable if data[f].nunique() >= 3]
    candidates = [main + inter + square, main + inter, main]
    terms = next((t for t in candidates if len(data) >= len(t) + 2), None)
    if terms is None:
        return None
    
    def design_matrix(values):
        coded = {f: code(f, values[f]) for f in usable}
        n = len(next(iter(coded.values())))
        columns = [np.ones(n)] + [np.prod([coded[f] for f in combo], axis=0) for combo, _ in terms]
        return np.column_stack(columns)
    
    X = design_matrix({f: data[f].values for f in usable})
    y = data[response].astype(float).values
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    residual = y - X @ beta
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - float((residual ** 2).sum()) / ss_tot if ss_tot > 0 else float("nan")
    model_name = {len(main + inter + square): "Quadratic", len(main + inter): "Linear + interactions", len(main): "Linear"}[len(terms)]
    return {
        "factors": usable,
        "terms": ["Intercept"] + [name for _, name in terms],
        "coefficients": beta,
        "r2": r2,
        "n": len(y),
        "model": model_name,
        "predict": lambda values: design_matrix(values) @ beta,
    }


def calculate_np_ratio(dna_mass_ug, ionizable_lipid_moles, amines_per_molecule=1.0):
    """Calculate N/P ratio using pDNA formulation methodology."""
    phosphate_moles_mol = dna_mass_ug * 1e-6 / 330.0
    phosphate_moles_umol = phosphate_moles_mol * 1e6
    amine_moles_umol = ionizable_lipid_moles * amines_per_molecule
    
    if phosphate_moles_umol > 0:
        np_ratio = amine_moles_umol / phosphate_moles_umol
    else:
        np_ratio = 0
    
    return np_ratio, amine_moles_umol, phosphate_moles_umol


def calculate_volumes(
    ionizable_pct, helper_pct, chol_pct, peg_pct,
    mw_ion, mw_helper, mw_chol, mw_peg,
    conc_ion, conc_helper, conc_chol, conc_peg,
    dna_mass_ug=None,
    dna_concentration=None,
    ionizable_lipid_to_dna_ratio=10.0,
    aqueous_to_ethanol_ratio=3.0
):
    """Convert this run's molar percentages to pipetting volumes (pDNA formulation)."""
    # Calculate ionizable lipid moles from Ion:DNA ratio
    ionizable_lipid_moles = (dna_mass_ug * ionizable_lipid_to_dna_ratio) / mw_ion
    
    # Other lipids follow this design point's molar ratios relative to the ionizable lipid
    helper_lipid_moles = ionizable_lipid_moles * helper_pct / ionizable_pct
    cholesterol_moles = ionizable_lipid_moles * chol_pct / ionizable_pct
    pegdmg2000_moles = ionizable_lipid_moles * peg_pct / ionizable_pct
    
    ionizable_lipid_mass = ionizable_lipid_moles * mw_ion
    helper_lipid_mass = helper_lipid_moles * mw_helper
    cholesterol_mass = cholesterol_moles * mw_chol
    pegdmg2000_mass = pegdmg2000_moles * mw_peg
    
    final_lnp_volume = dna_mass_ug / 0.1
    
    ionizable_lipid_volume = ionizable_lipid_mass / conc_ion
    helper_lipid_volume = helper_lipid_mass / conc_helper
    cholesterol_volume = cholesterol_mass / conc_chol
    pegdmg2000_volume = pegdmg2000_mass / conc_peg
    ethanol = final_lnp_volume / (aqueous_to_ethanol_ratio + 1) - ionizable_lipid_volume - helper_lipid_volume - cholesterol_volume - pegdmg2000_volume
    ethanol_phase_volume = ionizable_lipid_volume + helper_lipid_volume + cholesterol_volume + pegdmg2000_volume + ethanol
    
    aqueous_phase_volume = final_lnp_volume * (aqueous_to_ethanol_ratio / (aqueous_to_ethanol_ratio + 1))
    dna_volume = dna_mass_ug / dna_concentration
    citrate_volume = 0.1 * aqueous_phase_volume
    water_volume = aqueous_phase_volume - dna_volume - citrate_volume
    
    total = ionizable_lipid_volume + helper_lipid_volume + cholesterol_volume + pegdmg2000_volume + ethanol + dna_volume + citrate_volume + water_volume
    
    return {
        "Ionizable_Vol_uL": round(ionizable_lipid_volume, 2),
        "Helper_Vol_uL": round(helper_lipid_volume, 2),
        "Chol_Vol_uL": round(cholesterol_volume, 2),
        "PEG_Vol_uL": round(pegdmg2000_volume, 2),
        "Ethanol_Vol_uL": round(ethanol, 2),
        "Ethanol_Phase_Vol_uL": round(ethanol_phase_volume, 2),
        "DNA_Vol_uL": round(dna_volume, 2),
        "Citrate_Vol_uL": round(citrate_volume, 2),
        "Water_Vol_uL": round(water_volume, 2),
        "Total_Vol_uL": round(total, 2),
        "Ionizable_Moles": ionizable_lipid_moles,  # Return ionizable moles for N/P calculation
        "Phosphate_Moles": dna_mass_ug * 1e-6 / 330.0 * 1e6  # phosphate moles in μmol
    }


# FDA-approved LNP compositions (mol %), as on the FDA Approved Formulations page
LNP_REFERENCE_FORMULATIONS = {
    "SM-102": {"ion": 50.0, "helper": 10.0, "chol": 38.5, "peg": 1.5},
    "MC3": {"ion": 50.0, "helper": 10.0, "chol": 38.5, "peg": 1.5},
    "ALC-0315": {"ion": 46.3, "helper": 9.4, "chol": 42.7, "peg": 1.6},
}


# Volumes checked against the pipetting threshold. Ethanol and water are diluents: a small error
# there barely changes the composition, so they are not flagged.
PIPETTED_COMPONENTS = {
    "Ionizable": "Ionizable_Vol_uL",
    "Helper": "Helper_Vol_uL",
    "Cholesterol": "Chol_Vol_uL",
    "PEG": "PEG_Vol_uL",
    "Nucleic acid": "DNA_Vol_uL",
    "Citrate": "Citrate_Vol_uL",
}


def generate_run_sheet(design_df, num_replicates, num_blocks, mw_ion, mw_helper, mw_chol, mw_peg,
                       conc_ion, conc_helper, conc_chol, conc_peg,
                       dna_mass_ug=None, dna_concentration=None,
                       ionizable_lipid_to_dna_ratio=10.0,
                       aqueous_to_ethanol_ratio=3.0,
                       amines_per_molecule=1.0,
                       min_volume=0.0):
    """
    Generate a complete run sheet with pipetting volumes and N/P ratios.
    Same volume logic as the formulation calculator. Run order is randomized within each block.
    """
    standard_columns = set(COMPOSITION_COLUMNS) | {ION_RATIO_COL}
    extra_factors = [c for c in design_df.columns if c not in standard_columns]
    rng = np.random.default_rng()
    run_data = []
    run_number = 1
    
    for block in range(num_blocks):
        block_runs = []
        for idx, row in design_df.iterrows():
            ion_pct, helper_pct, chol_pct, peg_pct = (row[c] for c in COMPOSITION_COLUMNS)
            ion_dna_ratio = row.get(ION_RATIO_COL, ionizable_lipid_to_dna_ratio)
            
            vol_dict = calculate_volumes(
                ion_pct, helper_pct, chol_pct, peg_pct,
                mw_ion, mw_helper, mw_chol, mw_peg,
                conc_ion, conc_helper, conc_chol, conc_peg,
                dna_mass_ug=dna_mass_ug,
                dna_concentration=dna_concentration,
                ionizable_lipid_to_dna_ratio=ion_dna_ratio,
                aqueous_to_ethanol_ratio=aqueous_to_ethanol_ratio
            )
            
            # Calculate N/P ratio
            amine_moles = vol_dict["Ionizable_Moles"] * amines_per_molecule
            phosphate_moles = vol_dict["Phosphate_Moles"]
            np_ratio = amine_moles / phosphate_moles if phosphate_moles > 0 else 0
            low_volumes = [
                f"{name} {vol_dict[key]:g}"
                for name, key in PIPETTED_COMPONENTS.items()
                if 0 < vol_dict[key] < min_volume
            ]
            
            for rep in range(num_replicates):
                block_runs.append({
                    "Block": block + 1,
                    "Experiment": idx + 1,
                    "Replicate": rep + 1,
                    "Ionizable_%": round(ion_pct, 2),
                    "Helper_%": round(helper_pct, 2),
                    "Cholesterol_%": round(chol_pct, 2),
                    "PEG_%": round(peg_pct, 2),
                    ION_RATIO_COL: round(ion_dna_ratio, 2),
                    **{factor: row[factor] for factor in extra_factors},
                    "NP_Ratio": round(np_ratio, 2),
                    "Ionizable_Vol_uL": vol_dict["Ionizable_Vol_uL"],
                    "Helper_Vol_uL": vol_dict["Helper_Vol_uL"],
                    "Chol_Vol_uL": vol_dict["Chol_Vol_uL"],
                    "PEG_Vol_uL": vol_dict["PEG_Vol_uL"],
                    "Ethanol_Vol_uL": vol_dict["Ethanol_Vol_uL"],
                    f"{na}_Vol_uL": vol_dict["DNA_Vol_uL"],
                    f"Citrate_{citrate_stock_mM}mM_Vol_uL": vol_dict["Citrate_Vol_uL"],
                    "Water_Vol_uL": vol_dict["Water_Vol_uL"],
                    "Total_Vol_uL": vol_dict["Total_Vol_uL"],
                    "Volume_Check": ("⚠ < " + f"{min_volume:g} μL: " + ", ".join(low_volumes)) if low_volumes else "OK",
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Notes": ""
                })
        
        # Randomize execution order within the block; Run_ID follows the randomized order
        for i in rng.permutation(len(block_runs)):
            run_data.append({"Run_ID": f"R{run_number:03d}", **block_runs[i]})
            run_number += 1
    
    return pd.DataFrame(run_data)


# ============================================================================
# SECTION 3: STAGE 3 - OPTIMIZATION (设计生成与执行)
# ============================================================================

st.header("⚙️ STAGE 3: OPTIMIZATION - Generate Design & Run Sheet")

st.markdown("**Steps**: (1) Validate ranges → (2) Generate points → (3) Filter invalid → (4) Calculate volumes")

# Independent factors (the remainder lipid is calculated, not designed)
ranges = dict(factor_ranges)

# Check range validity
range_valid = True
for factor_name, (min_val, max_val) in ranges.items():
    if min_val >= max_val:
        st.error(f"❌ Invalid range for {factor_name}: Min ({min_val}) must be less than Max ({max_val})")
        range_valid = False

if not range_valid:
    st.stop()

# Composition used for lipids that are not being studied
baseline_pct = {
    "Ionizable_%": ionizable_lipid_ratio,
    "Helper_%": helper_lipid_ratio,
    "Cholesterol_%": cholesterol_ratio,
    "PEG_%": pegdmg2000_ratio,
}

with col_params:
    try:
        preview_df = build_design(design_type, ranges, baseline_pct, remainder_component, factor_steps, constraint_ranges)
        n_feasible = int(valid_design_mask(preview_df, constraint_ranges).sum())
        st.metric("Base Design Runs", len(preview_df), help="Design points before replicates and blocks")
        st.metric("Total Runs (incl. replicates & blocks)", len(preview_df) * num_replicates * num_blocks)
        if n_feasible < len(preview_df):
            st.caption(f"⚠️ {len(preview_df) - n_feasible} point(s) cannot sum to 100% within the ranges and will be removed → {n_feasible} feasible")
    except ValueError as e:
        st.warning(f"⚠️ {e}")

if st.button("🚀 Generate DOE Design & Run Sheet", type="primary", use_container_width=True):
    
    with st.spinner("Generating DOE design..."):
        try:
            design_df = build_design(design_type, ranges, baseline_pct, remainder_component, factor_steps, constraint_ranges)
            candidate_df = design_df.copy()
            
            # Filter invalid design points (where ratios sum > 100%)
            design_df = filter_valid_design_points(design_df, constraint_ranges)
            
            # Check if we have any valid points left
            if len(design_df) == 0:
                st.error("❌ No valid design points found! The specified ratio ranges are too wide and conflict with the requirement that all ratios sum to 100%. Please adjust your ranges.")
            else:
                run_sheet = generate_run_sheet(
                    design_df, num_replicates, num_blocks,
                    mw_ionizable, mw_helper, mw_chol, mw_peg,
                    conc_ionizable, conc_helper, conc_chol, conc_peg,
                    dna_mass_ug=dna_mass_ug,
                    dna_concentration=dna_concentration,
                    ionizable_lipid_to_dna_ratio=ionizable_lipid_to_dna_ratio,
                    aqueous_to_ethanol_ratio=aqueous_to_ethanol_ratio,
                    amines_per_molecule=amines_per_molecule,
                    min_volume=min_pipette_volume
                )
                
                # Check for negative Ethanol volumes
                invalid_runs = run_sheet[run_sheet['Ethanol_Vol_uL'] < 0]
                valid_run_sheet = run_sheet[run_sheet['Ethanol_Vol_uL'] >= 0].copy()
                # Renumber so the lab sequence has no gaps where runs were dropped
                valid_run_sheet["Run_ID"] = [f"R{i:03d}" for i in range(1, len(valid_run_sheet) + 1)]
                valid_run_sheet = valid_run_sheet.reset_index(drop=True)
                
                if len(invalid_runs) > 0:
                    st.warning(f"⚠️ **WARNING: {len(invalid_runs)} experimental runs have NEGATIVE Ethanol volume!**\n\nThese runs are INVALID and will be ignored:\n")
                    invalid_summary = invalid_runs[['Run_ID', 'Experiment', 'Ionizable_%', 'Cholesterol_%', 'PEG_%', 'Ethanol_Vol_uL']].copy()
                    st.dataframe(invalid_summary, use_container_width=True, hide_index=True)
                    st.info(f"💡 **Cause**: The combination of high lipid concentrations and/or high Ion:{na} ratio requires too much ethanol, exceeding available space. Consider:\n- Reducing Ion:{na} ratio\n- Using lower lipid percentages\n- Increasing final LNP volume (dna_mass_ug)\n- Adjusting aqueous:ethanol ratio")
                
                # Store the valid design points for visualization
                if len(valid_run_sheet) > 0:
                    # Get unique design points that are valid
                    valid_design_experiments = valid_run_sheet['Experiment'].unique()
                    valid_design_df = design_df[design_df.index.isin(valid_design_experiments - 1)].copy()
                    
                    st.session_state.design_df = valid_design_df
                    st.session_state.run_sheet = valid_run_sheet
                    st.session_state.design_type = design_type
                    st.session_state.response_variable = response_variable
                    st.session_state.doe_objective = objective
                    st.session_state.num_replicates = num_replicates
                    st.session_state.num_blocks = num_blocks
                    st.session_state.responses = {}
                    st.session_state.design_version = st.session_state.get("design_version", 0) + 1
                    # Snapshot for the design-space plots (independent of later widget changes)
                    st.session_state.viz_context = {
                        "candidates": candidate_df,
                        "factors": list(ranges),
                        "ranges": dict(ranges),
                        "remainder": remainder_component,
                        "constraints": dict(constraint_ranges),
                        "ratio_col": ION_RATIO_COL,
                        "na": na,
                        "min_volume": min_pipette_volume,
                        "stocks": {"Ionizable": conc_ionizable, "Helper": conc_helper, "Cholesterol": conc_chol, "PEG": conc_peg},
                        "scale_ug": dna_mass_ug,
                    }
                    
                    st.success(f"""✅ **Design Generated Successfully!**
                    
**Original Design Points**: {len(design_df)}
**Valid Design Points**: {len(valid_design_df)} (after filtering negative ethanol)
**Replicates**: {num_replicates} × **Blocks**: {num_blocks}
**Total Valid Runs**: {len(valid_run_sheet)} experimental runs
""")
                else:
                    st.error("❌ No valid experimental runs! All runs have negative Ethanol volume. Please adjust parameters.")
            
        except Exception as e:
            st.error(f"❌ Error generating design: {str(e)}")

st.markdown("---")

if "run_sheet" in st.session_state:
    run_sheet = st.session_state.run_sheet
    design_df = st.session_state.design_df
    design_type_used = st.session_state.design_type
    response_variable = st.session_state.response_variable
    doe_objective = st.session_state.doe_objective
    num_replicates = st.session_state.num_replicates
    num_blocks = st.session_state.num_blocks
    
    st.markdown("---")
    st.header("📊 STAGE 4: VERIFICATION - Results & Analysis")
    
    st.markdown("""
    ### Verification Phase
    In this stage, we:
    1. **Review design statistics** - Validate experimental design
    2. **Prepare lab protocols** - Generate run sheets for execution
    3. **Plan data analysis** - Determine analysis methods
    4. **Set validation criteria** - Define success metrics
    """)
    
    st.markdown("---")
    st.subheader("✅ Design Validation Summary")
    
    sum_col1, sum_col2, sum_col3, sum_col4, sum_col5 = st.columns(5)
    
    with sum_col1:
        st.metric("Design Type", design_type_used.split("(")[0].strip())
    with sum_col2:
        st.metric("Design Points", len(design_df))
    with sum_col3:
        st.metric("Total Runs", len(run_sheet))
    with sum_col4:
        st.metric("Replicates", num_replicates)
    with sum_col5:
        st.metric("Response", response_variable.split("(")[0].strip())
    
    st.markdown("---")
    
    col_obj, col_approach = st.columns(2)
    
    with col_obj:
        st.markdown("**DOE Objective**")
        st.info(doe_objective)
    
    with col_approach:
        st.markdown("**Measured Response**")
        st.info(response_variable)
    
    st.markdown("---")
    
    st.subheader("🧪 Design Matrix & Lab Run Sheet")
    
    # Design points on their own are still exported as a separate Excel sheet
    design_display = design_df.copy()
    design_display["Helper_%"] = 100.0 - design_display["Ionizable_%"] - design_display["Cholesterol_%"] - design_display["PEG_%"]
    
    st.caption(
        f"**{len(design_df)}** design points × **{num_replicates}** replicate(s) × **{num_blocks}** block(s) "
        f"= **{len(run_sheet)}** runs. Each row is one run; **Design point** is the formulation it belongs to."
    )
    
    id_cols = ["Run_ID", "Block", "Experiment", "Replicate"]
    volume_cols = [c for c in run_sheet.columns if c.endswith("_Vol_uL")]
    check_cols = [c for c in ["Volume_Check", "Notes"] if c in run_sheet.columns]
    factor_cols = [c for c in run_sheet.columns if c not in id_cols + volume_cols + check_cols + ["Timestamp"]]
    column_groups = {
        "Composition & factors": factor_cols,
        "Pipetting volumes (μL)": volume_cols,
        "Checks & notes": check_cols,
    }
    
    ctrl_order, ctrl_cols = st.columns([1, 1.4])
    with ctrl_order:
        row_order = st.segmented_control(
            "Order rows by", ["Run order", "Design point"], default="Run order", key="sheet_order",
            help="Run order is the randomized sequence to follow in the lab; Design point groups replicates and blocks of the same formulation."
        ) or "Run order"
    with ctrl_cols:
        shown_groups = st.segmented_control(
            "Columns", list(column_groups), selection_mode="multi", default=list(column_groups), key="sheet_columns"
        ) or []
    
    # Measured results live in session state keyed by Run_ID, so sorting or hiding columns never mixes them up
    responses = st.session_state.setdefault("responses", {})
    response_name = response_variable or "Response"
    
    with st.expander("📤 Upload results CSV instead of typing", expanded=False):
        st.caption("Columns: `Run_ID` and `Response` (or just `Response`, in run order R001, R002, …).")
        uploaded_file = st.file_uploader("Results CSV", type=["csv"], key="result_upload", label_visibility="collapsed")
        if uploaded_file is not None and st.session_state.get("loaded_upload_id") != uploaded_file.file_id:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                if "Response" not in uploaded_df.columns:
                    st.error("The CSV needs a 'Response' column.")
                else:
                    values = pd.to_numeric(uploaded_df["Response"], errors="coerce")
                    run_ids = uploaded_df["Run_ID"].astype(str) if "Run_ID" in uploaded_df.columns else run_sheet["Run_ID"].iloc[:len(values)]
                    responses.clear()
                    responses.update({rid: float(v) for rid, v in zip(run_ids, values) if pd.notna(v) and rid in set(run_sheet["Run_ID"])})
                    st.session_state.loaded_upload_id = uploaded_file.file_id
                    st.session_state.design_version = st.session_state.get("design_version", 0) + 1  # refresh the table
                    st.success(f"✅ Loaded {len(responses)} results from {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error loading file: {e}")
    
    sheet = run_sheet if row_order == "Run order" else run_sheet.sort_values(["Experiment", "Block", "Replicate"])
    shown_cols = id_cols + [c for group in column_groups if group in shown_groups for c in column_groups[group]]
    table = sheet[shown_cols].copy()
    table["Response"] = sheet["Run_ID"].map(responses).astype(float)
    edited = st.data_editor(
        table,
        use_container_width=True,
        hide_index=True,
        height=min(38 + 35 * len(sheet), 560),
        disabled=shown_cols,
        key=f"run_sheet_editor_{st.session_state.get('design_version', 0)}_{row_order}_{'-'.join(shown_groups)}",
        column_config={
            "Run_ID": st.column_config.TextColumn("Run", pinned=True),
            "Experiment": st.column_config.NumberColumn("Design point", help="Design point (formulation) this run belongs to"),
            "NP_Ratio": st.column_config.NumberColumn("N/P", format="%.2f"),
            **{c: st.column_config.NumberColumn(c.replace("_Vol_uL", " (μL)"), format="%.2f") for c in volume_cols},
            "Volume_Check": st.column_config.TextColumn("Volume check", width="medium"),
            "Response": st.column_config.NumberColumn(f"✏️ {response_name}", help="Type the measured result for each run", pinned=True),
        },
    )
    for run_id, value in zip(edited["Run_ID"], edited["Response"]):
        if pd.notna(value):
            responses[run_id] = float(value)
        else:
            responses.pop(run_id, None)
    st.caption(f"✏️ **{len(responses)} / {len(run_sheet)}** runs have a measured {response_name}. "
               "Type results in the last column — the response surface below updates as you go.")
    
    # N/P range across all runs
    np_values = pd.to_numeric(run_sheet.get("NP_Ratio"), errors="coerce").dropna() if "NP_Ratio" in run_sheet.columns else pd.Series(dtype=float)
    if len(np_values) > 0:
        col_np1, col_np2, col_np3 = st.columns(3)
        with col_np1:
            st.metric("N/P Min", f"{np_values.min():.2f}")
        with col_np2:
            st.metric("N/P Avg", f"{np_values.mean():.2f}")
        with col_np3:
            st.metric("N/P Max", f"{np_values.max():.2f}")
    
    st.markdown("---")
    
    st.subheader("📊 Design Space Visualization")
    
    viz = st.session_state.get("viz_context")
    if viz is None or "min_volume" not in viz:
        st.info("Generate the design again to see the design-space plots.")
    else:
        lipids = ["Ionizable_%", "Helper_%", "Cholesterol_%"]
        lipid_labels = {"Ionizable_%": "Ionizable", "Helper_%": "Helper", "Cholesterol_%": "Cholesterol"}
        ratio_col = viz["ratio_col"]
        factor_labels = {**{k: f"{v} %" for k, v in lipid_labels.items()}, ratio_col: f"Ion:{viz['na']} ratio"}
        min_vol = viz["min_volume"]
        
        # Theme-specific steps (light / dark are each chosen, not flipped)
        is_dark = getattr(getattr(st.context, "theme", None), "type", "light") == "dark"
        c_point = "#3987e5" if is_dark else "#2a78d6"
        c_warning = "#fab219"
        c_ink = "#f0efec" if is_dark else "#0b0b0b"
        c_excluded = "#8f8e88" if is_dark else "#8a8984"
        c_surface = "#0e1117" if is_dark else "#ffffff"
        c_region = "rgba(195,194,183,0.10)" if is_dark else "rgba(82,81,78,0.07)"
        c_region_line = "rgba(195,194,183,0.45)" if is_dark else "rgba(82,81,78,0.35)"
        
        # Design points whose runs need a volume below the pipetting threshold
        low_experiments = set(run_sheet.loc[run_sheet["Volume_Check"] != "OK", "Experiment"])
        candidates = viz["candidates"].copy()
        key_cols = list(candidates.columns)
        kept_status = {
            tuple(row): ("low" if idx + 1 in low_experiments else "kept")
            for idx, row in zip(design_df.index, design_df[key_cols].round(4).values)
        }
        feasible_mask = valid_design_mask(candidates, viz["constraints"])
        candidates["status"] = [
            kept_status.get(tuple(row), "volume" if feasible else "outside")
            for row, feasible in zip(candidates[key_cols].round(4).values, feasible_mask)
        ]
        is_kept = lambda s: s.isin(["kept", "low"])
        n_kept = int(is_kept(candidates["status"]).sum())
        n_low_runs = int((run_sheet["Volume_Check"] != "OK").sum())
        n_outside = int((candidates["status"] == "outside").sum())
        n_volume = int((candidates["status"] == "volume").sum())
        
        compositions = candidates.groupby(lipids, as_index=False).agg(
            n_kept=("status", lambda s: int(is_kept(s).sum())),
            n_low=("status", lambda s: int((s == "low").sum())),
            any_outside=("status", lambda s: bool((s == "outside").any())),
        )
        n_comp_kept = int((compositions["n_kept"] > 0).sum())
        summary = f"**{n_kept}** design points · **{n_comp_kept}** lipid compositions"
        if n_outside:
            summary += f" · {n_outside} candidates outside the composition limits"
        if n_volume:
            summary += f" · {n_volume} removed for negative ethanol volume"
        st.markdown(summary)
        
        # ---------- Pipetting check: what to change so every volume is ≥ the threshold ----------
        if n_low_runs:
            volume_cols = {name: col for name, col in [
                ("Ionizable", "Ionizable_Vol_uL"), ("Helper", "Helper_Vol_uL"), ("Cholesterol", "Chol_Vol_uL"),
                ("PEG", "PEG_Vol_uL"), (f"{viz['na']} stock", f"{viz['na']}_Vol_uL"),
                ("Citrate", next((c for c in run_sheet.columns if c.startswith("Citrate_")), None)),
            ] if col in run_sheet.columns}
            smallest = {name: run_sheet.loc[run_sheet[col] > 0, col].min() for name, col in volume_cols.items()}
            too_small = {name: v for name, v in smallest.items() if v < min_vol}
            
            fixes = []
            # Option 1: dilute lipid stocks (lipid volume grows, taken out of the added ethanol)
            dilutions = {}
            for name, v in too_small.items():
                if name in viz["stocks"]:
                    target = viz["stocks"][name] * v / min_vol
                    nice = max(np.floor(target * 2) / 2, 0.5) if target >= 1 else round(target, 2)
                    dilutions[name] = nice
            if dilutions:
                extra = sum(
                    run_sheet[volume_cols[name]] * (viz["stocks"][name] / conc - 1) for name, conc in dilutions.items()
                )
                new_ethanol = run_sheet["Ethanol_Vol_uL"] - extra
                n_neg = int((new_ethanol < 0).sum())
                change = ", ".join(f"{name} {viz['stocks'][name]:g} → **{conc:g} μg/μL**" for name, conc in dilutions.items())
                fixes.append(f"**Dilute lipid stocks:** {change}" + (
                    f" — but {n_neg} run(s) would then run out of ethanol." if n_neg else " — all runs stay feasible."))
            # Option 2: scale every run up (all volumes grow proportionally)
            factor = min_vol / min(too_small.values())
            new_scale = np.ceil(viz["scale_ug"] * factor * 2) / 2
            fixes.append(f"**Scale up** {viz['na']} per formulation from {viz['scale_ug']:g} to **{new_scale:g} μg** "
                         f"(uses {new_scale * n_kept:g} μg {viz['na']} in total for one replicate).")
            
            smallest_text = ", ".join(f"{name} {v:.2f} μL" for name, v in too_small.items())
            st.warning(f"⚠️ **{n_low_runs} of {len(run_sheet)} runs need a volume below {min_vol:g} μL** (smallest: {smallest_text}). "
                       "These are marked ◆ in the composition plot and in the run sheet's `Volume_Check` column.\n\n"
                       + "\n".join(f"- {f}" for f in fixes))
        
        st.caption("📥 To save a chart as SVG, hover over it and click the camera icon in its toolbar.")
        # Camera icon in each chart's toolbar downloads an SVG (rendered in the browser)
        svg_config = lambda name: {"toImageButtonOptions": {"format": "svg", "filename": name}, "displaylogo": False}
        
        col_ternary, col_pairs = st.columns(2)
        
        # ---------- Left: lipid composition on the mixture simplex ----------
        with col_ternary:
            st.markdown("##### Lipid composition (mol %)")
            peg_pct = float(candidates["PEG_%"].iloc[0])
            ternary_sum = 100.0 - peg_pct
            
            def ratio_levels(row, statuses):
                match = candidates[(candidates[lipids] == row[lipids].values).all(axis=1) & candidates["status"].isin(statuses)]
                if ratio_col not in match.columns or match.empty:
                    return ""
                return ", ".join(f"{v:g}" for v in sorted(match[ratio_col].unique()))
            
            def hover(row):
                text = (f"Ionizable {row['Ionizable_%']:.2f}% · Helper {row['Helper_%']:.2f}% · "
                        f"Cholesterol {row['Cholesterol_%']:.2f}% · PEG {peg_pct:.2f}%")
                if row["n_kept"]:
                    text += f"<br>{row['n_kept']} design point(s)"
                    levels = ratio_levels(row, ["kept", "low"])
                    if levels:
                        text += f" · Ion:{viz['na']} {levels}"
                if row["n_low"]:
                    levels = ratio_levels(row, ["low"])
                    text += f"<br>⚠ Volume below {min_vol:g} μL" + (f" at Ion:{viz['na']} {levels}" if levels else "")
                dropped = ratio_levels(row, ["volume"])
                if dropped:
                    text += f"<br>Removed (negative ethanol) at Ion:{viz['na']} {dropped}"
                if row["any_outside"]:
                    text += "<br>Outside composition limits"
                return text
            
            compositions["hover"] = compositions.apply(hover, axis=1)
            fig_tern = go.Figure()
            
            region = feasible_composition_polygon(viz["ranges"], viz["remainder"], viz["constraints"], peg_pct)
            if region:
                closed = region + region[:1]
                fig_tern.add_trace(go.Scatterternary(
                    a=[p["Ionizable_%"] for p in closed], b=[p["Helper_%"] for p in closed], c=[p["Cholesterol_%"] for p in closed],
                    mode="lines", fill="toself", fillcolor=c_region, line=dict(color=c_region_line, width=1),
                    name="Feasible region", hoverinfo="skip"
                ))
            
            groups = [
                ("Design point", (compositions["n_kept"] > 0) & (compositions["n_low"] == 0),
                 dict(symbol="circle", size=12, color=c_point, line=dict(color=c_surface, width=2))),
                (f"⚠ Volume < {min_vol:g} μL", compositions["n_low"] > 0,
                 dict(symbol="diamond", size=13, color=c_warning, line=dict(color=c_surface, width=2))),
                ("Removed: negative ethanol", (compositions["n_kept"] == 0) & ~compositions["any_outside"],
                 dict(symbol="x-thin", size=10, color=c_excluded, line=dict(color=c_excluded, width=2))),
                ("Outside composition limits", (compositions["n_kept"] == 0) & compositions["any_outside"],
                 dict(symbol="circle-open", size=9, color=c_excluded, line=dict(width=1.5))),
            ]
            for name, mask, marker in groups:
                subset = compositions[mask]
                if subset.empty:
                    continue
                fig_tern.add_trace(go.Scatterternary(
                    a=subset["Ionizable_%"], b=subset["Helper_%"], c=subset["Cholesterol_%"],
                    mode="markers", marker=marker, name=name,
                    text=subset["hover"], hovertemplate="%{text}<extra></extra>"
                ))
            
            # FDA-approved formulations as reference stars, rescaled to this design's PEG %
            references = {}
            for name, ref in LNP_REFERENCE_FORMULATIONS.items():
                key = (ref["ion"], ref["helper"], ref["chol"])
                references.setdefault(key, {"names": [], "peg": ref["peg"]})["names"].append(name)
            ref_rows = []
            for (ion, helper, chol), info in references.items():
                scale = ternary_sum / (ion + helper + chol)
                ref_rows.append({
                    "a": ion * scale, "b": helper * scale, "c": chol * scale, "label": " / ".join(info["names"]),
                    "hover": f"<b>{' / '.join(info['names'])}</b><br>Ionizable {ion}% · Helper {helper}% · "
                             f"Cholesterol {chol}% · PEG {info['peg']}%",
                })
            ref_df = pd.DataFrame(ref_rows)
            fig_tern.add_trace(go.Scatterternary(
                a=ref_df["a"], b=ref_df["b"], c=ref_df["c"], mode="markers+text",
                # Open star so a design point at the same composition stays visible underneath
                marker=dict(symbol="star-open", size=20, color=c_ink, line=dict(color=c_ink, width=1.5)),
                text=ref_df["label"], textposition="middle right", textfont=dict(size=11, color=c_ink),
                customdata=ref_df["hover"], hovertemplate="%{customdata}<extra>FDA-approved</extra>",
                name="FDA-approved reference"
            ))
            
            # Zoom the triangle onto the explored region (and the references)
            lows = {c: min(candidates[c].min(), ref_df[k].min()) for c, k in zip(lipids, "abc")}
            mins = {c: max(0.0, np.floor((lows[c] - 5) / 5) * 5) for c in lipids}
            if ternary_sum - sum(mins.values()) < 10:
                mins = {c: 0.0 for c in lipids}
            axis = lambda c: dict(title=dict(text=lipid_labels[c]), min=mins[c], ticksuffix="%", linewidth=1, gridcolor=c_region_line)
            fig_tern.update_layout(
                ternary=dict(sum=ternary_sum, aaxis=axis("Ionizable_%"), baxis=axis("Helper_%"), caxis=axis("Cholesterol_%")),
                height=560,
                margin=dict(l=50, r=50, t=30, b=40),
                legend=dict(orientation="h", yanchor="top", y=-0.06, xanchor="center", x=0.5),
            )
            st.plotly_chart(fig_tern, use_container_width=True, config=svg_config("design_space_lipid_composition"))
            st.caption(f"Each corner direction is one lipid; PEG is fixed at {peg_pct:.1f}%, so the three shown lipids sum to "
                       f"{ternary_sum:.1f}%. The shaded area is every composition allowed by the ranges. "
                       f"☆ FDA-approved formulations, rescaled to {peg_pct:.1f}% PEG.")
        
        # ---------- Right: response surface fitted to the measured results ----------
        with col_pairs:
            st.markdown("##### Response surface")
            label = lambda f: factor_labels.get(f, f)
            
            observed = run_sheet.copy()
            observed["Response"] = run_sheet["Run_ID"].map(st.session_state.get("responses", {})).astype(float)
            factors_in_data = [f for f in viz["factors"] if f in observed.columns]
            model = fit_response_surface(observed, factors_in_data, viz["ranges"])
            
            if model is None or len(model["factors"]) < 2:
                n_entered = int(observed["Response"].notna().sum())
                st.info(
                    "Type measured results in the **✏️ Response** column of the run sheet above (or upload a CSV) to see the fitted response surface. "
                    f"({n_entered} of {len(run_sheet)} runs have a response; a surface needs at least two varying factors "
                    "and a few more runs than model terms.)"
                )
            else:
                fitted = model["factors"]
                ctrl_x, ctrl_y, ctrl_view = st.columns([1, 1, 1])
                with ctrl_x:
                    x_factor = st.selectbox("X axis", fitted, index=0, format_func=label, key="surface_x")
                with ctrl_y:
                    y_options = [f for f in fitted if f != x_factor]
                    y_factor = st.selectbox("Y axis", y_options, index=0, format_func=label, key="surface_y")
                with ctrl_view:
                    view = st.radio("View", ["3D surface", "Contour"], horizontal=True, key="surface_view",
                                    help="Contour downloads as a true vector SVG; the 3D view is embedded as an image.")
                
                # Remaining factors are held at one of their tested levels
                held = {}
                for f in [f for f in fitted if f not in (x_factor, y_factor)]:
                    levels = sorted(observed[f].dropna().unique())
                    held[f] = st.select_slider(f"Hold {label(f)} at", options=levels,
                                               value=levels[len(levels) // 2], key=f"surface_hold_{f}")
                
                # Prediction grid; compositions outside the constraints are left blank
                gx = np.linspace(*viz["ranges"][x_factor], 80)
                gy = np.linspace(*viz["ranges"][y_factor], 80)
                mesh_x, mesh_y = np.meshgrid(gx, gy)
                grid = pd.DataFrame({x_factor: mesh_x.ravel(), y_factor: mesh_y.ravel(), **{f: v for f, v in held.items()}})
                for column in COMPOSITION_COLUMNS:
                    if column not in grid.columns and column != viz["remainder"]:
                        grid[column] = candidates[column].iloc[0]
                grid[viz["remainder"]] = 100.0 - grid[[c for c in COMPOSITION_COLUMNS if c != viz["remainder"]]].sum(axis=1)
                z = model["predict"]({f: grid[f].values for f in fitted})
                z[~valid_design_mask(grid, viz["constraints"]).values] = np.nan
                z = z.reshape(mesh_x.shape)
                
                # Measured runs that lie on this slice (held factors at the chosen levels)
                on_slice = observed.dropna(subset=["Response"])
                for f, v in held.items():
                    on_slice = on_slice[np.isclose(on_slice[f], v)]
                
                response_name = st.session_state.get("response_variable") or "Response"
                ramp = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
                colorscale = [[i / (len(ramp) - 1), c] for i, c in enumerate(ramp)]
                point_hover = (f"{label(x_factor)} %{{x:.4~g}}<br>{label(y_factor)} %{{y:.4~g}}<br>"
                               f"{response_name}: %{{customdata:.4~g}}<extra>Measured</extra>")
                
                if view == "3D surface":
                    fig_surface = go.Figure([
                        go.Surface(
                            x=gx, y=gy, z=z, colorscale=colorscale, opacity=0.9,
                            colorbar=dict(title=dict(text=response_name, side="right"), thickness=12),
                            contours=dict(z=dict(show=True, usecolormap=True, project=dict(z=True))),
                            hovertemplate=f"{label(x_factor)} %{{x:.4~g}}<br>{label(y_factor)} %{{y:.4~g}}<br>Predicted %{{z:.4~g}}<extra></extra>",
                            name="Fitted surface",
                        ),
                        go.Scatter3d(
                            x=on_slice[x_factor], y=on_slice[y_factor], z=on_slice["Response"], customdata=on_slice["Response"],
                            mode="markers", marker=dict(size=5, color=c_ink, line=dict(color=c_surface, width=2)),
                            name="Measured", hovertemplate=point_hover,
                        ),
                    ])
                    fig_surface.update_layout(
                        scene=dict(
                            xaxis_title=label(x_factor), yaxis_title=label(y_factor), zaxis_title=response_name,
                            camera=dict(eye=dict(x=1.35, y=-1.35, z=0.85)),
                            aspectmode="manual", aspectratio=dict(x=1, y=1, z=0.75),
                        ),
                        height=560, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                    )
                else:
                    fig_surface = go.Figure([
                        go.Contour(
                            x=gx, y=gy, z=z, colorscale=colorscale, ncontours=12,
                            contours=dict(showlabels=True, labelfont=dict(size=10, color="#ffffff")),
                            colorbar=dict(title=dict(text=response_name, side="right"), thickness=12),
                            hovertemplate=f"{label(x_factor)} %{{x:.4~g}}<br>{label(y_factor)} %{{y:.4~g}}<br>Predicted %{{z:.4~g}}<extra></extra>",
                            name="Fitted surface",
                        ),
                        go.Scatter(
                            x=on_slice[x_factor], y=on_slice[y_factor], customdata=on_slice["Response"],
                            mode="markers", marker=dict(size=9, color=c_ink, line=dict(color=c_surface, width=2)),
                            name="Measured", hovertemplate=point_hover,
                        ),
                    ])
                    fig_surface.update_layout(
                        xaxis_title=label(x_factor), yaxis_title=label(y_factor),
                        height=560, margin=dict(l=50, r=20, t=10, b=40), showlegend=False,
                    )
                st.plotly_chart(fig_surface, use_container_width=True,
                                config={**svg_config("design_space_response_surface"), "scrollZoom": False})
                
                held_text = "; ".join(f"{label(f)} = {v:g}" for f, v in held.items())
                st.caption(
                    f"{model['model']} model fitted to {model['n']} measured runs (R² = {model['r2']:.2f}). "
                    + (f"Slice at {held_text}. " if held_text else "")
                    + "Dots are measured runs on this slice; blank areas are compositions outside the ranges."
                )
                if model["n"] < 2 * len(model["terms"]):
                    st.caption(f"⚠ Only {model['n']} runs for {len(model['terms'])} model terms — treat the surface as a rough guide.")
                
                # Best predicted formulation over the whole feasible region (all factors, not just this slice)
                goal = st.segmented_control("Goal", ["Maximize", "Minimize"], default="Maximize", key="surface_goal") or "Maximize"
                points_per_factor = 11 if len(fitted) <= 4 else 6
                search = pd.DataFrame(
                    list(itertools.product(*[np.linspace(*viz["ranges"][f], points_per_factor) for f in fitted])),
                    columns=fitted,
                )
                for column in COMPOSITION_COLUMNS:
                    if column not in search.columns and column != viz["remainder"]:
                        search[column] = candidates[column].iloc[0]
                search[viz["remainder"]] = 100.0 - search[[c for c in COMPOSITION_COLUMNS if c != viz["remainder"]]].sum(axis=1)
                search = search[valid_design_mask(search, viz["constraints"]).values].copy()
                search["Predicted"] = model["predict"]({f: search[f].values for f in fitted})
                best = search.loc[search["Predicted"].idxmax() if goal == "Maximize" else search["Predicted"].idxmin()]
                measured = observed.dropna(subset=["Response"])
                best_run = measured.loc[measured["Response"].idxmax() if goal == "Maximize" else measured["Response"].idxmin()]
                
                col_pred, col_meas = st.columns(2)
                with col_pred:
                    st.metric(f"Predicted best {response_name}", f"{best['Predicted']:.4g}")
                    st.caption(" · ".join(
                        [f"{lipid_labels[c]} {best[c]:.1f}%" for c in lipids] + [f"PEG {best['PEG_%']:.1f}%"]
                        + [f"{label(f)} {best[f]:.3g}" for f in fitted if f not in COMPOSITION_COLUMNS]
                    ))
                with col_meas:
                    st.metric(f"Best measured {response_name}", f"{best_run['Response']:.4g}")
                    st.caption(f"Run {best_run['Run_ID']} · " + " · ".join(
                        [f"{lipid_labels[c]} {best_run[c]:.1f}%" for c in lipids]
                        + [f"{label(f)} {best_run[f]:.3g}" for f in fitted if f not in COMPOSITION_COLUMNS]
                    ))
                on_edge = [label(f) for f in fitted if np.isclose(best[f], viz["ranges"][f]).any()]
                if on_edge:
                    st.caption(f"The predicted best sits at the edge of the range for {', '.join(on_edge)} — "
                               "the true optimum may lie outside; consider extending that range in the next round.")
                
                with st.expander("Model coefficients (coded units)"):
                    coef = pd.DataFrame({"Term": model["terms"], "Coefficient": model["coefficients"]})
                    coef["Term"] = coef["Term"].replace({f: label(f) for f in fitted}, regex=False)
                    for f in fitted:
                        coef["Term"] = coef["Term"].str.replace(f, label(f), regex=False)
                    coef = pd.concat([coef.iloc[:1], coef.iloc[1:].reindex(coef.iloc[1:]["Coefficient"].abs().sort_values(ascending=False).index)])
                    st.dataframe(coef, hide_index=True, use_container_width=True,
                                 column_config={"Coefficient": st.column_config.NumberColumn(format="%.3f")})
                    st.caption("Factors are coded from −1 (low end of range) to +1 (high end), so coefficient sizes are directly "
                               "comparable: a larger absolute value means a bigger effect on the response.")
    
    st.markdown("---")
    
    st.subheader("💾 Export & Download")
    
    export_sheet = run_sheet.copy()
    export_sheet[response_variable or "Response"] = run_sheet["Run_ID"].map(st.session_state.get("responses", {}))
    csv_data = export_sheet.to_csv(index=False)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    col_csv, col_xlsx = st.columns(2)
    
    with col_csv:
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"LNP_RunSheet_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_xlsx:
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            export_sheet.to_excel(writer, sheet_name='Run Sheet', index=False)
            design_display.to_excel(writer, sheet_name='Design Matrix', index=False)
            
            # Get factor ranges for summary
            range_summary = []
            for factor_name, (min_val, max_val) in ranges.items():
                range_summary.append(f"{min_val:.1f} - {max_val:.1f}")
            
            summary_data = {
                "Parameter": ["DOE Objective", "Response Variable", "Design Type", "Design Points", "Replicates", "Blocks", "Total Runs", 
                             "Generated", "Ionizable MW", "Helper MW", "Chol MW", "PEG MW"],
                "Value": [doe_objective, response_variable, design_type_used, len(design_df), num_replicates, num_blocks, len(run_sheet),
                         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         mw_ionizable, mw_helper, mw_chol, mw_peg]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        excel_buffer.seek(0)
        st.download_button(
            label="📊 Download Excel",
            data=excel_buffer.getvalue(),
            file_name=f"LNP_RunSheet_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

else:
    st.info("👈 **Start with STAGE 1: PLANNING** - Define your DOE objective, response variable, and components to begin the DOE workflow.")

    # Check feasibility and suggest adjustments
    st.info("💡 **Tip**: Wider ranges explore more of design space but may include non-functional formulations. Narrow ranges focus on known good regions.")
