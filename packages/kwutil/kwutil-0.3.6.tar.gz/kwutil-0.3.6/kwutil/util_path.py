"""
Helpers resulated to filesystem paths, enumeration, manipulation, and search.
"""
import os
import ubelt as ub
# Backwards compat
from ubelt.util_path import ChDir   # NOQA


def tree(path):
    """
    Like os.walk but yields a flat list of file and directory paths

    Args:
        path (str | os.PathLike)

    Yields:
        str: path

    Example:
        >>> import itertools as it
        >>> from kwutil.util_path import *  # NOQA
        >>> import ubelt as ub
        >>> path = ub.Path('.')
        >>> gen = tree(path)
        >>> results = list(it.islice(gen, 5))
        >>> print('results = {}'.format(ub.urepr(results, nl=1)))
    """
    import os
    from os.path import join
    for r, fs, ds in os.walk(path):
        for f in fs:
            yield join(r, f)
        for d in ds:
            yield join(r, d)


def coerce_patterned_paths(data, expected_extension=None, globfallback=False):
    """
    Coerce input to a list of paths.

    Args:
        data (str | List[str]):
            a glob pattern or list of glob patterns or a yaml list of glob
            patterns

        expected_extension (None | str | List[str]):
            one or more expected extensions (including the leading dot)

        globfallback (bool):
            TODO: need a better name for this. The idea is that if an input
            doesn't contain a wildcard, but does not exist (i.e.  glob wont
            match it, then return that input back as-is)

    Returns:
        List[ub.Path]: Multiple paths that match the query

    Example:
        >>> # xdoctest: +REQUIRES(module:ruamel.yaml)
        >>> empty_fpaths = coerce_patterned_paths(None)
        >>> assert len(empty_fpaths) == 0

    Example:
        >>> # xdoctest: +REQUIRES(module:ruamel.yaml)
        >>> from kwutil.util_path import *  # NOQA
        >>> import ubelt as ub
        >>> dpath = ub.Path.appdir('kwutil/test/utils/path/').ensuredir()
        >>> (dpath / 'file1.txt').touch()
        >>> (dpath / 'dir').ensuredir()
        >>> (dpath / 'dir' / 'subfile1.txt').touch()
        >>> (dpath / 'dir' / 'subfile2.txt').touch()
        >>> paths = coerce_patterned_paths(
        ...     f'''
        ...     - {dpath / 'file1.txt'}
        ...     - {dpath / 'file2.txt'}
        ...     - {dpath / 'dir'}
        ...     ''', expected_extension='.txt')
        >>> paths = [p.shrinkuser() for p in paths]
        >>> print('paths = {}'.format(ub.urepr(paths, nl=1)))
        >>> with ChDir(dpath / 'dir'):
        >>>     paths = coerce_patterned_paths('*.txt*')
        >>> print('paths = {}'.format(ub.urepr(paths, nl=1)))
        >>> assert len(paths) == 2

        paths = [
            Path('~/.cache/kwutil/test/utils/path/file1.txt'),
            Path('~/.cache/kwutil/test/utils/path/dir/subfile1.txt'),
            Path('~/.cache/kwutil/test/utils/path/dir/subfile2.txt'),
        ]
    """
    from kwutil.util_yaml import Yaml
    from ruamel.yaml.composer import ComposerError
    from os.path import isdir, join
    import glob

    if data is None:
        datas = []
    elif ub.iterable(data):
        datas = data
    else:
        datas = [data]

    # Resolve any yaml
    resolved_globs = []
    for data in datas:
        if isinstance(data, str):
            try:
                loaded = Yaml.loads(data)
            except ComposerError:
                loaded = data
            if isinstance(loaded, str):
                loaded = [loaded]
            resolved_globs.extend(loaded)
        else:
            resolved_globs.append(data)

    paths = []
    for data_ in resolved_globs:
        if data_ is None:
            continue
        if expected_extension is not None and isdir(data_):
            exts = expected_extension if ub.iterable(expected_extension) else [expected_extension]
            globpats = [join(data_, '*' + e) for e in exts]
        else:
            globpats = [data_]

        for globpat in globpats:
            # If the input has glob wildcards allow zero outputs
            globpat = os.fspath(globpat)
            globresults = list(glob.glob(globpat, recursive=True))
            if len(globresults) == 0:
                wildcard_hack = globfallback
                if wildcard_hack:
                    # But if there are no wildcards then return the path-asis
                    if '*' not in globpat and '?' not in globpat:
                        paths.append(globpat)
            else:
                paths.extend(globresults)
    paths = [ub.Path(p) for p in paths]
    return paths


