# Single Command Programs`

Single command programs are simply scripts that parse some arguments, and run a function.

# Creating a `Command`

Use the static method `Command.create` to easily create, and use `Command`s.  
**Arguments**:

* `function: Callable`: Function to invoke, and extract signature from for parsing.
* `name: Optional[str] = None`: *Gets ignored if `names` is used.*
* `names: Optional[tuple[str, ...]] = None`
* `help: Optional[str] = None`: Useful help message
* `kwarg_prefix: Optional[str] = None`: **Default:`--`**. Prefix to denote a keyword argument

# Executing a `Command`

Use bound function `Command.exec_with` or `()`/`__call__` operator.  
**Arguments:**

* `args: list[str]`
* `parsers: Optional[dict[type, Callable[[str], Any]]] = None`

# Extras

Commands generate `details`. Add your own by using bound function `Command.add_detail`.  
See *primary* name of a command by accessing property `Command.name`.  
See aliases of a command by accessing property `Command.aliases`.

If you want to modify the command of a specific function *almost* like a decorator for commands, use the `future_cmd`
function. Pass in a `function` that will later be a `Command`, then pass in a `callback` function, that will be called
back to modify a `Command` after it has been created.

To check if a function is a `Command`, use `is_cmd` function.  
To get the `Command` of a function, use `cmd` function.
