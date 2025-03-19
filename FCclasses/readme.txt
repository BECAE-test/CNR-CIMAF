### Step-by-Step Guide to Compile and Run FCclasses

All the following commands must be executed in a Bash terminal.

#### Step 0: Extract "fcclasses3-3.0.4"

0.1 Extract "fcclasses3-3.0.4" by running the command:
	tar -xvf fcclasses3-3.0.4.tar.gz

#### Step 1: Run the Pre-Installation Script

1.1 Open a terminal and navigate to the directory where "pre-install-FCclasses.sh" is located.

1.2 If the script is not executable, make it executable by running the command:
	chmod a+x pre-install-FCclasses.sh

1.3 Run the command:
	./pre-install-FCclasses.sh
	
1.4 The terminal will display messages indicating whether the download and installation were successful.

#### Step 2: Compile the Code
	
2.1 If the script is not executable, make it executable by running the command:
	chmod a+x compile-FCclasses.sh
	
2.2 Run the compilation script with the command:
	./compile-FCclasses.sh
	
2.3 During the compilation process, the terminal will display error messages if something goes wrong. Otherwise, a success message will be shown.

2.4 If the compilation is successful, an executable file named "FCclasses" will be generated inside the "01_Anthracene" directory.

#### Step 3: Run the Executable

3.1 Navigate to the "01_Anthracene" directory

3.2 Run the program by executing the command:
	./FCclasses

#### Step 4: Install FCclasses

4.1 A window will appear asking whether you want to proceed with the installation of FCclasses. Press "Yes" only if this is the first time installing it.

4.2 If you press "Yes," another window will appear asking you to choose the installation directory.

4.3 Select the folder named "fcclasses3-3.0.4" for installation.

4.4 If everything is executed correctly, a confirmation window will appear with the message: "The program has been installed successfully!"

#### Step 5: Choose Whether to Run the FCclasses Test

5.1 A window will prompt you to decide whether to proceed with testing FCclasses.

5.2 Running the test is not mandatory to continue. To speed up the process, it is recommended to skip the test for now.

#### Step 6: Select the Input Files

6.1 A window will appear asking the user to select two ".fchk" files from the 01_Anthracene directory.

6.2 The first file should correspond to state 1, and the second file should correspond to state 2.

#### Step 7: Edit the fcc.inp File

7.1 A new window will open, allowing you to edit the "fcc.inp" file.

The interface consists of three sections:
- On the left, a column displays the line numbers of the file.
- In the center, the main file content is displayed.
- On the right, a command panel provides various options.

The command panel includes:
- A dropdown menu labeled "Select K-word in text," which allows the user to choose an existing keyword in the file. The associated text for that keyword can then be modified in the field below. The new text will replace the content after the = sign on the same line.
- A second dropdown menu labeled "Select K-word NOT in text," which allows the user to insert a new keyword. After selecting a keyword to add, the user must specify the line number where it should be inserted. The new keyword, along with its associated text, will be added below the selected line.

7.2 To apply any modifications, the user must press the "Confirm keywords" button.

7.3 Once all changes are made, the user must click the "Save" button.

7.4 If everything has been completed correctly, the "01_Anthracene" folder will be populated with new output files.