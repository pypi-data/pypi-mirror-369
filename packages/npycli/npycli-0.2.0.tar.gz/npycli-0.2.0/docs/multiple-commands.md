# Multiple Command Programs

Multiple command programs should use the `CLI` type as it manages multiple commands for you.

1. Create an instance of `CLI`, for this example, `cli = CLI()`.
2. Write a `Command` function, and apply the `cli.cmd()` decorator: `@cli.cmd() def func(): ...`
3. Use either `cli.prompt()` to give the user a prompt to enter a command and arguments, or use `cli.exec(entries)`
   and \
   pass in a list of arguments.

# Use return values of `Command` functions

To handle return values of `Command` functions, write a *callback* function that will be used by `cli`. The callback
function will take as arguments the `Command` and the return value.

This return value handler will simply print the command name, and print the return value if not None.

```python
@cli.retvals()
def retvals(command: Command, return_value: Optional[Any]) -> None:
    if return_value is None:
        return
    print(f'{command.name} -> {return_value}')
```  

# Handle exception raised while executing a `Command`

To handle raised exceptions, write a *callback* function that will take as arguments the `Command` the exception was
raised in, and the `Exception` itself.

This exception handler will simply print the exception, then exit.

```python
@cli.errors()
def errors(command: Command, exception: Exception) -> None:
    print(f'A {exception.__class__.__name__} error occurred executing {command.name}:\n{exception}')
```

***Note:** the `@cli.errors()` handler will not be called if an exception is thrown by `cli.prompt()` or `cli.exec()`,
only
if the exception is raised while **executing** the command.*
