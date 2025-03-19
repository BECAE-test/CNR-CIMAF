#!/bin/bash

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "[✖] Error: PyInstaller is not installed. Please install it using 'pip3 install pyinstaller'."
    exit 1
fi

# Check if Joyce.py exists in the current directory
if [[ ! -f "Joyce.py" ]]; then
    echo "[✖] Error: File 'Joyce.py' not found in the current directory."
    exit 1
fi

# Compile the Python script into a single executable file
pyinstaller --onefile Joyce.py

# Check if the compilation was successful
if [[ -f "dist/Joyce" || -f "dist/Joyce.exe" ]]; then
    echo "[✔] Compilation successful!"
else
    echo "[✖] Error: Compilation failed. Check PyInstaller logs for details."
fi

mv ./dist/Joyce ./

rm -rf build/ dist/

rm Joyce.spec
