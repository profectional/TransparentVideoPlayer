import requests
import subprocess
import os
import platform
import time
# Target Python version to install
target_version = (3, 12, 4)

# Get the current Python version
current_version = platform.python_version_tuple()
current_version = tuple(map(int, current_version))
STRversion_download = '3.12.4'
# Only download and install if the current version is older than the target version
if current_version < target_version:
    url = f"https://www.python.org/ftp/python/{STRversion_download}/python-{STRversion_download}-amd64.exe"
    response = requests.get(url)

    with open("python_installer.exe", "wb") as file:
        file.write(response.content)

    subprocess.run(["python_installer.exe", "/quiet", "PrependPath=1"])
    os.remove("python_installer.exe")
else:
    print(f"Python {current_version[0]}.{current_version[1]}.{current_version[2]} or newer is already installed.")

time.sleep(5)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the absolute path to module_setup.py
module_setup_path = os.path.join(script_dir, "module", "module_setup.py")

# Run module_setup.py
print("Installing modules...")
subprocess.run(["python", module_setup_path])

# Construct the absolute path to K-Lite_Codec_Pack_1810_Basic.exe
codec_pack_path = os.path.join(script_dir, "module", "K-Lite_Codec_Pack_1810_Basic.exe")

# Install K-Lite_Codec_Pack_1810_Basic.exe
print("Installing K-Lite Codec Pack...")
subprocess.run([codec_pack_path, "/quiet"])