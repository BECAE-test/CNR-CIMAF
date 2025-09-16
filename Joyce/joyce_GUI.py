#!/usr/bin/env python3
import tkinter as tk
import subprocess
import os
import sys
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import re
from pathlib import Path
from tkinter import messagebox, filedialog, scrolledtext, ttk, filedialog

DEFAULT_KEYWORDS = [
    "$title", "$print", "$equil", "$forcefield", "$generate", "$zero", "$whess",
    "$geoms", "$assign", "$dependence", "$keepff", "$scan", "$amber", "$gaussian",
    "$rearr", "$UnitedAtom", "$fitLJ", "$sep_el", "$mass", "$normal", "$wfreq", "$boltz"
]

def plot_torsional_profile(selected_files):
    """Plot torsional energy profiles from one or more selected data files."""
    markers = ['o', 's', 'v', 'D', '*', 'x', '+', '<', '>', 'p', 'h']
    colors = ['b', 'g', 'm', 'k', 'teal', 'y']

    plt.figure(figsize=(8, 5))
    for i, file in enumerate(selected_files):
        file_name = os.path.basename(file)
        data = pd.read_csv(file, sep=r'\s+', comment='#', names=["coordinate", "DE_kjmol"])
        plt.plot(
            data["coordinate"],
            data["DE_kjmol"],
            marker=markers[i % len(markers)],
            linestyle='None',
            label=file_name,
            color=colors[i % len(colors)],
            markerfacecolor='none',        
            markeredgewidth=1.2            
        )

    plt.xlabel(r'$\delta$')
    plt.ylabel("Energy (kJ/mol)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def select_file_to_plot(message):
    """Allow the user to select files from different folders."""

    all_selected_files = []

    while True:
        files = filedialog.askopenfilenames(title=f"Select {message} files to plot")
        if files:
            all_selected_files.extend(files)
        else:
            break  # User cancelled

        more = messagebox.askyesno("Add file?", "Do you want to select additional files?")
        if not more:
            break

    return list(set(all_selected_files))  # Remove duplicates

def plot_modes(selected_files):
    """Plot fitted vs QM normal mode frequencies from selected files."""

    x_g09 = []
    y_g09 = []
    markers = ['o', 's', 'v', 'D', '*', 'x', '+', '<', '>', 'p', 'h']
    colors = ['b', 'g', 'm', 'k', 'teal', 'y']

    folder_names = [os.path.basename(os.path.dirname(f)) for f in selected_files]
    duplicates = {name for name in folder_names if folder_names.count(name) > 1}

    for i, file in enumerate(selected_files):
        x = []
        y = []
        parent_folder = os.path.basename(os.path.dirname(file))
        file_base = os.path.basename(file)

        if parent_folder in duplicates:
            label = f"Joyce fitted {file_base}"
        else:
            label = f"Joyce fitted {parent_folder}"

        with open(file, 'r') as f:
            start = False
            for line in f:
                if "Freq/FF" in line and "err" in line:
                    start = True
                    continue
                if start:
                    if line.strip() == "" or "Standard deviation" in line:
                        break
                    parts = line.strip().split()
                    if len(parts) == 6:
                        try:
                            x.append(float(parts[0]))
                            y.append(float(parts[1]))
                            x_g09.append(float(parts[2]))
                            y_g09.append(float(parts[3]))
                        except ValueError:
                            continue  # Skip malformed lines

        plt.plot(x, y, marker=markers[i % len(markers)], linestyle='None',
                label=label, color=colors[i % len(colors)],
                markerfacecolor='none',        
                markeredgewidth=1.2 )

    # Plot QM reference data
    combined_g09 = list(zip(x_g09, y_g09))
    sorted_combined = sorted(combined_g09, key=lambda pair: pair[0])
    x_g09_sorted, y_g09_sorted = zip(*sorted_combined)

    plt.plot(x_g09_sorted, y_g09_sorted, marker='^', linestyle=':', label="QM", color='r',
                markerfacecolor='none',        
                markeredgewidth=1.2 )
    plt.xlabel('Normal mode')
    plt.ylabel(r'$\nu$ (cm$^{-1}$)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
 
def dihedrals_from_IC(file_path, start_keyword):
    """
    Displays rows between 'start_keyword' and the next empty line.
    Allows selecting rows by click or drag, editing them, duplicating them, and saving.
    """
    import tkinter as tk
    from tkinter import messagebox, scrolledtext

    saved_lines = []
    salta_modifiche_successive = False
    i = 0
    selezione_inizio = None
    file_name = file_path.split('/')[-2] + "/" + file_path.split('/')[-1]

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    start_idx = next((idx for idx, line in enumerate(lines) if start_keyword in line), None)
    if start_idx is None:
        messagebox.showinfo("Error", f"Keyword '{start_keyword}' not found in {file_path}")
        return

    display_lines = []
    for line in lines[start_idx + 1:]:
        if line.strip() == '':
            break
        display_lines.append(line)

    split_line = display_lines[0].split()
    if len(split_line) == 10:
        number = int(split_line[8])
    elif len(split_line) == 11:
        number = int(split_line[9])
    else:
        raise ValueError(f"Formato inatteso nella riga: {display_lines[0]}")

    def open_help(_event=None):
        help_win = tk.Toplevel(window)
        help_win.title("Help — Dihedrals from IC")
        help_text = (
            "Dihedrals from IC — Help\n\n"
            "• This window lists dihedral lines found in section [Dihedrals] found in Generated.IC.txt.\n"
            "• Select lines by clicking a line (toggle) or by click-dragging to select a range.\n"
            "• Duplicate line: duplicates the highlighted lines.\n"
            "• Save: edit the necessary columns per line (7- or 8-column format), supports Undo/Skip.\n"
            "• After Save, auto-numbering is applied to the field after '#' or ';' based on the first line number.\n"
            "• Close (X) asks for confirmation and discards unsaved changes.\n\n"
            "Shortcuts:\n"
            "• F1 — Open this help.\n"
        )
        txt = scrolledtext.ScrolledText(help_win, width=80, height=20, wrap="word")
        txt.pack(padx=10, pady=10, fill="both", expand=True)
        txt.insert("1.0", help_text)
        txt.configure(state="disabled")

    def mod_column(split_line, allow_undo):
        nonlocal salta_modifiche_successive
        if salta_modifiche_successive:
            return "ok"

        separators = ['#', ';']
        for sep in separators:
            if sep in split_line:
                comment_index = split_line.index(sep)
                break
        else:
            comment_index = len(split_line)

        valid_columns = split_line[:comment_index]

        if len(valid_columns) == 7:
            return modify_7_column(split_line, allow_undo)   # <-- ritorna il risultato
        elif len(valid_columns) == 8:
            return modify_8_column(split_line, allow_undo)   # <-- ritorna il risultato
        else:
            messagebox.showerror("Error", f"Unexpected number of columns: {len(valid_columns)}")
            return "ok"

    def modify_7_column(split_line, allow_undo):
        nonlocal salta_modifiche_successive
        indices = [4, 5]  # 0-based: 5a e 6a colonna

        if salta_modifiche_successive:
            # split_line[4] = "0"; split_line[5] = "0"
            return "ok"

        win = tk.Toplevel()
        win.title("Edit Dihedral")

        tk.Label(win, text="Modify Dihedral..").grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        tk.Label(win, text="  ".join(split_line)).grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        entries = []
        for j, idx in enumerate(indices):
            tk.Label(win, text=f"Column {idx+1}:").grid(row=j+2, column=0, padx=5, pady=5)
            entry = tk.Entry(win)
            entry.insert(0, split_line[idx])
            entry.grid(row=j+2, column=1, padx=5, pady=5)
            entries.append((entry, idx))

        result = {"value": "ok"}

        def apply_all():
            for entry, idx in entries:
                value = entry.get()
                if value:
                    split_line[idx] = value
            result["value"] = "ok"
            win.destroy()

        def skip_all():
            nonlocal salta_modifiche_successive
            salta_modifiche_successive = True
            result["value"] = "ok"
            win.destroy()

        def undo_this():
            result["value"] = "undo"
            win.destroy()

        tk.Button(win, text="Apply", command=apply_all).grid(row=len(indices)+2, columnspan=2, pady=10)
        tk.Button(win, text="Skip all remaining", command=skip_all).grid(row=len(indices)+3, columnspan=2, pady=5)
        if allow_undo:
            tk.Button(win, text="Undo", command=undo_this).grid(row=len(indices)+4, columnspan=2, pady=5)

        win.grab_set()
        win.wait_window()
        return result["value"]

    def modify_8_column(split_line, allow_undo):
        nonlocal salta_modifiche_successive
        indices = [4, 5, 7]  # 0-based: 5a, 6a, 8a

        if salta_modifiche_successive:
            # split_line[4] = "0"; split_line[5] = "0"; split_line[7] = split_line[7]
            return "ok"

        win = tk.Toplevel()
        win.title("Edit Dihedral")

        tk.Label(win, text="Modify Dihedral..").grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        tk.Label(win, text="  ".join(split_line)).grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        entries = []
        for j, idx in enumerate(indices):
            tk.Label(win, text=f"Column {idx+1}:").grid(row=j+2, column=0, padx=5, pady=5)
            entry = tk.Entry(win)
            entry.insert(0, split_line[idx])
            entry.grid(row=j+2, column=1, padx=5, pady=5)
            entries.append((entry, idx))

        result = {"value": "ok"}

        def apply_all():
            for entry, idx in entries:
                value = entry.get()
                if value:
                    split_line[idx] = value
            result["value"] = "ok"
            win.destroy()

        def skip_all():
            nonlocal salta_modifiche_successive
            salta_modifiche_successive = True
            result["value"] = "ok"
            win.destroy()

        def undo_this():
            result["value"] = "undo"
            win.destroy()

        tk.Button(win, text="Apply", command=apply_all).grid(row=len(indices)+2, columnspan=2, pady=10)
        tk.Button(win, text="Skip all remaining", command=skip_all).grid(row=len(indices)+3, columnspan=2, pady=5)
        if allow_undo:
            tk.Button(win, text="Undo", command=undo_this).grid(row=len(indices)+4, columnspan=2, pady=5)

        win.grab_set()
        win.wait_window()
        return result["value"]

    def start_selection(event):
        nonlocal selezione_inizio
        selezione_inizio = textbox.index(f"@{event.x},{event.y}")

    def drag_selection(event):
        if selezione_inizio is None:
            return
        selezione_fine = textbox.index(f"@{event.x},{event.y}")
        start_line = int(selezione_inizio.split('.')[0])
        end_line = int(selezione_fine.split('.')[0])
        if start_line > end_line:
            start_line, end_line = end_line, start_line
        for line in range(start_line, end_line + 1):
            line_start = f"{line}.0"
            line_end = f"{line + 1}.0"
            textbox.tag_add("highlight", line_start, line_end)

    def finish_selection(event):
        nonlocal selezione_inizio
        selezione_fine = textbox.index(f"@{event.x},{event.y}")
        if selezione_inizio == selezione_fine:
            line_idx = selezione_inizio.split('.')[0]
            line_start = f"{line_idx}.0"
            line_end = f"{int(line_idx)+1}.0"
            if "highlight" in textbox.tag_names(line_start):
                textbox.tag_remove("highlight", line_start, line_end)
            else:
                textbox.tag_add("highlight", line_start, line_end)
        selezione_inizio = None

    def duplicate_line():
        ranges = textbox.tag_ranges("highlight")
        if not ranges:
            return
        start = ranges[0]
        end = ranges[1]
        text = textbox.get(start, end)
        textbox.insert(end, text)
        textbox.update()
        textbox.tag_remove("highlight", "1.0", tk.END)

    def save_selected_lines():
        nonlocal saved_lines

        # 1) raccogli in ordine
        ranges = textbox.tag_ranges("highlight")
        selected_lines = []
        for r in range(0, len(ranges), 2):
            start = ranges[r]
            end   = ranges[r + 1]
            current = start
            while textbox.compare(current, "<", end):
                line_start = current
                line_end   = textbox.index(f"{line_start} lineend")
                line_text  = textbox.get(line_start, line_end).strip()
                if line_text:
                    selected_lines.append(line_text)
                current = textbox.index(f"{line_end} +1c")

        if not selected_lines:
            messagebox.showwarning("Note", "No rows were selected!")
            return

        # 2) processa con indice + undo
        saved_lines.clear()
        idx = 0
        while idx < len(selected_lines):
            split_line = selected_lines[idx].split()
            result = mod_column(split_line, idx > 0)

            if result == "undo":
                if idx > 0:
                    idx -= 1
                    if saved_lines:
                        saved_lines.pop()
                else:
                    messagebox.showinfo("Undo", "Nothing to undo.")
            else:
                saved_lines.append("   ".join(split_line) + "\n")
                idx += 1

        window.quit()
        window.destroy()
        return saved_lines

    def deselect_all():
        textbox.tag_remove("highlight", "1.0", tk.END)

    def on_closing():
        nonlocal saved_lines
        answer = messagebox.askokcancel(
            "Exit",
            "Are you sure you want to close?\n\nNo dihedral will be saved if you quit."
        )
        if answer:
            saved_lines.clear()
            window.quit()
            window.destroy()

    # GUI
    window = tk.Tk()
    window.title(f"Selecting dihedrals from .../{file_name}")
    window.protocol("WM_DELETE_WINDOW", on_closing)
    # Top bar with Help + main actions
    topbar = tk.Frame(window)
    topbar.pack(fill="x", padx=10, pady=(10, 0))
    tk.Button(topbar, text="Help", command=open_help).pack(side="left", padx=(0, 6))
   
    textbox = scrolledtext.ScrolledText(window, width=100, height=30)
    textbox.pack(padx=10, pady=10)

    for line in display_lines:
        textbox.insert(tk.END, line)

    textbox.tag_configure("highlight", background="lightblue")
    textbox.bind("<ButtonPress-1>", start_selection)
    textbox.bind("<B1-Motion>", drag_selection)
    textbox.bind("<ButtonRelease-1>", finish_selection)

    tk.Button(window, text="Save", command=save_selected_lines).pack(pady=5)
    tk.Button(window, text="Duplicate line", command=duplicate_line).pack(pady=5)
    tk.Button(window, text="Deselect All", command=deselect_all).pack(pady=5)

    window.mainloop()

    # post-processing: numerazione
    if saved_lines:
        new_lines = []
        for line in saved_lines:
            if not line.strip():
                continue
            columns = line.split()
            for sep in ['#', ';']:
                if sep in columns:
                    sep_index = columns.index(sep)
                    break
            else:
                messagebox.showwarning("Warning", f"No separator ('#' or ';') found in the following line:\n{line}")
                continue

            if sep_index + 1 < len(columns):
                columns[sep_index + 1] = str(number + i)
                i += 1
            else:
                messagebox.showwarning("Warning", f"No column to number found after '{columns[sep_index]}' in the following line:\n{line}")
                continue

            new_line = '   '.join(columns) + '\n'
            new_lines.append(new_line)

        new_lines.append('\n')
        return new_lines

    return saved_lines

def pairs_from_IC(file_path, start_keyword):
    """
    Displays the lines between 'start_keyword' and the next empty line.
    Allows selecting lines via click or drag, and saving them.
    """

    original_rows = []
    # current_index = 0
    saved_lines = []
    selection_start = None
    salta_modifiche_successive = False

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    start_idx = None
    for idx, line in enumerate(lines):
        if start_keyword in line:
            start_idx = idx
            break

    if start_idx is None:
        messagebox.showinfo("Error", f"Keyword '{start_keyword}' not found in the file.")
        return

    display_lines = []
    for line in lines[start_idx + 1:]:
        if line.strip() == '':
            break
        display_lines.append(line)

    def begin_selection(event):
        nonlocal selection_start
        selection_start = textbox.index(f"@{event.x},{event.y}")

    def drag_selection(event):
        if selection_start is None:
            return
        selection_end = textbox.index(f"@{event.x},{event.y}")
        start_line = int(selection_start.split('.')[0])
        end_line = int(selection_end.split('.')[0])
        if start_line > end_line:
            start_line, end_line = end_line, start_line
        for line in range(start_line, end_line + 1):
            line_start = f"{line}.0"
            line_end = f"{line + 1}.0"
            textbox.tag_add("highlight", line_start, line_end)

    def finish_click_or_drag(event):
        nonlocal selection_start
        selection_end = textbox.index(f"@{event.x},{event.y}")
        if selection_start == selection_end:
            line_idx = selection_start.split('.')[0]
            line_start = f"{line_idx}.0"
            line_end = f"{int(line_idx)+1}.0"
            if "highlight" in textbox.tag_names(line_start):
                textbox.tag_remove("highlight", line_start, line_end)
            else:
                textbox.tag_add("highlight", line_start, line_end)
        selection_start = None

    def deselect_all():
        textbox.tag_remove("highlight", "1.0", tk.END)

    def modify__column(split_line, allow_undo):
        nonlocal salta_modifiche_successive

        indices = [3, 4, 5, 6, 7, 8]

        if salta_modifiche_successive:
            split_line[4] = "0"
            split_line[5] = "0"
            return "ok"

        win = tk.Toplevel()
        win.title("Edit Dihedral")

        tk.Label(win, text="Modify Dihedral..").grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        tk.Label(win, text="  ".join(split_line)).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        entries = []
        for i, idx in enumerate(indices):
            tk.Label(win, text=f"Column {idx}:").grid(row=i+2, column=0, padx=5, pady=5)
            entry = tk.Entry(win)
            entry.insert(0, "0" if idx in [5, 6] else split_line[idx - 1])
            entry.grid(row=i+2, column=1, padx=5, pady=5)
            entries.append((entry, idx - 1))

        result = {"value": "ok"}  # workaround per uscire da scope

        def apply_all():
            for entry, idx in entries:
                value = entry.get()
                if value:
                    split_line[idx] = value
            result["value"] = "ok"
            win.destroy()

        def skip_all():
            nonlocal salta_modifiche_successive
            salta_modifiche_successive = True
            split_line[4] = "0"
            split_line[5] = "0"
            result["value"] = "ok"
            win.destroy()

        def undo_this():
            result["value"] = "undo"
            win.destroy()

        tk.Button(win, text="Apply", command=apply_all).grid(row=len(indices)+2, columnspan=2, pady=5)
        tk.Button(win, text="Skip all remaining", command=skip_all).grid(row=len(indices)+3, columnspan=2, pady=5)
        if allow_undo:
            tk.Button(win, text="Undo", command=undo_this).grid(row=len(indices)+4, columnspan=2, pady=5)

        win.grab_set()
        win.wait_window()

        return result["value"]

    def duplicate_line():
        ranges = textbox.tag_ranges("highlight")
        if not ranges:
            return
        start, end = ranges[0], ranges[1]
        text = textbox.get(start, end)
        textbox.insert(end, text)
        textbox.update()
        textbox.tag_remove("highlight", "1.0", tk.END)

    def save_selected_lines(window):
        nonlocal saved_lines

        # Prendi le righe selezionate nell'ordine
        ranges = textbox.tag_ranges("highlight")
        selected_lines = []

        for i in range(0, len(ranges), 2):
            start = ranges[i]
            end = ranges[i + 1]
            current = start
            while textbox.compare(current, "<", end):
                line_start = current
                line_end = textbox.index(f"{line_start} lineend")
                line_text = textbox.get(line_start, line_end).strip()
                if line_text and not line_text.startswith("#") and not line_text.startswith(";"):
                    selected_lines.append(line_text)
                current = textbox.index(f"{line_end} +1c")

        if not selected_lines:
            messagebox.showinfo("Info", "No lines were selected.")
            return

        # Cicla le righe una alla volta
        original_rows.clear()
        i = 0
        while i < len(selected_lines):
            split_line = selected_lines[i].split()
            original_rows.append(split_line.copy())

            result = modify__column(split_line, i > 0)

            if result == "undo":
                if i > 0:
                    i -= 1
                    saved_lines.pop()
                else:
                    messagebox.showinfo("Undo", "Nothing to undo.")
            else:
                saved_lines.append("   ".join(split_line) + "\n")
                i += 1

        saved_lines.append('\n')
        window.quit()
        window.destroy()

    def on_closing():
        nonlocal saved_lines
        answer = messagebox.askokcancel(
            "Exit",
            "Are you sure you want to close?\n\nNo dihedral will be saved if you quit."
        )
        if answer:
            saved_lines.clear()
            window.quit()
            window.destroy()

    def skip_line():
        saved_lines.clear()
        window.quit()
        window.destroy()
        return saved_lines
    
    def open_help(_event=None):
        """Open a scrollable help window for the 'pairs_from_IC' workflow."""
        help_win = tk.Toplevel(window)
        help_win.title("Help — Pairs from IC")

        help_text = (
            "Pairs from IC — Help\n\n"
            "Overview:\n"
            "• This window lists lines found after the provided start keyword until the first blank line.\n"
            "• You can select single or multiple lines to be saved/edited.\n\n"
            "Selection:\n"
            "• Click a line to toggle its selection.\n"
            "• Click and drag to select a range of lines (highlighted in light blue).\n"
            "• 'Deselect All' clears all highlights.\n\n"
            "Editing & Saving:\n"
            "• 'Save' collects the highlighted lines (ignoring lines starting with '#' or ';').\n"
            "• For each selected line, an editor dialog lets you adjust specific columns.\n"
            "• In the editor: 'Apply' saves changes; 'Skip all remaining' skips future edits; 'Undo' reverts the previous change.\n"
            "• After finishing, the edited lines are returned by the function (one per line, with a trailing blank line).\n\n"
            "Other Actions:\n"
            "• 'Duplicate line' duplicates the current highlighted block at the end of the block.\n"
            "• 'Skip pair saving' closes the window and returns an empty result.\n"
            "• Closing the window (X) asks for confirmation and discards unsaved changes if confirmed.\n\n"
            "Shortcuts:\n"
            "• F1 — Open this help.\n"
        )

        txt = scrolledtext.ScrolledText(help_win, width=90, height=24, wrap="word")
        txt.pack(padx=10, pady=10, fill="both", expand=True)
        txt.insert("1.0", help_text)
        txt.configure(state="disabled")

    # GUI setup
    window = tk.Tk()
    window.title("Select pairs to save")
    window.protocol("WM_DELETE_WINDOW", on_closing)
    # Top bar with Help + main actions
    topbar = tk.Frame(window)
    topbar.pack(fill="x", padx=10, pady=(10, 0))

    tk.Button(topbar, text="Help", command=open_help).pack(side="left", padx=(0, 6))
   
    textbox = scrolledtext.ScrolledText(window, width=100, height=30)
    textbox.pack(padx=10, pady=10)

    for line in display_lines:
        textbox.insert(tk.END, line)

    textbox.tag_configure("highlight", background="lightblue")
    textbox.bind("<ButtonPress-1>", begin_selection)
    textbox.bind("<B1-Motion>", drag_selection)
    textbox.bind("<ButtonRelease-1>", finish_click_or_drag)

    tk.Button(window, text="Save", command=lambda: save_selected_lines(window)).pack(pady=5)
    tk.Button(window, text="Skip pair saving", command=skip_line).pack(pady=5)
    tk.Button(window, text="Duplicate line", command=duplicate_line).pack(pady=5)
    tk.Button(window, text="Deselect All", command=deselect_all).pack(pady=5)

    window.mainloop()
    return saved_lines
    
def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'+{x}+{y}')

def copy_files(in_path, in_name, out_path, out_name):

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

def edit_inp_file(file_path, result_conteiner):

    # clicked_index = None
    file_name = os.path.basename(file_path)
    specie_name = file_name.split(".")[1]


    def new_dependence():
        # nonlocal clicked_index

        selected_lines = []
        built_lines = []
        selected_output_index = [None]
        
        file_top_path = filedialog.askopenfilename(title="Select topology file")

        def on_click(event):
            index = text_widget.index(f"@{event.x},{event.y}")
            line_num = int(index.split('.')[0])
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            line_text = text_widget.get(line_start, line_end)

            if line_text.strip().startswith(";") or not line_text.strip():
                return

            # Se la riga è già selezionata, rimuovila (deselezione)
            for i, (ln, _, tag) in enumerate(selected_lines):
                if ln == line_num:
                    text_widget.tag_delete(tag)
                    selected_lines.pop(i)
                    generate_button.config(state=tk.NORMAL if len(selected_lines) == 2 else tk.DISABLED)
                    return

            # Se sono già selezionate 2 righe, blocca
            if len(selected_lines) >= 2:
                messagebox.showwarning("Warning", "You have already selected 2 lines. Click 'Generate' or deselect.")
                return

            # Altrimenti seleziona la riga
            tag_name = f"sel_{line_num}"
            text_widget.tag_add(tag_name, line_start, line_end)
            text_widget.tag_config(tag_name, background="lightblue")
            selected_lines.append((line_num, line_text, tag_name))

            if len(selected_lines) == 2:
                generate_button.config(state=tk.NORMAL)
        
        def generate_line():
            if len(selected_lines) != 2:
                return

            def split_line(line):
                if ';' in line:
                    return line.split(';', 1)[1].strip().split(maxsplit=1)
                elif '#' in line:
                    return line.split('#', 1)[1].strip().split(maxsplit=1)
                else:
                    raise ValueError("Missing separator (';' or '#') in line")

            # Ordina in base al numero estratto dopo ; o #
            sorted_lines = sorted(
                selected_lines,
                key=lambda x: int(split_line(x[1])[0])
            )

            (_, line1, _), (_, line2, _) = sorted_lines

            try:
                num1, desc1 = split_line(line1)
                num2, desc2 = split_line(line2)
            except Exception as e:
                messagebox.showerror("Error", f"Error parsing lines:\n{e}")
                return
            # Decidi quale numero è minore
            if int(num1) < int(num2):
                major_num = num2
                minor_num = num1
                descriptor = desc1
            else:
                major_num = num1
                minor_num = num2
                descriptor = desc2
            line_normal = f"{major_num} =    {minor_num}*1.d0   # {descriptor:20} = {descriptor}"

            # Inseriamo SEMPRE la versione normale nell'output
            output_widget.insert(tk.END, line_normal + "\n")
                
            # Salviamo TUTTE le versioni per controllare duplicati
            built_lines.append("     " + line_normal)

            clear_highlights()
            selected_lines.clear()
            generate_button.config(state=tk.DISABLED)

        def clear_highlights():
            for _, _, tag in selected_lines:
                text_widget.tag_delete(tag)

        def on_output_click(event):
            index = output_widget.index(f"@{event.x},{event.y}")
            line_num = int(index.split('.')[0])

            output_widget.tag_delete("out_sel")
            output_widget.tag_add("out_sel", f"{line_num}.0", f"{line_num}.end")
            output_widget.tag_config("out_sel", background="salmon")

            selected_output_index[0] = line_num - 1

        def delete_selected_output_line():
            idx = selected_output_index[0]
            if idx is None or idx >= len(built_lines):
                return

            output_widget.delete(f"{idx + 1}.0", f"{idx + 1}.end + 1c")
            del built_lines[idx]
            selected_output_index[0] = None
            output_widget.tag_delete("out_sel")

        def normalize_line(line):
            """
            Rimuove spazi iniziali/finali e comprime spazi multipli.
            """
            return re.sub(r'\s+', ' ', line.strip())

        def save_and_exit():
            output_text = ""

            dep_pos = text_area.search("dependence", "1.0", tk.END)

            if dep_pos:
                line_index = int(dep_pos.split('.')[0])
                insert_index = f"{line_index + 1}.0"

                # Trova fine blocco
                end_pos = text_area.search("$end", insert_index, tk.END)
                if not end_pos:
                    messagebox.showerror("Error", "Found 'dependence' but not '$end' marker.", parent=root)
                    return

                end_line_idx = int(end_pos.split('.')[0])

                # Raccogli righe esistenti con numeri
                existing_lines = {}
                for i in range(line_index + 1, end_line_idx):
                    line_text = text_area.get(f"{i}.0", f"{i}.end")
                    normalized = normalize_line(line_text)
                    if normalized:
                        try:
                            first_number = int(normalized.split()[0])
                            existing_lines[first_number] = line_text.strip()
                        except ValueError:
                            pass  # ignora righe che non iniziano con numero

                # Controlla duplicati e aggiungi nuove righe
                duplicates = []
                for line in built_lines:
                    normalized = normalize_line(line)
                    try:
                        first_number = int(normalized.split()[0])
                    except ValueError:
                        continue

                    if first_number in existing_lines:
                        duplicates.append(line.strip())
                    else:
                        existing_lines[first_number] = line.strip()

                if not existing_lines:
                    messagebox.showinfo("Info", "No valid lines to save.")
                    return

                if duplicates:
                    messagebox.showinfo(
                        "Duplicates",
                        "Some lines were already present and were skipped:\n\n" +
                        "\n".join(duplicates),
                        parent=root
                    )

                # Ordina per numero
                sorted_lines = [existing_lines[k] for k in sorted(existing_lines.keys())]

                # Sostituisci l'intero blocco dependence
                # Rimuovi righe vecchie
                text_area.delete(f"{line_index + 1}.0", f"{end_line_idx}.0")

                # Inserisci righe ordinate
                new_text = ""
                for line in sorted_lines:
                    new_text += "   " + line + "\n"
                text_area.insert(f"{line_index + 1}.0", new_text)

            else:
                # Se non c'è dependence, crea blocco nuovo
                block = "$dependence 1.2\n"
                for line in built_lines:
                    block += "   " + line.strip() + "\n"
                block += "$end\n"
                text_area.insert(tk.END, block)

            root.destroy()

        # GUI setup
        root = tk.Tk()
        root.title(f"Line selection - {file_top_path}")

        text_widget = scrolledtext.ScrolledText(root, width=80, height=20)
        text_widget.pack(padx=10, pady=10)
        text_widget.bind("<Button-1>", on_click)

        generate_button = tk.Button(root, text="Generate", command=generate_line, state=tk.DISABLED)
        generate_button.pack(pady=5)

        output_widget = scrolledtext.ScrolledText(root, width=80, height=10)
        output_widget.pack(padx=10, pady=5)
        output_widget.bind("<Button-1>", on_output_click)

        delete_button = tk.Button(root, text="Delete selected line", command=delete_selected_output_line)
        delete_button.pack(pady=2)

        continue_button = tk.Button(root, text="Continue", command=save_and_exit)
        continue_button.pack(pady=5)

        try:
            with open(file_top_path) as f:
                text_widget.insert(tk.END, f.read())
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {file_top_path}")
            root.destroy()

        root.mainloop()

    def on_text_change(event):
        update_combobox_words()

    def load_dependecies():
        species_name, base_folder, step0_folder, step1_folder, step2_folder = capture_current_directory()
        dep_file_path = os.path.join(step1_folder, "suggdeps.txt")

        if not os.path.exists(dep_file_path):
            messagebox.showerror("Error", f"File {dep_file_path} does not exist")
            return

        with open(dep_file_path, 'r') as file:
            lines = [line.rstrip('\n') for line in file if line.strip()]  # ignora righe completamente vuote

        if not lines or len(lines) < 3:
            messagebox.showwarning("Warning", f"{dep_file_path} does not contain enough lines to trim.")
            return

        pos = text_area.search("dependence", "1.0", tk.END)

        if pos:
            # Elimina la prima e l'ultima riga effettiva
            trimmed_lines = lines[1:-1]
            content = '\n'.join(trimmed_lines)
            line_index = int(pos.split('.')[0])
            insert_index = f"{line_index + 1}.0"
            text_area.insert(insert_index, content + "\n")
        else:
            # Inserisci tutto (non tagliato)
            full_content = '\n'.join(lines)
            text_area.insert(tk.END, full_content)

        # update_line_numbers()
        update_combobox_words()

    def load_assign():

        species_name, base_folder, step0_folder, step1_folder, step2_folder = capture_current_directory()
        dep_file_path = os.path.join(step1_folder, "assign.dat")
        if os.path.exists(dep_file_path):
            content = []
            with open(dep_file_path, 'r') as file:
                content = file.read()
                # content.append("\n")
            text_area.insert(tk.END, content)
            # update_line_numbers()
            update_combobox_words()


        else:
            messagebox.showerror("Error", f"File {dep_file_path} does not exist")

    def save_file():
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
            root.title(f"Editor - {file_path} (Saved)")
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")
    
    def save_file_as():

        file_path = filedialog.asksaveasfilename(title="Save file as...")
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
            root.title(f"Editor - {file_path} (Saved)")
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")

    def continue_to_joyce():
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
            root.title(f"Editor - {file_path} (Saved)")
            root.quit()
            root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")

    def create_inp_file():
        species_name, base_folder, step0_folder, step1_folder, step2_folder = capture_current_directory()
        inp_file = os.path.join(step0_folder, "joyce." + species_name + ".inp")

        try:
            with open(inp_file, "r", encoding="utf-8") as file:
                content = file.read()
                content = content.replace("Step 0", "Step 1")
                text_area.delete("1.0", tk.END)
                text_area.insert(tk.END, content)
                # update_line_numbers()
                update_combobox_words()
                update_file()
        except Exception as e:
            messagebox.showerror("Error", f"Error while creating the file:\n{e}")
        return first_words

    def cancel_action():
        result_conteiner["value"] = "CANCELLED"
        root.quit()
        root.destroy()
        return
        # sys.exit()

    def extract_first_words():
        content = text_area.get("1.0", tk.END)
        lines = content.split("\n")
        first_words = []
        for line in lines:
            line = line.strip()
            if line and line.startswith("$") and not line.startswith(";"):
                first_word = line.split()[0]
                first_words.append(first_word)
        return first_words

    def insert_keyword():
        # nonlocal clicked_index

        selected2 = word_combobox2.get()
        end_word = ""
        if selected2 == "$dependence" or selected2 == "$assign":
            if selected2 == "$dependence":
                selected2 = "$dependence 1.2"
            end_word = "$end"

        command2 = entry2.get()

        if not selected2:
            messagebox.showerror("Error", "No word selected!")
            return

        if end_word:
            new_phrase ="\n" + selected2 + "\n" + end_word
        else:
            new_phrase ="\n" + selected2 + " " + command2

        # text_area.insert(clicked_index, new_phrase + "\n")
        text_area.insert(tk.END, new_phrase)
        update_file()
        entry2.delete(0, tk.END)
        # update_line_numbers()
        update_combobox_words()

    def update_combobox_words():
        first_words = extract_first_words()
        word_combobox1['values'] = first_words
        word_combobox1.set(first_words[0] if first_words else "")
        # line_numbers = update_line_numbers()

    def update_file():
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
            root.title(f"Editor - {file_path} (Saved)")
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")

    def erase():
        selected = word_combobox1.get()
        if not selected:
            messagebox.showerror("Error", "You must select a word!")
            return
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as e:
            messagebox.showerror("Error", f"Error while opening the file:\n{e}")
            return
        lines = content.splitlines()
        new_lines = [line for line in lines if not line.startswith(selected)]
        new_content = "\n".join(new_lines)
        text_area.replace("1.0", tk.END, new_content)
        # update_line_numbers()
        update_file()
        update_combobox_words()

    def load_geom(parent=None):
        """
        Ask the user for a folder and build:
        1) A $geom ... $end block listing .fchk/.fcc files grouped by scanX.Y,
            with first of each group marked '; i j k l' and the rest with '-f'.
        2) For each distinct 'scanX' group, append a $scan joyce.scanX.dat block:
                $scan joyce.scan1.dat
                i j k l ; -180. 180. 1.
                $end

        The final text is inserted into a Tkinter Text widget named `text_area`.
        """
        # Natural sort key for paths like 'scan3.12.fchk'
        def sort_key(path: Path):
            name = path.stem
            m = re.match(r"(scan\d+)\.(\d+)", name)
            if m:
                prefix = m.group(1)
                num = int(m.group(2))
                return (prefix, num)
            else:
                return (name, float("inf"))

        # Ask the folder
        folder_selected = filedialog.askdirectory(
            title="Select folder containing scans",
            parent=parent
        )
        if not folder_selected:
            return

        base_path = Path(folder_selected)
        all_files = list(base_path.rglob("*.fchk")) + list(base_path.rglob("*.fcc"))

        # Exclude exact 'opt+freq'
        filtered_files = [f for f in all_files if f.stem != "opt+freq"]

        # Sort
        sorted_files = sorted(filtered_files, key=sort_key)

        # Build $geom
        content_lines = []
        content_lines.append("$geom")
        last_prefix = None
        seen_prefixes_in_order = []  # keep distinct scan prefixes in the order encountered

        for path in sorted_files:
            name = Path(path).stem
            m = re.match(r"(scan\d+)\.(\d+)", name)
            prefix = m.group(1) if m else None

            if prefix != last_prefix:
                # first row of a group
                line = f"{path}   5.0   0.0   0.0   0.0   ; i j k l"
                last_prefix = prefix
                if prefix and (not seen_prefixes_in_order or seen_prefixes_in_order[-1] != prefix):
                    seen_prefixes_in_order.append(prefix)
            else:
                # subsequent rows of the same group
                line = f"{path}   5.0   0.0   0.0   0.0   -f"

            content_lines.append(line)

        content_lines.append("$end")

        # Append one $scan block per distinct 'scanX'
        for prefix in seen_prefixes_in_order:
            # Example: prefix = 'scan1' -> joyce.scan1.dat
            content_lines.append(f"$scan {specie_name}.joyce.{prefix}.dat")
            content_lines.append("i  j  k  l  ;  -180. 180. 1.")
            content_lines.append("$end")

        # Remove empty lines defensively and ensure trailing newline
        non_empty_lines = [ln for ln in content_lines if str(ln).strip()]
        content = "\n".join(non_empty_lines) + "\n"

        # Insert into the Tkinter Text widget named `text_area`
        text_area.insert(tk.END, content)
        return

    def open_help(_event=None):
        """Open a scrollable help window for the INP editor workflow."""
        help_win = tk.Toplevel(root)
        help_win.title("Help — INP Editor")

        help_text = (
            "INP Editor — Help\n\n"
            "Overview:\n"
            "• This window lets you view and edit a .inp file in the main text area.\n"
            "• The left panel offers file/block operations; the right panel inserts or loads blocks.\n\n"
            "Main Text Area:\n"
            "• Shows the current .inp content. Edits here are written back by Save/Continue.\n"
            "• The keywords list (comboboxes) is built from the first token of lines starting with '$'.\n\n"
            "Left Panel — Actions:\n"
            "• Erase: remove all lines starting with the selected keyword from the left combobox.\n"
            "• Generate new inp. file: load Step 0 template (joyce.<species>.inp) into the editor and switch it to Step 1.\n"
            "• Save file / Save file as: write the editor content to disk.\n"
            "• Cancel: close the editor without saving and exit the program.\n\n"
            "Right Panel — Actions:\n"
            "• Confirm keywords: insert the selected keyword from the right combobox.\n"
            "  - If '$dependence' is chosen, '$dependence 1.2' and the closing '$end' are inserted.\n"
            "  - Otherwise the keyword plus the text typed in the entry field are inserted at the end of the file.\n"
            "• Load dependencies: read Step 1 'suggdeps.txt' and insert its body (without the first/last line) "
            "  below the '$dependence' block if present, otherwise append it.\n"
            "• Create dependencies: open the line-selection tool to build dependence lines by selecting 2 entries in a topology file. "
            "  - Click two lines (non-empty, not starting with ';') to enable 'Generate'.\n"
            "  - 'Generate' creates a normalized line '<major> = <minor>*1.d0  # <desc> = <desc>' and sends it to the output panel.\n"
            "  - You can delete items from the output list, then 'Continue' merges them into the '$dependence 1.2' block, "
            "    avoiding duplicates and keeping numeric order.\n"
            "• Load assign: load 'assign.dat' from Step 1 and append it to the editor.\n"
            "• Load geom: open a folder and build a '$geom ... $end' block listing .fchk/.fcc (grouped by scanX.Y), "
            "  plus one '$scan <species>.joyce.scanN.dat ... $end' block per distinct scan group, appended to the editor.\n"
            "• Continue: save the current editor content to the original file and close the window.\n\n"
            "Selection tool (Create dependencies) — Notes:\n"
            "• In the top text area, single-click toggles a line selection; selecting two lines enables 'Generate'.\n"
            "• The output list supports click-to-select and deletion of the selected line.\n"
            "• On 'Continue', lines are merged into the '$dependence' block; duplicates by first integer are skipped.\n\n"
            "Tips & Shortcuts:\n"
            "• Use the right combobox + entry to quickly append parameterized blocks.\n"
            "• Consider binding F1 to this help: root.bind('<F1>', open_help).\n\n"
            "Warnings:\n"
            "• Save/Continue overwrite the target file with the current editor content.\n"
            "• 'Cancel' quits the app immediately.\n"
        )

        txt = scrolledtext.ScrolledText(help_win, width=90, height=28, wrap="word")
        txt.pack(padx=10, pady=10, fill="both", expand=True)
        txt.insert("1.0", help_text)
        txt.configure(state="disabled")

    root = tk.Tk()
    root.title(f"Editing of {file_path}")
    root.protocol("WM_DELETE_WINDOW", cancel_action)
        
    # Top bar with Help + main actions
    topbar = tk.Frame(root)
    topbar.pack(fill="x", padx=10, pady=(10, 0))
    tk.Button(topbar, text="Help", command=open_help).pack(side="left", padx=(0, 6))
    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both", padx=10, pady=10)


    text_area = tk.Text(frame, wrap=tk.WORD, font=("Arial", 12))
    text_area.pack(side="left", expand=True, fill="both")

    scrollbar = tk.Scrollbar(frame, orient="vertical")
    scrollbar.pack(side="left", fill="y")

    text_area.bind("<KeyRelease>", on_text_change)

    side_panel2 = tk.Frame(frame)
    side_panel2.pack(side="right", fill="y", padx=10)

    side_panel1 = tk.Frame(frame)
    side_panel1.pack(side="right", fill="y", padx=10)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = [line for line in file.readlines() if line.strip()]
            content = "".join(lines)
        text_area.insert(tk.END, content)
    except Exception as e:
        text_area.insert(tk.END, f"Error while opening the file:\n{e}")

    first_words = extract_first_words()

    tk.Label(side_panel1, text="Select K-word to eliminate").pack()
    tk.Label(side_panel2, text="Select K-word to insert").pack()

    word_combobox1 = ttk.Combobox(side_panel1, values=first_words, state="readonly")
    word_combobox1.set(first_words[0] if first_words else "")
    word_combobox1.pack(pady=5)

    word_combobox2 = ttk.Combobox(side_panel2, values=DEFAULT_KEYWORDS, state="readonly")
    word_combobox2.set(DEFAULT_KEYWORDS[0])
    word_combobox2.pack(pady=5)

    tk.Label(side_panel2, text="Insert mode for selected keywords").pack(pady=5)
    entry2 = tk.Entry(side_panel2)
    entry2.pack(pady=(5,10))

    #Button left panel
    tk.Button(side_panel1, text="Erase", command=erase).pack(pady=10)
    tk.Button(side_panel1, text="Generate new inp. file", command=create_inp_file).pack(pady=10)
    tk.Button(side_panel1, text="Save file", command=save_file).pack(pady=10, padx=10)
    tk.Button(side_panel1, text="Save file as", command=save_file_as).pack(pady=10, padx=10)
    tk.Button(side_panel1, text="Cancel", command=cancel_action).pack(side="bottom", pady=10, padx=10)

    #Button right panel
    tk.Button(side_panel2, text="Continue", command=continue_to_joyce).pack(side="bottom", pady=10, padx=10)
    tk.Button(side_panel2, text="Confirm keywords", command=insert_keyword).pack(padx=10, pady=5)
    tk.Button(side_panel2, text="Load dependencies", command=load_dependecies).pack(padx=10, pady=5)
    tk.Button(side_panel2, text="Create dependencies", command=new_dependence).pack(padx=10, pady=5)
    tk.Button(side_panel2, text="Load assign", command=load_assign).pack(padx=10, pady=5)
    tk.Button(side_panel2, text="Load geom", command=load_geom).pack(padx=10, pady=5)

    center_window(root)
    root.mainloop()

def create_folders():
    global STEP0_FOLDER, STEP1_FOLDER, STEP2_FOLDER, BASE_FOLDER
    message = "No Step folders were found."
    show_message(message)
    root = tk.Tk()
    root.withdraw()  # Hides the main Tkinter window

    # Select the main folder
    base_path = os.getcwd()
    # If the user closes the window without selecting anything (cancel or close button)
    if not base_path:
        messagebox.showinfo("Operation Canceled", "No folder selected.")
        root.quit()
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
        root.quit()
        root.destroy()  # Close the Tkinter window
        return  # Stop function execution

    # Ask for confirmation before creating the missing folders
    response = messagebox.askyesno(
        "Confirmation",
        f"Do you want to create the following folders in:\n{base_path}?\n\n" + "\n".join(folders_to_create)
    )

    if not response:
        messagebox.showinfo("Operation Canceled", "No folder created.")
        root.quit()
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

    root.quit()
    root.destroy()  # Close the Tkinter window

def run_go_joyce(run_folder, species_name):
    command = ["go.joyce", species_name]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=run_folder
        )

        output = result.stdout.lower() + result.stderr.lower()

        if "swap" in output:
            messagebox.showinfo("Info", "Swap warning detected, but proceeding.")
            messagebox.showinfo("INFO", f"Command output:\n{result.stdout}")
        # else:
        #     messagebox.showinfo("INFO", f"Command output:\n{result.stdout}")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error while executing the command:\n{e}")
        return

    # Alla fine: chiedi se mostrare il file .out
    out_files = list(Path(run_folder).glob("*.out"))
    if not out_files:
        messagebox.showwarning("Warning", "No .out file found in the run folder.")
        return

    out_file = out_files[0]

    if messagebox.askyesno("go.joyce has finished", f"Do you want to view the output file:\n{out_file.name}?"):
        show_output_file(out_file)

