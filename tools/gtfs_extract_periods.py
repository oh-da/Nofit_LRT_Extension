"""Extract the study-area stop times of the GTFS service day for the AM (06:00-09:00) and PM (16:00-19:00) windows,
plus the rail and Metronit trips of the day, into Output/gtfs/ — the same day and rules as step 29 (Tuesday 2 June 2026)."""
import os, zipfile, time
import numpy as np, pandas as pd
while not os.path.exists('METHODOLOGY.md') and os.getcwd() != '/': os.chdir('..')
t0 = time.time()
Z = zipfile.ZipFile('Input/GTFS/israel-public-transportation.zip')
def read(name, **kw): return pd.read_csv(Z.open(name), **kw)
BRT_CODES = {83001, 67002, 67003, 62004, 52005}
cal = read('calendar.txt', dtype={'service_id': str}); cal['start'] = pd.to_datetime(cal['start_date'].astype(str)); cal['end'] = pd.to_datetime(cal['end_date'].astype(str))
cands = [d for d in pd.date_range(cal['start'].min(), cal['end'].max(), freq='D') if d.weekday() == 1]
n_active = {d: int(((cal['tuesday'] == 1) & (cal['start'] <= d) & (cal['end'] >= d)).sum()) for d in cands}
DAY = max(n_active, key=n_active.get); active = set(cal[(cal['tuesday'] == 1) & (cal['start'] <= DAY) & (cal['end'] >= DAY)]['service_id'])
if 'calendar_dates.txt' in Z.namelist():
    cd = read('calendar_dates.txt', dtype={'service_id': str}); cd = cd[pd.to_datetime(cd['date'].astype(str)) == DAY]
    active = (active | set(cd[cd['exception_type'] == 1]['service_id'])) - set(cd[cd['exception_type'] == 2]['service_id'])
print(f'service day {DAY.date()}, {len(active):,} active services')
routes = read('routes.txt', dtype={'route_id': str, 'agency_id': str}); routes['route_code'] = pd.to_numeric(routes['route_desc'].astype(str).str.split('-').str[0], errors='coerce')
routes['is_brt'] = routes['route_code'].isin(BRT_CODES); routes['is_rail'] = routes['agency_id'].astype(str) == '2'
trips = read('trips.txt', dtype={'route_id': str, 'service_id': str, 'trip_id': str}, usecols=['route_id', 'service_id', 'trip_id', 'direction_id'])
trips = trips[trips['service_id'].isin(active)].merge(routes[['route_id', 'route_code', 'is_brt', 'is_rail', 'route_short_name', 'route_long_name']], on='route_id')
tset = set(trips['trip_id']); print(f'{len(trips):,} trips on the day ({trips.is_rail.sum():,} rail, {trips.is_brt.sum():,} Metronit)')
stops = pd.read_csv('Output/gtfs/stops_study_area.csv'); sset = set(stops['stop_id'])
def secs(s):
    p = s.str.split(':', expand=True).astype(float); return p[0] * 3600 + p[1] * 60 + p[2]
parts = []
with Z.open('stop_times.txt') as f:
    for k, ch in enumerate(pd.read_csv(f, usecols=['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence'], dtype={'trip_id': str}, chunksize=3_000_000)):
        ch = ch[ch['trip_id'].isin(tset) & ch['stop_id'].isin(sset)]
        parts.append(ch); print(f'  chunk {k}: kept {len(ch):,} ({time.time() - t0:.0f} s)', flush=True)
st = pd.concat(parts); st['arr'] = secs(st['arrival_time']); st['dep'] = secs(st['departure_time']); st = st.drop(columns=['arrival_time', 'departure_time'])
st = st.merge(stops[['stop_id', 'TAZ']], on='stop_id').merge(trips[['trip_id', 'route_code', 'direction_id', 'is_brt', 'is_rail']], on='trip_id').sort_values(['trip_id', 'stop_sequence'])
print(f'{len(st):,} study-area stop-time records on the day, {st.trip_id.nunique():,} trips')
for name, (a, b), (pa, pb) in [('am', (6 * 3600, 9 * 3600), (7 * 3600, 8 * 3600)), ('pm', (16 * 3600, 19 * 3600), (17 * 3600, 18 * 3600))]:
    win = st[st['dep'].between(a, b)]; tr_ids = set(win['trip_id'])
    out = st[st['trip_id'].isin(tr_ids) & ~st['is_rail']][['trip_id', 'route_code', 'direction_id', 'is_brt', 'stop_sequence', 'stop_id', 'TAZ', 'arr', 'dep']].copy(); out['peak'] = out['dep'].between(pa, pb)
    out.to_csv(f'Output/gtfs/stop_times_study_area_{name}_trips_v45.csv.gz', index=False, compression='gzip')
    print(f'{name}: {len(out):,} records, {out.trip_id.nunique():,} bus/Metronit trips departing a study-area stop in the window ({out[out.is_brt].trip_id.nunique():,} Metronit)')
rail = st[st['is_rail']][['trip_id', 'route_code', 'direction_id', 'stop_sequence', 'stop_id', 'TAZ', 'arr', 'dep']]
rail.to_csv('Output/gtfs/stop_times_study_area_rail_day.csv.gz', index=False, compression='gzip'); print(f'rail: {len(rail):,} records, {rail.trip_id.nunique():,} trips; {time.time() - t0:.0f} s')
