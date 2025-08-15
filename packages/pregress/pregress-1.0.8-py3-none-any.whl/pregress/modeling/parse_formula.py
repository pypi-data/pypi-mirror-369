import numpy as np
import pandas as pd
import re
import inspect
from pandas.api.types import CategoricalDtype
from itertools import combinations, product

class FormulaParser:
    def __init__(self, drop_first=True):
        self.drop_first = drop_first
        self.data = None
        self.response_var = None
        
    def parse_formula(self, formula, data=None):
        """
        Parse a formula string and return response variable, predictor names, Y, and X.
        
        Args:
            formula (str): Formula in the form "response ~ predictors"
            data (pd.DataFrame): Data containing the variables
            
        Returns:
            tuple: (response_var, predictor_names, Y, X)
        """
        if data is None:
            data = pd.DataFrame()
        
        self.data = data.copy()
        
        formula = formula.replace(' ', '')
        if '~' not in formula:
            raise ValueError("Formula must contain '~'.")
            
        response_part, predictors_part = formula.split('~', 1)
        
        # Parse response variable (handle transformations including powers)
        response_var, resp_func, resp_power = self._parse_response(response_part)
        self.response_var = response_var
        
        # Resolve external variables
        self._resolve_external_variable(response_var)
        
        # Parse predictors
        include_intercept, predictor_terms = self._parse_predictors(predictors_part)
        
        # Build design matrix
        X = self._build_design_matrix(predictor_terms, include_intercept)
        
        # Apply response transformation
        Y = self._apply_response_transformation(response_var, resp_func, resp_power)
        
        return response_var, X.columns.tolist(), Y, X
    
    def _parse_response(self, response_part):
        """Parse response variable, handling transformations including power transformations."""
        response_part = response_part.strip()
        
        # Check for power transformations first (e.g., "Y^2", "Y^0.5", "Y^(2)")
        power_match = re.match(r'^(\w+)\^(\(?([\d\.]+)\)?)$', response_part)
        if power_match:
            var_name = power_match.group(1)
            power_str = power_match.group(3) if power_match.group(3) else power_match.group(2)
            power = float(power_str)
            return var_name, 'power', power
        
        # Check for function transformations (e.g., "log(Y)", "sqrt(Y)")
        func_match = re.match(r'^(\w+)\((\w+)\)$', response_part)
        if func_match:
            func_name, var_name = func_match.groups()
            return var_name, func_name, None
        
        # Simple variable name
        return response_part, None, None
    
    def _parse_predictors(self, predictors_part):
        """Parse predictor part of formula."""
        predictors_part = predictors_part.strip()
        
        # Check for intercept exclusion
        include_intercept = True
        if '+0' in predictors_part or '-1' in predictors_part:
            include_intercept = False
            predictors_part = predictors_part.replace('+0', '').replace('-1', '')
        
        # Handle .^2 expansion (all variables + all pairwise interactions)
        if '.^2' in predictors_part:
            all_vars = [col for col in self.data.columns if col != self.response_var]
            # Add all variables
            expanded_terms = all_vars.copy()
            # Add all pairwise interactions
            for i in range(len(all_vars)):
                for j in range(i, len(all_vars)):
                    expanded_terms.append(f'{all_vars[i]}:{all_vars[j]}')
            predictors_part = '+'.join(expanded_terms)
        
        # Tokenize into terms
        terms = self._tokenize_formula(predictors_part)
        
        # Separate positive and negative terms
        positive_terms = []
        negative_terms = []
        
        for term in terms:
            if term.startswith('-'):
                negative_terms.append(term[1:])
            else:
                positive_terms.append(term)
        
        # Expand dot notation in positive terms
        expanded_positive = []
        for term in positive_terms:
            if '.' in term:
                expanded_positive.extend(self._expand_dot_notation(term))
            else:
                expanded_positive.append(term)
        
        # Expand dot notation in negative terms (for proper exclusion)
        expanded_negative = []
        for term in negative_terms:
            if '.' in term:
                expanded_negative.extend(self._expand_dot_notation(term))
            else:
                expanded_negative.append(term)
        
        # Remove negative terms from positive terms
        final_terms = []
        for term in expanded_positive:
            if term not in expanded_negative:
                final_terms.append(term)
        
        return include_intercept, final_terms
    
    def _tokenize_formula(self, formula_part):
        """Tokenize formula respecting parentheses and operators."""
        tokens = []
        current_token = ''
        paren_depth = 0
        
        i = 0
        while i < len(formula_part):
            char = formula_part[i]
            
            if char == '(':
                paren_depth += 1
                current_token += char
            elif char == ')':
                paren_depth -= 1
                current_token += char
            elif char == '+' and paren_depth == 0:
                if current_token.strip():
                    tokens.append(current_token.strip())
                current_token = ''
            elif char == '-' and paren_depth == 0:
                # Check if this is a negative term or subtraction
                if current_token.strip():
                    tokens.append(current_token.strip())
                    current_token = '-'
                else:
                    current_token = '-'
            else:
                current_token += char
            
            i += 1
        
        if current_token.strip():
            tokens.append(current_token.strip())
        
        return tokens
    
    def _expand_dot_notation(self, term):
        """Expand dot notation to actual variable names."""
        available_vars = [col for col in self.data.columns if col != self.response_var]
        
        if term == '.':
            return available_vars
        elif ':' in term:
            # Handle interactions with dot
            parts = term.split(':')
            expanded_parts = []
            
            for part in parts:
                if part == '.':
                    expanded_parts.append(available_vars)
                else:
                    expanded_parts.append([part])
            
            # Generate all combinations
            interactions = []
            for combo in product(*expanded_parts):
                if len(set(combo)) == len(combo):  # No self-interactions
                    interactions.append(':'.join(combo))
            
            return interactions
        else:
            return [term]
    
    def _build_design_matrix(self, terms, include_intercept):
        """Build the design matrix from parsed terms."""
        X_dict = {}
        
        for term in terms:
            term_matrix = self._evaluate_term(term)
            X_dict.update(term_matrix)
        
        X = pd.DataFrame(X_dict, index=self.data.index)
        
        if include_intercept:
            X.insert(0, 'Intercept', 1.0)
        
        return X
    
    def _evaluate_term(self, term):
        """Evaluate a single term and return dictionary of columns."""
        term = term.strip()
        
        # Handle interactions first, then power transformations within each part
        if ':' in term:
            return self._handle_interaction(term)
        
        # Handle power transformations for single variables
        # Updated regex to handle both X^2 and X^(2) formats
        power_match = re.match(r'^(\w+)\^(\(?([\d\.]+)\)?)$', term)
        if power_match:
            var_name = power_match.group(1)
            power_str = power_match.group(3) if power_match.group(3) else power_match.group(2)
            power = float(power_str)
            
            # Format power nicely (avoid .0 for integers)
            if power == int(power):
                power_display = str(int(power))
            else:
                power_display = str(power)
            
            self._resolve_external_variable(var_name)
            base_matrix = self._handle_variable(var_name)
            
            result = {}
            for col_name, col_values in base_matrix.items():
                transformed = col_values ** power
                result[f'{col_name}^{power_display}'] = transformed
            
            return result
        
        # Handle function calls
        func_match = re.match(r'^(\w+)\((.+)\)$', term)
        if func_match:
            func_name, inner_term = func_match.groups()
            return self._apply_function(func_name, inner_term)
        
        # Handle simple variable
        return self._handle_variable(term)
    
    def _handle_interaction(self, term):
        """Handle interaction terms like A:B or A:B:C, including power transformations."""
        parts = term.split(':')
        
        # Evaluate each part (which may include power transformations)
        part_matrices = []
        for part in parts:
            # Handle power transformations within interaction parts
            power_match = re.match(r'^(\w+)\^(\(?([\d\.]+)\)?)$', part)
            if power_match:
                var_name = power_match.group(1)
                power_str = power_match.group(3) if power_match.group(3) else power_match.group(2)
                power = float(power_str)
                
                # Format power nicely (avoid .0 for integers)
                if power == int(power):
                    power_display = str(int(power))
                else:
                    power_display = str(power)
                
                self._resolve_external_variable(var_name)
                base_matrix = self._handle_variable(var_name)
                
                # Apply power transformation
                transformed_matrix = {}
                for col_name, col_values in base_matrix.items():
                    transformed = col_values ** power
                    transformed_matrix[f'{col_name}^{power_display}'] = transformed
                
                part_matrices.append(transformed_matrix)
            else:
                self._resolve_external_variable(part)
                part_matrix = self._evaluate_term(part)
                part_matrices.append(part_matrix)
        
        # Compute interaction
        result = {}
        
        # Get all combinations of column names
        column_combinations = product(*[list(pm.keys()) for pm in part_matrices])
        
        for col_combo in column_combinations:
            # Create interaction column name
            interaction_name = ':'.join(col_combo)
            
            # Compute interaction values
            interaction_values = pd.Series(1.0, index=self.data.index)
            for i, col_name in enumerate(col_combo):
                interaction_values *= part_matrices[i][col_name]
            
            result[interaction_name] = interaction_values
        
        return result
    
    def _apply_function(self, func_name, inner_term):
        """Apply transformation function to term."""
        inner_matrix = self._evaluate_term(inner_term)
        result = {}
        
        for col_name, col_values in inner_matrix.items():
            if func_name == 'log':
                transformed = np.log(col_values.clip(lower=0.0001))
                result[f'log({col_name})'] = transformed
            elif func_name == 'sqrt':
                transformed = np.sqrt(col_values.clip(lower=0))
                result[f'sqrt({col_name})'] = transformed
            elif func_name == 'inverse':
                transformed = 1 / col_values.clip(lower=0.0001)
                result[f'inverse({col_name})'] = transformed
            elif func_name.startswith('pow__'):
                power = float(func_name.split('__')[1].replace('_', '.'))
                # Format power nicely (avoid .0 for integers)
                if power == int(power):
                    power_display = str(int(power))
                else:
                    power_display = str(power)
                transformed = col_values ** power
                result[f'{col_name}^{power_display}'] = transformed
            else:
                raise ValueError(f"Unknown function: {func_name}")
        
        return result
    
    def _handle_variable(self, var_name):
        """Handle a single variable, creating dummies if categorical."""
        self._resolve_external_variable(var_name)
        
        col = self.data[var_name]
        
        if isinstance(col.dtype, CategoricalDtype) or col.dtype == object:
            # Create dummy variables and ensure they're float type
            dummies = pd.get_dummies(col, prefix=var_name, drop_first=self.drop_first)
            # Convert to float to avoid boolean masking issues
            return {col_name: dummies[col_name].astype(float) for col_name in dummies.columns}
        else:
            # Numerical variable
            return {var_name: col}
    
    def _resolve_external_variable(self, var_name):
        """Resolve variable from external scope if not in data."""
        if var_name not in self.data.columns:
            frame = inspect.currentframe()
            try:
                # Go up the call stack to find the variable
                for _ in range(10):  # Limit depth to avoid infinite loops
                    frame = frame.f_back
                    if frame is None:
                        break
                    
                    if var_name in frame.f_locals:
                        self.data[var_name] = frame.f_locals[var_name]
                        return
                    elif var_name in frame.f_globals:
                        self.data[var_name] = frame.f_globals[var_name]
                        return
                
                raise KeyError(f"Variable '{var_name}' not found in data or external scope.")
            finally:
                del frame
    
    def _apply_response_transformation(self, response_var, resp_func, resp_power):
        """Apply transformation to response variable."""
        Y = self.data[response_var]
        
        if resp_func == 'power':
            # Handle power transformations
            if resp_power <= 0:
                # For zero or negative powers, clip to avoid division by zero or invalid operations
                Y_clipped = Y.clip(lower=0.0001)
            else:
                Y_clipped = Y
            return Y_clipped ** resp_power
        elif resp_func == 'log':
            return np.log(Y.clip(lower=0.0001))
        elif resp_func == 'sqrt':
            return np.sqrt(Y.clip(lower=0))
        elif resp_func == 'inverse':
            return 1 / Y.clip(lower=0.0001)
        else:
            return Y


