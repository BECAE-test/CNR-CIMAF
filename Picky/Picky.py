import os, shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

FOLDER_NAMES_CYCLE1 = ["Cycle1", "Cycle1/1.picky", "Cycle1/2.QMsampling", "Cycle1/3.fit", "Cycle1/4.deltaP", "Cycle1/5.MD"]
FOLDER_NAMES_CYCLE2 = ["Cycle2", "Cycle2/1.picky", "Cycle2/2.QMsampling", "Cycle2/3.fit", "Cycle2/4.deltaP", "Cycle2/5.MD"]
FOLDER_NAMES_CYCLE3 = ["Cycle3", "Cycle3/1.picky", "Cycle3/2.QMsampling", "Cycle3/3.fit", "Cycle3/4.deltaP", "Cycle3/5.MD"]
FOLDER_NAMES_CYCLE4 = ["Cycle4", "Cycle4/1.picky", "Cycle4/2.QMsampling", "Cycle4/3.fit", "Cycle4/4.deltaP", "Cycle4/5.MD"]
FOLDER_NAMES_CYCLE5 = ["Cycle5", "Cycle5/1.picky", "Cycle5/2.QMsampling", "Cycle5/3.fit", "Cycle5/4.deltaP", "Cycle5/5.MD"]
FOLDER_NAMES_CYCLE6 = ["Cycle6", "Cycle6/1.picky", "Cycle6/2.QMsampling", "Cycle6/3.fit", "Cycle6/4.deltaP", "Cycle6/5.MD"]
FOLDER_NAMES_CYCLE7 = ["Cycle7", "Cycle7/1.picky", "Cycle7/2.QMsampling", "Cycle7/3.fit", "Cycle7/4.deltaP", "Cycle7/5.MD"]
FOLDER_NAMES_CYCLE8 = ["Cycle8", "Cycle8/1.picky", "Cycle8/2.QMsampling", "Cycle8/3.fit", "Cycle8/4.deltaP", "Cycle8/5.MD"]
FOLDER_NAMES_CYCLE9 = ["Cycle9", "Cycle9/1.picky", "Cycle9/2.QMsampling", "Cycle9/3.fit", "Cycle9/4.deltaP", "Cycle9/5.MD"]
FOLDER_NAMES_CYCLE10 = ["Cycle10", "Cycle10/1.picky", "Cycle10/2.QMsampling", "Cycle10/3.fit", "Cycle10/4.deltaP", "Cycle10/5.MD"]

def create_folder(name):
    # Initialize Tkinter (without showing the main window)
    root = tk.Tk()
    root.withdraw()

    if not os.path.exists(name):
        # Create the folder
        os.mkdir(name)
        messagebox.showinfo("Success", f"The folder '{name}' has been successfully created.")
    else:
        messagebox.showwarning("Warning", f"The folder '{name}' already exists.")

    # Close the Tkinter root
    root.destroy()

def copy_files(in_path, in_name, out_path, out_name):
    # Initialize Tkinter (without showing the main window)
    root = tk.Tk()
    root.withdraw()

    if not in_path:
        in_path = os.getcwd()
    if not out_path:
        out_path = os.getcwd()
    if not out_name:
        out_name = in_name

    try:
        shutil.copy(os.path.join(in_path, in_name), os.path.join(out_path, out_name))
        messagebox.showinfo("Success", f"The file '{out_name}' has been copied to '{os.path.join(out_path, out_name)}'.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while copying: {e}")

    # Close Tkinter root
    root.destroy()

def copy_selected_file(out_path, out_name, root_name):
    # Initialize Tkinter (without showing the main window)
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    if not root_name:
        root_name = "Select a file to copy"

    # Open a file dialog for the user to select a file
    file_path = filedialog.askopenfilename(title=root_name, filetypes=[("All files", "*.*")])

    # Check if the user selected a file
    if not file_path:
        messagebox.showwarning("Warning", "No file selected.")
        root.destroy()
        return

    if not out_name:
        out_name = os.path.basename(file_path)

    try:
        shutil.copy(file_path, os.path.join(out_path, out_name))
        messagebox.showinfo("Success", f"The file '{out_name}' has been copied to '{out_path}'.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while copying: {e}")

    # Close Tkinter
    root.destroy()
  

def main():

    root = os.getcwd()
    picky_root = os.environ.get('PICKY')

    for name in FOLDER_NAMES_CYCLE1:
        create_folder(name)

    copy_files(os.path.join(picky_root,"Templates"),"basis.dat",os.path.join(root,FOLDER_NAMES_CYCLE1[1]),"")
    for i in range (2):
        if i == 0:
            message = "Select '.top' file to use"
            copy_selected_file(os.path.join(root,FOLDER_NAMES_CYCLE1[1]),"",message)
        if i == 1:
            message = "Select '.gro' file to use"
            copy_selected_file(os.path.join(root,FOLDER_NAMES_CYCLE1[1]),"",message)

    copy_files(os.path.join(picky_root,"Templates"),"picky.template.inp",os.path.join(root,FOLDER_NAMES_CYCLE1[1]),"")




if __name__ == "__main__":
    main()
