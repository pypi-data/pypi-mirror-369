"""
Filesystem Operation Managers

This module defines:

* :class:`CopyManager`

* :class:`MoveManager`

* :class:`DeleteManager`

which can perform their respective operations using multiple threads / workers.

TODO:
    - [ ] In CopyManager and MoveManager add option to check that no files are
          written to the same logical location (ignore symlink physical
          location problems, which would require a more expensive check).
"""
import ubelt as ub


class _FilesystemOperationManager:
    """
    Abstract class for shared components of Copy / Move / Delete manager.

    Each of these managerw will have a queue of unsubmitted jobs that haven't
    started to be worked on. They will also have a pool where they can submit
    jobs. Lastly, they will all have an eager or non-eager mode where in eager
    mode they will start a job as soon as they get it (i.e. there will be no
    unsubmitted jobs), but in non-eager mode, the develoepr will have to
    explicitly call run.
    """
    _worker_func = NotImplemented
    _operation_name = NotImplemented

    def __init__(self, workers=0, mode='thread', eager=False):
        self._pool = ub.JobPool(mode=mode, max_workers=workers)
        self.eager = eager
        self._unsubmitted = []

    def __enter__(self):
        self._pool.__enter__()
        return self

    def __len__(self) -> int:
        return len(self._unsubmitted) + len(self._pool)

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """
        Args:
            ex_type (Type[BaseException] | None):
            ex_value (BaseException | None):
            ex_traceback (TracebackType | None):

        Returns:
            bool | None
        """
        return self._pool.__exit__(ex_type, ex_value, ex_traceback)

    # def submit(self):
    #     raise NotImplementedError

    def run(self, desc=None, verbose=1, pman=None):
        """
        Args:
            desc (str | None): description for progress bars
            verbsoe (int): verbosity level
        """
        from kwutil import util_progress
        _our_pman = None

        if pman is None:
            pman = _our_pman = util_progress.ProgressManager(
                backend='progiter')
            _our_pman.__enter__()

        if verbose:
            print(f'Run {self.__class__._operation_name}')

        _worker_func = self.__class__._worker_func
        try:
            for task in self._unsubmitted:
                self._pool.submit(_worker_func, **task)
            self._unsubmitted.clear()
            job_iter = self._pool.as_completed()
            desc = desc or self.__class__._operation_name
            prog = pman.progiter(
                job_iter, desc=desc, total=len(self._pool), verbose=verbose)
            for job in prog:
                job.result()
        except Exception as ex:
            if _our_pman is not None:
                _our_pman.__exit__(ex, type(ex), None)
            raise
        finally:
            if _our_pman is not None:
                _our_pman.__exit__(None, None, None)


def _copy_worker(src, dst, skip_existing, overwrite, follow_file_symlinks, follow_dir_symlinks, meta):
    """
    Args:
        str (PathLike | str):
        dst (PathLike | str):
        overwrite (bool):
        skip_existing (bool):
    """
    src = ub.Path(src)
    dst = ub.Path(dst)
    if not skip_existing or not dst.exists():
        dst.parent.ensuredir()
        src.copy(dst, overwrite=overwrite,
                 follow_file_symlinks=follow_file_symlinks,
                 follow_dir_symlinks=follow_dir_symlinks, meta=meta)


def _move_worker(src, dst, follow_file_symlinks, follow_dir_symlinks, meta):
    """
    Args:
        str (PathLike | str):
        dst (PathLike | str):
    """
    src = ub.Path(src)
    dst = ub.Path(dst)
    dst.parent.ensuredir()
    src.move(dst, follow_file_symlinks=follow_file_symlinks,
             follow_dir_symlinks=follow_dir_symlinks, meta=meta)


