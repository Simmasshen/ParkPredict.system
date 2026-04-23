from flask import Blueprint, jsonify, request
from services.recommendation_service import get_recommendation
import logging

recommendation_bp = Blueprint('recommendation', __name__)
logger = logging.getLogger(__name__)

@recommendation_bp.route('/recommendation', methods=['GET'])
def recommend():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id parameter is required'}), 400
        
        result = get_recommendation(user_id)
        if not result:
            return jsonify({'error': 'Could not generate recommendation'}), 404
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500