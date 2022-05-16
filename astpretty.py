from __future__ import annotations

import argparse
import ast
import contextlib
from typing import Any
from typing import Generator
from typing import Sequence

AST: tuple[type[Any], ...] = (ast.AST,)
expr_context: tuple[type[Any], ...] = (ast.expr_context,)


def _is_sub_node(node: object) -> bool:
    return isinstance(node, AST) and not isinstance(node, expr_context)


def _is_leaf(node: ast.AST) -> bool:
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


def _fields(n: ast.AST, show_offsets: bool = True) -> tuple[str, ...]:
    if show_offsets:
        return n._attributes + n._fields
    else:
        return n._fields


def _leaf(node: ast.AST, show_offsets: bool = True) -> str:
    if isinstance(node, AST):
        return '{}({})'.format(
            type(node).__name__,
            ', '.join(
                '{}={}'.format(
                    field,
                    _leaf(getattr(node, field), show_offsets=show_offsets),
                )
                for field in _fields(node, show_offsets=show_offsets)
            ),
        )
    elif isinstance(node, list):
        return '[{}]'.format(
            ', '.join(_leaf(x, show_offsets=show_offsets) for x in node),
        )
    else:
        return repr(node)


def pformat(
        node: ast.AST | None | str,
        indent: str | int = '    ',
        show_offsets: bool = True,
        _indent: int = 0,
) -> str:
    if node is None:
        return repr(node)
    elif isinstance(node, str):  # pragma: no cover (ast27 typed-ast args)
        return repr(node)
    elif _is_leaf(node):
        return _leaf(node, show_offsets=show_offsets)
    else:
        if isinstance(indent, int):
            indent_s = indent * ' '
        else:
            indent_s = indent

        class state:
            indent = _indent

        @contextlib.contextmanager
        def indented() -> Generator[None, None, None]:
            state.indent += 1
            yield
            state.indent -= 1

        def indentstr() -> str:
            return state.indent * indent_s

        def _pformat(el: ast.AST | None | str, _indent: int = 0) -> str:
            return pformat(
                el, indent=indent, show_offsets=show_offsets,
                _indent=_indent,
            )

        out = type(node).__name__ + '(\n'
        with indented():
            for field in _fields(node, show_offsets=show_offsets):
                attr = getattr(node, field)
                if attr == []:
                    representation = '[]'
                elif (
                        isinstance(attr, list) and
                        len(attr) == 1 and
                        isinstance(attr[0], AST) and
                        _is_leaf(attr[0])
                ):
                    representation = f'[{_pformat(attr[0])}]'
                elif isinstance(attr, list):
                    representation = '[\n'
                    with indented():
                        for el in attr:
                            representation += '{}{},\n'.format(
                                indentstr(), _pformat(el, state.indent),
                            )
                    representation += indentstr() + ']'
                elif isinstance(attr, AST):
                    representation = _pformat(attr, state.indent)
                else:
                    representation = repr(attr)
                out += f'{indentstr()}{field}={representation},\n'
        out += indentstr() + ')'
        return out


def pprint(*args: Any, **kwargs: Any) -> None:
    print(pformat(*args, **kwargs))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument(
        '--no-show-offsets', dest='show_offsets',
        action='store_false',
    )
    args = parser.parse_args(argv)

    with open(args.filename, 'rb') as f:
        contents = f.read()

    tree = ast.parse(contents, filename=args.filename, type_comments=True)
    pprint(tree, show_offsets=args.show_offsets)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
