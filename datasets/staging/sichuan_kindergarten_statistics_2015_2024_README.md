# Sichuan Kindergarten Statistics: Staging Record

This staging table records three kindergarten variables visibly published in the 2025 Sichuan Statistical Yearbook: kindergarten count, children enrolled in kindergartens, and full-time kindergarten teacher count. The three original tables are retained under `datasets/raw/provincial_china_2015_2025/sichuan/2025_statistical_yearbook/` and their SHA-256 checksums are recorded in the accompanying raw-source manifest.

The values are a manual, source-faithful transcription of Tables 20-1, 20-2, and 20-3, each of which supplies a long historical provincial series. `teaching_staff` is not inferred because the selected tables report only full-time teachers. The city/prefecture table (20-19) is retained as context and is not summed to manufacture a provincial value.

All rows require an independent second review before promotion to `datasets/processed/`. The notable declines in enrolment in 2023 and 2024, and in kindergarten count in 2024, are retained and flagged for definition and transcription review; they are not removed or smoothed.
