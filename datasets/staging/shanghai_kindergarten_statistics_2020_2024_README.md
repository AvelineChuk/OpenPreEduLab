# Shanghai Kindergarten Statistics: Staging Record

This staging table records the visible values for 2020, 2023, and 2024 from Table 20.17, *Kindergarten Basic Conditions in Selected Years*, in the 2025 Shanghai Statistical Yearbook.

The original source is retained at:

`datasets/raw/provincial_china_2015_2025/shanghai/2025_statistical_yearbook/C2017_kindergarten_basic.html`

## Status

The source is official HTML, but its legacy layout was not reliably parsed by the standard HTML-table reader. Values were transcribed from the visible official table and require an independent second review before use. The reported children, staff, and full-time-teacher values are expressed in ten-thousand persons and have been converted to persons with the recorded multiplication factor.

`children_reported_count` remains a source-faithful staging field. It must not be mapped automatically to the PRAI field `enrolled_children` until the yearbook definition has been reviewed and found equivalent.

The table provides selected years only. Missing 2015–2019 and 2021–2022 observations are intentionally absent and must not be interpolated.