def find(pattern=None, dpath=None, include=None, exclude=None, type=None,
         recursive=True, followlinks=False):
    """
    Find all paths in a root subject to a search criterion

    Args:
        pattern (str):
            The glob pattern the path name must match to be returned

        dpath (str):
            The root directory to search. Default to cwd.

        include (str | List[str]):
            Pattern or list of patterns. If specified, search only files whose
            base name matches this pattern. By default the pattern is GLOB.

        exclude (str | List[str]):
            Pattern or list of patterns. Skip any file with a name suffix that
            matches the pattern. By default the pattern is GLOB.

        type (str | List[str]):
            A list of 1 character codes indicating what types of file can be
            returned. Currently we only allow either "f" for file or "d" for
            directory. Symbolic links are not currently distinguished. In the
            future we may support posix codes, see [1]_ for details.

        recursive:
            search all subdirectories recursively

        followlinks (bool, default=False):
            if True will follow directory symlinks

    References:
        _[1] https://linuxconfig.org/identifying-file-types-in-linux

    TODO:
        mindepth

        maxdepth

        ignore_case

        regex_match


    Example:
        >>> from kwutil.util_path import *  # NOQA
        >>> paths = list(find(pattern='*'))
        >>> paths = list(find(pattern='*', type='f'))
        >>> print('paths = {!r}'.format(paths))
        >>> print('paths = {!r}'.format(paths))
    """
    from os.path import join
    from kwutil import util_pattern

    if pattern is None:
        pattern = '*'

    if type is None:
        with_dirs = True
        with_files = True
    else:
        with_dirs = False
        with_files = False
        if 'd' in type:
            with_dirs = True
        if 'f' in type:
            with_files = True

    if dpath is None:
        dpath = os.getcwd()

    include_ = (None if include is None else
                util_pattern.MultiPattern(include, hint='glob'))
    exclude_ = (None if exclude is None else
                util_pattern.MultiPattern(exclude, hint='glob'))

    main_pattern = util_pattern.Pattern.coerce(pattern, hint='glob')

    def is_included(name):
        if not main_pattern.match(name):
            return False

        if exclude_ is not None:
            if exclude_.match(name):
                return False

        if include_ is not None:
            if include_.match(name):
                return True
            else:
                return False
        return True

    for root, dnames, fnames in os.walk(dpath, followlinks=followlinks):

        if with_files:
            for fname in fnames:
                if is_included(fname):
                    yield join(root, fname)

        if with_dirs:
            for dname in dnames:
                if is_included(dname):
                    yield join(root, dname)

        if not recursive:
            break


def resolve_relative_to(path, dpath, strict=False):
    """
    Given a path, try to resolve its symlinks such that it is relative to the
    given dpath.

    Ignore:
        def _symlink(self, target, verbose=0):
            return ub.Path(ub.symlink(target, self, verbose=verbose))
        ub.Path._symlink = _symlink

        # TODO: try to enumerate all basic cases

        base = ub.Path.appdir('kwcoco/tests/reroot')
        base.delete().ensuredir()

        drive1 = (base / 'drive1').ensuredir()
        drive2 = (base / 'drive2').ensuredir()

        data_repo1 = (drive1 / 'data_repo1').ensuredir()
        cache = (data_repo1 / '.cache').ensuredir()
        real_file1 = (cache / 'real_file1').touch()

        real_bundle = (data_repo1 / 'real_bundle').ensuredir()
        real_assets = (real_bundle / 'assets').ensuredir()

        # Symlink file outside of the bundle
        link_file1 = (real_assets / 'link_file1')._symlink(real_file1)
        real_file2 = (real_assets / 'real_file2').touch()
        link_file2 = (real_assets / 'link_file2')._symlink(real_file2)


        # A symlink to the data repo
        data_repo2 = (drive1 / 'data_repo2')._symlink(data_repo1)
        data_repo3 = (drive2 / 'data_repo3')._symlink(data_repo1)
        data_repo4 = (drive2 / 'data_repo4')._symlink(data_repo2)

        # A prediction repo TODO
        pred_repo5 = (drive2 / 'pred_repo5').ensuredir()

        _ = ub.cmd(f'tree -a {base}', verbose=3)

        fpaths = []
        for r, ds, fs in os.walk(base, followlinks=True):
            for f in fs:
                if 'file' in f:
                    fpath = ub.Path(r) / f
                    fpaths.append(fpath)


        dpath = real_bundle.resolve()

        for path in fpaths:
            # print(f'{path}')
            # print(f'{path.resolve()=}')
            resolved_rel = resolve_relative_to(path, dpath)
            print('resolved_rel = {!r}'.format(resolved_rel))
    """
    try:
        resolved_abs = resolve_directory_symlinks(path)
        resolved_rel = resolved_abs.relative_to(dpath)
    except ValueError:
        if strict:
            raise
        else:
            return path
    return resolved_rel


