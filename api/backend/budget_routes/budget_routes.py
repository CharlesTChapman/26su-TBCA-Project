import logging
 
import pandas as pd
from flask import Blueprint, jsonify, request
 
from backend.db_connection import get_db
from backend.ml_models.budget import recommend_reallocation
 
logger = logging.getLogger(__name__)
budget_routes = Blueprint("budget", __name__)
 
 
def _load_labor_df():
    cols = ["geo", "time", "nace_r2", "sector",
            "employment_thousands", "graduates", "absorption_rate"]
    cursor = get_db().cursor()
    cursor.execute(
        """
        SELECT geo, time, nace_r2, sector,
               employment_thousands, graduates, absorption_rate
        FROM labor_observations
        """
    )
    rows = cursor.fetchall()
    if rows and isinstance(rows[0], dict):
        return pd.DataFrame(rows)
    return pd.DataFrame(rows, columns=cols)
 
 
@budget_routes.route("/budget_recommendations", methods=["GET"])
def budget_recommendations():
    geo = request.args.get("geo", "BE")
    try:
        total_budget = float(request.args.get("total_budget", 12_000_000))
    except (TypeError, ValueError):
        return jsonify({"error": "total_budget must be numeric"}), 400
 
    try:
        df = _load_labor_df()
        recs = recommend_reallocation(df, geo=geo, total_budget=total_budget)
    except ValueError as e:
        logger.warning(f"budget_recommendations: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"budget_recommendations failed: {e}")
        return jsonify({"error": "internal error generating recommendations"}), 500
 
    return jsonify({"geo": geo, "total_budget": total_budget, "recommendations": recs})
 