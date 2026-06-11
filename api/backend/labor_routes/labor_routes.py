from flask import Blueprint, jsonify, current_app
from backend.ml_models.labor import predict_employment_level, predict_employment_change
from backend.db_connection import get_db

labor_routes = Blueprint('labor', __name__)


@labor_routes.route('/labor/predict/level/<float:emp_lag1>', methods=['GET'])
def get_employment_level_prediction(emp_lag1):
    current_app.logger.info(f'GET /labor/predict/level/{emp_lag1}')
    return jsonify(predict_employment_level(emp_lag1)), 200


@labor_routes.route('/labor/predict/change/<float:graduates>/<float:emp_lag1>/<int:time>', methods=['GET'])
def get_employment_change_prediction(graduates, emp_lag1, time):
    current_app.logger.info(f'GET /labor/predict/change/{graduates}/{emp_lag1}/{time}')
    return jsonify(predict_employment_change(graduates, emp_lag1, time)), 200


@labor_routes.route('/labor/observations', methods=['GET'])
def get_observations():
    cursor = get_db().cursor(dictionary=True)
    cursor.execute("""
        SELECT geo, time, nace_r2, sector,
               employment_thousands, graduates,
               emp_change, employment_rate, grad_ratio, absorption_rate, predicted
        FROM labor_observations
        ORDER BY geo, nace_r2, time
    """)
    return jsonify(cursor.fetchall()), 200