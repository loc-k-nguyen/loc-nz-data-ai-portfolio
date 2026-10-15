# Power BI Field Mapping

| Field | Power BI data type | Dashboard role | Notes |
| --- | --- | --- | --- |
| `period` | Text | Slicer, table display | Use for readable period labels. |
| `period_date` | Date | Time axis, latest-period measure | Confirm Power BI imports this as Date. |
| `year` | Whole Number | Slicer, grouping | Useful for annual filtering. |
| `quarter` | Whole Number | Slicer, grouping | Values should be 1 to 4. |
| `geography_type` | Text | Slicer, filter | Valid levels are `NZ` and `TA`; do not invent regions. |
| `area_id` | Whole Number | Key/reference field | Use for identifying areas, not as a measure. |
| `geography_name` | Text | Axis, legend, table display | Contains `New Zealand` and TA names. |
| `territorial_authority` | Text | Axis, slicer, table display | Blank for `NZ` rows; use for TA comparisons. |
| `theme` | Text | Slicer, grouping | Examples include `Affordability`, `MSD`, `Bonds`, `Sales`. |
| `indicator_name` | Text | Primary slicer, chart title context | Use to select the dashboard indicator. |
| `indicator_value` | Decimal Number | Measure/value | Use in cards, bars, and line charts. |
| `unit` | Text | Tooltip, table, chart title context | Example: `index`; may be blank for some indicators. |
| `ethnicity` | Text | Slicer, caveat field | May be blank depending on indicator. |
| `source` | Text | Methodology/source page | Use in methodology page or tooltip. |

