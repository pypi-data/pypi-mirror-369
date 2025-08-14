"""
Defines the :class:`ProcessContext` object, which is what mlops expects jobs to
be wrapped in.

TODO:
    - [ ] Make "most" telemetry opt-in
"""
import sys
import os
import ubelt as ub
from kwutil import util_environ

PROCESS_CONTEXT_DISABLE_ALL_TELEMETRY = util_environ.envflag('PROCESS_CONTEXT_DISABLE_ALL_TELEMETRY', default=False)
PROCESS_CONTEXT_DISABLE_MOST_TELEMETRY = util_environ.envflag('PROCESS_CONTEXT_DISABLE_MOST_TELEMETRY', default=False)


class ProcessContext:
    """
    Context manager to track the context under which a result was computed.

    This tracks things like start / end time. The command line that can
    reproduce the process (assuming an appropriate environment. The
    configuration the process was run with. The machine details the process was
    run on. The power usage / carbon emissions the process used, and other
    information.

    Args:
        args (str | List[str]):
            This should be the sys.argv or the command line string that can be
            used to rerun the process

        config (Dict):
            This should be a configuration dictionary (likely based on
            sys.argv)

        name (str): the name of this process

        type (str): The type of this process
            (usually keep the default of process)

        request_all_telemetry (bool):
            if False, telemetry is disabled. This is forced to False if
            PROCESS_CONTEXT_DISABLE_MOST_TELEMETRY is in the environment.

        request_most_telemetry (bool):
            if False, telemetry is disabled. This is forced to False if
            PROCESS_CONTEXT_DISABLE_ALL_TELEMETRY is in the environment.

    Note:
        This module provides telemetry, which records user-identifiable
        information. While useful, it does raise ethical concerns about user
        privacy, and the people running this code have a right to know about it
        and opt out. Notably, this module simply records the information, but
        does not send it anywhere. As such, a default opt-in is reasonable, but
        any future work that sends this information anywhere must be opt-out by
        default.

    Note:
        There are two levels of telemetry.

        Environment telemetry. These are things like the machine the code was
        run on. Use PROCESS_CONTEXT_DISABLE_MOST_TELEMETRY=0 to opt-out.

        The start / stop / sys.argv / config objects are necessary for mlops to
        do anything. But these can leak information by containing system paths.
        Emissions is also in this category. Use
        PROCESS_CONTEXT_DISABLE_ALL_TELEMETRY to opt out.

    CommandLine:
        xdoctest -m kwutil.process_context ProcessContext

    Example:
        >>> # xdoctest: +REQUIRES(module:psutil)
        >>> from kwutil.process_context import *
        >>> import rich
        >>> # Adding things like disk info an tracking emission usage
        >>> self = ProcessContext(track_emissions='offline')
        >>> obj1 = self.start().stop()
        >>> self.add_disk_info('.')
        >>> #
        >>> # Telemetry can be mostly disabled
        >>> self = ProcessContext(track_emissions='offline', request_most_telemetry=False)
        >>> obj2 = self.start().stop()
        >>> self.add_disk_info('.')
        >>> # Telemetry can be completely disabled
        >>> self = ProcessContext(track_emissions='offline', request_all_telemetry=False)
        >>> obj3 = self.start().stop()
        >>> self.add_disk_info('.')
        >>> rich.print('full_telemetry = {}'.format(ub.urepr(obj1, nl=3)))
        >>> rich.print('some_telemetry = {}'.format(ub.urepr(obj2, nl=3)))
        >>> rich.print('no_telemetry = {}'.format(ub.urepr(obj3, nl=3)))

    Example:
        >>> # xdoctest: +REQUIRES(module:psutil)
        >>> from kwutil.process_context import *
        >>> # flush can measure intermediate progress
        >>> self = ProcessContext(track_emissions=True)
        >>> self.add_disk_info('.')
        >>> obj1 = self.start().flush()
        >>> obj1_orig = obj1.copy()
        >>> obj2 = self.stop()
    """

    def __init__(self,
                 name=None,
                 type='process',
                 args=None,
                 config=None,
                 extra=None,
                 track_emissions=False,
                 request_all_telemetry=True,
                 request_most_telemetry=True,
                 output_dpath=None,
                 output_fpath=None,
                 ):
        import uuid
        if args is None:
            args = sys.argv
        else:
            import warnings
            warnings.warn(ub.paragraph(
                '''
                It is better to leave args unspecified so sys.argv is captured.
                Be sure to specify ``config`` as the resolved config.
                In the future we may add an extra param for unresolved configs.
                '''))

        self.properties = {
            "name": name,
            "args": args,
            "config": config,
            "machine": None,
            "start_timestamp": None,
            "stop_timestamp": None,
            "duration": None,
            "uuid": str(uuid.uuid4()),
            "extra": extra,
        }
        self.obj = {
            "type": type,
            "properties": self.properties
        }
        self.track_emissions = track_emissions
        self.emissions_tracker = None
        self._emission_backend = 'auto'
        self._started = False
        self._running = False

        if PROCESS_CONTEXT_DISABLE_ALL_TELEMETRY:
            request_all_telemetry = 0
        else:
            self.enable_all_telemetry = request_all_telemetry

        if PROCESS_CONTEXT_DISABLE_MOST_TELEMETRY:
            request_most_telemetry = 0
        else:
            self.enable_most_telemetry = request_most_telemetry

        if not self.enable_all_telemetry:
            self.enable_most_telemetry = 0
            self.properties.pop('config')
            self.properties.pop('args')
        self.output_dpath = output_dpath
        self.output_fpath = output_fpath

    def _infer_static_properties(self, func):
        props = self.properties
        if props['name'] is None:
            try:
                modname = func.__module__
            except AttributeError:
                try:
                    modname = func.__class__.__module__
                except AttributeError:
                    modname = None
            if modname is not None:
                try:
                    namespace = ub.modpath_to_modname(sys.modules[modname].__file__)
                except AttributeError:
                    namespace = sys.modules[modname].__name__
                if modname == '__main__':
                    namespace = f'{namespace}.__main__'
                props['name'] = f'{namespace}.{func.__name__}'
            else:
                props['name'] = func.__name__

        if self.output_dpath is None:
            self.output_dpath = ub.Path('.')

        if self.output_fpath is None:
            self.output_fpath = ub.Path(self.output_dpath) / '{name}-{uuid}.context'.format(**props)

    def _infer_dynamic_properties(self, func, args, kwargs):
        import kwutil
        props = self.properties
        jsonified = kwutil.Json.ensure_serializable(kwargs)
        props['config'] = jsonified

        self.add_disk_info('.')

        try:
            import torch
            device = torch.device(0) if torch.cuda.is_available() else torch.device('cpu')
            self.add_device_info(device)
        except Exception:
            ...

    @property
    def is_running(self):
        """
        Has the context object started and not yet been stopped?
        """
        return self._running

    @property
    def is_started(self):
        """
        Has the context object ever started? This can still return True if it
        has stopped.
        """
        return self._started

    def dump(self):
        import json
        text = json.dumps(self.obj)
        self.output_fpath.parent.ensuredir()
        self.output_fpath.write_text(text)

    def __call__(self, func):
        """
        Experimental use as a decorator.

        CommandLine:
            xdoctest -m kwutil.process_context ProcessContext.__call__

        Example:
            >>> # xdoctest: +REQUIRES(module:psutil)
            >>> import ubelt as ub
            >>> dpath = ub.Path.appdir('kwutil/test/process-context')
            >>> #
            >>> import kwutil
            >>> self = kwutil.ProcessContext(output_dpath=dpath)
            >>> def func():
            >>>     ...
            >>> _wrapper = self(func)
            >>> _wrapper.context
            >>> _wrapper()

        Example:
            >>> # xdoctest: +REQUIRES(module:psutil)
            >>> import kwutil
            >>> import ubelt as ub
            >>> dpath = ub.Path.appdir('kwutil/test/process-context')
            >>> @kwutil.ProcessContext(output_dpath=dpath)
            >>> def myfunc():
            >>>     ...
            >>> myfunc()
            >>> print(f'myfunc.context.obj = {ub.urepr(myfunc.context.obj, nl=3)}')
        """
        import functools
        self._infer_static_properties(func)

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            self._infer_dynamic_properties(func, args, kwargs)
            self.start()
            try:
                result = func(*args, **kwargs)
            finally:
                self.stop()
                try:
                    self.dump()
                except Exception as ex:
                    print('Failed to write context')
                    print(f'ex={ex}')
            return result

        _wrapper.context = self
        return _wrapper

    def write_invocation(self, invocation_fpath):
        """
        Write a helper file that contains a locally reproducible invocation of
        this process.
        """
        import shlex
        command = ' '.join(list(map(shlex.quote, self.properties['args'])))
        invocation_fpath = ub.Path(invocation_fpath)
        invocation_fpath.write_text(ub.codeblock(
            f'''
            #!/bin/bash
            {command}
            '''))

    def _timestamp(self):
        timestamp = ub.timestamp()
        return timestamp

    def _hostinfo(self):
        import socket
        if not self.enable_most_telemetry:
            return {}
        return {
            "host": socket.gethostname(),
            "user": ub.Path.home().name,
            'cwd': os.fspath(ub.Path.cwd()),
            "userhome": os.fspath(ub.Path.home()),
        }

    def _osinfo(self):
        import platform
        if not self.enable_most_telemetry:
            return {}
        (
            uname_system,
            _,
            uname_release,
            uname_version,
            _,
            uname_processor,
        ) = platform.uname()
        return {
            "os_name": uname_system,
            "os_release": uname_release,
            "os_version": uname_version,
            "arch": uname_processor,
        }

    def _pyinfo(self):
        import platform
        if not self.enable_most_telemetry:
            return {}
        return {
            "py_impl": platform.python_implementation(),
            "py_version": sys.version.replace("\n", ""),
        }

    def _meminfo(self):
        if not self.enable_most_telemetry:
            return {}
        import psutil
        # TODO: could collect memory info at start and stop and intermediate
        # stages.  Here we just want info that is static wrt to the machine.
        # For now, just get the total available.
        svmem_info = psutil.virtual_memory()
        return {
            "mem_total": svmem_info.total,
        }

    def _cpuinfo(self):
        if not self.enable_most_telemetry:
            return {}
        try:
            import cpuinfo
            _cpu_info = cpuinfo.get_cpu_info()
            cpu_info = {
                "cpu_brand": _cpu_info["brand_raw"],
                "cpu_count": _cpu_info["count"],
            }
        except ImportError as ex:
            cpu_info = {
                'error': f'ImportError: {ex}',
                "cpu_brand": None,
                "cpu_count": None,
            }
        return cpu_info

    def _gpuinfo(self):
        try:
            import torch
            num_devices = torch.cuda.device_count()
            device_infos = []
            for device_num in num_devices:
                device = torch.device(device_num)
                info = self._device_info(device)
                device_infos.append(info)
        # except ImportError as ex:
        except ImportError:
            device_infos = []
            # f'ImportError: {ex}'
        return device_infos

    def _machine(self):
        if not self.enable_most_telemetry:
            return {'telemetry_disabled': True}
        return ub.dict_union(
            self._hostinfo(),
            self._meminfo(),
            self._cpuinfo(),
            self._osinfo(),
            self._pyinfo(),
        )

    def start(self):
        self._started = True
        if not self.enable_all_telemetry:
            return self
        self._running = True
        self.properties.update({
            "machine": self._machine(),
            "start_timestamp": self._timestamp(),
            "stop_timestamp": None,
        })
        if self.track_emissions:
            self._start_emissions_tracker()

        return self

    def flush(self):
        if not self._started:
            raise Exception("Must start before you flush")
        if self.enable_all_telemetry:
            self.properties["stop_timestamp"] = self._timestamp()
            start_time = ub.timeparse(self.properties["start_timestamp"])
            stop_time = ub.timeparse(self.properties["stop_timestamp"])
            self.properties["duration"] = str(stop_time - start_time)
        if self.emissions_tracker is not None:
            try:
                self._flush_emissions_tracker()
            except Exception as ex:
                print(f'warning: issue with emissions ex={ex}')
        return self.obj

    def stop(self):
        if not self._started:
            raise Exception("Must start before you stop")
        if self.enable_all_telemetry:
            self.properties["stop_timestamp"] = self._timestamp()
            start_time = ub.timeparse(self.properties["start_timestamp"])
            stop_time = ub.timeparse(self.properties["stop_timestamp"])
            self.properties["duration"] = str(stop_time - start_time)
        if self.emissions_tracker is not None:
            try:
                self._stop_emissions_tracker()
            except Exception as ex:
                print(f'warning: issue with emissions ex={ex}')
        self._running = False
        return self.obj

    def __enter__(self):
        return self.start()

    def __exit__(self, a, b, c):
        self.stop()

    def _start_emissions_tracker(self):
        if not self.enable_all_telemetry:
            return

        emissions_tracker = None

        if isinstance(self.track_emissions, str):
            backend = self.track_emissions
        elif self.track_emissions:
            backend = 'auto'

        if backend == 'auto':
            backend = 'online'

        if backend == 'online':
            try:
                from codecarbon import EmissionsTracker
                """
                # emissions_tracker = EmissionsTracker(log_level='info')
                """
                try:
                    emissions_tracker = EmissionsTracker(log_level='error', allow_multiple_runs=True)
                except Exception:
                    emissions_tracker = EmissionsTracker(log_level='error')
                emissions_tracker.start()
            except Exception as ex:
                print('ex = {}'.format(ub.urepr(ex, nl=1)))
                print('Online emissions tracker is not available. Trying offline')
                if self._emission_backend == 'auto':
                    backend = 'offline'

        if backend == 'offline':
            try:
                # TODO: allow configuration
                from codecarbon import OfflineEmissionsTracker
                try:
                    emissions_tracker = OfflineEmissionsTracker(
                        country_iso_code='USA',
                        log_level='error',
                        # region='Virginia',
                        # cloud_provider='aws',
                        # cloud_region='us-east-1',
                        # country_2letter_iso_code='us'
                        allow_multiple_runs=True
                    )
                except Exception:
                    emissions_tracker = OfflineEmissionsTracker(
                        country_iso_code='USA',
                        log_level='error',
                        # region='Virginia',
                        # cloud_provider='aws',
                        # cloud_region='us-east-1',
                        # country_2letter_iso_code='us'
                    )
                emissions_tracker.start()
            except Exception as ex:
                print('Non-Critical Warning: Unable to track carbon emissions ex = {!r}'.format(ex))

        self.emissions_tracker = emissions_tracker

    def _flush_emissions_tracker(self):
        if self.emissions_tracker is None:
            self.properties['emissions'] = None
            return

        self.emissions_tracker._measure_power_and_energy()
        summary = emissions_data = self.emissions_tracker._prepare_emissions_data()
        self.emissions_tracker._persist_data(emissions_data)

        co2_kg = summary.emissions
        total_kWH = summary.energy_consumed
        # summary.cloud_provider
        # summary.cloud_region
        # summary.duration
        # summary.emissions_rate
        # summary.cpu_power
        # summary.gpu_power
        # summary.ram_power
        # summary.cpu_energy
        # summary.gpu_energy
        # summary.ram_energy
        emissions = {
            'co2_kg': co2_kg,
            'total_kWH': total_kWH,
            'run_id': str(self.emissions_tracker.run_id),
        }
        try:
            import pint
        except Exception as ex:
            print('Error stopping emissions tracker: ex = {!r}'.format(ex))
        else:
            reg = pint.UnitRegistry()
            if co2_kg is None:
                co2_kg = float('nan')
            co2_ton = (co2_kg * reg.kg).to(reg.metric_ton)
            dollar_per_ton = 15 / reg.metric_ton  # cotap rate
            emissions['co2_ton'] = co2_ton.m
            emissions['est_dollar_to_offset'] = (co2_ton * dollar_per_ton).m
        self.properties['emissions'] = emissions

    def _stop_emissions_tracker(self):
        if self.emissions_tracker is None:
            self.properties['emissions'] = None
            return
        self.emissions_tracker.stop()
        summary = self.emissions_tracker.final_emissions_data
        co2_kg = summary.emissions
        total_kWH = summary.energy_consumed
        # summary.cloud_provider
        # summary.cloud_region
        # summary.duration
        # summary.emissions_rate
        # summary.cpu_power
        # summary.gpu_power
        # summary.ram_power
        # summary.cpu_energy
        # summary.gpu_energy
        # summary.ram_energy
        emissions = {
            'co2_kg': co2_kg,
            'total_kWH': total_kWH,
            'run_id': str(self.emissions_tracker.run_id),
        }
        try:
            import pint
        except Exception as ex:
            print('Error stopping emissions tracker: ex = {!r}'.format(ex))
        else:
            reg = pint.UnitRegistry()
            if co2_kg is None:
                co2_kg = float('nan')
            co2_ton = (co2_kg * reg.kg).to(reg.metric_ton)
            dollar_per_ton = 15 / reg.metric_ton  # cotap rate
            emissions['co2_ton'] = co2_ton.m
            emissions['est_dollar_to_offset'] = (co2_ton * dollar_per_ton).m
        self.properties['emissions'] = emissions

    def _device_info(self, device):
        import torch
        try:
            device_info = {
                'device_index': device.index,
                'device_type': device.type,
            }
            try:
                device_props = torch.cuda.get_device_properties(device)
                capabilities = (device_props.multi_processor_count, device_props.minor)
                device_info.update({
                    'device_name': device_props.name,
                    'total_vram': device_props.total_memory,
                    'reserved_vram': torch.cuda.memory_reserved(device),
                    'allocated_vram': torch.cuda.memory_allocated(device),
                    'device_capabilities': capabilities,
                    'device_multi_processor_count': device_props.multi_processor_count,
                })
            except Exception:
                pass
        except Exception as ex:
            print('Error adding device info: ex = {!r}'.format(ex))
            device_info = str(ex)
        return device_info

    def add_device_info(self, device):
        """
        Add information about a torch device that was used in this process.

        Does nothing if telemetry is disabled.

        Args:
            device (torch.device): torch device to add info about

        Example:
            >>> # xdoctest: +REQUIRES(module:torch)
            >>> from kwutil.process_context import *
            >>> import torch
            >>> import rich
            >>> device = torch.device(0) if torch.cuda.is_available() else torch.device('cpu')
            >>> # Adding things like disk info an tracking emission usage
            >>> self = ProcessContext(track_emissions='offline')
            >>> obj1 = self.start().stop()
            >>> self.add_disk_info('.')
            >>> self.add_device_info(device)
            >>> #
            >>> # Telemetry can be mostly disabled
            >>> self = ProcessContext(track_emissions='offline', request_most_telemetry=False)
            >>> obj2 = self.start().stop()
            >>> self.add_disk_info('.')
            >>> self.add_device_info(device)
            >>> # Telemetry can be completely disabled
            >>> self = ProcessContext(track_emissions='offline', request_all_telemetry=False)
            >>> obj3 = self.start().stop()
            >>> self.add_disk_info('.')
            >>> self.add_device_info(device)
            >>> rich.print('full_telemetry = {}'.format(ub.urepr(obj1, nl=3)))
            >>> rich.print('some_telemetry = {}'.format(ub.urepr(obj2, nl=3)))
            >>> rich.print('no_telemetry = {}'.format(ub.urepr(obj3, nl=3)))
        """
        if not self.enable_most_telemetry:
            return
        self.properties['device_info'] = self._device_info(device)

    def add_disk_info(self, path):
        """
        Add information about a storage disk that was used in this process

        Does nothing if telemetry is disabled.
        """
        if not self.enable_most_telemetry:
            return
        try:
            from kwutil import util_hardware
            # Get information about disk used in this process
            disk_info = util_hardware.disk_info_of_path(path)
        except Exception as ex:
            print('ex = {!r}'.format(ex))
            print('ex = {!r}'.format(ex))
            disk_info = str(ex)
        self.properties['disk_info'] = disk_info

