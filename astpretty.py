import argparse
import ast
import contextlib
import sys
from typing import Any
from typing import Generator
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import TYPE_CHECKING
from typing import Union

if TYPE_CHECKING:
    from typed_ast import ast27
    from typed_ast import ast3
    ASTType = Union[ast.AST, ast27.AST, ast3.AST]

AST: Tuple[Type[Any], ...] = (ast.AST,)
expr_context: Tuple[Type[Any], ...] = (ast.expr_context,)
try:  # pragma: no cover (with typed-ast)
    from typed_ast import ast27
    from typed_ast import ast3
except ImportError:  # pragma: no cover (without typed-ast)
    typed_support = False
else:  # pragma: no cover (with typed-ast)
    AST += (ast27.AST, ast3.AST)
    expr_context += (ast27.expr_context, ast3.expr_context)
    typed_support = True


def _is_sub_node(node: Any) -> bool:
    return isinstance(node, AST) and not isinstance(node, expr_context)


def _is_leaf(node: 'ASTType') -> bool:
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


def _fields(n: 'ASTType', show_offsets: bool = True) -> Tuple[str, ...]:
    if show_offsets:
        return n._attributes + n._fields
    else:
        return n._fields


def _leaf(node: 'ASTType', show_offsets: bool = True) -> str:
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
        node: Union['ASTType', None, str],
        indent: Union[str, int] = '    ',
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

        def _pformat(el: Union['ASTType', None, str], _indent: int = 0) -> str:
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


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument(
        '--no-show-offsets', dest='show_offsets',
        action='store_false',
    )
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument(
        '--untyped', default=ast.parse,
        dest='parse_func', action='store_const', const=ast.parse,
        help='(default) Use the stdlib `ast` parser.',
    )
    if typed_support:  # pragma: no cover (requires typed-ast)
        grp.add_argument(
            '--typed-27',
            dest='parse_func', action='store_const', const=ast27.parse,
            help='Use typed_ast.ast27 to parse the ast.',
        )
        grp.add_argument(
            '--typed-3',
            dest='parse_func', action='store_const', const=ast3.parse,
            help='Use typed_ast.ast3 to parse the ast.',
        )
    args = parser.parse_args(argv)

    type_comments = args.parse_func is ast.parse and sys.version_info >= (3, 8)
    if type_comments:  # pragma: no cover (py38+)
        kwargs = {'type_comments': True}
    else:  # pragma: no cover (<py38)
        kwargs = {}

    with open(args.filename, 'rb') as f:
        contents = f.read()
    pprint(args.parse_func(contents, **kwargs), show_offsets=args.show_offsets)
    return 0


if __name__ == '__main__':
    exit(main())