class DeleteManager(_FilesystemOperationManager):
    """
    Helper to execute multiple delete operations on a local filesystem.

    Note:
        The topic of deleting a lot of files quickly is interesting.
        See: https://unix.stackexchange.com/questions/37329/efficiently-delete-large-directory-containing-thousands-of-files

    Example:
        >>> import ubelt as ub
        >>> from kwutil.fsops_managers import DeleteManager
        >>> dpath = ub.Path.appdir('kwutil', 'tests', 'delete_manager')
        >>> src_dpath = (dpath / 'src').ensuredir()
        >>> src_fpaths = [src_dpath / 'file{}.txt'.format(i) for i in range(10)]
        >>> for fpath in src_fpaths:
        >>>     fpath.touch()
        >>> deleteman = DeleteManager(workers=0, eager=False)
        >>> for fpath in src_fpaths:
        >>>     deleteman.submit(fpath)
        >>> assert len(src_dpath.ls()) == 10
        >>> deleteman.run()
        >>> assert len(src_dpath.ls()) == 0
    """
    _worker_func = ub.delete
    _operation_name = 'delete'

    def __init__(self, workers=0, mode='thread', eager=False,
                 overwrite=False, skip_existing=False):
        """
        Args:
            workers (int): number of parallel workers to use

            mode (str): thread, process, or serial

            eager (bool):
                if True starts copying as soon as a job is submitted, otherwise it
                wait until run is called.

            overwrite (bool):
                if True will overwrite the file if it exists, otherwise it will
                error unless skip_existing is True. Defaults to False.

            skip_existing (bool):
                if jobs where the destination already exists should be skipped by
                default. Default=False
        """
        super().__init__(workers=workers, mode=mode, eager=eager)
        self.skip_existing = skip_existing
        self.overwrite = overwrite

    def submit_many(self, paths):
        # Do we want to just do a type check on the submit method?
        for p in paths:
            self.submit(p)

    def submit(self, path):
        """
        Args:
            path (str | PathLike): path to delete
        """
        task = {
            'path': path,
        }
        if self.eager:
            self._pool.submit(ub.delete, **task)
        else:
            self._unsubmitted.append(task)


