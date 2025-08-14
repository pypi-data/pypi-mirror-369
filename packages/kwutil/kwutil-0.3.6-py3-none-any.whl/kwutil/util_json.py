"""
json utilities for debugging serializability and attempting to ensure it in
some cases.
"""
import copy
import decimal
import fractions
import pathlib
import ubelt as ub
from collections import OrderedDict

try:
    import numpy as np
except ImportError:
    np = None


def debug_json_unserializable(data, msg=''):
    """
    Raises an exception if the data is not serializable and prints information
    about it. This is a thin wrapper around :func:`find_json_unserializable`.
    """
    unserializable = list(find_json_unserializable(data))
    if unserializable:
        raise Exception(msg + ub.urepr(unserializable))


def ensure_json_serializable(dict_, normalize_containers=False, verbose=0,
                             unhandled_policy='keep'):
    """
    Attempt to convert common types (e.g. numpy) into something json compliant

    Convert numpy and tuples into lists. Attempts to decode bytes as utf8, but
    will skip if this is not possible.

    Args:
        dict_ (List | Dict):
            A data structure nearly compatible with json. (todo: rename arg)

        normalize_containers (bool):
            if True, normalizes dict containers to be standard python
            structures. Defaults to False.

        unhandled_policy (str):
            What to do if there isn't a straighforward way to convert to
            a serializable structure. Can be "keep", "error" or "stringify".

    Returns:
        Dict | List:
            normalized data structure that should be entirely json
            serializable.

    Note:
        This was ported from kwcoco.util

    Example:
        >>> from kwutil.util_json import *  # NOQA
        >>> assert ensure_json_serializable([]) == []
        >>> assert ensure_json_serializable({}) == {}
        >>> data = [pathlib.Path('.')]
        >>> assert ensure_json_serializable(data) == ['.']
        >>> assert ensure_json_serializable(data) != data

    Example:
        >>> # by default non-serializable objects are kept-as-is
        >>> data = [[], {}, object(), (1, 2)]
        >>> ensure_json_serializable(data)
        >>> ensure_json_serializable(data, unhandled_policy='stringify')
        >>> #ensure_json_serializable(data, unhandled_policy='pickle')
        >>> import pytest
        >>> with pytest.raises(Exception):
        >>>     ensure_json_serializable(data, unhandled_policy='error')

    Example:
        >>> # xdoctest: +REQUIRES(module:numpy)
        >>> from kwutil.util_json import *  # NOQA
        >>> data = ub.ddict(lambda: int)
        >>> data['foo'] = ub.ddict(lambda: int)
        >>> data['bar'] = np.array([1, 2, 3])
        >>> data['foo']['a'] = 1
        >>> data['foo']['b'] = (1, np.array([1, 2, 3]), {3: np.int32(3), 4: np.float16(1.0)})
        >>> dict_ = data
        >>> print(ub.urepr(data, nl=-1))
        >>> assert list(find_json_unserializable(data))
        >>> result = ensure_json_serializable(data, normalize_containers=True)
        >>> print(ub.urepr(result, nl=-1))
        >>> assert not list(find_json_unserializable(result))
        >>> assert type(result) is dict
    """
    dict_ = copy.deepcopy(dict_)

    scalar_types = (int, float, str, type(None))
    container_types = (tuple, list, dict)
    serializable_types = scalar_types + container_types

    def _norm_container(c):
        if isinstance(c, dict):
            # Cast to a normal dictionary
            if isinstance(c, OrderedDict):
                if type(c) is not OrderedDict:
                    c = OrderedDict(c)
            else:
                if type(c) is not dict:
                    c = dict(c)
        return c

    # TODO: use the version of the walker with a parent ref for efficient
    # modifications
    walker = ub.IndexableWalker(dict_)
    for prefix, value in walker:
        if isinstance(value, tuple):
            new_value = list(value)
            walker[prefix] = new_value
        elif isinstance(value, set):
            # TODO: do we need to recurse into this set differently?
            new_value = list(value)
            walker[prefix] = new_value
        elif np is not None and isinstance(value, np.ndarray):
            new_value = value.tolist()
            walker[prefix] = new_value
        elif np is not None and isinstance(value, (np.integer)):
            new_value = int(value)
            walker[prefix] = new_value
        elif np is not None and isinstance(value, (np.floating)):
            new_value = float(value)
            walker[prefix] = new_value
        elif np is not None and isinstance(value, (np.complexfloating)):
            new_value = complex(value)
            walker[prefix] = new_value
        elif isinstance(value, bytes):
            try:
                new_value = value.decode()
            except Exception:
                ...
            else:
                walker[prefix] = new_value
        elif isinstance(value, decimal.Decimal):
            new_value = float(value)
            walker[prefix] = new_value
        elif isinstance(value, fractions.Fraction):
            new_value = float(value)
            walker[prefix] = new_value
        elif isinstance(value, pathlib.Path):
            new_value = str(value)
            walker[prefix] = new_value
        elif hasattr(value, '__json__'):
            new_value = value.__json__()
            walker[prefix] = new_value
        else:
            if normalize_containers:
                if isinstance(value, dict):
                    new_value = _norm_container(value)
                    walker[prefix] = new_value

            if unhandled_policy == 'keep':
                # do nothing
                ...
            else:
                if not isinstance(value, serializable_types):
                    if unhandled_policy == 'error':
                        raise Exception(f'Unserializable: value={value!r}')
                    elif unhandled_policy == 'stringify':
                        new_value = f'UNSERIALIZABLE: {value!r}'
                        walker[prefix] = new_value
                    # elif unhandled_policy == 'pickle':
                    #     import pickle
                    #     new_value = pickle.dumps(value)
                    #     walker[prefix] = new_value
                    else:
                        raise KeyError(unhandled_policy)

    if normalize_containers:
        # normalize the outer layer
        dict_ = _norm_container(dict_)
    return dict_


