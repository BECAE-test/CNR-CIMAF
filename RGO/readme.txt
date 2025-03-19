### Overview

This program provides an interactive graphical interface for visualizing network structures based on user-defined parameters. Once executed, the program opens a window where users can specify key visualization settings before generating the graph.

### Compatibility and Execution

This code can be executed on any standard compiler or development environment, such as Visual Studio Code, PyCharm, or other Python-compatible IDEs. Ensure that all required dependencies are installed before running the program.

### User Interface Description

The graphical interface consists of three input fields where users can define the visualization criteria:

- Nodes to Display: Enter the specific nodes you want to visualize in the graph. Nodes should be separated by a comma (,) (e.g., 1,2,3,4).
- Connections per Node: Specify the number of connections (edges) to display for each node.
- Energy Threshold: Set a threshold value for the energy of the connections; only edges above this threshold will be displayed.

After entering these values, users must click the "Update Graph" button to generate and display the graph based on the provided input data.

### Input Data

For now, the program uses a sample input matrix embedded within the code itself. This matrix provides example data for testing the visualization features. Future versions may allow users to import custom datasets.

### Preliminary Version Notice

This is a preliminary version of the program, and the graph visualization has not yet been fully optimized. As a result, in some cases, the generated graph may not be clearly readable. Improvements in layout and rendering will be introduced in future updates.