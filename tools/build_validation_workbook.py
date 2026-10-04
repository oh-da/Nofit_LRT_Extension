"""Assemble Output/validation_mot/validation_workbook.xlsx from the CSV outputs of the MoT validation notebooks.

Usage:  python3 tools/build_validation_workbook.py
One sheet per test (matched data and metrics) plus a Summary sheet with one row per guideline check:
guideline reference, level, criterion, result, status (pass / miss (explained) / miss (unexplained) / not run / not applicable), explanation, data vintage.
"""
import os, glob
import pandas as pd
OUT = 'Output/validation_mot'
summ = pd.concat([pd.read_csv(p) for p in sorted(glob.glob(f'{OUT}/summary_stage*.csv'))], ignore_index=True)
order = {'T1': 0, 'T4': 1, 'T5': 2, 'T7': 3, 'T8': 4, 'T12': 5, 'T14': 6, 'T15': 7, 'T17': 8}
summ['_o'] = summ['test'].map(order); summ = summ.sort_values('_o', kind='stable').drop(columns='_o')
sheets = {
    'Summary': [summ],
    'T4_trip_length_KS': ['T4_trip_length_KS', 'T4_survey_distance_by_purpose', 'T4_survey_distance_by_sector'],
    'T5_CR_vs_cellular': ['T5_coincidence_ratio'],
    'T7_transit_OD_fit': ['T7_transit_OD_fit', 'T7_matched_cells_superzone'],
    'T8_time_of_day': ['T8_car_profile_vs_counts', 'T8_transit_profile_vs_ravkav'],
    'T12_cordon_sectors': ['T12_cordon_summary', 'T12_cordon_sectors'],
    'T14_bus_origins': ['T14_bus_origins_summary', 'T14_bus_origins_by_superzone', 'T14_bus_origins_TAZ'],
    'T15_rail_stations': ['T15_rail_stations', 'T15_rail_station_size_classes', 'T15_rail_origins_by_superzone'],
    'T17_running_times': ['T17_bus_running_times', 'T17_bus_running_times_by_length', 'T17_door_to_door_vs_survey'],
}
with pd.ExcelWriter(f'{OUT}/validation_workbook.xlsx', engine='openpyxl') as xw:
    readme = pd.DataFrame({'item': ['source', 'frozen version', 'criteria', 'status words', 'periods', 'stage notebooks'],
                           'text': ['Ministry of Transport, Systems Planning, round table on transport models: Validation of the metropolitan models 2024, draft 6 (16 Sep 2024)',
                                    '23 September 2026 rebuild of the survey-based layers (steps 15-36); nothing in the chain is changed by the validation',
                                    'as printed in the guideline; implemented in tools/validation_metrics.py', 'pass / miss (explained) / miss (unexplained) / not run / not applicable / finding',
                                    'AM 06:00-09:00 only (PM and midday matrices are extension X1 of docs/MOT_VALIDATION_PLAN.md)',
                                    'notebooks/diagnostics/MOT_Validation_Stage1_Inputs_Distribution, _Stage2_Timing, _Stage3_Counts_Transit']})
    readme.to_excel(xw, sheet_name='README', index=False)
    for name, parts in sheets.items():
        row = 0
        for p in parts:
            df = p if isinstance(p, pd.DataFrame) else pd.read_csv(f'{OUT}/{p}.csv')
            if not isinstance(p, pd.DataFrame) and row > 0:
                pd.DataFrame({p: ['']}).to_excel(xw, sheet_name=name, startrow=row, index=False, header=True); row += 2
            elif not isinstance(p, pd.DataFrame):
                pd.DataFrame({p: ['']}).to_excel(xw, sheet_name=name, startrow=row, index=False, header=True); row += 2
            df.to_excel(xw, sheet_name=name, startrow=row, index=False); row += len(df) + 3
    for ws in xw.book.worksheets:
        for col in ws.columns:
            w = max((len(str(c.value)) for c in col[:60] if c.value is not None), default=8)
            ws.column_dimensions[col[0].column_letter].width = min(max(10, w + 2), 70)
print('written', f'{OUT}/validation_workbook.xlsx', f'({len(summ)} summary rows)')
