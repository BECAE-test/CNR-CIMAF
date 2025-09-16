### Step-by-Step Guide to Compile and Run Gorgona

All the following commands must be executed in a Bash terminal.


#### Step 0: Extract "GOrGONA-main"

0.1 Extract "GOrGONA-main" by running the command:
	tar -xf GOrGONA.tar
	
	
#### Step 1: Run the Pre-Installation Script (Only Required the First Time)

WARNING: The commands used in this pre-installation script are tailored for Ubuntu-based systems. If you are using a different Linux distribution or another operating system, you may need to adapt them accordingly.

1.1 Open a terminal and navigate into the extracted directory "GOrGONA-main" where "pre-install-Gorgona.sh" is located.

1.2 If the script is not executable, make it executable by running the command:
	chmod a+x pre-install-Gorgona.sh

1.3 Run the command:
	./pre-install-Gorgona.sh


#### Step 2: Run "GORGONApre"

2.1 In the same folder, run the "GORGONApre" code by executing:
	python3 GORGONApre.py
	
2.2 A window will appear asking you to enter the name of the operating folder that will be created and where the script will be run. To continue, click OK.
	
2.3 The "Unbiased Search Input" window will appear asking you to select a pair of metals from a dropdown menu. The available pairs are listed in the "databse_ff" folder. (For this example you can choose AuCu)

2.4 In the same window, you will also need to specify the following parameters:

- Cluster Dimension
- Pruning
- NBH
- Box Dimension

2.5 If you need further clarification on these parameters, click the Help button.

2.6 Recommended values for a quick test run of the code are:

- Cluster Dimension: 50  
- Pruning: 25  
- NBH: 500  
- Box Dimension: 6  

2.6 Once the values are set, click Save.


#### Step 3: Continue with the Biased Analysis (Optional)

3.1 When the Unbiased Analysis parameters are set, a new window will open, asking whether you want to set also the parameters of Biased Analysis. If you click Yes continue with Step 3.2, if you choose No skip to Step 4.

3.2 Another window will appear requiring the following inputs:

- From ... atoms of type 1
- To ... atoms of type 1
- Pruning
- NBH

3.3 Recommended values for a quick test run are:

- From ... atoms of type 1: 0  
- To ... atoms of type 1: 50  
- Pruning: 25  
- NBH: 500

3.4 Once the Biased Analysis parameters are set, a message will be displayed in the terminal confirming the process is finished.


#### Step 4: Run Unbiased and Biased Search

4.1 A window will appear asking whether you want to proceed with the Unbiased and Biased Search (or only Unbiased if you've skipped Step 3). If you click Yes, the analysis will start (go to Step 5). If you click No, the process will stop, and you will be able to launch the simulation later (Step 4bis).


#### Step 4bis: Run Unbiased and Biased Search

WARNING: It is recommended to run this step on the same computer where all the previous steps were executed. If you intend to switch to a different computer, make sure that all required libraries and dependencies are properly installed and compatible.

NOTE: Following command must be run from inside the folder that was created in Step 2.2

4bis.1 If the parameters for the Unbiased and Biased Search have already been set but the script has not been run yet, you can start the analysis by executing the command:
	python3 GORGONArun.py

4bis.2 A window will appear asking whether you want to run only the Unbiased Search or both the Biased and Unbiased Search. When you choose an option the analysis will be run.


#### Step 5: Run GORGONApost for Post-Processing

NOTE: Step 5 and 6 make sense only if also Biased Search is performed

5.1 Run the GORGONApost tool by executing:
	python3 GORGONApost.py

5.2 A window will open, asking for the following inputs:

- Size Start (0)
- Size End (50)
- Pruning (25)
- Folder containing the "motifs" directory (created in step 2.2)

5.3 After entering these details, click Start to proceed.


#### Step 6: Visualizing and Analyzing the Graphs

6.1 A new window will open displaying various graphs. You can select which plots to visualize by toggling the flags at the bottom of the window.

6.2 Clicking on individual points within the curves will open a popup window displaying detailed information about that specific point.

6.3 The popup will also contains buttons allowing you to open the structure in:

- Molden
- XCrySDen
- Jmol

(Note: These tools must be installed on your system to function properly.)