def find_json_unserializable(data, quickcheck=False):
    """
    Recurse through json datastructure and find any component that
    causes a serialization error. Record the location of these errors
    in the datastructure as we recurse through the call tree.

    Args:
        data (object): data that should be json serializable
        quickcheck (bool): if True, check the entire datastructure assuming
            its ok before doing the python-based recursive logic.

    Returns:
        List[Dict]: list of "bad part" dictionaries containing items

            'value' - the value that caused the serialization error

            'loc' - which contains a list of key/indexes that can be used
            to lookup the location of the unserializable value.
            If the "loc" is a list, then it indicates a rare case where
            a key in a dictionary is causing the serialization error.

    Note:
        This was ported from kwcoco.util

    Example:
        >>> # xdoctest: +REQUIRES(module:numpy)
        >>> from kwutil.util_json import *  # NOQA
        >>> part = ub.ddict(lambda: int)
        >>> part['foo'] = ub.ddict(lambda: int)
        >>> part['bar'] = np.array([1, 2, 3])
        >>> part['foo']['a'] = 1
        >>> # Create a dictionary with two unserializable parts
        >>> data = [1, 2, {'nest1': [2, part]}, {frozenset({'badkey'}): 3, 2: 4}]
        >>> parts = list(find_json_unserializable(data))
        >>> print('parts = {}'.format(ub.urepr(parts, nl=1)))
        >>> # Check expected structure of bad parts
        >>> assert len(parts) == 2
        >>> part = parts[1]
        >>> assert list(part['loc']) == [2, 'nest1', 1, 'bar']
        >>> # We can use the "loc" to find the bad value
        >>> for part in parts:
        >>>     # "loc" is a list of directions containing which keys/indexes
        >>>     # to traverse at each descent into the data structure.
        >>>     directions = part['loc']
        >>>     curr = data
        >>>     special_flag = False
        >>>     for key in directions:
        >>>         if isinstance(key, list):
        >>>             # special case for bad keys
        >>>             special_flag = True
        >>>             break
        >>>         else:
        >>>             # normal case for bad values
        >>>             curr = curr[key]
        >>>     if special_flag:
        >>>         assert part['data'] in curr.keys()
        >>>         assert part['data'] is key[1]
        >>>     else:
        >>>         assert part['data'] is curr

    Example:
        >>> # xdoctest: +SKIP("TODO: circular ref detect algo is wrong, fix it")
        >>> from kwutil.util_json import *  # NOQA
        >>> import pytest
        >>> # Test circular reference
        >>> data = [[], {'a': []}]
        >>> data[1]['a'].append(data)
        >>> with pytest.raises(ValueError, match="Circular reference detected at.*1, 'a', 1*"):
        ...     parts = list(find_json_unserializable(data))
        >>> # Should be ok here
        >>> shared_data = {'shared': 1}
        >>> data = [[shared_data], shared_data]
        >>> parts = list(find_json_unserializable(data))
    """
    import json
    needs_check = True

    if quickcheck:
        try:
            # Might be a more efficient way to do this check. We duplicate a lot of
            # work by doing the check for unserializable data this way.
            json.dumps(data)
        except Exception:
            # if 'Circular reference detected' in str(ex):
            #     has_circular_reference = True
            # If there is unserializable data, find out where it is.
            # is_serializable = False
            pass
        else:
            # is_serializable = True
            needs_check = False

    # FIXME: the algo is wrong, fails when
    CHECK_FOR_CIRCULAR_REFERENCES = 0

    if needs_check:
        # mode = 'new'
        # if mode == 'new':
        scalar_types = (int, float, str, type(None))
        container_types = (tuple, list, dict)
        serializable_types = scalar_types + container_types
        walker = ub.IndexableWalker(data)

        if CHECK_FOR_CIRCULAR_REFERENCES:
            seen_ids = set()

        for prefix, value in walker:

            if CHECK_FOR_CIRCULAR_REFERENCES:
                # FIXME: We need to know if this container id is in this paths
                # ancestors. It is allowed to be elsewhere in the data
                # structure (i.e. the pointer graph must be a DAG)
                if isinstance(value, container_types):
                    container_id = id(value)
                    if container_id in seen_ids:
                        circ_loc = {'loc': prefix, 'data': value}
                        raise ValueError(f'Circular reference detected at {circ_loc}')
                    seen_ids.add(container_id)

            *root, key = prefix
            if not isinstance(key, scalar_types):
                # Special case where a dict key is the error value
                # Purposely make loc non-hashable so its not confused with
                # an address. All we can know in this case is that they key
                # is at this level, there is no concept of where.
                yield {'loc': root + [['.keys', key]], 'data': key}
            elif not isinstance(value, serializable_types):
                yield {'loc': prefix, 'data': value}


