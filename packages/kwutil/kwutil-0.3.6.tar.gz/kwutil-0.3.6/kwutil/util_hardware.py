"""
Helpers to get information about the available hardware. Request info about
things like cpus, gpus, memory, and disk.

Backed by external modules:

    * :mod:`cpuinfo`.
    * :mod:`psutil`.
    * and various linux cli calls via :func:`ubelt.cmd`.
"""
import ubelt as ub

# Used in: ./process_context.py


def get_cpu_mem_info():
    cpu_info = get_cpu_info()
    mem_info = get_mem_info()
    system_info = {
        'cpu_info': cpu_info,
        'mem_info': mem_info,
    }
    return system_info


def get_cpu_info():
    import cpuinfo
    cpu_info = cpuinfo.get_cpu_info()
    return cpu_info


def get_mem_info(with_units=False):
    """
    Memory info is returned in bytes.

    TODO:
        - [ ] Should we use pint to give these numbers units?

    References:
        https://psutil.readthedocs.io/en/latest/#psutil.virtual_memory

    Example:
        >>> # xdoctest: +REQUIRES(module:psutil)
        >>> from kwutil import util_hardware
        >>> import ubelt as ub
        >>> mem_info = util_hardware.get_mem_info(with_units=1)
        >>> print(f'mem_info = {ub.urepr(mem_info, nl=1)}')

        total = mem_info['used']
        tmp = (
            # mem_info['cached'] +
            # mem_info['buffers'] +
            # mem_info['inactive'] +
            mem_info['slab'])
        green = total - tmp
        print(f'green={green}')
        percent = ((green / mem_info['total']) * 100).m
        print(f'percent={percent}')
    """
    import psutil
    svmem_info = psutil.virtual_memory()
    mem_info = dict(zip(svmem_info._fields, svmem_info))

    if 0:
        # Measure memory used by this process and its children
        import psutil
        import os
        this_process = psutil.Process(os.getpid())
        this_total_pcnt = 0
        this_total_pcnt += this_process.memory_percent()
        for child in this_process.children():
            this_total_pcnt += child.memory_percent()

    if 0:
        # Measure memory explicitly used by userland processes
        total_vms = 0
        total_pcnt = 0
        for proc in psutil.process_iter():
            total_pcnt += proc.memory_percent()
            total_vms += proc.memory_info().vms

    if with_units:
        from kwutil import util_units
        ureg = util_units.unit_registry()
        bytes_keys = [
            'total', 'available', 'used', 'free', 'active', 'inactive',
            'buffers', 'cached', 'shared', 'slab', 'wired',
        ]
        for key in bytes_keys:
            if key in mem_info:
                mem_info[key] = (mem_info[key] * ureg.bytes).to('gigabytes')
    return mem_info


def disk_info_of_path(path):
    """
    Get disk info wrt where a file lives

    WIP - needs more work

    CommandLine:
        xdoctest -m kwutil.util_hardware disk_info_of_path

    Returns:
        dict - dictionary of information

    Example:
        >>> from kwutil.util_hardware import *  # NOQA
        >>> path = '.'
        >>> x = disk_info_of_path(path)
        >>> import ubelt as ub
        >>> print(ub.urepr(x))

    TODO:
        - [ ] Handle btrfs
        - [ ] Handle whatever AWS uses
        - [ ] Use udisksctl or udevadm

    Ignore:
        lsblk  /dev/nvme1n1
        lsblk -afs /dev/mapper/vgubuntu-root
        lsblk -nasd /dev/mapper/vgubuntu-root

        df $HOME --output=source,fstype
        df $HOME/data/dvc-repos/smart_watch_dvc --output=source,fstype
        df $HOME/data/dvc-repos/smart_watch_dvc-hdd --output=source,fstype

        df . --output=source,fstype,itotal,iused,iavail,ipcent,size,used,avail,pcent,file,target

    References:
        https://askubuntu.com/questions/609708/how-to-find-hard-drive-brand-name-or-model
        https://stackoverflow.com/questions/38615464/how-to-get-device-name-on-which-a-file-is-located-from-its-path-in-c
    """
    import ubelt as ub
    import os
    path = ub.Path(path)
    path = path.resolve()
    # Returns the lvm name: e.g.
    # Filesystem     Type
    # data           zfs
    # /dev/sde1      ext4
    # /dev/md0       ext4
    # /dev/mapper/vgubuntu-root ext4
    # /dev/nvme1n1              f2fs
    info = ub.cmd(f'df {path} --output=source,fstype', check=True)
    parts = info['out'].split('\n')[1].rsplit(' ', 1)
    source, filesystem = [p.strip() for p in parts]

    hwinfo = {
        'path': os.fspath(path),
        'source': source,
        'filesystem': filesystem,
    }

    if filesystem == 'zfs':
        # Use ZFS to get more information
        # info = ub.cmd(f'zpool list {source}', verbose=3)
        # info = ub.cmd(f'zpool iostat {source}', verbose=3)
        # info = ub.cmd(f'zpool list -H {source}', verbose=3)
        # info = ub.cmd(f'zpool iostat -H {source}', verbose=3)
        try:
            zfs_status = _zfs_status(source)
            hwinfo['hwtype'] = zfs_status['coarse_type']
        except Exception as ex:
            print('error in zfs stuff: ex = {}'.format(ub.urepr(ex, nl=1)))
    elif filesystem == 'overlay':
        # This is the case on AWS. lsblk isnt able to provide us with more info
        # I'm not sure how to determine more info.
        # References:
        # https://docs.kernel.org/filesystems/overlayfs.html
        ...
    else:
        try:
            if _device_is_hdd(source):
                hwinfo['hwtype'] = 'hdd'
            else:
                hwinfo['hwtype'] = 'ssd'
        except Exception as ex:
            print('warning: unable to infer disk info: ex = {}'.format(ub.urepr(ex, nl=1)))

    try:
        import json
        info = ub.cmd(f'lsblk -as {source} --json')
        lsblk_info = json.loads(info['out'])
        walker = ub.IndexableWalker(lsblk_info)
        names = []
        for path, item in walker:
            if isinstance(item, dict):
                if 'name' in item:
                    names.append(item['name'])
        hwinfo['names'] = names
    except Exception:
        pass
    # print(ub.Path('/proc/partitions').read_text())
    return hwinfo


