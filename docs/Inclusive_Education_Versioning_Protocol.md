# Inclusive Education Instrument Versioning and Comparability Protocol

## 1. Purpose and boundary

This protocol governs item-set version registration and structural comparison for the aggregate Inclusive Education research instrument. It prevents silent comparison of scores calculated from different item definitions, dimensions, response scales, or weights.

The audit is not an equating, linking, calibration, measurement-invariance, or causal model. It never creates a score conversion and never authorises direct cross-version comparison.

## 2. Complete version snapshots

Every registered instrument version must contain a complete snapshot of its active items across all five dimensions. A version record includes version and release metadata, stable item ID, predecessor item ID where applicable, dimension, wording, response interval, item weight, change type, comparability assessment, limitation note, and governance status.

Weights must be positive and sum to 1 within each version and dimension. This records the declared scoring rule; it does not establish that the weights are valid.

## 3. Stable identities and predecessors

Unchanged items should retain stable item IDs. Revised, moved, or split items must identify predecessor items. Newly added baseline items do not claim predecessors. A split may create multiple new item IDs that refer to one predecessor.

Predecessor metadata supports provenance only. It does not prove that the old and new items measure the same construct.

## 4. Structural audit

For a selected source and target version, the software reports:

- source, target, shared, added, and removed item counts;
- item counts and overlap within each dimension;
- shared-item dimension changes;
- shared-item wording changes;
- response-scale changes; and
- weight changes.

The audit uses registered metadata only. It does not inspect respondent-level distributions or estimate statistical equivalence.

## 5. Interpretation rules

If any item is added, removed, moved, reworded, rescaled, or reweighted, the platform marks a structural change and states that direct score comparison or conversion is not authorised without a separately justified linking or recalibration study.

If no registered structural difference is found, the platform reports structural alignment only. Empirical comparability is still not established. Administration mode, translation, sampling, respondent interpretation, data collection, and population differences may still break comparability.

## 6. Required future evidence

Depending on the research question and design, future comparability work may require common-item designs, bridge samples, cognitive evidence, reliability analysis, construct analysis, differential item functioning, measurement invariance, calibration, or other explicitly justified methods. No one method is automatically appropriate.

## 7. Governance and reproducibility

Released or retired versions should not be silently overwritten. Each new version requires a dated snapshot, documented decision trail, safeguarding and equity/accessibility review, and limitations. The Streamlit prototype processes uploaded registries in the current session and does not intentionally persist them.

No institution, teacher, child, family, clinical, or case data belong in the version registry.

## 8. Completion criteria

A structural audit is complete when both version snapshots pass validation, all detected changes are documented, limitations are visible, and the research team records whether a separate empirical linking study is needed. Completion does not mean the versions are interchangeable. Once a version is ready for governed administration, software-level collection review should follow the [Feasibility Pilot and Data Quality Protocol](Inclusive_Education_Feasibility_Protocol.md).
