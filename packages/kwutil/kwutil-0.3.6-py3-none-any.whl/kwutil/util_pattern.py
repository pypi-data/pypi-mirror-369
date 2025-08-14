"""
An encapsulation of regex and glob (and maybe other) patterns.

Note:
    This implementation is maintained in kwutil and xdev. These versions should
    be kept in sync.

    See:
        ~/code/kwutil/kwutil/util_pattern.py
        ~/code/xdev/xdev/patterns.py

TODO:
    rectify with xdev / whatever package this goes in
"""
import os
import re
import fnmatch
import ubelt as ub
import pathlib

if hasattr(re, 'Pattern'):
    RE_Pattern = re.Pattern
else:
    # sys.version_info[0:2] <= 3.6
    RE_Pattern = type(re.compile('.*'))

try:
    import parse
except ImportError:
    class FakeParseModule:
        def Parser(self, *args, **kwargs):
            raise ImportError('Unable to import parse')
    parse = FakeParseModule()


class PatternBase:
    """
    Abstract class that defines the Pattern api
    """

    def match(self, text):
        raise NotImplementedError

    def search(self, text):
        raise NotImplementedError

    def sub(self, repl, text):
        raise NotImplementedError


# # TODO: wrapper for results of re and fnmatch
# class Match(ub.NiceRepr):
#     def __init__(self, string, pos, endpos):
#         self.string = string
#         self.pos = pos
#         self.endpos = endpos
#         self.lastgroup
#         self.lastindex
#     def span(self):
#         return (self.pos, self.endpos)
#     def __nice__(self):
#         return self.string
#     def __bool__(self):
#         return True


def _maybe_expandable_glob(pat):
    """
    Determine if a string might be a expandable glob pattern by looking for
    special glob characters: *, ? and [].

    Note:
        ! is also special, but always inside of a [] bracket, so we dont need
        to check it.

    Returns:
        bool: if False then the input is 100% not an expandable glob pattern
            (although it could still be a glob pattern, but it is equivalent to
            strict matching). if True, then there are special glob characters
            in the string, but it is not guaranteed to be a valid glob pattern.
    """
    return ('*' in pat or '?' in pat or ('[' in pat and ']' in pat))


