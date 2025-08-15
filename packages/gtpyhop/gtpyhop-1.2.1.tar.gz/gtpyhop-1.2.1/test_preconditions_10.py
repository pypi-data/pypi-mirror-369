# test_preconditions_10.py
"""
Script de test restructuré pour la validation de préconditions avec Lark
Version organisée avec classes pour:
- Validation des préconditions
- Tests organisés par catégories avec différents niveaux de parenthèses
- Séparation des tests valides et invalides
"""

from lark import Lark, ParseError, Transformer, v_args, Token
from typing import Dict, Any, List
import unittest

# Grammaire Lark étendue - VERSION CORRIGÉE
PRECONDITION_GRAMMAR = r"""
    start: precondition_expr

    precondition_expr: comparison_expr
                     | negated_expr

    negated_expr: NOT precondition_expr
                | NOT LPAREN precondition_expr RPAREN

    ?comparison_expr: arithmetic_expr COMPARISON_OP arithmetic_expr
                    | arithmetic_expr MEMBERSHIP_OP interval
                    | arithmetic_expr MEMBERSHIP_OP set_expr

    interval: LBRACKET arithmetic_expr INTERVAL_SEP arithmetic_expr RBRACKET

    set_expr: LBRACE set_elements RBRACE

    set_elements: arithmetic_expr (COMMA arithmetic_expr)*

    ?arithmetic_expr: term
                    | arithmetic_expr ADD_OP term

    ?term: factor
         | term MUL_OP factor

    ?factor: atom
           | atom EXP_OP factor  // Right-associative exponentiation

    ?atom: identifier
         | number
         | LPAREN arithmetic_expr RPAREN

    identifier: IDENTIFIER (DOT IDENTIFIER)*

    number: SIGNED_NUMBER

    // Opérateurs de comparaison et logiques
    COMPARISON_OP: "==" | "!=" | ">=" | "<=" | ">" | "<" | "~"
    NOT: "not"
    
    // Opérateurs de membership
    MEMBERSHIP_OP: "in" | NOT WS+ "in"
    
    // Opérateurs arithmétiques
    ADD_OP: "+" | "-"
    MUL_OP: "*" | "/" | "%"
    EXP_OP: "^"
    
    // Symboles de structure
    LPAREN: "("
    RPAREN: ")"
    LBRACKET: "["
    RBRACKET: "]"
    LBRACE: "{"
    RBRACE: "}"
    DOT: "."
    COMMA: ","
    INTERVAL_SEP: ".."
    
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    SIGNED_NUMBER: /[+-]?[0-9]+(\.[0-9]+)?/

    %import common.WS
    %ignore WS
"""

class ExpressionBase:
    """Base class for expressions"""
    def to_string(self):
        return str(self)

    def _item_to_string(self, item):
        if isinstance(item, Token):
            return str(item).strip()
        elif hasattr(item, 'to_string'):
            return item.to_string()
        else:
            return str(item)

class ArithmeticExpression(ExpressionBase):
    """Arithmetic expression with + or - operators"""
    def __init__(self, items):
        self.items = items
    
    def to_string(self):
        if len(self.items) == 1:
            return self._item_to_string(self.items[0])
        
        result = self._item_to_string(self.items[0])
        for i in range(1, len(self.items), 2):
            if i + 1 < len(self.items):
                op = self._item_to_string(self.items[i])
                operand = self._item_to_string(self.items[i + 1])
                result += f" {op} {operand}"
        return result

class TermExpression(ExpressionBase):
    """Term expression with *, / or % operators"""
    def __init__(self, items):
        self.items = items
    
    def to_string(self):
        if len(self.items) == 1:
            return self._item_to_string(self.items[0])
        
        result = self._item_to_string(self.items[0])
        for i in range(1, len(self.items), 2):
            if i + 1 < len(self.items):
                op = self._item_to_string(self.items[i])
                operand = self._item_to_string(self.items[i + 1])
                result += f" {op} {operand}"
        return result

