# Beijing Open Data Platform Archive

This directory retains original files manually downloaded from the Beijing Government Data Open Platform. The raw files are not modified after archival.

## Current File

`北京市教育委员会-各级教育生均一般公共预算公用经费支出增长情况.csv` contains district-level records for 16 Beijing districts in update years 2023 and 2025. `市教委-各级教育生均一般公共预算教育事业费支出增长情况.csv` contains the same 16 districts for update year 2023. Their kindergarten fields describe per-student general public-budget expenditure measures, not confirmed measures of preschool-specific public expenditure. `北京市教育委员会-一般公共预算教育经费增长情况（公开）.csv` contains general education-budget context for the same 16 districts in 2023 and 2025; it is not preschool-specific.

The current real-data pilot is provincial-level. This file must not be summed or otherwise transformed into a Beijing municipal observation, and it must not be copied to `datasets/staging/` for the provincial PRAI panel. It is preserved for provenance and for a possible future, separately designed district-level extension.
