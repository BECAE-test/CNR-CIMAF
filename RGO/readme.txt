### Step-by-Step Guide to Compile and Run Gorgona

All the following commands must be executed in a Bash terminal.


#### Step 0: Extract "RGO"

0.1 Extract "RGO" by running the command:
	tar -xzf RGO.tar.gz
	
	
#### Step 1: Run the Pre-Installation Script (Only Required the First Time)

WARNING: The commands used in this pre-installation script are tailored for Ubuntu-based systems. If you are using a different Linux distribution or another operating system, you may need to adapt them accordingly.

1.1 Open a terminal and navigate into the extracted directory "RGO" where "pre-install.sh" is located.

1.2 If the script is not executable, make it executable by running the command:
	chmod a+x pre-install.sh

1.3 Run the command:
	./pre-install.sh


#### Step 2: Open "venv" virtual environment

2.1 Run the command:
	source .venv/bin/activate
	
2.2 If Step 1 was successful (.venv) appear

NOTE: The script works only in this virtual environment


#### Step 3: Run "dijkstra"

3.1 In the same folder, run the "dijkstra_prova" code by executing:
	python3 dijkstra_prova.py
	
3.2 A window will appear prompting the user to enter the initial and final structures for which the minimum energy path is to be calculated.. To continue, click Calculate path.
	
3.3 Another window will appear, displaying the minimum energy path. Within the same window, a button is available that allows the user to plot the computed path.

3.4 Click ‘Plot’ to open a graph of the Path Energy Profile. Click any point to see its details in a pop-up. For structure points, press ‘Open in Xcrysden’ to visualize the structural transition between the selected point and the next one.

(Note: Xcrysden must be installed on your system to function properly.)


#### Step 4: Close "venv" virtual environment

4.1 If you have finished, you can close the virtual environmetn by executing:
	deactivate


