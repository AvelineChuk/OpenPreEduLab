# Shanghai Raw-Provenance Correction Queue

## Renewed review resolution

Resolved on 2026-08-01 by `Barnabe-Zihan-Ding` without changing any manifest,
raw file, or staging value.

The manifest hashes identify the official HTTP response bytes, which use CRLF
line endings. The current worktree files use LF line endings. Re-inserting CR
before every retained LF reproduces each manifest hash exactly. A fresh download
from every official URL also reproduces the manifest hash. Git history shows no
later content overwrite. The discrepancy is therefore a byte-representation
difference, not a value or source-identity change.

| Review ID | Official URL | Official / manifest CRLF SHA-256 | Worktree LF SHA-256 | Renewed decision |
| --- | --- | --- | --- | --- |
| `SH_KG_2020_2024` | `https://tjj.sh.gov.cn/tjnj/2025tjnj/C2017.htm` | `4ac93b23b584dfb10963c6abb928596959270232d67b4b6761658ebc34afa3cf` | `ce0bbf527b71188b4289616047f47528e6bd3be4b488db1c0ec09b48b6ba597f` | `hold_for_definition_review` |
| `SH_POP_CONTEXT_2015_2024` header | `https://tjj.sh.gov.cn/tjnj/2025tjnj/C02/C0201A.htm` | `7167d306421840a943253a4dc698034546fd739f033cedddc4fbab646bbd1dfd` | `7e772928627c4301c0cd41d9adf26af6a59d93e41077a07d8f88254645073230` | `approved_context_only` |
| `SH_POP_CONTEXT_2015_2024` main | `https://tjj.sh.gov.cn/tjnj/2025tjnj/C02/C0201B.htm` | `eaf746de0d58becc0ded4d229f5ce89fa535d9f9a4d5fb5f2107cc6c5168da07` | `18224fdaea7c2b8cb0be296d0a7d119ec7049f61bddcf256532248e796fcb62b` | `approved_context_only` |
| `SH_FISCAL_CONTEXT_2015_2024` header | `https://tjj.sh.gov.cn/tjnj/2025tjnj/C04/C0401A.htm` | `ef340591886e8c668684ba1d1e3302587df64f138a80dc38fa2e6a84f98e9838` | `9ca0257b31e2604524f0598241abb18195d6508d511aafa0485f046aa4689a69` | `approved_context_only` |
| `SH_FISCAL_CONTEXT_2015_2024` main | `https://tjj.sh.gov.cn/tjnj/2025tjnj/C04/C0401B.htm` | `15b636561673d38e26d7bddd897e624dac5d48a3ec72f4ce6fdf7acc57406587` | `bfab0f2ce7c6783b3a1a843babee010a844e8a619c960f2058a9742ad121539e` | `approved_context_only` |

The official URLs were retrieved again on 2026-08-01. The population tables
remain general context rather than a preschool-age denominator. The fiscal
table remains a general public-budget aggregate rather than preschool-specific
expenditure. The kindergarten table remains held because `幼儿数` comparability
and the mapping from `专任教师` to FTE are unresolved. Nothing is authorized for
promotion to `datasets/processed/`.
