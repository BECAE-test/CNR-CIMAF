### Step-by-Step Guide to Install and Run joyce GUI

N.B. THIS VERSION OF GUI WORKS ONLY WITH JOYCE.V2.10 update version will be released soon.

All the following commands must be executed in a Bash terminal.

#### Step 1: Run the Pre-Installation Script

1.1 Download joyce: http://www.iccom.cnr.it/it/joyce/
	
2.1 Install joyce:
	Please refer to joyce manual. 

#### Step 2: Install joyce GUI libraries
N.B. "requirements.txt" contains the names of additional library to be installaed. Do not elimitate it.

2.1 If the script is not executable, make it executable by running the command:
	chmod a+x Setup_joyce_GUI.sh
	
2.2 Run the script with the command:
	./Setup_joyce_GUI.sh
	
2.3 During the installation process, the terminal will display error messages if something goes wrong. Otherwise, a success message will be shown.

2.4 Once installation ends type the following:
	source ~/.bashrc


#### Step 3: Run the Executable (this procedure requires the activation of virtual environment!)

3.1 Copy the new executable where you need to run joyce

3.2 To activate virtual environment just type:
	JOYCE
	"(.venv)" must appears

3.3 To run the Joyce GUI type the following:
	python3 ./joyce_GUI.py

#### Step 4: joyce GUI user-guide

4.1 At first this code searches for a Step folder in the execution directory; if these folders are not present, it shows a dialog box to inform the user.
	Folder(s) can be created later. If there are no Step folders, the code cannot be executed.

4.2 A small interface shows several buttons.
	Button "Step0": Initial calculation step
	Button "Step1": Subsequent calculation step(s)
	Button "Step2": Final calculation step
	Button "Display molecule": Shortcut for software such as Molden, Xcrysden that allows visualization of the molecule from a .xyz file
	Button "Plot Modes": Allows the selection of one or more joyce .out files to plot the vibrational modes of the molecule
	Button "Plot Torsional Profile": Allows the selection of one or more external or joyce-generated scan files for visualization
	Button "Quit": Closes the interface
	
	4.2.1 Button "Step0":  
		Pressing the button, the program looks inside the Step0 folder for topology .top files, reporting their presence. If no file is found,  
		an interface allows selecting a starting topology file to copy into the current Step0 folder.  
		Afterwards, the user is asked if they want to select an "opt+freq" file which will be inserted into the input file template to be generated.  
		An .inp file template is generated inside the Step0 folder, from which the first calculation step is executed.  
		Once the calculation is finished, another window asks whether or not to display the "go.joyce" output.  
	
	4.2.2 Button "Step1":  
		This button asks the user if they wish to perform the selection of dihedrals and pairs to then associate with a new topology file.  
		The dihedrals and pairs in question will be extracted from the "generated.IC.txt" file produced in the previous calculation step.  
		If the user enables the selection, first the dihedral section of "generated.IC.txt" is displayed, with the following functions enabled:  
		- Selection of a dihedral by clicking on its associated line  
		- Duplication of the selected line with the "Duplicate line" button  
		- Deselection of the selected lines with the "Deselect all" button  
		- Saving of the selected lines with subsequent editing through the "Save" button  
		- A "Help" button displays a small guide about the interface  
		Clicking on the "Save" button, another small interface sequentially displays the selected lines, allowing editing of the parameters associated with the dihedral. Once modified, parameters can be  
		confirmed with the "Apply" button, and the line will be saved. Starting from the next line, an "Undo" button is also shown to allow re-editing of the previously modified line.  
		The "Skip all remaining" button allows skipping the editing of subsequent lines if you wish to leave them unchanged.  
		
		Afterwards, the interface displays the [pairs] section extracted from "generated.IC.txt". The interface is identical to the previous one except for the  
		"Skip pair saving" button, which skips the entire saving procedure for the pairs.  
		Selecting the lines and pressing the "Save" button gives the option to edit one by one the selected lines, as explained before.  
		
		When all lines are saved, they are automatically added to the ".top" file placed in the "Step1" folder,  
		at the same time the starting ".inp" file is copied into "Step1" and shown in the next interface.  
		The interface allows interacting with the displayed ".inp" file, enabling its editing. (N.B. the file can also be edited manually from the keyboard)  
		Two drop-down menus display the keywords present in the text (for deletion) and those that can be inserted into the file.  
		By selecting a keyword present in the text and pressing the "Erase" button, the user can delete the associated line; the displayed file updates automatically.  
		By selecting a keyword to insert, the user can write the associated value in the dedicated field and insert it into the file by pressing "Confirm keywords".  
		In addition:  
		- "Generate new .inp file" generates a new input template with the starting values  
		- "Save file" allows overwriting the file being displayed  
		- "Save file as" allows saving the displayed file with a specified name  
		- "Load dependencies" allows inserting into the file the dependencies listed in "suggdeps.txt", if this file is present in the Step1 directory  
		- "Create dependencies" allows selecting a topology file, which then enables another interface  
			this allows selecting two lines at a time to build a dependency between them; once selected, the two lines can be paired with the "Generate" button.  
			The result is shown in the same interface. Created dependencies can be deleted by selecting them and pressing "Delete selected line".  
			The "Continue" button saves the created dependencies and automatically adds them to the input file (if the created dependencies already exist, the user is notified).  
		- "Load assign" allows loading the assigned coordinates generated in "assign.dat", if this file is present in the Step1 directory  
		- "Load geom" allows selecting the folder containing the molecular scans (e.g. G09.data/scan1.0.fchk), automatically adding the paths and linking them to the related keywords ($geom and $scan)  
		- "Cancel" closes the screen  
		- "Continue" launches go.joyce on the just-compiled input file  
		It is then possible to display the go.joyce output.  
	
	4.2.3 Button "Step2"  
		This copies the necessary calculation files from the "Step1" folder to the "Step2" folder (.top and .inp).  
		Afterwards, it displays the input file just copied into "Step2"; the shown interface is the same as previously described.  
		It is then possible to display the go.joyce output.  
	
	4.2.4 Button "Display molecule"  
		This button allows selecting a .xyz file to visualize the associated molecule via "Molden". Shortcuts to other similar software will be added later.  
		
	4.2.5 Button "Plot Modes"  
		Allows the selection of one or more joyce output files (.out) containing the vibrational mode tables of the molecules.  
		A plot is then generated by extracting the data from these tables. Each selected file is displayed with its associated legend.  
		N.B. This function only supports the output table structure from go.joyce "Compare Norm Modes from QM and FF"!  
	
	4.2.6 Button "Plot Torsional Profile"  
		Allows the selection of one or more scan files (scanx.dat) for comparison.  
	
	4.2.7 Button "Quit"  
		Closes the interface.  
