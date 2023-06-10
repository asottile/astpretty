from __future__ import annotations

import ast
import sys

import pytest

import astpretty


def _to_module_body(s):
    return ast.parse(s).body[0]


def _to_expr_value(s):
    return _to_module_body(s).value


@pytest.mark.parametrize('s', ('x', '"y"', '5', '[]'))
def test_is_leaf_true(s):
    assert astpretty._is_leaf(_to_expr_value(s)) is True


def test_is_leaf_has_attr_with_list_of_primitives():
    assert astpretty._is_leaf(_to_module_body('global x, y')) is True


@pytest.mark.parametrize('s', ('a.b', '[4]', 'x()'))
def test_is_leaf_false(s):
    assert astpretty._is_leaf(_to_expr_value(s)) is False


def test_pformat_py35_regression():
    expected = (
        'Dict(\n'
        '    keys=[\n'
        "        Name(id='a', ctx=Load()),\n"
        '        None,\n'
        '    ],\n'
        '    values=[\n'
        "        Name(id='b', ctx=Load()),\n"
        "        Name(id='k', ctx=Load()),\n"
        '    ],\n'
        ')'
    )
    s = '{a: b, **k}'
    assert astpretty.pformat(_to_expr_value(s), show_offsets=False) == expected


def test_pformat_node():
    ret = astpretty.pformat(_to_expr_value('x'), show_offsets=False)
    assert ret == "Name(id='x', ctx=Load())"


def test_pformat_nested_with_offsets():
    expected = (
        'Assign(\n'
        '    lineno=1,\n'
        '    col_offset=0,\n'
        '    end_lineno=1,\n'
        '    end_col_offset=5,\n'
        "    targets=[Name(lineno=1, col_offset=0, end_lineno=1, end_col_offset=1, id='x', ctx=Store())],\n"  # noqa: E501
        '    value=Constant(lineno=1, col_offset=4, end_lineno=1, end_col_offset=5, value=5, kind=None),\n'  # noqa: E501
        '    type_comment=None,\n'
        ')'
    )
    ret = astpretty.pformat(_to_module_body('x = 5'))
    assert ret == expected


def test_pformat_nested_attr_empty_list():
    ret = astpretty.pformat(_to_module_body('if x: pass'), show_offsets=False)
    assert ret == (
        'If(\n'
        "    test=Name(id='x', ctx=Load()),\n"
        '    body=[Pass()],\n'
        '    orelse=[],\n'
        ')'
    )


def test_pformat_mixed_sub_nodes_and_primitives():
    node = _to_module_body('from y import x')
    ret = astpretty.pformat(node, show_offsets=False)
    assert ret == (
        'ImportFrom(\n'
        "    module='y',\n"
        "    names=[alias(name='x', asname=None)],\n"
        '    level=0,\n'
        ')'
    )


def test_pformat_nested_multiple_elements():
    ret = astpretty.pformat(_to_expr_value('[a, b, c]'), show_offsets=False)
    assert ret == (
        'List(\n'
        '    elts=[\n'
        "        Name(id='a', ctx=Load()),\n"
        "        Name(id='b', ctx=Load()),\n"
        "        Name(id='c', ctx=Load()),\n"
        '    ],\n'
        '    ctx=Load(),\n'
        ')'
    )


def test_pformat_custom_indent():
    node = _to_expr_value('[a, b, c]')
    ret = astpretty.pformat(node, indent='\t', show_offsets=False)
    assert ret == (
        'List(\n'
        '\telts=[\n'
        "\t\tName(id='a', ctx=Load()),\n"
        "\t\tName(id='b', ctx=Load()),\n"
        "\t\tName(id='c', ctx=Load()),\n"
        '\t],\n'
        '\tctx=Load(),\n'
        ')'
    )


def test_pformat_integer_indent():
    node = _to_expr_value('[a, b, c]')
    ret = astpretty.pformat(node, indent=3, show_offsets=False)
    assert ret == (
        'List(\n'
        '   elts=[\n'
        "      Name(id='a', ctx=Load()),\n"
        "      Name(id='b', ctx=Load()),\n"
        "      Name(id='c', ctx=Load()),\n"
        '   ],\n'
        '   ctx=Load(),\n'
        ')'
    )


def test_pformat_nested_node_without_line_information():
    expected_39 = (
        'Subscript(\n'
        '    lineno=1,\n'
        '    col_offset=0,\n'
        '    end_lineno=1,\n'
        '    end_col_offset=4,\n'
        "    value=Name(lineno=1, col_offset=0, end_lineno=1, end_col_offset=1, id='a', ctx=Load()),\n"  # noqa: E501
        '    slice=Constant(lineno=1, col_offset=2, end_lineno=1, end_col_offset=3, value=0, kind=None),\n'  # noqa: E501
        '    ctx=Load(),\n'
        ')'
    )
    expected_38 = (
        'Subscript(\n'
        '    lineno=1,\n'
        '    col_offset=0,\n'
        '    end_lineno=1,\n'
        '    end_col_offset=4,\n'
        "    value=Name(lineno=1, col_offset=0, end_lineno=1, end_col_offset=1, id='a', ctx=Load()),\n"  # noqa: E501
        '    slice=Index(\n'
        '        value=Constant(lineno=1, col_offset=2, end_lineno=1, end_col_offset=3, value=0, kind=None),\n'  # noqa: E501
        '    ),\n'
        '    ctx=Load(),\n'
        ')'
    )
    expected = expected_39 if sys.version_info >= (3, 9) else expected_38
    ret = astpretty.pformat(_to_expr_value('a[0]'))
    assert ret == expected


