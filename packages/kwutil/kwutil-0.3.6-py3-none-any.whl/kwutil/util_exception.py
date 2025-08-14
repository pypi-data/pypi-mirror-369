"""
Helpers related to exceptions
"""


def add_exception_note(ex, note, force_legacy=False):
    """
    Add unstructured information to an exception.

    If PEP 678 is available (i.e. on Python >= 3.11), use it, otherwise create
    a new exception based on the old one with an updated note.

    Args:
        ex (BaseException): the exception to modify
        note (str): extra information to append to the exception
        force_legacy (bool): for testing

    Returns:
        BaseException: modified exception

    Typical usage should look like:

    .. code:: python

        try:
            assert False, 'something happened'
        except Exception as ex:
            from kwutil import util_exception
            raise util_exception.add_exception_note(ex, 'extra notes')

    Example:
        >>> from kwutil.util_exception import add_exception_note
        >>> ex = Exception('foo')
        >>> new_ex = add_exception_note(ex, 'hello world', force_legacy=False)
        >>> print(new_ex)
        >>> new_ex = add_exception_note(ex, 'hello world', force_legacy=True)
        >>> print(new_ex)
    """
    if not force_legacy and hasattr(ex, 'add_note'):
        # Requires python.311 PEP 678
        ex.add_note(note)  # type: ignore
        return ex
    else:
        return type(ex)(f'{ex}\n{note}')
