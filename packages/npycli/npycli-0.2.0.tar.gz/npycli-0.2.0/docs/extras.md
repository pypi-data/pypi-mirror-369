# Extras

## Keyword argument aliases

the `kwarg_aliasing` module provides a function decorator to give aliases to arguments.  
There is one for regular functions: `alias_kwargs`, and one for functions that would be a `Command`:
`alias_cmd_kargs`.

#### Example

`def f(a): ...`

Let's make `b`, and `c` be aliases of argument `a`:

```python
@alias_kwargs({'a': ('b', 'c')})
def f(a): ...
```