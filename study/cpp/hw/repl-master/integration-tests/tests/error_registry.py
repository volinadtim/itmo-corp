class ErrorRegistry:
    def __init__(self):
        self._errors = {}

    def register(self, what: str, message: str) -> None:
        assert what not in self._errors
        self._errors[what] = message

    def dump(self) -> None:
        print()
        print()
        title = f"Registered {len(self._errors)} error messages:"
        print(title)
        for what, message in self._errors.items():
            padded_what = what.rjust(44)
            msg_lines = message.split('\n')
            print(f"{padded_what} :: {msg_lines[0]}")
            if len(msg_lines) > 1:
                print(' ' * 48 + f"(+ {len(msg_lines)} lines truncated)")


error_registry = ErrorRegistry()
