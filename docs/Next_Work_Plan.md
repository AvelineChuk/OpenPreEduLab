# Next Work Plan: Real-Data Pilot

## Immediate Objective

Advance the provincial pilot from source-faithful staging records to a small, independently reviewed, definition-compatible dataset. The immediate objective is not to produce a PRAI score. It is to establish whether a valid score can eventually be constructed.

## Completed: Inclusive Education Software Prototype

The aggregate Inclusive Education Research Module is implemented and locally
validated. It includes synthetic institution-level data, five prototype
dimension scores, Support Gap diagnostics, Researcher Mode, visualisations,
exploratory scenarios, bounded research insights, and exports. Its scores are
not empirically validated, and no inclusive-education record is approved for
`datasets/processed/`. Future work is methodological review, accessibility, and
eventual separately governed real-data validation.

Automated, code-level, and public desktop accessibility follow-up now covers
non-colour semantic chart tables, narrow-screen overflow guards, sidebar
recovery, measured key-text contrast, heatmap label contrast, visible keyboard
focus, heading hierarchy, keyboard operation of the main navigation and
Researcher Mode tabs, and a semantic Researcher Mode quick-navigation map.
Physical mobile/tablet review, verifiable 200% browser zoom, full keyboard
traversal, real screen-reader testing, third-party widget contrast, and
stakeholder review of plain language and cognitive load remain manual; see
[Inclusive Education Accessibility Check](Inclusive_Education_Accessibility_Check.md).

The first inclusive-method robustness check is also complete: Researcher Mode
now reports leave-one-item-out dimension sensitivity. It does not replace
expert content review, alternative weights, or empirical validation.

The next inclusive-method step is now specified as a prospective expert and
content-validation protocol. No expert ratings have been collected and no
content-validity claim is authorised. See
`docs/Inclusive_Education_Content_Validation_Protocol.md`.

The blank 28-item expert-review CSV, strict rating validation, threshold-free
I-CVI, S-CVI/Ave, and CVR calculation backend, and session-only completed-
rating upload interface are implemented. The cognitive-interview evidence and
versioned item-revision audit templates, validators, summaries, uploads, and
exports are also implemented. Complete instrument-version registration and
structural comparability auditing are implemented without score conversion or
automatic comparison. A separate feasibility-pilot workflow now preserves
missingness and audits completion, endpoint concentration, variation, duration,
burden, and administration modes without treating them as validity evidence.
A separate preliminary reliability workflow now calculates dimension-level
Cronbach alpha, item diagnostics, and matched repeated-administration Pearson
and ICC(3,1) summaries without automatic thresholds or validity claims.
The later policy-research readiness sequence now also documents longitudinal
event alignment, institution-level exposure definitions, identification-design
assumptions, falsification and sensitivity plans, and estimation specifications.
These are session-only planning audits. They run no causal model, estimate no
effect, approve no design, and do not convert temporal ordering into evidence
of policy impact.
The subsequent analysis-reproducibility readiness audit now records data
snapshot, checksum, code commit, environment lock, random-seed policy,
specification lock, deviations, quality-control status, and governed output
boundaries. It executes no code and verifies no result. Actual computational
reproduction requires separately authorised data, code, environment, execution,
and independent review.

The results-reporting and claim-boundary readiness audit now documents complete
reporting scope, uncertainty, multiplicity, deviations, subgroup privacy,
visualization scales, Support Gap language, causal wording, and bounded AI
review. It receives no numerical results and produces no significance, policy,
or causal conclusion.

The claim-evidence traceability readiness audit now links non-identifying claim
records to specifications, aggregate output references, uncertainty,
limitations, alternative explanations, provenance, AI origin, human review,
and disclosure status. It reads no result values and makes no truth,
publication, policy-effect, or causal judgement.

The release package readiness audit now records versioned manifests, checksums,
documentation, licenses, citations, privacy, accessibility, claim review,
Synthetic Data labels, AI disclosure, and independent review. It does not
inspect, approve, upload, or publish files.

The Methodological Readiness Navigator now organises all 25 readiness workflows
into instrument foundations, measurement evidence, longitudinal readiness,
policy-design readiness, and reproducibility and release. The downloadable
catalog improves navigation without assigning scores, approvals, or causal
status.

Actual expert recruitment, rating collection, cognitive interviews, and
instrument decisions require separate governance and human participation; they
have not been completed.

## Priority 0: Complete the 2026 Fund Provenance Chain

**Current status:** An official government republication has been verified: Xinxing County Finance Bureau's page for the Ministry of Finance and Ministry of Education notice `Caijiao [2026] No. 68`, with both XLS attachments. The local supplied files and republished files have different binary hashes but identical visible workbook content. The primary Ministry of Finance notice page has now been located: `http://jkw.mof.gov.cn/zxzyzf/zcxqjyfzzj/202604/t20260429_3988831.htm`, published 2026-04-29.

**Action:** Retain the verified republication evidence and, if available, locate the primary Ministry of Finance or Ministry of Education publication URL. Record any primary URL in the raw-source manifest without replacing the archived republication files.

**Completion condition:** The primary URL and notice identity receive an independently reviewable provenance check. This verifies provenance only; the allocation remains a future scenario parameter, not historical expenditure.

## Completed: Independent Review of Existing Staging Records

**Status:** All original staging records have an independent review decision.
The decisions include conditional policy-simulation use, context-only use, and
definition holds; none authorises a processed PRAI input. Shanghai provenance
review has been resolved, and the Guangdong 2019/2020 provincial-level
final-accounts sources have been independently confirmed as context-only.

## Priority 2: Preschool-Age Population

**Required variable:** Annual provincial or municipal population aged 3–5 or 3–6, with a documented definition and unit.

**Acceptable sources:** Official population-census tables, population-sampling reports, provincial education statistics, or authorised administrative enrolment-demand records.

**Do not use as a substitute:** Total resident population, registered population, birth rate, or the broad 0–14 age group.

## Priority 3: Preschool-Specific Public Expenditure

**Required variable:** Annual public expenditure explicitly identified as preschool or kindergarten expenditure, with a compatible child denominator where per-child intensity is required.

**Acceptable sources:** Education-expenditure statistics, education-department final accounts, finance-department final accounts, or programme documents with a clear expenditure definition.

**Do not use as a substitute:** General education expenditure, general public-budget expenditure, or an unverified future allocation.

**Current source boundary:** The archived Guangdong 2017, 2019, and 2020
provincial-level final-accounts tables are narrow fiscal context references,
not Guangdong-wide or per-child inputs. All three have completed independent
scope review. See `docs/Fiscal_Source_Search.md`.

## Priority 4: Gansu Source Acquisition

**Action:** Obtain Gansu official yearbooks or education-statistics files through normal authorised browser access. Store originals under `datasets/raw/provincial_china_2015_2025/gansu/`, then register URL, publisher, year, table title, checksum, geographic level, and variable definition before transcription.

## Priority 5: Processed Pilot and Software-Flow Check

Only after the above gates are met for a definition-compatible subset should approved records be copied to `datasets/processed/`. The first pipeline execution should be treated as a reproducibility and software-flow check, not a real policy evaluation.

## Completed: Repository Synchronisation

On 31 July 2026, the local `main` branch was fetched and normally pushed to
`origin/main`. Future updates should continue to use normal fetch and push
operations; force push is not permitted.