def show_output_file(out_file_path):
    """
    Apre una finestra Tkinter per visualizzare il contenuto del file.
    """
    viewer = tk.Tk()
    viewer.title(f"Viewing: {out_file_path.name}")

    text_widget = scrolledtext.ScrolledText(viewer, wrap=tk.WORD, width=100, height=30)
    text_widget.pack(fill=tk.BOTH, expand=True)

    try:
        with open(out_file_path, "r") as f:
            content = f.read()
    except Exception as e:
        messagebox.showerror("Error", f"Could not read file:\n{e}")
        viewer.destroy()
        return

    text_widget.insert(tk.END, content)
    text_widget.config(state=tk.DISABLED)

def select_and_copy_file(destination, warning_message):
    # Create the Tkinter window but do not show it
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Show the warning message
    messagebox.showinfo("Warning", warning_message)

    # Ask the user to select a .top file
    selected_file = filedialog.askopenfilename(
        title="Select topology file",
        filetypes=[("Text files", "*.top")]  # Only .top files
    )

    # If the user cancels or closes the window (selected_file is an empty string)
    if not selected_file:
        messagebox.showinfo("INFO","Operation canceled by the user.")
        root.quit()
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
        messagebox.showinfo("INFO", f"File successfully copied to {full_destination}")
        # print(f"File successfully copied to {full_destination}")
    except Exception as e:
        messagebox.showerror("ERROR", f"An error occurred while copying the file {e}")
        # print(f"An error occurred while copying the file: {e}")

    # Destroy the Tkinter window to free up resources
    root.quit()
    root.destroy()

