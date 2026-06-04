from flask import Blueprint, request, jsonify, current_app
from backend.ml_models.02_labor import predict_employment_level, predict_employment_change

labor_routes = Blueprint('labor', __name__)

@labor_routes.route('/labor/predict/level/<float:emp_lag1>', methods=['GET'])
def get_employment_level_prediction(emp_lag1):
    current_app.logger.info(f'GET /labor/predict/level/{emp_lag1}')
    result = predict_employment_level(emp_lag1)
    return jsonify(result), 200


@labor_routes.route('/labor/predict/change/<float:graduates>/<float:emp_lag1>/<int:time>', methods=['GET'])
def get_employment_change_prediction(graduates, emp_lag1, time):
    current_app.logger.info(f'GET /labor/predict/change/{graduates}/{emp_lag1}/{time}')
    result = predict_employment_change(graduates, emp_lag1, time)
    return jsonify(result), 200