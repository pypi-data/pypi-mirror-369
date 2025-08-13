import os
import sys
import platform
import subprocess
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class CustomBuildExt(build_ext):
    """Custom build extension to handle OpenMP configuration."""

    def build_extensions(self):
        # Detect platform
        system = platform.system()
        machine = platform.machine()

        # Get compiler
        compiler = self.compiler.compiler_type

        print(f"Building for {system} {machine} with {compiler}")

        for ext in self.extensions:
            # Platform-specific configuration
            if system == "Darwin":  # macOS
                self._configure_macos(ext, machine)
            elif system == "Linux":
                self._configure_linux(ext)
            elif system == "Windows":
                self._configure_windows(ext, compiler)
            else:
                raise RuntimeError(f"Unsupported platform: {system}")

            # Print final configuration for debugging
            print(f"Compile args: {ext.extra_compile_args}")
            print(f"Link args: {ext.extra_link_args}")

        # Call parent build_extensions
        super().build_extensions()

    def _configure_macos(self, ext, machine):
        """Configure for macOS with OpenMP support."""
        # Base flags
        ext.extra_compile_args = ['-std=c++11', '-O3', '-fPIC', '-D LINUX']
        ext.extra_link_args = []  # Don't add -shared on macOS, Python adds -bundle automatically

        # Try to find OpenMP
        omp_found = False

        # Check common OpenMP locations
        possible_paths = [
            '/opt/homebrew/opt/libomp',  # ARM64 Homebrew
            '/usr/local/opt/libomp',  # Intel Homebrew
            '/opt/local',  # MacPorts
        ]

        # Also check conda environment
        conda_prefix = os.environ.get('CONDA_PREFIX')
        if conda_prefix:
            possible_paths.insert(0, conda_prefix)

        for base_path in possible_paths:
            lib_path = os.path.join(base_path, 'lib')
            inc_path = os.path.join(base_path, 'include')

            # Check if libomp exists in this location
            if os.path.exists(lib_path) and os.path.exists(inc_path):
                # Check for libomp specifically
                if any('omp' in f for f in os.listdir(lib_path)):
                    print(f"Found OpenMP at {base_path}")
                    ext.extra_compile_args.extend([
                        '-Xpreprocessor', '-fopenmp',
                        f'-I{inc_path}'
                    ])
                    ext.extra_link_args.extend([
                        '-lomp',
                        f'-L{lib_path}',
                        f'-Wl,-rpath,{lib_path}'  # Add rpath to avoid runtime issues
                    ])
                    omp_found = True
                    break

        if not omp_found:
            # Try to detect if libomp is in standard paths
            try:
                # Try to compile a simple OpenMP program
                result = subprocess.run(
                    ['clang++', '-Xpreprocessor', '-fopenmp', '-lomp', '-x', 'c++', '-', '-o', '/dev/null'],
                    input=b'#include <omp.h>\nint main() { return omp_get_num_threads(); }',
                    capture_output=True
                )
                if result.returncode == 0:
                    print("OpenMP found in standard paths")
                    ext.extra_compile_args.extend(['-Xpreprocessor', '-fopenmp'])
                    ext.extra_link_args.append('-lomp')
                    omp_found = True
            except:
                pass

        if not omp_found:
            print("\n" + "=" * 60)
            print("WARNING: OpenMP not found!")
            print("Please install OpenMP using one of:")
            print("  brew install libomp")
            print("  conda install openmp")
            print("  port install libomp")
            print("=" * 60 + "\n")

            # Option 1: Fail the build
            raise RuntimeError("OpenMP is required but not found. Please install it first.")

            # Option 2: Build without OpenMP (comment out the raise above and uncomment below)
            # print("Building without OpenMP support (single-threaded)")
            # ext.define_macros.append(('NO_OPENMP', '1'))

    def _configure_linux(self, ext):
        """Configure for Linux with OpenMP support."""
        ext.extra_compile_args = ['-std=c++11', '-O3', '-fPIC', '-D LINUX', '-fopenmp']
        ext.extra_link_args = ['-shared', '-fopenmp']

        # Check if OpenMP is available
        try:
            result = subprocess.run(
                ['g++', '-fopenmp', '-x', 'c++', '-', '-o', '/dev/null'],
                input=b'#include <omp.h>\nint main() { return omp_get_num_threads(); }',
                capture_output=True
            )
            if result.returncode != 0:
                print("WARNING: OpenMP test compilation failed")
                print("Make sure gcc/g++ with OpenMP support is installed")
        except:
            print("WARNING: Could not test OpenMP availability")

    # def _configure_windows(self, ext, compiler):
    #     """Configure for Windows with OpenMP support."""
    #     if compiler == 'msvc':
    #         ext.extra_compile_args = ['/O2', '/openmp', '/D WINDOWS']
    #         ext.extra_link_args = []
    #     elif compiler == 'mingw32':
    #         ext.extra_compile_args = ['-std=c++11', '-O3', '-D WINDOWS', '-fopenmp']
    #         ext.extra_link_args = ['-fopenmp']
    #     else:
    #         raise RuntimeError(f"Unsupported Windows compiler: {compiler}")

    def _configure_windows(self, ext, compiler):
        """Configure for Windows with OpenMP support."""
        if compiler == 'msvc':
            # Microsoft Visual C++ uses different flag syntax
            ext.extra_compile_args = ['/O2', '/openmp', '/D', 'WINDOWS']
            ext.extra_link_args = []  # MSVC handles OpenMP linking automatically
        elif compiler == 'mingw32':
            # MinGW uses GCC-style flags
            ext.extra_compile_args = ['-std=c++11', '-O3', '-D WINDOWS', '-fopenmp']
            ext.extra_link_args = ['-fopenmp']
        else:
            # Default to MSVC style
            ext.extra_compile_args = ['/O2', '/D', 'WINDOWS']
            ext.extra_link_args = []
            print("WARNING: Unknown compiler, OpenMP may not be enabled")