def test_pformat_leaf_node_with_list():
    ret = astpretty.pformat(_to_module_body('global x, y'), show_offsets=False)
    assert ret == "Global(names=['x', 'y'])"


def test_pprint(capsys):
    astpretty.pprint(_to_expr_value('x'), show_offsets=False)
    out, _ = capsys.readouterr()
    assert out == "Name(id='x', ctx=Load())\n"


def test_main_with_offsets(capsys, tmpdir):
    expected = '''\
Module(
    body=[
        Assign(
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=5,
            targets=[Name(lineno=1, col_offset=0, end_lineno=1, end_col_offset=1, id='x', ctx=Store())],
            value=Name(lineno=1, col_offset=4, end_lineno=1, end_col_offset=5, id='y', ctx=Load()),
            type_comment=None,
        ),
    ],
    type_ignores=[],
)
'''  # noqa: E501
    f = tmpdir.join('test.py')
    f.write('x = y\n')
    astpretty.main((f.strpath,))
    out, _ = capsys.readouterr()
    assert out == expected


def test_main_hide_offsets(capsys, tmpdir):
    expected = '''\
Module(
    body=[
        Assign(
            targets=[Name(id='x', ctx=Store())],
            value=Name(id='y', ctx=Load()),
            type_comment=None,
        ),
    ],
    type_ignores=[],
)
'''
    f = tmpdir.join('test.py')
    f.write('x = y\n')
    astpretty.main((f.strpath, '--no-show-offsets'))
    out, _ = capsys.readouterr()
    assert out == expected


TYPED_SRC = 'x = 5  # type: int\nx = "foo"  # type: ignore\n'
TYPED27_OUT = '''\
Module(
    body=[
        Assign(
            lineno=1,
            col_offset=0,
            targets=[Name(lineno=1, col_offset=0, id='x', ctx=Store())],
            value=Num(lineno=1, col_offset=4, n=5),
            type_comment='int',
        ),
        Assign(
            lineno=2,
            col_offset=0,
            targets=[Name(lineno=2, col_offset=0, id='x', ctx=Store())],
            value=Str(lineno=2, col_offset=4, s=b'foo', kind=''),
            type_comment=None,
        ),
    ],
    type_ignores=[TypeIgnore(lineno=2, tag='')],
)
'''
TYPED3_OUT = '''\
Module(
    body=[
        Assign(
            lineno=1,
            col_offset=0,
            targets=[Name(lineno=1, col_offset=0, id='x', ctx=Store())],
            value=Num(lineno=1, col_offset=4, n=5),
            type_comment='int',
        ),
        Assign(
            lineno=2,
            col_offset=0,
            targets=[Name(lineno=2, col_offset=0, id='x', ctx=Store())],
            value=Str(lineno=2, col_offset=4, s='foo', kind=''),
            type_comment=None,
        ),
    ],
    type_ignores=[TypeIgnore(lineno=2, tag='')],
)
'''
FUNC_SRC = '''\
def f(
    self,
    s,  # type: str
):
    # type: (...) -> None
    pass
'''
FUNC_SRC_TYPED27_OUT = '''\
Module(
    body=[
        FunctionDef(
            lineno=1,
            col_offset=0,
            name='f',
            args=arguments(
                args=[
                    Name(lineno=2, col_offset=4, id='self', ctx=Param()),
                    Name(lineno=3, col_offset=4, id='s', ctx=Param()),
                ],
                vararg=None,
                kwarg=None,
                defaults=[],
                type_comments=[
                    None,
                    'str',
                ],
            ),
            body=[Pass(lineno=6, col_offset=4)],
            decorator_list=[],
            type_comment='(...) -> None',
        ),
    ],
    type_ignores=[],
)
'''


def test_pformat_py38_type_comments(tmpdir, capsys):
    expected_38 = '''\
Module(
    body=[
        FunctionDef(
            lineno=1,
            col_offset=0,
            end_lineno=2,
            end_col_offset=8,
            name='f',
            args=arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
            body=[Pass(lineno=2, col_offset=4, end_lineno=2, end_col_offset=8)],
            decorator_list=[],
            returns=None,
            type_comment='() -> None',
        ),
    ],
    type_ignores=[TypeIgnore(lineno=2, tag='')],
)
'''  # noqa: E501
    expected_312 = '''\
Module(
    body=[
        FunctionDef(
            lineno=1,
            col_offset=0,
            end_lineno=2,
            end_col_offset=8,
            name='f',
            args=arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
            body=[Pass(lineno=2, col_offset=4, end_lineno=2, end_col_offset=8)],
            decorator_list=[],
            returns=None,
            type_comment='() -> None',
            type_params=[],
        ),
    ],
    type_ignores=[TypeIgnore(lineno=2, tag='')],
)
'''  # noqa: E501
    expected = expected_312 if sys.version_info >= (3, 12) else expected_38
    mod = (
        'def f():  # type: () -> None\n'
        '    pass  # type: ignore\n'
    )
    f = tmpdir.join('test.py')
    f.write(mod)
    astpretty.main((f.strpath,))
    out, _ = capsys.readouterr()
    assert out == expected
