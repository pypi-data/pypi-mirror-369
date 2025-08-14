The kwutil Module
=================


|GitlabCIPipeline| |GitlabCICoverage| |Pypi| |PypiDownloads| |ReadTheDocs|


+------------------+------------------------------------------------------+
| Read the docs    | https://kwutil.readthedocs.io                        |
+------------------+------------------------------------------------------+
| Gitlab (main)    | https://gitlab.kitware.com/computer-vision/kwutil    |
+------------------+------------------------------------------------------+
| Github (mirror)  | https://github.com/Kitware/kwutil                    |
+------------------+------------------------------------------------------+
| Pypi             | https://pypi.org/project/kwutil                      |
+------------------+------------------------------------------------------+

.. .. |ReadTheDocs|

The Kitware utility module.

This module is for small, pure-python utility functions. Dependencies are
allowed, but they must be small and highly standard packages (e.g. rich,
psutil, ruamel.yaml).

These were originally derived from `geowatch <https://gitlab.kitware.com/computer-vision/geowatch>`_ utilities.
Some of them were also from `xdev <https://github.com/Erotemic/xdev>`_.

In the case that a no-dependency utility in this library proves itself to be
extremely useful, it may be ported to `ubelt <https://github.com/Erotemic/ubelt>`_.


Current top-level API:

.. code:: python

    from kwutil import copy_manager
    from kwutil import fsops_managers
    from kwutil import partial_format
    from kwutil import process_context
    from kwutil import slugify_ext
    from kwutil import util_environ
    from kwutil import util_eval
    from kwutil import util_exception
    from kwutil import util_hardware
    from kwutil import util_json
    from kwutil import util_locks
    from kwutil import util_parallel
    from kwutil import util_path
    from kwutil import util_pattern
    from kwutil import util_progress
    from kwutil import util_random
    from kwutil import util_resources
    from kwutil import util_time
    from kwutil import util_units
    from kwutil import util_windows
    from kwutil import util_xml
    from kwutil import util_yaml

    from kwutil.fsops_managers import (CopyManager, MoveManager, DeleteManager,)
    from kwutil.process_context import (ProcessContext,)
    from kwutil.util_environ import (envflag,)
    from kwutil.util_eval import (safeeval,)
    from kwutil.util_hardware import (Hardware,)
    from kwutil.util_json import (Json,)
    from kwutil.util_locks import (Superlock,)
    from kwutil.util_parallel import (coerce_num_workers,)
    from kwutil.util_pattern import (Pattern, MultiPattern,)
    from kwutil.util_progress import (ProgressManager,)
    from kwutil.util_random import (ensure_rng,)
    from kwutil.util_time import (datetime, timedelta,)
    from kwutil.util_yaml import (Yaml,)
    from kwutil.util_xml import (XML,)

    __all__ = ['CopyManager', 'DeleteManager', 'Hardware', 'Json', 'MoveManager',
               'MultiPattern', 'Pattern', 'ProcessContext', 'ProgressManager',
               'Superlock', 'XML', 'Yaml', 'coerce_num_workers', 'copy_manager',
               'datetime', 'ensure_rng', 'envflag', 'fsops_managers',
               'partial_format', 'process_context', 'safeeval', 'slugify_ext',
               'timedelta', 'util_environ', 'util_eval', 'util_exception',
               'util_hardware', 'util_json', 'util_locks', 'util_parallel',
               'util_path', 'util_pattern', 'util_progress', 'util_random',
               'util_resources', 'util_time', 'util_units', 'util_windows',
               'util_xml', 'util_yaml']


.. |Pypi| image:: https://img.shields.io/pypi/v/kwutil.svg
    :target: https://pypi.python.org/pypi/kwutil

.. |PypiDownloads| image:: https://img.shields.io/pypi/dm/kwutil.svg
    :target: https://pypistats.org/packages/kwutil

.. |ReadTheDocs| image:: https://readthedocs.org/projects/kwutil/badge/?version=release
    :target: http://kwutil.readthedocs.io/en/release/

.. # See: https://ci.appveyor.com/project/jon.crall/kwutil/settings/badges
.. |Appveyor| image:: https://ci.appveyor.com/api/projects/status/py3s2d6tyfjc8lm3/branch/main?svg=true
   :target: https://ci.appveyor.com/project/jon.crall/kwutil/branch/main

.. |GitlabCIPipeline| image:: https://gitlab.kitware.com/computer-vision/kwutil/badges/main/pipeline.svg
   :target: https://gitlab.kitware.com/computer-vision/kwutil/-/jobs

.. |GitlabCICoverage| image:: https://gitlab.kitware.com/computer-vision/kwutil/badges/main/coverage.svg
    :target: https://gitlab.kitware.com/computer-vision/kwutil/commits/main
