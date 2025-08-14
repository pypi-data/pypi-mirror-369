"""
The kwutil Module
=================

+------------------+------------------------------------------------------+
| Read the docs    | https://kwutil.readthedocs.io                        |
+------------------+------------------------------------------------------+
| Gitlab (main)    | https://gitlab.kitware.com/computer-vision/kwutil    |
+------------------+------------------------------------------------------+
| Github (mirror)  | https://github.com/Kitware/kwutil                    |
+------------------+------------------------------------------------------+
| Pypi             | https://pypi.org/project/kwutil                      |
+------------------+------------------------------------------------------+

The Kitware utility module.

This module is for small, pure-python utility functions. Dependencies are
allowed, but they must be small and highly standard packages (e.g. rich,
psutil, ruamel.yaml).

"""
__version__ = '0.3.6'

__autogen__ = """
mkinit ~/code/kwutil/kwutil/__init__.py --lazy_loader --diff
mkinit ~/code/kwutil/kwutil/__init__.py --lazy_loader -w
mkinit ~/code/kwutil/kwutil/__init__.py
"""


__submodules__ = {
    'copy_manager': [],
    'fsops_managers': ['CopyManager', 'MoveManager', 'DeleteManager'],
    'partial_format': [],
    'process_context': ['ProcessContext'],
    'slugify_ext': [],
    'util_environ': ['envflag'],
    'util_eval': ['safeeval'],
    'util_exception': [],
    'util_hardware': ['Hardware'],
    'util_iter': [],
    'util_json': ['Json'],
    'util_locks': ['Superlock'],
    'util_parallel': ['coerce_num_workers'],
    'util_path': ['sanitize_path_name'],
    'util_pattern': ['Pattern', 'MultiPattern'],
    'util_progress': ['ProgressManager'],
    'util_random': ['ensure_rng'],
    'util_resources': [],
    'util_time': ['datetime', 'timedelta'],
    'util_units': [],
    'util_windows': [],
    'util_xml': ['XML'],
    'util_yaml': ['Yaml'],
}

import lazy_loader


__getattr__, __dir__, __all__ = lazy_loader.attach(
    __name__,
    submodules={
        'copy_manager',
        'fsops_managers',
        'partial_format',
        'process_context',
        'slugify_ext',
        'util_environ',
        'util_eval',
        'util_exception',
        'util_hardware',
        'util_iter',
        'util_json',
        'util_locks',
        'util_parallel',
        'util_path',
        'util_pattern',
        'util_progress',
        'util_random',
        'util_resources',
        'util_time',
        'util_units',
        'util_windows',
        'util_xml',
        'util_yaml',
    },
    submod_attrs={
        'fsops_managers': [
            'CopyManager',
            'MoveManager',
            'DeleteManager',
        ],
        'process_context': [
            'ProcessContext',
        ],
        'util_environ': [
            'envflag',
        ],
        'util_eval': [
            'safeeval',
        ],
        'util_hardware': [
            'Hardware',
        ],
        'util_json': [
            'Json',
        ],
        'util_locks': [
            'Superlock',
        ],
        'util_parallel': [
            'coerce_num_workers',
        ],
        'util_pattern': [
            'Pattern',
            'MultiPattern',
        ],
        'util_progress': [
            'ProgressManager',
        ],
        'util_random': [
            'ensure_rng',
        ],
        'util_time': [
            'datetime',
            'timedelta',
        ],
        'util_xml': [
            'XML',
        ],
        'util_yaml': [
            'Yaml',
        ],
    },
)

__all__ = ['CopyManager', 'DeleteManager', 'Hardware', 'Json', 'MoveManager',
           'MultiPattern', 'Pattern', 'ProcessContext', 'ProgressManager',
           'Superlock', 'XML', 'Yaml', 'coerce_num_workers', 'copy_manager',
           'datetime', 'ensure_rng', 'envflag', 'fsops_managers',
           'partial_format', 'process_context', 'safeeval', 'slugify_ext',
           'timedelta', 'util_environ', 'util_eval', 'util_exception',
           'util_hardware', 'util_iter', 'util_json', 'util_locks',
           'util_parallel', 'util_path', 'util_pattern', 'util_progress',
           'util_random', 'util_resources', 'util_time', 'util_units',
           'util_windows', 'util_xml', 'util_yaml']
