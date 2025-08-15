# `managed-readline-sessions`

## The Problem

Every Python CLI tool that wants:

- Tab completion
- Command history
- Custom key bindings

...ends up writing the same fragile boilerplate that:

1. Modifies global readline state
2. Often leaks those modifications
3. Reimplements the same completion caching
4. Struggles with nested scenarios

## The Solution

```python
import os.path
import typing

from managed_readline_sessions import TabBasedTokenCompletionSession, ReadWriteHistoryFileSession, PrefilledExampleTextSession

all_commands = ['help', 'exit', 'load']


# Can return anything that is `typing.Iterable[str]`
# We will consume the iterable and cache its elements
# Every time the user initiates a tab-based token completion
# And the values passed to `line`, `token`, and `index` change
def get_token_completions(line: str, token: str, index: int) -> typing.Iterable[str]:
    # The token starts at the beginning of the line with no characters in front of it
    if index == 0:
        for command in all_commands:
            # The token is a prefix of a command
            if command.startswith(token):
                # Add a space at the end of the command such that the user moves on to enter the next token
                yield command + ' '


# Delimit tokens with spaces
token_boundary_delimiters = {' '}

with ReadWriteHistoryFileSession(os.path.join(os.path.expanduser('~'), '.myapp_history')):
    while True:
        with TabBasedTokenCompletionSession(get_token_completions, token_boundary_delimiters):    
            # Show a template each time (e.g., a frequently used command style)
            with PrefilledExampleTextSession('myapp run --input='):
                try:
                    command_line = input('myapp> ')
                    # The line will start with 'myapp run --input=' pre-inserted for the user to edit
                    # Process `command_line`...
                except EOFError:
                    break  # History saved automatically
```

Now your tool has:
- Persistent history
- Tab completion
- Clean state management
- Professional UX

All in just 10 lines of bulletproof code!

## Key Benefits

- ✓ **Guaranteed cleanup** - Never corrupt a user's shell session again  
- ✓ **Nested sessions** - Works correctly when called from other tools  
- ✓ **Performance optimized** - Smart completion caching  
- ✓ **Example-filled prompts** - Guide users with prefilled templates
- ✓ **Battle-tested** - Properly handles edge cases most implementations miss  
- ✓ **Zero dependencies** - Except `pyreadline` and `typing`, which are pure-Python
- ✓ **Compatibility** - Supports all operating systems and Python 2+

## Real-World Use Cases

1. **REPLs** - Give users tab completion without breaking their existing shell
2. **CLI tools** - Add history support that persists between runs
3. **Interactive apps** - Implement custom key bindings safely
4. **Debuggers** - Offer completion without interfering with parent process

## Installation

```bash
pip install managed-readline-sessions
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
