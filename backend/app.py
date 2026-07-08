from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import json
import re
from decimal import Decimal, InvalidOperation, getcontext
import logging

# Set decimal precision for calculations
getcontext().prec = 28

app = Flask(__name__)
CORS(app, origins=['*'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalculationEngine:
    """Core calculation engine with robust arithmetic operations"""

    @staticmethod
    def safe_division(dividend, divisor):
        """Safely perform division with zero-check"""
        if divisor == 0:
            raise ValueError("Division by zero is not allowed")
        return dividend / divisor

    @staticmethod
    def check_overflow(number):
        """Check for number overflow and handle large numbers"""
        if abs(number) > 1e308:
            raise ValueError("Number overflow: result too large")
        return number

    @staticmethod
    def validate_number(value):
        """Validate that a value is a valid number"""
        if value is None:
            raise ValueError("Operand cannot be None")

        try:
            # Convert to float and check for infinity or NaN
            num = float(value)
            if math.isnan(num):
                raise ValueError("Invalid number: NaN")
            if math.isinf(num):
                raise ValueError("Invalid number: Infinity")
            return num
        except (ValueError, TypeError):
            raise ValueError(f"Invalid number: {value}")

    @staticmethod
    def perform_operation(operation, operand1, operand2=None):
        """Perform arithmetic operation with error handling"""
        try:
            # Validate operands
            num1 = CalculationEngine.validate_number(operand1)

            if operation == "sqrt":
                if num1 < 0:
                    raise ValueError("Cannot calculate square root of negative number")
                result = math.sqrt(num1)
            else:
                if operand2 is None:
                    raise ValueError(f"Operation '{operation}' requires two operands")
                num2 = CalculationEngine.validate_number(operand2)

                if operation == "add":
                    result = num1 + num2
                elif operation == "subtract":
                    result = num1 - num2
                elif operation == "multiply":
                    result = num1 * num2
                elif operation == "divide":
                    result = CalculationEngine.safe_division(num1, num2)
                elif operation == "modulo":
                    if num2 == 0:
                        raise ValueError("Modulo by zero is not allowed")
                    result = num1 % num2
                elif operation == "power":
                    if abs(num1) > 1000 and num2 > 100:
                        raise ValueError("Power operation would result in overflow")
                    result = num1 ** num2
                else:
                    raise ValueError(f"Unsupported operation: {operation}")

            # Check for overflow
            result = CalculationEngine.check_overflow(result)

            # Round to 10 decimal places to handle floating point precision
            result = round(result, 10)

            return result

        except Exception as e:
            raise ValueError(str(e))

class CalculationRequest:
    """Request model for calculation operations"""

    def __init__(self, data):
        self.operation = data.get('operation')
        self.operand1 = data.get('operand1')
        self.operand2 = data.get('operand2')
        self.validate()

    def validate(self):
        """Validate calculation request"""
        if not self.operation:
            raise ValueError("Operation is required")

        valid_operations = ['add', 'subtract', 'multiply', 'divide', 'modulo', 'power', 'sqrt']
        if self.operation not in valid_operations:
            raise ValueError(f"Invalid operation. Must be one of: {', '.join(valid_operations)}")

        if self.operand1 is None:
            raise ValueError("operand1 is required")

        if self.operation != 'sqrt' and self.operand2 is None:
            raise ValueError(f"operand2 is required for operation '{self.operation}'")

class BatchCalculationRequest:
    """Request model for batch calculations"""

    def __init__(self, data):
        self.calculations = data.get('calculations', [])
        self.validate()

    def validate(self):
        """Validate batch calculation request"""
        if not self.calculations:
            raise ValueError("calculations array is required")

        if not isinstance(self.calculations, list):
            raise ValueError("calculations must be an array")

        if len(self.calculations) > 100:
            raise ValueError("Maximum 100 calculations allowed per batch")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'calculator-api'}), 200

@app.route('/calculate', methods=['POST'])
def calculate():
    """Single calculation endpoint"""
    try:
        # Validate JSON content
        if not request.is_json:
            return jsonify({
                'result': None,
                'operation': None,
                'operands': [],
                'success': False,
                'error': 'Request must be JSON'
            }), 400

        data = request.get_json()
        if not data:
            return jsonify({
                'result': None,
                'operation': None,
                'operands': [],
                'success': False,
                'error': 'Invalid JSON data'
            }), 400

        # Parse and validate request
        calc_request = CalculationRequest(data)

        # Perform calculation
        result = CalculationEngine.perform_operation(
            calc_request.operation,
            calc_request.operand1,
            calc_request.operand2
        )

        # Prepare operands array
        operands = [calc_request.operand1]
        if calc_request.operand2 is not None:
            operands.append(calc_request.operand2)

        return jsonify({
            'result': result,
            'operation': calc_request.operation,
            'operands': operands,
            'success': True,
            'error': None
        }), 200

    except ValueError as e:
        return jsonify({
            'result': None,
            'operation': data.get('operation') if 'data' in locals() else None,
            'operands': [],
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Unexpected error in calculate endpoint: {str(e)}")
        return jsonify({
            'result': None,
            'operation': None,
            'operands': [],
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/calculate/batch', methods=['POST'])
def calculate_batch():
    """Batch calculation endpoint"""
    try:
        # Validate JSON content
        if not request.is_json:
            return jsonify({
                'results': [],
                'success': False,
                'error': 'Request must be JSON'
            }), 400

        data = request.get_json()
        if not data:
            return jsonify({
                'results': [],
                'success': False,
                'error': 'Invalid JSON data'
            }), 400

        # Parse and validate batch request
        batch_request = BatchCalculationRequest(data)

        results = []

        # Process each calculation
        for calc_data in batch_request.calculations:
            calc_id = calc_data.get('id', 'unknown')

            try:
                # Create individual calculation request
                individual_calc = CalculationRequest(calc_data)

                # Perform calculation
                result = CalculationEngine.perform_operation(
                    individual_calc.operation,
                    individual_calc.operand1,
                    individual_calc.operand2
                )

                results.append({
                    'id': calc_id,
                    'result': result,
                    'success': True,
                    'error': None
                })

            except ValueError as e:
                results.append({
                    'id': calc_id,
                    'result': None,
                    'success': False,
                    'error': str(e)
                })
            except Exception as e:
                results.append({
                    'id': calc_id,
                    'result': None,
                    'success': False,
                    'error': 'Internal calculation error'
                })

        return jsonify({
            'results': results
        }), 200

    except ValueError as e:
        return jsonify({
            'results': [],
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Unexpected error in batch calculate endpoint: {str(e)}")
        return jsonify({
            'results': [],
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
