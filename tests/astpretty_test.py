from __future__ import absolute_import
from __future__ import unicode_literals

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


@pytest.mark.xfail(sys.version_info < (3, 5), reason='py35+ syntax only')
def test_pformat_py35_regression():
    expected = (
        'Dict(\n'
        '    lineno=1,\n'
        '    col_offset=0,\n'
        '    keys=[\n'
        '        Num(lineno=1, col_offset=1, n=1),\n'
        '        None,\n'
        '    ],\n'
        '    values=[\n'
        '        Num(lineno=1, col_offset=4, n=2),\n'
        "        Name(lineno=1, col_offset=9, id='k', ctx=Load()),\n"
        '    ],\n'
        ')'
    )
    assert astpretty.pformat(_to_expr_value('{1: 2, **k}')) == expected


def test_pformat_node():
    ret = astpretty.pformat(_to_expr_value('x'))
    assert ret == "Name(lineno=1, col_offset=0, id='x', ctx=Load())"


def test_pformat_nested():
    ret = astpretty.pformat(_to_module_body('x = 5'))
    assert ret == (
        'Assign(\n'
        '    lineno=1,\n'
        '    col_offset=0,\n'
        "    targets=[Name(lineno=1, col_offset=0, id='x', ctx=Store())],\n"
        '    value=Num(lineno=1, col_offset=4, n=5),\n'
        ')'
    )


def test_pformat_nested_no_offsets():
    ret = astpretty.pformat(_to_module_body('x = 5'), show_offsets=False)
    assert ret == (
        'Assign(\n'
        "    targets=[Name(id='x', ctx=Store())],\n"
        '    value=Num(n=5),\n'
        ')'
    )


def test_pformat_nested_attr_empty_list():
    ret = astpretty.pformat(_to_module_body('if 1: pass'))
    assert ret == (
        'If(\n'
        '    lineno=1,\n'
        '    col_offset=0,\n'
        '    test=Num(lineno=1, col_offset=3, n=1),\n'
        '    body=[Pass(lineno=1, col_offset=6)],\n'
        '    orelse=[],\n'
        ')'
    )


def test_pformat_mixed_sub_nodes_and_primitives():
    ret = astpretty.pformat(_to_module_body('from y import x'))
    assert ret == (
        'ImportFrom(\n'
        '    lineno=1,\n'
        '    col_offset=0,\n'
        "    module='y',\n"
        "    names=[alias(name='x', asname=None)],\n"
        '    level=0,\n'
        ')'
    )


def test_pformat_nested_multiple_elements():
    ret = astpretty.pformat(_to_expr_value('[1, 2, 3]'))
    assert ret == (
        'List(\n'
        '    lineno=1,\n'
        '    col_offset=0,\n'
        '    elts=[\n'
        '        Num(lineno=1, col_offset=1, n=1),\n'
        '        Num(lineno=1, col_offset=4, n=2),\n'
        '        Num(lineno=1, col_offset=7, n=3),\n'
        '    ],\n'
        '    ctx=Load(),\n'
        ')'
    )


def test_pformat_custom_indent():
    ret = astpretty.pformat(_to_expr_value('[1, 2, 3]'), indent='\t')
    assert ret == (
        'List(\n'
        '\tlineno=1,\n'
        '\tcol_offset=0,\n'
        '\telts=[\n'
        '\t\tNum(lineno=1, col_offset=1, n=1),\n'
        '\t\tNum(lineno=1, col_offset=4, n=2),\n'
        '\t\tNum(lineno=1, col_offset=7, n=3),\n'
        '\t],\n'
        '\tctx=Load(),\n'
        ')'
    )


def test_pformat_nested_node_without_line_information():
    ret = astpretty.pformat(_to_expr_value('a[0]'))
    assert ret == (
        'Subscript(\n'
        '    lineno=1,\n'
        '    col_offset=0,\n'
        "    value=Name(lineno=1, col_offset=0, id='a', ctx=Load()),\n"
        '    slice=Index(\n'
        '        value=Num(lineno=1, col_offset=2, n=0),\n'
        '    ),\n'
        '    ctx=Load(),\n'
        ')'
    )


def test_pformat_leaf_node_with_list():
    ret = astpretty.pformat(_to_module_body('global x, y'))
    assert ret == "Global(lineno=1, col_offset=0, names=['x', 'y'])"


def test_pprint(capsys):
    astpretty.pprint(_to_expr_value('x'))
    out, _ = capsys.readouterr()
    assert out == "Name(lineno=1, col_offset=0, id='x', ctx=Load())\n"


def test_main(capsys, tmpdir):
    f = tmpdir.join('test.py')
    f.write('x = 5\n')
    astpretty.main((f.strpath,))
    out, _ = capsys.readouterr()
    assert out == '''\
Module(
    body=[
        Assign(
            lineno=1,
            col_offset=0,
            targets=[Name(lineno=1, col_offset=0, id='x', ctx=Store())],
            value=Num(lineno=1, col_offset=4, n=5),
        ),
    ],
)
'''


def test_main_hide_offsets(capsys, tmpdir):
    f = tmpdir.join('test.py')
    f.write('x = 5\n')
    astpretty.main((f.strpath, '--no-show-offsets'))
    out, _ = capsys.readouterr()
    assert out == '''\
Module(
    body=[
        Assign(
            targets=[Name(id='x', ctx=Store())],
            value=Num(n=5),
        ),
    ],
)
'''


def test_typedast_support():
    assert (sys.version_info >= (3,)) == astpretty.typed_support


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


@pytest.mark.xfail(not astpretty.typed_support, reason='needs typed-ast')
def test_typedast_support_27():
    expected = TYPED27_OUT.rstrip()
    assert astpretty.pformat(astpretty.ast27.parse(TYPED_SRC)) == expected


@pytest.mark.xfail(not astpretty.typed_support, reason='needs typed-ast')
def test_typedast_support_3():
    expected = TYPED3_OUT.rstrip()
    assert astpretty.pformat(astpretty.ast3.parse(TYPED_SRC)) == expected


@pytest.mark.xfail(not astpretty.typed_support, reason='needs typed-ast')
def test_typedast_ast27_arguments():
    expected = FUNC_SRC_TYPED27_OUT.strip()
    assert astpretty.pformat(astpretty.ast27.parse(FUNC_SRC)) == expected


@pytest.mark.xfail(not astpretty.typed_support, reason='needs typed-ast')
def test_typedast_support_cmdline_27(tmpdir, capsys):  # pragma: no cover
    f = tmpdir.join('f.py')
    f.write(TYPED_SRC)
    assert not astpretty.main((str(f), '--typed-27'))
    out, _ = capsys.readouterr()
    assert out == TYPED27_OUT


@pytest.mark.xfail(not astpretty.typed_support, reason='needs typed-ast')
def test_typedast_support_cmdline_3(tmpdir, capsys):  # pragma: no cover
    f = tmpdir.join('f.py')
    f.write(TYPED_SRC)
    assert not astpretty.main((str(f), '--typed-3'))
    out, _ = capsys.readouterr()
    assert out == TYPED3_OUT
