---
title: LNP Formulation Calculator
emoji: 🧬
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.52.2"
app_file: src/homepage.py
pinned: false
---

# HuggfaceLNP - Advanced LNP Formulation & DOE Tool

A comprehensive Streamlit application for Lipid Nanoparticle (LNP) formulation design and Design of Experiments (DOE) optimization.

## Features

### 🧬 Core Tools
- **LNP Formulation Calculator**: Rapid N/P ratio calculations and molar compositions
- **Design of Experiments (DOE)**: Professional DOE platform with 7 design types
- **Response Surface Design (RSM)**: Quadratic modeling with Box-Behnken and Central Composite designs
- **High-Throughput Formulation**: Batch experimental design and run sheet generation
- **DNA-Additional Components**: Multi-step LNP formulation with DNA-binding compounds
- **FDA Approved Formulations**: Reference database of clinically relevant LNP formulations

### 🎯 DOE Capabilities

#### Design Types (7 Methods)
1. **Full Factorial (2-Level)**: 2^k comprehensive screening
2. **Full Factorial (3-Level)**: 3^k detailed parameter mapping
3. **Fractional Factorial**: 2^(k-p) efficient screening for 4+ factors
4. **Plackett-Burman**: 12-run screening for main effects only
5. **Box-Behnken**: 3-level RSM without corner points
6. **Central Composite**: Full quadratic RSM with selectable alpha
7. **Mixture Design**: Component ratio optimization

#### Response Surface Design (RSM) ⭐ **NEW**
- **Box-Behnken**: Balanced 3-level design, excellent interior prediction
  - Best for: Constraint-aware optimization, fewer runs needed
  - Avoids corner points, ideal for LNP validity ranges
  
- **Central Composite**: Full factorial + axial + center points
  - **Alpha Parameter Control**:
    - **Orthogonal** (α = √k): JMP default, independent blocking
    - **Face-Centered** (α = 1): No extrapolation beyond bounds
    - **Rotatable** (α = 2^(k/4)): Constant prediction variance
  - Best for: Full quadratic exploration with flexible bounds

#### JMP-Standard Diagnostics
- **D-Efficiency**: Parameter estimation quality (0-1 scale)
- **A-Efficiency**: Prediction variance optimization
- **Condition Number**: Matrix stability assessment
- **Degrees of Freedom**: Statistical power evaluation

### 📊 Experimental Output
- Complete run sheets with randomization and blocking
- N/P ratio calculations for each experimental point
- Volume/mass calculations for all components
- Export to Excel for lab execution
- Design history and tracking

### 📐 LNP-Specific Features
- Automatic mixture constraint handling (sum = 100%)
- N/P ratio targeting for ionizable-DNA complexes
- Helper lipid, cholesterol, and PEG-lipid optimization
- Aqueous-to-ethanol ratio management
- Batch volume calculations
- Component solubility validation

## Technical Stack

- **Framework**: Streamlit 1.52.2
- **Data**: Pandas 2.3.3, NumPy 2.4.0
- **Visualization**: Plotly 6.5.0, Matplotlib 3.10.8
- **Statistics**: JMP-aligned design efficiency metrics
- **Export**: openpyxl for Excel generation

