These notes explain the functionality of the Python code created to expand the audience that the Joyce calculation code can target.
The code uses interfaces and automated operations to ensure that the end user can perform calculations more intuitively.
The code relies on some libraries for compilation and interface usage, which must be installed before execution.
This code is still under construction. It is helpful untill last step of Joyce calculation.
For more information on how to use Joyce, please refer to the proper manual.

Along with the Python code, an executable is provided that automates the preliminary operations necessary for the usage of both the Joyce code and the code described here.

### Step-by-Step Guide to Compile and Run Joyce ###
Every command described below must be executed in a Bash terminal.
Once Joyce has been downloaded, follow these steps:

## Step 0: Extract "joyce.v2.10.tar"

0.1 	Open terminal window and navigate to the folder in which Joyce has been downloaded. Extract "joyce.v2.10.tar" by typing the following command:
		tar -xvf joyce.v2.10.tar

## Step 1: Run the Pre-Installation Script

1.1 	Open a terminal window in the directory where the files were downloaded.

1.2 	If the script is not executable, make it executable by running the command:
		chmod a+x pre-install-Joyce.sh

1.3 	Run the following command:
		./pre-install-Joyce.sh

1.4 	The terminal will display messages indicating that the necessary files have been successfully downloaded and installed.

## Step 2: Run the Joyce Installation Script

2.1 	Open a terminal window in the directory where the files were downloaded.

2.2 	If the script is not executable, make it executable by running the command:
		chmod a+x Install-Joyce

2.3 	Run the following command:
		./Install-Joyce

2.4	A GUI will ask to user to select code folder, please select folder extracted at step 0.

2.5 	The terminal will display messages indicating that the necessary files have been successfully downloaded and installed.

2.6	Please restart bash terminal.

## Step 3: Compile the Code

3.1 	If the script is not executable, make it executable with the following command:
		chmod a+x Compile-Joyce-py

3.2 	Run the compilation script with the command:
		./Compile-Joyce-py

3.3 	During the compilation process, the terminal will display error messages if something goes wrong. Otherwise, a success message will be shown.

3.4 	If the compilation is successful, an executable file named "Joyce" will be generated inside the root directory.

## Step 4: Run the Executable. *PLEASE NOTE that the executable code must be placed (or copied) where you want to perform the calculation even if the necessary folders do not exist*

4.1 	If the script is not executable, make it executable by running the command:
		chmod a+x Joyce

4.2 	Open a terminal in the directory containing the executable "Joyce" and type the following command:
		./Joyce

4.3 	The program scans the folder from which it is executed for the directories "step 0", "step 1", and "step 2". If these are not found, it create them.

4.4 	A GUI appears asking the user to select the calculation step to execute.

4.6 	The first step to execute is Step 0. Once the corresponding button is pressed, the program searches for a topology file (.top) in the Step0 folder. If it is not found, the user is prompted to select a desired .top file, which will be copied into the Step0 folder. 
	Additionally, an .inp file for the first calculation step is generated, containing the topology file details and the .fchk files.
	The user must provide the fchk files, which the program will search for in the root directory under the "G09.data" folder.
	If the folder does not exists the code will ask to select folder with necessary .fchk files and automatically it copies the folder into the root directory in which the code is launched.
	All the mentioned files are available in "Example_file".

4.7 	The program automatically executes Step 0 of the Joyce code.

4.8 	The GUI will appear again at the end of Joyce calculation

4.9 	This time, select the button corresponding to Step 1 in the GUI.

4.10 	The interface displays the contents of the Generated.IC file (output of Step 0), specifically the Dihedrals section. The user can select which lines to keep by clicking on them. Once selected, the user enters the desired multiplicity value for the dihedrals and confirms the data (for butane example the multiplicity is 3).
	The selected lines are added to the topology file, and everything is saved in the Step1 folder.

4.11	Another interface appears, displaying the contents of the .inp file (which the program previously copied into the folder).
	The interface allows the user to modify the commands in the file with the following features:

		-Keyword selection: A dropdown menu allows the user to select keywords present in the file and remove the associated line with the "cancel" button.
		-Keyword insertion: A dropdown menu allows the user to choose a keyword from a database and enter custom text that will follows it. Another dropdown menu lets the user select the line above which the command should be inserted. The command is added using the "Confirm keyword" button.
		-Generate a new template: Creates a pre-filled .inp file for executing Step 1.
		-Cancel button: Discards the operation.
		-Save button: Saves the edited file.
		
	Each action instantly updates the displayed text.
	(	for butane example the .inp file at this step must look as follow:	
		$title Butane - Step 1
		$equil ../G09.data/opt+freq.fchk
		$forcefield gromacs butane.top
		$zero 1.d-12
		$whess 5000. 2500.0
		end-of-file	)

4.12 	Once the file is saved, the program executes the second calculation step of Joyce.

4.13 	The GUI will appear again at the end of Joyce calculation

4.14 	Proceed with Step 1bis. 
	This automatically inserts into the .inp file (located in the Step1 folder) the dependencies contained in "suggdeps.txt", which was generated in the previous step. The program then automatically executes the associated calculation step.