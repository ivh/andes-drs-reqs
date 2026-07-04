# Requirements on the ANDES DRS work package — flow-down and assessment

Extracted from `ANDES_model.mdzip` (Cameo/MagicDraw XMI, no Cameo needed) on 2026-07-04.
Interactive diagram: `drs-flowdown.html` (also at https://claude.ai/code/artifact/59108c49-d09b-426a-bd3c-2eb304bf23f6).

## The 14 requirements linked to SW DRS

The work package is the `SW DRS` class in `6.WBS / ANDES_WP / SW Sys Eng`. Fourteen
requirements are linked to it via dependencies, from two source documents.

### ANDES Technical Requirements Specification (8)

Seven three-level derivation chains (document requirement -> SW-level -> DRS-level),
plus one requirement applying directly:

| Chain | DRS-level requirement (verbatim) |
|---|---|
| [R-AND-65] -> .3 -> **.3.SW2** | The ANDES DRS software shall be able to reduce data for seeing-limited mode data and IFU mode data |
| [R-AND-70] -> .1 -> **.1.SW1** | The DRS shall cover reduction procedure in the full wavelength range of ANDES and shall support the extension to U band and K band. The DRS shall be modular to tolerate gaps and further wavelength extensions. |
| [R-AND-88] -> .1 -> **.1.SW1** | The ANDES DRS shall not degradate the spectral resolution of the recored spectra more than [-5%; +5%] across the wavelength range |
| [R-AND-112] -> .1 -> **.1.SW1** | The ANDES DRS shall not require night-time calibrations to reduce the data and fullfil the requirements on accuracy, precisions, flux calibration and resolution. All day-time calibrations shall be valid for at least 24 hours. |
| [R-AND-114] -> .1 -> **.1.SW1** | For observations in which optimal sky subtraction is requested (one sub-FoV serving as simultaneous sky probe), the sky subtraction obtained by the DRS shall be better than 1% of the measured sky background between OH lines. |
| [R-AND-115] -> .1 -> **.1.SW1** | The ANDES Data Reduction, when interpolating onto a regular output grid, shall not increase the FWHM of a Nyquist sampled Gaussian by more than 20%. |
| [R-AND-119] -> .1 -> **.1.SW1** | DRS data product shall be fully compliance with the ELT data flow system as specified in AD-8 |
| **[R-AND-120]** (direct) | Data Reduction Software (DRS): the Pipeline shall be compliant with AD8; science grade data products for both seeing-limited and IFU modes. |

### Common Requirements for ELT Instruments (6)

[R-INS-896] -> [R-INS-896].1, which branches into three DRS-level requirements
(expressed by containment, not DeriveReqt), plus three applying directly:

- **[R-INS-896].1.SW1** — QC algorithms in the reduction cascade, QC parameters stored in FITS headers, processable during the night (RON, efficiency from standard stars, etc.)
- **[R-INS-896].1.SW2** — science grade reduction offline, interactively
- **[R-INS-896].1.SW3** — all DRS functionality based on CPL, HDRL and Reflex, supporting different use cases
- **[R-INS-928]** (direct) — reduced products conform to ESO DICD (DFS keywords) and the Science Data Product Standard for Phase 3
- **[R-INS-1049]** (direct) — science-grade reduction based on CPL and HDRL as provided by ESO (AD8 section 4.7)
- **[R-INS-1050]** (direct) — interactive data reduction adaptable to specific data sets, Phase 3-compliant products

## Assessment

### Methodology: above average

Real multi-level derivation rather than flat allocation; quantified, verifiable leaves
(±5% resolution, 1% sky subtraction, 20% FWHM growth, 24 h calibration validity);
source documents kept as versioned baselines with stable IDs; compliance status fields
maintained. Hygiene issues, minor but real:

- `[R-AND-88].1 -> [R-AND-88].1.SW1` exists only by naming convention; no modeled
  DeriveReqt relationship.
- The R-INS-896 branch expresses derivation by containment while the TRS branch uses
  DeriveReqt; two mechanisms for the same semantics makes automated queries fragile.
- Some derivations are verbatim echoes of their parent ([R-AND-115].1 and .1.SW1 are
  identical); a derivation should add an architectural decision, not copy.
- Texts need a review pass ("degradate", "recored", "fullfil", "shall be fully
  compliance").

### The main gap: the RV thread never reaches the DRS work package

The model itself knows the DRS is an RV error contributor: `Analysis & Budgets /
RV Budget / Total RV Error Budget` contains an explicit "Reduction Pipeline RV Error"
node under "Software Algorythms RV Error". But no requirement linked to SW DRS carries
any RV or wavelength-accuracy allocation. Concretely:

- **[R-SYS-4].0a** reads "The DRS shall provide a correction to the wavelength solution
  along the full slit by using spectra of the simultaneous reference..." — a DRS
  requirement by its own text — yet it is linked to the SW Sys Eng WP, not SW DRS.
- **[R-AND-84]** (wavelength precision better than 1 m/s RMS) and **[R-AND-85]**
  (stability of wavelength calibration accuracy) flow to "SW Architect - SWSE" and the
  Optical Architect, then stop.

### Other content gaps for a DRS specification

- Error propagation: no requirement for per-pixel variance and quality flags on products.
- SNR / extraction efficiency: nothing bounds signal loss relative to the photon limit.
- Flux/continuum fidelity: only indirectly referenced via [R-AND-112].
- Telluric correction: absent, despite the science living in the red/NIR.
- Throughput/latency: no "reduce faster than acquisition" or QC-latency requirement.
- Verification: none of the 14 has a Verify or Satisfy link. The practice exists
  elsewhere in the model (wavelength requirements link to "Wavelength precision -
  L1...L4" test cases) but has not been applied to the DRS set.
- Currency: [R-INS-896].1.SW3 mandates Reflex, which ESO has been superseding with
  EDPS; inherited from the Common Requirements baseline, worth checking.

### Verdict

Fulfilling these 14 yields an ESO-ecosystem-compliant pipeline (CPL/HDRL, Phase 3,
DFS keywords) that preserves resolution and sampling, handles both modes, and subtracts
sky to 1%. Necessary but not sufficient: nothing binds the pipeline to the RV error
budget, wavelength-solution accuracy, error propagation, or telluric handling — a fully
compliant DRS could still miss the science. The depth likely lives in the referenced
`E-AND-SW-SPE-*` documents outside the model, so this is probably incomplete linkage
rather than an incomplete project; but as modeled, the flow-down is a compliance
skeleton, not an acceptance basis.

Suggested actions:

1. Allocate a quantified number from "Reduction Pipeline RV Error" into a DRS-level
   requirement linked to the SW DRS WP.
2. Re-home [R-SYS-4].0a to the SW DRS WP.
3. Add the missing DeriveReqt for [R-AND-88].1 -> .1.SW1.
4. Add Verify links for the 14 (pattern already exists for the wavelength requirements).

## Method notes

Requirement-to-WP links are model dependencies whose client is the `SW DRS` class.
Upward chains follow DeriveReqt abstractions, requirement nesting (R-INS-896 subtree),
and in one case naming convention. Requirement texts are verbatim from the stereotype
attributes in the XMI (`sysml:Requirement`, `AstroMBSE_Profile:AstroMBSE_Requirement`,
`Local_Reqs_Profile:AstroMBSE_Requirement_Local`). Extraction scripts (`index_model.py`,
`trace_flowdown.py`, `gap_check.py`) are reusable for any other work package.