class ExponentiationExpression(ExpressionBase):
    """Expression with exponentiation operator (^)"""
    def __init__(self, base, exponent):
        self.base = base
        self.exponent = exponent
    
    def to_string(self):
        base_str = self._item_to_string(self.base)
        exp_str = self._item_to_string(self.exponent)
        return f"{base_str} ^ {exp_str}"

class ParenthesizedExpression(ExpressionBase):
    """Expression enclosed in parentheses"""
    def __init__(self, inner_expr):
        self.inner_expr = inner_expr
    
    def to_string(self):
        inner_str = self._item_to_string(self.inner_expr)
        return f"({inner_str})"

class IdentifierExpression(ExpressionBase):
    """Identifier expression with dots (e.g., a.b.c)"""
    def __init__(self, items):
        self.items = items
    
    def to_string(self):
        result = ""
        for item in self.items:
            if isinstance(item, Token):
                if item.type == "DOT":
                    result += "."
                else:
                    result += str(item).strip()
            else:
                result += str(item)
        return result

class NumberExpression(ExpressionBase):
    """Numeric expression"""
    def __init__(self, value):
        self.value = value
    
    def to_string(self):
        return str(self.value).strip()

class IntervalExpression(ExpressionBase):
    """Interval expression [a..b]"""
    def __init__(self, start_expr, end_expr):
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.start_str = self._item_to_string(start_expr)
        self.end_str = self._item_to_string(end_expr)
    
    def to_string(self):
        return f"[{self.start_str}..{self.end_str}]"

class SetExpression(ExpressionBase):
    """Set expression {a, b, c}"""
    def __init__(self, elements):
        self.elements = elements
        self.elements_str = elements.to_string() if hasattr(elements, 'to_string') else str(elements)
    
    def to_string(self):
        return f"{{{self.elements_str}}}"

class SetElementsExpression(ExpressionBase):
    """Set elements expression"""
    def __init__(self, items):
        self.items = items
    
    def to_string(self):
        if not self.items:
            return ""
        
        result = self._item_to_string(self.items[0])
        for i in range(1, len(self.items)):
            item = self.items[i]
            if isinstance(item, Token) and item.type == "COMMA":
                result += ", "
            else:
                result += self._item_to_string(item)
        return result

class NegatedPreconditionExpression(ExpressionBase):
    """Negated precondition expression"""
    def __init__(self, inner_expr, with_parentheses=False):
        self.inner_expr = inner_expr
        self.with_parentheses = with_parentheses
    
    def to_string(self):
        inner_str = self._item_to_string(self.inner_expr)
        if self.with_parentheses:
            return f"not ({inner_str})"
        return f"not {inner_str}"

