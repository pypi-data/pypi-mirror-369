# ruff: noqa: F401, E402
from __future__ import annotations


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'sasktran2.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-sasktran2-2025.8.0')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-sasktran2-2025.8.0')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("RUST_BACKTRACE", "full")

# from ._core import Geodetic

from . import (
    appconfig,
    climatology,
    constituent,
    database,
    mie,
    optical,
    solar,
    spectroscopy,
    test_util,
    util,
    viewinggeo,
)
from ._core_rust import (
    EmissionSource,
    GeometryType,
    InputValidationMode,
    InterpolationMethod,
    LogLevel,
    MultipleScatterSource,
    OccultationSource,
    SingleScatterSource,
    StokesBasis,
    ThreadingLib,
    ThreadingModel,
)
from .atmosphere import Atmosphere
from .config import Config
from .engine import Engine
from .geodetic import WGS84, Geodetic, SphericalGeoid
from .geometry import Geometry1D
from .viewinggeo.wrappers import (
    GroundViewingSolar,
    SolarAnglesObserverLocation,
    TangentAltitudeSolar,
    ViewingGeometry,
)
