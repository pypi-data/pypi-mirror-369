"""
Utilities for dictionaries where dots in keys represent nestings

Related Work:
    https://pypi.org/project/python-benedict/

    https://pypi.org/project/jmespath/

    https://pypi.org/project/jmespath/

    https://pypi.org/project/dotmap/

    https://pypi.org/project/glom/

    https://pypi.org/project/dpath/

    https://pypi.org/project/python-box/

    https://pypi.org/project/omegaconf/
"""
import ubelt as ub
import weakref


class DotDict(ub.UDict):
    """
    A flat dictionary representation of a nested structure.

    This provides some similar functionality to benedict

    Example:
        >>> from kwutil.util_dotdict import *  # NOQA
        >>> self = DotDict({
        >>>     'proc1.param1': 1,
        >>>     'proc1.param2': 2,
        >>>     'proc2.param1': 3,
        >>>     'proc2.param2': 4,
        >>>     'proc3.param1': 5,
        >>>     'proc3.param2': 6,
        >>>     'proc4.part1.param1': 7,
        >>>     'proc4.part1.param2': 8,
        >>>     'proc4.part2.param2': 9,
        >>> })
        >>> self.prefix_subdict('proc4', strip=True)
        {'part1.param1': 7, 'part1.param2': 8, 'part2.param2': 9}

        >>> nested = self.to_nested()
        >>> recon = DotDict.from_nested(nested)
        >>> assert nested != self
        >>> assert recon == self
    """

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The prefix tree backend allows us to efficiently query items as if
        # the flat data structure was nested.
        # FIXME: we do not invalidate the cache on mutations yet.
        # NOTE: using the trie backend is almost always slower than a loop,
        # theoretically it should be faster, but we need a better
        # implementation
        self._trie_cache = _TrieCache(self)

    @classmethod
    def from_nested(cls, data):
        """
        Construct this flat representation from a nested one

        Args:
            data (Dict):
                nested data

        Returns:
            DotDict

        Example:
            >>> data = {
            >>>     'type': 'process',
            >>>     'properties': {
            >>>         'machine': {
            >>>             'os_name': 'Linux',
            >>>             'arch': 'x86_64',
            >>>             'py_impl': 'CPython',
            >>>         }
            >>>     }
            >>> }
            >>> from kwutil.util_dotdict import DotDict
            >>> flat = DotDict.from_nested(data)
            >>> print(f'flat = {ub.urepr(flat, nl=2)}')
            flat = {
                'type': 'process',
                'properties.machine.os_name': 'Linux',
                'properties.machine.arch': 'x86_64',
                'properties.machine.py_impl': 'CPython',
            }

        Example:
            >>> # By default lists are not flattened, only contiguous nested
            >>> # dicts
            >>> data = {
            >>>     'type': 'measure',
            >>>     'results': [
            >>>         {'score': 1},
            >>>         {'score': 2},
            >>>         {'score': 3},
            >>>     ]}
            >>> from kwutil.util_dotdict import DotDict
            >>> flat = DotDict.from_nested(data)
            >>> print(f'flat = {ub.urepr(flat, nl=2)}')
            flat = {
                'type': 'measure',
                'results': [
                    {'score': 1},
                    {'score': 2},
                    {'score': 3},
                ],
            }
        """
        flat = cls()
        walker = ub.IndexableWalker(data, list_cls=tuple())
        for path, value in walker:
            if not isinstance(value, dict):
                spath = list(map(str, path))
                key = '.'.join(spath)
                flat[key] = value
        return flat

    def to_nested(self):
        """
        Converts this flat DotDict into a nested representation.  I.e. keys are
        broken using the "." separtor, with each separator becoming a new
        nesting level.

        Example:
            >>> from kwutil.util_dotdict import *  # NOQA
            >>> self = DotDict(**{
            >>>     'foo.bar.baz': 1,
            >>>     'foo.bar.biz': 1,
            >>>     'foo.spam': 1,
            >>>     'eggs.spam': 1,
            >>> })
            >>> nested = self.to_nested()
            >>> print(f'nested = {ub.urepr(nested, nl=2)}')
            nested = {
                'foo': {
                    'bar': {'baz': 1, 'biz': 1},
                    'spam': 1,
                },
                'eggs': {
                    'spam': 1,
                },
            }
        """
        auto = ub.AutoDict()
        # Note: this could be much more efficient if we build the tree
        # incrementally by splitting all keys, and then grouping based on
        # prefix, and then popping them off as we descend down the tree. This
        # would prevent repeated walking down the tree with IndexableWalker's
        # setitem.
        walker = ub.IndexableWalker(auto)
        d = self
        for k, v in d.items():
            path = k.split('.')
            walker[path] = v
        return auto.to_dict()

    def suffix_subdict(self, suffix, backend='loop'):
        """
        Retrieve all key-value pairs whose keys end with a given dot-suffix.

        Args:
            suffix (str | List[str]): one or more dot-separated suffix strings
            default: fallback if no matches found
            backend (str): 'trie' or 'loop'

        Returns:
            DotDict: subdictionary containing the suffix

        Example:
            >>> from kwutil.util_dotdict import *  # NOQA
            >>> self = DotDict({
            >>>     'a.b.c': 1,
            >>>     'x.b.c': 2,
            >>>     'z.y': 3,
            >>>     'z.c': 4,
            >>> })
            >>> self.suffix_subdict('b.c')
            {'a.b.c': 1, 'x.b.c': 2}
            >>> self.suffix_subdict('c')
            {'a.b.c': 1, 'x.b.c': 2, 'z.c': 4}

        Example:
            >>> from kwutil.util_dotdict import *  # NOQA
            >>> self = DotDict({
            >>>     'proc1.param1': 1,
            >>>     'proc2.param1': 2,
            >>>     'proc3.param2': 3,
            >>>     'proc4.part1.param1': 4,
            >>>     'proc4.part2.param2': 5,
            >>> })
            >>> new = self.suffix_subdict(['param1', 'part2.param2'])
            >>> print(f'new = {ub.urepr(new, nl=1, sort=1)}')
            new = {
                'proc1.param1': 1,
                'proc2.param1': 2,
                'proc4.part1.param1': 4,
                'proc4.part2.param2': 5,
            }
            >>> alt1 = self.suffix_subdict(['param1', 'part2.param2'], backend='loop')
            >>> # xdoctest: +REQUIRES(module:pygtrie)
            >>> alt2 = self.suffix_subdict(['param1', 'part2.param2'], backend='trie')
            >>> assert alt1 == alt2
        """
        if backend == 'loop':
            cls = self.__class__
            # Normalize to iterable
            if isinstance(suffix, (list, tuple, set)):
                exact = set(suffix)
                dot_suffixes = tuple('.' + s for s in suffix)
                matches = cls({
                    k: v for k, v in self.items()
                    if k.endswith(dot_suffixes) or k in exact
                })
            else:
                dot_suffix = '.' + suffix
                matches = cls({
                    k: v for k, v in self.items()
                    if k.endswith(dot_suffix) or k == suffix
                })
        elif backend == 'trie':
            matches = self._trie_cache.subdict_suffix(suffix)
        else:
            raise KeyError(f'Unknown backend={backend}')
        return matches

    def prefix_subdict(self, prefix, strip=False, backend='loop'):
        """
        Retrieve all key-value pairs whose keys end with a given dot-prefix.

        Args:
            prefix (str | List[str]): select a subdictionary with this prefix / prefixes.
            strip (bool):
                if True, strip the prefix. If multiple prefixes are given,
                results may be inconsistent if new keys have duplicates.
            backend (str): 'trie' or 'loop'

        Returns:
            DotDict: subdictionary containing the prefix

        Example:
            >>> from kwutil.util_dotdict import *  # NOQA
            >>> self = DotDict(**{
            >>>     'foo.bar.baz': 1,
            >>>     'foo.bar.biz': 1,
            >>>     'foo.spam': 1,
            >>>     'eggs.spam': 1,
            >>> })
            >>> self.prefix_subdict('foo', strip=True)
            {'bar.baz': 1, 'bar.biz': 1, 'spam': 1}
            >>> self.prefix_subdict('foo', strip=False)
            {'foo.bar.baz': 1, 'foo.bar.biz': 1, 'foo.spam': 1}

        Example:
            >>> from kwutil.util_dotdict import *  # NOQA
            >>> self = DotDict({
            >>>     'proc1.param1': 1,
            >>>     'proc1.param2': 2,
            >>>     'proc2.param1': 3,
            >>>     'proc3.param2': 4,
            >>>     'proc4.part1.param1': 5,
            >>>     'proc4.part2.param2': 6,
            >>> })
            >>> new = self.prefix_subdict(['proc1', 'proc4.part1'])
            >>> print(f'new = {ub.urepr(new, nl=1, sort=1)}')
            new = {
                'proc1.param1': 1,
                'proc1.param2': 2,
                'proc4.part1.param1': 5,
            }
            >>> alt1 = self.prefix_subdict(['proc1', 'proc4.part1'], backend='loop')
            >>> # xdoctest: +REQUIRES(module:pygtrie)
            >>> alt2 = self.prefix_subdict(['proc1', 'proc4.part1'], backend='trie')
            >>> assert alt1 == alt2
        """
        if backend == 'loop':
            cls = self.__class__
            if isinstance(prefix, (list, tuple, set)):
                prefixes = list(prefix)
                exact = set(prefixes)
                dot_prefixes = [(p + '.', len(p) + 1) for p in prefixes]
                # Sort by length DESC so we strip the most specific (longest) prefix
                dot_prefixes.sort(key=lambda t: t[1], reverse=True)
                out_items = []
                for k, v in self.items():
                    if k in exact:
                        if strip:
                            out_items.append(('', v))  # mirrors previous behavior
                        else:
                            out_items.append((k, v))
                        continue
                    # Check tuple-optimized startswith, but we need the length that matched
                    # so we scan our small list ordered by length.
                    for dp, n in dot_prefixes:
                        if k.startswith(dp):
                            out_items.append((k[n:], v) if strip else (k, v))
                            break
                    # else: no match; skip
                matches = cls(out_items)
            else:
                prefix_ = prefix + '.'
                n = len(prefix_)
                if strip:
                    matches = cls({
                        (k[n:] if k.startswith(prefix_) else k): v
                        for k, v in self.items()
                        if k.startswith(prefix_) or k == prefix
                    })
                else:
                    matches = cls({
                        k: v for k, v in self.items()
                        if k.startswith(prefix_) or k == prefix
                    })
        elif backend == 'trie':
            matches = self._trie_cache.subdict_prefix(prefix)
        else:
            raise KeyError(f'Unknown backend={backend}')
        return matches

    def insert_prefix(self, prefix, index=0):
        """
        Adds a prefix to all items

        Args:
            prefix (str): prefix to insert
            index (int): the depth to insert the new param

        Example:
            >>> from kwutil.util_dotdict import *  # NOQA
            >>> self = DotDict({
            >>>     'proc1.param1': 1,
            >>>     'proc2.param1': 3,
            >>>     'proc4.part2.param2': 10,
            >>> })
            >>> new = self.insert_prefix('foo', index=0)
            >>> print('new = {}'.format(ub.urepr(new, nl=1)))
            new = {
                'foo.proc1.param1': 1,
                'foo.proc2.param1': 3,
                'foo.proc4.part2.param2': 10,
            }
        """
        if index == 0:
            # Faster special case
            new = self.__class__((prefix + '.' + k, v) for k, v in self.items())
        else:
            def _generate_new_items():
                sep = '.'
                for k, v in self.items():
                    path = k.split(sep)
                    path.insert(index, prefix)
                    k2 = sep.join(path)
                    yield k2, v
            new = self.__class__(_generate_new_items())
        return new

    def query_keys(self, col):
        """
        Finds columns where one level has this key

        Example:
            >>> from kwutil.util_dotdict import *  # NOQA
            >>> self = DotDict({
            >>>     'proc1.param1': 1,
            >>>     'proc1.param2': 2,
            >>>     'proc2.param1': 3,
            >>>     'proc4.part1.param2': 8,
            >>>     'proc4.part2.param2': 9,
            >>>     'proc4.part2.param2': 10,
            >>> })
            >>> list(self.query_keys('param1'))

        Ignore:
            could use _trie_iteritems
            trie = self._prefix_trie
        """
        for key in self.keys():
            if col in set(key.split('.')):
                yield key

    # def __contains__(self, key):
    #     if super().__contains__(key):
    #         return True
    #     else:
    #         subkeys = []
    #         subkeys.extend(self._prefix_trie.values(key))
    #         return bool(subkeys)

    # def get(self, key, default=ub.NoParam):
    #     if default is ub.NoParam:
    #         return self[key]
    #     else:
    #         try:
    #             return self[key]
    #         except KeyError:
    #             return default

    # def __getitem__(self, key):
    #     try:
    #         return super().__getitem__(key)
    #     except KeyError:
    #         subkeys = []
    #         subkeys.extend(self._prefix_trie.values(key))
    #         return self.__class__([(k, self[k]) for k in subkeys])


