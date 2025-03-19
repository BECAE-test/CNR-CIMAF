#!/usr/bin/env python3
import tkinter as tk
import subprocess
from tkinter import messagebox, ttk, filedialog
from tkinter import messagebox, filedialog, scrolledtext
import os
import sys
import shutil

DEFAULT_KEYWORDS = [
    "$title", "$sprint", "$equil", "$forcefield", "$generate", "$zero", "$whess",
    "$geoms", "$assign", "$dependence", "$keepff", "$scan", "$amber", "$gaussian",
    "$rearr", "$UnitedAtom", "$fitLJ", "$sep_el", "$mass", "$normal", "$wfreq", "$boltz"
]

def edit_inp_file(file_path):
    """Opens a text file given a path and displays it in the GUI with a combobox for word selection."""
    
    def save_file():
        """Saves the content of the text area to the specified file and closes the window."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))  # Saves the content of the text area
            root.title(f"Editor - {file_path} (Saved)")
            root.quit()  # Ensures complete closure of the tkinter loop
            root.destroy()  # Closes the window
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")

    def create_inp_file():
        species_name, base_folder, step0_folder, step1_folder, step2_folder = capture_current_directory()

        inp_file = os.path.join(step1_folder, "joyce." + species_name + ".inp")
        optfreq = os.path.abspath("G09.data/opt+freq.fchk")

        try:
            with open(inp_file, 'w') as file:
                file.write("$title " + species_name + " - Step 1\n")
                file.write("$equil " + optfreq + "\n")
                file.write("$forcefield gromacs " + species_name + ".top\n")
                file.write("$generate\n")
                file.write("end-of-file\n")
            
            print(f"The file joyce.{species_name}.inp has been generated inside the Step1 folder")
            
            # After creating the file, reload the content into the text_area
            with open(inp_file, "r", encoding="utf-8") as file:
                content = file.read()
                text_area.delete("1.0", tk.END)  # Clears existing content
                text_area.insert(tk.END, content)  # Inserts the new content
                update_line_numbers()  # Reloads line numbers
                update_combobox_words()  # Reloads the combobox with words and line numbers

        except Exception as e:
            messagebox.showerror("Error", f"Error while creating the file:\n{e}")

    def cancel_action():
        """Closes the window without saving."""
        root.quit()
        root.destroy()
    
    def extract_first_words():
        """Extracts the first word of each line in the ScrolledText widget."""
        # Get the content of the ScrolledText widget
        content = text_area.get("1.0", tk.END)
        
        # Split content into lines
        lines = content.split("\n")
        
        # List to store first words
        first_words = []
        
        for line in lines:
            line = line.strip()  # Removes leading and trailing spaces
            if line and not line.startswith(";"):  # Ignores empty lines and comments
                # Extract the first word
                first_word = line.split()[0]
                first_words.append(first_word)
        
        return first_words
        
    def on_close():
        """Handles window closing when pressing the 'X' button."""
        root.quit()
        root.destroy()
        
    def insert_keyword():
        """Inserts the command from the Entry next to the selected word in the Combobox in the specified line."""
        
        selected2 = word_combobox2.get()  # Selected word in the combobox
        command2 = entry2.get()  # Command to insert from the entry  
        nselected = int(num_combobox2.get())  # Selected number in the combobox

        # Check if the selected word is empty
        if not selected2:
            messagebox.showerror("Error", "No word selected!")
            return
        
        # Check if the Entry is empty
        if not command2:
            messagebox.showerror("Error", "You must enter a command!")
            return

        # Load the file
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            text_area.insert(tk.END, content)
            update_line_numbers()

        except FileNotFoundError:
            content = ""
            text_area.insert(tk.END, "Error: File not found!")
        except Exception as e:
            content = ""
            text_area.insert(tk.END, f"Error while opening the file:\n{e}")

        if command2:
            # Update content only if the line starts with the selected word
            new_content = ""
            inserted = False  # Flag to check if a line was inserted at the beginning
            for i, line in enumerate(content.split("\n"), start=1):
                line = line.strip()  # Removes leading and trailing spaces
                if line:
                    if nselected == i:  # Insert the new line before the selected line
                        new_phrase = selected2 + " " + command2
                        new_content += new_phrase + "\n"  # Add the new line at the beginning
                        new_content += line + "\n"  # Add the original line
                        inserted = True  # Mark that the line has been inserted
                    else:
                        new_content += line + "\n"  # Add unchanged lines
                else:
                    continue
            
            # If the line was not inserted, insert it at the beginning
            if not inserted:
                new_phrase = selected2 + " = " + command2
                new_content = new_phrase + "\n" + new_content

            # Update the text area with the new content
            text_area.replace("1.0", tk.END, new_content)
            update_file()
            entry2.delete(0, tk.END)
            update_line_numbers()

            # Update the comboboxes with the new words and line numbers
            update_combobox_words()

    def update_combobox_words():
        """Reloads the words in the combobox after a modification to the file."""
        # Extract words from the file content again
        first_words = extract_first_words()
        
        # Update the combobox with the extracted words
        word_combobox1['values'] = first_words
        if first_words: 
            word_combobox1.set(first_words[0])  # Set the first word if available
        else:
            word_combobox1.set("")  # If no words are present, leave it empty

        # Also update the line number combobox
        line_numbers = update_line_numbers()
        if line_numbers:
            num_combobox2['values'] = line_numbers
            num_combobox2.set(line_numbers[0])  # Set the first number if available
        else:
            num_combobox2.set("")  # If no line numbers are present, leave it empty

    def update_file():
        """Saves the content of the text area to the specified file."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))  # Save the content of the text area
            root.title(f"Editor - {file_path} (Saved)")         
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")    
    def update_line_numbers(event=None):
        """Updates the line numbers in the sidebar, excluding empty lines."""
        line_numbers_text.config(state="normal")
        line_numbers_text.delete("1.0", tk.END)
        
        # Get all lines of text
        lines = text_area.get("1.0", tk.END).split("\n")
        
        # Filter only non-empty lines and number them
        non_empty_lines = [i + 1 for i, line in enumerate(lines) if line.strip()]  
        
        # Generate the string with line numbers
        line_numbers = "\n".join(map(str, non_empty_lines))
        
        # Insert the updated line numbers
        line_numbers_text.insert(tk.END, line_numbers)
        line_numbers_text.config(state="disabled")  # Prevents manual modifications
        return line_numbers
            
    def erase():
        selected = word_combobox1.get()  # Selected word in the combobox
        if not selected:
            messagebox.showerror("Error", "You must select a word!")
            return

        # Load the file content
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as e:
            messagebox.showerror("Error", f"Error while opening the file:\n{e}")
            return

        # Split the content into lines
        lines = content.splitlines()

        # Filter out lines that start with the selected word
        new_lines = [line for line in lines if not line.startswith(selected)]

        # Reconstruct the new content
        new_content = "\n".join(new_lines)

        # Update the content of the text_area
        text_area.delete("1.0", tk.END)  # Clears the current text
        text_area.replace("1.0", tk.END, new_content)
        
        # Update line numbers
        update_line_numbers()
        update_file()    

        # Call the method to update the comboboxes
        update_combobox_words()  # Add this line
         

    # GUI Creation
    root = tk.Tk()
    root.title(f"Editor - {file_path}")
    root.protocol("WM_DELETE_WINDOW", on_close)  # Handles window closing

    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate position to center the window
    pos_x = (screen_width // 2)
    pos_y = (screen_height // 2)

    # Set the position without specifying dimensions
    root.geometry(f"+{pos_x}+{pos_y}")

    # Main frame
    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Sidebar for line numbers
    line_numbers_text = scrolledtext.ScrolledText(frame, width=4, padx=5, state="disabled", wrap="none", bg="lightgrey", font=("Arial", 12))
    line_numbers_text.pack(side="left", fill="y")

    # Text area with scrollbar
    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Arial", 12))
    text_area.pack(side="left", expand=True, fill="both")

    # Bind events to update line numbers when text changes or is scrolled
    text_area.bind("<KeyRelease>", update_line_numbers)
    text_area.bind("<MouseWheel>", update_line_numbers)
    text_area.bind("<ButtonRelease>", update_line_numbers)

    # Right-side panel
    side_panel2 = tk.Frame(frame)
    side_panel2.pack(side="right", fill="y", padx=10)

    # Another right-side panel
    side_panel1 = tk.Frame(frame)
    side_panel1.pack(side="right", fill="y", padx=10)
    # File loading
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        text_area.insert(tk.END, content)
        line_numbers = update_line_numbers()
        
    except FileNotFoundError:
        content = ""
        text_area.insert(tk.END, "Error: File not found!")
    except Exception as e:
        content = ""
        text_area.insert(tk.END, f"Error while opening the file:\n{e}")
    line_numbers = update_line_numbers()

    # Extract first words
    first_words = extract_first_words()
    
    # Label for combobox
    label = tk.Label(side_panel1, text="Select K-word to eliminate")
    label.pack()
    
    # Label for combobox
    label = tk.Label(side_panel2, text="Select K-word to insert")
    label.pack()
    
    # Combobox for word selection
    selected_word = tk.StringVar()
    word_combobox1 = ttk.Combobox(side_panel1, textvariable=selected_word, values=first_words, state="readonly")
    word_combobox1.set(first_words[0] if first_words else "")  # Set first value if there are words
    word_combobox1.pack(pady=5) 

    # Combobox for word selection
    word_combobox2 = ttk.Combobox(side_panel2, values=DEFAULT_KEYWORDS, state="readonly")
    word_combobox2.set(DEFAULT_KEYWORDS[0])  # Set first value if there are words
    word_combobox2.pack(pady=5)

    # Label for line number selection
    label = tk.Label(side_panel2, text="Select line number to insert before")
    label.pack(pady=5)

    # Combobox for line selection
    num_combobox2 = ttk.Combobox(side_panel2, values=line_numbers, state="readonly")
    num_combobox2.set(line_numbers[0])  # Set first value if there are words
    num_combobox2.pack(pady=5)
    
    label = tk.Label(side_panel2, text="Insert mode for selected keywords")
    label.pack(pady=5)

    # Text entry field
    entry2 = tk.Entry(side_panel2)
    entry2.pack(pady=10)

    # Button to erase line
    erase_button = tk.Button(side_panel1, text="Cancel", command=erase)
    erase_button.pack(pady=10)

    # Button to generate a new empty inp file
    generate_button = tk.Button(side_panel1, text="Generate new inp. file", command=create_inp_file)
    generate_button.pack(pady=10)

    # Save button
    save_button = tk.Button(side_panel2, text="Save", command=save_file)
    save_button.pack(side="bottom", pady=10, padx=10)
    
    # Cancel button
    cancel_button = tk.Button(side_panel1, text="Cancel", command=cancel_action)
    cancel_button.pack(side="bottom", pady=10, padx=10)

    # Button to insert command
    insert = tk.Button(side_panel2, text="Confirm keywords", command=insert_keyword)
    insert.pack(side="bottom", padx=10, pady=5)

    root.mainloop()  # Start the GUI when required

def create_folders():
    global STEP0_FOLDER, STEP1_FOLDER, STEP2_FOLDER, BASE_FOLDER
    #message = "No Step folders were found. Please select a destination for Step0, Step1, and Step2 folders."
    message = "No Step folders were found."
    show_message(message)
    root = tk.Tk()
    root.withdraw()  # Hides the main Tkinter window

    # Select the main folder
    #base_path = filedialog.askdirectory(title="Select the destination folder")
    base_path = os.getcwd()
    # If the user closes the window without selecting anything (cancel or close button)
    if not base_path:
        messagebox.showinfo("Operation Canceled", "No folder selected.")
        root.destroy()  # Close the Tkinter window
        return  # Stop function execution

    # Dictionary for folder paths
    folder_paths = {
        "Step0": os.path.join(base_path, "Step0"),
        "Step1": os.path.join(base_path, "Step1"),
        "Step2": os.path.join(base_path, "Step2"),
    }

    existing_folders = [c for c in folder_paths if os.path.exists(folder_paths[c])]
    folders_to_create = [c for c in folder_paths if not os.path.exists(folder_paths[c])]

    # Notify the user about existing folders
    if existing_folders:
        existing_msg = "\n".join(existing_folders)
        messagebox.showwarning("Warning", f"The following folders already exist:\n{existing_msg}")

    # If all folders exist, terminate
    if not folders_to_create:
        messagebox.showinfo("Operation Canceled", "All folders already exist. No operation performed.")
        root.destroy()  # Close the Tkinter window
        return  # Stop function execution

    # Ask for confirmation before creating the missing folders
    response = messagebox.askyesno(
        "Confirmation", 
        f"Do you want to create the following folders in:\n{base_path}?\n\n" + "\n".join(folders_to_create)
    )

    if not response:
        messagebox.showinfo("Operation Canceled", "No folder created.")
        root.destroy()  # Close the Tkinter window
        return  # Stop function execution

    # Create the remaining folders
    try:
        for folder in folders_to_create:
            os.makedirs(folder_paths[folder], exist_ok=True)
        messagebox.showinfo("Success", "The folders have been successfully created!")
    except Exception as e:
        messagebox.showerror("Error", f"Error while creating folders:\n{e}")

    # Define constants with the final paths
    STEP0 = os.path.abspath(folder_paths["Step0"])
    STEP1 = os.path.abspath(folder_paths["Step1"])
    STEP2 = os.path.abspath(folder_paths["Step2"])

    # Define the base folder where the files are stored
    BASE_FOLDER = base_path
    STEP0_FOLDER = os.path.join(BASE_FOLDER, "Step0")
    STEP1_FOLDER = os.path.join(BASE_FOLDER, "Step1")
    STEP2_FOLDER = os.path.join(BASE_FOLDER, "Step2")
    
    # Print the paths in the terminal as well
    #print(f"STEP0 = {STEP0}")
    #print(f"STEP1 = {STEP1}")
    #print(f"STEP2 = {STEP2}")

    root.destroy()  # Close the Tkinter window

def step0():  
    species_name, base_folder, step0_folder, step1_folder, step2_folder = capture_current_directory()
    create_inp_file(step0_folder)
    check_G09_folder()
    run_go_joyce(step0_folder, species_name)
    #print(f"Found the following species in the Step0 folder: '{species_name}'")
    
def step1():    
    species_name, base_folder, step0_folder, step1_folder, step2_folder = capture_current_directory()
    create_inp_file(step1_folder)
    file_IC = os.path.join(step0_folder, "generated.IC.txt")
    stop_word_top = 'bonds'
    stop_word_top_2 = 'system'
    extension = ".top"
    path_top_file = os.path.join(step0_folder, species_name)
    
    lines_before, lines_after = read_before_and_after(path_top_file + extension, stop_word_top, stop_word_top_2)
    
    if lines_before and lines_after:
        modified_lines = merge_lists_with_file(lines_before, lines_after, file_IC, "Stretchings", "Exclusions")
        write_file(os.path.join(step1_folder, (species_name + ".top")), modified_lines)
        modified_lines = read_range_between_words(os.path.join(step1_folder, (species_name + ".top")), stop_word_top, stop_word_top_2)
    
    delete_from = 'dihedrals'
    delete_to = 'Nonbonded terms'
    keep_selected_lines(os.path.join(step1_folder, (species_name + ".top")), os.path.join(step1_folder, (species_name + ".top")), delete_from, delete_to)   
    
    global root, text_widget  # Declare global variables
    file_to_read = os.path.join(step1_folder, "joyce." + species_name + ".inp")

    replace_word(file_to_read, "Step 0", "Step 1")
    edit_inp_file(file_to_read)

    run_go_joyce(step1_folder, species_name)

def step1bis():
    species_name, base_folder, step0_folder, step1_folder, step2_folder = capture_current_directory()
    file_suggdeps = os.path.join(step1_folder, "suggdeps.txt")
    stop_word_1 = 'end-of-file'
    stop_word_2 = 'end-of-file'
    extension = ".inp"
    file_path = os.path.join(step1_folder, ("joyce." + species_name))
    
    lines_before, lines_after = read_before_and_after(file_path + extension, stop_word_1, stop_word_2)
    
    if lines_before and lines_after:
        modified_lines = merge_lists_with_file(lines_before, lines_after, file_suggdeps, "", "")
        write_file(os.path.join(step1_folder, ("joyce." + species_name + ".inp")), modified_lines)
    
    run_go_joyce(step1_folder, species_name)
    return 

def inp_file_step0(input_path, text_widget):
    """Reads the `input_path` file and displays its content in the Text widget `text_widget`."""
    try:
        with open(input_path, 'r') as file:
            content = file.read()
            text_widget.delete("1.0", tk.END)  # Clears the Text widget
            text_widget.insert(tk.END, content)  # Inserts the text
    except FileNotFoundError:
        print(f"Error: the file '{input_path}' was not found.\n")
    return

def on_text_click(event):
    """Handles clicking on the Text widget: asks whether to delete the line or insert new text."""
    index = text_widget.index(f"@{event.x},{event.y}")  # Gets the row.column index
    line_str, _ = index.split(".")
    line = int(line_str)

    response = messagebox.askyesno(
        "Delete Confirmation",
        f"Do you want to delete line {line}? (If you choose No, you can insert new text below this line.)"
    )

    if response:
        text_widget.delete(f"{line}.0", f"{line+1}.0")  # Deletes the selected line
    else:
        open_insert_window(line)

def open_insert_window(line):
    """Opens a window to select a word and insert new text."""
    top = tk.Toplevel(root)
    top.title("Insert Additional Text")

    label = tk.Label(top, text=f"You clicked line {line}. Choose a word and add text:")
    label.pack(pady=5)

    combo_label = tk.Label(top, text="Select word:")
    combo_label.pack()

    combo_words = ttk.Combobox(top, values=DEFAULT_KEYWORDS, state="readonly")
    combo_words.set("Select...")
    combo_words.pack(pady=5)

    text_insert_label = tk.Label(top, text="Add more text (optional):")
    text_insert_label.pack()

    text_insert = tk.Text(top, width=50, height=5)
    text_insert.pack(padx=10, pady=5)

    def confirm_insert(event=None):
        """Confirms the insertion of the selected word and additional text."""
        selected_word = combo_words.get()
        additional_text = text_insert.get("1.0", tk.END).strip()

        if selected_word == "Select...":
            selected_word = ""

        text_to_insert = (selected_word + " " + additional_text).strip()

        if text_to_insert:
            insert_position = f"{line+1}.0"
            text_widget.insert(insert_position, text_to_insert + "\n")

        top.destroy()

    # Confirmation button
    btn_ok = tk.Button(top, text="OK", command=confirm_insert)
    btn_ok.pack(pady=5)

    # Bind Enter key to confirmation function
    top.bind("<Return>", confirm_insert)

def save_inp_file_step1():
    """Saves the content of the Text widget into an output file and reloads it."""
    
    base_folder = os.getcwd()
    step1_folder = os.path.join(base_folder, "Step1")
    output_file = os.path.join(step1_folder, "joyce.butane.inp")

    # If the output file is not defined, ask for the path with a dialog window
    if not output_file:
        output_file = filedialog.asksaveasfilename(
            title="Save the file",
            defaultextension=".inp",
            filetypes=[("Text files", "*.inp"), ("All files", "*.*")]
        )

    if output_file:
        try:
            # Save the content of the Text widget into the file
            with open(output_file, "w") as file:
                file.write(text_widget.get("1.0", tk.END).strip())  # Writes content without trailing spaces
            
            messagebox.showinfo("Save Completed", f"File successfully saved in:\n{output_file}")
            
            # Reload the saved file into the Text widget
            inp_file_step0(output_file, text_widget)
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving: {e}")
        root.destroy()
    
def run_go_joyce(run_folder, species_name):
    
    # Define the Linux command to execute
    command = ["go.joyce", species_name]

    try:
        
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        # Check if the output contains swap warnings
        if "swap" in result.stderr.lower() or "swap" in result.stdout.lower():
            result = subprocess.run("Y")
            print("Swap warning detected, but the response will be positive.")
        else:
            print("Command executed without warnings.")
        
        # You can also print the command output
        print("Command output:", result.stdout)
        # Execute the command in the specified run folder using 'cwd'
        result = subprocess.run(command, cwd=run_folder, check=True)
        print(result.stdout)  # Show command output

    except subprocess.CalledProcessError as e:
        print(f"Error while executing the command: {e}")

def select_and_copy_file(destination, warning_message):
    # Create the Tkinter window but do not show it
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Show the warning message
    messagebox.showinfo("Warning", warning_message)

    # Ask the user to select a .top file
    selected_file = filedialog.askopenfilename(
        title="Select a .top file",
        filetypes=[("Text files", "*.top")]  # Only .top files
    )

    # If the user cancels or closes the window (selected_file is an empty string)
    if not selected_file:
        print("Operation canceled by the user.")
        root.destroy()  # Close the Tkinter window and terminate the program
        sys.exit()
        return

    # If the user has selected a file
    try:
        # Extract the file name
        file_name = os.path.basename(selected_file)
        # Full destination path
        full_destination = os.path.join(destination, file_name)

        # Check if the destination folder exists
        if not os.path.exists(destination):
            os.makedirs(destination)  # Create the folder if it does not exist

        # Copy the file to the destination folder
        shutil.copy(selected_file, full_destination)
        print(f"File successfully copied to {full_destination}")
    except Exception as e:
        print(f"An error occurred while copying the file: {e}")

    # Destroy the Tkinter window to free up resources
    root.destroy()

def capture_current_directory():
    exists = bool
    base_folder = os.getcwd()
    step0_folder = os.path.join(base_folder, "Step0")
    step1_folder = os.path.join(base_folder, "Step1")
    step2_folder = os.path.join(base_folder, "Step2")
    
    exists = any(os.path.isfile(os.path.join(step0_folder, f)) and f.endswith(".top") for f in os.listdir(step0_folder))    
    
    if exists:
        species_name = [os.path.splitext(f)[0] for f in os.listdir(step0_folder) if os.path.isfile(os.path.join(step0_folder, f)) and f.endswith(".top")]
        return species_name[0], base_folder, step0_folder, step1_folder, step2_folder
    else:
        message = "No topology file was found inside the Step 0 folder"
        select_and_copy_file(step0_folder, message)
        species_name = [os.path.splitext(f)[0] for f in os.listdir(step0_folder) if os.path.isfile(os.path.join(step0_folder, f)) and f.endswith(".top")]
        return species_name[0], base_folder, step0_folder, step1_folder, step2_folder

def read_until_word(file_path, stop_word):
    """Reads a file until a specific word is found and returns the read lines."""
    lines = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                lines.append(line)
                if stop_word in line:
                    break
        return lines
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []

def read_before_and_after(file_path, word1, word2):
    """
    Reads a file and returns the lines before `word1` and after `word2`,
    excluding the lines containing `word1` and `word2` and the entire block between them.
    """
    lines_before = []
    lines_after = []
    collect_after = False  # Initially, collect only in `lines_before`
    ignore_block = False
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if word1 in line:
                    collect_after = False  # Stop collecting in `lines_before`
                    ignore_block = True  # Start ignoring lines between `word1` and `word2`

                if word2 in line:
                    collect_after = True  # Now collect in `lines_after`
                    ignore_block = False  # End of the ignored section

                if collect_after:
                    lines_after.append(line)  # Collect lines after `word2`
                elif not ignore_block:
                    lines_before.append(line)  # Collect only lines before `word1`

        return lines_before, lines_after  # Return the separate lists

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return [], []

def merge_lists_with_file(list1, list2, file_path, word1, word2):
    """
    Reads a file and retrieves the lines between `word1` and `word2`.
    If `word2` is not present, it takes until the end of the file.
    Inserts them between `list1` and `list2`, returning the merged list.
    """
    interval_lines = []
    collect = False  # Flag to control when to start collecting lines

    try:
        with open(file_path, 'r') as file:
            for line in file:

                if word1 in line:
                    collect = True  # Start collecting from `word1`

                if collect:
                    interval_lines.append(line)  # Add the line to the interval

                if word2 and word2 in line:  # If `word2` is found, stop
                    break

        # Merge list1, the extracted block, and list2
        merged_list = list1 + interval_lines + list2

        return merged_list  # Return the final list

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return list1 + list2  # If the file does not exist, return only list1 + list2

def add_content(lines, stop_word, file_to_add):
    """Adds the content of another file after the line containing stop_word."""
    try:
        with open(file_to_add, 'r') as file:
            found = False
            for line in file:
                if stop_word in line:
                    found = True
                    if found:
                        new_lines = file.readlines()
                        text_to_add = ''.join(new_lines).strip()
            if not found: 
                new_lines = file.readlines()
                text_to_add = ''.join(new_lines).strip()
        for i, line in enumerate(lines):
            if stop_word in line:
                lines[i] = lines[i].strip() + f"\n{text_to_add}\n"
                break
        return lines
    except FileNotFoundError:
        print(f"Error: The file '{file_to_add}' was not found.")
        return lines
    
def write_file(file_path, lines):
    """Writes the lines into a file."""
    try:
        with open(file_path, 'w') as file:
            file.writelines(lines)
        print(f"File successfully saved in '{file_path}'!")
    except Exception as e:
        print(f"Error writing the file '{file_path}': {e}")

def modify_columns(line, new_col5_value, start_col10):
    """Modifies column 5 and updates column 10 in sequential order."""
    columns = line.split()
    if len(columns) >= 10:
        columns[7] = str(new_col5_value)
        columns[9] = str(start_col10)
    return '   '.join(columns) + '\n'

def extract_lines_in_range(file_path, start, end): 
    """
    Returns the lines between two specific words, excluding those containing `start` and `end`.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()  # Reads all lines of the file

        found = False
        interval_lines = []

        for i, line in enumerate(lines, start=1):
            clean_line = line.strip()  # Removes leading and trailing whitespace

            if start in clean_line:
                found = True  # Start collecting lines, but DO NOT add this line
                continue  # Skip adding this line and move to the next

            if end in clean_line:
                break  # If `end` is found, stop the loop WITHOUT adding the line

            if found:
                interval_lines.append((i, clean_line))  # Add only the lines in the middle

        return lines, interval_lines  # Return the entire file + only the selected interval

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return [], []

def keep_selected_lines(file_path, output_path, start, end):
    """Graphical interface to select lines to keep with a mouse click."""
    
    lines, interval_lines = extract_lines_in_range(file_path, start, end)
    
    if not interval_lines:
        print("No lines were extracted within the word range: ", start, "and", end)
        return

    def confirm_selection(): # Opens the selection window for the lines
        """Retrieves the selected lines, modifies the columns, and saves the file."""
        selected = list(map(int, listbox.curselection()))
        if not selected:
            messagebox.showwarning("Warning", "Select at least one line!")
            return
        
        lines_to_keep = {interval_lines[idx][0] for idx in selected}

        new_col5_value = entry_col5.get()
        if not new_col5_value.isdigit():
            messagebox.showerror("Error", "Enter a valid numeric value for the multiplicity column.")
            return
        
        new_col5_value = int(new_col5_value)

        # Retrieve the initial value of column 10 from the first selected line
        first_selected_line = interval_lines[0][1].split()
        start_col10 = int(first_selected_line[9]) if len(first_selected_line) >= 10 else 1
        index = 0
        new_lines = []
        for i, line in enumerate(lines, start=1):
            if i in lines_to_keep:
                new_lines.append(modify_columns(line, new_col5_value, start_col10))
                start_col10 += 1  # Increment column 10 progressively
                index += 1
                if index == len(selected):
                    new_lines.append('\n')
            elif i not in {num for num, _ in interval_lines}:
                new_lines.append(line)
        
        write_file(output_path, new_lines)
        messagebox.showinfo("Success", f"File saved in '{output_path}'")
        root.destroy()

    # Create the Tkinter window
    root = tk.Tk()
    root.title("Select the lines to keep")

    label = tk.Label(root, text="Select the lines to keep:")
    label.pack()

    listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, height=20, width=80)
    for i, (_, line) in enumerate(interval_lines):
        listbox.insert(tk.END, f"{i+1}: {line}")
    listbox.pack()

    label_col5 = tk.Label(root, text="Value for multiplicity:")
    label_col5.pack()
    entry_col5 = tk.Entry(root)
    entry_col5.pack()

    btn_confirm = tk.Button(root, text="Confirm selection", command=confirm_selection)
    btn_confirm.pack()
    root.bind()
    root.mainloop()

def modify_inp_file(file_path_inp_in, file_path_inp_out, stop_word_inp):
    """Modifies the inp file, stopping reading at a keyword chosen by the user."""
    try:
        other_file_lines = []
        keep_lines = []
        with open(file_path_inp_in, 'r') as file:
            for line in file:
                print(f"{line.strip()}")
                if stop_word_inp in line:
                    print(f"\nReading interrupted: found the word '{stop_word_inp}'")
                    print("Enter the desired text, this will start replacing the found word")
                    break
                other_file_lines.append(line)
            keep_lines = file.readlines()
        
        print("\nEnter new lines (type 'STOP' to finish):")
        while True:
            new_line = input()
            if new_line.strip().upper() == 'STOP':
                break
            other_file_lines.append(new_line + '\n')
        
        other_file_lines.extend(keep_lines)
        with open(file_path_inp_out, 'w') as file:
            file.writelines(other_file_lines)
        print("\nModification on 'inp' completed!")
    except FileNotFoundError:
        print(f"The file '{file_path_inp_in}' was not found.")
    except Exception as e:
        print(f"Error opening '{file_path_inp_in}': {e}")

def read_range_between_words(file_path, word1, word2):
    """
    Reads a file and returns the lines between `word1` and `word2`,
    keeping the original format without removing spaces or newlines.
    """
    interval_lines = []
    collect = False  # Flag to start collecting lines

    try:
        with open(file_path, 'r') as file:
            for line in file:
                if word1 in line:
                    collect = True  # Start collecting from `word1`

                if collect:
                    interval_lines.append(line)  # Keep the original line

                if word2 in line:
                    break  # If `word2` is found, stop collecting

        return interval_lines  # Return the list of extracted lines

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []

def replace_word(file_path, word_to_replace, new_word):
    """
    Opens a file, replaces all occurrences of `word_to_replace` with `new_word`,
    and saves the changes to the file.
    """
    try:
        # Read the entire content of the file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Replace the word
        new_content = content.replace(word_to_replace, new_word)

        # Write the new content to the file (overwriting it)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

        print(f"Replacement completed: '{word_to_replace}' → '{new_word}' in '{file_path}'.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"Error while modifying the file: {e}")

def check_step_folders():
    """
    Checks if the current directory contains the folders Step0, Step1, Step2.
    Returns a dictionary with the results.
    """
    # List of folders to check
    folders_to_check = ["Step0", "Step1", "Step2"]

    if all(os.path.isdir(folder) for folder in folders_to_check):
        return "yes"
    else:
        return "no"

def check_G09_folder():
    """
    Checks if the current directory contains the folder G09.data,
    and if the folder contains any files.
    If the folder is not found, it prompts the user to select it.
    """
    folder_to_check = "G09.data"
    
    # Check if the folder exists
    if os.path.isdir(folder_to_check):
        # Get the files in the folder
        files_in_folder = os.listdir(folder_to_check)
        
        # Check if the folder contains files
        if not files_in_folder:  # If the list is empty, the folder is empty
            return {"status": "folder exists", "content": "empty"}
        else:
            return {"status": "folder exists", "content": "full", "file_count": len(files_in_folder)}
    else:
        # If the folder doesn't exist, show a warning message and prompt the user to select the folder
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showwarning("Folder not found", "The G09.data folder was not found. Please select it to copy.")
        select_and_copy_G09_folder()  # Ask the user to select the folder
        return {"status": "folder does not exist, user needs to select it"}

def select_and_copy_G09_folder():
    """
    Prompts the user to select a folder to copy, and ensures it is named 'G09.data'.
    """
    # Open a file dialog to ask the user to select a folder
    folder_path = filedialog.askdirectory(title="Select the G09.data folder to copy")
    if folder_path:
        folder_name = os.path.basename(folder_path)
        
        # Check if the folder name is not 'G09.data'
        if folder_name != "G09.data":
            # Define the new folder path with the correct name
            destination_folder = os.path.join(os.getcwd(), "G09.data")
            
            # Rename the folder by copying it to the new destination
            shutil.copytree(folder_path, destination_folder)
            print(f"Folder renamed and copied as: {destination_folder}")
        else:
            # If the folder is already named 'G09.data', just copy it
            print(f"Folder already named 'G09.data'. Copying folder...")
            # You can copy it directly or add any other logic here if necessary
            destination_folder = os.path.join(os.getcwd(), "G09.data")
            shutil.copytree(folder_path, destination_folder)
        
    else:
        print("No folder selected.")

def create_inp_file(path):
    
    species_name, base_folder, step0_folder, step1_folder, step2_folder = capture_current_directory()

    inp_file = os.path.join(path, "joyce." + species_name + ".inp")
    optfreq = os.path.abspath("G09.data/opt+freq.fchk")
    
    with open(inp_file, 'w') as file:
        file.write("$title " + species_name +  " - Step 0\n")
        file.write("$equil " + optfreq + "\n")
        file.write("$forcefield gromacs " + species_name + ".top\n")
        file.write("$generate\n")
        file.write("end-of-file\n")
        print(f"The file joyce." + species_name + ".inp has been generated inside the Step0 folder" )
    return

def ask_for_step():
    # Global variable to store the response
    result = None

    # Function called when a button is pressed
    def on_button_click(button_name):
        nonlocal result  # Use the result variable from the outer function
        result = button_name
        root.quit()  # Ends the mainloop
        root.destroy()  # Destroys the main window

    # Function to handle window closing (clicking the close button)
    def on_close():
        nonlocal result
        result = "cancel"  # Sets result to "cancel" when the window is closed
        root.quit()
        root.destroy()

    # Create the main window
    root = tk.Tk()
    root.title("Execution step")
    root.geometry("300x300")

    # Configure window closing to stop execution
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Create a label to display the result
    result_label = tk.Label(root, text="Choose option", font=("Arial", 14))
    result_label.pack(pady=20)

    # Create the 3 buttons
    button1 = tk.Button(root, text="Step 0", command=lambda: on_button_click("Step 0"))
    button1.pack(pady=10)

    button2 = tk.Button(root, text="Step 1", command=lambda: on_button_click("Step 1"))
    button2.pack(pady=10)

    button3 = tk.Button(root, text="Step 1bis", command=lambda: on_button_click("Step 1bis"))
    button3.pack(pady=10)

    # Add the "Cancel" button
    cancel_button = tk.Button(root, text="Cancel", command=on_close)
    cancel_button.pack(pady=10)

    # Start the main tkinter loop
    root.mainloop()

    return result  # Returns the value of the result variable

def show_message(message):
    # Create the main window
    root = tk.Tk()
    root.title("INFO")
    root.geometry("400x150")

    # Create a label with the message
    label = tk.Label(root, text=message, font=("Arial", 14), wraplength=350)
    label.pack(pady=30)  # Add some space above and below the text

    # Add a button to close the window
    button = tk.Button(root, text="OK", command=root.destroy)
    button.pack()

    # Start the main tkinter loop
    root.mainloop()

def main():
    
    exists = check_step_folders()
    if exists == "yes":
        message = "Necessary folders for the execution of go.joyce already exist"
        show_message(message)
    if exists == "no":
        create_folders()
        message = "Necessary folders for the execution of go.joyce have been created"
        show_message(message)
    
    # Initialize step variable
    step=""
    while step!= "cancel":
        step = ask_for_step()
        if step == "Step 0":
            step0()
            print("Step 0 executed")
        elif step == "Step 1":
            step1()
            print("Step 1 executed")
        elif step == "Step 1bis":
            step1bis()
            print("Step 1bis executed")
            step = "cancel"  # Exit loop after executing step 1bis
        else:
            print("Exit")  # Handles invalid input
    
if __name__ == "__main__":
    main()
