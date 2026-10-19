import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import itertools
from datetime import datetime
from io import BytesIO
import ternary
import matplotlib.pyplot as plt
from matplotlib import cm

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
            value=10.0,
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
            value=10.0,
            step=0.1,
            key="conc_peg"
        )
    
    st.subheader(f"{na} Parameters")
    dna_col1, dna_col2 = st.columns(2)
    
    with dna_col1:
        dna_mass_ug = st.number_input(
            f"{na} Scale (μg)",
            value=3.0,
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
col_add1, col_add2, col_add3 = st.columns(3)
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
    range_specs = {
        "Ionizable_%": ("Ionizable Lipid %", (20.0, 70.0), (30.0, 50.0), 5.0, "Primary driver: 5% steps give 5 levels across 30-50%"),
        "Helper_%": ("Helper Lipid %", (0.0, 40.0), (10.0, 20.0), 5.0, "Narrow range: 5% steps give 3 levels (10/15/20%)"),
        "Cholesterol_%": ("Cholesterol %", (20.0, 60.0), (35.0, 50.0), 5.0, "5% steps give 4 levels across 35-50%"),
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
    
    st.markdown("**📌 Recommended Ranges**: Ionizable 30-50% | Helper 10-20% | Cholesterol 35-50% | **PEG 1% optimal**")
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


def generate_run_sheet(design_df, num_replicates, num_blocks, mw_ion, mw_helper, mw_chol, mw_peg,
                       conc_ion, conc_helper, conc_chol, conc_peg,
                       dna_mass_ug=None, dna_concentration=None,
                       ionizable_lipid_to_dna_ratio=10.0,
                       aqueous_to_ethanol_ratio=3.0,
                       amines_per_molecule=1.0):
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
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Notes": ""
                })
        
        # Randomize execution order within the block; Run_ID follows the randomized order
        for i in rng.permutation(len(block_runs)):
            run_data.append({"Run_ID": f"R{run_number:03d}", **block_runs[i]})
            run_number += 1
    
    return pd.DataFrame(run_data)


# ============================================================================
# TERNARY PLOT VISUALIZATION FOR MIXTURE DESIGN
# ============================================================================

