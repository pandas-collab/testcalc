import unittest
import json
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, CalculationEngine

class TestCalculationEngine(unittest.TestCase):
    """Test the core calculation engine"""

    def test_addition(self):
        """Test addition operation"""
        result = CalculationEngine.perform_operation("add", 5, 3)
        self.assertEqual(result, 8)

        result = CalculationEngine.perform_operation("add", -5, 3)
        self.assertEqual(result, -2)

        result = CalculationEngine.perform_operation("add", 0.1, 0.2)
        self.assertAlmostEqual(result, 0.3, places=10)

    def test_subtraction(self):
        """Test subtraction operation"""
        result = CalculationEngine.perform_operation("subtract", 10, 3)
        self.assertEqual(result, 7)

        result = CalculationEngine.perform_operation("subtract", -5, -3)
        self.assertEqual(result, -2)

    def test_multiplication(self):
        """Test multiplication operation"""
        result = CalculationEngine.perform_operation("multiply", 6, 7)
        self.assertEqual(result, 42)

        result = CalculationEngine.perform_operation("multiply", -3, 4)
        self.assertEqual(result, -12)

        result = CalculationEngine.perform_operation("multiply", 0, 100)
        self.assertEqual(result, 0)

    def test_division(self):
        """Test division operation"""
        result = CalculationEngine.perform_operation("divide", 15, 3)
        self.assertEqual(result, 5)

        result = CalculationEngine.perform_operation("divide", 1, 3)
        self.assertAlmostEqual(result, 0.3333333333, places=10)

    def test_division_by_zero(self):
        """Test division by zero error handling"""
        with self.assertRaises(ValueError) as context:
            CalculationEngine.perform_operation("divide", 10, 0)
        self.assertIn("Division by zero", str(context.exception))

    def test_modulo(self):
        """Test modulo operation"""
        result = CalculationEngine.perform_operation("modulo", 17, 5)
        self.assertEqual(result, 2)

        result = CalculationEngine.perform_operation("modulo", 10, 3)
        self.assertEqual(result, 1)

    def test_modulo_by_zero(self):
        """Test modulo by zero error handling"""
        with self.assertRaises(ValueError) as context:
            CalculationEngine.perform_operation("modulo", 10, 0)
        self.assertIn("Modulo by zero", str(context.exception))

    def test_power(self):
        """Test power operation"""
        result = CalculationEngine.perform_operation("power", 2, 3)
        self.assertEqual(result, 8)

        result = CalculationEngine.perform_operation("power", 5, 0)
        self.assertEqual(result, 1)

        result = CalculationEngine.perform_operation("power", 4, 0.5)
        self.assertEqual(result, 2)

    def test_sqrt(self):
        """Test square root operation"""
        result = CalculationEngine.perform_operation("sqrt", 9)
        self.assertEqual(result, 3)

        result = CalculationEngine.perform_operation("sqrt", 2)
        self.assertAlmostEqual(result, 1.4142135624, places=10)

        result = CalculationEngine.perform_operation("sqrt", 0)
        self.assertEqual(result, 0)

    def test_sqrt_negative(self):
        """Test square root of negative number"""
        with self.assertRaises(ValueError) as context:
            CalculationEngine.perform_operation("sqrt", -1)
        self.assertIn("negative number", str(context.exception))

    def test_invalid_operation(self):
        """Test invalid operation handling"""
        with self.assertRaises(ValueError) as context:
            CalculationEngine.perform_operation("invalid", 5, 3)
        self.assertIn("Unsupported operation", str(context.exception))

    def test_invalid_numbers(self):
        """Test invalid number handling"""
        with self.assertRaises(ValueError):
            CalculationEngine.perform_operation("add", "not_a_number", 3)

        with self.assertRaises(ValueError):
            CalculationEngine.perform_operation("add", None, 3)

    def test_precision_handling(self):
        """Test floating point precision"""
        result = CalculationEngine.perform_operation("divide", 1, 3)
        # Should be rounded to 10 decimal places
        self.assertEqual(len(str(result).split('.')[-1]), 10)