class Pattern(PatternBase, ub.NiceRepr):
    r"""
    Provides a common API to several common pattern matching syntaxes.

    A general patterns class, which can use a backend from BACKENDS

    Args:
        pattern (str | object):
            The pattern text or a precompiled backend pattern object

        backend (str):
            Code indicating what backend the pattern text should be
            interpreted with. See BACKENDS for available choices.

    Notes:
        # BACKENDS

        The glob backend uses the :mod:`fnmatch` module [fnmatch_docs]_.
        The regex backend uses the Python :mod:`re` module.
        The strict backend uses the "==" string equality testing.
        The parse backend uses the :mod:`parse` module.

    References:
        .. [fnmatch_docs] https://docs.python.org/3/library/fnmatch.html

    Example:
        >>> # The most flexible way to define a pattern is using the
        >>> # coerce method with a prefixed pattern string.
        >>> import kwutil

        >>> # Glob pattern: matches filenames ending in .jpg
        >>> pat = kwutil.Pattern.coerce('glob:*.jpg')
        >>> assert pat.match('image.jpg')
        >>> assert not pat.match('image.png')

        >>> # Regex pattern: similar logic using regular expressions
        >>> pat = kwutil.Pattern.coerce(r'regex:.*\.jpg')
        >>> assert pat.match('photo.jpg')
        >>> assert not pat.match('photo.jpeg')

        >>> # Strict pattern: exact string match
        >>> pat = kwutil.Pattern.coerce('strict:hello.jpg')
        >>> assert pat.match('hello.jpg')
        >>> assert not pat.match('hello2.jpg')

        >>> # Parse pattern: extract named groups from string
        >>> # xdoctest: +REQUIRES(module:parse)
        >>> pat = kwutil.Pattern.coerce('parse:{name}.jpg')
        >>> assert pat.match('cat.jpg').named == {'name': 'cat'}
        >>> assert pat.match('cat.png') is None


    Example:
        >>> # But you can also explicitly define the backend with a hint.
        >>> # Test Regex backend
        >>> repat = Pattern.coerce('foo.*', 'regex')
        >>> assert repat.match('foobar')
        >>> assert not repat.match('barfoo')
        >>> match = repat.search('baz-biz-foobar')
        >>> match = repat.match('baz-biz-foobar')
        >>> # Test Glob backend
        >>> globpat = Pattern.coerce('foo*', 'glob')
        >>> assert globpat.match('foobar')
        >>> assert not globpat.match('barfoo')
        >>> globpat = Pattern.coerce('[foo|bar]', 'glob')
        >>> assert not globpat.match('foo')

    Example:
        >>> # xdoctest: +REQUIRES(module:parse)
        >>> # Test parse backend
        >>> pattern1 = Pattern.coerce('A {adjective} pattern', 'parse')
        >>> result1 = pattern1.match('A cool pattern')
        >>> print(f'result1.named = {ub.urepr(result1.named, nl=1)}')
        >>> pattern2 = pattern1.to_regex()
        >>> result2 = pattern2.match('A cool pattern')
    """

    def __init__(self, pattern, backend):
        if isinstance(pattern, pathlib.Path):
            pattern = os.fspath(pattern)
        if backend == 'regex':
            if isinstance(pattern, str):
                pattern = re.compile(pattern)
        elif backend == 'parse':
            if isinstance(pattern, str):
                pattern = parse.Parser(pattern)
        self.pattern = pattern
        self.backend = backend

    def __nice__(self) -> str:
        return '{}, {}'.format(self.pattern, self.backend)

    def to_regex(self):
        """
        Returns an equivalent pattern with the regular expression backend

        Returns:
            Pattern

        Example:
            >>> globpat = Pattern.coerce('foo*', 'glob')
            >>> strictpat = Pattern.coerce('foo*', 'strict')
            >>> repat1 = strictpat.to_regex()
            >>> repat2 = globpat.to_regex()
            >>> print(f'repat1={repat1}')
            >>> print(f'repat2={repat2}')
        """
        if self.backend == 'regex':
            regex_pattern = self.pattern
        elif self.backend == 'parse':
            # regex_pattern = self.pattern._generate_expression()
            regex_pattern = self.pattern._expression
        elif self.backend == 'glob':
            regex_pattern = fnmatch.translate(self.pattern)
        elif self.backend == 'strict':
            regex_pattern = re.escape(self.pattern)
        else:
            raise AssertionError
        new = self.__class__(regex_pattern, 'regex')
        return new

    @classmethod
    def from_regex(cls, data, flags=0, multiline=False, dotall=False,
                   ignorecase=False):
        """
        Create a Pattern object with a regex backend.
        """
        if multiline:
            flags |= re.MULTILINE
        if dotall or multiline:
            flags |= re.DOTALL
        if ignorecase:
            flags |= re.IGNORECASE
        pat = re.compile(data, flags=flags)
        self = cls(pat, 'regex')
        return self

    @classmethod
    def from_glob(cls, data):
        """
        Create a Pattern object with a glob backend.
        """
        self = cls(data, 'glob')
        return self

    # map from prefixes a pattern might start with to the corresponding backend
    _prefix_mappings = {
        'glob:': 'glob',
        'strict:': 'strict',
        'exact:': 'strict',
        'regex:': 'regex',
        'parse:': 'parse',
    }

    @classmethod
    def coerce_backend(cls, data, hint='auto'):
        """
        Example:
            >>> assert Pattern.coerce_backend('foo', hint='auto')[1] == 'strict'
            >>> assert Pattern.coerce_backend('foo*', hint='auto')[1] == 'glob'
            >>> assert Pattern.coerce_backend(re.compile('foo*'), hint='auto')[1] == 'regex'
        """
        if isinstance(data, RE_Pattern):
            backend = 'regex'
        elif isinstance(data, cls) or type(data).__name__ == cls.__name__:
            backend = data.backend
        else:
            if hint == 'auto':
                for prefix, backend in cls._prefix_mappings.items():
                    if data.startswith(prefix):
                        data = data[len(prefix):]
                        hint = backend
                        return data, hint
                hint = 'glob'
                if isinstance(data, str):
                    if not _maybe_expandable_glob(data):
                        hint = 'strict'
            backend = hint
        return data, backend

    @classmethod
    def coerce(cls, data, hint='auto'):
        """
        Attempt to automatically interpret the input data with the appropriate
        pattern backend. If it cannot be determined, then fallback to the hint.

        Args:
            data (str | Pattern | PathLike):
                an input string or existing object

            hint (str):
                can be 'glob', 'regex', 'strict' or 'auto'. In 'auto' we will
                use 'glob' if the input is a string and '*' is in the pattern,
                otherwise we will use strict. Pattern inputs keep their
                existing interpretation.

        Example:
            >>> import kwutil
            >>> # Coerce assumes glob if there is a star
            >>> pat = kwutil.Pattern.coerce('foo*')
            >>> bool(pat.match('foobar'))
            True
            >>> # Otherwise it is a strict match
            >>> pat = kwutil.Pattern.coerce('foo')
            >>> bool(pat.match('foobar'))
            False

        Example:
            >>> # xdoctest: +REQUIRES(module:parse)
            >>> import kwutil
            >>> # The hint can explicitly specify the backend to use
            >>> pat1 = kwutil.Pattern.coerce('foo.*', 'glob')
            >>> pat2 = kwutil.Pattern.coerce('foo.*', 'regex')
            >>> pat3 = kwutil.Pattern.coerce('foo.{}*', 'parse')
            >>> inputs = ['spam', 'foobar', 'foo.bar', 'foo.bar*']
            >>> print([bool(pat1.match(x)) for x in inputs])
            >>> print([bool(pat2.match(x)) for x in inputs])
            >>> print([bool(pat3.match(x)) for x in inputs])
            [False, False, True, True]
            [False, True, True, True]
            [False, False, False, True]

        Example:
            >>> # The hint can explicitly specify the backend to use
            >>> import kwutil
            >>> pat = kwutil.Pattern.coerce('foo*', 'glob')
            >>> # A hint is ignored if the input data is not a string
            >>> pat2 = kwutil.Pattern.coerce(pat, 'regex')
            >>> assert pat2.backend == 'glob'

        Example:
            >>> from kwutil.util_pattern import *  # NOQA
            >>> assert Pattern.coerce('glob:*.jpg').backend == 'glob'
            >>> assert Pattern.coerce('regex:.*\\.jpg').backend == 'regex'
            >>> assert Pattern.coerce('exact:hello.jpg').backend == 'strict'
            >>> assert Pattern.coerce('strict:hello.jpg').backend == 'strict'
            >>> assert Pattern.coerce('hello*.jpg').backend == 'glob'
            >>> assert Pattern.coerce('hello.jpg').backend == 'strict'
            >>> assert Pattern.coerce('nopat:data').backend == 'strict'
            >>> assert Pattern.coerce('foo').backend == 'strict'
            >>> assert Pattern.coerce('foo*').backend == 'glob'
            >>> assert Pattern.coerce(re.compile('foo*')) .backend == 'regex'
            >>> # xdoctest: +REQUIRES(module:parse)
            >>> assert Pattern.coerce('parse:hello.jpg').backend == 'parse'
        """
        if isinstance(data, cls):
            #or type(data).__name__ == cls.__name__:
            self = data
        else:
            data, backend = cls.coerce_backend(data, hint=hint)
            self = cls(data, backend)
        return self

    def match(self, text):
        # TODO standardize return value with a Result class.
        if self.backend == 'regex':
            return self.pattern.match(text)
        elif self.backend == 'parse':
            return self.pattern.parse(text)
        elif self.backend == 'glob':
            return fnmatch.fnmatch(text, self.pattern)
        elif self.backend == 'strict':
            return self.pattern == text
        else:
            raise KeyError(self.backend)

    def search(self, text):
        if self.backend == 'regex':
            return self.pattern.search(text)
        elif self.backend == 'parse':
            return self.pattern.search(text)
        elif self.backend == 'glob':
            return fnmatch.fnmatch(text, '*{}*'.format(self.pattern))
        elif self.backend == 'strict':
            return self.pattern in text
        else:
            raise KeyError(self.backend)

    def sub(self, repl, text, count=-1):
        """
        Args:
            repl (str): text to insert in place of pattern
            text (str): text to be searched and modified
            count (int): if non-negative, the maximum number of replacements
                that will be made.
        """
        if count == 0:
            return text  # make regex conform to the API
        if self.backend == 'regex':
            return self.pattern.sub(repl, text, count=max(0, count))
        elif self.backend == 'parse':
            raise NotImplementedError
        elif self.backend == 'glob':
            raise NotImplementedError
        elif self.backend == 'strict':
            return text.replace(self.pattern, repl, count=count)
        else:
            raise KeyError(self.backend)

    def paths(self, cwd=None, recursive=False):
        """
        Find paths in the filesystem that match this pattern

        Yields:
            ub.Path
        """
        from ubelt.util_path import ChDir
        if self.backend == 'glob':
            import glob
            with ChDir(cwd):
                yield from map(ub.Path, glob.glob(
                    self.pattern, recursive=recursive))
        elif self.backend == 'strict':
            with ChDir(cwd):
                p  = ub.Path(self.pattern)
                if p.exists():
                    yield p
        else:
            raise NotImplementedError


