import platform
import fnmatch
import os
import sys

def get_flags_from_int(value, enum):
    set_flags = [flag for flag in enum if value & flag.value]
    return set_flags

def find_latest_version_folder_in_path(path: str, aimms_version: str = None) -> list:
    if not os.path.exists(path):
        raise FileNotFoundError(f"The specified path does not exist: {path}")

    # List directories that match the version pattern
    if not aimms_version:
        # If no version is specified, find the latest version
        version_dirs = [d for d in os.listdir(path)]
    else:
        version_dirs = [d for d in os.listdir(path) if d.startswith(aimms_version)]

    if not version_dirs:
        raise FileNotFoundError(f"AIMMS version {aimms_version} not found in {path}")    

    # strip of the platform and compiler information
    versions = [d.split('-')[0] for d in version_dirs]

    if not versions:
        raise FileNotFoundError(f"No valid AIMMS version directories found in {path}")
    
    # order them by latest version
    versions.sort(key=lambda x: tuple(map(int, x.split('.'))), reverse=True)

    # find again the exact folder, based upon the resolved version
    version_dirs = [d for d in os.listdir(path) if d.startswith(versions[0])]
    if not version_dirs:
        raise FileNotFoundError(f"No valid AIMMS version directories found in {path} for resolved version {versions[0]}")

    return os.path.join(path, version_dirs[0])

# determine the path to the AIMMS executable by looking for the aimms folder
# based on the given version number
def find_aimms_path(aimms_version: str = None) -> str:
    """
    Finds the path to the AIMMS executable based on the given version number.

    Args:
        aimms_version (str): The version of AIMMS to find. If None, it will look for the default installation path on Linux.

    Returns:
        str: The path to the folder that contains libaimms3.dll or libaimms3.so.
    """
    aimms_folder = None
    if not aimms_version and platform.system() == "Linux":
        # check if /usr/local/Aimms/Lib exists
        default_folder = os.path.join("/usr", "local", "Aimms", "Lib")
        if os.path.exists(default_folder):
            aimms_folder = default_folder
        else:
            raise FileNotFoundError("AIMMS version not specified and /usr/local/Aimms/Lib does not exist.")
    elif platform.system() == "Windows":
        base_path = os.path.join(os.getenv("LOCALAPPDATA"), "AIMMS", "IFA", "Aimms")

        aimms_folder = os.path.join(find_latest_version_folder_in_path(base_path, aimms_version), "Bin")
    else:
        base_path = os.path.join(os.getenv("HOME"), ".Aimms")
        
        aimms_folder = os.path.join(find_latest_version_folder_in_path(base_path, aimms_version), "Lib")
    
    # Check if the dynamic library exists
    if platform.system() == "Windows":
        lib_name = "libaimms3.dll"
    else:
        lib_name = "libaimms3.so"
    lib_path = os.path.join(aimms_folder, lib_name)
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"AIMMS dynamic library {lib_name} not found in {aimms_folder}")
    return aimms_folder

def show_dependencies():
    """
    Prints the versions of all imported modules that have a __version__ attribute.
    """
    for name, module in sys.modules.items():
        if hasattr(module, '__version__'):
            if "." not in name and not name.startswith("_"):
                print(f"{name}: {module.__version__}")

if __name__ == "__main__":
    # Example usage
    try:
        if len(os.sys.argv) > 1:
            aimms_version = os.sys.argv[1]
        else:
            aimms_version = None
        aimms_path = find_aimms_path(aimms_version)
        print(f"AIMMS path found: {aimms_path}")
    except FileNotFoundError as e:
        print(e)