## Installation & Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run src/homepage.py
```

## File Structure

```
HuggfaceLNP/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── RSM_IMPLEMENTATION_GUIDE.md        # Response Surface Design documentation
├── Data/                              # Supporting data files
├── src/
│   ├── homepage.py                   # Main landing page
│   └── pages/
│       ├── 1_🔬_General_info.py      # General LNP information
│       ├── 2_🧬_LNP_Formulation_Calculator.py
│       ├── 3_💊_FDA_Approved_Formulations.py
│       ├── 4_🀄️_High-Throughput_Formulation.py  # DOE/RSM core
│       ├── 5_📚_References.py
│       ├── 6_⚗️_Fifth_Compoents.py
│       └── 7_🔬_DNA_additional_Compoents.py
└── venv/                              # Virtual environment
```

## Usage Workflow

### Quick Start: DOE Optimization
1. **Homepage**: Review available tools and objectives
2. **Stage 1 - Planning**: Define DOE objective and response variable
3. **Stage 2 - Screening**: Select factors and ranges (if screening design)
4. **Stage 3 - Optimization**: Choose design type and parameters
   - For quadratic effects: Select **Box-Behnken** or **Central Composite**
   - For response surface designs: Configure **alpha parameter** (RSM only)
5. **Stage 4 - Verification**: Review run sheet, export to Excel
6. **Lab Execution**: Run experiments using generated protocol

### Response Surface Design Selection

| Design | Runs | Factors | When to Use |
|--------|------|---------|------------|
| **Box-Behnken** | 3k+1 | 3-8 | Constraint-aware, no corners, efficient |
| **CCD-Orthogonal** | 2^k+2k+1 | 2-8 | Standard quadratic modeling |
| **CCD-Face** | 2^k+2k+1 | 2-8 | Strict bounds required |
| **CCD-Rotatable** | 2^k+2k+1 | 2-8 | Uniform prediction needed |

## Key Innovations

✅ **JMP-Standard Compliance**: Follows JMP DOE platform best practices
✅ **RSM Alpha Control**: Selectable alpha parameter for CCD optimization
✅ **LNP Constraint Handling**: Automatic mixture ratio validation
✅ **Design Efficiency Metrics**: Real-time D/A-efficiency diagnostics
✅ **Lab-Ready Output**: Complete experimental protocols and run sheets
✅ **Multi-Block Support**: Randomization and blocking structures

## Documentation

- **In-App Guidance**: Comprehensive help throughout the interface
- **Design Recommendations**: Context-specific suggestions based on factors
- **DOE Theory**: Detailed explanations of each design type
- **RSM Guide**: See `RSM_IMPLEMENTATION_GUIDE.md` for Response Surface Design details
- **JMP Reference**: https://www.jmp.com/support/help/en/17.0/jmp/overview-of-response-surface-designs.shtml

## Troubleshooting

### Invalid Design Points After Filtering
The constraint that all lipid components sum to 100% may remove edge points. Solutions:
- Expand factor ranges slightly
- Use Box-Behnken (efficient, constraint-aware)
- Use Face-Centered CCD to stay within bounds

### Negative Ethanol Volumes
Some factor combinations exceed physical limits. Causes:
- High ionizable lipid % + high Ion:DNA ratio
- Adjust ranges or increase final LNP volume

### Design Efficiency Low
For exploratory designs, efficiency naturally varies. Tips:
- Use larger replicates for better statistics
- Consider sequential two-stage design (Screening → Optimization)
- Verify factor ranges are appropriate

## Version History

**v1.0** (Current)
- ✅ Virtual environment setup with 35+ packages
- ✅ 7 DOE design types
- ✅ Response Surface Designs (Box-Behnken, Central Composite)
- ✅ JMP-standard efficiency diagnostics
- ✅ LNP-specific constraint handling
- ✅ Professional run sheet generation

## Contributing

Suggestions and improvements welcome. Areas for enhancement:
- Custom blocking patterns
- Sequential experimentation support
- Advanced mixture constraints
- Prediction surface visualization

## References

1. JMP Response Surface Design Platform
   https://www.jmp.com/support/help/en/17.0/jmp/overview-of-response-surface-designs.shtml

2. Box-Behnken Design
   Box, G.E.P. and Behnken, D.W. (1960). "Some three-level designs for the study of quantitative variables"

3. Central Composite Design  
   Box, G.E.P. and Wilson, K.B. (1951). "On the experimental attainment of optimum conditions"

4. Rotatable Designs
   Box, G.E.P. and Hunter, J.S. (1957). "Multi-factor experimental designs for exploring response surfaces"

## License

Educational use. For commercial applications, consult institutional guidelines.

---

**Last Updated**: January 2025
**Alignment**: JMP DOE Platform Standards
**Focus**: LNP Formulation Optimization & Response Surface Design
