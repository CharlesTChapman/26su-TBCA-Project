from flask import Blueprint, jsonify, request, current_app
from backend.ml_models.modelrec import university_ranking_model
from backend.utils import error_response

modelrec_routes = Blueprint('modelrec', __name__)
model = university_ranking_model()


@modelrec_routes.route('/modelrec/predict/<float:budget>/<int:degree>/<int:size>', methods=['GET'])
def get_top_matches(budget, degree, size):
    current_app.logger.info(f'GET /modelrec/predict/{budget}/{degree}/{size}')
    try:
        country = request.args.get("country")
        max_km = request.args.get('max_km', type=float)
        result = model.predict(budget, degree, size, top_n=10, student_country=country, max_distance_km=max_km)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f'GET /modelrec/predict/{budget}/{degree}/{size} failed: {e}')
        return error_response('Could not retrieve university recommendations')


@modelrec_routes.route('/modelrec/predict/all/<float:budget>/<int:degree>/<int:size>', methods=['GET'])
def get_all_matches(budget, degree, size):
    current_app.logger.info(f'GET /modelrec/predict/all/{budget}/{degree}/{size}')
    try:
        country = request.args.get("country")
        max_km = request.args.get('max_km', type=float)
        result = model.predict(budget, degree, size, top_n=100, student_country=country, max_distance_km=max_km)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f'GET /modelrec/predict/all/{budget}/{degree}/{size} failed: {e}')
        return error_response('Could not retrieve university recommendations')
