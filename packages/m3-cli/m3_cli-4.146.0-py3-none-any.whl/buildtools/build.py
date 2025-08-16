import os
import subprocess
import platform
import shutil
import sys
import glob


def ensure_pyinstaller():
    if shutil.which("pyinstaller") is None:
        print("Error: PyInstaller is not installed or not in PATH.")
        print("Please install it with: `pip install pyinstaller==6.13.0`\n")
        sys.exit(1)


def clean_previous_builds():
    """
    Clean previous PyInstaller build artifacts
    """
    for dir_to_clean in ['build', 'dist']:
        if os.path.exists(dir_to_clean):
            shutil.rmtree(dir_to_clean)


def get_platform_separator():
    """
    Get the appropriate path separator for --add-data based on platform
    """
    return ';' if platform.system() == 'Windows' else ':'


def build_executable():
    # Determine project root directory based on script location
    # Change working directory to project root, so all paths work from root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)

    separator = get_platform_separator()

    clean_previous_builds()

    commands_def_path = os.path.join("m3cli", "commands_def.json")
    if not os.path.exists(commands_def_path):
        print(f"Error: {commands_def_path} not found")
        sys.exit(1)
    else:
        print(f"Found {commands_def_path}")

    data_files = [
        (commands_def_path, "m3cli")
    ]

    access_meta_path = os.path.join(
        "m3cli", "m3cli_complete", "access_meta.json"
    )
    if os.path.exists(access_meta_path):
        data_files.append(
            (access_meta_path, os.path.join("m3cli", "m3cli_complete"))
        )

    plugins_dir = os.path.join("m3cli", "plugins")
    if os.path.exists(plugins_dir):
        data_files.append((plugins_dir, "m3cli/plugins"))
    else:
        print(f"Warning: Plugins directory {plugins_dir} not found")

    cmd = [
        "pyinstaller",
        "--name=m3",
        "--onefile",
        "--console",
        "--hidden-import=click",
        "--hidden-import=requests",
        "--hidden-import=tabulate",
        "--hidden-import=pika",
        "--hidden-import=cryptography",
        "--hidden-import=jsonschema",
        "--hidden-import=yaml",
        "--hidden-import=PIL",
        "--hidden-import=importlib.metadata",
        "--hidden-import=pkg_resources",
        "--copy-metadata", "m3-cli",
        "--hidden-import=m3cli.plugins.utils",
        "--hidden-import=m3cli.plugins.utils.plugin_utilities",
    ]

    # Add plugin modules explicitly
    if os.path.exists(plugins_dir):
        for plugin_file in glob.glob(os.path.join(plugins_dir, "*.py")):
            plugin_name = os.path.splitext(os.path.basename(plugin_file))[0]
            cmd.append(f"--hidden-import=m3cli.plugins.{plugin_name}")

    # Add data files
    for src, dst in data_files:
        if os.path.exists(src):
            cmd.append(f"--add-data={src}{separator}{dst}")
        else:
            print(f"Warning: Data file {src} not found")

    cmd.append(os.path.join("m3cli", "m3.py"))

    print("Running PyInstaller command:")
    print(" ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("\nBuild failed!")
        print(f"Error details: {e}")
        sys.exit(e.returncode)
    except FileNotFoundError as e:
        print("\nBuild failed: PyInstaller not found!")
        print(f"Error details: {e}")
        sys.exit(1)
    except Exception as e:
        print("\nAn unexpected error occurred!")
        print(f"Error details: {e}")
        sys.exit(1)

    print("\nBuild complete! Executable is in the 'dist' directory")


if __name__ == "__main__":
    ensure_pyinstaller()
    build_executable()
