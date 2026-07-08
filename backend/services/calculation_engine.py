import math
from decimal import Decimal, DecimalException, getcontext
from backend.utils.math_helpers import safe_divide, check_overflow

# Set precision for decimal operations
getcontext().prec = 28

class CalculationEngine:
    """Core calculation engine with robust arithmetic operations"""

    SUPPORTED_OPERATORS = ['+', '-', '*', '/', '**', '%', 'sqrt', 'sin', 'cos', 'tan', 'log']

    def __init__(self):
        self.precision = 10

    def calculate(self, operand1, operator, operand2=None):
        """
        Perform calculation with error handling and precision management

        Args:
            operand1: First operand (number)
            operator: Mathematical operator (string)
            operand2: Second operand (number, optional for unary operations)

        Returns:
            dict: Result with success status and value or error message

        Raises:
            ValueError: For invalid inputs
            ZeroDivisionError: For division by zero
        """
        try:
            # Convert inputs to Decimal for precision
            if operand1 is not None:
                operand1 = Decimal(str(operand1))
            if operand2 is not None:
                operand2 = Decimal(str(operand2))

            # Validate operator
            if operator not in self.SUPPORTED_OPERATORS:
                return {
                    'success': False,
                    'error': f'Unsupported operator: {operator}',
                    'result': None
                }

            # Perform calculation based on operator
            if operator == '+':
                result = operand1 + operand2
            elif operator == '-':
                result = operand1 - operand2
            elif operator == '*':
                result = operand1 * operand2
            elif operator == '/':
                result = safe_divide(operand1, operand2)
            elif operator == '**':
                # Check for reasonable power limits
                if abs(operand2) > 1000:
                    return {
                        'success': False,
                        'error': 'Exponent too large',
                        'result': None
                    }
                result = operand1 ** operand2
            elif operator == '%':
                if operand2 == 0:
                    return {
                        'success': False,
                        'error': 'Modulo by zero',
                        'result': None
                    }
                result = operand1 % operand2
            elif operator == 'sqrt':
                if operand1 < 0:
                    return {
                        'success': False,
                        'error': 'Cannot calculate square root of negative number',
                        'result': None
                    }
                result = Decimal(str(math.sqrt(float(operand1))))
            elif operator == 'sin':
                result = Decimal(str(math.sin(float(operand1))))
            elif operator == 'cos':
                result = Decimal(str(math.cos(float(operand1))))
            elif operator == 'tan':
                result = Decimal(str(math.tan(float(operand1))))
            elif operator == 'log':
                if operand1 <= 0:
                    return {
                        'success': False,
                        'error': 'Cannot calculate logarithm of non-positive number',
                        'result': None
                    }
                result = Decimal(str(math.log(float(operand1))))

            # Check for overflow
            check_overflow(result)

            # Round to specified precision
            result = round(float(result), self.precision)

            return {
                'success': True,
                'error': None,
                'result': result
            }

        except (ValueError, DecimalException) as e:
            return {
                'success': False,
                'error': f'Invalid input: {str(e)}',
                'result': None
            }
        except ZeroDivisionError:
            return {
                'success': False,
                'error': 'Division by zero',
                'result': None
            }
        except OverflowError:
            return {
                'success': False,
                'error': 'Result too large',
                'result': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Calculation error: {str(e)}',
                'result': None
            }

    def batch_calculate(self, calculations):
        """
        Perform multiple calculations in batch

        Args:
            calculations: List of calculation dictionaries

        Returns:
            list: Results for each calculation
        """
        results = []
        for calc in calculations:
            try:
                result = self.calculate(
                    calc.get('operand1'),
                    calc.get('operator'),
                    calc.get('operand2')
                )
                results.append(result)
            except Exception as e:
                results.append({
                    'success': False,
                    'error': f'Batch calculation error: {str(e)}',
                    'result': None
                })
        return results

    def add(self, a, b):
        """Addition operation"""
        return self.calculate(a, '+', b)

    def subtract(self, a, b):
        """Subtraction operation"""
        return self.calculate(a, '-', b)

    def multiply(self, a, b):
        """Multiplication operation"""
        return self.calculate(a, '*', b)

    def divide(self, a, b):
        """Division operation"""
        return self.calculate(a, '/', b)

    def power(self, a, b):
        """Exponentiation operation"""
        return self.calculate(a, '**', b)

    def modulo(self, a, b):
        """Modulo operation"""
        return self.calculate(a, '%', b)

    def square_root(self, a):
        """Square root operation"""
        return self.calculate(a, 'sqrt')

    def sine(self, a):
        """Sine operation"""
        return self.calculate(a, 'sin')

    def cosine(self, a):
        """Cosine operation"""
        return self.calculate(a, 'cos')

    def tangent(self, a):
        """Tangent operation"""
        return self.calculate(a, 'tan')

    def logarithm(self, a):
        """Natural logarithm operation"""
        return self.calculate(a, 'log')
