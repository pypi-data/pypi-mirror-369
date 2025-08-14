"""
This is effectively an interface to pint. These are scattered throughout
different codebases, and it might make sense to consolidate them here.

Currently we are using pint for units, we might consider other libraries that
handle units like:

    * pint
    * quantities
    * astropy
    * unyt

See [UnitTableComparison]_ for a table comparing some unit / quantity packages.

References:
    .. [UnTy17] https://github.com/yt-project/unyt/issues/17
    .. [UnTyCompare] https://unyt.readthedocs.io/en/latest/usage.html#working-with-code-that-uses-astropy-units
    .. [UnitTableComparison] https://socialcompare.com/en/comparison/python-units-quantities-packages
"""

try:
    from functools import cache
except ImportError:
    from ubelt import memoize as cache


__all__ = ['unit_registry', 'ureg']  # NOQA


@cache
def unit_registry():
    """
    A memoized unit registry

    Returns:
        pint.UnitRegistry
    """
    import pint
    ureg = pint.UnitRegistry()
    return ureg


class __module_property_definitions__:
    """
    experimental feature for handling module level properties.

    References:
        https://github.com/scientific-python/lazy-loader/issues/127
    """
    def __init__(self):
        self.names = {'ureg'}

    @property
    def ureg(self):
        return unit_registry()

__modprops__ = __module_property_definitions__()


def __getattr__(name):
    """
    Create a lazy properties for this module that gives quick access to the
    unit registry.
    """
    if name in __modprops__.names:
        return getattr(__modprops__, name)
    else:
        raise AttributeError(f'Module {__name__!r} has no attribute {name!r}')


def byte_str(num, unit='auto', precision=2):
    """
    Automatically chooses relevant unit (KB, MB, or GB) for displaying some
    number of bytes.

    Args:
        num (int): number of bytes
        unit (str): which unit to use, can be auto, B, KB, MB, GB, TB, PB, EB,
            ZB, or YB.
        precision (int): number of decimals of precision

    References:
        https://en.wikipedia.org/wiki/Orders_of_magnitude_(data)

    Returns:
        str: string representing the number of bytes with appropriate units

    Example:
        >>> import ubelt as ub
        >>> num_list = [1, 100, 1024,  1048576, 1073741824, 1099511627776]
        >>> result = ub.urepr(list(map(byte_str, num_list)), nl=0)
        >>> print(result)
        ['0.00 KB', '0.10 KB', '1.00 KB', '1.00 MB', '1.00 GB', '1.00 TB']
    """
    import ubelt as ub
    abs_num = abs(num)
    if unit == 'auto':
        if abs_num < 2.0 ** 10:
            unit = 'KB'
        elif abs_num < 2.0 ** 20:
            unit = 'KB'
        elif abs_num < 2.0 ** 30:
            unit = 'MB'
        elif abs_num < 2.0 ** 40:
            unit = 'GB'
        elif abs_num < 2.0 ** 50:
            unit = 'TB'
        elif abs_num < 2.0 ** 60:
            unit = 'PB'
        elif abs_num < 2.0 ** 70:
            unit = 'EB'
        elif abs_num < 2.0 ** 80:
            unit = 'ZB'
        else:
            unit = 'YB'
    if unit.lower().startswith('b'):
        num_unit = num
    elif unit.lower().startswith('k'):
        num_unit =  num / (2.0 ** 10)
    elif unit.lower().startswith('m'):
        num_unit =  num / (2.0 ** 20)
    elif unit.lower().startswith('g'):
        num_unit = num / (2.0 ** 30)
    elif unit.lower().startswith('t'):
        num_unit = num / (2.0 ** 40)
    elif unit.lower().startswith('p'):
        num_unit = num / (2.0 ** 50)
    elif unit.lower().startswith('e'):
        num_unit = num / (2.0 ** 60)
    elif unit.lower().startswith('z'):
        num_unit = num / (2.0 ** 70)
    elif unit.lower().startswith('y'):
        num_unit = num / (2.0 ** 80)
    else:
        raise ValueError('unknown num={!r} unit={!r}'.format(num, unit))
    return ub.urepr(num_unit, precision=precision) + ' ' + unit
