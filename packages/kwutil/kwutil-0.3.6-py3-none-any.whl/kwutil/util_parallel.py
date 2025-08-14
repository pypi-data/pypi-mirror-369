"""
Run parallel jobs but only let a fixed number run at a time and pause main
thread execution (i.e. block) if the buffer gets too full. This can help if the
main thread has the potential to overload the waiting buffer. This is used in
several geowatch predict scripts.

Uses concurrent.futures thread or process pool executors.
"""
import ubelt as ub
# from collections import deque


class BlockingJobQueue:
    """
    Helper to execute some number of processes in a separate thread.

    A call to submit will block if there is any available background workers
    until at least one of them finishes.

    The wait_until_finished should always be called at the end.

    TODO:
        - [ ] Compare with https://gist.github.com/noxdafox/4150eff0059ea43f6adbdd66e5d5e87e
        - [ ] Add parameter that lets the user answer the question: "when does this block?"
              We could block:
                  1. When there are too many live jobs (I think it is, but how is this different from max-workers?)
                  2. Whenever there are more than some number of unhanled results. (Good if results take a lot of memory)

    Example:
        >>> from kwutil.util_parallel import *  # NOQA
        >>> import time
        >>> import random
        >>> # Test with zero workers
        >>> N = 100
        >>> global_list = []
        >>> def background_job(i):
        >>>     time.sleep(random.random() * 0.001)
        >>>     global_list.append(f'Executed job {i:03d}')
        >>> self = BlockingJobQueue()
        >>> for i in range(100):
        >>>     self.submit(background_job, i)
        >>> self.wait_until_finished()
        >>> assert len(global_list) == N
        >>> assert sorted(global_list) == global_list
        >>> #
        >>> # xdoctest: +REQUIRES(env:TEST_BLOCKING_JOB_QUEUE_THREADS)
        >>> #
        >>> # Test the threaded case
        >>> global_list = []
        >>> def background_job(i):
        >>>     time.sleep(random.random() * 0.1 + 0.1)
        >>>     global_list.append(f'Executed job {i:03d}')
        >>> self = BlockingJobQueue(max_workers=10)
        >>> for i in range(100):
        >>>     if i == self.max_workers:
        >>>         assert len(self.jobs) == self.max_workers
        >>>     self.submit(background_job, i)
        >>> self.wait_until_finished()
        >>> assert len(global_list) == N
        >>> assert sorted(global_list) != global_list
    """

    def __init__(self, mode='thread', max_workers=0):
        self.max_workers = max_workers
        self.executor = ub.Executor(mode=mode, max_workers=max_workers)
        self.jobs = []

    def has_room(self):
        return len(self.jobs) >= max(1, self.max_workers)

    def _wait_for_room(self):
        # Wait until the pool has available workers
        while len(self.jobs) >= max(1, self.max_workers):
            new_active_jobs = []
            for job in self.jobs:
                if job.running():
                    new_active_jobs.append(job)
                else:
                    # Check that the result is ok
                    job.result()
            self.jobs = new_active_jobs

    def wait_until_finished(self, desc=None):
        if desc is None:
            jobiter = self.jobs
        else:
            jobiter = ub.ProgIter(self.jobs, desc=desc)
        for job in jobiter:
            job.result()

    def submit(self, func, *args, **kwargs):
        self._wait_for_room()
        job = self.executor.submit(func, *args, **kwargs)
        self.jobs.append(job)
        return job


class _DelayedFuture:
    """
    Wraps a future object so we can execute logic when its result has been
    accessed.
    """
    def __init__(self, func, args, kwargs, parent):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.task = (func, args, kwargs)
        self.parent = parent
        self.future = None

    def result(self, timeout=None):
        if self.future is None:
            raise Exception('The task has not been submitted yet')
        result = self.future.result(timeout)
        self.parent._job_result_accessed_callback(self)
        return result


class _DelayedBlockingJobQueue:
    """

    References:
        .. [GISTnoxdafoxMaxQueuePool] https://gist.github.com/noxdafox/4150eff0059ea43f6adbdd66e5d5e87e

    Ignore:
        >>> from kwutil.util_parallel import _DelayedBlockingJobQueue
        >>> self = _DelayedBlockingJobQueue(max_unhandled_jobs=5)
        >>> futures = [
        >>>     self.submit(print, i)
        >>>     for i in range(10)
        >>> ][::-1]
        >>> import time
        >>> time.sleep(0.5)
        >>> print(self._num_submitted_jobs)
        >>> print(self._num_handled_results)
        >>> print('--- First 5 should have printed ---')
        >>> for _ in range(3):
        >>>     f = futures.pop()
        >>>     f.result()
        >>> time.sleep(0.5)
        >>> print(self._num_submitted_jobs)
        >>> print(self._num_handled_results)
        >>> print('--- 3 Results were haneld, so 3 more can join the queue')
        >>> for _ in range(3):
        >>>     f = futures.pop()
        >>>     f.result()
        >>> time.sleep(0.5)
        >>> print(self._num_submitted_jobs)
        >>> print(self._num_handled_results)
        >>> print('--- Handling the rest, but everything should have already been submitted')
        >>> for _ in range(4):
        >>>     f = futures.pop()
        >>>     f.result()
    """
    def __init__(self, max_unhandled_jobs, mode='thread', max_workers=None):
        from collections import deque
        self._unsubmitted = deque()
        self.pool = ub.Executor(mode=mode, max_workers=max_workers)
        self.max_unhandled_jobs = max_unhandled_jobs
        self._num_handled_results = 0
        self._num_submitted_jobs = 0
        self._num_unhandled = 0

    def submit(self, func, *args, **kwargs):
        """
        Queues a new job, but wont execute until
        some conditions are met
        """
        delayed = _DelayedFuture(func, args, kwargs, parent=self)
        self._unsubmitted.append(delayed)
        self._submit_if_room()
        return delayed

    def _submit_if_room(self):
        while self._num_unhandled < self.max_unhandled_jobs and self._unsubmitted:
            delayed = self._unsubmitted.popleft()
            self._num_submitted_jobs += 1
            self._num_unhandled += 1
            delayed.future = self.pool.submit(delayed.func, *delayed.args, **delayed.kwargs)

    def _job_result_accessed_callback(self, _):
        """Called when the user handles a result """
        self._num_handled_results += 1
        self._num_unhandled -= 1
        self._submit_if_room()