# def _test_offline():
#     """
#     xdoctest -m kwutil.process_context ProcessContext
#     """
#     from codecarbon import OfflineEmissionsTracker
#     emissions_tracker = OfflineEmissionsTracker(
#         country_iso_code='USA',
#         # region='Virginia',
#         region='virginia',
#         cloud_provider='aws',
#         cloud_region='us-east-1',
#         log_level='info',
#         # country_2letter_iso_code='us'
#     )
#     emissions_tracker.start()
#     emissions_tracker.stop()

#     from codecarbon import EmissionsTracker
#     emissions_tracker = EmissionsTracker(log_level='debug')
#     emissions_tracker.start()
#     emissions_tracker.stop()

#     from codecarbon.external.geography import CloudMetadata, GeoMetadata
#     geo = GeoMetadata(
#         country_iso_code="USA", country_name="United States", region="Illinois"
#     )

#     self = ProcessContext(track_emissions=True)
#     self.start()
#     self.stop()
#     _ = self.emissions_tracker._data_source.get_country_emissions_data('usa')


def jsonify_config(config):
    """
    Converts an object to a jsonifiable config as best as possible
    """
    from kwutil.util_json import Json
    if hasattr(config, 'asdict'):
        config = config.asdict()
    jsonified_config = Json.ensure_serializable(config)
    walker = ub.IndexableWalker(jsonified_config)
    for problem in Json.find_unserializable(jsonified_config):
        bad_data = problem['data']
        walker[problem['loc']] = str(bad_data)
    return jsonified_config


class Reconstruction:
    # TODO
    ...


def main():
    """
    Simple CLI to get hardware measurements that process context would provide.
    """
    # Adding things like disk info an tracking emission usage
    self = ProcessContext(track_emissions=False)
    obj = self.start().stop()
    self.add_disk_info('.')
    try:
        import torch
        if torch.cuda.is_available():
            device = torch.device(0)
            self.add_device_info(device)
    except ImportError:
        ...
    self.stop()
    print('obj = {}'.format(ub.urepr(obj, nl=3)))


# def _codecarbon_mwe():
#     from codecarbon import OfflineEmissionsTracker
#     self = OfflineEmissionsTracker(
#         country_iso_code='USA',
#         # cloud_provider='gcp',
#         # region='us-east-1',
#         # country_2letter_iso_code='us'
#     )
#     self.start()
#     self.flush()
#     emissions_data = self._prepare_emissions_data()
#     cloud = self._get_cloud_metadata()
#     df = self._data_source.get_cloud_emissions_data()


if __name__ == '__main__':
    """
    CommandLine:
        python -m kwutil.process_context
    """
    main()
