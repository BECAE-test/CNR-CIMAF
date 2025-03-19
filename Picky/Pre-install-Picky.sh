#!/bin/bash

# Array to store output messages
OUTPUT_MESSAGES=()

# Function to check if a package is installed
check_install() {
    PACKAGE_NAME=$1
    COMMAND_TO_CHECK=$2
    INSTALL_COMMAND=$3
    CHECK_METHOD=$4

    if [[ "$CHECK_METHOD" == "command" ]]; then
        if command -v $COMMAND_TO_CHECK &> /dev/null; then
            OUTPUT_MESSAGES+=("[✔] $PACKAGE_NAME is already installed.")
        else
            OUTPUT_MESSAGES+=("[+] Installing $PACKAGE_NAME...")
            eval $INSTALL_COMMAND
            if command -v $COMMAND_TO_CHECK &> /dev/null; then
                OUTPUT_MESSAGES+=("[✔] $PACKAGE_NAME installed successfully!")
            else
                OUTPUT_MESSAGES+=("[✖] Error: $PACKAGE_NAME was not installed.")
            fi
        fi
    elif [[ "$CHECK_METHOD" == "dpkg" ]]; then
        if dpkg -l | grep -q "$COMMAND_TO_CHECK"; then
            OUTPUT_MESSAGES+=("[✔] $PACKAGE_NAME is already installed.")
        else
            OUTPUT_MESSAGES+=("[+] Installing $PACKAGE_NAME...")
            eval $INSTALL_COMMAND
            if dpkg -l | grep -q "$COMMAND_TO_CHECK"; then
                OUTPUT_MESSAGES+=("[✔] $PACKAGE_NAME installed successfully!")
            else
                OUTPUT_MESSAGES+=("[✖] Error: $PACKAGE_NAME was not installed.")
            fi
        fi
    elif [[ "$CHECK_METHOD" == "python" ]]; then
        if python3 -c "import $COMMAND_TO_CHECK" &>/dev/null; then
            OUTPUT_MESSAGES+=("[✔] $PACKAGE_NAME is already installed.")
        else
            OUTPUT_MESSAGES+=("[+] Installing $PACKAGE_NAME...")
            eval $INSTALL_COMMAND
            if python3 -c "import $COMMAND_TO_CHECK" &>/dev/null; then
                OUTPUT_MESSAGES+=("[✔] $PACKAGE_NAME installed successfully!")
            else
                OUTPUT_MESSAGES+=("[✖] Error: $PACKAGE_NAME was not installed.")
            fi
        fi
    fi
}

# Update package list
OUTPUT_MESSAGES+=("[+] Updating package list...")
sudo apt update -y && sudo apt upgrade -y

# Install required packages
check_install "Python3" "python3" "sudo apt install -y python3" "command"
check_install "PIP3" "pip3" "sudo apt install -y python3-pip" "command"
check_install "PyInstaller" "pyinstaller" "sudo pip3 install pyinstaller" "command"
check_install "Tkinter" "tkinter" "sudo apt install -y python3-tk" "python"
check_install "GFortran" "gfortran" "sudo apt install -y gfortran" "command"
check_install "LAPACK Library" "liblapack-dev" "sudo apt install -y liblapack-dev" "dpkg"
check_install "FFTW3 Library" "libfftw3-dev" "sudo apt install -y libfftw3-dev" "dpkg"

# Print all messages at the end
for MESSAGE in "${OUTPUT_MESSAGES[@]}"; do
    echo "$MESSAGE"
done

echo "[✔] Installation completed!"

