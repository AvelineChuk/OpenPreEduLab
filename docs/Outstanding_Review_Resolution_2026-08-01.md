# Outstanding Review Resolution, 2026-08-01

Reviewer: `Barnabe-Zihan-Ding`

## Immediate raw-source reviews

- `GD_2019_FINAL_ACCOUNTS_SCREEN`: PDF SHA-256
  `f8779f386f664172f49a6453932e1f366d6139ec02093dd13dc42ea3184bb3e4`
  matches the manifest. Text-layer and rendered-page review confirmed Table 5
  on PDF page 17, printed page 13, unit 10,000 yuan, and 学前教育 values 6,893
  budget, 6,893 adjusted budget, and 7,094 final accounts. The title is
  explicitly provincial-level. Decision: `confirmed_context_only`.
- `GD_2020_FINAL_ACCOUNTS_SCREEN`: PDF SHA-256
  `25b72c8b1f7ae2a077114c6165aaf9b8124bb385e5277c243c13d52b2c49e6f0`
  matches the manifest. Text-layer and rendered-page review confirmed Table 5
  on PDF page 20, printed page 16, unit 10,000 yuan, and 学前教育 values 6,861
  budget, 6,861 adjusted budget, and 8,585 final accounts. Decision:
  `confirmed_context_only`; it is not total Guangdong preschool expenditure.
- `GD_YEARBOOK_2025_TABLE_3_4_SCREEN`: ZIP SHA-256
  `1415924265864a3039a2a2758082b3e3def48dcdcc38f8da3415e91b24d6a94e`
  matches the manifest. Entry `directory/03/html/03-04.htm` is present. Its
  title is `3-4 常住人口年龄结构和抚养比`, unit `万人、%`, and visible groups
  are `0-14`, `15-64`, and `65 and over`. It contains no single-year ages or
  compatible 3-5/3-6 band. Decision: `confirmed_not_definition_compatible`;
  no splitting or interpolation.
- `GD_YEARBOOK_2025_TABLE_8_2_SCREEN`: the same verified ZIP contains
  `directory/08/html/08-02.htm`. The table title is `8-2 地方一般公共预算收支基本情况`
  and its unit is `亿元`. The visible general Education row reports 921.48,
  2040.65, 3510.56, 3796.69, 3871.14, 4004.45, and 4055.57 for the table's
  displayed years, but the table has no preschool or kindergarten sub-item.
  Decision: `confirmed_context_only`; it cannot be a PRAI fiscal input.

## Shanghai provenance

The three reviews are resolved in
`docs/Shanghai_Provenance_Correction_Queue.md`. Official downloads use CRLF;
the committed files use LF. Content identity and both byte-level hashes are
documented. Population and fiscal datasets are context-only. The kindergarten
dataset remains held because its variable mappings are unresolved.

## Teacher definitions

Repository-held official tables and metadata for `BJ_KG_2015_2024`,
`GD_KG_2015_2024`, and `SC_KG_2015_2024` use `专任教师`. A repository-wide
definition search found no official statement that this is an FTE measure and
no conversion formula with year, coverage, geography, unit, and method. The
three tracker decisions therefore remain `hold_for_definition_review`.
`专任教师` must not be relabelled as `fte_teacher_count` or promoted without a
separately reviewed methodological mapping.

## Promotion decision

No raw file or staged value was changed, and nothing was added to
`datasets/processed/`.