def capture_current_directory():

    name = ""
    base_folder = os.getcwd()
    step0_folder = os.path.join(base_folder, "Step0")
    step1_folder = os.path.join(base_folder, "Step1")
    step2_folder = os.path.join(base_folder, "Step2")

    exists = any(os.path.isfile(os.path.join(step0_folder, f)) and f.endswith(".top") for f in os.listdir(step0_folder))

    if exists:
        # Prende il primo file .top e ne estrae solo il nome prima del primo punto
        top_files = [f for f in os.listdir(step0_folder) if f.endswith(".top")]
        base_filename = os.path.splitext(top_files[0])[0]
        name = base_filename.split(".")[0]
        return name, base_folder, step0_folder, step1_folder, step2_folder
    else:
        message = "No topology file was found inside the Step 0 folder"
        select_and_copy_file(step0_folder, message)
        top_files = [f for f in os.listdir(step0_folder) if f.endswith(".top")]
        base_filename = os.path.splitext(top_files[0])[0]
        name = base_filename.split(".")[0]
        return name, base_folder, step0_folder, step1_folder, step2_folder

def read_before_and_after(file_path, word1, word2):
    """
    Reads a file and returns the lines before `word1` and after `word2`,
    excluding the lines containing `word1` and `word2` and the entire block between them.
    """
    lines_before = []
    lines_after = []
    collect_after = False
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
        messagebox.showerror("ERROR",f"Error: The file '{file_path}' was not found.")
        return [], []

