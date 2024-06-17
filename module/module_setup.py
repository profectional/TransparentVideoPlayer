import os
import sys
import subprocess

def install_packages():
    packages = [
        'PyQt5',
        'moviepy',
        'yt-dlp'
    ]
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *packages])

def setup_completed():
    return os.path.exists('setup_completed.txt')


if not setup_completed():
    print("Installing dependencies for the first time...")
    install_packages()
    print("Dependencies installed successfully!")
    # Create a file to indicate that setup has been completed
    with open('setup_completed.txt', 'w') as f:
        f.write('Setup completed')
else:
    print("Setup has already been completed previously.")

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the absolute path to K-Lite_Codec_Pack_1810_Basic.exe
codec_pack_path = os.path.join(script_dir, "K-Lite_Codec_Pack_1810_Basic.exe")

# Install K-Lite_Codec_Pack_1810_Basic.exe
print("Installing K-Lite Codec Pack...")
subprocess.run([codec_pack_path, "/quiet"])
