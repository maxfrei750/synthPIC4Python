import os
import urllib.request
import shutil
import platform
from utilities import execute_and_print


def is_os_64bit():
    return platform.machine().endswith("64")


def get_os_architecture():
    if is_os_64bit:
        return "64"
    else:
        return "32"


def get_os_name():
    if os.name == "nt":  # Windows
        return "windows"
    elif os.name == "posix":  # Linux
        return "linux"
    else:
        raise OSError("Unsupported operating system. Only Windows and Linux are supported.")


def get_blender_version_number_string():
    return "2.80"


def get_blender_version_string():
    os_architecture = get_os_architecture()
    os_name = get_os_name()
    blender_version_number = get_blender_version_number_string()

    blender_version_base = "blender-"

    if os_name == "windows":
        blender_version_suffix = os_name + os_architecture
    elif os_name == "linux":
        if os_architecture == "32":
            blender_version_suffix = os_name + "-glibc224-i686"
        elif os_architecture == "64":
            blender_version_suffix = os_name + "-glibc217-x86_" + os_architecture

    return blender_version_base + blender_version_number + "-" + blender_version_suffix


def get_external_module_folder():
    self_folder = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(self_folder, "external")


def get_blender_executable_path():
    blender_path_base = get_external_module_folder()
    blender_version_string = get_blender_version_string()
    os_name = get_os_name()

    if os_name == "windows":
        blender_filename = "blender.exe"
    elif os_name == "linux":
        blender_filename = "blender"

    return os.path.join(blender_path_base, blender_version_string, blender_filename)


def get_blender_python_folder():
    external_module_folder = get_external_module_folder()
    blender_version_string = get_blender_version_string()
    blender_version_number_string = get_blender_version_number_string()

    return os.path.join(external_module_folder, blender_version_string, blender_version_number_string, "python")


def get_blender_python_executable_path():
    blender_python_folder = get_blender_python_folder()

    os_name = get_os_name()

    if os_name == "windows":
        python_filename = "python.exe"
    elif os_name == "linux":
        python_filename = "python"

    return os.path.join(blender_python_folder, "bin", python_filename)


def install_dependencies():
    blender_python_executable_path = get_blender_python_executable_path()
    blender_python_folder = get_blender_python_folder()

    print("Setting up the python of blender.")

    print("Install and upgrade pip.")
    execute_and_print([blender_python_executable_path, "-m", "ensurepip"])
    execute_and_print([blender_python_executable_path, "-m", "pip", "install", "-U", "pip"])

    print("Fix numpy.")
    execute_and_print([blender_python_executable_path, "-m", "pip", "uninstall", "--yes", "numpy"])
    numpy_path = os.path.join(blender_python_folder, "lib", "site-packages", "numpy")
    shutil.rmtree(numpy_path, ignore_errors=True)
    execute_and_print([blender_python_executable_path, "-m", "pip", "install", "--no-warn-script-location", "numpy"])

    print("Install trimesh.")
    execute_and_print([blender_python_executable_path, "-m", "pip", "install", "trimesh"])

    print("Successfully installed all dependencies.")


def download_blender():
    os_name = get_os_name()
    blender_version_string = get_blender_version_string()
    blender_version_number_string = get_blender_version_number_string()

    if os_name == "windows":
        archive_extension = ".zip"
    elif os_name == "linux":
        archive_extension = ".tar.bz2"

    url_base = "https://ftp.halifax.rwth-aachen.de/blender/release/Blender" + blender_version_number_string + "/"

    url = url_base + blender_version_string + archive_extension

    archive_folder = get_external_module_folder()
    archive_path = os.path.join(archive_folder, blender_version_string + archive_extension)

    print("Downloading Blender...")
    urllib.request.urlretrieve(url, archive_path)
    print("Finished.")

    print("Extracting archive...")
    shutil.unpack_archive(archive_path, archive_folder)
    print("Finished.")

    print("Deleting archive...")
    os.remove(archive_path)
    print("Finished.")


if __name__ == "__main__":
    download_blender()
    install_dependencies()