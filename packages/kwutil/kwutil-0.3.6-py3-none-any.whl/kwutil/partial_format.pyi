import string


def partial_format(format_string: str, *args, **kwargs) -> str:
    ...


class _PartialFormatter(string.Formatter):

    def vformat(self, format_string, args, kwargs):
        ...


def subtemplate(*args, **kwargs) -> str:
    ...


def fsubtemplate(*args, **kwargs) -> str:
    ...
