"""Module for AST Transformer subclass which specially-parses utility expressions"""

import ast
from collections import deque
from typing import Dict, Set, Tuple, Union

import astor
import numpy as np
from numexpr import expressions as nee

from .constants import NAN_STR
from .exceptions import UnsupportedSyntaxError
from .expr_items import ChainedSymbol, EvaluationMode

# Only nodes used in expressions are included, due to the limited parsing
_UNSUPPORTED_NODES: Tuple[type] = (
    ast.Load,
    ast.Store,
    ast.Del,
    ast.IfExp,
    ast.Subscript,
    ast.ListComp,
    ast.DictComp,
    ast.Starred,
)
_NAN_REPRESENTATIONS = {"none", "nan"}
_NUMEXPR_FUNCTIONS = set(nee.functions.keys())
_SUPPORTED_AGGREGATIONS = {"count", "first", "last", "max", "min", "mean", "median", "prod", "std", "sum", "var"}

Number = Union[int, float, np.float64]


class ExpressionParser(ast.NodeTransformer):

    def __init__(self, prior_simple: Set[str] = None, prior_chained: Set[str] = None, mode=EvaluationMode.UTILITIES):
        self.mode: EvaluationMode = mode

        self.dict_literals: Dict[str, Dict[tuple, Number]] = {}

        # Optionally, use an ongoing collection of simple and chained symbols to enforce consistent usage
        # across a group of expressions
        self.simple_symbols: Set[str] = set() if prior_simple is None else prior_simple
        self.all_chained_symbols = prior_chained if prior_chained is not None else set()
        self.chained_symbols: Dict[str, ChainedSymbol] = {}
        self.visited_simple: Set[str] = set()

    def visit(self, node):
        return self.__get_visitor(node)(node)

    def __get_visitor(self, node):
        if isinstance(node, _UNSUPPORTED_NODES):
            raise UnsupportedSyntaxError(node.__class__.__name__)
        name = "visit_" + node.__class__.__name__.lower()
        return getattr(self, name) if hasattr(self, name) else self.generic_visit

    # region Required transformations for NumExpr

    @staticmethod
    def visit_str(node):
        # Converts text-strings to NumExpr-supported byte-strings
        return ast.Bytes(node.s.encode())

    def visit_unaryop(self, node):
        # Converts 'not' into '~' which NumExpr supports
        if isinstance(node.op, ast.Not):
            return ast.UnaryOp(op=ast.Invert(), operand=self.visit(node.operand))
        elif isinstance(node.op, ast.USub):
            return node
        raise NotImplementedError(type(node.op))

    def visit_boolop(self, node):
        # Converts 'and' and 'or' into '&' and '|' which NumExpr supports
        # BoolOp objects have a list of values but need to be converted into a tree of BinOps

        if isinstance(node.op, ast.And):
            new_op = ast.BitAnd()
        elif isinstance(node.op, ast.Or):
            new_op = ast.BitOr()
        else:
            raise NotImplementedError(type(node.op))

        values = node.values
        left = self.visit(values[0])
        i = 1
        while i < len(values):
            right = self.visit(values[i])
            left = ast.BinOp(left=left, right=right, op=new_op)
            i += 1
        return left

    def visit_compare(self, compare_node: ast.Compare):
        # Visit downstream symbols
        new_left = self.visit(compare_node.left)
        new_comparators = [self.visit(node) for node in compare_node.comparators]

        # Simple comparison node
        if len(new_comparators) == 1:
            return ast.Compare(left=new_left, comparators=[new_comparators[0]], ops=compare_node.ops)

        # Compound comparison node

        # Convert to multiple Compare operations
        new_nodes, left = [], new_left
        for right, op in zip(new_comparators, compare_node.ops):
            new_node = ast.Compare(left=left, comparators=[right], ops=[op])
            new_nodes.append(new_node)
            left = right

        assert len(new_nodes) >= 2

        bin_op = ast.BinOp(left=new_nodes[0], right=new_nodes[1], op=ast.BitAnd())
        for new_right in new_nodes[2:]:
            bin_op = ast.BinOp(left=bin_op, right=new_right, op=ast.BitAnd())
        return bin_op

    def visit_call(self, node):
        func_node = node.func

        if isinstance(func_node, ast.Name):
            # Top-level function
            return self.__visit_toplevel_func(node, func_node)
        elif isinstance(func_node, ast.Attribute):
            # Method of an object
            return self.__visit_method(node, func_node)
        else:
            return self.generic_visit(node)

    def __visit_toplevel_func(self, node, func_node):
        func_name = func_node.id
        if func_name not in _NUMEXPR_FUNCTIONS:
            raise UnsupportedSyntaxError("Function '%s' not supported." % func_name)

        node.args = [self.__get_visitor(arg)(arg) for arg in node.args]
        node.starargs = None
        if not hasattr(node, "kwargs"):
            node.kwargs = None

        return node

    # endregion

    # region Dict literals

    @staticmethod
    def __get_dict_key(node) -> tuple:
        if isinstance(node, ast.Name):
            return (node.id,)
        if isinstance(node, ast.Str):
            return (node.s,)
        if isinstance(node, ast.Attribute):
            keylist = deque()
            while not isinstance(node, ast.Name):
                keylist.appendleft(node.attr)
                node = node.value
            keylist.appendleft(node.id)
            return tuple(keylist)
        raise UnsupportedSyntaxError("Dict key of type '%s' unsupported" % node)

    @staticmethod
    def __resolve_key_levels(keys: list, max_level: int):
        assert max_level >= 1
        resovled_keys = []
        for key in keys:
            # Convert to list to pad if needed
            converted = list(key) if isinstance(key, tuple) else [key]
            length = len(converted)

            if max_level == 1:
                if length != 1:
                    raise UnsupportedSyntaxError("Inconsistent usage of multi-item keys")
                resovled_keys.append(converted[0])  # Convert to singleton for consistency
            elif length <= max_level:
                # Applies to top-level
                for _ in range(max_level - length):
                    converted.append(".")
                resovled_keys.append(tuple(converted))
            else:
                raise NotImplementedError("This should never happen. Length=%s Max length=%s" % (length, max_level))
        return resovled_keys

    def visit_dict(self, node):
        if not self.mode != EvaluationMode.UTILITIES:
            raise UnsupportedSyntaxError("Dict literals not allowed in this context")

        substitution = "__dict%s" % len(self.dict_literals)
        new_node = ast.Name(substitution, ast.Load())

        try:

            new_literal = {}
            for key_node, val_node in zip(node.keys, node.values):
                new_key = self.__get_dict_key(key_node)

                if isinstance(val_node, ast.UnaryOp):
                    assert isinstance(val_node.operand, ast.Num)
                    assert isinstance(val_node.op, ast.USub)
                    new_val = np.float32(-val_node.operand.n)
                elif isinstance(val_node, ast.Num):
                    new_val = np.float32(val_node.n)
                else:
                    raise ValueError()

                new_literal[new_key] = new_val

            self.dict_literals[substitution] = new_literal

            return new_node

        except (ValueError, AssertionError):
            # Catch simple errors and emit them as syntax errors
            raise UnsupportedSyntaxError("Dict literals are supported for numeric values only")

    # endregion

    # region Simple symbols

    def visit_name(self, node):
        symbol_name = node.id

        if symbol_name.lower() in _NAN_REPRESENTATIONS:
            # Allow None or NaN or nan to mean 'null'
            node.id = NAN_STR
        elif symbol_name in self.all_chained_symbols:
            raise UnsupportedSyntaxError("Inconsistent use for symbol '%s'" % symbol_name)
        else:
            self.simple_symbols.add(symbol_name)
            self.visited_simple.add(symbol_name)
        return node

    # endregion

    # region Chained symbols

    def visit_attribute(self, node):
        name, chain = self.__get_name_from_attribute(node)

        if name in self.simple_symbols:
            raise UnsupportedSyntaxError("Inconsistent usage of symbol '%s'" % name)

        if name in self.chained_symbols:
            container = self.chained_symbols[name]
        else:
            container = ChainedSymbol(name)
            self.chained_symbols[name] = container
        self.all_chained_symbols.add(name)
        substitution = container.add_chain(chain)

        return ast.Name(substitution, ast.Load())

    @staticmethod
    def __get_name_from_attribute(node):
        current_node = node
        stack = deque()
        while not isinstance(current_node, ast.Name):
            if not isinstance(current_node, ast.Attribute):
                raise UnsupportedSyntaxError()
            stack.append(current_node.attr)
            current_node = current_node.value

        return current_node.id, stack

    def __visit_method(self, call_node, func_node):
        name, chain = self.__get_name_from_attribute(func_node)
        func_name = chain.popleft()

        if func_name not in _SUPPORTED_AGGREGATIONS:
            raise UnsupportedSyntaxError("Aggregation method '%s' is not supported." % func_name)

        if not hasattr(call_node, "starargs"):
            call_node.starargs = None
        if not hasattr(call_node, "kwargs"):
            call_node.kwargs = None

        if len(call_node.keywords) > 0:
            raise UnsupportedSyntaxError("Keyword args are not supported inside aggregations")
        if call_node.starargs is not None or call_node.kwargs is not None:
            raise UnsupportedSyntaxError("Star-args or star-kwargs are not supported inside aggregations")
        arg_expression = astor.to_source(call_node.args[0])

        if name in self.simple_symbols:
            raise UnsupportedSyntaxError("Inconsistent usage of symbol '%s'" % name)

        if name in self.chained_symbols:
            container = self.chained_symbols[name]
        else:
            container = ChainedSymbol(name)
            self.chained_symbols[name] = container
        self.all_chained_symbols.add(name)
        substitution = container.add_chain(chain, func_name, arg_expression)

        new_node = ast.Name(substitution, ast.Load())
        return new_node

    # endregion