class _TrieCache:
    """
    Helper to maintain fast nested lookup caches with prefix trees.

    Benchmarks seem to indicate that this isn't helpful.
    """
    def __init__(self, parent):
        self.parent = weakref.proxy(parent)
        self._prefix_tree = None
        self._suffix_tree = None

    def clear(self):
        self._prefix_tree = None
        self._suffix_tree = None

    @property
    def prefix_tree(self):
        if self._prefix_tree is None:
            import pygtrie
            self._prefix_tree = pygtrie.StringTrie(ub.dzip(self.parent.keys(), self.parent.keys()), separator='.')
        return self._prefix_tree

    @property
    def suffix_tree(self):
        if self._suffix_tree is None:
            import pygtrie
            reversed_keys = {
                '.'.join(reversed(k.split('.'))): k
                for k in self.parent.keys()
            }
            self._suffix_tree = pygtrie.StringTrie(reversed_keys, separator='.')
        return self._suffix_tree

    def prefix_keys(self, prefix):
        "Return keys that match this prefix"
        try:
            return self.prefix_tree.values(prefix)
        except KeyError:
            return []

    def suffix_keys(self, suffix):
        "Return keys that match this suffix"
        reversed_suffix = '.'.join(reversed(suffix.split('.')))
        try:
            return self.suffix_tree.values(reversed_suffix)
        except KeyError:
            return []

    def subdict_prefix(self, prefix, default=ub.NoParam):
        if isinstance(prefix, (list, tuple, set)):
            keys = []
            for p in prefix:
                keys.extend(self.prefix_keys(p))
        else:
            keys = self.prefix_keys(prefix)
        return self.parent.subdict(keys, default=default)

    def subdict_suffix(self, suffix, default=ub.NoParam):
        if isinstance(suffix, (list, tuple, set)):
            keys = []
            for s in suffix:
                keys.extend(self.suffix_keys(s))
        else:
            keys = self.suffix_keys(suffix)
        return self.parent.subdict(keys, default=default)