def create_ternary_plot(analysis_data, response_variable, component1='Ionizable_%', 
                       component2='Cholesterol_%', component3='PEG_%',
                       label1='Ionizable Lipid %', label2='Cholesterol %', label3='PEG-Lipid %'):
    """Create ternary plot for mixture design response visualization."""
    
    # Prepare data - convert to numeric and filter valid data
    data_clean = analysis_data.copy()
    data_clean[component1] = pd.to_numeric(data_clean[component1], errors='coerce')
    data_clean[component2] = pd.to_numeric(data_clean[component2], errors='coerce')
    data_clean[component3] = pd.to_numeric(data_clean[component3], errors='coerce')
    data_clean['Response'] = pd.to_numeric(data_clean['Response'], errors='coerce')
    
    # Remove rows with any NaN values
    data_clean = data_clean[[component1, component2, component3, 'Response']].dropna()
    
    if len(data_clean) == 0:
        return None
    
    # Create figure and ternary axis
    scale = 100
    figure, tax = ternary.figure(scale=scale)
    
    # Draw boundary and gridlines
    tax.boundary(linewidth=2.0)
    tax.gridlines(color='gray', multiple=10, linewidth=0.5, alpha=0.3)
    
    # Set axis labels
    tax.left_axis_label(label1, offset=0.14, fontsize=10, fontweight='bold')
    tax.right_axis_label(label2, offset=0.14, fontsize=10, fontweight='bold')
    tax.bottom_axis_label(label3, offset=0.14, fontsize=10, fontweight='bold')
    
    # Draw ticks
    tax.ticks(axis='lbr', linewidth=1, multiple=10, offset=0.02, fontsize=8)
    
    # Prepare points and values
    points = [(row[component1], row[component2], row[component3]) 
              for _, row in data_clean.iterrows()]
    values = data_clean['Response'].values
    
    # Normalize values for color mapping (0-1 range)
    if len(values) > 0 and (values.max() - values.min()) > 0:
        values_normalized = (values - values.min()) / (values.max() - values.min())
    else:
        values_normalized = np.ones_like(values) * 0.5
    
    # Get colormap
    cmap = cm.get_cmap('RdYlGn')
    colors = [cmap(v) for v in values_normalized]
    
    # Plot scatter points with colors
    for point, value, color, orig_value in zip(points, values_normalized, colors, values):
        tax.scatter([point], c=[color], s=150, edgecolors='black', linewidth=1.5, zorder=3)
        
        # Add value annotations
        tax.annotate(f'{orig_value:.1f}', position=point, ha='center', va='center',
                    color='white', fontweight='bold', fontsize=7, zorder=4)
    
    # Clear matplotlib ticks and hide axes
    tax.clear_matplotlib_ticks()
    
    # Add colorbar manually
    sm = cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=values.min(), vmax=values.max()))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=tax.get_axes(), orientation='right', pad=0.1, fraction=0.046)
    cbar.set_label(response_variable, fontsize=10, fontweight='bold')
    
    return figure


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
                    amines_per_molecule=amines_per_molecule
                )
                
                # Check for negative Ethanol volumes
                invalid_runs = run_sheet[run_sheet['Ethanol_Vol_uL'] < 0]
                valid_run_sheet = run_sheet[run_sheet['Ethanol_Vol_uL'] >= 0].copy()
                
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
                    st.session_state.pop("response_data", None)
                    
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
    
    st.subheader("🔍 Design Matrix")

    
    design_display = design_df.copy()
    design_display["Helper_%"] = 100.0 - design_display["Ionizable_%"] - design_display["Cholesterol_%"] - design_display["PEG_%"]
    
    # Display number of design points
    num_design_points = len(design_display)
    st.info(f"📍 **Total Design Points: {num_design_points}**")
    
    st.dataframe(
        design_display.round(2),
        use_container_width=True,
        height=300
    )
    
    st.markdown("---")
    
    st.subheader("🧪 Lab Run Sheet")
    
    if len(run_sheet) > 20:
        show_rows = st.slider("Show first N rows", min_value=5, max_value=len(run_sheet), value=10)
    else:
        show_rows = len(run_sheet)
    
    # Display run sheet with N/P ratio information highlighted
    run_sheet_display = run_sheet.head(show_rows).copy()
    
    # Highlight columns with N/P information if available
    st.dataframe(
        run_sheet_display,
        use_container_width=True,
        height=400
    )
    
    if len(run_sheet) > show_rows:
        st.info(f"📌 Showing first {show_rows} of {len(run_sheet)} runs. Download full sheet below.")
    
    # Show N/P Ratio summary if calculated
    if "NP_Ratio" in run_sheet.columns and run_sheet["NP_Ratio"].dtype != 'object':
        np_values = pd.to_numeric(run_sheet["NP_Ratio"], errors='coerce')
        np_values = np_values.dropna()
        if len(np_values) > 0:
            st.markdown("---")
            col_np1, col_np2, col_np3 = st.columns(3)
            with col_np1:
                st.metric("N/P Min", f"{np_values.min():.2f}")
            with col_np2:
                st.metric("N/P Avg", f"{np_values.mean():.2f}")
            with col_np3:
                st.metric("N/P Max", f"{np_values.max():.2f}")
    
    st.markdown("---")
    
    st.subheader("📊 Design Space Visualization")
    
    # Get design points from design_display (which corresponds to valid design_df)
    # This ensures 3D visualization matches the actual Design Matrix
    design_for_viz = design_display.copy()
    
    # Create two columns for side-by-side display
    col_3d, col_bubble = st.columns(2)
    
    with col_3d:
        st.markdown("### 3D Molar Ratio Design Space")
        
        # Display number of visualization points
        st.info(f"📍 **Visualizing {len(design_for_viz)} design points** (synchronized with Design Matrix)")
        
        # 3D Molar Ratio Space: Ionizable vs Cholesterol vs PEG
        fig3d_molar = go.Figure(data=[go.Scatter3d(
            x=design_for_viz["Ionizable_%"],
            y=design_for_viz["Cholesterol_%"],
            z=design_for_viz["PEG_%"],
            mode='markers',
            marker=dict(
                size=8,
                color=design_for_viz["Helper_%"],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Helper %", x=1.1),
                line=dict(width=1, color='white'),
                opacity=0.9
            ),
            text=[f"Ion: {i:.1f}%<br>Chol: {c:.1f}%<br>PEG: {p:.1f}%<br>Helper: {h:.1f}%" 
                  for i, c, p, h in zip(design_for_viz["Ionizable_%"], 
                                       design_for_viz["Cholesterol_%"],
                                       design_for_viz["PEG_%"],
                                       design_for_viz["Helper_%"])],
            hoverinfo='text',
            name='Design Points'
        )])
        
        fig3d_molar.update_layout(
            scene=dict(
                xaxis_title="Ionizable Lipid (%)",
                yaxis_title="Cholesterol (%)",
                zaxis_title="PEG-Lipid (%)",
                xaxis=dict(
                    range=[design_display["Ionizable_%"].min() - 2, design_display["Ionizable_%"].max() + 2]
                ),
                yaxis=dict(
                    range=[design_display["Cholesterol_%"].min() - 2, design_display["Cholesterol_%"].max() + 2]
                ),
                zaxis=dict(
                    range=[design_display["PEG_%"].min() - 2, design_display["PEG_%"].max() + 2]
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.3)
                )
            ),
            height=600,
            hovermode='closest',
            showlegend=False,
            margin=dict(l=0, r=0, t=20, b=0)
        )
        
        st.plotly_chart(fig3d_molar, use_container_width=True)
    
    with col_bubble:
        st.markdown("### Response Surface Heatmap")
        
        # Bubble Chart: Helper Percentage vs Ionizable% and Cholesterol%
        # Bubble size represents the Helper% value
        
        # Create bubble chart data - each row becomes one bubble
        bubble_data = []
        for _, row in design_display.iterrows():
            bubble_data.append({
                'Ionizable_%': row['Ionizable_%'],
                'Cholesterol_%': row['Cholesterol_%'],
                'Helper_%': row['Helper_%']
            })
        bubble_df = pd.DataFrame(bubble_data)
        num_bubbles = len(bubble_df)
        
        # Normalize bubble sizes (scale Helper% to reasonable marker sizes)
        min_helper = bubble_df['Helper_%'].min()
        max_helper = bubble_df['Helper_%'].max()
        helper_range = max_helper - min_helper if max_helper > min_helper else 1
        bubble_sizes = 10 + (bubble_df['Helper_%'] - min_helper) / helper_range * 50  # Size range: 10-60
        
        st.info(f"🔵 **Bubbles: {num_bubbles}** (each bubble = 1 design point, size ∝ Helper %)")
        
        fig_hm = go.Figure(data=go.Scatter(
            x=bubble_df['Ionizable_%'],
            y=bubble_df['Cholesterol_%'],
            mode='markers',
            marker=dict(
                size=bubble_sizes,
                color=bubble_df['Helper_%'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Helper (%)"),
                line=dict(width=1, color='white'),
                opacity=0.7
            ),
            text=[f"Ionizable: {i:.1f}%<br>Cholesterol: {c:.1f}%<br>Helper: {h:.1f}%" 
                  for i, c, h in zip(bubble_df['Ionizable_%'], bubble_df['Cholesterol_%'], bubble_df['Helper_%'])],
            hoverinfo='text',
            name='Design Points'
        ))
        
        # Set axis ranges based on Design Matrix data
        fig_hm.update_layout(
            xaxis_title="Ionizable Lipid (%)",
            yaxis_title="Cholesterol (%)",
            xaxis=dict(
                range=[design_display["Ionizable_%"].min() - 2, design_display["Ionizable_%"].max() + 2]
            ),
            yaxis=dict(
                range=[design_display["Cholesterol_%"].min() - 2, design_display["Cholesterol_%"].max() + 2]
            ),
            height=600,
            hovermode='closest',
            margin=dict(l=50, r=50, t=20, b=50)
        )
        
        st.plotly_chart(fig_hm, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("💾 Export & Download")
    
    csv_data = run_sheet.to_csv(index=False)
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
            run_sheet.to_excel(writer, sheet_name='Run Sheet', index=False)
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
    
    # ========================================================================
    # DATA INPUT & ANALYSIS SECTION
    # ========================================================================
    
    st.markdown("---")
    st.subheader("📈 Data Input & Statistical Analysis")
    
    with st.expander("📊 Enter Experimental Results & Analyze", expanded=True):
        st.markdown(f"**Response Variable:** {response_variable}")
        st.markdown("Enter the measured outcome values for each experimental run below:")
        
        # Create data input interface
        col_input_info, col_input_upload = st.columns([2, 1])
        
        with col_input_info:
            st.info("💡 You can either manually enter values row-by-row, or upload a CSV file with results")
        
        with col_input_upload:
            uploaded_file = st.file_uploader(
                "Upload results CSV (with 'Response' column)",
                type=['csv'],
                key='result_upload'
            )
        
        # Initialize or load response data
        if "response_data" not in st.session_state:
            st.session_state.response_data = pd.DataFrame({
                'Run': range(1, len(run_sheet) + 1),
                'Response': [None] * len(run_sheet)
            })
        
        # Process uploaded file
        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                if 'Response' in uploaded_df.columns:
                    st.session_state.response_data['Response'] = uploaded_df['Response'].values[:len(run_sheet)]
                    st.success("✅ Data loaded successfully!")
            except Exception as e:
                st.error(f"Error loading file: {e}")
        
        # Manual data input using editable dataframe
        st.write("**Enter Response Values:**")
        response_df = st.data_editor(
            st.session_state.response_data,
            use_container_width=True,
            key='response_editor',
            hide_index=True,
            num_rows="fixed"
        )
        
        # Store the response data
        st.session_state.response_data = response_df
        
        # Convert Response column to numeric, handling any string values
        response_df['Response'] = pd.to_numeric(response_df['Response'], errors='coerce')
        
        # Count non-null responses
        valid_responses = response_df['Response'].dropna()
        st.info(f"📌 {len(valid_responses)}/{len(run_sheet)} runs have response values entered")
        
        # Analysis button
        col_analyze1, col_analyze2 = st.columns([1, 1])
        
        with col_analyze1:
            analyze_button = st.button("🔍 Perform Statistical Analysis", use_container_width=True)
        
        with col_analyze2:
            export_results = st.button("💾 Export Analysis Results", use_container_width=True)
        
        # Perform analysis if button clicked and we have data
        if analyze_button and len(valid_responses) > 0:
            st.markdown("---")
            st.subheader("📊 Analysis Results")
            
            # Basic statistics
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("Mean Response", f"{valid_responses.mean():.2f}")
            with col_stat2:
                st.metric("Std Deviation", f"{valid_responses.std():.2f}")
            with col_stat3:
                st.metric("Min Response", f"{valid_responses.min():.2f}")
            with col_stat4:
                st.metric("Max Response", f"{valid_responses.max():.2f}")
            
            # Merge response data with design data
            analysis_data = run_sheet.copy()
            analysis_data['Response'] = response_df['Response'].values
            
            st.markdown("---")
            st.write("**Run Sheet with Response Values:**")
            
            # Build column list dynamically based on what exists in the dataframe
            cols_to_display = []
            if 'Run_ID' in analysis_data.columns:
                cols_to_display.append('Run_ID')
            if 'Ionizable_%' in analysis_data.columns:
                cols_to_display.append('Ionizable_%')
            if 'Cholesterol_%' in analysis_data.columns:
                cols_to_display.append('Cholesterol_%')
            if 'PEG_%' in analysis_data.columns:
                cols_to_display.append('PEG_%')
            if ION_RATIO_COL in analysis_data.columns:
                cols_to_display.append(ION_RATIO_COL)
            if 'NP_Ratio' in analysis_data.columns:
                cols_to_display.append('NP_Ratio')
            cols_to_display.append('Response')
            
            st.dataframe(
                analysis_data[cols_to_display],
                use_container_width=True,
                height=300
            )
            
            st.markdown("---")
            st.subheader("🔺 Interactive Ternary Plot - Component Ratios vs Response")
            
            # Create ternary plot if we have the required components
            try:
                if 'Ionizable_%' in analysis_data.columns and 'Cholesterol_%' in analysis_data.columns and 'PEG_%' in analysis_data.columns:
                    # Prepare data for ternary plot
                    ternary_data = analysis_data[['Ionizable_%', 'Cholesterol_%', 'PEG_%', 'Response']].copy()
                    ternary_data = ternary_data.dropna()
                    
                    if len(ternary_data) > 0:
                        # Calculate factor importance (sensitivity analysis)
                        ionizable_corr = abs(ternary_data['Ionizable_%'].corr(ternary_data['Response']))
                        chol_corr = abs(ternary_data['Cholesterol_%'].corr(ternary_data['Response']))
                        peg_corr = abs(ternary_data['PEG_%'].corr(ternary_data['Response']))
                        
                        # Normalize importance scores
                        importance_scores = {
                            'Ionizable': ionizable_corr,
                            'Cholesterol': chol_corr,
                            'PEG': peg_corr
                        }
                        total_importance = sum(importance_scores.values())
                        if total_importance > 0:
                            importance_pct = {k: (v / total_importance * 100) for k, v in importance_scores.items()}
                        else:
                            importance_pct = {k: 0 for k in importance_scores}
                        
                        # Find most important factor
                        most_important = max(importance_scores, key=importance_scores.get)
                        
                        # Display factor importance insights
                        st.markdown("**📊 Factor Importance Analysis:**")
                        col1, col2, col3 = st.columns(3)
                        
                        # Color code factors based on importance
                        factor_colors = {
                            'Ionizable': '🔴' if most_important == 'Ionizable' else '⚪',
                            'Cholesterol': '🔴' if most_important == 'Cholesterol' else '⚪',
                            'PEG': '🔴' if most_important == 'PEG' else '⚪'
                        }
                        
                        with col1:
                            st.metric(
                                f"{factor_colors['Ionizable']} Ionizable Lipid Impact",
                                f"{importance_pct['Ionizable']:.1f}%",
                                delta="Most Important" if most_important == 'Ionizable' else None
                            )
                        
                        with col2:
                            st.metric(
                                f"{factor_colors['Cholesterol']} Cholesterol Impact",
                                f"{importance_pct['Cholesterol']:.1f}%",
                                delta="Most Important" if most_important == 'Cholesterol' else None
                            )
                        
                        with col3:
                            st.metric(
                                f"{factor_colors['PEG']} PEG Impact",
                                f"{importance_pct['PEG']:.1f}%",
                                delta="Most Important" if most_important == 'PEG' else None
                            )
                        
                        st.markdown(f"""
                        **Key Finding:** **{most_important}** is the most critical factor, with **{importance_pct[most_important]:.1f}%** 
                        of the correlation strength with {response_variable}. This factor should be prioritized in optimization.
                        """)
                        
                        st.markdown("---")
                        st.markdown("""
                        **📍 Interactive Ternary Plot - Component Ratios vs Response**
                        - 🖱️ **Hover**: See detailed information for each run
                        - 🔍 **Zoom**: Click and drag to zoom into regions of interest
                        - 📍 **Pan**: Scroll to move around the plot
                        - 💾 **Save**: Download the plot as PNG from the toolbar
                        """)
                        
                        # Prepare data for interactive Plotly ternary plot
                        values = ternary_data['Response'].values
                        
                        # Normalize values for color mapping (0-1 range)
                        if len(values) > 0 and (values.max() - values.min()) > 0:
                            values_normalized = (values - values.min()) / (values.max() - values.min())
                        else:
                            values_normalized = np.ones_like(values) * 0.5
                        
                        # Create color scale based on RdYlGn (Red=High, Yellow=Mid, Green=Low)
                        # Reverse it so red is high response
                        colorscale = [
                            [0.0, '#1a9850'],    # Green (low)
                            [0.5, '#ffffbf'],    # Yellow (mid)
                            [1.0, '#d73027']     # Red (high)
                        ]
                        
                        # Create hover text with rich information
                        hover_texts = []
                        for idx, row in ternary_data.iterrows():
                            helper_pct = 100.0 - row['Ionizable_%'] - row['Cholesterol_%'] - row['PEG_%']
                            hover_text = (
                                f"<b>Run #{idx + 1}</b><br>"
                                f"<b>Component Ratios:</b><br>"
                                f"  • Ionizable: {row['Ionizable_%']:.1f}%<br>"
                                f"  • Cholesterol: {row['Cholesterol_%']:.1f}%<br>"
                                f"  • PEG: {row['PEG_%']:.1f}%<br>"
                                f"  • Helper: {helper_pct:.1f}%<br>"
                                f"<b>Response:</b> {row['Response']:.2f}<br>"
                                f"<i>Click for more details</i>"
                            )
                            hover_texts.append(hover_text)
                        
                        # Create Plotly ternary plot
                        fig_ternary = go.Figure(data=[go.Scatterternary(
                            a=ternary_data['Ionizable_%'].values,
                            b=ternary_data['Cholesterol_%'].values,
                            c=ternary_data['PEG_%'].values,
                            mode='markers+text',
                            marker=dict(
                                size=8 + (values_normalized * 12),  # Size varies with response
                                color=values,  # Color based on response value
                                colorscale=colorscale,
                                showscale=True,
                                colorbar=dict(
                                    title=f"<b>{response_variable}</b>",
                                    thickness=15,
                                    len=0.7,
                                    x=1.02
                                ),
                                line=dict(color='rgba(26, 26, 26, 0.8)', width=1.5),
                                opacity=0.85
                            ),
                            text=[f"{v:.0f}" for v in values],
                            textposition="middle center",
                            textfont=dict(size=8, color='white', family='monospace'),
                            hovertext=hover_texts,
                            hoverinfo='text',
                            customdata=np.arange(len(ternary_data)),
                        )])
                        
                        # Update layout for better appearance
                        fig_ternary.update_layout(
                            title=dict(
                                text=f"<b>Component Mixture Design - {response_variable} Response Surface</b><br>" +
                                     f"<sub>Most Important Factor: <span style='color:#d32f2f'>{most_important}</span></sub>",
                                font=dict(size=16, color='#1a1a1a', family='sans-serif'),
                                x=0.5,
                                xanchor='center'
                            ),
                            ternary=dict(
                                sum=100,
                                aaxis=dict(
                                    title="Ionizable Lipid %",
                                    min=0.01,
                                    linewidth=2,
                                    ticks='outside',
                                    tickfont=dict(size=11, color='#1a1a1a')
                                ),
                                baxis=dict(
                                    title="Cholesterol %",
                                    min=0.01,
                                    linewidth=2,
                                    ticks='outside',
                                    tickfont=dict(size=11, color='#1a1a1a')
                                ),
                                caxis=dict(
                                    title="PEG %",
                                    min=0.01,
                                    linewidth=2,
                                    ticks='outside',
                                    tickfont=dict(size=11, color='#1a1a1a')
                                ),
                                bgcolor='rgba(240, 240, 245, 0.5)'
                            ),
                            hovermode='closest',
                            height=700,
                            margin=dict(l=80, r=150, t=120, b=80),
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(family='sans-serif', size=11, color='#1a1a1a'),
                            showlegend=False
                        )
                        
                        # Add annotations for factor importance
                        fig_ternary.add_annotation(
                            text=f"<b>Factor Importance Rankings:</b><br>" +
                                 f"1️⃣ {most_important}: {importance_pct[most_important]:.1f}%<br>" +
                                 f"2️⃣ {[k for k in importance_pct.keys() if k != most_important][0]}: {importance_pct[[k for k in importance_pct.keys() if k != most_important][0]]:.1f}%<br>" +
                                 f"3️⃣ {[k for k in importance_pct.keys() if k != most_important][1]}: {importance_pct[[k for k in importance_pct.keys() if k != most_important][1]]:.1f}%",
                            xref='paper', yref='paper',
                            x=0.02, y=0.98,
                            showarrow=False,
                            bgcolor='rgba(255, 255, 255, 0.9)',
                            bordercolor='#d32f2f',
                            borderwidth=2,
                            borderpad=10,
                            font=dict(size=10, family='monospace'),
                            align='left',
                            xanchor='left',
                            yanchor='top'
                        )
                        
                        st.plotly_chart(fig_ternary, use_container_width=True, height=700)
                        
                        # Display additional insights
                        st.markdown("**📈 Response Statistics:**")
                        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                        with stats_col1:
                            st.metric("Max Response", f"{values.max():.2f}", delta_color="off")
                        with stats_col2:
                            st.metric("Min Response", f"{values.min():.2f}", delta_color="off")
                        with stats_col3:
                            st.metric("Mean Response", f"{values.mean():.2f}", delta_color="off")
                        with stats_col4:
                            st.metric("Std Dev", f"{values.std():.2f}", delta_color="off")
                        
                    else:
                        st.warning("No valid data for ternary plot")
                else:
                    st.info("Ternary plot requires Ionizable, Cholesterol, and PEG components in the design")
            except Exception as e:
                st.warning(f"Could not create ternary plot: {e}")
                import traceback
                st.error(traceback.format_exc())
            
            st.markdown("---")
            st.subheader("📊 Comprehensive Factor Analysis & Optimization Summary")
            
            # Paper-based guidance
            st.markdown("""
            ### Key Findings from Literature Analysis:
            1. **In Vitro ≠ In Vivo Efficacy**: Transfection efficiency observed in cell culture does NOT correlate with animal model performance
            2. **Special Cubic Model Required**: Lipid component effects are non-additive (interaction terms A×B×C are essential)
            3. **PEG Paradox**: Higher PEG reduces particle size but **significantly decreases both pDNA and siRNA efficacy**
            4. **Recommended pDNA Formulation**: DLin-KC2-DMA : DOPE : Cholesterol : C16-PEG2000 = **39:10:50:1** (mol%)
            5. **Key Difference**: pDNA prefers **low PEG (1%)** while delivery performance is highly sensitive to cholesterol
            """)
            
            # Create comprehensive analysis panel
            try:
                if len(valid_responses) > 0 and len(analysis_data) > 0:
                    # Prepare data for analysis
                    analysis_clean = analysis_data.copy()
                    for col in ['Ionizable_%', 'Cholesterol_%', 'PEG_%', 'Helper_%', ION_RATIO_COL]:
                        if col in analysis_clean.columns:
                            analysis_clean[col] = pd.to_numeric(analysis_clean[col], errors='coerce')
                    analysis_clean['Response'] = pd.to_numeric(analysis_clean['Response'], errors='coerce')
                    analysis_clean = analysis_clean.dropna()
                    
                    if len(analysis_clean) > 0:
                        # ============ PANEL 1: Factor Importance Ranking ============
                        st.markdown("### 1️⃣ Factor Importance Ranking")
                        
                        st.markdown(
                            "💡 **Paper Finding**: These linear correlations give first-order approximation, "
                            "but the true model requires **Special Cubic interactions** (A×B×C terms) "
                            "to capture non-additive lipid synergistic effects."
                        )
                        
                        # Calculate correlations for all factors (excluding PEG since it's fixed)
                        factor_correlations = {}
                        factor_names_display = {}
                        
                        if 'Ionizable_%' in analysis_clean.columns:
                            ion_corr = analysis_clean['Ionizable_%'].corr(analysis_clean['Response'])
                            factor_correlations['Ionizable Lipid %'] = abs(ion_corr)
                            factor_names_display['Ionizable Lipid %'] = 'Ionizable_%'
                        
                        if 'Cholesterol_%' in analysis_clean.columns:
                            chol_corr = analysis_clean['Cholesterol_%'].corr(analysis_clean['Response'])
                            factor_correlations['Cholesterol %'] = abs(chol_corr)
                            factor_names_display['Cholesterol %'] = 'Cholesterol_%'
                        
                        if 'Helper_%' in analysis_clean.columns:
                            helper_corr = analysis_clean['Helper_%'].corr(analysis_clean['Response'])
                            factor_correlations['Helper Lipid %'] = abs(helper_corr)
                            factor_names_display['Helper Lipid %'] = 'Helper_%'
                        
                        if ION_RATIO_COL in analysis_clean.columns:
                            ion_dna_corr = analysis_clean[ION_RATIO_COL].corr(analysis_clean['Response'])
                            factor_correlations[f'Ion:{na} Ratio'] = abs(ion_dna_corr)
                            factor_names_display[f'Ion:{na} Ratio'] = ION_RATIO_COL
                        
                        # Note: PEG is excluded because it's fixed at 1.5%
                        
                        # Sort by importance
                        sorted_factors = sorted(factor_correlations.items(), key=lambda x: x[1], reverse=True)
                        factor_names_sorted = [f[0] for f in sorted_factors]
                        factor_values_sorted = [f[1] for f in sorted_factors]
                        
                        # Normalize to 0-100 scale
                        if max(factor_values_sorted) > 0:
                            factor_importance_pct = [v / max(factor_values_sorted) * 100 for v in factor_values_sorted]
                        else:
                            factor_importance_pct = [0] * len(factor_values_sorted)
                        
                        # Create bar chart
                        fig_importance = go.Figure(data=[
                            go.Bar(
                                y=factor_names_sorted,
                                x=factor_importance_pct,
                                orientation='h',
                                marker=dict(
                                    color=factor_importance_pct,
                                    colorscale='RdYlGn_r',
                                    showscale=False,
                                    line=dict(color='#1a1a1a', width=1.5)
                                ),
                                text=[f'{v:.1f}%' for v in factor_importance_pct],
                                textposition='outside',
                                hovertemplate='<b>%{y}</b><br>Importance: %{x:.1f}%<extra></extra>'
                            )
                        ])
                        
                        fig_importance.update_layout(
                            title='<b>Factor Importance Scores</b><br><sub>Relative importance for response optimization</sub>',
                            xaxis_title='Importance Score (%)',
                            yaxis_title='',
                            height=350,
                            margin=dict(l=150, r=80, t=100, b=50),
                            showlegend=False,
                            font=dict(size=11),
                            paper_bgcolor='white',
                            plot_bgcolor='#f8f9fa'
                        )
                        
                        st.plotly_chart(fig_importance, use_container_width=True)
                        
                        # ============ PANEL 2: Main Effects Plots ============
                        st.markdown("### 2️⃣ Factor Main Effects (Influence on Response)")
                        
                        num_factors_to_display = min(4, len(factor_names_sorted))
                        fig_main_effects = make_subplots(
                            rows=2, cols=2,
                            subplot_titles=[name for name in factor_names_sorted[:4]],
                            specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
                                   [{'type': 'scatter'}, {'type': 'scatter'}]],
                            horizontal_spacing=0.15,
                            vertical_spacing=0.15
                        )
                        
                        colors_gradient = ['#d73027', '#fc8d59', '#fee090', '#e0f3f8', '#91bfdb', '#4575b4']
                        
                        for idx, factor_name in enumerate(factor_names_sorted[:4]):
                            row = idx // 2 + 1
                            col = idx % 2 + 1
                            factor_col = factor_names_display.get(factor_name)
                            
                            if factor_col and factor_col in analysis_clean.columns:
                                # Sort data for line plot
                                plot_data = analysis_clean[[factor_col, 'Response']].sort_values(by=factor_col)
                                
                                fig_main_effects.add_trace(
                                    go.Scatter(
                                        x=plot_data[factor_col],
                                        y=plot_data['Response'],
                                        mode='markers+lines',
                                        name=factor_name,
                                        marker=dict(
                                            size=8,
                                            color=plot_data['Response'],
                                            colorscale='RdYlGn',
                                            showscale=False,
                                            line=dict(color='white', width=1)
                                        ),
                                        line=dict(color='rgba(0,0,0,0.3)', width=2),
                                        hovertemplate=f'<b>{factor_name}</b>: %{{x:.2f}}<br>' +
                                                     f'{response_variable}: %{{y:.2f}}<extra></extra>'
                                    ),
                                    row=row, col=col
                                )
                                
                                fig_main_effects.update_xaxes(title_text=factor_name, row=row, col=col, title_font=dict(size=10))
                                if col == 1:
                                    fig_main_effects.update_yaxes(title_text=response_variable, row=row, col=col, title_font=dict(size=10))
                        
                        fig_main_effects.update_layout(
                            title='<b>Main Effects on Response</b><br><sub>How each factor individually affects the outcome</sub>',
                            height=600,
                            showlegend=False,
                            font=dict(size=10),
                            paper_bgcolor='white',
                            plot_bgcolor='#f8f9fa'
                        )
                        
                        st.plotly_chart(fig_main_effects, use_container_width=True)
                        
                        # ============ PANEL 3: Optimal Formulation Prediction ============
                        st.markdown("### 3️⃣ 🎯 Optimal Formulation Prediction")
                        
                        st.warning(
                            "⚠️ **Important**: This is based on observed data, not a predictive model. "
                            "For reliable in vivo predictions, model should have ±25% error tolerance. "
                            "Always validate with independent experiments!"
                        )
                        
                        # Find best run
                        best_idx = analysis_clean['Response'].idxmax()
                        best_response = analysis_clean['Response'].max()
                        
                        # Prepare optimal formulation
                        optimal_formulation = {}
                        pred_confidence = 0
                        
                        if 'Ionizable_%' in analysis_clean.columns:
                            optimal_formulation['Ionizable Lipid %'] = analysis_clean.loc[best_idx, 'Ionizable_%']
                        
                        if 'Cholesterol_%' in analysis_clean.columns:
                            optimal_formulation['Cholesterol %'] = analysis_clean.loc[best_idx, 'Cholesterol_%']
                        
                        if 'PEG_%' in analysis_clean.columns:
                            optimal_formulation['PEG %'] = analysis_clean.loc[best_idx, 'PEG_%']
                        
                        if ION_RATIO_COL in analysis_clean.columns:
                            optimal_formulation[f'Ion:{na} Ratio'] = analysis_clean.loc[best_idx, ION_RATIO_COL]
                        
                        # Calculate Helper %
                        ion_val = optimal_formulation.get('Ionizable Lipid %', 0)
                        chol_val = optimal_formulation.get('Cholesterol %', 0)
                        peg_val = optimal_formulation.get('PEG %', 1.5)
                        helper_val = max(0, 100.0 - ion_val - chol_val - peg_val)
                        optimal_formulation['Helper Lipid %'] = helper_val
                        
                        # Calculate confidence based on response distribution
                        response_std = analysis_clean['Response'].std()
                        response_mean = analysis_clean['Response'].mean()
                        if response_std > 0:
                            pred_confidence = min(100, ((best_response - response_mean) / response_std) * 15 + 70)
                        else:
                            pred_confidence = 85
                        
                        # Display optimal formulation in cards
                        st.markdown("**📍 Predicted Optimal Formulation:**")
                        
                        opt_col1, opt_col2, opt_col3 = st.columns([2, 2, 1])
                        
                        with opt_col1:
                            st.markdown("**Component Ratios (Molar %):**")
                            for component, value in optimal_formulation.items():
                                st.write(f"  • **{component}**: `{value:.2f}%`")
                        
                        with opt_col2:
                            st.markdown("**Expected Performance:**")
                            st.metric(f"Peak {response_variable}", f"{best_response:.2f}", 
                                     delta=f"+{best_response - response_mean:.2f} vs. mean")
                            st.metric("Confidence Level", f"{pred_confidence:.0f}%",
                                     delta="High" if pred_confidence > 80 else "Medium")
                        
                        with opt_col3:
                            st.markdown("**Statistics:**")
                            st.write(f"Based on **{len(analysis_clean)}** runs")
                            st.write(f"Mean: `{response_mean:.2f}`")
                            st.write(f"Std Dev: `{response_std:.2f}`")
                        
                        # ============ PANEL 4: Optimization Recommendations ============
                        st.markdown("### 4️⃣ 💡 Optimization Recommendations (Based on Paper Findings)")
                        
                        # Provide actionable insights
                        recommendations = []
                        
                        # PEG warning based on paper findings
                        if 'PEG_%' in analysis_clean.columns:
                            peg_in_optimal = optimal_formulation.get('PEG %', 1.5)
                            if peg_in_optimal > 2.0:
                                recommendations.append(
                                    f"⚠️ **PEG Alert**: Your optimal formulation has {peg_in_optimal:.1f}% PEG. "
                                    f"**Paper strongly recommends 1% PEG** for in vivo delivery. "
                                    f"High PEG significantly reduces transfection efficacy!"
                                )
                        
                        # Check top factors
                        if len(sorted_factors) > 0:
                            top_factor = sorted_factors[0][0]
                            top_importance = sorted_factors[0][1]
                            
                            recommendations.append(
                                f"🎯 **Priority Factor**: {top_factor} is the most critical ({factor_importance_pct[0]:.0f}% importance). "
                                f"Focus optimization efforts on this factor."
                            )
                        
                        # Check response trend
                        if len(sorted_factors) > 1:
                            second_factor = sorted_factors[1][0]
                            recommendations.append(
                                f"📈 **Secondary Factor**: {second_factor} ({factor_importance_pct[1]:.0f}% importance) should be considered "
                                f"as a secondary optimization target."
                            )
                        
                        # Suggest next steps based on confidence
                        if pred_confidence < 75:
                            recommendations.append(
                                "⚠️ **Low Confidence Alert**: Consider running more experiments around the optimal region "
                                "to improve confidence in the prediction."
                            )
                        elif pred_confidence > 85:
                            recommendations.append(
                                "✅ **High Confidence**: The predicted formulation is strongly supported by the data. "
                                "Proceed with validation studies."
                            )
                        
                        # Response variability check
                        cv = (response_std / response_mean * 100) if response_mean > 0 else 0
                        if cv > 30:
                            recommendations.append(
                                f"🔍 **High Variability**: Response variation is {cv:.1f}%. "
                                "Check for experimental noise or identify additional controlling factors."
                            )
                        
                        # Display recommendations
                        for i, rec in enumerate(recommendations, 1):
                            st.markdown(f"**{i}.** {rec}")
                        
                        # ============ PANEL 5: Interaction Analysis (if available) ============
                        if len(factor_names_sorted) >= 2:
                            st.markdown("### 5️⃣ 🔗 Factor Interactions (2D Response Maps)")
                            
                            # Create heatmaps for top 2 factor combinations
                            factor1_col = factor_names_display.get(factor_names_sorted[0])
                            factor2_col = factor_names_display.get(factor_names_sorted[1])
                            
                            if factor1_col and factor2_col and factor1_col in analysis_clean.columns and factor2_col in analysis_clean.columns:
                                # Create 2D heatmap
                                pivot_data = analysis_clean.pivot_table(
                                    values='Response',
                                    index=factor2_col,
                                    columns=factor1_col,
                                    aggfunc='mean'
                                )
                                
                                if pivot_data is not None and not pivot_data.empty:
                                    fig_heatmap = go.Figure(data=go.Heatmap(
                                        z=pivot_data.values,
                                        x=pivot_data.columns,
                                        y=pivot_data.index,
                                        colorscale='RdYlGn',
                                        text=np.round(pivot_data.values, 1),
                                        texttemplate='%{text:.1f}',
                                        textfont={"size": 9},
                                        colorbar=dict(title=response_variable),
                                        hovertemplate='<b>%{x:.2f}</b> - <b>%{y:.2f}</b><br>' +
                                                     f'{response_variable}: %{{z:.2f}}<extra></extra>'
                                    ))
                                    
                                    fig_heatmap.update_layout(
                                        title=f'<b>Interaction: {factor_names_sorted[0]} vs {factor_names_sorted[1]}</b><br>' +
                                              '<sub>Response values at different factor combinations</sub>',
                                        xaxis_title=factor_names_sorted[0],
                                        yaxis_title=factor_names_sorted[1],
                                        height=450,
                                        font=dict(size=11),
                                        paper_bgcolor='white'
                                    )
                                    
                                    st.plotly_chart(fig_heatmap, use_container_width=True)
                        
                        # ============ EXPORT OPTIMAL FORMULATION ============
                        st.markdown("---")
                        st.markdown("### 📥 Export Optimization Results")
                        
                        col_export1, col_export2 = st.columns(2)
                        
                        with col_export1:
                            if st.button("📋 Copy Optimal Formulation", key="copy_optimal"):
                                optimal_text = "Optimal LNP Formulation:\n" + "\n".join(
                                    [f"  {k}: {v:.2f}%" if '%' in k else f"  {k}: {v:.2f}" 
                                     for k, v in optimal_formulation.items()]
                                )
                                optimal_text += f"\n\nExpected {response_variable}: {best_response:.2f}\nConfidence: {pred_confidence:.0f}%"
                                st.code(optimal_text)
                        
                        with col_export2:
                            # Prepare download data
                            export_data = pd.DataFrame({
                                'Component': list(optimal_formulation.keys()),
                                'Value': list(optimal_formulation.values()),
                                'Unit': ['%', '%', '%', '%', '%'] if len(optimal_formulation) >= 5 else ['%'] * len(optimal_formulation),
                                'Performance': [best_response] + ['' for _ in range(len(optimal_formulation)-1)],
                                'Confidence': [f"{pred_confidence:.0f}%"] + ['' for _ in range(len(optimal_formulation)-1)]
                            })
                            
                            csv_buffer = export_data.to_csv(index=False)
                            st.download_button(
                                label="📊 Download Optimization Report",
                                data=csv_buffer,
                                file_name="optimal_formulation.csv",
                                mime="text/csv",
                                key="download_optimal"
                            )
                    
            except Exception as e:
                st.warning(f"Could not complete factor analysis: {e}")
            
            # Export results
            if export_results and len(valid_responses) > 0:
                # Create comprehensive analysis report
                analysis_output = run_sheet.copy()
                analysis_output['Response'] = valid_responses.values
                
                export_buffer = BytesIO()
                with pd.ExcelWriter(export_buffer, engine='openpyxl') as writer:
                    analysis_output.to_excel(writer, sheet_name='Results', index=False)
                    
                    # Statistics summary
                    stats_summary = pd.DataFrame({
                        'Metric': ['Mean', 'Std Dev', 'Min', 'Max', 'Range', 'Count'],
                        'Value': [
                        valid_responses.mean(),
                        valid_responses.std(),
                        valid_responses.min(),
                        valid_responses.max(),
                        valid_responses.max() - valid_responses.min(),
                        len(valid_responses)
                    ]
                    })
                    stats_summary.to_excel(writer, sheet_name='Statistics', index=False)
                
                export_buffer.seek(0)
                st.download_button(
                    label="📥 Download Analysis Report",
                    data=export_buffer.getvalue(),
                    file_name=f"DOE_Analysis_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    
    st.markdown("---")
    
    st.subheader("📈 Experimental Design Statistics")
    
    stat_col1, stat_col2 = st.columns(2)
    
    with stat_col1:
        st.markdown("**Design Space Coverage**")
        coverage_text = "**Factor Ranges Explored:**\n\n"
        for column, label in [("Ionizable_%", "Ionizable"), ("Helper_%", "Helper"), ("Cholesterol_%", "Cholesterol")]:
            if column in factor_ranges:
                low, high = factor_ranges[column]
                coverage_text += f"• {label}: {low:.1f} → {high:.1f}% (step {factor_steps[column]:g})\n"
            elif column == remainder_component:
                coverage_text += f"• {label}: remainder ({design_display[column].min():.1f} → {design_display[column].max():.1f}%)\n"
        coverage_text += f"• PEG: {pegdmg2000_ratio:.1f}% (fixed)\n"
        if ION_RATIO_COL in factor_ranges:
            low, high = factor_ranges[ION_RATIO_COL]
            coverage_text += f"• Ion:{na}: {low:.1f} → {high:.1f} μg/μg (step {factor_steps[ION_RATIO_COL]:g})"
        
        st.text(coverage_text)
    
    with stat_col2:
        st.markdown("**Actual Design Point Statistics**")
        stats_text = f"""Design Points Generated: {len(design_df)}
Total Experimental Runs: {len(run_sheet)}

Ionizable Lipid:
  Range: {design_display['Ionizable_%'].min():.1f}% - {design_display['Ionizable_%'].max():.1f}%
  
Cholesterol:
  Range: {design_display['Cholesterol_%'].min():.1f}% - {design_display['Cholesterol_%'].max():.1f}%
  
Helper Lipid (Calculated):
  Range: {design_display['Helper_%'].min():.1f}% - {design_display['Helper_%'].max():.1f}%
"""
        st.text(stats_text)
    
    with stat_col2:
        st.markdown("**Volume Range (µL)**")
        st.text(f"""Ion:    {run_sheet['Ionizable_Vol_uL'].min():.1f} → {run_sheet['Ionizable_Vol_uL'].max():.1f}
Helper: {run_sheet['Helper_Vol_uL'].min():.1f} → {run_sheet['Helper_Vol_uL'].max():.1f}
Chol:   {run_sheet['Chol_Vol_uL'].min():.1f} → {run_sheet['Chol_Vol_uL'].max():.1f}
PEG:    {run_sheet['PEG_Vol_uL'].min():.1f} → {run_sheet['PEG_Vol_uL'].max():.1f}""")

else:
    st.info("👈 **Start with STAGE 1: PLANNING** - Define your DOE objective, response variable, and components to begin the DOE workflow.")

    # Check feasibility and suggest adjustments
    st.info("💡 **Tip**: Wider ranges explore more of design space but may include non-functional formulations. Narrow ranges focus on known good regions.")
