#!/bin/bash

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "[✖] Error: PyInstaller is not installed. Please install it using 'pip3 install pyinstaller'."
    exit 1
fi

# Check if FCclasses.py exists in the current directory
if [[ ! -f "FCclasses.py" ]]; then
    echo "[✖] Error: File 'FCclasses.py' not found in the current directory."
    exit 1
fi

# Compile the Python script into a single executable file
pyinstaller --onefile FCclasses.py

# Check if the compilation was successful
if [[ -f "dist/FCclasses" || -f "dist/FCclasses.exe" ]]; then
    echo "[✔] Compilation successful!"
else
    echo "[✖] Error: Compilation failed. Check PyInstaller logs for details."
fi

mv ./dist/FCclasses ./

rm -rf build/ dist/

rm FCclasses.spec
