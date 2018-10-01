[![Build Status](https://travis-ci.org/asottile/astpretty.svg?branch=master)](https://travis-ci.org/asottile/astpretty)
[![Coverage Status](https://coveralls.io/repos/github/asottile/astpretty/badge.svg?branch=master)](https://coveralls.io/github/asottile/astpretty?branch=master)

astpretty
=========

Pretty print the output of python stdlib `ast.parse`.

astpretty is intended to be a replacement for `ast.dump`.

## Installation

`pip install astpretty`


## Usage

`astpretty` provides two api functions:


### `astpretty.pprint(node, indent=FOUR_SPACE_INDENT, show_offsets=True)`

Print a representation of the ast node.

```python
>>> astpretty.pprint(ast.parse('if x == y: y += 4').body[0])
If(
    lineno=1,
    col_offset=0,
    test=Compare(
        lineno=1,
        col_offset=3,
        left=Name(lineno=1, col_offset=3, id='x', ctx=Load()),
        ops=[Eq()],
        comparators=[Name(lineno=1, col_offset=8, id='y', ctx=Load())],
    ),
    body=[
        AugAssign(
            lineno=1,
            col_offset=11,
            target=Name(lineno=1, col_offset=11, id='y', ctx=Store()),
            op=Add(),
            value=Num(lineno=1, col_offset=16, n=4),
        ),
    ],
    orelse=[],
)
```

`indent` allows control over the indentation string:

```python
>>> astpretty.pprint(ast.parse('if x == y: y += 4').body[0], indent='  ')
If(
  lineno=1,
  col_offset=0,
  test=Compare(
    lineno=1,
    col_offset=3,
    left=Name(lineno=1, col_offset=3, id='x', ctx=Load()),
    ops=[Eq()],
    comparators=[Name(lineno=1, col_offset=8, id='y', ctx=Load())],
  ),
  body=[
    AugAssign(
      lineno=1,
      col_offset=11,
      target=Name(lineno=1, col_offset=11, id='y', ctx=Store()),
      op=Add(),
      value=Num(lineno=1, col_offset=16, n=4),
    ),
  ],
  orelse=[],
)
```

`show_offsets` controls whether the output includes line / column information:

```python
>>> astpretty.pprint(ast.parse('x += 5').body[0], show_offsets=False)
AugAssign(
    target=Name(id='x', ctx=Store()),
    op=Add(),
    value=Num(n=5),
)
```

### `astpretty.pformat(node, indent=FOUR_SPACE_INDENT, show_offsets=True)`

Return a string representation of the ast node.

Arguments are identical to `astpretty.pprint`.

```python
>>> astpretty.pformat(ast.parse('if x == y: y += 4').body[0])
"If(\n    lineno=1,\n    col_offset=0,\n    test=Compare(\n        lineno=1,\n        col_offset=3,\n        left=Name(lineno=1, col_offset=3, id='x', ctx=Load()),\n        ops=[Eq()],\n        comparators=[Name(lineno=1, col_offset=8, id='y', ctx=Load())],\n    ),\n    body=[\n        AugAssign(\n            lineno=1,\n            col_offset=11,\n            target=Name(lineno=1, col_offset=11, id='y', ctx=Store()),\n            op=Add(),\n            value=Num(lineno=1, col_offset=16, n=4),\n        ),\n    ],\n    orelse=[],\n)"
```

### Comparison with stdlib `ast.dump`

```python
>>> print(ast.dump(ast.parse('if x == y: y += 4').body[0]))
If(test=Compare(left=Name(id='x', ctx=Load()), ops=[Eq()], comparators=[Name(id='y', ctx=Load())]), body=[AugAssign(target=Name(id='y', ctx=Store()), op=Add(), value=Num(n=4))], orelse=[])
```

### `typed-ast` support

`astpretty` works with [typed-ast](https://github.com/python/typed_ast)!

For usage with `typed-ast` make sure you have `typed-ast` installed, a
convenient way to do this is with the `typed` extra to `astpretty`:

```bash
pip install astpretty[typed]
```

The apis above work equally well with the return values from the `ast` modules
provided by `typed_ast`:

```pycon
>>> import astpretty
>>> from typed_ast import ast3
>>> astpretty.pprint(ast3.parse('x = 4  # type: int'))
Module(
    body=[
        Assign(
            lineno=1,
            col_offset=0,
            targets=[Name(lineno=1, col_offset=0, id='x', ctx=Store())],
            value=Num(lineno=1, col_offset=4, n=4),
            type_comment='int',
        ),
    ],
    type_ignores=[],
)
```

With `typed-ast` installed, the commandline interface adds `--typed-27` and
`--typed-3` options for using the alternative ast parsers:

```console
$ astpretty --typed-3 t.py
Module(
    body=[
        Assign(
            lineno=1,
            col_offset=0,
            targets=[Name(lineno=1, col_offset=0, id='x', ctx=Store())],
            value=Num(lineno=1, col_offset=4, n=4),
            type_comment='int',
        ),
    ],
    type_ignores=[],
)
```