class Json:
    """
    Similar to kwutil.Yaml, the Json class provides a set of helpers to make
    working with json easier.

    Example:
        >>> from kwutil.util_json import Json
        >>> import ubelt as ub
        >>> unserializable_data = {
        >>>     'a': 'hello world',
        >>>     'b': ub.udict({'a': 3}),
        >>>     'c': ub.Path('a/path/object'),
        >>> }
        >>> data = Json.ensure_serializable(unserializable_data)
        >>> text1 = Json.dumps(data, backend='stdlib')
        >>> # Coerce is idempotent and resolves the input to nested Python
        >>> # structures.
        >>> resolved1 = Json.coerce(data)
        >>> resolved2 = Json.coerce(text1)
        >>> resolved3 = Json.coerce(resolved2)
        >>> assert resolved1 == resolved2 == resolved3 == data
        >>> # with stdlib
        >>> data2 = Json.loads(text1)
        >>> assert data2 == data
        >>> # with ujson
        >>> # xdoctest: +REQUIRES(module:ujson)
        >>> data2 = Json.loads(text1, backend='ujson')
        >>> assert data2 == data
    """

    @staticmethod
    def load(file, backend='stdlib'):
        import os
        if isinstance(file, (str, os.PathLike)):
            fpath = file
            with open(fpath, 'r') as fp:
                return Json.load(fp, backend=backend)
        else:
            if backend == 'stdlib':
                import json
                data = json.load(file)
            elif backend == 'ujson':
                import ujson
                data = ujson.load(file)
            elif backend == 'orjson':
                import orjson
                with open(file, 'r') as file:
                    data = orjson.loads(file.read())
            else:
                raise NotImplementedError(backend)
            return data

    @staticmethod
    def loads(text, backend='stdlib'):
        if backend == 'stdlib':
            import json
            data = json.loads(text)
        elif backend == 'ujson':
            import ujson
            data = ujson.loads(text)
        elif backend == 'orjson':
            import orjson
            data = orjson.loads(text)
        else:
            raise NotImplementedError(backend)
        return data

    @staticmethod
    def dump(data, fp, backend='stdlib', **kwargs):
        """
        Write json data to a file with a chosen backend.

        Args:
            data (dict | list | int | float | str): json serializable data.
            fp (PathLike | IO): Where to write the data
            backend (str): stdlib, ujson, or orjson
            **kwargs : additional arguments to pass to the specific backend.
        """
        if backend == 'stdlib':
            import json
            json.dump(data, fp, **kwargs)
        elif backend == 'ujson':
            import ujson
            ujson.dump(data, fp, **kwargs)
        elif backend == 'orjson':
            import orjson
            fp.write(orjson.dumps(data, **kwargs))
        else:
            raise NotImplementedError(backend)

    @staticmethod
    def dumps(data, backend='stdlib', **kwargs):
        """
        Convert json data to text with a chosen backend.

        Args:
            data (dict | list | int | float | str): json serializable data.
            backend (str): stdlib, ujson, or orjson
            **kwargs : additional arguments to pass to the specific backend.
        """
        if backend == 'stdlib':
            import json
            text = json.dumps(data, **kwargs)
        elif backend == 'ujson':
            import ujson
            text = ujson.dumps(data, **kwargs)
        elif backend == 'orjson':
            import orjson
            text = orjson.dumps(data, **kwargs)
        else:
            raise NotImplementedError(backend)
        return text

    @classmethod
    def coerce(cls, data, backend='stdlib', path_policy='existing_file_with_extension'):
        """
        Example:
            >>> from kwutil.util_json import Json
            >>> import ubelt as ub
            >>> Json.coerce('[1, 2, 3]')
            [1, 2, 3]
            >>> fpath = ub.Path.appdir('kwutil/tests/util_json').ensuredir() / 'file.json'
            >>> fpath.write_text(Json.dumps([4, 5, 6]))
            >>> Json.coerce(fpath)
            [4, 5, 6]
            >>> Json.coerce(str(fpath))
            [4, 5, 6]
            >>> dict(Json.coerce('{"a": "b", "c": "d"}'))
            {'a': 'b', 'c': 'd'}
            >>> Json.coerce(None)
            None
        """
        import os
        if isinstance(data, os.PathLike):
            result = Json.load(data, backend=backend)
        elif isinstance(data, str):
            maybe_path = None

            if path_policy == 'never':
                ...
            else:
                if path_policy == 'existing_file':
                    path_requires_extension = False
                elif path_policy == 'existing_file_with_extension':
                    path_requires_extension = True
                else:
                    raise KeyError(path_policy)

                if '\n' not in data and len(data.strip()) > 0:
                    # Ambiguous case: might this be path-like?
                    maybe_path = ub.Path(data)
                    try:
                        if not maybe_path.is_file():
                            maybe_path = None
                    except OSError:
                        maybe_path = None

                if maybe_path and path_requires_extension:
                    # If the input looks like a path, try to load it.  This was
                    # added because I tried to coerce "auto" as a string, but
                    # for some reason there was a file "auto" in my cwd and
                    # that was confusing.
                    if '.' not in maybe_path.name:
                        maybe_path = None

            if maybe_path is not None:
                result = Json.coerce(maybe_path, backend=backend)
            else:
                result = Json.loads(data, backend=backend)
        elif hasattr(data, 'read'):
            # assume file
            result = Json.load(data, backend=backend)
        else:
            # Probably already parsed. Return the input
            result = data
        return result

    @classmethod
    def find_unserializable(cls, data, quickcheck=False):
        """
        Example:
            >>> import kwutil
            >>> import ubelt as ub
            >>> data = {
            >>>     'a': 1,
            >>>     'b': 2,
            >>>     'c': ub.Path('/pathlib/object')
            >>> }
            >>> results = list(kwutil.Json.find_unserializable(data))
            >>> print(f'results = {ub.urepr(results, nl=1)}')
            results = [
                {'loc': ['c'], 'data': Path('/pathlib/object')},
            ]
        """
        find_json_unserializable.__doc__
        return find_json_unserializable(data, quickcheck)

    @classmethod
    def ensure_serializable(cls, dict_, normalize_containers=False, verbose=0,
                            unhandled_policy='keep'):
        """
        Example:
            >>> import kwutil
            >>> import pathlib
            >>> data = {
            >>>     'a': 1,
            >>>     'b': 2,
            >>>     'c': pathlib.Path('/pathlib/object')
            >>> }
            >>> results = kwutil.Json.ensure_serializable(data)
            >>> print(f'results = {ub.urepr(results, nl=1)}')
            results = {
                'a': 1,
                'b': 2,
                'c': '/pathlib/object',
            }
        """
        ensure_json_serializable.__doc__
        return ensure_json_serializable(
            dict_, normalize_containers=normalize_containers, verbose=verbose,
            unhandled_policy=unhandled_policy)

    @classmethod
    def debug_unserializable(cls, data, msg=''):
        """
        Raises an exception if the data is not serializable and prints information
        about it. This is a thin wrapper around :func:`Json.find_unserializable`.

        Example:
            >>> import kwutil
            >>> import ubelt as ub
            >>> data = {
            >>>     'a': 1,
            >>>     'b': 2,
            >>>     'c': ub.Path('/pathlib/object')
            >>> }
            >>> try:
            >>>     kwutil.Json.debug_unserializable(data, 'obj had non-json data at: ')
            >>> except Exception as ex:
            >>>     print(f'Exception: {ex}')
            Exception: obj had non-json data at: [
                {'loc': ['c'], 'data': Path('/pathlib/object')},
            ]
        """
        unserializable = list(find_json_unserializable(data))
        if unserializable:
            raise Exception(msg + ub.urepr(unserializable))
