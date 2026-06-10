import numpy as np
import pandas as pd

PROGRAM_TO_SECTORS = {
    "Computer Science": ["J"],            # ICT
    "Engineering": ["C"],                 # Manufacturing
    "Business": ["K", "M_N"],             # Finance & Insurance + Professional Services
}

RECENT_YEARS = 6
ALPHA = 0.5
BALANCED_BAND = 0.02


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
    sub = df[df["geo"] == geo].copy()
    if sub.empty:
        raise ValueError(f"No labor data for geo={geo!r}")

    cutoff = sub["time"].max() - RECENT_YEARS + 1
    rows = []
    for sector, g in sub.groupby("nace_r2"):
        g = g.sort_values("time")
        growth = forecast_growth(g["time"], g["employment_thousands"])
        recent = g[g["time"] >= cutoff]
        # absorption_rate = emp_change / graduates; mean over recent years
        absorption = recent["absorption_rate"].dropna().mean()
        if np.isnan(absorption):
            absorption = 0.0
        rows.append({
            "sector": sector,
            "label": g["sector"].iloc[-1],
            "growth": growth,
            "absorption": absorption,
        })

    out = pd.DataFrame(rows)
    out["demand_score"] = 0.65 * _zscore(out["growth"]) + 0.35 * _zscore(out["absorption"])
    return out.set_index("sector")


def recommend_reallocation(df, geo, total_budget, programs=None, current_shares=None):
    if programs is None:
        programs = list(PROGRAM_TO_SECTORS.keys())
    if current_shares is None:
        current_shares = {p: 1.0 / len(programs) for p in programs}

    sd = sector_demand(df, geo)

    # Average sector demand per program.
    prog_demand = {}
    for p in programs:
        sectors = PROGRAM_TO_SECTORS.get(p, [])
        vals = [sd.loc[s, "demand_score"] for s in sectors if s in sd.index]
        prog_demand[p] = float(np.mean(vals)) if vals else 0.0

    # Convert demand into a target split. Softmax keeps everything positive and
    # bounded so no single program eats the whole budget.
    raw = np.array([prog_demand[p] for p in programs])
    exp = np.exp(raw - raw.max())
    demand_split = exp / exp.sum()

    cur = np.array([current_shares.get(p, 0.0) for p in programs])
    cur = cur / cur.sum()  # normalize in case it doesn't sum to 1
    target = (1 - ALPHA) * cur + ALPHA * demand_split

    results = []
    for i, p in enumerate(programs):
        cur_pct = cur[i]
        tgt_pct = target[i]
        delta_share = tgt_pct - cur_pct
        budget_adj = delta_share * total_budget

        if delta_share > BALANCED_BAND:
            status = "Underfunded"      # market wants more here -> increase
        elif delta_share < -BALANCED_BAND:
            status = "Overfunded"       # saturated/shrinking -> cut
        else:
            status = "Balanced"

        results.append({
            "Program": p,
            "Sectors": ", ".join(PROGRAM_TO_SECTORS.get(p, [])),
            "Current Target": f"{cur_pct*100:.0f}% -> {tgt_pct*100:.0f}%",
            "Demand Score": round(prog_demand[p], 3),
            "Budget Adj.": f"{budget_adj:+,.0f}",
            "Budget Adj. Raw": round(budget_adj, 2),
            "Status": status,
        })

    results.sort(key=lambda r: r["Budget Adj. Raw"], reverse=True)
    return results