def resolve_directory_symlinks(path):
    """
    Only resolve symlinks of directories
    """
    return path.parent.resolve() / path.name
    # prev = path
    # curr = prev.parent
    # while prev != curr:
    #     if curr.is_symlink():
    #         rhs = path.relative_to(curr)
    #         resolved_lhs = curr.resolve()
    #         new_path = resolved_lhs / rhs
    #         return new_path
    #     prev = curr
    #     curr = prev.parent
    # return path


def sidecar_glob(main_pat, sidecar_ext, main_key='main', sidecar_key=None,
                 recursive=0):
    """
    Similar to a regular glob, but returns a dictionary with associated
    main-file / sidecar-file pairs.

    TODO:
        add as a general option to Pattern.paths?

    Args:
        main_pat (str | PathLike):
            glob pattern for the main non-sidecar file

    Yields:
        Dict[str, ub.Path | None]

    Notes:
        A sidecar file is defined by the sidecar extension. We usually use this
        for .dvc sidecars.

        When the pattern includes a .dvc suffix, the result will include those .dvc
        files and any matching main files they correspond to. Note: if you search
        for paths like `foo_*.dvc` this might skipped unstaged files. Therefore it
        is recommended to only include the .dvc suffix in the pattern ONLY if you
        do not want any unstaged files.

        If you want both staged and unstaged files, ensure the pattern does not
        exclude objects without a .dvc suffix (i.e. don't end the pattern with
        .dvc).

        When the pattern does not include a .dvc suffix, we include all those
        files, for other files that exist by adding a .dvc suffix.

        With the pattern matches both a dvc and non-dvc file, they are grouped
        together.

    Example:
        >>> from kwutil.util_path import *  # NOQA
        >>> dpath = ub.Path.appdir('xdev/tests/sidecar_glob')
        >>> dpath.delete().ensuredir()
        >>> (dpath / 'file1').touch()
        >>> (dpath / 'file1.ext').touch()
        >>> (dpath / 'file1.ext.car').touch()
        >>> (dpath / 'file2.ext').touch()
        >>> (dpath / 'file3.ext.car').touch()
        >>> (dpath / 'file4.car').touch()
        >>> (dpath / 'file5').touch()
        >>> (dpath / 'file6').touch()
        >>> (dpath / 'file6.car').touch()
        >>> (dpath / 'file7.bike').touch()
        >>> def _handle_resulst(results):
        ...     results = list(results)
        ...     for row in results:
        ...         for k, v in row.items():
        ...             if v is not None:
        ...                 row[k] = v.relative_to(dpath)
        ...     print(ub.urepr(results, sv=1))
        ...     return results
        >>> main_key = 'main',
        >>> sidecar_key = '.car'
        >>> sidecar_ext = '.car'
        >>> main_pat = dpath / '*'
        >>> _handle_resulst(sidecar_glob(main_pat, sidecar_ext))
        >>> _handle_resulst(sidecar_glob(dpath / '*.ext', '.car'))
        >>> _handle_resulst(sidecar_glob(dpath / '*.car', '.car'))
        >>> _handle_resulst(sidecar_glob(dpath / 'file*.ext', '.car'))
        >>> _handle_resulst(sidecar_glob(dpath / '*', '.ext'))
    """
    from kwutil import util_pattern
    import warnings
    import os
    _len_ext = len(sidecar_ext)
    main_pat = os.fspath(main_pat)
    glob_patterns = [main_pat]
    if main_pat.endswith(sidecar_ext):
        warnings.warn(
            'The main path query should not end with the sidecar extension.'
            ' {main_pat=} {sidecar_ext=}'
        )
        # We could have a variant that removes the extension, but lets not do
        # that and document it.
        # glob_patterns.append(pat[:-_len_ext])
    else:
        if main_pat.endswith('/*'):
            # Optimization dont need an extra pattern in this case
            pass
        else:
            glob_patterns.append(main_pat + sidecar_ext)

    mpat = util_pattern.MultiPattern.coerce(glob_patterns)
    if sidecar_key is None:
        sidecar_key = sidecar_ext
    default = {main_key: None, sidecar_key: None}
    id_to_row = ub.ddict(default.copy)
    paths = mpat.paths(recursive=recursive)

    def _gen():
        for path in paths:
            parent = path.parent
            name = path.name
            if name.endswith(sidecar_ext):
                this_key = sidecar_key
                other_key = main_key
                main_path = parent / name[:-_len_ext]
                other_path = main_path
            else:
                this_key = main_key
                other_key = sidecar_key
                main_path = path
                other_path = parent / (name + sidecar_ext)
            needs_yield = main_path not in id_to_row
            row = id_to_row[main_path]
            row[this_key] = path
            if row[other_key] is None:
                if other_path.exists():
                    row[other_key] = other_path
            if needs_yield:
                yield row
    # without this, yilded rows might modify themselves later, that is
    # confusing for a user. Don't do it or come up with a scheme where we
    # detect if a row is "complete" and only yield it then
    # We could more easily do this if we used a walk-style find and pattern
    # match mechanism
    rows = list(_gen())
    yield from rows


