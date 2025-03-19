import subprocess
import sys

# Function to install required packages only if not already installed
def install_package(package, module_name=None):
    module_name = module_name or package  # Allow for different module names
    try:
        __import__(module_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required libraries only if necessary
install_package("tkinter", "tk")
install_package("networkx")
install_package("matplotlib")

import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Reduced matrix for testing
small_matrix = [
    ["Y", 0, -156694.906, 84642.8359, 866171.688, 915261.375, 5, 10, 18, 19, 40, 49, -156694.031, -156694.609, -156694.734, -156694.094, -156694.703],
    ["Y", 10, -156694.984, 88295.5938, 871187.125, 916459.438, 4, 92, 19, 40, 49, -156694.781, -156694.844, -156694.547, -156694.781],
    ["Y", 18, -156696.078, 85273.9609, 866165.375, 915857.875, 3, 19, 40, 49, -156695.891, -156695.672, -156695.297],
    ["Y", 19, -156694.922, 84859.9531, 866874.062, 915775.812, 3, 40, 49, 83, -156694.859, -156694.469, -156694.750],
    ["Y", 40, -156695.078, 85424.3203, 866764.250, 915983.812, 3, 49, 83, 92, -156694.922, -156694.922, -156694.812],
    ["Y", 49, -156695.031, 84600.9219, 866355.250, 915372.375, 2, 83, 92, -156694.891, -156694.766],
    ["Y", 83, -156695.094, 88492.0156, 866588.062, 919510.000, 2, 92, 199, -156694.984, -156694.781],
    ["Y", 92, -156695.000, 84408.1172, 867398.125, 916131.375, 2, 199, 397, -156694.969, -156694.781],
    ["Y", 199, -156694.812, 84882.1406, 867136.938, 916396.188, 1, 397, -156694.797],
    ["Y", 397, -156695.234, 88245.3125, 870975.250, 923617.750, 0]
]

def get_color(energy):
    """ Assign a color to nodes based on energy """
    if energy < -156695:
        return "red"
    elif energy < -156694.5:
        return "orange"
    else:
        return "green"

def create_graph(start_nodes="0", max_links=2, energy_threshold=-156696):
    """ Create a graph with NetworkX and display multiple nodes simultaneously """
    G.clear()
    start_nodes = [int(n) for n in start_nodes.split(",") if n.strip().isdigit()]
    
    added_nodes = set()
    for start_node in start_nodes:
        node_data = next((row for row in small_matrix if row[1] == start_node), None)
        if not node_data:
            continue
        
        node_energy = node_data[2]
        G.add_node(start_node, energy=node_energy, color="blue")
        added_nodes.add(start_node)
        
        num_links = node_data[6]
        linked_nodes = node_data[7:7+num_links]
        energies = node_data[7+num_links:7+2*num_links]
        
        for i, linked_node in enumerate(linked_nodes[:max_links]):
            link_energy = energies[i]
            if energy_threshold is not None and link_energy < energy_threshold:
                continue
            
            linked_node = int(linked_node)
            linked_node_data = next((row for row in small_matrix if row[1] == linked_node), None)
            if not linked_node_data:
                continue
            
            linked_node_energy = linked_node_data[2]
            if linked_node not in added_nodes:
                G.add_node(linked_node, energy=linked_node_energy, color=get_color(linked_node_energy))
                added_nodes.add(linked_node)
            
            G.add_edge(start_node, linked_node, weight=abs(link_energy))
    
    draw_graph()

def draw_graph():
    """ Draw the graph in the Tkinter window """
    ax.clear()
    pos = nx.spring_layout(G, seed=42)
    
    node_colors = [G.nodes[n]["color"] for n in G.nodes]
    nx.draw(G, pos, ax=ax, with_labels=True, node_size=700, node_color=node_colors, edge_color="gray", width=2)
    
    edge_labels = {(u, v): f"{d['weight']:.1f}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=edge_labels, font_size=8)
    
    canvas.draw()

def update_graph():
    """ Function called when the update button is pressed """
    start_nodes = start_node_entry.get()
    max_links = int(max_links_entry.get())
    energy_threshold = float(energy_threshold_entry.get())
    create_graph(start_nodes=start_nodes, max_links=max_links, energy_threshold=energy_threshold)

# Tkinter window setup
root = tk.Tk()
root.title("Interactive Graph")
root.geometry("600x700")

tk.Label(root, text="Initial structures (comma-separated):").pack()
start_node_entry = tk.Entry(root)
start_node_entry.insert(0, "0")
start_node_entry.pack()

tk.Label(root, text="Max number of links:").pack()
max_links_entry = tk.Entry(root)
max_links_entry.insert(0, "2")
max_links_entry.pack()

tk.Label(root, text="Energy threshold:").pack()
energy_threshold_entry = tk.Entry(root)
energy_threshold_entry.insert(0, "-156696")
energy_threshold_entry.pack()

update_button = tk.Button(root, text="Update Graph", command=update_graph)
update_button.pack()

def on_close():
    root.quit()
    root.destroy()
    os._exit(0)

root.protocol("WM_DELETE_WINDOW", on_close)

fig, ax = plt.subplots(figsize=(5, 5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

G = nx.Graph()
create_graph()

root.mainloop()