def _device_is_hdd(path):
    import ubelt as ub
    import json
    info = ub.cmd(f'lsblk -as {path} --json -o name,rota')
    info.check_returncode()
    lsblk_info = json.loads(info['out'])
    walker = ub.IndexableWalker(lsblk_info)
    rotas = []
    for path, item in walker:
        if isinstance(item, dict):
            if 'rota' in item:
                rotas.append(item['rota'])
    return any(rotas)


def _zfs_status(pool, verbose=0):
    """
    Semi-parsable zfs status output.  This is a proof-of-concept and needs some
    work to handle the nested pool structure.
    """
    import ubelt as ub
    import re
    info = ub.cmd(f'zpool status {pool} -P', verbose=verbose)
    info.check_returncode()

    splitter = re.compile(r'\s+')

    config = ub.ddict(list)
    context = None
    state = None
    header = None
    # stack = [] todo

    for line in info.stdout.split('\n'):
        indentation = line[:len(line) - len(line.lstrip())]
        if not line.strip():
            continue
        if state is None:
            if line.strip() == 'config:':
                state = 'CONFIG'
        elif state == 'CONFIG':
            parts = splitter.split(line.strip())
            if parts[0] == 'NAME':
                state = 'NAME'
                header = parts
        elif state == 'NAME':
            if len(indentation) == 1:
                parts = splitter.split(line.strip())
                row = ub.dzip(header, parts)
                name = parts[0]
                row['children'] = []
                context = config[name] = row
            elif len(indentation) > 1:
                parts = splitter.split(line.strip())
                row = ub.dzip(header, parts)
                context['children'].append(row)
            else:
                state = None

    # hack to get the data we currently need
    dev_paths = []
    for row in config[pool]['children']:
        if row['NAME'].startswith('/dev'):
            dev_paths.append(row['NAME'])

    is_part_hdd = []
    for path in dev_paths:
        flag = _device_is_hdd(path)
        is_part_hdd.append(flag)

    if all(is_part_hdd):
        coarse_type = 'hdd'
    elif not any(is_part_hdd):
        coarse_type = 'ssd'
    else:
        coarse_type = 'mixed'

    output = {
        'coarse_type': coarse_type,
        'poc_config': config,
    }

    # print('records = {}'.format(ub.urepr(config, nl=True)))
    return output


def _torch_device_info(device):
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


# The following classes are experimental and we are avoiding any signature
# definition that would limit the use of these names in the future in order to
# iterate towards a good design. The initial constructor will be called
# _discover_v1

class _HardwareComponent(ub.NiceRepr):

    def __nice__(self):
        import kwutil
        return kwutil.Yaml.dumps(self.summary())

    def summary(self):
        """
        Concise summary of most important information.
        """
        raise NotImplementedError('abstract method')


class CPUs(_HardwareComponent):
    """
    Storage container for info about system CPUs.
    """
    def __init__(self):
        self._cpu_info = None

    def summary(self):
        return {
            'brand': self._cpu_info['brand_raw'],
            'num_cores': self._cpu_info['count'],
        }

    @classmethod
    def _discover_v1(cls):
        self = cls()
        self._cpu_info = get_cpu_info()
        return self


class Memory(_HardwareComponent):
    """
    Storage container for info about system RAM.
    """
    def __init__(self):
        self._memory_info = None

    def summary(self):
        import kwutil
        total_gb = (self._memory_info['total'] * kwutil.util_units.ureg.bytes).to('gibibyte')
        return {
            'total_gb': total_gb.m,
        }

    @classmethod
    def _discover_v1(Memory):
        self = Memory()
        self._memory_info = get_mem_info()
        return self


