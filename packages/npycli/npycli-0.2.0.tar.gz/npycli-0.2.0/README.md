# npycli

A library to create fast and easy cli programs.

Programs contain either one or many *commands*. a command is represented by
the type `Command`.  
A program with *more than one* `Command` should use the type `CLI` which manages many things.

`Command`s can be executed by using the `()`/`__call__` operator, by passing in a `list` of arguments,
and type parsers that convert a `str` to a specific type.  
ex. `{bool: lambda s: s.strip().casefold() == 'true'.strip().casefold()}`: Converts `str` to `bool`.

`CLI` will execute a specified command when using `the CLI.exec` bound function. Pass in `entries` to the function which
is a `list` of arguments, the first being the name of a `Command`.

See more [documentation](./docs).

# See [examples](./examples):

* [Simple single command program that sums numbers](./examples/summation.py)
* [Multiple command program that uses a `dict` to manage user key-value pairs](./examples/user_items.py)