class ExtendedPreconditionTransformer(Transformer):
    """Transformer for extended precondition grammar - VERSION CORRIGÉE"""
    
    def __init__(self):
        self.components = {}
        super().__init__()
    
    def start(self, items):
        """Entry point"""
        return items[0]
    
    def precondition_expr(self, items):
        """Handle precondition expressions - delegates to child nodes"""
        return items[0]
    
    def negated_expr(self, items):
        """Handle negated expressions - VERSION CORRIGÉE"""
        if len(items) == 2:  # NOT comparison_expr
            expr = items[1]
            expr_str = self._to_string(expr)
            self.components = {
                "type": "negation",
                "inner_expression": expr_str,
                "with_parentheses": False
            }
            return NegatedPreconditionExpression(expr, False)
        elif len(items) == 4:  # NOT LPAREN precondition_expr RPAREN
            expr = items[2]
            expr_str = self._to_string(expr)
            self.components = {
                "type": "negation",
                "inner_expression": expr_str,
                "with_parentheses": True
            }
            return NegatedPreconditionExpression(expr, True)
        return items[0]
    
    def comparison_expr(self, items):
        """Handle comparison expressions"""
        if len(items) == 3:
            left_expr, op, right_expr = items
            
            left_str = self._to_string(left_expr)
            op_str = self._to_string(op)
            right_str = self._to_string(right_expr)
            
            op_type = "membership" if op_str in ["in", "not in"] else "comparison"
            
            self.components = {
                "type": op_type,
                "left_expression": left_str,
                "operator": op_str,
                "right_expression": right_str
            }
            
            if op_type == "membership":
                if isinstance(right_expr, IntervalExpression):
                    self.components["right_type"] = "interval"
                    self.components["interval_start"] = right_expr.start_str
                    self.components["interval_end"] = right_expr.end_str
                elif isinstance(right_expr, SetExpression):
                    self.components["right_type"] = "set"
                    self.components["set_elements"] = right_expr.elements_str
            
            return f"{left_str} {op_str} {right_str}"
        return self._to_string(items[0]) if items else ""
    
    def interval(self, items):
        """Handle intervals [a..b]"""
        if len(items) == 5:
            return IntervalExpression(items[1], items[3])
        return None
    
    def set_expr(self, items):
        """Handle sets {a, b, c}"""
        if len(items) == 3:
            return SetExpression(items[1])
        return None
    
    def set_elements(self, items):
        """Handle set elements"""
        return SetElementsExpression(items)
    
    def arithmetic_expr(self, items):
        """Handle arithmetic expressions"""
        if len(items) == 1:
            return items[0]
        return ArithmeticExpression(items)
    
    def term(self, items):
        """Handle terms"""
        if len(items) == 1:
            return items[0]
        return TermExpression(items)
    
    def factor(self, items):
        """Handle factors including exponentiation"""
        if len(items) == 1:
            return items[0]
        elif len(items) == 3:  # Base ^ Exponent
            base = items[0]
            exponent = items[2]
            return ExponentiationExpression(base, exponent)
        return items[0] if items else ""
    
    def atom(self, items):
        """Handle atoms (basic elements)"""
        if len(items) == 3 and items[0].type == "LPAREN":  # Parenthesized expression
            return ParenthesizedExpression(items[1])
        return items[0]
    
    def identifier(self, items):
        """Handle identifiers"""
        return IdentifierExpression(items)
    
    def number(self, items):
        """Handle numbers"""
        return NumberExpression(items[0]) if items else ""
    
    def _to_string(self, obj):
        """Convert object to string representation"""
        if isinstance(obj, Token):
            return str(obj).strip()
        elif isinstance(obj, str):
            return obj
        elif hasattr(obj, 'to_string'):
            return obj.to_string()
        else:
            return str(obj)