class CopyManager(_FilesystemOperationManager):
    """
    Helper to execute multiple copy operations on a local filesystem.

    Notes:
        It would be nice for this to support an rsync backend that could sync
        at the src/dst pair level. Not sure if this works.

    References:
        https://unix.stackexchange.com/questions/133995/rsyncing-multiple-src-dest-pairs
        https://serverfault.com/questions/163859/using-rsync-as-a-queue
        https://unix.stackexchange.com/questions/602606/rsync-source-list-to-destination-list

    TODO:
        - [ ] Add optional check that all src paths exist
        - [ ] Add optional check that all dst paths do not exist (unless overwrite=True or skip_existing=True)
        - [ ] Add optional check that that no dst path is or is inside of a src
              dpath (would make things ambiguous), the operation graph should be
              bipartite.
        - [ ] Add backend that uses a fast protocol like rsync (or write one in Rust)

    Example:
        >>> import ubelt as ub
        >>> from kwutil.fsops_managers import CopyManager
        >>> dpath = ub.Path.appdir('kwutil', 'tests', 'copy_manager')
        >>> src_dpath = (dpath / 'src').ensuredir()
        >>> dst_dpath = (dpath / 'dst').delete()
        >>> src_fpaths = [src_dpath / 'file{}.txt'.format(i) for i in range(10)]
        >>> for fpath in src_fpaths:
        >>>     fpath.touch()
        >>> # To use a copy manager, iterate through your source and
        >>> # destination paths and submit them.
        >>> copyman = CopyManager(workers=0)
        >>> # by default it will do nothing
        >>> # unless you specify eager=True or explicitly call run.
        >>> for fpath in src_fpaths:
        >>>     dst = fpath.augment(dpath=dst_dpath)
        >>>     copyman.submit(fpath, dst)
        >>> report = copyman.report()
        >>> print(f'report = {ub.urepr(report, nl=1)}')
        >>> copyman.run()

    Example:
        >>> import ubelt as ub
        >>> from kwutil.fsops_managers import CopyManager
        >>> dpath = ub.Path.appdir('kwutil', 'tests', 'copy_manager')
        >>> src_dpath = (dpath / 'src').ensuredir()
        >>> dst_dpath = (dpath / 'dst').delete()
        >>> src_fpaths = [src_dpath / 'file{}.txt'.format(i) for i in range(10)]
        >>> for fpath in src_fpaths:
        >>>     fpath.touch()
        >>> copyman = CopyManager(workers=0)
        >>> for fpath in src_fpaths:
        >>>     dst = fpath.augment(dpath=dst_dpath)
        >>>     copyman.submit(fpath, dst)
        >>> copyman.run()
        >>> assert len(dst_dpath.ls()) == len(src_dpath.ls())
        >>> copyman = CopyManager(workers=0)
        >>> for fpath in src_fpaths:
        >>>     dst = fpath.augment(dpath=dst_dpath)
        >>>     copyman.submit(fpath, dst)
        >>> import pytest
        >>> with pytest.raises(FileExistsError):
        >>>     copyman.run()
        >>> copyman = CopyManager(workers=0)
        >>> for fpath in src_fpaths:
        >>>     dst = fpath.augment(dpath=dst_dpath)
        >>>     copyman.submit(fpath, dst, skip_existing=True)
        >>> copyman.run()
    """
    _worker_func = _copy_worker
    _operation_name = 'copy'

    def __init__(self, workers=0, mode='thread', eager=False,
                 overwrite=False, skip_existing=False):
        """
        Args:
            workers (int): number of parallel workers to use

            mode (str): thread, process, or serial

            eager (bool):
                if True starts copying as soon as a job is submitted, otherwise it
                wait until run is called.

            overwrite (bool):
                if True will overwrite the file if it exists, otherwise it will
                error unless skip_existing is True. Defaults to False.

            skip_existing (bool):
                if jobs where the destination already exists should be skipped by
                default. Default=False
        """
        super().__init__(workers=workers, mode=mode, eager=eager)
        self.skip_existing = skip_existing
        self.overwrite = overwrite

    def submit(self, src, dst, skip_existing=False, overwrite=None,
               follow_file_symlinks=False, follow_dir_symlinks=False,
               meta='stats'):
        """
        Args:
            src (str | PathLike): source file or directory

            dst (str | PathLike): destination file or directory

            skip_existing (bool | None):
                if jobs where the destination already exists should be skipped by
                default. If None, then uses the class default. Default=None

            overwrite (bool | None):
                if True will overwrite the file if it exists, otherwise it will
                error unless skip_existing is True. If None, then uses the
                class default. Default=None.

            follow_file_symlinks (bool):
                If True and src is a link, the link will be resolved before
                it is copied (i.e. the data is duplicated), otherwise just
                the link itself will be copied.

            follow_dir_symlinks (bool):
                if True when src is a directory and contains symlinks to
                other directories, the contents of the linked data are
                copied, otherwise when False only the link itself is
                copied.

            meta (str | None):
                Indicates what metadata bits to copy. This can be 'stats' which
                tries to copy all metadata (i.e. like :py:func:`shutil.copy2`),
                'mode' which copies just the permission bits (i.e. like
                :py:func:`shutil.copy`), or None, which ignores all metadata
                (i.e.  like :py:func:`shutil.copyfile`).
        """
        if skip_existing is None:
            skip_existing = self.skip_existing
        if overwrite is None:
            overwrite = self.overwrite
        task = {
            'src': src,
            'dst': dst,
            'skip_existing': skip_existing,
            'overwrite': overwrite,
            'follow_file_symlinks': follow_file_symlinks,
            'follow_dir_symlinks': follow_dir_symlinks,
            'meta': meta,
        }
        if self.eager:
            self._pool.submit(_copy_worker, **task)
        else:
            self._unsubmitted.append(task)

    def report(self):
        report = self._unsubmitted_report()
        return report

    def _unsubmitted_report(self):
        """
        Build a report on the unsubmitted jobs.
        """
        from collections import Counter
        from os.path import commonprefix

        stats = Counter({
            'skips': 0,
            'overwrites': 0,
            'num_tasks': len(self._unsubmitted),
        })
        src_stat_accum = Counter()
        dst_stat_accum = Counter()

        src_paths = [task['src'] for task in self._unsubmitted]
        dst_paths = [task['dst'] for task in self._unsubmitted]

        meta = {}

        duplicate_src_paths = ub.find_duplicates(src_paths)
        duplicate_dst_paths = ub.find_duplicates(dst_paths)

        meta['common_src_prefix'] = commonprefix(src_paths)
        meta['common_dst_prefix'] = commonprefix(dst_paths)
        stats['duplicate_src_paths'] = len(duplicate_src_paths)
        stats['duplicate_dst_paths'] = len(duplicate_dst_paths)

        if 0:
            records = []
            prog = ub.ProgIter(self._unsubmitted, desc='build report')
            for task in prog:
                dst_exists = task['dst'].exists()
                src_stat = _pathinfo(task['src'])
                dst_stat = _pathinfo(task['dst'])
                src_stat_accum.update(src_stat['stats'])
                dst_stat_accum.update(dst_stat['stats'])

                if dst_exists:
                    if task['skip_existing']:
                        stats['skips'] += 1
                    elif task['overwrite']:
                        stats['overwrites'] += 1

                records.append({
                    'src_stat': src_stat,
                    'dst_stat': dst_stat,
                    'task': task
                })

        report = {**meta, **stats}
        return report


