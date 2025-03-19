These notes explain the functionality of the Python code created to expand the audience that the Picky calculation code can target.
The code uses interfaces and automated operations to ensure that the end user can perform calculations more intuitively.
The code relies on some libraries for compilation and interface usage, which must be installed before execution.
This code is still under construction.
For more information on how to use Picky, please refer to the proper manual.

Along with the Python code, some executables are provided that automates the preliminary operations necessary for the usage of both the Picky code and the code described here.

### Step-by-Step Guide to Compile and Run Picky ###
Every command described below must be executed in a Bash terminal.
Once Picky has been downloaded, follow these steps:

## Step 0: Extract "picky_v3.0.tar"

0.1 	Open terminal window and navigate to the folder in which Picky has been downloaded. Extract "picky_v3.0.tar" by typing the following command:
		tar -xvf picky_v3.0.tar

## Step 1: Run the Pre-Installation Script

1.1 	Open a terminal window in the directory where the files were downloaded.

1.2 	If the script is not executable, make it executable by running the command:
		chmod a+x Pre-install-Picky.sh

1.3 	Run the following command:
		./Pre-install-Picky.sh

1.4 	The terminal will display messages indicating that the necessary files have been successfully downloaded and installed.

## Step 2: Run the Picky Installation Script

2.1 	Open a terminal window in the directory where the files were downloaded.

2.2 	If the script is not executable, make it executable by running the command:
		chmod a+x Install-Picky

2.3 	Run the following command:
		./Install-Picky

2.4	A GUI will ask to user to select code folder, please select folder extracted at step 0.

2.5 	The terminal will display messages indicating that the necessary files have been successfully downloaded and installed.

2.6	Please restart bash terminal.

## Step 3: Compile the Code

3.1 	If the script is not executable, make it executable with the following command:
		chmod a+x Compile-Picky-py

3.2 	Run the compilation script with the command:
		./Compile-Picky-py

3.3 	During the compilation process, the terminal will display error messages if something goes wrong. Otherwise, a success message will be shown.

3.4 	If the compilation is successful, an executable file named "Picky" will be generated inside the root directory.

## Step 4: Run the Executable. *PLEASE NOTE that the executable code must be placed (or copied) where you want to perform the calculation even if the necessary folders do not exist*

4.1 	If the script is not executable, make it executable by running the command:
		chmod a+x Picky

4.2 	Open a terminal in the directory containing the executable "Picky" and type the following command:
		./Picky

4.3 	The program scans the folder from which it is executed for the directory "Cycle1" and subdirectories "1.picky", "2.QMsampling", "3.fit", 4.deltaP", "5.MD". If these are not found, it create them.

4.4 	A GUI appears asking the user to select the ".top" file to copy in "Cycle1\1.picky" (example of .top file is available inside "Benzene\Cycle0" folder.

4.5 	A GUI appears asking the user to select the ".gro" file to copy in "Cycle1\1.picky" (example of .gro file is available inside "Benzene\Cycle0" folder.

4.6 	The code automatically will copy a template of ".inp" file inside "Cycle1\1.picky".

Next steps will be released soon.
