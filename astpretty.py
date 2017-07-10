from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
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


def pformat(node, indent='    ', _indent=0):
    if _is_leaf(node):
        if hasattr(node, 'lineno'):
            ret = ast.dump(node)
            # For nodes like Pass() which have information but no data
            if ret.endswith('()'):
                info = '(lineno={}, col_offset={}'.format(
                    node.lineno, node.col_offset,
                )
            else:
                info = '(lineno={}, col_offset={}, '.format(
                    node.lineno, node.col_offset,
                )
            return ret.replace('(', info, 1)
        else:
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
            return state.indent * indent

        def _pformat(el, _indent=0):
            return pformat(el, indent=indent, _indent=_indent)

        out = type(node).__name__ + '(\n'
        with indented():
            if hasattr(node, 'lineno'):
                fields = ('lineno', 'col_offset') + node._fields
            else:
                fields = node._fields

            for field in fields:
                attr = getattr(node, field)
                if attr == []:
                    representation = '[]'
                elif (
                        isinstance(attr, list) and
                        len(attr) == 1 and
                        isinstance(attr[0], ast.AST) and
                        _is_leaf(attr[0])
                ):
                    representation = '[{}]'.format(_pformat(attr[0]))
                elif isinstance(attr, list):
                    representation = '[\n'
                    with indented():
                        for el in attr:
                            representation += '{}{},\n'.format(
                                indentstr(), _pformat(el, state.indent),
                            )
                    representation += indentstr() + ']'
                elif isinstance(attr, ast.AST):
                    representation = _pformat(attr, state.indent)
                else:
                    representation = repr(attr)
                out += '{}{}={},\n'.format(indentstr(), field, representation)
        out += indentstr() + ')'
        return out


def pprint(*args, **kwargs):
    print(pformat(*args, **kwargs))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args(argv)

    with open(args.filename, 'rb') as f:
        contents = f.read()
    pprint(ast.parse(contents))


if __name__ == '__main__':
    exit(main())