# Convenience function to maintain compatibility
def parse_formula(formula, data=None, drop_first=True):
    """
    Parse a formula string and return components for regression modeling.
    
    Args:
        formula (str): Formula string like "Y ~ X1 + X2" or "Y ~ . - X3"
        data (pd.DataFrame): DataFrame containing the variables
        drop_first (bool): Whether to drop first level of categorical variables
        
    Returns:
        tuple: (response_var, predictor_names, Y, X)
    
    Examples:
        >>> data = pd.DataFrame({
        ...     'Y': [1, 2, 3, 4],
        ...     'X1': [1, 2, 3, 4],
        ...     'X2': ['A', 'B', 'A', 'B'],
        ...     'X3': [0.1, 0.2, 0.3, 0.4]
        ... })
        >>> response_var, predictors, Y, X = parse_formula("Y ~ .", data)
        >>> response_var, predictors, Y, X = parse_formula("Y ~ . - X3", data)
        >>> response_var, predictors, Y, X = parse_formula("Y ~ X1 + X2:X3", data)
        >>> response_var, predictors, Y, X = parse_formula("log(Y) ~ log(X1) + X2", data)
        >>> response_var, predictors, Y, X = parse_formula("Y^2 ~ X1 + X2", data)
        >>> response_var, predictors, Y, X = parse_formula("Followers^0.5 ~ Tweets", data)
        >>> response_var, predictors, Y, X = parse_formula("Likes^2 ~ Age^2 + PromoterA:Age^2 + PromoterA", data)
    """
    parser = FormulaParser(drop_first=drop_first)
    return parser.parse_formula(formula, data)
