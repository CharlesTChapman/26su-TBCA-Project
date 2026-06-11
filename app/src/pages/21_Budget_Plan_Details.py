import logging

import requests
import streamlit as st

from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks()

API = "http://web-api:4000"

EU27_NAME_TO_GEO = {
    "Austria": "AT", "Belgium": "BE", "Bulgaria": "BG", "Croatia": "HR",
    "Cyprus": "CY", "Czechia": "CZ", "Czech Republic": "CZ", "Denmark": "DK",
    "Estonia": "EE", "Finland": "FI", "France": "FR", "Germany": "DE",
    "Greece": "EL", "Hungary": "HU", "Ireland": "IE", "Italy": "IT",
    "Latvia": "LV", "Lithuania": "LT", "Luxembourg": "LU", "Malta": "MT",
    "Netherlands": "NL", "Poland": "PL", "Portugal": "PT", "Romania": "RO",
    "Slovakia": "SK", "Slovenia": "SI", "Spain": "ES", "Sweden": "SE",
}
EU27_GEOS = set(EU27_NAME_TO_GEO.values())


def resolve_geo(uni):
    # 1) university record already carries a code, e.g. "PL"
    for key in ("geo", "country_code", "countryCode"):
        v = uni.get(key)
        if isinstance(v, str) and v.strip().upper() in EU27_GEOS:
            return v.strip().upper(), None
    for key in ("country", "country_name"):
        v = uni.get(key)
        if isinstance(v, str):
            code = EU27_NAME_TO_GEO.get(v.strip())
            if code:
                return code, None
    loc = (uni.get("location") or "").lower()
    for name, code in EU27_NAME_TO_GEO.items():
        if name.lower() in loc:
            return code, None
    return None, (
        f"Couldn't determine a country for " 
        f"{uni.get('name', 'this university')!r}. "
        f"Add a country/geo field to the /universities record or include the "
        f"country in its location string."
    )

def _g(row, *keys, default=None):
    for k in keys:
        if row.get(k) is not None:
            return row[k]
    return default


def _fmt_demand(v):
    if isinstance(v, (int, float)):
        return f"{v:+.2f}"
    return v if v is not None else "—"


def _fmt_money(v):
    if isinstance(v, (int, float)):
        return f"€{v:,.0f}"
    return v if v is not None else "—"


def _amount_raw(row):
    raw = row.get("_target_amount_raw")
    if isinstance(raw, (int, float)):
        return raw
    v = row.get("Target Amount")
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        try:
            return float(v.replace("€", "").replace(",", "").strip())
        except ValueError:
            return 0.0
    return 0.0


@st.cache_data(ttl=300)
def load_universities():
    """Fetch all universities from the API's GET /universities route."""
    r = requests.get(f"{API}/universities", timeout=10)
    r.raise_for_status()
    return r.json()


if st.button("← Back", key="back_button"):
    st.switch_page("pages/20_Budget_Manager_Home.py")

st.title("Budget Plan Details")

# --- Pick a university --------------------------------------------------------
try:
    universities = load_universities()
except Exception as e:
    logger.error(f"Could not load universities from API: {e}")
    st.error(f"Could not load universities from the API: {e}")
    st.stop()

options = {u["name"]: u for u in universities}
names = sorted(options.keys())

preset = st.session_state.get("selected_university")
default_index = names.index(preset) if preset in options else None

selected_name = st.selectbox(
    "University",
    options=names,
    index=default_index,
    placeholder="Search for a university...",
)

if not selected_name:
    st.info("Select a university to build its budget plan.")
    st.stop()

uni = options[selected_name]
uni_id = uni["id"]
st.session_state["selected_university"] = selected_name

# Resolve the country once, here, from the selected record.
geo, geo_warning = resolve_geo(uni)
st.session_state["selected_country"] = geo

# --- Gather the figures -------------------------------------------------------
num_students = None
graduation_rate = None
report_year = None
try:
    r = requests.get(f"{API}/stats/universities/{uni_id}", timeout=10)
    if r.status_code == 200:
        reports = [row for row in r.json() if row.get("year") is not None]
        if reports:
            latest = max(reports, key=lambda row: row["year"])
            num_students = latest.get("students")
            graduation_rate = latest.get("graduation_rate")
            report_year = latest.get("year")
except Exception as e:
    logger.error(f"Could not load academic stats for university {uni_id}: {e}")