def _run_benchmark():
    import string
    import random

    size = 300
    depth = 100

    def random_dotkey(depth, chars=string.ascii_lowercase, seglen=1):
        return '.'.join(
            ''.join(random.choices(chars, k=seglen))
            for _ in range(depth)
        )

    def generate_random_dotdict(size, depth):
        """
        Generate a DotDict with random dot-path keys.
        Each key is composed of `depth` segments.

        Args:
            size (int): number of key-value pairs
            depth (int): number of dot-separated segments in keys

        Returns:
            DotDict
        """
        keys = set()
        while len(keys) < size:
            keys.add(random_dotkey(depth))
        data = {k: random.random() for k in keys}
        self = DotDict(data)
        return self

    self = generate_random_dotdict(size, depth)

    from geowatch.utils.util_dotdict import DotDict as DotDictOrig
    orig = DotDictOrig(self)

    import timerit
    ti = timerit.Timerit(1000, bestof=10, verbose=2)
    for timer in ti.reset('suffix-get-loop'):
        with timer:
            result1 = self.suffix_get('a', backend='loop')

    for timer in ti.reset('suffix-get-trie'):
        with timer:
            result2 = self.suffix_get('a', backend='trie')

    for timer in ti.reset('geowatch-suffix-get-trie'):
        with timer:
            result3 = orig.suffix_get('a', backend='trie')

    assert result2 == result1
    assert result3 == result1

    import timerit
    ti = timerit.Timerit(10000, bestof=10, verbose=2)
    for timer in ti.reset('prefix-get-loop'):
        with timer:
            result1 = self.prefix_subdict('a', backend='loop')

    for timer in ti.reset('prefix-get-trie'):
        with timer:
            result2 = self.prefix_subdict('a', backend='trie')

    for timer in ti.reset('geowatch-prefix-get-trie'):
        with timer:
            result3 = orig.prefix_subdict('a')
