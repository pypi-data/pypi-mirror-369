##############################################################################
# Copyright (c) 2024, NVIDIA Corporation. All rights reserved.
#
# This work is made available under the Nvidia Source Code License-NC.
# To view a copy of this license, visit
# https://nvlabs.github.io/gbrl/license.html
#
##############################################################################


# start delvewheel patch
def _delvewheel_patch_1_10_0():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'gbrl.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-gbrl-1.1.1')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-gbrl-1.1.1')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_10_0()
del _delvewheel_patch_1_10_0
# end delvewheel patch

__version__ = "1.1.1"

import importlib.util
import os
import platform
import sys

_loaded_cpp_module = None


def load_cpp_module():
    global _loaded_cpp_module
    module_name = "gbrl_cpp"
    python_version = (f"cpython-{sys.version_info.major}"
                      f"{sys.version_info.minor}")
    python_version_short = (f"cp{sys.version_info.major}"
                            f"{sys.version_info.minor}")

    if platform.system() == "Windows":
        ext = ".pyd"
    elif platform.system() == "Darwin":  # macOS
        ext = ".dylib"
    else:  # Assume Linux/Unix
        ext = ".so"
    possible_paths = [
        os.path.join(os.path.dirname(__file__)),  # Current directory
        os.path.join(os.path.dirname(__file__), "Release"),  # Release folder
    ]

    for dir_path in possible_paths:
        if os.path.exists(dir_path):
            # Scan for files that match the module name and extension
            for file_name in os.listdir(dir_path):
                if file_name.startswith(module_name) and \
                    file_name.endswith(ext) and \
                    (python_version in file_name or
                        python_version_short in file_name):
                    # Dynamically load the matching shared library
                    file_path = os.path.join(dir_path, file_name)
                    spec = importlib.util.spec_from_file_location(module_name,
                                                                  file_path)
                    module = importlib.util.module_from_spec(spec)  # type: ignore
                    spec.loader.exec_module(module)  # type: ignore
                    _loaded_cpp_module = module = module
                    return module

    if platform.system() == "Darwin":  # check for .so on Darwin
        ext = ".so"
        for dir_path in possible_paths:
            if os.path.exists(dir_path):
                # Scan for files that match the module name and extension
                for file_name in os.listdir(dir_path):
                    if file_name.startswith(module_name) and \
                        file_name.endswith(ext) and (python_version in
                                                     file_name or
                                                     python_version_short
                                                     in file_name):
                        # Dynamically load the matching shared library
                        file_path = os.path.join(dir_path, file_name)
                        spec = importlib.util.spec_from_file_location(
                            module_name, file_path)
                        module = importlib.util.module_from_spec(spec)  # type: ignore
                        spec.loader.exec_module(module)  # type: ignore
                        _loaded_cpp_module = module = module
                        return module
    raise ImportError(f"Could not find {module_name}{ext} in any of the"
                      f"expected locations: {possible_paths}")


# Load the C++ module dynamically
_gbrl_cpp_module = load_cpp_module()

# Create a global alias for the GBRL class
GBRL_CPP = _gbrl_cpp_module.GBRL

cuda_available = GBRL_CPP.cuda_available