def write_file(file_path, lines):
    """Writes the lines into a file."""
    try:
        with open(file_path, 'w') as file:
            file.writelines(lines)
    except Exception as e:
        messagebox.showerror("ERROR",f"Error writing the file '{file_path}': {e}")

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
        messagebox.showerror("ERROR",f"Error: The file '{file_path}' was not found.")
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

    except FileNotFoundError:
        messagebox.showerror("ERROR",f"Error: The file '{file_path}' was not found.")

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

def show_message(message):
    # Create the main window
    rootmex = tk.Tk()
    rootmex.title("INFO")
    rootmex.geometry("400x150")

    # Create a label with the message
    label = tk.Label(rootmex, text=message, font=("Arial", 14), wraplength=350)
    label.pack(pady=30)  # Add some space above and below the text

    # Add a button to close the window
    button = tk.Button(rootmex, text="OK", command=rootmex.destroy)
    button.pack()

    # Start the main tkinter loop
    center_window(rootmex)
    rootmex.mainloop()

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
        sys.exit()

    # Create the main window
    root = tk.Tk()
    root.title("Joyce GUI")
    root.geometry("250x320")

    # Configure window closing to stop execution
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Create the buttons
    button_width = 20  # adjust this number until all look good
    button1 = tk.Button(root, text="Step 0", width=button_width, command=lambda: on_button_click("Step 0"))
    button1.pack(pady=(15,5))

    button2 = tk.Button(root, text="Step 1", width=button_width, command=lambda: on_button_click("Step 1"))
    button2.pack(pady=5)

    button3 = tk.Button(root, text="Step 2", width=button_width, command=lambda: on_button_click("Step 2"))
    button3.pack(pady=5)

    button4 = tk.Button(root, text="Display molecule", width=button_width, command=lambda: on_button_click("Display molecule"))
    button4.pack(pady=5)

    button5 = tk.Button(root, text="Plot Modes", width=button_width, command=lambda: on_button_click("Plot_modes"))
    button5.pack(pady=5)

    button6 = tk.Button(root, text="Plot Torsional Profile", width=button_width, command=lambda: on_button_click("Plot"))
    button6.pack(pady=5)

    # Add the "Quit" button
    cancel_button = tk.Button(root, text="Quit", width=button_width, command=on_close)
    cancel_button.pack(pady=5)

    # Start the main tkinter loop
    center_window(root)
    root.winfo_screenheight
    root.mainloop()

    return result  # Returns the value of the result variable