class GPUs(_HardwareComponent):
    """
    Storage container for info about system GPUS.
    """
    def __init__(self):
        self._num_gpus = None
        self._device_infos = None

    def summary(self):
        return {
            'count': self._num_gpus,
            'models': self._gpu_model_freq,
        }

    @classmethod
    def _discover_v1(cls):
        self = cls()
        import torch
        _num_gpus = torch.cuda.device_count()
        device_infos = []
        for idx in range(_num_gpus):
            device = torch.device(idx)
            info = _torch_device_info(device)
            device_infos.append(info)
        gpu_model_freq = ub.dict_hist([d['device_name'] for d in device_infos])
        self._gpu_model_freq = gpu_model_freq
        self._num_gpus = _num_gpus
        self._device_infos = device_infos
        return self


class Motherboard(_HardwareComponent):
    """
    Storage container for info about system motherboard.

    References:
        https://askubuntu.com/questions/179958/how-do-i-find-out-my-motherboard-model
    """
    def __init__(self):
        self._dmi_info = None

    def summary(self):
        return {
            'name': self._dmi_info['board_name'],
        }

    @classmethod
    def _discover_v1(cls):
        self = cls()
        # TODO: dmidecode variant, but requires sudo
        self._dmi_info = cls._discover_dmi_info_linux_non_admin()
        return self

    def _discover_dmi_info_linux_non_admin():
        # Try to discover infow without admin
        import ubelt as ub
        dpath = ub.Path('/sys/devices/virtual/dmi/id/')
        dmi_info = {}
        for board_info_fpath in list(dpath.glob('board_*')):
            try:
                dmi_info[board_info_fpath.name] = board_info_fpath.read_text()
            except PermissionError as ex:
                dmi_info[board_info_fpath.name] = ex
        print(f'info = {ub.urepr(dmi_info, nl=1)}')
        return dmi_info


class Disks(_HardwareComponent):
    """
    Storage container for info about system storage disks.

    TODO:
        Find all mounted filesystems that correspond with physical disks
        via ``cat /proc/mounts`` or ``mount -l``

    References:
        https://unix.stackexchange.com/questions/24182/how-to-get-the-complete-and-exact-list-of-mounted-filesystems-in-linux
    """
    def __init__(self):
        self._hardware_diskinfo = None

    def summary(self):
        return {
            'num_disks': self._total_disks,
        }

    @classmethod
    def _discover_v1(Disks):
        import hardware.diskinfo
        self = Disks()
        _tupinfo = hardware.diskinfo.detect()
        self._hardware_diskinfo = _tup_to_nested(_tupinfo)['disk']
        self._total_disks = self._hardware_diskinfo['logical']['count']
        return self


class Networking(_HardwareComponent):
    """
    Storage container for info about system networking devices.
    """
    def __init__(self):
        self._hardware_network_info = None

    def summary(self):
        return {
            'num_network_devices': self._num_network_devices,
        }

    @classmethod
    def _discover_v1(Networking):
        self = Networking()
        nested_info = _hardware_nested_system_info()
        self._hardware_network_info = nested_info['network']
        self._num_network_devices = len(self._hardware_network_info)
        return self


class Peripherals(_HardwareComponent):
    """
    Storage container for info about system peripherals.
    """
    def __init__(self):
        raise NotImplementedError()

    @classmethod
    def _discover_v1(Peripherals):
        self = Peripherals()
        return self


def _hardware_nested_system_info():
    from hardware import system
    _hardware_sysinfo = system.detect()
    nested_info = _tup_to_nested(_hardware_sysinfo)
    return nested_info


def _tup_to_nested(tuples):
    nested_info = {}
    for tup in tuples:
        *path, value = tup
        curr = nested_info
        for p in path[:-1]:
            if p not in curr:
                curr[p] = {}
            curr = curr[p]
        final = path[-1]
        curr[final] = value
    return nested_info


class Hardware:
    """
    TODO: class level namespace

    References:
        https://pypi.org/project/hardware/

    Example:
        >>> # xdoctest: +SKIP
        >>> import kwutil
        >>> kwutil.Hardware.report()
    """

    @staticmethod
    def report():
        """
        Build a high level hardware report
        """
        components = {}
        components['cpus'] = Hardware.cpus()
        components['memory'] = Hardware.memory()
        components['gpus'] = Hardware.gpus()
        components['disks'] = Hardware.disks()
        components['motherboard'] = Hardware.motherboard()
        components['networking'] = Hardware.networking()
        print(f'components = {ub.urepr(components, nl=2)}')

    @staticmethod
    def cpus():
        return CPUs._discover_v1()

    @staticmethod
    def memory():
        return Memory._discover_v1()

    @staticmethod
    def gpus():
        return GPUs._discover_v1()

    @staticmethod
    def disks():
        return Disks._discover_v1()

    @staticmethod
    def motherboard():
        return Motherboard._discover_v1()

    @staticmethod
    def networking():
        return Networking._discover_v1()

    @staticmethod
    def peripherals():
        return Peripherals._discover_v1()
