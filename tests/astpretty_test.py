from __future__ import absolute_import
from __future__ import unicode_literals

import ast

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


def test_pformat_node():
    ret = astpretty.pformat(_to_expr_value('x'))
    assert ret == "Name(id='x', ctx=Load())"


def test_pformat_nested():
    ret = astpretty.pformat(_to_module_body('x = 5'))
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
        "    test=Num(n=1),\n"
        '    body=[Pass()],\n'
        '    orelse=[],\n'
        ')'
    )


def test_pformat_mixed_sub_nodes_and_primitives():
    ret = astpretty.pformat(_to_module_body('from y import x'))
    assert ret == (
        'ImportFrom(\n'
        "    module='y',\n"
        "    names=[alias(name='x', asname=None)],\n"
        '    level=0,\n'
        ')'
    )


def test_pformat_nested_multiple_elements():
    ret = astpretty.pformat(_to_expr_value('[1, 2, 3]'))
    assert ret == (
        'List(\n'
        '    elts=[\n'
        '        Num(n=1),\n'
        '        Num(n=2),\n'
        '        Num(n=3),\n'
        '    ],\n'
        '    ctx=Load(),\n'
        ')'
    )


def test_pformat_custom_indent():
    ret = astpretty.pformat(_to_expr_value('[1, 2, 3]'), indent='\t')
    assert ret == (
        'List(\n'
        '\telts=[\n'
        '\t\tNum(n=1),\n'
        '\t\tNum(n=2),\n'
        '\t\tNum(n=3),\n'
        '\t],\n'
        '\tctx=Load(),\n'
        ')'
    )


def test_pprint(capsys):
    astpretty.pprint(_to_expr_value('x'))
    out, _ = capsys.readouterr()
    assert out == "Name(id='x', ctx=Load())\n"