def step0():
    global opt_freq_path

    def select_optfreq():
        """
        Ask the user if they want to select a file.
        If yes, open a file dialog and return its path.
        If no or canceled, return None.
        """
        root = tk.Tk()
        root.withdraw()

        # Ask confirmation
        proceed = messagebox.askyesno("File Selection", "Do you want to select a Gaussian checkpoint file?")

        if not proceed:
            # messagebox.showinfo("Info", "You chose not to select any file.")
            return None, None

        # If yes → open dialog
        selected_file = filedialog.askopenfilename(
            title="Select Gaussian checkpoint file"
        )

        if not selected_file:
            messagebox.showwarning("Cancelled", "No file was selected.")
            return None, None

        return selected_file, proceed

    def create_inp_file(path, optfreq, species_name):
        global inp_step0_name

        inp_step0_name = "joyce." + species_name + ".inp"
        inp_file = os.path.join(step0_folder, inp_step0_name)
        with open(inp_file, 'w') as file:

            file.write("$title " + species_name +  " - Step 0 -\n")
            if optfreq:file.write("$equil " + optfreq + "\n")
            else: file.write("$equil\n")
            file.write("$forcefield gromacs " + species_name + ".top\n")
            file.write("$generate\n")
            messagebox.showinfo("Info", f"The file joyce.{species_name}.inp has been generated inside the '{os.path.basename(path)}' folder.")

        return
    
    def search_inp_file(path):
        """
        Scan the given folder `path` and check if there are any .inp files.
        Returns True if at least one is found, otherwise False.
        """
        p = Path(path)
        if not p.is_dir():
            return False

        inp_files = list(p.rglob("*.inp"))
        return len(inp_files) > 0

    species_name, _, step0_folder, _, _ = capture_current_directory()
    inp_true = search_inp_file(step0_folder)
    if inp_true:
        ans = messagebox.askyesno(title="Warning", message="Input file found!\nDo you want to run Joyce on it?\nChoosing 'NO' new input file will be generated.")
        if ans:
            run_go_joyce(step0_folder, species_name)
            return
    opt_freq_path, proceed = select_optfreq()
    create_inp_file(step0_folder, opt_freq_path, species_name)
    if proceed:
        run_go_joyce(step0_folder, species_name)
    else:
        messagebox.showinfo("Warning!","No Gaussian checkpoint file selected:\n$equil keyword requires file's path!\nExecution aborted.")

