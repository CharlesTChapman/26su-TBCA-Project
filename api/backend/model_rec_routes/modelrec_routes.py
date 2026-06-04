from flask import Blueprint, jsonify, current_app
from backend.ml_models.modelrec import university_ranking_model
from backend.utils import error_response

modelrec_routes = Blueprint('modelrec', __name__)
model = university_ranking_model()


@modelrec_routes.route('/modelrec/predict/<float:budget>/<int:degree>/<int:size>', methods=['GET'])
def get_top_matches(budget, degree, size):
    current_app.logger.info(f'GET /modelrec/predict/{budget}/{degree}/{size}')
    try:
        result = model.predict(budget, degree, size, top_n=10)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f'GET /modelrec/predict/{budget}/{degree}/{size} failed: {e}')
        return error_response('Could not retrieve university recommendations')


@modelrec_routes.route('/modelrec/predict/all/<float:budget>/<int:degree>/<int:size>', methods=['GET'])
def get_all_matches(budget, degree, size):
    current_app.logger.info(f'GET /modelrec/predict/all/{budget}/{degree}/{size}')
    try:
        result = model.predict(budget, degree, size)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f'GET /modelrec/predict/all/{budget}/{degree}/{size} failed: {e}')
        return error_response('Could not retrieve university recommendations')
