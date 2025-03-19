### Step-by-Step Guide to Compile and Run Gorgona

All the following commands must be executed in a Bash terminal.

#### Step 0: Extract "GOrGONA-main"

0.1 Extract "GOrGONA-main" by running the command:
	tar -xvf GORGONA.tar
	
#### Step 1: Run the Pre-Installation Script

1.1 Open a terminal and navigate into the extracted directory "GOrGONA-main" where "pre-install-Gorgona.sh" is located.

1.2 If the script is not executable, make it executable by running the command:
	chmod a+x pre-install-Gorgona.sh

1.3 Run the command:
	./pre-install-Gorgona.sh
	
1.4 The terminal will display messages indicating whether the download and installation were successful.

#### Step 2: Compile the "GORGONAzero_due" Code
	
2.1 If the script is not executable, make it executable by running the command:
	chmod a+x compile-Gorgona.sh
	
2.2 Run the compilation script with the command:
	./compile-Gorgona.sh
	
2.3 During the compilation process, the terminal will display error messages if something goes wrong. Otherwise, a success message will be shown.

2.4 If the compilation is successful, an executable file named "GORGONAzero_due" will be generated inside the "GOrGONA-main" directory.

#### Step 3: Compile the "graficoGORG" Code
	
3.1 If the script is not executable, make it executable by running the command:
	chmod a+x compile-PostGorgona.sh
	
3.2 Run the compilation script with the command:
	./compile-PostGorgona.sh
	
3.3 During the compilation process, the terminal will display error messages if something goes wrong. Otherwise, a success message will be shown.

3.4 If the compilation is successful, an executable file named "graficoGORG" will be generated inside the "GOrGONA-main" directory.

#### Step 4: Run "GOrGONAzero_due"

3.1 Run the "GORGONAzero_due" code by executing:
	./GORGONAzero_due
	
4.2 A window will appear asking you to select a pair of metals from a dropdown menu. The available pairs are listed in the "databse_ff" folder.

4.3 In the same window, you will also need to specify the following parameters:

- Cluster Dimension
- Cluster Start
- Pruning
- NBH
- Box Dimension

4.4 If you need further clarification on these parameters, click the Help button.

4.5 Recommended values for a quick test run of the code are:

- Cluster Dimension: 50  
- Cluster Start: 0  
- Pruning: 25  
- NBH: 500  
- Box Dimension: 6  

4.6 Once the values are set, click Save to start the Unbiased Analysis.

#### Step 5: Continue with the Biased Analysis (Optional)

5.1 When the Unbiased Analysis is completed, a new window will open, asking whether you want to proceed with the Biased Analysis or terminate the process.

5.2 If you choose to continue, another window will appear requiring the following inputs:

- Size Start
- Size End
- Pruning
- NBH

5.3 Recommended values for a quick test run are:

- Size Start: 0  
- Size End: 50  
- Pruning: 25  
- NBH: 500  

5.5 Once the Biased Analysis is completed, a message will be displayed in the terminal confirming the process is finished.

#### Step 6: Run graficoGORG for Post-Processing

6.1 Run the graficoGORG tool by executing:
	./graficoGORG

6.2 A window will open, asking for the following inputs:

- Size Start (e.g., 0)
- Size End (e.g., 50)
- Pruning (e.g., 25)
- Folder containing the "motifs" directory (e.g., GOrGONA-main)

6.3 After entering these details, click Save to proceed.

#### Step 7: Visualizing and Analyzing the Graphs

7.1 A new window will open displaying various graphs. You can select which plots to visualize by toggling the flags at the bottom of the window.

7.2 Clicking on individual points within the curves will open a popup window displaying detailed information about that specific point.

7.3 The popup will also contain two buttons allowing you to open the structure in:

- Molden
- XCrySDen

(Note: These tools must be installed on your system to function properly.)