def step1():

    result_conteiner = {"value": None} 
    specie_name, _, step0_folder, step1_folder, _ = capture_current_directory()
    inp_step0_name = "joyce." + specie_name + ".inp"
    inp_step1_name = "joyce." + specie_name + ".inp"
    path_IC = os.path.join(step0_folder, "generated.IC.txt")
    stop_word_top = 'bonds'
    stop_word_top_2 = 'system'
    extension = ".top"
    path_top_file = os.path.join(step0_folder, specie_name)
    lines_before, lines_after = read_before_and_after(path_top_file + extension, stop_word_top, stop_word_top_2)
    bonds_and_angles_IC = read_range_between_words(path_IC, "; Stretchings", "; Torsions")
    dihedrals_header = ["[ dihedrals ]\n ; ai   aj   ak   al\n"]
    pairs_header = ["; Nonbonded terms\n [ pairs ]\n; 1-4 interactions\n"]

    ans = messagebox.askyesno("INFO","Do you want to select dihedrals and pairs?")
    if ans:
        if lines_before and lines_after:
            saved_dihedrals = dihedrals_from_IC(path_IC,"dihedrals")
            saved_pairs = pairs_from_IC(path_IC, "pairs")
            modified_lines = lines_before + bonds_and_angles_IC + dihedrals_header + saved_dihedrals + pairs_header + saved_pairs + lines_after
            write_file(os.path.join(step1_folder, (specie_name + ".top")), modified_lines)
    
    if not os.path.isfile(os.path.join(step1_folder, inp_step1_name)):
        copy_files(step0_folder, inp_step0_name, step1_folder, inp_step1_name)

    file_to_read = os.path.join(step1_folder, inp_step1_name)
    replace_word(file_to_read, "Step 0", "Step 1")
    edit_inp_file(file_to_read, result_conteiner)
    if result_conteiner["value"] != "CANCELLED":
        run_go_joyce(step1_folder, specie_name)

