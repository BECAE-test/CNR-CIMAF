#!/bin/bash

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "[✖] Error: PyInstaller is not installed. Please install it using 'pip3 install pyinstaller'."
    exit 1
fi

# Check if Joyce.py exists in the current directory
if [[ ! -f "Picky.py" ]]; then
    echo "[✖] Error: File 'Picky.py' not found in the current directory."
    exit 1
fi

# Compile the Python script into a single executable file
pyinstaller --onefile Picky.py

# Check if the compilation was successful
if [[ -f "dist/Picky" || -f "dist/Picky.exe" ]]; then
    echo "[✔] Compilation successful!"
else
    echo "[✖] Error: Compilation failed. Check PyInstaller logs for details."
fi

mv ./dist/Picky ./

rm -rf build/ dist/

rm Picky.spec
