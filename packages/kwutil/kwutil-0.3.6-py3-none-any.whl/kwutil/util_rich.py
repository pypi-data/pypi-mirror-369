"""
Helpers for using the optional rich dependency
"""
try:
    from functools import cache
except ImportError:
    from ubelt import memoize as cache


@cache
def _tryimport_rich():
    try:
        import rich
    except ImportError:
        rich = None
    return rich


# @functools.cache
@cache
def _get_rich_print():
    rich = _tryimport_rich()
    if rich is None:
        return print
    else:
        return rich.print


def rich_print(*args, **kwargs):
    """
    Does a rich print if available, otherwise fallback to regular print
    """
    print_func = _get_rich_print()
    print_func(*args, **kwargs)
