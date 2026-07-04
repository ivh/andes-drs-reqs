# ANDES Cameo model analysis

`ANDES_model.mdzip` and `AstroMBSE_Profile.mdzip` are Cameo Systems Modeler (MagicDraw)
projects for the ANDES spectrograph (ELT). They are zip archives; the model is standard
XMI (UML 2.5/SysML) and fully parseable without Cameo.

## File format

- The model is the zip entry `com.nomagic.magicdraw.uml_model.model` (~150 MB XML).
- `BINARY-*` entries are RTF element descriptions (embedded images), not diagrams.
- Diagram layouts are Cameo-proprietary; diagram names and contents are extractable,
  renderings are not.

## Model conventions (non-obvious, verified against the XMI)

- Requirement Id/Text live in stereotype attributes on: `sysml:Requirement`,
  `AstroMBSE_Profile:AstroMBSE_Requirement`, `AstroMBSE_Profile:AstroMBSE_Interface_Requirement`,
  `Local_Reqs_Profile:AstroMBSE_Requirement_Local` (working copies of the ESO Common
  Requirements use only the last one).
- Requirement-to-work-package allocation: plain unstereotyped `uml:Dependency`,
  WBS work-package class as client, requirement as supplier.
- Flow-down is expressed three ways: `DeriveReqt` abstractions, containment nesting
  (e.g. R-INS-896 subtree), and sometimes naming convention only (no modeled link).
- One dependency can carry multiple stereotypes (e.g. DeriveReqt + track).
- Document section headings are requirement-stereotyped classes too; real requirements
  have bracketed names like `[R-AND-65]`.

## Tools (in tools/, run with uv from this directory)

All have PEP 723 headers, so plain `uv run` works.

1. Extract: `unzip -o ANDES_model.mdzip -d extracted/` (extracted/ is disposable).
2. `uv run tools/outline.py extracted/com.nomagic.magicdraw.uml_model.model [depth]`
   — package tree and diagram list.
3. `uv run tools/index_model.py extracted/com.nomagic.magicdraw.uml_model.model model_index.pkl`
   — one-time index (elements, requirements, dependencies, stereotypes); the pickle is
   what the other scripts read. Takes a minute or two.
4. `uv run tools/trace_flowdown.py` — requirements linked to a WBS work package plus
   their upward derivation chains; writes `flowdown.json`. The WP element id is
   hardcoded near the top (currently SW DRS); find another WP's id via the index.
5. `uv run tools/gap_check.py` — the RV/wavelength-calibration gap analysis and
   Verify/Satisfy link check for the DRS requirement set; query patterns are reusable.
6. `uv run tools/gen_viz.py` — turns flowdown.json into the grid cells of
   drs-flowdown.html (row layout is hand-ordered for the DRS analysis).

## Results so far

- `drs-flowdown.md` — the 14 requirements on the SW DRS work package, derivation
  chains, and SE assessment (main finding: the RV error budget thread never reaches
  the DRS WP; no Verify/Satisfy links on any of the 14).
- `drs-flowdown.html` — self-contained flow-down diagram of the same.