class PreconditionValidator:
    """Classe de validation des préconditions avec méthodes de validation"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        try:
            self.parser = Lark(PRECONDITION_GRAMMAR, parser='lalr')
            self.transformer = ExtendedPreconditionTransformer()
            if self.verbose:
                print("✓ Extended Lark parser initialized successfully")
        except Exception as e:
            if self.verbose:
                print(f"✗ Parser initialization error: {e}")
            raise
    
    def validate_precondition(self, expression: str) -> Dict[str, Any]:
        """Validate a single precondition"""
        try:
            expression = expression.strip()
            
            if not expression:
                return self._error_result(expression, "Empty expression")
            
            tree = self.parser.parse(expression)
            self.transformer.components = {}
            transformed = self.transformer.transform(tree)
            components = self.transformer.components.copy()
            
            return {
                "is_valid": True,
                "expression": expression,
                "message": f"Expression '{expression}' is syntactically valid",
                "error_details": None,
                "components": components if components else None
            }
            
        except ParseError as e:
            return self._error_result(expression, f"Parse error: {str(e)}")
        except Exception as e:
            return self._error_result(expression, f"Unexpected error: {str(e)}")
    
    def validate_preconditions_batch(self, expressions: list) -> Dict[str, Any]:
        """Validate multiple preconditions"""
        if not expressions:
            return {
                "total_count": 0,
                "valid_count": 0,
                "invalid_count": 0,
                "results": [],
                "summary": "No expressions provided for validation"
            }
        
        results = []
        valid_count = 0
        invalid_count = 0
        
        for expr in expressions:
            if not isinstance(expr, str):
                result = {
                    "is_valid": False,
                    "expression": str(expr),
                    "message": "Expression must be a string",
                    "error_details": f"Expected string, got {type(expr).__name__}",
                    "components": None
                }
                invalid_count += 1
            else:
                result = self.validate_precondition(expr)
                if result["is_valid"]:
                    valid_count += 1
                else:
                    invalid_count += 1
            
            results.append(result)
        
        total_count = len(expressions)
        summary = f"Validated {total_count} expressions: {valid_count} valid, {invalid_count} invalid"
        
        return {
            "total_count": total_count,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "results": results,
            "summary": summary
        }
    
    def _error_result(self, expression: str, error_msg: str) -> Dict[str, Any]:
        """Standardized error result"""
        return {
            "is_valid": False,
            "expression": expression,
            "message": f"Expression '{expression}' is syntactically invalid",
            "error_details": error_msg,
            "components": None
        }

class PreconditionTests(unittest.TestCase):
    """Classe de tests pour les préconditions avec différents niveaux de parenthèses"""
    
    def setUp(self):
        """Initialisation du validateur pour chaque test"""
        self.validator = PreconditionValidator(True)
    
    def _test_expressions(self, test_cases, description=""):
        """Méthode utilitaire pour tester des expressions"""
        print(f"\n=== {description} ===")
        
        for expr, expected_valid in test_cases:
            with self.subTest(expression=expr):
                result = self.validator.validate_precondition(expr)
                actual_valid = result["is_valid"]
                status = "✅" if actual_valid == expected_valid else "❌"
                
                print(f"\n{status} '{expr}' -> {actual_valid}")
                if actual_valid and result["components"]:
                    comp = result["components"]
                    print(f"    Type: {comp['type']}")
                    if comp["type"] == "negation":
                        print(f"    Inner Expression: '{comp['inner_expression']}'")
                        print(f"    With Parentheses: {comp['with_parentheses']}")
                    else:
                        print(f"    Left: '{comp['left_expression']}'")
                        print(f"    Operator: '{comp['operator']}'")
                        print(f"    Right: '{comp['right_expression']}'")
                        if "right_type" in comp:
                            print(f"    Right Type: {comp['right_type']}")
                elif not actual_valid:
                    print(f"    Error: {result['error_details']}")
                
                self.assertEqual(actual_valid, expected_valid, 
                               f"Expression '{expr}' should be {'valid' if expected_valid else 'invalid'}")
    
    def test_comparison_operators_valid(self):
        """Test des opérateurs de comparaison - cas valides avec différents niveaux de parenthèses"""
        test_cases = [
            # Niveau 0 : sans parenthèses
            ("x == y", True),
            ("a != b", True),
            ("value > threshold", True),
            ("count <= max_count", True),
            ("temperature >= min_temp", True),
            ("size < limit", True),
            ("pattern ~ regex", True),
            
            # Niveau 1 : parenthèses simples
            ("(x) == (y)", True),
            ("(a + b) != (c + d)", True),
            ("(value) > (threshold)", True),
            
            # Niveau 2 : parenthèses multiples
            ("((x)) == ((y))", True),
            ("((a + b)) != ((c + d))", True),
            
            # Niveau 3 : parenthèses complexes
            ("(((x + 1))) == (((y - 1)))", True),
            ("((a * 2) + (b / 3)) >= ((c - 4) * (d + 5))", True),
        ]
        
        self._test_expressions(test_cases, "Opérateurs de comparaison - Cas valides")
    
    def test_comparison_operators_invalid(self):
        """Test des opérateurs de comparaison - cas invalides"""
        test_cases = [
            # Opérateurs malformés
            ("x = y", False),
            ("a !== b", False),
            ("value >> threshold", False),
            ("count <<= max_count", False),
            
            # Parenthèses non équilibrées
            ("(x == y", False),
            ("x == y)", False),
            ("((x) == y", False),
            ("x == (y))", False),
            
            # Expressions incomplètes
            ("x ==", False),
            ("== y", False),
            ("x >= >= y", False),
        ]
        
        self._test_expressions(test_cases, "Opérateurs de comparaison - Cas invalides")
    
    def test_arithmetic_expressions_valid(self):
        """Test des expressions arithmétiques - cas valides avec différents niveaux de parenthèses"""
        test_cases = [
            # Niveau 0 : expressions simples
            ("x + y == z", True),
            ("a - b != c", True),
            ("p * q > r", True),
            ("m / n <= s", True),
            ("x % y == z", True),
            
            # Niveau 1 : parenthèses simples
            ("(x + y) == z", True),
            ("x == (y + z)", True),
            ("(a - b) * (c + d) == result", True),
            
            # Niveau 2 : parenthèses multiples
            ("((x + y)) == z", True),
            ("(x + (y * z)) == result", True),
            ("((a - b) * (c + d)) == ((e / f) + g)", True),
            
            # Niveau 3 : parenthèses complexes
            ("(((x + y) * z)) == (((a - b) / c))", True),
            ("((x + (y * (z - w)))) == ((a / (b + c)))", True),
            
            # Expressions arithmétiques complexes
            ("a + b * c - d / e == result", True),
            ("(a + b) * (c - d) / (e + f) >= threshold", True),
        ]
        
        self._test_expressions(test_cases, "Expressions arithmétiques - Cas valides")
    
    def test_arithmetic_expressions_invalid(self):
        """Test des expressions arithmétiques - cas invalides"""
        test_cases = [
            # Opérateurs consécutifs
            ("x ++ y == z", False),
            ("a -- b != c", False),
            ("p ** q > r", False),
            ("m // n <= s", False),
            
            # Parenthèses non équilibrées
            ("(x + y == z", False),
            ("x + y) == z", False),
            ("((x + y) == z", False),
            
            # Expressions incomplètes
            ("x + == y", False),
            ("== x + y", False),
            ("x + y ==", False),
            ("+ x == y", False),
        ]
        
        self._test_expressions(test_cases, "Expressions arithmétiques - Cas invalides")
    
    def test_exponentiation_valid(self):
        """Test des exponentiations - cas valides avec différents niveaux de parenthèses"""
        test_cases = [
            # Niveau 0 : exponentiations simples
            ("x^2 == 4", True),
            ("base^exponent > threshold", True),
            ("2^3 == 8", True),
            
            # Niveau 1 : parenthèses simples
            ("(x)^2 == 4", True),
            ("x^(2) == 4", True),
            ("(base)^(exponent) > threshold", True),
            
            # Niveau 2 : parenthèses multiples
            ("((x))^2 == 4", True),
            ("x^((2)) == 4", True),
            ("((x + y))^2 == result", True),
            
            # Niveau 3 : parenthèses complexes et associativité à droite
            ("2^3^2 == 512", True),  # 2^(3^2) = 2^9 = 512
            ("a^b^c == x^(y^z)", True),
            ("(((x + y)))^(((z - w))) == result", True),
            
            # Expressions complexes avec exponentiation
            ("(x + y)^2 == x^2 + 2*x*y + y^2", True),
            ("(a^2 + b^2)^0.5 == c", True),
            ("2^(n+1) - 1 == max_value", True),
        ]
        
        self._test_expressions(test_cases, "Exponentiations - Cas valides")
    
    def test_exponentiation_invalid(self):
        """Test des exponentiations - cas invalides"""
        test_cases = [
            # Exponentiations malformées
            ("x^^2", False),
            ("^2", False),
            ("2^", False),
            ("x^", False),
            
            # Parenthèses non équilibrées avec exponentiation
            ("(x^2 == 4", False),
            ("x^2) == 4", False),
            ("x^(2 == 4", False),
            
            # Expressions incomplètes
            ("^ == 4", False),
            ("x^ == 4", False),
            ("x^^ == 4", False),
        ]
        
        self._test_expressions(test_cases, "Exponentiations - Cas invalides")
    
    def test_intervals_valid(self):
        """Test des intervalles - cas valides avec différents niveaux de parenthèses"""
        test_cases = [
            # Niveau 0 : intervalles simples
            ("x in [0..10]", True),
            ("value in [min..max]", True),
            ("temperature in [-10..50]", True),
            
            # Niveau 1 : parenthèses simples
            ("(x) in [0..10]", True),
            ("x in [(0)..(10)]", True),
            ("(value + offset) in [min..max]", True),
            
            # Niveau 2 : parenthèses multiples
            ("((x)) in [0..10]", True),
            ("x in [((min))..((max))]", True),
            ("((x + y)) in [(min - delta)..(max + delta)]", True),
            
            # Niveau 3 : parenthèses complexes
            ("(((x * factor))) in [(((min_base)))..((max_base))]", True),
            ("((x + (y * z))) in [((a - b))..(c + (d / e))]", True),
            
            # Intervalles avec expressions complexes
            ("x^2 in [0..100]", True),
            ("(x - center)^2 in [0..radius^2]", True),
            ("point.x in [bounds.min..bounds.max]", True),
            
            # Négation d'intervalles
            ("value not in [forbidden_min..forbidden_max]", True),
            ("(result + bias) not in [error_range.start..error_range.end]", True),
        ]
        
        self._test_expressions(test_cases, "Intervalles - Cas valides")
    
    def test_intervals_invalid(self):
        """Test des intervalles - cas invalides"""
        test_cases = [
            # Syntaxe d'intervalle incorrecte
            ("x in [0.10]", False),
            ("x in [0...10]", False),
            ("x in (0..10)", False),
            ("x in {0..10}", False),
            
            # Intervalles incomplets
            ("x in [..10]", False),
            ("x in [0..]", False),
            ("x in [..]", False),
            ("x in []", False),
            
            # Parenthèses non équilibrées
            ("x in [0..10", False),
            ("x in 0..10]", False),
            ("(x in [0..10]", False),
            ("x in [0..10])", False),
            
            # Expressions malformées
            ("in [0..10]", False),
            ("x in", False),
            ("x in [0..10] in [20..30]", False),
        ]
        
        self._test_expressions(test_cases, "Intervalles - Cas invalides")
    
    def test_sets_valid(self):
        """Test des ensembles - cas valides avec différents niveaux de parenthèses"""
        test_cases = [
            # Niveau 0 : ensembles simples
            ("x in {1, 2, 3}", True),
            ("status in {active, inactive, pending}", True),
            ("color in {red, green, blue}", True),
            
            # Niveau 1 : parenthèses simples
            ("(x) in {1, 2, 3}", True),
            ("x in {(1), (2), (3)}", True),
            ("(status + modifier) in {state1, state2}", True),
            
            # Niveau 2 : parenthèses multiples
            ("((x)) in {1, 2, 3}", True),
            ("x in {((1)), ((2)), ((3))}", True),
            ("((result % base)) in {((val1)), ((val2))}", True),
            
            # Niveau 3 : parenthèses complexes
            ("(((x + offset))) in {(((min_val))), (((max_val)))}", True),
            ("((x * (y + z))) in {((a - b)), ((c + d)), ((e / f))}", True),
            
            # Ensembles avec expressions complexes
            ("x^2 in {1, 4, 9, 16}", True),
            ("result.type in {success, warning, error}", True),
            ("(temperature - 32) * 5/9 in {celsius_values}", True),
            
            # Négation d'ensembles
            ("status not in {error, failed, timeout}", True),
            ("(code % 100) not in {forbidden_codes}", True),
        ]
        
        self._test_expressions(test_cases, "Ensembles - Cas valides")
    
    def test_sets_invalid(self):
        """Test des ensembles - cas invalides"""
        test_cases = [
            # Syntaxe d'ensemble incorrecte
            ("x in (1, 2, 3)", False),
            ("x in [1, 2, 3]", False),
            ("x in 1, 2, 3", False),
            
            # Ensembles incomplets ou malformés
            ("x in {}", False),
            ("x in {1,}", False),
            ("x in {,2}", False),
            ("x in {1,,3}", False),
            
            # Parenthèses non équilibrées
            ("x in {1, 2, 3", False),
            ("x in 1, 2, 3}", False),
            ("(x in {1, 2, 3}", False),
            ("x in {1, 2, 3})", False),
            
            # Expressions malformées
            ("in {1, 2, 3}", False),
            ("x in", False),
            ("x in {1, 2, 3} in {4, 5, 6}", False),
        ]
        
        self._test_expressions(test_cases, "Ensembles - Cas invalides")
    
    def test_negated_preconditions_valid(self):
        """Test des préconditions négatives - cas valides avec différents niveaux de parenthèses"""
        test_cases = [
            # Niveau 0 : négations simples
            ("not x == y", True),
            ("not a > b", True),
            ("not value in [0..10]", True),
            ("not status in {error, failed}", True),
            
            # Niveau 1 : négations avec parenthèses simples
            ("not (x == y)", True),
            ("not (a > b)", True),
            ("not (value in [0..10])", True),
            ("not (status in {error, failed})", True),
            
            # Niveau 2 : négations avec parenthèses multiples
            ("not ((value + offset) in [min..max])", True),
            ("not ((x^2 + y^2) <= radius^2)", True),
            
            # Niveau 3 : négations avec parenthèses complexes
            ("not (((x + y) * z) == (((a - b) / c)))", True),
            ("not (((point.x))^2 + ((point.y))^2 <= ((radius))^2)", True),
            
            # Négations complexes
            ("not x^2 in [0..100]", True),
            ("not (base^n == target)", True),
            ("not ((a + b)^2 == c^2 + d^2)", True),
            ("not point in [x_min..x_max]", True),
            
            # Négations multiples
            ("not not x == y", True),
            ("not (not (a > b))", True),
            ("not not not x == y", True),
            ("not (not (not (a > b)))", True),
            
            # Négations avec expressions complexes
            ("not ((x^2 + y^2)^0.5 in [0..max_radius])", True),
            ("not (value^exponent in {2^1, 2^2, 2^3, 2^4})", True),
        ]
        
        self._test_expressions(test_cases, "Préconditions négatives - Cas valides")
    
    def test_negated_preconditions_invalid(self):
        """Test des préconditions négatives - cas invalides"""
        test_cases = [
            # Négations incomplètes
            ("not", False),
            ("not )", False),
            ("not (", False),
            
            # Parenthèses non équilibrées avec négation
            ("not (x == y", False),
            ("not x == y)", False),
            ("not ((x == y)", False),
            ("not (x == y))", False),
            
            # Expressions malformées avec négation
            ("not not", False),
            ("not (not)", False),
            ("not (not ()", False),
            ("not () == y", False),
            
            # Négations de constructions invalides
            ("not x ==", False),
            ("not == y", False),
            ("not (x ==)", False),
            ("not (== y)", False),

            # Négation de préconditions avec parenthèses multiples            
            ("not ((x == y))", False),
            ("not ((distance^2 <= threshold^2))", False),
        ]
        
        self._test_expressions(test_cases, "Préconditions négatives - Cas invalides")

def run_all_tests():
    """Fonction pour exécuter tous les tests"""
    print("🚀 Démarrage des tests de validation des préconditions")
    print("=" * 60)
    
    # Créer une suite de tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(PreconditionTests)
    
    # Exécuter les tests avec des détails
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Résumé final
    print("\n" + "=" * 60)
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ Tous les tests ont réussi!")
    else:
        print("❌ Certains tests ont échoué.")
        
    return result.wasSuccessful()

if __name__ == "__main__":
    # Initialiser le validateur global pour les tests manuels
    print("Initialisation du validateur de préconditions...")
    try:
        global_validator = PreconditionValidator()
        print("✓ Validateur initialisé avec succès")
    except Exception as e:
        print(f"✗ Erreur d'initialisation: {e}")
        exit(1)
    
    # Exécuter tous les tests
    success = run_all_tests()
    
    if success:
        print("\n🎉 Tous les tests de validation sont passés avec succès!")
    else:
        print("\n⚠️  Certains tests ont échoué, vérifiez les détails ci-dessus.")
