"""Methodological-readiness registry for Inclusive Education Researcher Mode."""

from __future__ import annotations

from typing import Final

import pandas as pd


PHASE_ORDER: Final[tuple[str, ...]] = (
    "1. Instrument foundations",
    "2. Measurement evidence",
    "3. Longitudinal readiness",
    "4. Policy-design readiness",
    "5. Reproducibility and release",
)

_WORKFLOWS: Final[tuple[tuple[str, str, str, str, str, str], ...]] = (
    (PHASE_ORDER[0], "Expert content review", "Are proposed items relevant and clear?", "Threshold-free review summaries", "Prospective expert evidence; no validity claim", "Inclusive_Education_Content_Validation_Protocol.md"),
    (PHASE_ORDER[0], "Cognitive interview and item revision", "How are items understood and revised?", "Human-entered evidence and decision logs", "No simulated interviews or automatic item decisions", "Inclusive_Education_Cognitive_Interview_Protocol.md"),
    (PHASE_ORDER[0], "Instrument version comparability", "What changed between instrument versions?", "Structural change inventory", "No score conversion or empirical comparability claim", "Inclusive_Education_Versioning_Protocol.md"),
    (PHASE_ORDER[0], "Feasibility pilot and data quality", "Can the instrument be administered as planned?", "Completion, missingness, duration, and burden summaries", "No imputation, validity judgement, or item removal", "Inclusive_Education_Feasibility_Protocol.md"),
    (PHASE_ORDER[1], "Preliminary reliability", "How consistent are complete responses in the observed sample?", "Alpha, item diagnostics, Pearson, and ICC summaries", "Reliability does not establish validity or fairness", "Inclusive_Education_Reliability_Protocol.md"),
    (PHASE_ORDER[1], "Exploratory construct structure", "Is exploratory component analysis feasible?", "KMO, Bartlett, eigenvalues, and PCA loadings", "Not CFA, EFA validation, or factor-count approval", "Inclusive_Education_Construct_Structure_Protocol.md"),
    (PHASE_ORDER[1], "Subgroup measurement comparability", "Are descriptive response structures similar across groups?", "Coverage, distributions, SMDs, and correlation differences", "No invariance, DIF, bias, or group-effect claim", "Inclusive_Education_Subgroup_Comparability_Protocol.md"),
    (PHASE_ORDER[1], "External measure relationships", "How do scores relate to an independent institutional measure?", "Pearson, Spearman, and approximate intervals", "Correlation does not establish validity or causality", "Inclusive_Education_External_Measure_Protocol.md"),
    (PHASE_ORDER[1], "Alternative item-weight sensitivity", "How sensitive are summaries to declared item weights?", "Baseline-versus-alternative score and Gap comparisons", "No learned, optimal, recommended, or adopted weights", "Inclusive_Education_Weight_Sensitivity_Protocol.md"),
    (PHASE_ORDER[1], "Bootstrap sampling uncertainty", "How variable are aggregate sample summaries under resampling?", "Bootstrap bias, standard errors, and percentile intervals", "No representativeness, significance, or causal claim", "Inclusive_Education_Bootstrap_Uncertainty_Protocol.md"),
    (PHASE_ORDER[2], "Longitudinal panel readiness", "Are repeated institutional observations linkable across rounds?", "Round coverage, matching, and aggregate change summaries", "Time order is not improvement or policy-effect evidence", "Inclusive_Education_Longitudinal_Readiness_Protocol.md"),
    (PHASE_ORDER[2], "Attrition and panel composition", "Who is retained, exits, or enters between rounds?", "Retention, entry, and bounded aggregate comparisons", "No missingness mechanism, bias diagnosis, or weights", "Inclusive_Education_Attrition_Protocol.md"),
    (PHASE_ORDER[2], "Paired longitudinal Bootstrap", "How uncertain are matched aggregate mean changes?", "Paired-resampling bias, SEs, and percentile intervals", "No significance, improvement, or causal conclusion", "Inclusive_Education_Paired_Longitudinal_Bootstrap_Protocol.md"),
    (PHASE_ORDER[2], "Timing and fieldwork metadata", "Are round timing and fieldwork conditions documented?", "Collection-window and implementation metadata summaries", "Metadata differences are prompts, not quality judgements", "Inclusive_Education_Longitudinal_Metadata_Protocol.md"),
    (PHASE_ORDER[2], "Longitudinal measurement comparability", "Are response distributions descriptively comparable across rounds?", "Round distributions, SMDs, matching, and correlations", "No invariance, DIF, bias, or substantive-change claim", "Inclusive_Education_Longitudinal_Comparability_Protocol.md"),
    (PHASE_ORDER[2], "Longitudinal analysis plan", "Is the planned contrast and estimand documented?", "Analysis-plan summary and unresolved prompts", "No method selection, model fitting, or plan approval", "Inclusive_Education_Longitudinal_Analysis_Plan_Protocol.md"),
    (PHASE_ORDER[2], "Policy and context event alignment", "How do documented events align with collection windows?", "Chronology, overlap, scope, and verification summaries", "Temporal alignment does not establish exposure or effects", "Inclusive_Education_Longitudinal_Event_Alignment_Protocol.md"),
    (PHASE_ORDER[3], "Event exposure definition", "How would institution-level exposure be defined?", "Scope, timing, intensity, lag, and comparator records", "No inferred treatment, dose, policy effect, or causality", "Inclusive_Education_Event_Exposure_Protocol.md"),
    (PHASE_ORDER[3], "Identification-design readiness", "Which assumptions would a proposed design require?", "Design declarations and identification prompts", "A design label does not establish identification", "Inclusive_Education_Identification_Design_Protocol.md"),
    (PHASE_ORDER[3], "Falsification and sensitivity plan", "Which diagnostics and alternative specifications are planned?", "Pretrend, placebo, negative-control, and sensitivity plan", "Favourable diagnostics would not prove causality", "Inclusive_Education_Falsification_Plan_Protocol.md"),
    (PHASE_ORDER[3], "Estimation specification", "What exact outcome, estimand, estimator, and uncertainty plan is proposed?", "Specification summary and unresolved prompts", "No model, coefficient, p-value, or effect estimate", "Inclusive_Education_Estimation_Specification_Protocol.md"),
    (PHASE_ORDER[4], "Analysis reproducibility", "Can execution be reconstructed from versioned artefacts?", "Snapshot, commit, environment, seed, and review record", "No code execution, result verification, or method approval", "Inclusive_Education_Analysis_Reproducibility_Protocol.md"),
    (PHASE_ORDER[4], "Results reporting and claim boundaries", "How will complete results and uncertainty be disclosed?", "Reporting, privacy, Support Gap, causal, and AI plan", "Receives no result values and verifies no finding", "Inclusive_Education_Results_Reporting_Protocol.md"),
    (PHASE_ORDER[4], "Claim-evidence traceability", "Can each planned statement be linked to bounded evidence?", "Evidence, uncertainty, limitation, and review links", "No truth, validity, publication, or causal judgement", "Inclusive_Education_Claim_Traceability_Protocol.md"),
    (PHASE_ORDER[4], "Release package readiness", "Is a governed aggregate release candidate documented?", "Manifest, checksum, license, privacy, and review status", "Does not inspect, approve, upload, or publish files", "Inclusive_Education_Release_Readiness_Protocol.md"),
)


def method_readiness_catalog() -> pd.DataFrame:
    """Return the ordered methodological-readiness workflow catalog."""
    return pd.DataFrame(
        _WORKFLOWS,
        columns=(
            "phase",
            "workflow",
            "research_problem",
            "prototype_output",
            "interpretation_boundary",
            "protocol_document",
        ),
    )


def filter_method_readiness_catalog(phase: str | None = None) -> pd.DataFrame:
    """Return all workflows or the workflows in one declared phase."""
    catalog = method_readiness_catalog()
    if phase in (None, "", "All phases"):
        return catalog
    if phase not in PHASE_ORDER:
        raise ValueError(f"Unknown methodological-readiness phase: {phase}")
    return catalog[catalog["phase"].eq(phase)].reset_index(drop=True)
