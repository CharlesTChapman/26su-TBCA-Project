import logging
import pandas as pd
from flask import Blueprint, jsonify, request
from backend.db_connection import get_db
from backend.ml_models.budget import recommend_reallocation_from_students
logger = logging.getLogger(__name__)
budget_routes = Blueprint('budget', __name__)

def _load_labor_df():
    cols = ['geo', 'time', 'nace_r2', 'sector', 'employment_thousands', 'graduates', 'absorption_rate']
    cursor = get_db().cursor()
    cursor.execute('\n        SELECT geo, time, nace_r2, sector,\n               employment_thousands, graduates, absorption_rate\n        FROM labor_observations\n        ')
    rows = cursor.fetchall()
    if rows and isinstance(rows[0], dict):
        return pd.DataFrame(rows)
    return pd.DataFrame(rows, columns=cols)

def _load_students():
    cursor = get_db().cursor(dictionary=True)
    cursor.execute('SELECT id, major FROM student WHERE major IS NOT NULL')
    return cursor.fetchall()

@budget_routes.route('/budget_recommendations/students', methods=['GET'])
def budget_recommendations_from_students():
    geo = request.args.get('geo', 'BE')
    try:
        total_budget = float(request.args.get('total_budget', 12000000))
    except (TypeError, ValueError):
        return (jsonify({'error': 'total_budget must be numeric'}), 400)
    try:
        df = _load_labor_df()
        students = _load_students()
        recs = recommend_reallocation_from_students(df, geo=geo, total_budget=total_budget, students=students)
    except ValueError as e:
        logger.warning(f'budget_recommendations/students: {e}')
        return (jsonify({'error': str(e)}), 404)
    except Exception as e:
        logger.error(f'budget_recommendations/students failed: {e}')
        return (jsonify({'error': 'internal error generating recommendations'}), 500)
    return jsonify({'geo': geo, 'total_budget': total_budget, 'n_students': len(students), 'recommendations': recs})