class _MaxQueuePool:
    """
    This Class wraps a concurrent.futures.Executor
    limiting the size of its task queue.
    If `max_queue_size` tasks are submitted, the next call to submit will block
    until a previously submitted one is completed.

    References:
        .. [GISTnoxdafoxMaxQueuePool] https://gist.github.com/noxdafox/4150eff0059ea43f6adbdd66e5d5e87e

    Ignore:
        import sys, ubelt
        sys.path.append(ubelt.expandpath('~/code/geowatch'))
        from geowatch.tasks.fusion.evaluate import *  # NOQA
        from geowatch.tasks.fusion.evaluate import _memo_legend, _redraw_measures
        self = _MaxQueuePool(max_queue_size=0)

        dpath = ub.Path.appdir('kwutil/doctests/maxpoolqueue')
        dpath.delete().ensuredir()
        signal_fpath = dpath / 'signal'

        def waiting_worker():
            counter = 0
            while not signal_fpath.exists():
                counter += 1
            return counter

        future = self.submit(waiting_worker)

        try:
            future.result(timeout=0.001)
        except TimeoutError:
            ...
        signal_fpath.touch()
        result = future.result()

    """
    def __init__(self, max_queue_size=None, mode='thread', max_workers=0):
        from threading import BoundedSemaphore
        if max_queue_size is None:
            max_queue_size = max_workers
        self.pool = ub.Executor(mode=mode, max_workers=max_workers)
        if 'serial' in self.pool.backend.__class__.__name__.lower():
            self.pool_queue = None
        else:
            self.pool_queue = BoundedSemaphore(max_queue_size)

    def submit(self, function, *args, **kwargs):
        """Submits a new task to the pool, blocks if Pool queue is full."""
        if self.pool_queue is not None:
            self.pool_queue.acquire()

        future = self.pool.submit(function, *args, **kwargs)
        future.add_done_callback(self.pool_queue_callback)

        return future

    def pool_queue_callback(self, _):
        """Called once task is done, releases one queue slot."""
        if self.pool_queue is not None:
            self.pool_queue.release()

    def shutdown(self):
        """
        Calls the shutdown function of the underlying backend.
        """
        return self.pool.shutdown()


def coerce_num_workers(num_workers='auto', minimum=0):
    """
    Return some number of CPUs based on a chosen heuristic

    Args:
        num_workers (int | str):
            A special string code, or an exact number of cpus

        minimum (int): minimum workers we are allowed to return

    Returns:
        int : number of available cpus based on request parameters

    CommandLine:
        xdoctest -m kwutil.util_parallel coerce_num_workers

    Example:
        >>> # xdoctest: +REQUIRES(module:psutil)
        >>> from kwutil.util_parallel import *  # NOQA
        >>> print(coerce_num_workers('all'))
        >>> print(coerce_num_workers('avail'))
        >>> print(coerce_num_workers('auto'))
        >>> print(coerce_num_workers('all-2'))
        >>> print(coerce_num_workers('avail-2'))
        >>> print(coerce_num_workers('all/2'))
        >>> print(coerce_num_workers('min(all,2)'))
        >>> #print(coerce_num_workers('[max(all,2)][0]'))
        >>> import pytest
        >>> with pytest.raises(Exception):
        >>>     print(coerce_num_workers('all + 1' + (' + 1' * 100)))
        >>> total_cpus = coerce_num_workers('all')
        >>> assert coerce_num_workers('all-2') == max(total_cpus - 2, 0)
        >>> assert coerce_num_workers('all-100') == max(total_cpus - 100, 0)
        >>> assert coerce_num_workers('avail') <= coerce_num_workers('all')
        >>> assert coerce_num_workers(3) == max(3, 0)
    """
    import psutil
    from kwutil.util_eval import restricted_eval

    try:
        num_workers = int(num_workers)
    except Exception:
        pass

    if isinstance(num_workers, str):

        num_workers = num_workers.lower()

        if num_workers == 'auto':
            num_workers = 'avail-2'

        # input normalization
        num_workers = num_workers.replace('available', 'avail')

        local_dict = {}

        if 'avail' in num_workers:
            current_load = [p / 100 for p in psutil.cpu_percent(percpu=True)]
            local_dict['avail'] = sum(f < 0.5 for f in current_load)
        local_dict['all_'] = psutil.cpu_count()

        if num_workers == 'none':
            num_workers = None
        else:
            expr = num_workers.replace('all', 'all_')
            # limit chars even further if eval is used
            # Mitigate attack surface by restricting builtin usage
            max_chars = 32
            builtins_passlist = ['min', 'max', 'round', 'sum']
            num_workers = restricted_eval(expr, max_chars, local_dict,
                                          builtins_passlist)

    if num_workers is not None:
        num_workers = max(int(num_workers), minimum)

    return num_workers