class TestCalculatorAPI(unittest.TestCase):
    """Test the Flask API endpoints"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'calculator-api')

    def test_single_calculation_success(self):
        """Test successful single calculation"""
        payload = {
            'operation': 'add',
            'operand1': 5,
            'operand2': 3
        }

        response = self.app.post('/calculate',
                               data=json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['result'], 8)
        self.assertEqual(data['operation'], 'add')
        self.assertEqual(data['operands'], [5, 3])
        self.assertTrue(data['success'])
        self.assertIsNone(data['error'])

    def test_single_calculation_sqrt(self):
        """Test single operand calculation (sqrt)"""
        payload = {
            'operation': 'sqrt',
            'operand1': 16
        }

        response = self.app.post('/calculate',
                               data=json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['result'], 4)
        self.assertEqual(data['operation'], 'sqrt')
        self.assertEqual(data['operands'], [16])
        self.assertTrue(data['success'])

    def test_single_calculation_division_by_zero(self):
        """Test division by zero error"""
        payload = {
            'operation': 'divide',
            'operand1': 10,
            'operand2': 0
        }

        response = self.app.post('/calculate',
                               data=json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIsNone(data['result'])
        self.assertFalse(data['success'])
        self.assertIn("Division by zero", data['error'])

    def test_single_calculation_invalid_operation(self):
        """Test invalid operation error"""
        payload = {
            'operation': 'invalid_op',
            'operand1': 5,
            'operand2': 3
        }

        response = self.app.post('/calculate',
                               data=json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn("Invalid operation", data['error'])

    def test_single_calculation_missing_operand(self):
        """Test missing operand error"""
        payload = {
            'operation': 'add',
            'operand1': 5
            # Missing operand2
        }

        response = self.app.post('/calculate',
                               data=json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn("operand2 is required", data['error'])

    def test_batch_calculation_success(self):
        """Test successful batch calculations"""
        payload = {
            'calculations': [
                {
                    'id': 'calc1',
                    'operation': 'add',
                    'operand1': 5,
                    'operand2': 3
                },
                {
                    'id': 'calc2',
                    'operation': 'multiply',
                    'operand1': 4,
                    'operand2': 6
                },
                {
                    'id': 'calc3',
                    'operation': 'sqrt',
                    'operand1': 25
                }
            ]
        }

        response = self.app.post('/calculate/batch',
                               data=json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(len(data['results']), 3)

        # Check first calculation
        calc1 = data['results'][0]
        self.assertEqual(calc1['id'], 'calc1')
        self.assertEqual(calc1['result'], 8)
        self.assertTrue(calc1['success'])

        # Check second calculation
        calc2 = data['results'][1]
        self.assertEqual(calc2['id'], 'calc2')
        self.assertEqual(calc2['result'], 24)
        self.assertTrue(calc2['success'])

        # Check third calculation
        calc3 = data['results'][2]
        self.assertEqual(calc3['id'], 'calc3')
        self.assertEqual(calc3['result'], 5)
        self.assertTrue(calc3['success'])

    def test_batch_calculation_mixed_results(self):
        """Test batch calculations with mixed success/failure"""
        payload = {
            'calculations': [
                {
                    'id': 'success',
                    'operation': 'add',
                    'operand1': 2,
                    'operand2': 3
                },
                {
                    'id': 'division_by_zero',
                    'operation': 'divide',
                    'operand1': 10,
                    'operand2': 0
                },
                {
                    'id': 'invalid_op',
                    'operation': 'unknown',
                    'operand1': 5,
                    'operand2': 2
                }
            ]
        }

        response = self.app.post('/calculate/batch',
                               data=json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        results = data['results']

        # First should succeed
        self.assertTrue(results[0]['success'])
        self.assertEqual(results[0]['result'], 5)

        # Second should fail with division by zero
        self.assertFalse(results[1]['success'])
        self.assertIn("Division by zero", results[1]['error'])

        # Third should fail with invalid operation
        self.assertFalse(results[2]['success'])
        self.assertIn("Invalid operation", results[2]['error'])

    def test_batch_calculation_empty_array(self):
        """Test batch calculation with empty calculations array"""
        payload = {'calculations': []}

        response = self.app.post('/calculate/batch',
                               data=json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn("calculations array is required", data['error'])

    def test_invalid_json(self):
        """Test invalid JSON handling"""
        response = self.app.post('/calculate',
                               data='invalid json',
                               content_type='application/json')

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn("JSON", data['error'])

    def test_non_json_content_type(self):
        """Test non-JSON content type handling"""
        response = self.app.post('/calculate',
                               data='some data',
                               content_type='text/plain')

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn("Request must be JSON", data['error'])

    def test_404_handling(self):
        """Test 404 error handling"""
        response = self.app.get('/nonexistent')

        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn("not found", data['error'])

    def test_decimal_precision(self):
        """Test decimal precision handling"""
        payload = {
            'operation': 'divide',
            'operand1': 1,
            'operand2': 3
        }

        response = self.app.post('/calculate',
                               data=json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        # Result should be rounded to 10 decimal places
        self.assertAlmostEqual(data['result'], 0.3333333333, places=10)

if __name__ == '__main__':
    unittest.main()
