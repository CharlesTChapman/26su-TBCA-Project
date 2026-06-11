import numpy as np
import pandas as pd
from backend.ml_models.crosswalk import resolve_sectors, program_weights_from_students
from backend.ml_models.labor import merge_employment_models

RECENT_YEARS = 6
ALPHA = 0.5
BALANCED_BAND = 0.02
W_ABSORPTION = 0.45
W_POLYFIT_TREND = 0.25
W_MODEL_OUTLOOK = 0.3
PROGRAM_TO_SECTORS = {'Computer Science': ['J'], 'Engineering': ['C'], 'Business': ['K', 'M_N']}

def _zscore(arr):
    arr = np.asarray(arr, dtype=float)
    sd = arr.std()
    if sd == 0 or np.isnan(sd):
        return np.zeros_like(arr)
    return (arr - arr.mean()) / sd

def forecast_growth(years, employment):
    years = np.asarray(years, dtype=float)
    employment = np.asarray(employment, dtype=float)
    if len(years) < 3:
        return 0.0
    slope, intercept = np.polyfit(years, employment, 1)
    next_year = years.max() + 1
    forecast = slope * next_year + intercept
    latest = employment[np.argmax(years)]
    if latest == 0:
        return 0.0
    return (forecast - latest) / latest

def sector_demand(df, geo):
    sub = df[df['geo'] == geo].copy()
    if sub.empty:
        raise ValueError(f'No labor data for geo={geo!r}')
    cutoff = sub['time'].max() - RECENT_YEARS + 1
    rows = []
    for sector, g in sub.groupby('nace_r2'):
        g = g.sort_values('time')
        latest = g.iloc[-1]
        emp_lag1 = float(latest['employment_thousands'])
        grads = float(latest['graduates']) if not pd.isna(latest['graduates']) else 0.0
        next_year = int(latest['time']) + 1
        outlook = merge_employment_models(grads, emp_lag1, next_year)['outlook_growth']
        polyfit = forecast_growth(g['time'], g['employment_thousands'])
        recent = g[g['time'] >= cutoff]
        absorption = recent['absorption_rate'].dropna().mean()
        if np.isnan(absorption):
            absorption = 0.0
        rows.append({'sector': sector, 'label': g['sector'].iloc[-1], 'model_outlook': outlook, 'polyfit_growth': polyfit, 'absorption': absorption})
    out = pd.DataFrame(rows)
    out['demand_score'] = W_ABSORPTION * _zscore(out['absorption']) + W_POLYFIT_TREND * _zscore(out['polyfit_growth']) + W_MODEL_OUTLOOK * _zscore(out['model_outlook'])
    return out.set_index('sector')

def _reallocate(programs, current_shares, program_demand, program_sectors, total_budget):
    raw = np.array([program_demand[p] for p in programs])
    exp = np.exp(raw - raw.max())
    demand_split = exp / exp.sum()
    cur = np.array([current_shares.get(p, 0.0) for p in programs], dtype=float)
    if cur.sum() == 0:
        cur = np.ones(len(programs)) / len(programs)
    cur = cur / cur.sum()
    target = (1 - ALPHA) * cur + ALPHA * demand_split
    results = []
    for i, p in enumerate(programs):
        cur_pct = cur[i]
        tgt_pct = target[i]
        ideal_pct = demand_split[i]
        delta_share = tgt_pct - cur_pct
        budget_adj = delta_share * total_budget
        if delta_share > BALANCED_BAND:
            status = 'Underfunded'
        elif delta_share < -BALANCED_BAND:
            status = 'Overfunded'
        else:
            status = 'Balanced'
        results.append({'Program': p, 'Sectors': ', '.join(program_sectors.get(p, [])), 'Current Target': f'{cur_pct * 100:.0f}% → {tgt_pct * 100:.0f}% → {ideal_pct * 100:.0f}%', 'Demand Score': round(program_demand[p], 3), 'Budget Adj.': f'{budget_adj:+,.0f}', 'Budget Adj. Raw': round(budget_adj, 2), 'Target Amount': round(tgt_pct * total_budget, 2), 'Status': status})
    results.sort(key=lambda r: r['Budget Adj. Raw'], reverse=True)
    return results

def recommend_reallocation(df, geo, total_budget, programs=None, current_shares=None):
    if programs is None:
        programs = list(PROGRAM_TO_SECTORS.keys())
    if current_shares is None:
        current_shares = {p: 1.0 / len(programs) for p in programs}
    sd = sector_demand(df, geo)
    program_demand, program_sectors = ({}, {})
    for p in programs:
        sectors = [s for s in PROGRAM_TO_SECTORS.get(p, []) if s in sd.index]
        program_sectors[p] = sectors
        vals = [sd.loc[s, 'demand_score'] for s in sectors]
        program_demand[p] = float(np.mean(vals)) if vals else 0.0
    return _reallocate(programs, current_shares, program_demand, program_sectors, total_budget)

def recommend_reallocation_from_students(df, geo, total_budget, students):
    sd = sector_demand(df, geo)
    available = list(sd.index)
    current_shares = program_weights_from_students(students, available_sectors=available)
    programs = list(current_shares.keys())
    if not programs:
        raise ValueError('No students map to any available sector for this geo')
    program_demand, program_sectors = ({}, {})
    for p in programs:
        sectors = resolve_sectors(p, available)
        program_sectors[p] = sectors
        vals = [sd.loc[s, 'demand_score'] for s in sectors]
        program_demand[p] = float(np.mean(vals)) if vals else 0.0
    return _reallocate(programs, current_shares, program_demand, program_sectors, total_budget)

def build_budget_plan(df, geo, total_budget, students, university_id=None, budget_manager_id=None):
    recs = recommend_reallocation_from_students(df, geo, total_budget, students)
    line_items = [{'program': r['Program'], 'sectors': r['Sectors'], 'target_amount': r['Target Amount'], 'budget_adjustment': r['Budget Adj. Raw'], 'status': r['Status'], 'demand_score': r['Demand Score']} for r in recs]
    return {'university_id': university_id, 'budget_manager_id': budget_manager_id, 'geo': geo, 'total_amount': round(float(total_budget), 2), 'n_students': len(students), 'line_items': line_items}