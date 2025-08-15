"""Unit tests for symbol resolvers."""

import pytest

from chunker.context import BaseSymbolResolver, ContextFactory
from chunker.parser import get_parser


class TestBaseSymbolResolver:
    """Test the base symbol resolver functionality."""

    @classmethod
    def test_init(cls):
        """Test initialization."""
        resolver = BaseSymbolResolver("python")
        assert resolver.language == "python"
        assert resolver._definition_cache == {}
        assert resolver._reference_cache == {}

    @classmethod
    def test_get_symbol_type_unknown(cls):
        """Test getting symbol type for unknown node."""
        resolver = BaseSymbolResolver("python")
        mock_node = type("MockNode", (), {"type": "unknown_node", "parent": None})()
        result = resolver.get_symbol_type(mock_node)
        assert result == "unknown"

    @classmethod
    def test_get_symbol_type_with_parent(cls):
        """Test getting symbol type based on parent."""
        resolver = BaseSymbolResolver("python")
        parent_node = type(
            "MockNode",
            (),
            {"type": "function_definition", "parent": None},
        )()
        child_node = type(
            "MockNode",
            (),
            {"type": "identifier", "parent": parent_node},
        )()
        result = resolver.get_symbol_type(child_node)
        assert result == "function"


class TestPythonSymbolResolver:
    """Test Python-specific symbol resolution."""

    @staticmethod
    @pytest.fixture
    def python_code():
        """Sample Python code for testing."""
        return """
class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, x, y):
        result = x + y
        self.result = result
        return result

def calculate(a, b):
    calc = Calculator()
    return calc.add(a, b)

PI = 3.14159
result = calculate(5, PI)
""".strip()

    @staticmethod
    def test_get_symbol_type_class(python_code):
        """Test getting symbol type for a class."""
        parser = get_parser("python")
        tree = parser.parse(python_code.encode())
        resolver = ContextFactory.create_symbol_resolver("python")

        def find_identifier(node, name):
            if node.type == "identifier" and node.text == name.encode():
                return node
            for child in node.children:
                result = find_identifier(child, name)
                if result:
                    return result
            return None

        for node in tree.root_node.children:
            if node.type == "class_definition":
                calc_id = find_identifier(node, "Calculator")
                if calc_id:
                    symbol_type = resolver.get_symbol_type(calc_id)
                    assert symbol_type == "class"
                    break

    @staticmethod
    def test_get_symbol_type_function(python_code):
        """Test getting symbol type for a function."""
        parser = get_parser("python")
        tree = parser.parse(python_code.encode())
        resolver = ContextFactory.create_symbol_resolver("python")

        def find_function_name(node, name):
            if node.type == "function_definition":
                for child in node.children:
                    if child.type == "identifier" and child.text == name.encode():
                        return child
            for child in node.children:
                result = find_function_name(child, name)
                if result:
                    return result
            return None

        calc_func = find_function_name(tree.root_node, "calculate")
        assert calc_func is not None
        symbol_type = resolver.get_symbol_type(calc_func)
        assert symbol_type == "function"

    @staticmethod
    def test_find_symbol_references(python_code):
        """Test finding symbol references."""
        parser = get_parser("python")
        tree = parser.parse(python_code.encode())
        resolver = ContextFactory.create_symbol_resolver("python")
        refs = resolver.find_symbol_references("Calculator", tree.root_node)
        assert isinstance(refs, list)


class TestJavaScriptSymbolResolver:
    """Test JavaScript-specific symbol resolution."""

    @staticmethod
    @pytest.fixture
    def javascript_code():
        """Sample JavaScript code for testing."""
        return """
class Calculator {
    constructor() {
        this.result = 0;
    }

    add(x, y) {
        const result = x + y;
        this.result = result;
        return result;
    }
}

function calculate(a, b) {
    const calc = new Calculator();
    return calc.add(a, b);
}

const PI = 3.14159;
let result = calculate(5, PI);

export { Calculator, calculate };
""".strip()

    @staticmethod
    def test_get_symbol_type_class(javascript_code):
        """Test getting symbol type for a JavaScript class."""
        parser = get_parser("javascript")
        tree = parser.parse(javascript_code.encode())
        resolver = ContextFactory.create_symbol_resolver("javascript")

        def find_class_identifier(node):
            if node.type == "class_declaration":
                for child in node.children:
                    if child.type == "identifier":
                        return child
            for child in node.children:
                result = find_class_identifier(child)
                if result:
                    return result
            return None

        calc_id = find_class_identifier(tree.root_node)
        assert calc_id is not None
        symbol_type = resolver.get_symbol_type(calc_id)
        assert symbol_type == "class"

    @staticmethod
    def test_get_symbol_type_const(javascript_code):
        """Test getting symbol type for a const declaration."""
        parser = get_parser("javascript")
        tree = parser.parse(javascript_code.encode())
        resolver = ContextFactory.create_symbol_resolver("javascript")

        def find_const_identifier(node, name):
            if node.type == "variable_declarator":
                for child in node.children:
                    if child.type == "identifier" and child.text == name.encode():
                        parent = node.parent
                        if parent and "const" in parent.text.decode():
                            return child
            for child in node.children:
                result = find_const_identifier(child, name)
                if result:
                    return result
            return None

        pi_id = find_const_identifier(tree.root_node, "PI")
        if pi_id:
            symbol_type = resolver.get_symbol_type(pi_id)
            assert symbol_type in {"constant", "variable"}

    @staticmethod
    def test_get_node_type_map():
        """Test the node type mapping for JavaScript."""
        resolver = ContextFactory.create_symbol_resolver("javascript")
        type_map = resolver._get_node_type_map()
        assert "function_declaration" in type_map
        assert type_map["function_declaration"] == "function"
        assert "class_declaration" in type_map
        assert type_map["class_declaration"] == "class"
        assert "const_declaration" in type_map
        assert type_map["const_declaration"] == "constant"
