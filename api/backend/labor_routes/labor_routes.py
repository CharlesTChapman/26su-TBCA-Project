from flask import Blueprint, request, jsonify, current_app
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


@labor_routes.route('/labor/observations/<geo>', methods=['GET'])
def get_observations_by_country(geo):
    cursor = get_db().cursor(dictionary=True)
    cursor.execute("""
        SELECT geo, time, nace_r2, sector,
               employment_thousands, graduates, emp_change
        FROM labor_observations
        WHERE geo = %s
        ORDER BY nace_r2, time
    """, (geo.upper(),))
    return jsonify(cursor.fetchall()), 200


@labor_routes.route('/labor/sectors', methods=['GET'])
def get_sectors():
    cursor = get_db().cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT nace_r2, sector FROM labor_observations ORDER BY sector")
    return jsonify(cursor.fetchall()), 200


@labor_routes.route('/labor/countries', methods=['GET'])
def get_countries():
    cursor = get_db().cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT geo FROM labor_observations ORDER BY geo")
    return jsonify(cursor.fetchall()), 200


@labor_routes.route('/labor/observations', methods=['POST'])
def add_observation():
    data = request.get_json()
    cursor = get_db().cursor(dictionary=True)
    cursor.execute("""
        INSERT INTO labor_observations
            (geo, time, nace_r2, sector, employment_thousands, graduates)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (data["geo"], data["time"], data["nace_r2"], data["sector"],
          data["employment_thousands"], data["graduates"]))
    get_db().commit()
    return jsonify({"message": "Added", "id": cursor.lastrowid}), 201


@labor_routes.route('/labor/observations/<int:obs_id>', methods=['PUT'])
def update_observation(obs_id):
    data = request.get_json()
    cursor = get_db().cursor(dictionary=True)
    cursor.execute("""
        UPDATE labor_observations
        SET employment_thousands = %s, graduates = %s
        WHERE id = %s
    """, (data["employment_thousands"], data["graduates"], obs_id))
    get_db().commit()
    return jsonify({"message": f"Updated {obs_id}"}), 200


@labor_routes.route('/labor/observations/<int:obs_id>', methods=['DELETE'])
def delete_observation(obs_id):
    cursor = get_db().cursor(dictionary=True)
    cursor.execute("DELETE FROM labor_observations WHERE id = %s", (obs_id,))
    get_db().commit()
    return jsonify({"message": f"Deleted {obs_id}"}), 200


@labor_routes.route('/labor/absorption', methods=['GET'])
def get_absorption_rates():
    cursor = get_db().cursor(dictionary=True)
    cursor.execute("""
        SELECT sector, AVG(absorption_rate) as avg_absorption
        FROM labor_observations
        WHERE absorption_rate IS NOT NULL
        GROUP BY sector
        ORDER BY avg_absorption
    """)
    return jsonify(cursor.fetchall()), 200