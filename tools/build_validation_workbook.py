"""Assemble Output/validation_mot/validation_workbook.xlsx from the CSV outputs of the MoT validation notebooks.

Usage:  python3 tools/build_validation_workbook.py
One sheet per test (matched data and metrics) plus a Summary sheet with one row per guideline check:
guideline reference, level, criterion, result, status (pass / miss (explained) / miss (unexplained) / not run / not applicable), explanation, data vintage.
"""
import os, glob
import pandas as pd
OUT = 'Output/validation_mot'
summ = pd.concat([pd.read_csv(p) for p in sorted(glob.glob(f'{OUT}/summary_*.csv'))], ignore_index=True)
if 'period' not in summ.columns: summ['period'] = 'AM'
summ['period'] = summ['period'].fillna('AM')
summ = summ[['period'] + [c for c in summ.columns if c != 'period']]
summ['_p'] = summ['period'].map({'AM': 0, 'PM': 1, 'MD': 2})
order = {'T1': 0, 'T2': 0.3, 'T3': 0.6, 'T4': 1, 'T5': 2, 'T6': 2.5, 'T7': 3, 'T7b': 3.5, 'T8': 4, 'T9': 4.3, 'T10': 4.6, 'T11': 4.8, 'T12': 5, 'T14': 6, 'T15': 7, 'T16': 7.5, 'T17': 8, 'T19': 9}
summ['_o'] = summ['test'].map(order); summ = summ.sort_values(['_o', '_p'], kind='stable').drop(columns=['_o', '_p'])
sheets = {
    'Summary': [summ],
    'T1_zone_system': ['T1_levels', 'T1_nesting_checks', 'T1_sector_coding', 'T1_zone_hierarchy'],
    'T2_population': ['T2_residents_by_superzone', 'T2_residents_by_sector', 'T2_households_by_superzone', 'T2_car_availability_descriptive'],
    'T3_trip_rates': ['T3_rates_by_superzone', 'T3_rates_by_sector', 'T3_rates_by_locality'],
    'T4_trip_length_KS': ['T4_trip_length_KS', 'T4_survey_distance_by_purpose', 'T4_survey_distance_by_sector'],
    'T5_CR_vs_cellular': ['T5_coincidence_ratio'],
    'T7_transit_OD_fit': ['T7_transit_OD_fit', 'T7_matched_cells_superzone'],
    'T7b_bus_pattern': ['BusPattern_survey_destination_prediction', 'BusPattern_bootstrap', 'BusPattern_trip_length_and_local_share', 'BusPattern_by_origin_superzone'],
    'T6_intra_zonal': ['T6_intra_by_layer', 'T6_intra_by_superzone', 'T6_intra_by_locality', 'T6_intra_by_sector'],
    'T9_mode_split': ['T9_modesplit_by_origin_sz', 'T9_modesplit_by_destination_sz', 'T9_modesplit_by_locality', 'T9_modesplit_by_sector'],
    'T10_occupancy': ['T10_occupancy'],
    'T16_metronit': ['T16_metronit_by_superzone'],
    'T19_convergence': ['T19_furness_convergence', 'T19_aggregation_check'],
    'T8_time_of_day': ['T8_car_profile_vs_counts', 'T8_transit_profile_vs_ravkav'],
    'T8b_time_by_window': ['T8b_car_profile_by_window', 'T8b_bus_profile_by_window', 'T8b_bus_hourly_profiles'],
    'T11_link_volumes': ['T11_link_fit', 'T11_peak_hour_classes', 'T11_screenlines_from_assignment'],
    'T12_cordon_sectors': ['T12_cordon_summary', 'T12_cordon_sectors'],
    'T14_bus_origins': ['T14_bus_origins_summary', 'T14_bus_origins_by_superzone', 'T14_bus_origins_TAZ'],
    'T15_rail_stations': ['T15_rail_stations', 'T15_rail_station_size_classes', 'T15_rail_origins_by_superzone'],
    'T17_running_times': ['T17_bus_running_times', 'T17_bus_running_times_by_length', 'T17_door_to_door_vs_survey'],
}
for P, lab in [('PM', 'PM 16-19'), ('MD', 'midday 10-14')]:      # wave 1b: the same tests for the PM peak and midday survey matrices
    sheets[f'T4_{P}_trip_length'] = [f'T4_trip_length_KS_{P}', f'T4_survey_distance_by_purpose_{P}', f'T4_survey_distance_by_sector_{P}']
    sheets[f'T5_{P}_CR_cellular'] = [f'T5_coincidence_ratio_{P}']
    sheets[f'T7_{P}_transit_OD'] = [f'T7_transit_OD_fit_{P}', f'T7_matched_cells_superzone_{P}']
    sheets[f'T3_{P}_trip_rates'] = [f'T3_rates_by_superzone_{P}', f'T3_rates_by_sector_{P}', f'T3_rates_by_locality_{P}']
    sheets[f'T6_{P}_intra_zonal'] = [f'T6_intra_by_layer_{P}', f'T6_intra_by_superzone_{P}', f'T6_intra_by_locality_{P}', f'T6_intra_by_sector_{P}']
    sheets[f'T9_{P}_mode_split'] = [f'T9_modesplit_by_origin_sz_{P}', f'T9_modesplit_by_destination_sz_{P}', f'T9_modesplit_by_locality_{P}', f'T9_modesplit_by_sector_{P}']
    sheets[f'T10_{P}_occupancy'] = [f'T10_occupancy_{P}']
    sheets[f'T19_{P}_convergence'] = [f'T19_furness_convergence_{P}', f'T19_aggregation_check_{P}']
    sheets[f'T11_{P}_link_volumes'] = [f'T11_link_fit_{P}']
    sheets[f'T12_{P}_cordons'] = [f'T12_cordon_summary_{P}', f'T12_cordon_sectors_{P}']
    sheets[f'T14_{P}_bus_origins'] = [f'T14_bus_origins_summary_{P}', f'T14_bus_origins_by_superzone_{P}', f'T14_bus_origins_TAZ_{P}']
with pd.ExcelWriter(f'{OUT}/validation_workbook.xlsx', engine='openpyxl') as xw:
    readme = pd.DataFrame({'item': ['source', 'frozen version', 'criteria', 'status words', 'periods', 'stage notebooks'],
                           'text': ['Ministry of Transport, Systems Planning, round table on transport models: Validation of the metropolitan models 2024, draft 6 (16 Sep 2024)',
                                    '23 September 2026 rebuild of the survey-based layers (steps 15-36); nothing in the chain is changed by the validation',
                                    'as printed in the guideline; implemented in tools/validation_metrics.py', 'pass / miss (explained) / miss (unexplained) / not run / not applicable / finding',
                                    'AM 06:00-09:00 is the base; the PM 16-19 and midday 10-14 matrices (extension X1) repeat the tests that depend on the time window, on sheets with the period in the name',
                                    'notebooks/diagnostics/MOT_Validation_Stage1_Inputs_Distribution, _Stage1d_Zones_Population_Rates, _Stage2_Timing, _Stage2c_Mode_Occupancy_Convergence, _Stage3_Counts_Transit, _Stage4_Link_volumes (and the _Stage1c, _Stage2b, _Stage3b period variants)']})
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
