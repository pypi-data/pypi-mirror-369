"""
Experimental.

For handling race conditions within and between processes (ideally).
"""
import ubelt as ub
import weakref


DEBUG = 0


class Superlock:
    """
    A thread and/or process lock

    The lockiest lock that ever did lock... or at least an attempt at it.

    This is experimental and not well tested.

    If lock_fpath is NoParam, uses a global shared process lock. If None, then
    no process lock is used.

    If thread_key is NoParam, uses a global shared thread lock. If None, then
    no thread lock is used.

    Otherwise locks with the same process_fpath OR thread_key will not execute
    concurrently, up to system limitations of the locking mechanisms.

    Uses [Fasteners]_ for the process-based file-locks, which do have
    fundamental issues [OnFileLocks]_.

    TODO: Evaluate [FileLock]_ as an alternative.

    References:
        .. [FileLock] https://github.com/tox-dev/filelock
        .. [Fasteners] https://pypi.org/project/fasteners/
        .. [OnFileLocks] https://0pointer.de/blog/projects/locking.html

    SeeAlso:

        https://pypi.org/project/readerwriterlock/#description
        https://github.com/python/cpython/issues/53046
        https://gist.github.com/tylerneylon/a7ff6017b7a1f9a506cf75aa23eacfd6
        https://discuss.python.org/t/add-rw-locks-to-python/76638
        https://py-filelock.readthedocs.io/en/latest/index.html

    Ignore:
        Fasterners has `fasteners.ReaderWriterLock()` thread RW lock
        impelmentation that favors readers. It would be nice if we let the user
        specify priority.

    Example:
        >>> # xdoctest: +REQUIRES(module:fasteners)
        >>> self = Superlock()
        >>> with self:
        >>>     print('non-concurent code')

    Example:
        >>> # xdoctest: +REQUIRES(module:fasteners)
        >>> from kwutil.util_locks import *  # NOQA
        >>> import ubelt as ub
        >>> lock1 = Superlock()
        >>> lock2 = Superlock()
        >>> assert lock1.acquire(timeout=10)
        >>> assert not lock2.acquire(timeout=0.01)
        >>> lock1.release()
        >>> assert lock2.acquire()
        >>> lock2.release()

    Example:
        >>> # Demonstrate a real world case with thread locks
        >>> # xdoctest: +REQUIRES(module:fasteners)
        >>> import time
        >>> from kwutil.util_locks import Superlock
        >>> import ubelt as ub
        >>> #
        >>> shared_counter = []
        >>> #
        >>> def task(i):
        ...     with Superlock():
        ...         # simulate work inside critical section
        ...         current_len = len(shared_counter)
        >>>         print(f'current_len={current_len}')
        ...         time.sleep(0.05)
        ...         shared_counter.append(i)
        ...         # ensure no concurrent execution by checking counter length did not change during sleep
        ...         assert len(shared_counter) == current_len + 1
        ...     return i
        >>> #
        >>> with ub.Executor(mode='thread', max_workers=4) as executor:
        ...     results = list(executor.map(task, range(8)))
        >>> #
        >>> sorted(results) == list(range(8))
        True
        >>> len(shared_counter) == 8
        True

    Example:
        >>> # Demonstrate a real world case with process locks
        >>> # xdoctest: +REQUIRES(module:fasteners)
        >>> # xdoctest: +SKIP('xdoctest does not support pickled functions yet')
        >>> import time
        >>> import ubelt as ub
        >>> from pathlib import Path
        >>> #
        >>> dpath = ub.Path.appdir('kwutil/tests/superlock').ensuredir()
        >>> counter_fpath = dpath / 'shared_counter.txt'
        >>> counter_fpath.write_text('0')
        >>> #
        >>> def task(i):
        ...     import time
        ...     from pathlib import Path
        ...     from kwutil.util_locks import Superlock
        ...     lock = Superlock()
        ...     counter_fpath = Path(ub.Path.appdir('kwutil/tests/superlock') / 'shared_counter.txt')
        ...     with lock:
        ...         current = int(counter_fpath.read_text())
        ...         time.sleep(0.05)  # simulate some work
        ...         counter_fpath.write_text(str(current + 1))
        ...     return i
        >>> #
        >>> with ub.Executor(mode='process', max_workers=4) as executor:
        ...     results = list(executor.map(task, range(8)))
        >>> #
        >>> sorted(results) == list(range(8))
        True
        >>> final_value = int(counter_fpath.read_text())
        >>> final_value == 8
        True
    """

    THREAD_LOCKS = weakref.WeakValueDictionary()
    GLOBAL_THREAD_KEY = '__GLOBAL_THREAD_LOCK__'
    GLOBAL_APPNAME = 'fasteners_ext/file_locks'
    GLOBAL_LOCK_FNAME = 'superlock.lock'

    def _debug(self, msg):
        import os
        import threading
        print(f'[pid={os.getpid()} tid={threading.get_ident()}] {msg}')

    def __init__(self, lock_fpath=ub.NoParam, thread_key=ub.NoParam):
        if DEBUG:
            self._debug('Init SuperLock')
        import fasteners
        import threading
        if lock_fpath is ub.NoParam:
            lock_fpath = self.global_lock_fpath

        if thread_key is ub.NoParam:
            thread_key = self.GLOBAL_THREAD_KEY

        self.lock_fpath = lock_fpath
        self.thread_key = thread_key
        self.process_lock = None
        self.thread_lock = None

        self._thread_counter = 0
        self._process_counter = 0
        # Only let one super lock within a thread aquire / release something at
        # the same time. But you can release while another is trying to aquire.
        self._aquire_lock = threading.Lock()
        self._release_lock = threading.Lock()

        if thread_key is not None:
            self.thread_lock = self.THREAD_LOCKS.get(thread_key, None)
            if self.thread_lock is None:
                self.thread_lock = threading.Lock()
                self.THREAD_LOCKS[thread_key] = self.thread_lock

        if lock_fpath is not None:
            self.process_lock = fasteners.InterProcessLock(lock_fpath)  #

    @property
    def global_lock_fpath(self):
        global_dpath = ub.Path.appdir(self.GLOBAL_APPNAME, type='cache').ensuredir()
        global_lock_fpath = global_dpath / self.GLOBAL_LOCK_FNAME
        return global_lock_fpath

    def acquire(self, blocking=True, timeout=None, delay=0.01, max_delay=0.1):
        # got = []
        # # FIXME: corner case when one acquires and the other doesn't
        # if self.thread_lock is not None:
        #     thread_timeout = -1 if timeout is None else timeout
        #     gotten1 = self.thread_lock.acquire(blocking=blocking, timeout=thread_timeout)
        #     got.append(gotten1)
        # if self.process_lock is not None:
        #     gotten2 = self.process_lock.acquire(
        #         blocking=blocking, timeout=timeout, delay=delay,
        #         max_delay=max_delay)
        #     got.append(gotten2)
        # gotten = all(got)
        # return gotten

        if DEBUG:
            self._debug('About to aquire SuperLock')

        gotten1 = False
        gotten2 = False

        with self._aquire_lock:
            if self.thread_lock is not None:
                thread_timeout = -1 if timeout is None else timeout

                if DEBUG:
                    self._debug('About to aquire thread lock')
                gotten1 = self.thread_lock.acquire(blocking=blocking, timeout=thread_timeout)
                if not gotten1:
                    if DEBUG:
                        self._debug('Failed to aquire thread lock')
                    return False
                self._thread_counter += 1
                if DEBUG:
                    self._debug('Aquired thread lock')

            if self.process_lock is not None:
                if DEBUG:
                    self._debug('About to aquire process lock')
                gotten2 = self.process_lock.acquire(
                    blocking=blocking, timeout=timeout, delay=delay,
                    max_delay=max_delay)
                if not gotten2:
                    # Undo thread_lock if process lock failed to aquire
                    if DEBUG:
                        self._debug('Failed to aquire process lock')
                    if gotten1:
                        if DEBUG:
                            self._debug('Undo thread lock')
                        self.thread_lock.release()
                        self._thread_counter -= 1
                    return False
                self._process_counter += 1

        if DEBUG:
            self._debug('Aquired process lock')

        # Both locks (if any) acquired successfully or no locks requested
        return True

    def release(self):
        if DEBUG:
            self._debug('Attempting to release superlock')
        with self._release_lock:
            if self.process_lock is not None:
                self.process_lock.release()
                self._process_counter -= 1
                if DEBUG:
                    self._debug('Released process lock')

            if self.thread_lock is not None:
                self.thread_lock.release()
                self._thread_counter -= 1
                if DEBUG:
                    self._debug('Released thread lock')
            if DEBUG:
                self._debug('Releasing superlock')

    def __enter__(self):
        gotten = self.acquire()
        assert gotten, 'should always be true'
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """
        Args:
            ex_type (Type[BaseException] | None):
            ex_value (BaseException | None):
            ex_traceback (TracebackType | None):

        Returns:
            bool | None
        """
        self.release()
