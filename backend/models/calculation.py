class CalculationRequest:
    """Model for single calculation request validation"""

    def __init__(self, data):
        self.operand1 = data.get('operand1')
        self.operator = data.get('operator')
        self.operand2 = data.get('operand2')
        self.errors = []

    def is_valid(self):
        """Validate calculation request data"""
        self.errors = []

        # Validate operand1
        if self.operand1 is None:
            self.errors.append("operand1 is required")
        else:
            try:
                float(self.operand1)
            except (TypeError, ValueError):
                self.errors.append("operand1 must be a valid number")

        # Validate operator
        if not self.operator:
            self.errors.append("operator is required")
        elif self.operator not in ['+', '-', '*', '/', '**', '%', 'sqrt', 'sin', 'cos', 'tan', 'log']:
            self.errors.append(f"unsupported operator: {self.operator}")

        # Validate operand2 (not required for unary operations)
        unary_operators = ['sqrt', 'sin', 'cos', 'tan', 'log']
        if self.operator not in unary_operators:
            if self.operand2 is None:
                self.errors.append("operand2 is required for binary operations")
            else:
                try:
                    float(self.operand2)
                except (TypeError, ValueError):
                    self.errors.append("operand2 must be a valid number")

        return len(self.errors) == 0

    def get_validation_errors(self):
        """Get validation error messages"""
        return self.errors

class CalculationResponse:
    """Model for calculation response"""

    def __init__(self, result, operation, error=None):
        self.result = result
        self.operation = operation
        self.error = error

    def to_dict(self):
        """Convert response to dictionary"""
        response = {
            'operation': self.operation,
        }

        if self.error:
            response['error'] = self.error
        else:
            response['result'] = self.result

        return response

class BatchCalculationRequest:
    """Model for batch calculation request validation"""

    def __init__(self, data):
        self.calculations = data.get('calculations', [])
        self.errors = []

    def is_valid(self):
        """Validate batch calculation request"""
        self.errors = []

        if not isinstance(self.calculations, list):
            self.errors.append("calculations must be an array")
            return False

        if len(self.calculations) == 0:
            self.errors.append("calculations array cannot be empty")
            return False

        if len(self.calculations) > 100:  # Limit batch size
            self.errors.append("calculations array too large (max 100)")
            return False

        return len(self.errors) == 0

    def get_validation_errors(self):
        """Get validation error messages"""
        return self.errors
