from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import ast
import contextlib


def _is_sub_node(node):
    return (
        isinstance(node, ast.AST) and not isinstance(node, ast.expr_context)
    )


def _is_leaf(node):
    for field in node._fields:
        attr = getattr(node, field)
        if _is_sub_node(attr):
            return False
        elif isinstance(attr, (list, tuple)):
            for val in attr:
                if _is_sub_node(val):
                    return False
    else:
        return True


def pformat(node, _indent=0):
    if _is_leaf(node):
        return ast.dump(node)
    else:
        class state:
            indent = _indent

        @contextlib.contextmanager
        def indented():
            state.indent += 1
            yield
            state.indent -= 1

        def indentstr():
            return state.indent * '    '

        out = type(node).__name__ + '(\n'
        with indented():
            for field in node._fields:
                attr = getattr(node, field)
                if attr == []:
                    representation = '[]'
                elif (
                        isinstance(attr, list) and
                        len(attr) == 1 and
                        isinstance(attr[0], ast.AST) and
                        _is_leaf(attr[0])
                ):
                    representation = '[{}]'.format(pformat(attr[0]))
                elif isinstance(attr, list):
                    representation = '[\n'
                    with indented():
                        for el in attr:
                            representation += '{}{},\n'.format(
                                indentstr(), pformat(el, state.indent),
                            )
                    representation += indentstr() + ']'
                elif isinstance(attr, ast.AST):
                    representation = pformat(attr, state.indent)
                else:
                    representation = repr(attr)
                out += '{}{}={},\n'.format(indentstr(), field, representation)
        out += indentstr() + ')'
        return out


def pprint(node):
    print(pformat(node))
