import os
import platform
import shutil
import urllib.request

from system_utilities import execute_and_print


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
        raise OSError(
            "Unsupported operating system. Only Windows and Linux are supported."
        )


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
            blender_version_suffix = (
                os_name + "-glibc217-x86_" + os_architecture
            )

    return (
        blender_version_base
        + blender_version_number
        + "-"
        + blender_version_suffix
    )


def get_external_module_folder_path():
    self_folder = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(self_folder, "external")


def get_blender_executable_path():
    blender_folder_path = get_blender_folder_path()
    os_name = get_os_name()

    if os_name == "windows":
        blender_filename = "blender.exe"
    elif os_name == "linux":
        blender_filename = "blender"

    return os.path.join(blender_folder_path, blender_filename)


def get_blender_python_folder_path():
    blender_folder_path = get_blender_folder_path()
    blender_version_number_string = get_blender_version_number_string()

    return os.path.join(
        blender_folder_path, blender_version_number_string, "python",
    )


def get_blender_python_executable_path():
    blender_python_folder = get_blender_python_folder_path()

    os_name = get_os_name()

    if os_name == "windows":
        python_filename = "python.exe"
    elif os_name == "linux":
        python_filename = "python3.7m"

    return os.path.join(blender_python_folder, "bin", python_filename)


def install_dependencies():
    os_name = get_os_name()

    blender_python_executable_path = get_blender_python_executable_path()
    requirement_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "requirements.txt"
    )

    print("Installing dependencies...")

    execute_and_print([blender_python_executable_path, "-m", "ensurepip"])
    execute_and_print(
        [
            blender_python_executable_path,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "setuptools",
            "wheel",
        ]
    )

    if os_name == "linux":
        numpy_folder = os.path.join(
            get_blender_python_folder_path(),
            "lib",
            "python3.7",
            "site-packages",
            "numpy",
        )
    elif os_name == "windows":
        numpy_folder = os.path.join(
            get_blender_python_folder_path(), "lib", "site-packages", "numpy"
        )

    shutil.rmtree(numpy_folder)

    execute_and_print(
        [
            blender_python_executable_path,
            "-m",
            "pip",
            "install",
            "--requirement",
            requirement_file_path,
            "--no-warn-script-location",
        ]
    )

    print("Successfully installed python and dependencies.")


def download_blender():
    os_name = get_os_name()
    blender_version_string = get_blender_version_string()
    blender_version_number_string = get_blender_version_number_string()

    if os_name == "windows":
        archive_extension = ".zip"
    elif os_name == "linux":
        archive_extension = ".tar.bz2"

    url_base = (
        "https://ftp.halifax.rwth-aachen.de/blender/release/Blender"
        + blender_version_number_string
        + "/"
    )

    url = url_base + blender_version_string + archive_extension

    archive_folder = get_external_module_folder_path()
    archive_path = os.path.join(
        archive_folder, blender_version_string + archive_extension
    )

    print("Downloading Blender...")
    urllib.request.urlretrieve(url, archive_path)

    print("Extracting archive...")
    shutil.unpack_archive(archive_path, archive_folder)

    print("Deleting archive...")
    os.remove(archive_path)


def get_blender_folder_path():
    external_module_folder = get_external_module_folder_path()
    blender_version_string = get_blender_version_string()

    return os.path.join(external_module_folder, blender_version_string)


def delete_old_blender():
    old_blender_folder_path = get_blender_folder_path()

    if os.path.exists(old_blender_folder_path):
        print("Deleting old Blender folder...")
        shutil.rmtree(old_blender_folder_path, ignore_errors=True)


def activate_addon(addon):
    blender_executable_path = get_blender_executable_path()

    execute_and_print(
        [
            blender_executable_path,
            "--background",
            "--python-expr",
            f"import bpy; bpy.ops.preferences.addon_enable(module='{addon}')",
        ]
    )


def activate_addons():
    print("Activating addons...")

    with open("addons.txt") as file:
        addons = [line.rstrip() for line in file]

    for addon in addons:
        print(f"\tAddon: {addon}")
        activate_addon(addon)


if __name__ == "__main__":
    delete_old_blender()
    download_blender()
    install_dependencies()
    activate_addons()
