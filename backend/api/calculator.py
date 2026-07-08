from flask import Blueprint, request, jsonify
from backend.services.calculation_engine import CalculationEngine
from backend.models.calculation import CalculationRequest, CalculationResponse, BatchCalculationRequest

calculator_bp = Blueprint('calculator', __name__)
calc_engine = CalculationEngine()

@calculator_bp.route('/calculate', methods=['POST'])
def calculate():
    """Single calculation endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        calc_request = CalculationRequest(data)
        if not calc_request.is_valid():
            return jsonify({'error': calc_request.get_validation_errors()}), 400

        result = calc_engine.calculate(
            calc_request.operand1,
            calc_request.operator,
            calc_request.operand2
        )

        response = CalculationResponse(
            result=result,
            operation=f"{calc_request.operand1} {calc_request.operator} {calc_request.operand2}"
        )

        return jsonify(response.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@calculator_bp.route('/calculate/batch', methods=['POST'])
def calculate_batch():
    """Batch calculation endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        batch_request = BatchCalculationRequest(data)
        if not batch_request.is_valid():
            return jsonify({'error': batch_request.get_validation_errors()}), 400

        results = []
        for calc_data in batch_request.calculations:
            calc_request = CalculationRequest(calc_data)
            if calc_request.is_valid():
                try:
                    result = calc_engine.calculate(
                        calc_request.operand1,
                        calc_request.operator,
                        calc_request.operand2
                    )
                    response = CalculationResponse(
                        result=result,
                        operation=f"{calc_request.operand1} {calc_request.operator} {calc_request.operand2}"
                    )
                    results.append(response.to_dict())
                except Exception as e:
                    results.append({'error': str(e), 'operation': calc_data})
            else:
                results.append({'error': calc_request.get_validation_errors(), 'operation': calc_data})

        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
