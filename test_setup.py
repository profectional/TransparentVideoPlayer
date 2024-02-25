import os
import sys
import subprocess

def install_packages():
    packages = [
        'PyQt5',
        'moviepy'
    ]
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *packages])

def setup_completed():
    return os.path.exists('setup_completed.txt')

if __name__ == '__main__':
    if not setup_completed():
        print("Installing dependencies for the first time...")
        install_packages()
        print("Dependencies installed successfully!")
        # Create a file to indicate that setup has been completed
        with open('setup_completed.txt', 'w') as f:
            f.write('Setup completed')
    else:
        print("Setup has already been completed previously.")