class MultiPattern(PatternBase, ub.NiceRepr):
    """
    Groups multiple patterns together with an "any" or "all" predicate.

    Note:
        We may remove the idea of a predicate in the future and just use
        behavior that currently corresponds to the "any" predicate.

    Example:
        >>> import kwutil
        >>> pat = kwutil.MultiPattern.coerce(['aaa*', 'bbb'])
        >>> assert not pat.match('aabb')
        >>> assert pat.match('aaabb')
        >>> assert pat.match('bbb')
        >>> assert not pat.match('bbbaaa')

    Example:
        >>> dpath = ub.Path.appdir('xdev/tests/multipattern_paths').ensuredir().delete().ensuredir()
        >>> (dpath / 'file0.txt').touch()
        >>> (dpath / 'data0.dat').touch()
        >>> (dpath / 'other0.txt').touch()
        >>> ((dpath / 'dir1').ensuredir() / 'file1.txt').touch()
        >>> ((dpath / 'dir2').ensuredir() / 'file2.txt').touch()
        >>> ((dpath / 'dir2').ensuredir() / 'file3.txt').touch()
        >>> ((dpath / 'dir1').ensuredir() / 'data.dat').touch()
        >>> ((dpath / 'dir2').ensuredir() / 'data.dat').touch()
        >>> ((dpath / 'dir2').ensuredir() / 'data.dat').touch()
        >>> pat = MultiPattern.coerce(['*.txt'], 'glob')
        >>> print(list(pat.paths(cwd=dpath)))
        >>> pat = MultiPattern.coerce(['*0*', '**/*.txt'], 'glob')
        >>> print(list(pat.paths(cwd=dpath, recursive=1)))
        >>> pat = MultiPattern.coerce(['*.txt', '**/*.txt', '**/*.dat'], 'glob')
        >>> print(list(pat.paths(cwd=dpath)))
    """

    def __init__(self, patterns, predicate):
        self.predicate = predicate
        self.patterns = patterns

    def __nice__(self):
        return f'{self.predicate.__name__}({[str(p) for p in self.patterns]})'

    def __len__(self):
        """
        Example:
            >>> import kwutil
            >>> # An empty multipattern will appear falsy and never match anything
            >>> falsy_pat = kwutil.MultiPattern.coerce([])
            >>> assert not falsy_pat
            >>> assert not falsy_pat.match('')
            >>> truthy_pat = kwutil.MultiPattern.coerce('aaa*')
            >>> assert truthy_pat
        """
        return len(self.patterns)

    def matches(self, text):
        """
        Returns all valid matches to the pattern.
        """
        for p in self.patterns:
            match = p.match(text)
            if match:
                yield match

    def match(self, text):
        """
        Check if a string matches this multipattern

        Args:
            text (str): text to check matches against

        Example:
            >>> # xdoctest: +REQUIRES(module:parse)
            >>> import kwutil
            >>> self = kwutil.MultiPattern.coerce([
            >>>     kwutil.Pattern.coerce('{key1}={val1},{key2}={val2}', hint='parse')
            >>> ])
            >>> text = 'aaa=bbb,ccc=ddd'
            >>> result = self.match(text)
            >>> assert result
            >>> assert result.named['val1'] == 'bbb'
        """
        if self.predicate is any:
            # special case for any
            return next(self.matches(text), False)
        else:
            matches = (p.match(text) for p in self.patterns)
            return self.predicate(matches)

    def paths(self, cwd=None, recursive=False):
        """
        Return paths matching this multipattern
        """
        groups = (p.paths(cwd=cwd, recursive=recursive) for p in self.patterns)
        if self.predicate in {any}:  # all}:
            yield from ub.unique(ub.flatten(groups))
        elif self.predicate in {all}:  # all}:
            yield from set.intersection(*map(set, groups))
        else:
            raise NotImplementedError

    # def search(self, text):
    #     return self.predicate(p.search(text) for p in self.patterns)

    def _squeeze(self):
        if self.predicate in {any, all}:
            if len(self.patterns) == 1:
                new = self.patterns[0]
            else:
                new = self
        else:
            raise NotImplementedError
        return new

    @classmethod
    def coerce(cls, data, hint='auto', predicate='any'):
        """
        Args:
            data (str | List | Pattern | PathLike | MultiPattern)

            hint (str):
                can be 'glob', 'regex', 'strict' or 'auto'. In 'auto' we will
                use 'glob' if the input is a string and '*' is in the pattern,
                otherwise we will use strict. Pattern inputs keep their
                existing interpretation.

        Returns:
            MultiPattern

        Example:
            >>> from kwutil.util_pattern import *  # NOQA
            >>> pat = MultiPattern.coerce('foo*', 'glob')
            >>> pat2 = MultiPattern.coerce(pat, 'regex')
            >>> pat3 = MultiPattern.coerce([pat, pat], 'regex')
            >>> pat4 = MultiPattern.coerce([ub.Path('bar*'), pat], 'regex')
            >>> print('pat = {}'.format(ub.urepr(pat, nl=1)))
            >>> print('pat2 = {}'.format(ub.urepr(pat2, nl=1)))
            >>> print('pat3 = {!r}'.format(pat3))
            >>> print('pat4 = {!r}'.format(pat4))

            >>> pat00 = MultiPattern.coerce('foo', 'glob')
            >>> pat01 = MultiPattern.coerce('foo*', 'glob')
            >>> pat02 = MultiPattern.coerce('foo*', 'regex')
            >>> pat5 = MultiPattern.coerce(['foo', 'foo*', pat, pat00, pat01, pat02])
            >>> print(f'pat5={pat5}')

        Example:
            >>> # Test all acceptable input types
            >>> from kwutil.util_pattern import *  # NOQA
            >>> import itertools as it
            >>> str_pat = 'pattern*'
            >>> scalar_inputs = {
            >>>     'str': str_pat,
            >>>     'path': ub.Path(str_pat),
            >>>     'pat': Pattern.coerce(str_pat),
            >>>     'mpat': MultiPattern.coerce(str_pat)
            >>> }
            >>> # Test scalar input types
            >>> scalar_outputs = {}
            >>> for k, v in scalar_inputs.items():
            >>>     scalar_outputs[k] = MultiPattern.coerce(v)
            >>> print('scalar_outputs = {}'.format(ub.urepr(scalar_outputs, nl=1)))
            >>> #
            >>> # Test iterable input types
            >>> multi_outputs = []
            >>> for v in it.combinations(scalar_inputs.values(), 2):
            >>>     multi_outputs.append(MultiPattern.coerce(v))
            >>> for v in it.combinations(scalar_inputs.values(), 3):
            >>>     multi_outputs.append(MultiPattern.coerce(v))
            >>> # Higher order nesting test
            >>> higher_order_output = MultiPattern.coerce(multi_outputs)
            >>> print('higher_order_output = {}'.format(ub.urepr(higher_order_output, nl=1)))
        """
        if isinstance(data, cls) or type(data).__name__ == cls.__name__:
            self = data
        else:
            # coerce predicate
            if predicate == 'any':
                predicate = any
            else:
                raise NotImplementedError
            if isinstance(data, (str, os.PathLike, Pattern)):
                data, backend = Pattern.coerce_backend(data, hint=hint)
                pat = Pattern.coerce(data, backend)
                patterns = [pat]
                self = MultiPattern(patterns, predicate)
            else:
                self = MultiPattern([
                    MultiPattern.coerce(d, hint)._squeeze()
                    for d in data], predicate)
        return self