class MoveManager(_FilesystemOperationManager):
    """
    Helper to execute multiple move operations on a local filesystem.

    TODO:
        - [ ] Add optional check that all src paths exist
        - [ ] Add optional check that all dst paths do not exist
        - [ ] Add optional check that that no dst path is or is inside of a src
              dpath (would make things ambiguous), the operation graph should be
              bipartite.

    Example:
        >>> import ubelt as ub
        >>> from kwutil.fsops_managers import MoveManager
        >>> dpath = ub.Path.appdir('kwutil', 'tests', 'move_manager')
        >>> src_dpath = (dpath / 'src').ensuredir()
        >>> dst_dpath = (dpath / 'dst').delete()
        >>> src_fpaths = [src_dpath / 'file{}.txt'.format(i) for i in range(10)]
        >>> for fpath in src_fpaths:
        >>>     fpath.touch()
        >>> moveman = MoveManager(workers=0)
        >>> for src_fpath in src_fpaths:
        >>>     dst_fpath = src_fpath.augment(dpath=dst_dpath)
        >>>     moveman.submit(src_fpath, dst_fpath)
        >>> moveman.run()
        >>> assert len(dst_dpath.ls()) == len(src_fpaths)
        >>> assert len(src_dpath.ls()) == 0
    """
    _worker_func = _move_worker
    _operation_name = 'move'

    def __init__(self, workers=0, mode='thread', eager=False):
        """
        Args:
            workers (int): number of parallel workers to use

            mode (str): thread, process, or serial

            eager (bool):
                if True starts copying as soon as a job is submitted, otherwise it
                wait until run is called.
        """
        super().__init__(workers=workers, mode=mode, eager=eager)

    def submit(self, src, dst, skip_existing=False, follow_file_symlinks=False,
               follow_dir_symlinks=False, meta='stats'):
        """
        Args:
            src (str | PathLike): source file or directory

            dst (str | PathLike): destination file or directory

            follow_file_symlinks (bool):
                If True and src is a link, the link will be resolved before
                it is copied (i.e. the data is duplicated), otherwise just
                the link itself will be copied.

            follow_dir_symlinks (bool):
                if True when src is a directory and contains symlinks to
                other directories, the contents of the linked data are
                copied, otherwise when False only the link itself is
                copied.

            meta (str | None):
                Indicates what metadata bits to copy. This can be 'stats' which
                tries to copy all metadata (i.e. like :py:func:`shutil.copy2`),
                'mode' which copies just the permission bits (i.e. like
                :py:func:`shutil.copy`), or None, which ignores all metadata
                (i.e.  like :py:func:`shutil.copyfile`).
        """
        task = {
            'src': src,
            'dst': dst,
            'follow_file_symlinks': follow_file_symlinks,
            'follow_dir_symlinks': follow_dir_symlinks,
            'meta': meta,
        }
        if self.eager:
            self._pool.submit(_move_worker, **task)
        else:
            self._unsubmitted.append(task)

    def _check(self):
        """
        Validate that the set of move tasks looks sane.

        Exact logic of this is currently in flux.
        """
        tasks = self._unsubmitted
        paths = [task['src'] for task in tasks]
        dst_paths = [task['dst'] for task in tasks]
        dupliate_destinations = ub.find_duplicates(dst_paths)
        print('dupliate_destinations = {}'.format(ub.urepr(dupliate_destinations, nl=1)))
        assert not dupliate_destinations
        src_exist_flags = [task['src'].exists() for task in tasks]
        dst_exist_flags = [task['dst'].exists() for task in tasks]
        both_exist_flags = [f1 and f2 for f1, f2 in zip(src_exist_flags, dst_exist_flags)]
        total = len(tasks)
        num_both_exist = sum(both_exist_flags)
        num_src_exist = sum(src_exist_flags)
        num_dst_exist = sum(dst_exist_flags)
        num_src_missing = total - num_src_exist
        print(f'num_src_exist={num_src_exist}')
        print(f'num_dst_exist={num_dst_exist}')
        print(f'num_src_missing={num_src_missing}')
        print(f'num_both_exist={num_both_exist}')
        print(f'total={total}')

        # TODO:
        # Check if any tasks are moving directories, and if so, ensure they

        if num_both_exist:
            raise Exception('A src and dst path both exist! this error cannot be bypassed: {num_both_exist} / {total}')

        errors = []

        if num_dst_exist > 0:
            if num_dst_exist == total:
                errors.append('Script seems like it already ran')
            else:
                errors.append(f'Script seems like it partially ran: {num_dst_exist} / {total}')

        if num_src_missing > 0:
            errors.append(f'Missing source {num_src_missing} / {total} data')
        if errors:
            raise Exception('\n'.join(errors))

        _unsubmitted_info(paths)


