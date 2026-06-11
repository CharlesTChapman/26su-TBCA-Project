import logging
import pandas as pd
from flask import Blueprint, jsonify, request
from backend.db_connection import get_db
from backend.ml_models.budget import recommend_reallocation, recommend_reallocation_from_students, build_budget_plan
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

@budget_routes.route('/budget_recommendations', methods=['GET'])
def budget_recommendations():
    geo = request.args.get('geo', 'BE')
    try:
        total_budget = float(request.args.get('total_budget', 12000000))
    except (TypeError, ValueError):
        return (jsonify({'error': 'total_budget must be numeric'}), 400)
    try:
        df = _load_labor_df()
        recs = recommend_reallocation(df, geo=geo, total_budget=total_budget)
    except ValueError as e:
        logger.warning(f'budget_recommendations: {e}')
        return (jsonify({'error': str(e)}), 404)
    except Exception as e:
        logger.error(f'budget_recommendations failed: {e}')
        return (jsonify({'error': 'internal error generating recommendations'}), 500)
    return jsonify({'geo': geo, 'total_budget': total_budget, 'recommendations': recs})

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

@budget_routes.route('/budget_plan', methods=['POST'])
def create_budget_plan():
    data = request.get_json(silent=True) or {}
    geo = data.get('geo', 'BE')
    try:
        total_budget = float(data.get('total_budget', 12000000))
    except (TypeError, ValueError):
        return (jsonify({'error': 'total_budget must be numeric'}), 400)
    try:
        df = _load_labor_df()
        students = _load_students()
        plan = build_budget_plan(df, geo=geo, total_budget=total_budget, students=students, university_id=data.get('university_id'), budget_manager_id=data.get('budget_manager_id'))
    except ValueError as e:
        logger.warning(f'create_budget_plan: {e}')
        return (jsonify({'error': str(e)}), 404)
    except Exception as e:
        logger.error(f'create_budget_plan failed: {e}')
        return (jsonify({'error': 'internal error building budget plan'}), 500)