def sanitize_path_name(path: str,
                       maxlen=128,
                       hash_suffix=None,
                       preserve_prefix: bool = True,
                       replacements=None,
                       safe=False,
                       allow_unicode: bool = True,
                       **deprecated) -> str:
    r"""
    Sanitize an input string so it can be safely used as a filename or path segment.

    This function replaces characters that are illegal on common file systems,
    strips control characters, optionally normalizes Unicode (or converts to ASCII),
    trims the length if necessary (while preserving a prefix), and ensures the name
    does not conflict with reserved names (e.g. on Windows).

    Args:
        path (str): The input file name or path segment.

        maxlen (int | None):
            Maximum allowed length for the sanitized name. If exceeded, the name
            is truncated with a hash appended. Set to None for no length limit.
            (If specified, must be at least 8.)

        hash_suffix (str | None | callable):
            An optional extra suffix to append if the name is hashed. Can be a string
            or a callable returning a string.

        preserve_prefix (bool):
            If True, preserve as much of the original sanitized name as possible
            when truncating (with an underscore plus hash appended); if False, replace
            the name entirely with the hash (and optional hash_suffix).

        replacements (dict | str |  None):
            The characters: `|<>:?*"/\` are always illegal by default.
            A mapping of substrings to replace in addition to the defaults.
            The illegal characters are always replaced, but the user can
            overwrite what they are replaced with here. If given as a string,
            all special characters are replaced with the given character.

        safe (bool):
            If True, also replaces characters that are *unsafe* but not strictly illegal.
            This includes characters problematic for shell commands, URLs, or scripts,
            i.e. ' #^&@{}[]$+;!,`~=%'.
            By default (False), only *illegal* characters are replaced.

        allow_unicode (bool):
            If True, preserves Unicode characters (using NFC normalization);
            if False, converts the name to ASCII (discarding unsupported characters).

        **deprecated :
            handles deprecated arguments

    Returns:
        str: A sanitized string that is safe for use as a filename.


    Notes:
        - **Illegal characters** are disallowed by common filesystems:
          `|`, `<`, `>`, `:`, `"`, `?`, `*`, `/`, `\`
            - These are reserved or control characters on Windows and Linux.
            - Always replaced, regardless of `safe`.

        - **Unsafe characters** are technically allowed in filenames but may cause issues:
          `#`, `&`, `@`, `^`, `{}`, `[]`, `$`, `+`, `;`, `!`, `,`, `` ` ``
            - Unsafe for use in:
                - Shell commands (e.g., `&`, `;`, `$`)
                - URLs or cloud storage (e.g., `#`, `%`, `+`)
                - Code injection or parsing bugs (e.g., `{}`, `[]`, `` ` ``)

    References:
        https://chatgpt.com/c/67aa3e3b-cf48-8013-9be6-f4ff88eecf72
        https://stackoverflow.com/questions/1976007/what-characters-are-forbidden-in-windows-and-linux-directory-names

    Examples:
        >>> from kwutil.util_path import *  # NOQA
        >>> sanitize_path_name('a chan with space_PIPE_bar_PIPE_baz')
        'a chan with space_PIPE_bar_PIPE_baz'
        >>> sanitize_path_name('dont|use<these>chars:in?a*path.')
        'dont_PIPE_use_LT_these_GT_chars_COLON_in_QM_a_ASTRIX_path._'
        >>> sanitize_path_name('dont|use<these>chars:in?a*path.', maxlen=8)
        'nckzxtpn'
        >>> sanitize_path_name('CON')
        _CON_
        >>> # Handling long names (forcing a hash):
        >>> # "abcd|efgh" becomes "abcd_efgh" (9 characters) which exceeds maxlen=8,
        >>> # so the output will be a hash (of length 8). We cannot predict the hash value,
        >>> # but we can check that the length is 8.
        >>> result = sanitize_path_name("abcd|efgh", maxlen=8)
        >>> len(result) == 8
        True
        >>> # Preserving a prefix vs. not preserving it:
        >>> # With preserve_prefix True (default) and a moderately short maxlen,
        >>> # some of the original string is kept along with an appended hash.
        >>> result = sanitize_path_name("longfilename_with_illegal|chars", maxlen=20)
        >>> "_" in result  # contains an underscore separating prefix and hash
        True
        >>> # With preserve_prefix False, the entire output is just the hash.
        >>> result2 = sanitize_path_name("longfilename_with_illegal|chars", maxlen=20, preserve_prefix=False)
        >>> "_" not in result2 or result2.count('_') == 1  # only a possible separator with hash_suffix
        True
        >>> # Unicode handling:
        >>> sanitize_path_name('café', allow_unicode=True)
        'café'
        >>> sanitize_path_name('café', allow_unicode=False)
        'cafe'
        >>> # Windows reserved names:
        >>> sanitize_path_name('CON')
        '_CON_'
        >>> sanitize_path_name('NUL')
        '_NUL_'
        >>> # Removal of control characters:
        >>> sanitize_path_name("hello\x00world")
        'helloworld'
        >>> sanitize_path_name("abc\x01def")
        'abcdef'
        >>> # Handling names ending with a dot or space:
        >>> sanitize_path_name("filename. ")
        'filename._'
        >>> # Non-string input is converted to a string:
        >>> sanitize_path_name(12345)
        '12345'
        >>> # Using a custom replacement map:
        >>> sanitize_path_name("a#b#c", replacements={"#": "X"})
        'aXbXc'
        >>> # When you specify a map, it updates the defaults
        >>> sanitize_path_name("a#b|#c", replacements={"#": "X"})
        'aXb_PIPE_Xc'
        >>> # But you can overwrite what the invalid characters map to
        >>> sanitize_path_name("a#b|#c", replacements={"#": "X", '|': 'HELLO'})
        'aXbHELLOXc'
        >>> # Use a single character to replace everything.
        >>> sanitize_path_name("a/b|<<c", replacements='_')
        'a_b___c'
        >>> # Unsafe characters are preserved by default
        >>> sanitize_path_name('report#final@v2[notes]')
        'report#final@v2[notes]'
        >>> # When safe=True, unsafe characters are also replaced
        >>> sanitize_path_name('report#final@v2[notes]', safe=True)
        'report_HASH_final_AT_v2_LSB_notes_RSB_'
        >>> # Unsafe and illegal characters can be replaced together
        >>> sanitize_path_name('a|b#c@d[e]f', safe=True)
        'a_PIPE_b_HASH_c_AT_d_LSB_e_RSB_f'
        >>> # Custom replacement mappings still apply and override defaults
        >>> sanitize_path_name('a#b|#c', safe=True, replacements={'#': 'X', '|': '-'})
        'aXb-Xc'
    """
    import re
    import unicodedata
    if not isinstance(path, str):
        path = str(path)

    if 'replacement_map' in deprecated:
        ub.schedule_deprecation(
            'kwutil', 'replacement_map', 'argument',
            migration='use replacements instead',
            deprecate='0.3.5', error='1.0.0', remove='1.1.0')
        if replacements is None:
            replacements = deprecated['replacement_map']
        else:
            raise ValueError('Cannot specify replacements and replacement_map')

    # A set of Windows-reserved filenames (case-insensitive)
    WINDOWS_RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }

    # Normalize Unicode if allowed.
    if allow_unicode:
        sanitized = unicodedata.normalize('NFC', path)
    else:
        # Convert to ASCII: decompose Unicode and remove non-ASCII parts.
        sanitized = unicodedata.normalize('NFKD', path).encode('ascii', 'ignore').decode('ascii')

    # Default replacement mapping: extend your original mapping to cover more characters.
    illegal_replacements = {
        '|': '_PIPE_',
        '<': '_LT_',
        '>': '_GT_',
        ':': '_COLON_',
        '?': '_QM_',
        '*': '_ASTRIX_',
        '"': '_DQ_',
        '/': '_FS_',
        '\\': '_BS_',
        # Add more mappings as needed.
    }

    if safe:
        unsafe_replacements = {
            ' ': '_SPACE_',
            '#': '_HASH_',
            '^': '_CARAT_',
            '&': '_AMP_',
            '@': '_AT_',
            '{': '_LCB_',     # Left Curly Brace
            '}': '_RCB_',     # Right Curly Brace
            '[': '_LSB_',     # Left Square Bracket
            ']': '_RSB_',     # Right Square Bracket
            '(': '_LP__',     # Left Square Bracket
            ')': '_RP__',     # Right Square Bracket
            '$': '_DOLLAR_',
            '+': '_PLUS_',
            ';': '_SEMI_',
            '!': '_BANG_',
            ',': '_COMMA_',
            '`': '_BTICK_',   # Backtick
            '~': '_TILDE_',
            '=': '_EQ_',
            '%': '_PERC_',
            "'": '_SQ_',
            # Add more as needed for your domain
        }
        default_replacements = ub.udict.union(illegal_replacements, unsafe_replacements)
    else:
        default_replacements = illegal_replacements

    if replacements is None:
        replacements = default_replacements
    elif isinstance(replacements, str):
        replacements = {k: replacements for k in default_replacements.keys()}
    else:
        unspecified = ub.udict(default_replacements) - replacements
        replacements = replacements | unspecified

    # Use a regex to replace all occurrences of the illegal substrings.
    pattern = re.compile('|'.join(re.escape(key) for key in replacements))
    sanitized = pattern.sub(lambda m: replacements[m.group(0)], sanitized)

    # Remove control characters (ASCII 0-31)
    sanitized = re.sub(r'[\x00-\x1f]', '', sanitized)

    # Strip leading and trailing whitespace
    sanitized = sanitized.strip()

    # Windows disallows filenames ending with a dot or space.
    if sanitized.endswith(('.', ' ')):
        sanitized += '_'

    # If the name is empty, use a default name.
    if not sanitized:
        sanitized = 'untitled'

    # Prevent conflict with Windows reserved names (case-insensitive).
    if sanitized.upper() in WINDOWS_RESERVED_NAMES:
        sanitized = f'_{sanitized}_'

    # If a maximum length is specified and exceeded, shorten the name.
    if maxlen is not None and len(sanitized) > maxlen:
        if maxlen < 8:
            raise ValueError("maxlen must be at least 8")

        # Compute a robust hash (SHA-256) from the sanitized name.
        # Choose a hash length (here, between 8 and 16 characters) based on maxlen.
        hash_length = max(8, min(16, maxlen // 4))
        hash_str = ub.hash_data(sanitized, base='abc')[:hash_length]

        # Process the optional hash_suffix.
        if hash_suffix is not None:
            if callable(hash_suffix):
                hash_suffix = hash_suffix()
            hash_suffix = str(hash_suffix)

        if preserve_prefix:
            # Reserve space for an underscore, the hash, and the optional suffix.
            extra = 1 + len(hash_str)
            if hash_suffix:
                extra += 1 + len(hash_suffix)
            prefix_length = maxlen - extra
            if prefix_length < 1:
                # Not enough space for a prefix; fall back to hash only.
                prefix = ''
                sep = ''
            else:
                prefix = sanitized[:prefix_length]
                sep = '_'
            if hash_suffix:
                new_name = f'{prefix}{sep}{hash_str}_{hash_suffix}'
            else:
                new_name = f'{prefix}{sep}{hash_str}'
        else:
            # Replace the entire name with the hash (plus optional suffix).
            new_name = f'{hash_str}_{hash_suffix}' if hash_suffix else hash_str

        sanitized = new_name

    return sanitized