def remove_empty_dirs(dpath):
    """
    Remove any directories that are empty or only contain (recursively) other
    empty directories.

    In bash this is similar to

    .. code:: bash
        # with POSIX find
        find . -type d -empty -print
        find . -type d -empty -delete

        # or with fd-find
        fd -u --type empty --type directory
        fd -u --type empty --type directory -x rmdir

    Args:
        dpath (str | PathLike):
            directory to remove other empty directories in. If the input
            directory is empty it is also removed.

    References:
        .. [UnixSE46322] https://unix.stackexchange.com/questions/46322/how-can-i-recursively-delete-empty-directories-in-my-home-directory

    Example:
        >>> import ubelt as ub
        >>> from kwutil.fsops_managers import remove_empty_dirs
        >>> test_dpath = ub.Path.appdir('kwutil', 'tests', 'remove_empty_dirs')
        >>> (test_dpath / 'dir1' / 'dir2' / 'dir3').ensuredir()
        >>> dpath = (test_dpath / 'dir1')
        >>> assert dpath.exists()
        >>> remove_empty_dirs(dpath)
        >>> assert not dpath.exists()
    """
    # in bash:
    import os
    empty_dpaths = True
    dpath = os.path.abspath(dpath)
    while empty_dpaths:
        empty_dpaths = []
        for r, ds, fs in os.walk(dpath):
            if not ds and not fs:
                empty_dpaths.append(r)
        for d in empty_dpaths:
            os.rmdir(d)


def _unsubmitted_info(paths):
    from kwutil.util_units import byte_str

    pathinfos = []
    for path in paths:
        node_data = _pathinfo(path)
        node_data['path'] = path
        pathinfos.append(node_data)

    sizes = ub.ddict(int)
    for info in pathinfos:
        for k, v in info['stats'].items():
            if k.endswith('.size'):
                sizes[k + '.' + info['typelabel']] += v

    human_sizes = ub.udict(sizes).map_values(byte_str)
    print(f'human_sizes={human_sizes}')

    type_hist = ub.dict_hist(p['typelabel'] for p in pathinfos)
    print(f'type_hist = {ub.urepr(type_hist, nl=1)}')


def _pathinfo(path, with_stats=True, assume_exists=False):
    # From xdev DirectoryWalker
    import os
    node_data = {}

    if not assume_exists:
        node_data['exists'] = path.exists()

    islink = os.path.islink(path)
    isfile = os.path.isfile(path)
    isdir = os.path.isdir(path)

    if islink:
        target = os.readlink(path)
        isbroken = not isdir and not isfile
        node_data['broken'] = isbroken
        node_data['target'] = target

    if isfile:
        node_data['X_ok'] = os.access(path, os.X_OK)

    types = []
    if islink:
        types.append('L')
        if isbroken:
            types.append('B')
    if isfile:
        types.append('F')
    if isdir:
        types.append('D')
    typelabel = ''.join(types)

    node_data['islink'] = islink
    node_data['isfile'] = isfile
    node_data['isdir'] = isdir
    node_data['typelabel'] = typelabel

    if with_stats:
        ext = path.suffix
        prefix = ext.lstrip('.') + '.'
        stats = {}
        try:
            stat_obj = path.stat(follow_symlinks=False)
        except FileNotFoundError:
            stats['broken_link'] = True
            stats['size'] = 0
        else:
            stats['size'] = stat_obj.st_size

        stats['files'] = 1

        stats = {prefix + k: v for k, v in stats.items()}
        node_data['stats'] = stats
    return node_data
