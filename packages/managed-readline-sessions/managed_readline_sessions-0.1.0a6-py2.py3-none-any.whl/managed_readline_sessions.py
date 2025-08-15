import os.path
import sys

from typing import Callable, Iterable, List, Optional

if 'readline' in sys.modules:
    raise ImportError('readline is already imported; we cannot manage a readline session for you')

import readline as _readline

# Manually manage getting and setting tab bindings (because readline doesn't support getting tab bindings)
DEFAULT_TAB_BINDING = 'tab: self-insert'
_readline.parse_and_bind(DEFAULT_TAB_BINDING)
_current_tab_binding = DEFAULT_TAB_BINDING


def _readline_get_tab_binding():
    # type: () -> str
    """Get the current tab key binding configuration.

    Returns:
        str: The current tab binding string (e.g., 'tab: complete')
    """
    global _current_tab_binding

    return _current_tab_binding


def _readline_set_tab_binding(tab_binding):
    # type: (str) -> None
    """Set a new tab key binding configuration.

    Args:
        tab_binding (str): The new tab binding string to configure
    """
    global _current_tab_binding

    _readline.parse_and_bind(tab_binding)
    _current_tab_binding = tab_binding


# Manually manage getting and setting pre-input hooks (because readline doesn't support getting pre-input hooks)
DEFAULT_PRE_INPUT_HOOK = None
_readline.set_pre_input_hook(DEFAULT_PRE_INPUT_HOOK)
_current_pre_input_hook = DEFAULT_PRE_INPUT_HOOK


def _readline_get_pre_input_hook():
    """
    Get the current pre-input hook function registered with readline.

    Returns:
        Callable or None: The currently registered pre-input hook function, or None if no hook is set.
    """
    global _current_pre_input_hook

    return _current_pre_input_hook


def _readline_set_pre_input_hook(pre_input_hook):
    """
    Set a new pre-input hook function for readline.

    Args:
        pre_input_hook (Callable or None): The pre-input hook function to register. Pass None to clear any existing hook.
    """
    global _current_pre_input_hook

    _readline.set_pre_input_hook(pre_input_hook)
    _current_pre_input_hook = pre_input_hook


class _GetTokenCompletionsWrapper:
    __slots__ = (
        '_get_token_completions',
        '_last_line',
        '_last_token',
        '_last_index',
        '_last_completions',
    )

    def __init__(self, get_token_completions):
        # type: (Callable[[str, str, int], Iterable[str]]) -> None
        self._get_token_completions = get_token_completions  # type: Callable[[str, str, int], Iterable[str]]

        self._last_line = None  # type: Optional[str]
        self._last_token = None  # type: Optional[str]
        self._last_index = None  # type: Optional[int]
        self._last_completions = []  # type: List[str]

    def __call__(self, token, i):
        # type: (str, int) -> Optional[str]
        line = _readline.get_line_buffer()
        index = _readline.get_begidx()

        if self._last_line != line or self._last_token != token or self._last_index != index:
            self._last_line = line
            self._last_token = token
            self._last_index = index
            self._last_completions = list(self._get_token_completions(line, token, index))

        if i > len(self._last_completions):
            return None
        else:
            return self._last_completions[i]


class TabBasedTokenCompletionSession:
    """Context manager for managing readline tab-based token completion sessions.

    Provides safe installation and automatic removal of tab-based token completion functionality."""
    __slots__ = (
        '_completer',
        '_completer_delims',
        '_old_completer',
        '_old_completer_delims',
        '_old_tab_binding',
    )

    def __init__(self, get_token_completions, token_boundary_delimiters):
        # type: (Callable[[str, str, int], Iterable[str]], Iterable[str]) -> None
        """Initialize a tab-based token completion session manager.

        Args:
            get_token_completions: A callable that takes the current line, a token to complete, and its index in the current line, and returns an iterable of possible completions.
            token_boundary_delimiters: An iterable of single-character delimiters that define token boundaries. All delimiters must be single ASCII characters.

        Raises:
            ValueError: If any delimiter is not a single ASCII character.
        """
        self._completer = _GetTokenCompletionsWrapper(get_token_completions)  # type: _GetTokenCompletionsWrapper
        _completer_delim_chars = set()
        for token_boundary_delimiter in token_boundary_delimiters:
            if len(token_boundary_delimiter) == 1 and token_boundary_delimiter.isascii():
                _completer_delim_chars.add(token_boundary_delimiter)
            else:
                raise ValueError('All delimiters must be single ASCII characters.')
        self._completer_delims = ''.join(sorted(_completer_delim_chars))  # type: str

        self._old_completer = _readline.get_completer()
        self._old_completer_delims = _readline.get_completer_delims()
        self._old_tab_binding = _readline_get_tab_binding()

    def __enter__(self):
        """Set up readline completion when entering the context."""
        _readline.set_completer(self._completer)
        _readline.set_completer_delims(self._completer_delims)
        _readline_set_tab_binding('tab: complete')

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Restore previous readline state when exiting the context."""
        _readline.set_completer(self._old_completer)
        _readline.set_completer_delims(self._old_completer_delims)
        _readline_set_tab_binding(self._old_tab_binding)


class ReadWriteHistoryFileSession:
    """Context manager for readline history file operations."""
    __slots__ = (
        '_filename',
    )

    def __init__(self, filename):
        # type: (str) -> None
        """Initialize a history file session manager.

        Args:
            filename: Path to the history file to read from and write to. If the file doesn't exist, it will be created when writing.
        """
        self._filename = filename

    def __enter__(self):
        if os.path.isfile(self._filename):
            _readline.read_history_file(self._filename)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _readline.write_history_file(self._filename)


class PrefilledExampleTextSession:
    """
    Context manager to pre-fill the readline input buffer with example or template text.

    Upon entering, inserts the specified text at the prompt, allowing users to edit or accept it.
    Upon exiting, restores the previously set pre-input hook.

    Example:
        with PrefilledExampleTextSession('example command --flag '):
            user_input = input('Prompt> ')
    """
    __slots__ = (
        '_old_pre_input_hook',
        '_new_pre_input_hook'
    )

    def __init__(self, prefilled_example_text):
        """
        Initialize the session with text to pre-insert into the readline input buffer.

        Args:
            prefilled_example_text (str): The text to insert at the prompt before user input.
        """
        self._old_pre_input_hook = _readline_get_pre_input_hook()

        def _new_pre_input_hook():
            _readline.insert_text(prefilled_example_text)
            _readline.redisplay()

        self._new_pre_input_hook = _new_pre_input_hook

    def __enter__(self):
        _readline_set_pre_input_hook(self._new_pre_input_hook)

    def __exit__(self, exc_type, exc_val, exc_tb):
        _readline_set_pre_input_hook(self._old_pre_input_hook)

