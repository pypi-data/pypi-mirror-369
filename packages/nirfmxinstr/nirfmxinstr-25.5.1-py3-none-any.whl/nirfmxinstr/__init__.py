"""nirfmxinstr package."""

__version__ = "25.5.1"

from nirfmxinstr.attributes import *  # noqa: F403
from nirfmxinstr.enums import *  # noqa: F403
from nirfmxinstr.errors import Error, RFmxError
from nirfmxinstr.session import Session


def get_diagnostic_information():
    """Get diagnostic information about the system state that is suitable for printing or logging.
    returns: dict
    note: Python bitness may be incorrect when running in a virtual environment.
    """
    import importlib.metadata
    import os
    import platform
    import struct
    import sys

    def is_python_64bit():
        return struct.calcsize("P") == 8

    def is_os_64bit():
        return platform.machine().endswith("64")

    def is_venv():
        return "VIRTUAL_ENV" in os.environ

    info = {}  # type: ignore
    info["os"] = {}
    info["python"] = {}
    info["driver"] = {}
    info["module"] = {}
    if platform.system() == "Windows":
        try:
            import winreg as winreg
        except ImportError:
            import _winreg as winreg  # type: ignore

        os_name = "Windows"
        try:
            driver_version_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\National Instruments\RFmx\RFInstr\C Runtime Support")  # type: ignore
            driver_version = winreg.QueryValueEx(driver_version_key, "Version")[0]  # type: ignore
        except WindowsError:  # type: ignore
            driver_version = "Unknown"
    else:
        raise SystemError("Unsupported platform: {}".format(platform.system()))

    if sys.version_info[1] >= 10:
        installed_packages_names = [
            name
            for name_list in importlib.metadata.packages_distributions().values()
            for name in name_list
        ]
        installed_packages_names = set(installed_packages_names)  # type: ignore
        installed_packages_list = [
            {"name": name, "version": importlib.metadata.distribution(name).version}
            for name in sorted(installed_packages_names)
        ]
    else:
        import pkg_resources

        installed_packages = pkg_resources.working_set
        installed_packages_list = [
            {
                "name": i.key,
                "version": i.version,
            }
            for i in installed_packages
        ]

    info["os"]["name"] = os_name
    info["os"]["version"] = platform.version()
    info["os"]["bits"] = "64" if is_os_64bit() else "32"  # type: ignore
    info["driver"]["name"] = "NI-RFmxInstr"
    info["driver"]["version"] = driver_version
    info["module"]["name"] = "nirfmxinstr"
    info["module"]["version"] = "25.5.1"
    info["python"]["version"] = sys.version
    info["python"]["bits"] = "64" if is_python_64bit() else "32"  # type: ignore
    info["python"]["is_venv"] = is_venv()  # type: ignore
    info["python"]["packages"] = installed_packages_list

    return info


def print_diagnostic_information():
    """Print diagnostic information in a format suitable for issue report.
    note: Python bitness may be incorrect when running in a virtual environment.
    """
    info = get_diagnostic_information()  # type: ignore

    row_format = "    {:<10"
    for type in ["OS", "Driver", "Module", "Python"]:
        typename = type.lower()
        print(type + ":")
        for item in info[typename]:
            if item != "packages":
                print(row_format.format(item.title() + ":", info[typename][item]))
    print("    Installed Packages:")
    for p in info["python"]["packages"]:
        print((" " * 8) + p["name"] + "==" + p["version"])

    return info