student_fees = uni.get("student_fees")

# --- Current standing ---------------------------------------------------------
st.divider()
st.header(selected_name)
st.caption(uni.get("location") or "")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Budget",
            f"€{student_fees:,.0f}" if student_fees is not None else "—",
            help="The university's reported total student-fee revenue.")
col2.metric("Total Students",
            f"{num_students:,}" if num_students is not None else "—")
col3.metric("Graduation Rate",
            f"{graduation_rate:.1%}" if graduation_rate is not None else "—")
col4.metric("Country", geo or "Unknown")

if report_year is not None:
    st.caption(f"📅 Academic figures are from the {report_year} report.")

# --- Save a budget plan -------------------------------------------------------
st.divider()
st.subheader("💾 Save Budget Plan")

manager = st.session_state.get("selected_manager", {})
manager_id = manager.get("id")

if manager_id is None:
    st.warning("Log in as a budget manager from the home page to save a plan.")
else:
    plan_amount = st.number_input(
        "Budget amount for this plan (€)",
        min_value=0,
        value=int(student_fees) if student_fees else 0,
        step=100_000,
        key="save_plan_amount",
    )
    if st.button("Save budget plan", type="primary"):
        try:
            resp = requests.post(
                f"{API}/budget_plans",
                json={
                    "university_id": uni_id,
                    "budget_manager_id": manager_id,
                    "total_amount": int(plan_amount),
                },
                timeout=10,
            )
            if resp.status_code == 201:
                st.success(
                    f"Saved budget plan for {selected_name} (€{int(plan_amount):,}).")
            else:
                st.error("Could not save the budget plan. Please try again.")
        except Exception as e:
            logger.error(f"Failed to save budget plan: {e}")
            st.error(f"Could not save the budget plan: {e}")

# ---- Sector ML model: program reallocation -----------------------------------
st.divider()
st.subheader("Program Reallocation")

if geo_warning:
    st.warning(geo_warning)

col_a, _ = st.columns([1, 3])
with col_a:
    program_budget = st.number_input(
        "Total program budget (€)",
        min_value=0,
        value=12_000_000,
        step=50_000,
        help="Split across every major based on labor-market demand and enrollment.",
    )

recs = []
n_students = 0
try:
    r = requests.get(
        f"{API}/budget_recommendations/students",
        params={"geo": geo, "total_budget": program_budget},
        timeout=15,
    )
    r.raise_for_status()
    payload = r.json()
    recs = payload.get("recommendations", [])
    n_students = payload.get("n_students", 0)
except Exception as e:
    logger.error(f"Could not load budget recommendations for {geo}: {e}")
    st.error(f"Could not load recommendations for {selected_name} ({geo}): {e}")

with st.container(border=True):
    st.subheader("Program Reallocation Table")
    st.caption(
        f"Targets are model-driven across all {len(recs)} majors, starting from "
        f"current enrollment ({n_students} students). Majors feeding growing, "
        f"high-absorption sectors in {geo} gain budget; saturated or shrinking "
        f"sectors get cut."
    )
    st.divider()

    widths = [2.4, 2.2, 1.7, 1.2, 1.6, 1.5, 1.2]
    head = st.columns(widths)
    head[0].write("**Major**")
    head[1].write("**Current → Target**")
    head[2].write("**Demand**")
    head[3].write("**Budget Adj.**")
    head[4].write("**Target Amount**")
    head[5].write("**Status**")
    st.divider()

    status_color = {"Underfunded": ":green", "Overfunded": ":red", "Balanced": ":gray"}

    if not recs:
        st.info("No recommendations to show.")

    for row in recs:
        c = st.columns(widths)
        c[0].write(_g(row, "Major", "Program", default="—"))
        c[1].write(_g(row, "Current → Target", "Current Target", default="—"))
        c[2].write(_fmt_demand(_g(row, "Demand", "Demand Score")))
        c[3].write(_g(row, "Budget Adj.", default="—"))
        c[4].write(_fmt_money(_g(row, "Target Amount")))
        status = _g(row, "Status", default="—")
        prefix = status_color.get(status, "")
        c[5].write(f"{prefix}[{status}]" if prefix else status)

    if recs:
        st.divider()
        total_alloc = sum(_amount_raw(r) for r in recs)
        st.caption(f"Allocated: €{total_alloc:,.0f} of €{program_budget:,.0f}")