# Define the extension module
# def get_extension():
#     """Create the C++ extension with all source files."""
#
#     # Use the actual directory name
#     source_dir = Path('pygsfit/src_gyrosynchrotron')
#
#     # List all source files (excluding Windows-specific dllmain.cpp)
#     sources = [
#         'Arr_DF.cpp',
#         'Coulomb.cpp',
#         'ExtMath.cpp',
#         'FF.cpp',
#         'getparms.cpp',
#         'GS.cpp',
#         'IDLinterface.cpp',
#         'PythonInterface.cpp',
#         'Messages.cpp',
#         'MWmain.cpp',
#         'Plasma.cpp',
#         'Std_DF.cpp',
#         'Zeta.cpp'
#     ]
#
#     # Convert to full paths
#     source_files = [str(source_dir / src) for src in sources]
#
#     # Verify source files exist
#     missing = [f for f in source_files if not os.path.exists(f)]
#     if missing:
#         print(f"WARNING: Missing source files: {missing}")
#         print("Make sure all C++ source files are in pygsfit/src_gyrosynchrotron/")
#
#     # Create extension
#     ext = Extension(
#         'pygsfit.MWTransferArr',  # This will create pygsfit/MWTransferArr.so
#         sources=source_files,
#         include_dirs=[str(source_dir)],  # For header files
#         language='c++'
#     )
#
#     return ext


def get_extension():
    """Create the C++ extension with all source files."""

    # Use the actual directory name
    source_dir = Path('pygsfit/src_gyrosynchrotron')

    # List all source files (excluding Windows-specific dllmain.cpp)
    sources = [
        'Arr_DF.cpp',
        'Coulomb.cpp',
        'ExtMath.cpp',
        'FF.cpp',
        'getparms.cpp',
        'GS.cpp',
        'IDLinterface.cpp',
        'PythonInterface.cpp',
        'Messages.cpp',
        'MWmain.cpp',
        'Plasma.cpp',
        'Std_DF.cpp',
        'Zeta.cpp'
    ]

    # Convert to full paths
    source_files = [str(source_dir / src) for src in sources]

    # Create extension with a SIMPLE, PREDICTABLE NAME
    ext = Extension(
        'pygsfit.binaries.MWTransferArr_compiled_local',  # This creates MWTransferArr_compiled.so
        sources=source_files,
        include_dirs=[str(source_dir)],
        language='c++'
    )

    return ext


# Setup configuration
setup(
    ext_modules=[get_extension()],
    cmdclass={'build_ext': CustomBuildExt},
)