def step2():
    
    result_conteiner = {"value": None} 
    specie_name, _, _, step1_folder, step2_folder = capture_current_directory()
    inp_step1_name = "joyce." + specie_name + ".inp"
    inp_step2_name = "joyce." + specie_name + ".inp"
    top_step1_name = specie_name + ".top"
    top_step2_name = specie_name + ".top"
    if not os.path.isfile(os.path.join(step2_folder, inp_step2_name)):
        copy_files(step1_folder, inp_step1_name, step2_folder, inp_step2_name)
    if not os.path.isfile(os.path.join(step2_folder, top_step2_name)):
        copy_files(step1_folder, top_step1_name, step2_folder, top_step2_name)
    file_to_read = os.path.join(step2_folder, inp_step2_name)
    replace_word(file_to_read, "Step 1", "Step 2")

    edit_inp_file(file_to_read, result_conteiner)
    if result_conteiner["value"] != "CANCELLED":
        run_go_joyce(step1_folder, specie_name)

def display_molecule():
    """Open moden on a selected file"""
    selected_file = filedialog.askopenfilename(title="Select file to open with Molden")
    if not selected_file:
        messagebox.showerror("Warning", "No file selected")
        return
    
    command = ["molden", selected_file]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)

    except subprocess.CalledProcessError as e:
        messagebox.showinfo("Info", f"Error while executing the command: {e}")

def main():

    exists = check_step_folders()
    if exists == "no":
        create_folders()

    # Initialize step variable
    step=""
    while step!= "cancel":
        step = ask_for_step()
        if step == "Step 0":
            exists = check_step_folders()
            if exists == "no":
                messagebox.showerror(title="ERROR", message="No folder Step0 found, execution aborted")
                continue
            step0()
        elif step == "Step 1":
            exists = check_step_folders()
            if exists == "no":
                messagebox.showerror(title="ERROR", message="No folder Step0 found, execution aborted")
                continue
            step1()
        elif step == "Step 2":
            exists = check_step_folders()
            if exists == "no":
                messagebox.showerror(title="ERROR", message="No folder Step0 found, execution aborted")
                continue
            step2()
        elif step == "Plot":
            message = "scan file"
            selected_files = select_file_to_plot(message)
            if not selected_files:
                return
            plot_torsional_profile(selected_files)
        elif step == "Plot_modes":
            message = "output file"
            selected_files = select_file_to_plot(message)
            if not selected_files:
                return
            plot_modes(selected_files)
        elif step == "Display molecule":
            display_molecule()

if __name__ == "__main__":
    main()
