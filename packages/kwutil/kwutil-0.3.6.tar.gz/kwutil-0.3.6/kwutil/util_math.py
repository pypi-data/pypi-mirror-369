import fractions


class Rational(fractions.Fraction):
    """
    Extension of the Fraction class representing a rational number.

    Improvements are:

        * Nicer string representation
        * long and shortform json representations
        * coerce classmethod

    Example:
        >>> from kwutil.util_math import *  # NOQA
        >>> self = 3 * -(Rational(1) / 9)
        >>> print(self)
        >>> print(self.__smalljson__())
        >>> print(self.__json__())
        -0.3333333333333333
        -1/3
        {'type': 'rational', 'numerator': -1, 'denominator': 3}
    """
    def __str__(self):
        if self.denominator == 1:
            return str(self.numerator)
        else:
            return '{}'.format(self.numerator / self.denominator)
            # return '({}/{})'.format(self.numerator, self.denominator)

    def __json__(self):
        return {
            'type': 'rational',
            'numerator': self.numerator,
            'denominator': self.denominator,
        }

    def __smalljson__(self):
        return '{:d}/{:d}'.format(self.numerator, self.denominator)

    @classmethod
    def coerce(cls, data):
        """
        Example:
            >>> from kwutil.util_math import *  # NOQA
            >>> Rational.coerce(1)
            >>> Rational.coerce(1.3)
            >>> Rational.coerce('1/3')
            >>> Rational.coerce({'numerator': 1, 'denominator': 3})
        """
        if isinstance(data, dict):
            return cls.from_json(data)
        elif isinstance(data, int):
            return cls(data, 1)
        elif isinstance(data, float):
            return cls(*data.as_integer_ratio())
        elif isinstance(data, str):
            return cls(*map(int, data.split('/')))
        else:
            import sys
            if 'PIL' in sys.modules:
                from PIL.TiffImagePlugin import IFDRational
            else:
                IFDRational = None
            if IFDRational is not None and isinstance(data, IFDRational):
                return cls(data.numerator, data.denominator)
            else:
                raise TypeError(f'Unable to coerce {data} as a Rational Number')

    @classmethod
    def from_json(cls, data):
        return cls(data['numerator'], data['denominator'])

    def __repr__(self):
        return str(self)

    def __neg__(self):
        return Rational(super().__neg__())

    def __add__(self, other):
        return Rational(super().__add__(other))

    def __radd__(self, other):
        return Rational(super().__radd__(other))

    def __sub__(self, other):
        return Rational(super().__sub__(other))

    def __mul__(self, other):
        return Rational(super().__mul__(other))

    def __rmul__(self, other):
        return Rational(super().__rmul__(other))

    def __truediv__(self, other):
        return Rational(super().__truediv__(other))

    def __floordiv__(self, other):
        return Rational(super().__floordiv__(other))
