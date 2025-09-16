#!/usr/bin/env python3
import os, shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, simpledialog
import subprocess
import psutil
import sys
import re

WORDS_PICKYFIT_TEMPLATE = ["LJ>", "Coul>", "Fix_LJ>", "Fix_Coul>", "$weig"]

SUGGESTED_KWORDS = [
    "$Traj", "$Parameters", "$Ndimer", "$Accepted", "$Rmax", "$Rmin",
    "$Emax", "$Emin", "$Random", "$DI_threshold", "$DI_weights", "$rigid",
    "$axisL", "$axisS", "$axisChain", "$intraw",
    "$QM_method", "$QM_basis", "$QM_disp", "$molecule", "$virtual",
    "$potpar", "$fixpar", "$weig", "$dimergeom", "$configuration",
    "$system", "$out", "$virtualsites", "$displacement"
]

picky_root = os.environ.get('PICKY')

def main_GUI():

    def show_help_folders():
        help_win = tk.Toplevel()
        help_win.title("Help - Folder creation")
        help_win.geometry("500x300")
        help_win.transient(root)  # stays on top of main window

        txt = scrolledtext.ScrolledText(help_win, wrap=tk.WORD, font=("Arial", 11), state="normal")
        txt.pack(fill="both", expand=True, padx=12, pady=(12, 4))
        help_text = (
            "Folder Creation Help\n"
            "====================\n\n"
            "• Enter an integer in the box next to 'Create cycle-n folder'.\n"
            "  Example: typing 3 and pressing the button creates a folder named:\n"
            "      Cycle3\n\n"
            "Inside each CycleN folder, the following subfolders are created:\n"
            "  • 1.picky        → stores Picky input/output data\n"
            "  • 2.QMsampling   → for Quantum Mechanics sampling files\n"
            "  • 3.fit          → for fitting force field parameters\n"
            "  • 4.deltaP       → for ΔP calculations\n"
            "  • 5.MD           → for Molecular Dynamics runs\n\n"
            "Notes:\n"
            "• If a folder already exists, it is not overwritten and will be reported as 'Already existing'.\n"
            "• You can create multiple cycles by entering different numbers (Cycle1, Cycle2, ...).\n"
        )
        txt.insert(tk.END, help_text)
        txt.configure(state="disabled")

        tk.Button(help_win, text="Close", command=help_win.destroy).pack(pady=(0, 12))

    def create_folders_return_path():
        global cycle_paths, cycle_paths_prev
        value = entry_valore.get()
        if not value.isdigit():
            messagebox.showerror("Invalid input", "Please enter a valid integer.")
            return
        cycle_paths = create_folders(int(value))
        entry_valore.delete(0, tk.END)

    def run_dimer_sampling(): #STEP BETA
        root.destroy()
        global cycle_paths, cycle_paths_prev
        cycle_paths, cycle_num, cycle_paths_prev = select_cycle_root(os.getcwd())
        if cycle_paths:
            step_beta(cycle_paths, cycle_num, cycle_paths_prev)
        else:
            messagebox.showwarning("No folder selected", "No valid Cycle folder was selected.")
        main_GUI()

    def edit_hw():
        root.destroy()
        global cycle_paths
        cycle_paths, _, _ = select_cycle_root(os.getcwd())
        working_folder = cycle_paths[1]
        com_files = [f for f in os.listdir(working_folder) if f.lower().endswith(".com")]
        if com_files:
            edit_resource(working_folder)
        else: 
            messagebox.showerror(title="Error", message="No gaussian files found to edit")
            return
        main_GUI()
        
    def QM_recover(): #STEP GAMMA
        root.destroy()
        global cycle_paths, cycle_paths_prev
        cycle_paths, _, _ = select_cycle_root(os.getcwd())
        if cycle_paths:
            step_gamma(cycle_paths)
        else:
            messagebox.showwarning("No folder selected", "No valid Cycle folder was selected.")    
        main_GUI()

    def fitting_FF():    #STEP DELTA    
        root.destroy()
        global cycle_paths, cycle_paths_prev
        cycle_paths, cycle_num, _= select_cycle_root(os.getcwd())
        if cycle_paths:
            step_delta(cycle_paths, cycle_num)
        else:
            messagebox.showwarning("No folder selected", "No valid Cycle folder was selected.")
        main_GUI()

    def convergence():    #STEP ETA    
        root.destroy()
        global cycle_paths, cycle_paths_prev
        cycle_paths, cycle_num, _ = select_cycle_root(os.getcwd())
        if cycle_paths:
            step_eta(cycle_paths, cycle_num)
        else:
            messagebox.showwarning("No folder selected", "No valid Cycle folder was selected.")
        main_GUI()

    def get_system_configuration():    #STEP ETA    
        root.destroy()
        global cycle_paths, cycle_paths_prev
        cycle_paths, cycle_num, _ = select_cycle_root(os.getcwd())
        if cycle_paths:
            step_alpha(cycle_paths, cycle_num)
        else:
            messagebox.showwarning("No folder selected", "No valid Cycle folder was selected.")
        main_GUI()

    def on_close():
        root.quit()
        root.destroy()
        sys.exit()

    # Finestra principale
    root = tk.Tk()
    root.title("Picky GUI")
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Top frame for folder creation
    frame1 = tk.Frame(root)
    frame1.pack(pady=5, anchor="w")  # anchor left

    tk.Button(frame1, text="Create cycle-n folder", width=18,
            command=create_folders_return_path).pack(side=tk.LEFT, padx=(10,3))
    entry_valore = tk.Entry(frame1, width=4, justify="center")
    entry_valore.pack(side=tk.LEFT, padx=3)
    tk.Button(frame1, text="?", width=2, command=show_help_folders).pack(side=tk.LEFT, padx=(3,10))

    # All other buttons aligned left
    tk.Button(root, text="Dimer sampling", width=20,
            command=run_dimer_sampling).pack(anchor="w", padx=10, pady=3)
    tk.Button(root, text="Edit resources", width=20,
            command=edit_hw).pack(anchor="w", padx=10, pady=3)
    tk.Button(root, text="QM recover", width=20,
            command=QM_recover).pack(anchor="w", padx=10, pady=3)
    tk.Button(root, text="Fitting FF", width=20,
            command=fitting_FF).pack(anchor="w", padx=10, pady=3)
    tk.Button(root, text="Convergence test", width=20,
            command=convergence).pack(anchor="w", padx=10, pady=3)
    tk.Button(root, text="Get system configuration", width=20,
            command=get_system_configuration).pack(anchor="w", padx=10, pady=3)
    tk.Button(root, text="Quit", width=20,
            command=on_close).pack(anchor="w", padx=10, pady=10)

    root.mainloop()  

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'+{x}+{y}')

def create_folders(cycle_number):
    base = f"Cycle{cycle_number}"
    folder_names = [
        base,
        f"{base}/1.picky",
        f"{base}/2.QMsampling",
        f"{base}/3.fit",
        f"{base}/4.deltaP",
        f"{base}/5.MD"
    ]

    created_folders = []
    existing_folders = []

    for name in folder_names:
        if not os.path.exists(name):
            os.makedirs(name)  # Usa makedirs per creare anche le cartelle padre se necessario
            created_folders.append(name)
        else:
            existing_folders.append(name)

    # Messaggio riepilogativo
    message = ""
    if created_folders:
        message += f"Created folders:\n" + '\n'.join(created_folders) + "\n"
    if existing_folders:
        message += "\nAlready existing folders:\n" + '\n'.join(existing_folders)

    messagebox.showinfo("Folder Creation Status", message)
    
    # Restituisce tutti i path assoluti (creati ed esistenti)
    all_paths = [os.path.abspath(name) for name in folder_names]
    return all_paths

def copy_files(in_path, in_name, out_path, out_name):
    """Copy file inpath/inname to outpath/outname.
    If in_path is not provided, use current folder.
    If out_path is not provided, use current folder.
    If out_name is not provided, use in_name.
    Always return out_name, even if operation is canceled or fails.
    """

    if not in_path:
        in_path = os.getcwd()
    if not out_path:
        out_path = os.getcwd()
    if not out_name:
        out_name = in_name

    rel_path = os.path.relpath(out_path, start=os.getcwd())
    dest_file_path = os.path.join(out_path, out_name)

    if os.path.exists(dest_file_path):
        user_choice = messagebox.askyesno(
            "File already exists",
            f"File '{out_name}' already exists in '{rel_path}'.\nDo you want to select another file?"
        )
        if user_choice:
            new_file = filedialog.askopenfilename(title="Select file to copy")
            if new_file:
                in_path, in_name = os.path.split(new_file)
            else:
                messagebox.showinfo("Cancel", "No file selected.")
                return out_name
        else:
            return out_name

    try:
        shutil.copy(os.path.join(in_path, in_name), dest_file_path)
        messagebox.showinfo("Success", f"File '{out_name}' has been copied to '{os.path.join(rel_path, out_name)}'.")
    except Exception as e:
        messagebox.showerror("Error", f"An error has occurred: {e}")

    return out_name

def copy_selected_file(out_folder, out_name, message, extension):
    if not message:
        message = "Select a file to copy"
    if not extension:
        extension = "*"

    file_path = None
    rel_path = os.path.relpath(out_folder, start=os.getcwd())
    # Verifica se esiste già un file con quella estensione nella cartella
    if extension:
        for file in os.listdir(out_folder):
            if file.endswith(extension):
                # messagebox.showinfo("Nota", f"Il file '{file}' è già presente in '{out_folder}'.")
                ans = messagebox.askyesno("Warning", f"File '{file}' is already present in '{rel_path}'.\nDo you want to select another file?")
                if not ans:
                    return file  # Usa il file esistente, non copia nulla
                break  # L’utente ha detto "sì", selezioniamo un altro
    if out_name:    
        for file in os.listdir(out_folder):
            if os.path.exists(os.path.join(out_folder, out_name)):
                # messagebox.showinfo("Nota", f"Il file '{file}' è già presente in '{out_folder}'.")
                ans = messagebox.askyesno("Warning", f"File '{file}' is already present in '{rel_path}'.\nDo you want to select another file?")
                if not ans:
                    return file  # Usa il file esistente, non copia nulla
                break  # L’utente ha detto "sì", selezioniamo un altro

    # Apertura dialogo di selezione file
    file_path = filedialog.askopenfilename(title=message,filetypes=[("File", f"*{extension}")]
                                           )
    if not file_path:
        messagebox.showwarning("Warning", "No file selected.")
        return None

    # Imposta out_name se vuoto
    final_name = out_name or os.path.basename(file_path)

    try:
        shutil.copy(file_path, os.path.join(out_folder, final_name))
        messagebox.showinfo("Success", f"The file '{final_name}' has been copied to '{out_folder}'.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while copying: {e}")
        return None

    return final_name

def edit_inp_file(file_path):
    """Opens a text file given a path and displays it in a GUI with a combobox for word selection."""
    
    # === NEW: help window (English) ===
    def show_help():
        """Show a help window with quick instructions (English)."""
        help_win = tk.Toplevel()
        help_win.title("Help")
        help_win.geometry("760x560")
        help_win.transient()  # keep on top

        txt = scrolledtext.ScrolledText(help_win, wrap=tk.WORD, font=("Arial", 11), state="normal")
        txt.pack(fill="both", expand=True, padx=12, pady=(12, 4))

        help_text = (
            "Quick Guide\n"
            "===========\n\n"
            "• Editor area: edit your .inp text on the left.\n"
            "• Panel 1 (left): works on k-words already present in the text.\n"
            "  - Select a k-word in 'Select K-word'.\n"
            "  - Type a value in the entry.\n"
            "  - Click 'Confirm keywords' to replace/insert a line as:  <kword> <value>\n"
            "• Panel 2 (right): adds new k-words that are missing from the text.\n"
            "  - Pick a k-word in 'Add new K-word (not in text)'.\n"
            "  - Type a value in 'Value for new k-word'.\n"
            "  - Click 'Confirm keywords' (same button) to insert the new line.\n"
            "• Create new geometry: opens a small form to build a $geometry ... $end block.\n"
            "• Save: overwrites the current file.  Save as...: writes a new file.\n"
            "• Continue: saves and closes the editor, returning to main GUI."
            "• Cancel: closes without saving.\n\n"
        )
        txt.insert(tk.END, help_text)
        txt.configure(state="disabled")

        tk.Button(help_win, text="Close", command=help_win.destroy).pack(pady=(0, 12))

    def extract_kwords(text: str):
        """
        Estrae tutte le k-word dal testo: parole precedute da '$',
        escludendo '$end' (case-insensitive). Mantiene l'ordine e rimuove i duplicati.
        Restituisce una lista nel formato ['$parola1', '$parola2', ...].
        """
        # trova token del tipo $nome (limite su bordo parola)
        found = re.findall(r'(?<!\S)\$([A-Za-z0-9_]+)\b', text)
        # filtra $end e riaggiunge il prefisso '$'
        kwords = [f'${w}' for w in found if w.lower() != 'end']
        # de-dup mantenendo l'ordine
        seen = set()
        ordered = []
        for k in kwords:
            if k not in seen:
                seen.add(k)
                ordered.append(k)
        return ordered

    def get_missing_keywords(current_text: str):
        found = set(extract_kwords(current_text))
        # escludi anche $end per sicurezza
        return sorted([kw for kw in SUGGESTED_KWORDS if kw.lower() != "$end" and kw not in found], key=str.lower)

    def refresh_keywords():
        current_text = text_area.get("1.0", tk.END)

        # pannello 1: k-word trovate nel testo (per modificare/riscrivere righe già presenti)
        new_found = extract_kwords(current_text)
        cur1 = word_combobox1.get().strip()
        word_combobox1["values"] = new_found
        if cur1 and (cur1 in new_found):
            word_combobox1.set(cur1)
        elif new_found:
            word_combobox1.set(new_found[0])
        else:
            word_combobox1.set("")

        # pannello 2: k-word suggerite che NON sono nel testo (per inserimento nuove righe)
        new_missing = get_missing_keywords(current_text)
        cur2 = word_combobox2.get().strip()
        word_combobox2["values"] = new_missing
        if cur2 and (cur2 in new_missing):
            word_combobox2.set(cur2)
        elif new_missing:
            word_combobox2.set(new_missing[0])
        else:
            word_combobox2.set("")

    def save_file():
        """Saves the content of the text area to the specified file and closes the window."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))  # Save the text area content
            root.title(f"Editor - {file_path} (Saved)")
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")
    
    def save_file_as(default_extension=".inp"):
        file_path = filedialog.asksaveasfilename(
            defaultextension=default_extension,
            filetypes=[("All Files", "*.*"), ("Text Files", "*.inp")],
            title="Save As"
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(text_area.get("1.0", tk.END))  
                messagebox.showinfo("Success", f"File saved as:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def cancel_action():
        """Closes the window without saving."""
        root.quit()
        root.destroy()
        main_GUI()

    def on_close():
        """Handles window closing when 'X' is pressed."""
        root.quit()
        root.destroy()
        main_GUI()

    def continue_to_picky():
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))  # Save the text area content
            root.title(f"Editor - {file_path} (Saved)")
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")
            
        root.quit()  # Ensure the complete termination of the tkinter loop
        root.destroy()  # Close the window
    
    def update_file():
        """Saves the content of the text area to the specified file."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))  # Save the text area content
            root.title(f"Editor - {file_path} (Saved)")         
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")    
    
    def insert_keyword():
        """
        - Se 'entry' (pannello 1) ha testo, agisce su word_combobox1 (k-word presenti): modifica/sostituisce la riga.
        - Altrimenti, se 'entry_new' (pannello 2) ha testo, agisce su word_combobox2 (k-word mancanti): inserisce nuova riga.
        Regole:
        * inserisce/se sostituisce SEMPRE iniziando da una NUOVA riga (mai in coda alla riga corrente);
        * normalizza CRLF/CR -> LF e ripulisce righe vuote (spazi/tab inclusi).
        """

        def _normalize(text: str) -> str:
            # normalizza CRLF/CR e rimuove spazi finali
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            lines = [ln.rstrip() for ln in text.split("\n")]
            return "\n".join(lines)

        def _clean(text: str) -> str:
            """
            Elimina righe vuote iniziali/finali e collassa vuoti multipli a ZERO tra inserimenti:
            se vuoi mantenerne 1 tra blocchi, sostituisci il blocco 'collasso' con una singola append("").
            """
            text = _normalize(text)
            raw = text.split("\n")
            # togli leading/trailing vuoti (anche con spazi/tab)
            while raw and raw[0].strip() == "":
                raw.pop(0)
            while raw and raw[-1].strip() == "":
                raw.pop()
            # collassa vuoti interni: rimuovi completamente righe vuote
            out = []
            for ln in raw:
                if ln.strip() == "":
                    continue
                out.append(ln)
            return ("\n".join(out) + ("\n" if out else ""))

        def _force_newline_cursor():
            """
            Porta il cursore a inizio di una NUOVA riga:
            - se la riga corrente ha testo, vai a fine riga, inserisci '\n'
            - se è già vuota (solo spazi/tab), puliscila e posizionati lì
            """
            cur_start = text_area.index("insert linestart")
            cur_end   = text_area.index("insert lineend")
            line_txt  = text_area.get(cur_start, cur_end)
            if line_txt.strip() != "":
                # c'è testo -> vai a fine riga e aggiungi un newline
                text_area.mark_set("insert", cur_end)
                text_area.insert("insert", "\n")
            else:
                # la riga è vuota: se contiene spazi/tab, ripulisci
                if line_txt != "":
                    text_area.delete(cur_start, cur_end)

        def _replace_first_line_starting_with(content: str, kw: str, new_line: str) -> str:
            lines = content.split("\n")
            replaced = False
            for i, ln in enumerate(lines):
                if not replaced and ln.strip().startswith(kw):
                    lines[i] = new_line
                    replaced = True
            if not replaced:
                # se non trovata, appenderemo tramite inserimento cursor-based
                return content
            return "\n".join(lines)

        # --- input dalle due entry ---
        val1 = entry.get().strip()
        val2 = entry_new.get().strip()

        if not val1 and not val2:
            messagebox.showerror("Error", "Inserisci un valore in una delle due entry.")
            return
        if val1 and val2:
            messagebox.showinfo("Info", "Sono stati inseriti due valori: eseguo la modifica (pannello sinistro).")

        # carica e normalizza il testo una volta
        content = _normalize(text_area.get("1.0", tk.END))

        # --- caso 1: MODIFICA / INSERIMENTO usando pannello 1 (k-word presenti) ---
        if val1:
            kw = word_combobox1.get().strip()
            if not kw:
                messagebox.showerror("Error", "Nessuna k-word selezionata nel pannello sinistro.")
                return
            if kw.lower() == "$end":
                messagebox.showerror("Error", "La k-word '$end' non può essere modificata qui.")
                return

            kwords_in_text = extract_kwords(content)
            if kw in kwords_in_text:
                # sostituisci la PRIMA riga che inizia con kw
                replaced_text = _replace_first_line_starting_with(content, kw, f"{kw} {val1}".rstrip())
                text_area.replace("1.0", tk.END, replaced_text + ("\n" if not replaced_text.endswith("\n") else ""))
            else:
                # inserisci su NUOVA riga alla posizione del cursore
                text_area.replace("1.0", tk.END, content + ("\n" if not content.endswith("\n") else ""))
                _force_newline_cursor()
                text_area.insert(tk.INSERT, (f"{kw} {val1}".rstrip() + "\n"))

            # pulizia robusta
            cleaned = _clean(text_area.get("1.0", tk.END))
            text_area.replace("1.0", tk.END, cleaned)

            entry.delete(0, tk.END)
            update_file()
            refresh_keywords()
            return

        # --- caso 2: INSERIMENTO NUOVA RIGA usando pannello 2 (k-word mancanti) ---
        kw2 = word_combobox2.get().strip()
        if not kw2:
            messagebox.showerror("Error", "Nessuna k-word selezionata nel pannello destro.")
            return
        if kw2.lower() == "$end":
            messagebox.showerror("Error", "La k-word '$end' non può essere inserita qui.")
            return

        kwords_in_text = extract_kwords(content)
        if kw2 in kwords_in_text:
            replaced_text = _replace_first_line_starting_with(content, kw2, f"{kw2} {val2}".rstrip())
            text_area.replace("1.0", tk.END, replaced_text + ("\n" if not replaced_text.endswith("\n") else ""))
        else:
            text_area.replace("1.0", tk.END, content + ("\n" if not content.endswith("\n") else ""))
            _force_newline_cursor()
            text_area.insert(tk.INSERT, (f"{kw2} {val2}".rstrip() + "\n"))

        # pulizia robusta (CRLF, spazi e righe vuote)
        cleaned = _clean(text_area.get("1.0", tk.END))
        text_area.replace("1.0", tk.END, cleaned)

        entry_new.delete(0, tk.END)
        update_file()
        refresh_keywords()

    def new_geom():
        """Apre una finestra per inserire una sezione $geometry...$end con righe a b c d e f 'a'."""
        geometry_window = tk.Toplevel()
        geometry_window.title("Editor $geometry")

        entry_rows = []  # Lista di liste di Entry
        row_frames = []  # Per tenere traccia dei frame delle righe
        
        def show_help_geometry():
            win = tk.Toplevel(geometry_window)
            win.title("Help - $geometry")
            win.geometry("560x420")
            win.transient(geometry_window)
            win.grab_set()

            txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Arial", 11), state="normal")
            txt.pack(fill="both", expand=True, padx=12, pady=(12, 4))

            help_text = (
                "$geometry Block - Quick Help\n"
                "============================\n\n"
                "• This dialog builds a $geometry ... $end section.\n"
                "• Each row contains 6 fields: a b c d e f\n"
                "  - The FIRST field (a) is REQUIRED and will also be appended as a quoted label at the end of the line:\n"
                "      a b c d e f 'A'\n"
                "    where 'A' is the capitalized version of the first field.\n"
                "\n"
                "How to use\n"
                "----------\n"
                "• Add row: inserts a new line with 6 input boxes.\n"
                "• Delete row: removes the most recently added line.\n"
                "• Confirm: generates the block and inserts it into the editor:\n"
                "      $geometry  A B\n"
                "          a    b    c    d    e    f    'A'\n"
                "      $end\n"
                "  - Empty rows are skipped.\n"
                "  - If a $geometry ... $end block already exists, it will be REPLACED.\n"
                "  - Otherwise, the new block is appended to the end of the file (with a blank line before it).\n"
                "• Cancel: closes this window without changes.\n"
                "\n"
                "Validation notes\n"
                "---------------\n"
                "• The first field of every non-empty row must be filled; otherwise you’ll get an error.\n"
                "• All entered values are capitalized before insertion.\n"
            )
            txt.insert(tk.END, help_text)
            txt.configure(state="disabled")
            tk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 12))

        # Top bar with small '?' button
        topbar = tk.Frame(geometry_window)
        topbar.pack(fill="x", padx=8, pady=(6, 0))
        tk.Label(topbar, text="$geometry editor", font=("Arial", 11, "bold")).pack(side="left")
        tk.Button(topbar, text="?", width=2, command=show_help_geometry).pack(side="right")

        def add_row():
            """Aggiunge una nuova riga di 6 Entry."""
            row_frame = tk.Frame(geometry_window)
            row_frame.pack(padx=5, pady=2)

            row_entries = []
            for _ in range(6):
                entry = tk.Entry(row_frame, width=10)
                entry.pack(side=tk.LEFT, padx=2)
                row_entries.append(entry)

            entry_rows.append(row_entries)
            row_frames.append(row_frame)

        def remove_last_row():
            """Rimuove l'ultima riga aggiunta."""
            if entry_rows:
                last_entries = entry_rows.pop()
                last_frame = row_frames.pop()
                last_frame.destroy()
            else:
                messagebox.showinfo("Info", "Non ci sono più righe da rimuovere.")

        def confirm_geometry():
            """Crea e inserisce la sezione $geometry...$end nel text_area."""
            lines = []
            lines.append("\n$geometry  A B")
            for row in entry_rows:
                values = [e.get().strip() for e in row]
                if any(values):  # Salta righe completamente vuote
                    if values[0]:  # Serve il primo campo per fare 'a'
                        quoted = f"'{values[0].capitalize()}'"
                        values_capitalized = [v.capitalize() for v in values]
                        full_line = "    ".join(values_capitalized + [quoted])
                        lines.append(full_line)
                    else:
                        messagebox.showerror("Errore", "Il primo campo della riga non può essere vuoto.")
                        return
            lines.append("$end\n")

            new_block = "\n".join(lines)

            # --- Sostituzione nel text_area ---
            content = text_area.get("1.0", tk.END)

            # Cerca il blocco esistente
            pattern = re.compile(r"\$geometry\b.*?\$end\b", re.IGNORECASE | re.DOTALL)
            if pattern.search(content):
                updated_content = pattern.sub(new_block, content)
            else:
                updated_content = content.rstrip() + "\n\n" + new_block
            # Aggiorna il text_area con il nuovo contenuto
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, updated_content)
            geometry_window.destroy()


        # --- Pulsanti ---
        button_frame = tk.Frame(geometry_window)
        button_frame.pack(pady=10)

        add_button = tk.Button(button_frame, text="Add row", command=add_row)
        add_button.pack(side=tk.LEFT, padx=(5,10))

        remove_button = tk.Button(button_frame, text="Delete row", command=remove_last_row)
        remove_button.pack(side=tk.LEFT, padx=(5,10))

        confirm_button = tk.Button(button_frame, text="Confirm", command=confirm_geometry)
        confirm_button.pack(side=tk.LEFT, padx=(5,10))

        cancel_button = tk.Button(button_frame, text="Cancel", command=geometry_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=(5,10))

        add_row()  # Prima riga iniziale

    # GUI Creation
    root = tk.Tk()
    root.title(f"Editor - {file_path}")
    root.protocol("WM_DELETE_WINDOW", on_close)  # Handles window closing
    
    # Main frame
    frame = tk.Frame(root)
    frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    # === NEW: top bar with right-aligned '?' button ===
    topbar = tk.Frame(frame)
    topbar.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(0, 8))
    title_lbl = tk.Label(topbar, text="INP Editor", font=("Arial", 12, "bold"))
    title_lbl.pack(side="left")
    spacer = tk.Frame(topbar)
    spacer.pack(side="left", expand=True, fill="x")
    tk.Button(topbar, text="?", width=3, command=show_help).pack(side="right")

    # Text area with scrollbar
    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Arial", 12))
    text_area.grid(row=1, column=1, sticky="nsew")

    # Additional right side panel
    side_panel1 = tk.Frame(frame)
    side_panel1.grid(row=1, column=3, sticky="ns", padx=10)

    # Secondo pannello (a destra del primo)
    side_panel2 = tk.Frame(frame)
    side_panel2.grid(row=1, column=4, sticky="ns", padx=10)

    # Grid weights (ensure proper resizing)  ### UPDATED
    frame.grid_columnconfigure(0, weight=0)  # topbar/left gutter
    frame.grid_columnconfigure(1, weight=1)  # editor expands
    frame.grid_columnconfigure(2, weight=0)  # (optional spacer)
    frame.grid_columnconfigure(3, weight=0)  # side panel 1
    frame.grid_columnconfigure(4, weight=0)  # side panel 2
    frame.grid_rowconfigure(1, weight=1)     # main row expands
    root.grid_rowconfigure(0, weight=1)

        
    # Load the file
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        text_area.insert(tk.END, content)
    except FileNotFoundError:
        content = ""
        text_area.insert(tk.END, "Error: File not found!")
    except Exception as e:
        content = ""
        text_area.insert(tk.END, f"Error while opening the file:\n{e}")

    # === NUOVO: ottieni le k-word dal contenuto caricato ===
    KEYWORDS = extract_kwords(content)
    if not KEYWORDS:
        KEYWORDS = []  # o un default se vuoi, es. ["$geometry"]

    # Label for combobox
    label = tk.Label(side_panel1, text="Select K-word")
    label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    # Combobox for word selection
    selected_word = tk.StringVar()
    word_combobox1 = ttk.Combobox(side_panel1, textvariable=selected_word, values=KEYWORDS, state="readonly")
    if KEYWORDS:
        word_combobox1.set(KEYWORDS[0])
    word_combobox1.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    # Label for text input
    label = tk.Label(side_panel1, text="Value for selected k-word")
    label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    # Text input field
    entry = tk.Entry(side_panel1)
    entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")

    # Insert command button
    insert = tk.Button(side_panel1, text="Confirm keyword", command=insert_keyword)
    insert.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

    # Save button
    save_button = tk.Button(side_panel1, text="Save", command=save_file)
    save_button.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")
    # Save as button
    save_button = tk.Button(side_panel1, text="Save as...", command=save_file_as)
    save_button.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")
    
    # Edit geometry
    insert = tk.Button(side_panel1, text="Create new geometry", command=new_geom)
    insert.grid(row=7, column=0, padx=10, pady=5, sticky="nsew")
    
    # Continue to picky
    insert = tk.Button(side_panel1, text="Continue", command=continue_to_picky)
    insert.grid(row=8, column=0, padx=10, pady=5, sticky="nsew")

    # Cancel button
    cancel_button = tk.Button(side_panel1, text="Cancel", command=cancel_action)
    cancel_button.grid(row=9, column=0, padx=10, pady=20, sticky="nsew")
    
    # PANNELLO 2
    label2 = tk.Label(side_panel2, text="Add new K-word (not in text)")
    label2.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    missing_kwords = get_missing_keywords(content)
    selected_word2 = tk.StringVar()
    word_combobox2 = ttk.Combobox(side_panel2, textvariable=selected_word2, values=missing_kwords, state="readonly")
    if missing_kwords:
        word_combobox2.set(missing_kwords[0])
    word_combobox2.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    # ---- UI: entry valore per nuova k-word ----
    label2v = tk.Label(side_panel2, text="Value for new k-word")
    label2v.grid(row=2, column=0, padx=5, pady=5, sticky="w")

    entry_new = tk.Entry(side_panel2)
    entry_new.grid(row=3, column=0, padx=5, pady=5, sticky="w")

    center_window(root)
    root.mainloop()  # Launch the GUI when needed

def edit_npt_file(file_path):
    """Opens a text file given a path and displays it in a GUI with a combobox for word selection."""
    
    def show_help():
        """Show a help window with quick instructions (English)."""
        help_win = tk.Toplevel()
        help_win.title("Help")
        help_win.geometry("720x520")
        help_win.transient()  # keep on top of the main window

        txt = scrolledtext.ScrolledText(help_win, wrap=tk.WORD, font=("Arial", 11), state="normal")
        txt.pack(fill="both", expand=True, padx=12, pady=(12, 4))

        help_text = (
            "Quick Guide\n"
            "===========\n\n"
            "• Select a k-word: use the 'Select K-word' combo.\n"
            "• Enter the command: type it under 'Insert mode for selected keywords'.\n"
            "• Confirm: click 'Confirm keywords' to insert/replace the line as\n"
            "  <kword>           = <command>\n"
            "• Save: 'Save' overwrites the current file. 'Save as...' writes a new file.\n"
            "• Continue: saves and closes the editor, returning to Picky.\n"
            "• Cancel: closes without saving and returns to the previous screen.\n\n"
        )
        txt.insert(tk.END, help_text)
        txt.configure(state="disabled")

        btn = tk.Button(help_win, text="Close", command=help_win.destroy)
        btn.pack(pady=(0, 12))

    def extract_kwords(text: str):
        """
        Estrae la *prima parola* di ogni riga che:
        - non è vuota
        - non inizia con ';'
        Mantiene l'ordine di apparizione ed evita duplicati.
        Esempio riga -> 'keyword arg1 arg2 ; comment'  -> 'keyword'
        """
        words = []
        seen = set()
        for line in text.splitlines():
            s = line.strip()
            if not s or s.startswith(';'):
                continue
            # prima parola fino a spazio/tab (ignora eventuali commenti dopo)
            m = re.match(r'^([^\s;]+)', s)
            if m:
                w = m.group(1)
                if w not in seen:
                    seen.add(w)
                    words.append(w)
        return words

    def refresh_keywords():
        current_text = text_area.get("1.0", tk.END)
        new_keywords = extract_kwords(current_text)
        word_combobox1["values"] = new_keywords
        if new_keywords:
            word_combobox1.set(new_keywords[0])
        else:
            word_combobox1.set("")

    def save_file():
        """Saves the content of the text area to the specified file and closes the window."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))  # Save the text area content
            root.title(f"Editor - {file_path} (Saved)")
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")
    
    def save_file_as(default_extension=".inp"):
        file_path = filedialog.asksaveasfilename(
            defaultextension=default_extension,
            filetypes=[("All Files", "*.*"), ("Text Files", "*.inp")],
            title="Save As"
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(text_area.get("1.0", tk.END))  
                messagebox.showinfo("Success", f"File saved as:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def cancel_action():
        """Closes the window without saving."""
        root.quit()
        root.destroy()
        main_GUI()
    
    def on_close():
        """Handles window closing when 'X' is pressed."""
        root.quit()
        root.destroy()
        main_GUI()

    def continue_to_picky():
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))  # Save the text area content
            root.title(f"Editor - {file_path} (Saved)")
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")
            
        root.quit()  # Ensure the complete termination of the tkinter loop
        root.destroy()  # Close the window
    
    def update_file():
        """Saves the content of the text area to the specified file."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))  # Save the text area content
            root.title(f"Editor - {file_path} (Saved)")         
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")    
    
    def insert_keyword():
        """Inserisce il comando accanto alla k-word selezionata oppure alla posizione corrente."""
        selected = word_combobox1.get()
        command = entry.get()

        if not selected:
            messagebox.showerror("Error", "No word selected!")
            return

        content = text_area.get("1.0", tk.END)
        # k-word presenti adesso (per coerenza)
        kwords_in_text = extract_kwords(content)

        if selected in kwords_in_text:
            new_content = ""
            replaced = False
            for line in content.split("\n"):
                original_line = line
                line_stripped = line.strip()
                if line_stripped and not replaced and line_stripped.startswith(selected):
                    new_line = f"{selected}           = {command}"
                    new_content += new_line + "\n"
                    replaced = True
                else:
                    new_content += original_line + "\n"
            text_area.replace("1.0", tk.END, new_content)
        else:
            # Inserisci una nuova riga alla posizione del cursore
            insert_text = f"{selected}           = {command}\n"
            text_area.insert(tk.INSERT, insert_text)

        entry.delete(0, tk.END)
        update_file()
        refresh_keywords()
    
    # GUI Creation
    root = tk.Tk()
    root.title(f"Editor - {file_path}")
    root.protocol("WM_DELETE_WINDOW", on_close)  # Handles window closing
    
    # Main frame
    frame = tk.Frame(root)
    frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    topbar = tk.Frame(frame)
    topbar.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 8))
    # left title (optional)
    title_lbl = tk.Label(topbar, text="NPT Editor", font=("Arial", 12, "bold"))
    title_lbl.pack(side="left")
    # spacer to push the button to the right
    topbar_spacer = tk.Frame(topbar)
    topbar_spacer.pack(side="left", expand=True, fill="x")
    help_btn = tk.Button(topbar, text="?", width=3, command=show_help)
    help_btn.pack(side="right")
    
    # Text area with scrollbar
    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Arial", 12))
    text_area.grid(row=1, column=1, sticky="nsew")
 
    # Additional right side panel
    side_panel1 = tk.Frame(frame)
    side_panel1.grid(row=1, column=3, sticky="ns", padx=10)

    # Grid weights (aggiungi la riga giusta e completa le colonne)
    frame.grid_columnconfigure(0, weight=0)  # topbar/left
    frame.grid_columnconfigure(1, weight=1)  # text area
    frame.grid_columnconfigure(2, weight=0)  # (eventuale spacer)
    frame.grid_columnconfigure(3, weight=0)  # side panel
    frame.grid_rowconfigure(1, weight=1)     # ← la riga principale che deve espandersi
    root.grid_rowconfigure(0, weight=1)
        
    # Load the file
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        text_area.insert(tk.END, content)
    except FileNotFoundError:
        content = ""
        text_area.insert(tk.END, "Error: File not found!")
    except Exception as e:
        content = ""
        text_area.insert(tk.END, f"Error while opening the file:\n{e}")

    # === NUOVO: ottieni le k-word dal contenuto caricato ===
    KEYWORDS = extract_kwords(content)
    if not KEYWORDS:
        KEYWORDS = []  # o un default se vuoi, es. ["$geometry"]

    # Label for combobox
    label = tk.Label(side_panel1, text="Select K-word")
    label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    # Combobox for word selection
    selected_word = tk.StringVar()
    word_combobox1 = ttk.Combobox(side_panel1, textvariable=selected_word, values=KEYWORDS, state="readonly")
    if KEYWORDS:
        word_combobox1.set(KEYWORDS[0])
    word_combobox1.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    # Label for text input
    label = tk.Label(side_panel1, text="Insert mode for selected keywords")
    label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    # Text input field
    entry = tk.Entry(side_panel1)
    entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")

    # Insert command button
    insert = tk.Button(side_panel1, text="Confirm keywords", command=insert_keyword)
    insert.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

    # Save button
    save_button = tk.Button(side_panel1, text="Save", command=save_file)
    save_button.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")
    # Save as button
    save_button = tk.Button(side_panel1, text="Save as...", command=save_file_as)
    save_button.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")

    # === NEW: pulsante Help
    # help_button = tk.Button(side_panel1, text="Help (?)", command=show_help)
    # help_button.grid(row=7, column=0, padx=10, pady=10, sticky="nsew")

    # Continue to picky
    continue_button = tk.Button(side_panel1, text="Continue", command=continue_to_picky)
    continue_button.grid(row=8, column=0, padx=10, pady=5, sticky="nsew")

    # Cancel button
    cancel_button = tk.Button(side_panel1, text="Cancel", command=cancel_action)
    cancel_button.grid(row=9, column=0, padx=10, pady=20, sticky="nsew")

    center_window(root)
    root.mainloop()  # Launch the GUI when needed

def extract_section_from_file_with_list(file_path, word_list):
    """Estrae, per ogni 'word' in 'word_list', la sezione che inizia *dopo* l'header
    '[ word ]' (case-insensitive) e termina alla prima riga vuota O al prossimo header.
    Ogni riga salvata inizia con almeno uno spazio (come in versione originale).
    Ritorna: {word: list_of_lines}."""


    # Prepara i pattern header alla GROMACS, ordinando le key per lunghezza decrescente
    # per evitare shadowing (es. 'atomtypes' prima di 'atoms').
    keys_sorted = sorted(word_list, key=lambda k: len(k), reverse=True)
    header_patterns = {
        k: re.compile(rf'^\s*\[\s*{re.escape(k)}\s*\]\s*(?:;.*)?\s*$', flags=re.IGNORECASE)
        for k in keys_sorted
    }

    def match_header(line):
        for key in keys_sorted:
            cre = header_patterns[key]
            if cre.match(line):
                return key
        return None

    result = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Per ogni parola, estrai dalla PRIMA occorrenza (comportamento invariato)
        for word in word_list:
            section = []
            collecting = False

            for i, row in enumerate(lines):
                if not collecting:
                    # attiva solo se la riga è un vero header [ word ]
                    key = match_header(row)
                    if key is not None and key.lower() == word.lower():
                        collecting = True
                    continue
                else:
                    # Stop alla prima riga vuota
                    if not row.strip():
                        break
                    # Stop se incontriamo un altro header
                    if match_header(row) is not None:
                        break
                    # Mantieni compatibilità: garantisci almeno uno spazio davanti.
                    # (Se vuoi preservare l’indentazione originale, usa semplicemente: section.append(row))
                    section.append(row)

            result[word] = section

    except Exception as e:
        messagebox.showerror("Error", f"Error: {e}")
        return None

    return result

def replace_sections_in_file(dest_file_path, replacements):
    """
    Sostituisce più sezioni nel file 'dest_file_path'.
    Ogni sezione inizia con una riga header '[ KEY ]' (case-insensitive, stile GROMACS),
    e termina alla prima riga vuota O al prossimo header.
    Se una KEY non si trova, chiede se appenderla in fondo come:
        [ KEY ]
        <contenuto>
    'replacements' è {KEY: list_of_lines} dove list_of_lines NON include l'header.
    """
 

    # Ordina chiavi per lunghezza decrescente per evitare shadowing (es. 'atomtypes' prima di 'atoms')
    keys_sorted = sorted(replacements.keys(), key=lambda k: len(k), reverse=True)

    # Header stile GROMACS: [ key ] con eventuale commento in coda
    header_patterns = {
        k: re.compile(rf'^\s*\[\s*{re.escape(k)}\s*\]\s*(?:;.*)?\s*$', flags=re.IGNORECASE)
        for k in keys_sorted
    }

    def match_header(line):
        for key in keys_sorted:
            cre = header_patterns[key]
            if cre.match(line):
                return key
        return None

    def norm_lines(lines_list):
        out = []
        for s in lines_list:
            out.append(s if s.endswith('\n') else s + '\n')
        return out

    # Normalizza i contenuti in input
    replacements_norm = {k: norm_lines(v) for k, v in replacements.items()}

    try:
        with open(dest_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_content = []
        i = 0
        replaced_keys = set()

        while i < len(lines):
            line = lines[i]
            matched_key = match_header(line)

            if matched_key is not None:
                # Copia l'header così com'è
                new_content.append(line)
                # Sostituisci il contenuto della sezione
                new_content.extend(replacements_norm.get(matched_key, []))
                replaced_keys.add(matched_key)

                # Salta l'originale fino a riga vuota O prossimo header (non consumare l'header successivo)
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    if not nxt.strip():
                        i += 1  # consuma la riga vuota di chiusura
                        break
                    if match_header(nxt) is not None:
                        break
                    i += 1
                continue

            # Riga normale
            new_content.append(line)
            i += 1

        # Gestisci chiavi mancanti
        missing = [k for k in replacements_norm.keys() if k not in replaced_keys]
        if missing:
            missing_txt = "\n - ".join(missing)
            if messagebox.askyesno(
                "Missing sections",
                f"The following sections were not found in:\n{dest_file_path}\n\n - {missing_txt}\n\n"
                f"Do you want to append them at the end of the file?"
            ):
                # Assicura una riga vuota prima di appendere
                if new_content and new_content[-1].strip():
                    new_content.append('\n')

                for k in missing:
                    # Header coerente con GROMACS
                    new_content.append(f"[ {k} ]\n")
                    new_content.extend(replacements_norm[k])
                replaced_keys.update(missing)

        with open(dest_file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content)

        if replaced_keys:
            replaced_list = "\n - ".join(sorted(replaced_keys, key=str.lower))
            messagebox.showinfo(
                "Sections Replaced",
                f"The following sections were processed in:\n{dest_file_path}\n\n - {replaced_list}"
            )
        else:
            messagebox.showwarning(
                "No Sections Replaced",
                f"No matching sections found in:\n{dest_file_path}"
            )

        return True

    except Exception as e:
        messagebox.showerror("Error", f"Error replacing sections: {e}")
        return False

def build_gopicky_command_from_folder(working_dir):
    """
    GUI to build a go.picky command by selecting .inp files from working_dir.
    Returns the assembled command as a list of strings (with filename cleaned).
    """
    command = []

    # List all .inp files
    inp_files = [f for f in os.listdir(working_dir) if f.endswith(".inp")]
    if not inp_files:
        messagebox.showerror("No .inp files found", f"No .inp files found in:\n{working_dir}")
        return None

    # Build cleaned display names
    file_map = {}
    for f in inp_files:
        cleaned = f
        if cleaned.startswith("picky."):
            cleaned = cleaned[len("picky."):]
        if cleaned.endswith(".inp"):
            cleaned = cleaned[:-len(".inp")]
        file_map[cleaned] = f

    display_names = list(file_map.keys())

    def show_help():
        help_win = tk.Toplevel(window)
        help_win.title("Help")
        help_text = (
            "This interface lets you compose a go.picky command.\n\n"
            "• You can enter up to two optional command-line arguments.\n"
            "• Select the desired .inp file from the dropdown list.\n"
            "• The file list shows cleaned names (without 'picky.' and '.inp').\n\n"
            "The final command will look like:\n"
            "go.picky <arg1> <arg2> <filename>\n"
        )
        label = tk.Label(help_win, text=help_text, justify="left", padx=10, pady=10)
        label.pack()

    def confirm_inputs():
        selected_display_name = combo.get().strip()
        cmd1 = entry1.get().strip()
        cmd2 = entry2.get().strip()

        if not selected_display_name:
            messagebox.showerror("Missing selection", "You must select a .inp file.")
            return

        command.append("go.picky")
        if cmd1:
            command.append(cmd1)
        if cmd2:
            command.append(cmd2)
        command.append(selected_display_name)
        window.destroy()

    # --- GUI Setup ---
    window = tk.Tk()
    
    window.title("Build go.picky command")

    # Top frame with help icon
    top_frame = tk.Frame(window)
    top_frame.pack(anchor="ne", pady=(5, 0), padx=5)
    help_button = tk.Button(top_frame, text="❓", command=show_help, relief="flat", font=("Arial", 10, "bold"))
    help_button.pack()

    # Command-line style row
    row_frame = tk.Frame(window)
    row_frame.pack(padx=10, pady=10)

    tk.Label(row_frame, text="go.picky").pack(side="left", padx=(0, 5))

    entry1 = tk.Entry(row_frame, width=5)
    entry1.pack(side="left", padx=5)

    entry2 = tk.Entry(row_frame, width=5)
    entry2.pack(side="left", padx=5)

    combo = ttk.Combobox(row_frame, values=display_names, state="readonly", width=20)
    combo.pack(side="left", padx=5)
    combo.set(display_names[0])

    # Confirm button
    confirm_button = tk.Button(window, text="Confirm", command=confirm_inputs)
    confirm_button.pack(pady=(0, 10))

    window.grab_set()
    window.wait_window()
    return command

def gopicky(command, directory):

    def show_output_gui(file_label_text, output_text, parent):
        
        def on_close():
            output_root.grab_release()
            output_root.destroy()

        output_root = tk.Toplevel(parent)
        output_root.title("Picky output")
        output_root.geometry("800x500")
        output_root.grab_set()
        output_root.focus_force()
        output_root.protocol("WM_DELETE_WINDOW", on_close)

        label = tk.Label(output_root, text=file_label_text, font=("Arial", 12, "bold"))
        label.pack(pady=5)

        text_area = scrolledtext.ScrolledText(output_root, font=("Arial", 12))
        text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        text_area.insert(tk.END, output_text)
        text_area.config(state="disabled")

        btn = tk.Button(output_root, text="Close", command=on_close)
        btn.pack(pady=10)

        parent.wait_window(output_root)

    def wait_for_process_to_finish(name):
        try:
            while True:
                active = any(name in p.name() for p in psutil.process_iter(attrs=["name"]))
                if not active:
                    break
        except Exception:
            pass

    def run_process():
        nonlocal output_text, file_label_text, found_out_file

        try:
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=directory
            )

            try:
                proc.stdin.write("y\n")
                proc.stdin.flush()
            except Exception:
                pass

            stdout, stderr = proc.communicate()

            if "go.getDeltaP" in command[0]:
                wait_for_process_to_finish("difpes")

            found_out_file = False
            for file in os.listdir(directory):
                if file.endswith(".out"):
                    file_label_text = f"Output file: {file}"
                    with open(os.path.join(directory, file), "r", encoding="utf-8") as f:
                        output_text = f.read()
                    found_out_file = True
                    break

            if not found_out_file:
                output_text = ""
                file_label_text = ""

        except Exception as e:
            output_text = str(e)
            file_label_text = "Execution Exception"

    # Crea root invisibile principale
    root = tk.Tk()
    root.withdraw()

    output_text = ""
    file_label_text = ""
    found_out_file = False

    thread = threading.Thread(target=run_process)
    thread.start()
    thread.join()  # Aspetta che il thread termini

    if found_out_file:
        open_gui = messagebox.askyesno("Open Picky output?", "Do you want to visualize Picky output?", parent=root)
        if open_gui:
            show_output_gui(file_label_text, output_text, parent=root)

    root.destroy()

def edit_resource(folder):
    
    def on_close():
        root_HW.destroy()
        root_HW.quit()
        main_GUI()

    def show_help():
        messagebox.showinfo("Help", 
            "This window allows you to insert hardware resource values for Gaussian input files (.com).\n\n"
            "- RAM: Insert the amount of memory to allocate.\n"
            "- Unit: Choose between MB (megabytes) or GB (gigabytes).\n"
            "- Processors: Set the number of CPU cores to use.\n\n"
            "After clicking Submit, all .com files in the selected folder will be updated with these values.")

    def on_submit():
        try:
            # Ottieni i valori inseriti nelle entry
            ram = float(entryram.get())
            ram_unit = memoryunit.get()
            nproc = float(entrycpu.get())
            
            # Chiudi la finestra dopo aver mostrato il risultato
            root_HW.quit()

            for filename in os.listdir(folder):
                if filename.endswith(".com"):
                    filepath = os.path.join(folder, filename)
                    with open (filepath, "r") as file:
                        righe = file.readlines()
                    if righe:
                        righe[0] = "%Mem=" + str(ram) + str(ram_unit) + "\n"
                        righe[1] = "%Nproc=" + str(nproc) + "\n"
                        with open(filepath, "w") as f:
                            f.writelines(righe)


        except ValueError as ve:
            print(f"Error: Choosen vaules are not valid: {ve}")
        except Exception as e:
            print(f"Error: {e}")
        root_HW.destroy()
        return 

    root_HW = tk.Tk()
    root_HW.title("Insert HW characteristics")
    root_HW.protocol("WM_DELETE_WINDOW", on_close)
    root_HW.geometry("320x175")
    
    # Crea etichette e entry per l'inserimento dei numeri
    labelram = tk.Label(root_HW, text="Insert value for RAM usage:")
    labelram.grid(row=1, column=0, pady=5)  # Aggiungi una piccola distanza verticale

    entryram = tk.Entry(root_HW, width=8)
    entryram.grid(row=2, column=0, padx=5, pady=2)  # Riduci lo spazio verticale e orizzontale

    memoryunit = ttk.Combobox(root_HW, values=["MB", "GB"], width=4)
    memoryunit.set("MB")
    memoryunit.grid(row=2, column=0, padx=(130, 0), pady=2)  # Usa lo stesso pady per ravvicinarlo

    labelcpu = tk.Label(root_HW, text="Insert value for Number of processors:")
    labelcpu.grid(row=4, column=0, padx=5, pady=5)

    entrycpu = tk.Entry(root_HW, width=8)
    entrycpu.grid(row=5, column=0)

    # Crea un pulsante per inviare i valori
    submit_button = tk.Button(root_HW, text="Submit", command=on_submit)
    submit_button.grid(row=6, column=0)

    # Botton help
    help_button = tk.Button(root_HW, text="?", width=2, command=show_help)
    help_button.grid(row=1, column=1, sticky="e", padx=5, pady=5)
    
    # Avvia la GUI
    root_HW.mainloop()

def edit_pickyfit_inp(file_path):

    def update_combo_par(event=None):
        # mostra i controlli quando serve
        label_combo_name.grid()
        combo_name.grid()
        label_combo_par.grid()
        combo_par.grid()
        label_entry_value.grid()
        entry_value.grid()

        sel_word = combo_words.get()

        # parametri per blocco (in base a WORDS_PICKYFIT_TEMPLATE)
        if sel_word == WORDS_PICKYFIT_TEMPLATE[0]:
            params = ["e0", "sigma", "csi"]
        elif sel_word == WORDS_PICKYFIT_TEMPLATE[1]:
            params = ["charge"]
        elif sel_word == WORDS_PICKYFIT_TEMPLATE[2]:
            params = ["e0", "sigma", "csi"]
        elif sel_word == WORDS_PICKYFIT_TEMPLATE[3]:
            params = ["charge"]
        else:
            params = []

        combo_par['values'] = params
        if params:
            combo_par.set(params[0])
        else:
            combo_par.set("")

        # aggiorna l’elenco dei "name" dal testo corrente (2a colonna delle righe del blocco)
        content = text_area.get("1.0", tk.END)
        lines = content.splitlines()
        names = set()

        found_block = False
        for line in lines:
            s = line.strip()
            if s.startswith(sel_word):
                found_block = True
                continue
            if found_block:
                # fine blocco: riga con "end" o riga separatrice ">"
                if "end" in s.lower() or ">" in s:
                    break
                parts = line.split()
                if len(parts) > 2:
                    names.add(parts[1])  # seconda colonna = name

        names_sorted = sorted(names)
        combo_name['values'] = names_sorted
        if names_sorted:
            combo_name.set(names_sorted[0])
        else:
            combo_name.set("")


    def edit(event=None):
        sel_word = combo_words.get()
        sel_par = combo_par.get()
        sel_name = combo_name.get()
        new_val = entry_value.get()

        if not sel_word or not sel_par or not sel_name:
            messagebox.showerror("ERROR", "Please select block, parameter and species.")
            return
        if new_val is None or new_val == "":
            messagebox.showerror("ERROR", "Please enter a value.")
            return

        content = text_area.get("1.0", tk.END)
        lines = content.splitlines()
        new_lines = []

        in_block = False
        header = []
        edited = False   # <--- flag per applicare UNA sola sostituzione

        for line in lines:
            stripped = line.strip()

            # inizio blocco
            if stripped.startswith(sel_word):
                in_block = True
                header = stripped.split()
                new_lines.append(line)
                continue

            if in_block:
                # fine blocco
                if "end" in stripped.lower():
                    in_block = False
                    new_lines.append(line)
                    # opzionale: se abbiamo già modificato, possiamo uscire prima
                    # per efficienza (ma non è obbligatorio)
                    # if edited: 
                    #     new_lines.extend(lines[lines.index(line)+1:])
                    #     break
                    continue

                # salta eventuali righe separatrici
                if ">" in stripped:
                    new_lines.append(line)
                    continue

                parts = line.split()

                # header può apparire sulla prima riga dati in alcune varianti
                if len(header) == 0 and not any(x == '=' for x in parts):
                    header = parts

                # se abbiamo già fatto una sostituzione, non toccare altro
                if edited:
                    new_lines.append(line)
                    continue

                # mappatura colonne e sostituzione SOLO sulla prima corrispondenza
                if len(header) > 0 and len(parts) >= len(header) - 1:
                    name = parts[1] if len(parts) > 1 else None
                    if name == sel_name:
                        try:
                            col_idx = header.index(sel_par) - 1
                            if 0 <= col_idx < len(parts):
                                parts[col_idx] = str(new_val)
                                line = '       ' + '      '.join(parts)
                                edited = True  # <--- da qui in poi non modifichiamo più
                        except Exception as e:
                            print(f"[edit] mapping error: {e}")

            new_lines.append(line)

        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, '\n'.join(new_lines))
        entry_value.delete(0, tk.END)

        if not edited:
            messagebox.showinfo("Info", "Nessuna riga corrispondente trovata nel blocco selezionato.")

    def save_file(event=None):
        content = text_area.get("1.0", "end-1c")
        if not content:
            messagebox.showerror("ERROR", "No content found")
            return
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            messagebox.showinfo("Successful", f"File {file_path} has been saved correctly.")
        except Exception as e:
            messagebox.showerror("Error", f"An error has occurred: {e}")

    def on_close():
        risposta = messagebox.askyesno("WARNING", "\nAre you sure?")
        if risposta:
            root.destroy()
            main_GUI()

    def continue_to_picky():
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
            root.title(f"Editor - {file_path} (Saved)")
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")
        root.quit()
        root.destroy()
    # === NEW: help window ===
    def show_help_pickyfit():
        win = tk.Toplevel(root)
        win.title("Help - PickyFit Editor")
        win.geometry("680x520")
        win.transient(root)
        win.grab_set()

        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Arial", 11), state="normal")
        txt.pack(fill="both", expand=True, padx=12, pady=(12, 4))

        # Nota: descrive i blocchi in base alla logica della funzione (e0/sigma/csi o charge)
        help_text = (
            "PickyFit Input Editor - Quick Help\n"
            "===================================\n\n"
            "Workflow\n"
            "--------\n"
            "1) Select input block: choose the section you want to edit from the dropdown.\n"
            "   • Some blocks expose parameters [e0, sigma, csi].\n"
            "   • Others expose [charge].\n\n"
            "2) Select parameter to edit: pick the parameter (e.g., e0, sigma, csi, or charge).\n\n"
            "3) Select species to edit: the list is auto-populated from the current text.\n"
            "   • Names are taken from the second column of each data line inside the selected block,\n"
            "     until an 'end' line or a '>' separator is found.\n\n"
            "4) Insert desired value: type the new value and click 'Edit'.\n"
            "   • The editor maps the chosen parameter to the correct column using the block header,\n"
            "     then replaces the value for the selected species on the first matching line.\n\n"
            "Buttons\n"
            "-------\n"
            "• Edit: applies the change to the in-memory text (not saved yet).\n"
            "• Save: writes the edited text back to disk.\n"
            "• Continue: saves and closes the editor, returning to Picky.\n"
            "• Close: prompts and closes the editor without saving if you confirm.\n\n"
            "Notes & Tips\n"
            "------------\n"
            "• If a block does not list any species, ensure the file is formatted with a header line\n"
            "  followed by data lines where the 2nd column is the species name.\n"
            "• Parameter mapping relies on the header tokens. If header/columns are misaligned,\n"
            "  the change may be skipped. Fix the header labels or the spacing if needed.\n"
            "• Edits preserve general spacing by rejoining tokens; fine-grained formatting may differ.\n"
        )
        txt.insert(tk.END, help_text)
        txt.configure(state="disabled")
        tk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 12))

    # --- GUI ---
    root = tk.Tk()
    root.title(f"Opening {file_path} ....")
    root.protocol("WM_DELETE_WINDOW", on_close)
    center_window(root)

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)

    # pannello controlli (destra)
    frame_controli = tk.Frame(root)
    frame_controli.grid(row=0, column=1, sticky='nsew')

    # header controlli con piccolo bottone "?"
    header_controls = tk.Frame(frame_controli)
    header_controls.grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=(6, 4))
    tk.Label(header_controls, text="Editing parameters:", font=("Arial", 11, "bold")).pack(side="left")
    tk.Button(header_controls, text="?", width=2, command=show_help_pickyfit).pack(side="right")

    # lascia crescere lo spazio vuoto tra i controlli e i bottoni in fondo
    # frame_controli.rowconfigure(8, weight=1)

    # pannello testo (sinistra)
    frame_text = tk.Frame(root)
    frame_text.grid(row=0, column=0, sticky='nsew')

    # label e area testo
    label_text_area = tk.Label(frame_text, text=f"Text of {file_path}")
    label_text_area.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    text_area = scrolledtext.ScrolledText(frame_text, wrap=tk.WORD)
    text_area.grid(row=1, column=0, padx=10, sticky="nsew")

    frame_text.rowconfigure(1, weight=1)
    frame_text.columnconfigure(0, weight=1)

    # carica file
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.read()
            text_area.insert(tk.END, lines)
    except Exception as e:
        print(f"[edit_pickyfit_inp] open error: {e}")

    # riga 1: scelta blocco
    label_combo_words = tk.Label(frame_controli, text="Select input block:")
    label_combo_words.grid(row=1, column=0, pady=5, sticky="w")

    combo_words = ttk.Combobox(frame_controli, values=WORDS_PICKYFIT_TEMPLATE[0:-1], state="readonly", width=12)
    combo_words.grid(row=1, column=1, padx=(2, 10), pady=5)
    combo_words.set(WORDS_PICKYFIT_TEMPLATE[0])
    combo_words.bind("<<ComboboxSelected>>", update_combo_par)

    # riga 2: parametro
    label_combo_par = tk.Label(frame_controli, text="Select parameter to edit:")
    label_combo_par.grid(row=2, column=0, pady=5, sticky="w")

    combo_par = ttk.Combobox(frame_controli, values=[], state="readonly", width=12)
    combo_par.grid(row=2, column=1, padx=(2, 10), pady=5)

    # riga 3: specie
    label_combo_name = tk.Label(frame_controli, text="Select species to edit:")
    label_combo_name.grid(row=3, column=0, pady=5, sticky="w")

    combo_name = ttk.Combobox(frame_controli, values=[], state="readonly", width=12)
    combo_name.grid(row=3, column=1, padx=(2, 10), pady=5)

    # riga 4: valore
    label_entry_value = tk.Label(frame_controli, text="Insert desired value:")
    label_entry_value.grid(row=4, column=0, pady=5, sticky="w")

    entry_value = ttk.Entry(frame_controli, width=14)
    entry_value.grid(row=4, column=1, padx=(2, 10), pady=5)

    # riga 5: Edit
    edit_button = tk.Button(frame_controli, text="Edit", command=edit)
    edit_button.grid(row=5, column=1, padx=(2, 10), pady=5, sticky="nsew")

    # riga 6: Save
    save_button = tk.Button(frame_controli, text="Save", command=save_file)
    save_button.grid(row=6, column=1, padx=(2, 10), pady=10, sticky="nsew")

    # riga 7: spacer (riempitivo)
    label_spacer = tk.Label(frame_controli)
    label_spacer.grid(row=7, column=0, columnspan=2, sticky="nsew")

    # riga 8-9: Continue & Close
    continue_button = tk.Button(frame_controli, text="Continue", command=continue_to_picky)
    continue_button.grid(row=8, column=1, padx=(2, 10), pady=(10, 6), sticky="nsew")

    close_button = tk.Button(frame_controli, text="Close", command=on_close)
    close_button.grid(row=9, column=1, padx=(2, 10), pady=(6, 16), sticky="nsew")

    # inizializza le combo dipendenti
    update_combo_par()

    root.mainloop()

def replace_row_in_file(file_path, old_row_start, new_row):
    """Replace rows that start with 'old_row_start' with 'new row'"""

    # Leggi tutte le righe
    with open(file_path, "r") as file:
        righe = file.readlines()

    # Sostituisci la riga desiderata
    righe_modificate = [new_row if riga.startswith(old_row_start) else riga for riga in righe]

    # Scrivi le righe modificate nel file
    with open(file_path, "w") as file:
        file.writelines(righe_modificate)

def aggiorna_file_con_input(file_path):
    chiavi = ["energygrps", "tc_grps", "ref_t", "ref_p"]
    entries = {}

    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale se non necessaria

    # Finestra modale secondaria
    window = tk.Toplevel()
    window.title("Update Gromacs Directives")
    window.grab_set()       # Rende la finestra modale
    window.focus_force()    # Porta in primo piano
    window.resizable(False, False)

    # Costruisci i campi input
    for i, chiave in enumerate(chiavi):
        tk.Label(window, text=f"{chiave}:").grid(row=i, column=0, sticky="e", padx=5, pady=2)
        entry = tk.Entry(window, width=30)
        entry.grid(row=i, column=1, padx=5, pady=2)
        entries[chiave] = entry

    def conferma():
        nuovi_valori = {k: e.get().strip() for k, e in entries.items()}

        try:
            with open(file_path, 'r') as f:
                righe = f.readlines()

            with open(file_path, 'w') as f:
                for riga in righe:
                    sostituita = False
                    for chiave, valore in nuovi_valori.items():
                        if riga.strip().startswith(chiave):
                            f.write(f"{chiave} = {valore}\n")
                            sostituita = True
                            break
                    if not sostituita:
                        f.write(riga)

            messagebox.showinfo("Success", "File updated!", parent=window)
            window.destroy()
            root.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Error during edit:\n{e}", parent=window)

    def on_close():
        if messagebox.askokcancel("Close", "Do you want to close without saving?", parent=window):
            window.destroy()
            root.quit()

    window.protocol("WM_DELETE_WINDOW", on_close)

    tk.Button(window, text="Confirm", command=conferma).grid(row=len(chiavi), columnspan=2, pady=10)

    root.mainloop()

def select_cycle_root(base_dir):
    """
    Ritorna sempre una tupla (subfolders, cycle_num, subfolders_prev).
    - Se l'utente annulla/chiude o non ci sono cartelle 'Cycle*': (None, None, None).
    - Altrimenti: (dict_subfolders, int_cycle_num, dict_prev_or_None).
    """
    # Elenco cartelle Cycle*
    try:
        cycle_dirs = {
            d.lower(): d for d in os.listdir(base_dir)
            if os.path.isdir(os.path.join(base_dir, d)) and d.lower().startswith("cycle")
        }
    except Exception as e:
        messagebox.showerror("Error", f"Unable to list directory:\n{e}")
        return (None, None, None)

    if not cycle_dirs:
        messagebox.showwarning("No Cycle folders found",
                               "No folders starting with 'Cycle' were found in the current directory.")
        return (None, None, None)

    # Prompt finché non inserisce un numero valido o annulla
    while True:
        prompt_root = tk.Tk()
        prompt_root.withdraw()

        # Usa askinteger per evitare isdigit / input non numerici
        folders_list = ", ".join(sorted(cycle_dirs.values(), key=str.lower))
        cycle_num = simpledialog.askinteger(
            "Select Cycle Folder",
            f"The following 'Cycle' folders were found:\n\n{folders_list}\n\n"
            f"Enter the cycle number (e.g., 3 for Cycle3):",
            parent=prompt_root,
            minvalue=0  # puoi usare 1 se non esistono Cycle0
        )
        prompt_root.destroy()

        # Utente ha annullato/chiuso
        if cycle_num is None:
            return (None, None, None)

        cycle_folder_key = f"cycle{cycle_num}".lower()
        if cycle_folder_key not in cycle_dirs:
            messagebox.showerror("Not found", f"No folder named '{cycle_folder_key}' exists.")
            continue

        # Input valido -> esci dal loop
        break

    selected_folder = cycle_dirs[cycle_folder_key]
    base_path = os.path.abspath(os.path.join(base_dir, selected_folder))
    subfolders = {
        "base": base_path,
        "picky": os.path.join(base_path, "1.picky"),
        "qmsampling": os.path.join(base_path, "2.QMsampling"),
        "fit": os.path.join(base_path, "3.fit"),
        "deltaP": os.path.join(base_path, "4.deltaP"),
        "MD": os.path.join(base_path, "5.MD"),
        0: base_path,
        1: os.path.join(base_path, "1.picky"),
        2: os.path.join(base_path, "2.QMsampling"),
        3: os.path.join(base_path, "3.fit"),
        4: os.path.join(base_path, "4.deltaP"),
        5: os.path.join(base_path, "5.MD"),
    }

    # Cycle precedente (se esiste)
    cycle_folder_key_prev = f"cycle{cycle_num - 1}".lower()
    if cycle_folder_key_prev in cycle_dirs:
        selected_folder_prev = cycle_dirs[cycle_folder_key_prev]
        base_path_prev = os.path.abspath(os.path.join(base_dir, selected_folder_prev))
        subfolders_prev = {
            "base": base_path_prev,
            "picky": os.path.join(base_path_prev, "1.picky"),
            "qmsampling": os.path.join(base_path_prev, "2.QMsampling"),
            "fit": os.path.join(base_path_prev, "3.fit"),
            "deltaP": os.path.join(base_path_prev, "4.deltaP"),
            "MD": os.path.join(base_path_prev, "5.MD"),
            0: base_path_prev,
            1: os.path.join(base_path_prev, "1.picky"),
            2: os.path.join(base_path_prev, "2.QMsampling"),
            3: os.path.join(base_path_prev, "3.fit"),
            4: os.path.join(base_path_prev, "4.deltaP"),
            5: os.path.join(base_path_prev, "5.MD"),
        }
    else:
        subfolders_prev = None

    # Restituisce SEMPRE tre valori
    return subfolders, cycle_num, subfolders_prev

# =======INTERFACE STEPS===========
def step_beta(cycle_paths, cycle_num, cycle_paths_prev):

    working_folder = cycle_paths[1]
    
    if int(cycle_num) == 1:
        copy_files(os.path.join(picky_root,"Templates"),"basis.dat",working_folder,"")
        for i in range (2):
            if i == 0:
                message = "Select '.top' file to use"
                top_file_name = copy_selected_file(working_folder,"",message, extension="top")
                specie_name = top_file_name.split(sep='.')[0]
            if i == 1:
                message = "Select '.gro' file to use"
                copy_selected_file(working_folder,"",message, extension=".gro")

        new_name_inp = "picky." + specie_name + f".cycle{int(cycle_num)}.inp"
        extension = "inp"
        inp_file_found = any(file.endswith(extension) for file in os.listdir(working_folder))

        if inp_file_found:
            messagebox.showinfo("Note", f"A {extension} file is already present in {working_folder}")
        else:
            copy_files(os.path.join(picky_root, "Templates"),"picky.template.inp",working_folder,new_name_inp)
   
        if not top_file_name:
            messagebox.showerror("Error", "File .top not selected, impossible to proceed.")
            return
        replace_row_in_file(os.path.join(working_folder,new_name_inp),"$Parameters", f"$Parameters {top_file_name}\n")
        replace_row_in_file(os.path.join(working_folder,new_name_inp),"$Traj", f"$Traj final.opls.gro\n")
    
    if int(cycle_num) > 1:            
        copy_files(cycle_paths_prev[1], "basis.dat", cycle_paths[1], "")
        copy_files(cycle_paths_prev[1], "accepted.dat", cycle_paths[1], "")
        copy_files(cycle_paths_prev[1], "energy.dat", cycle_paths[1], "energy.dat.old")
        copy_files(cycle_paths_prev[1], "IntCoord.dat", cycle_paths[1], "IntCoord.dat.old")

        for file in os.listdir(cycle_paths_prev[1]):
            if file.endswith("top"):
                specie_name = os.path.basename(file).split('.')[0]
        new_name_inp = copy_files(cycle_paths_prev[1], f"picky.{specie_name}.cycle{int(cycle_num)-1}.inp", cycle_paths[1], f"picky.{specie_name}.cycle{int(cycle_num)}.inp") # copy .inp
        top_file_name = copy_files(cycle_paths_prev[5], f"{specie_name}.cycle{int(cycle_num)-1}.top", cycle_paths[1], "") #copy .top
        copy_files(cycle_paths_prev[5], f"final.cycle{int(cycle_num)-1}.gro", cycle_paths[1], "") #copy .gro
        replace_row_in_file(os.path.join(working_folder,new_name_inp),"$Parameters", f"$Parameters {top_file_name}\n")
        replace_row_in_file(os.path.join(working_folder,new_name_inp),"$Traj", f"$Traj final.cycle{int(cycle_num) - 1}.gro\n")
    
    edit_inp_file(os.path.join(working_folder,new_name_inp))

    # command = build_gopicky_command(specie_name, cycle_num)
    command_folder = cycle_paths[1]
    command = build_gopicky_command_from_folder(command_folder)
    
    # print(command)
    gopicky(command, directory=command_folder)
    
def step_gamma(cycle_paths):
    
    def show_help_step_gamma(parent=None):
        """Small help window for Step Gamma (QM Recover)."""
        win = tk.Toplevel(parent) if parent else tk.Toplevel()
        win.title("Help - Step Gamma (QM Recover)")
        win.geometry("520x360")
        if parent:
            win.transient(parent)
        win.grab_set()

        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, state="normal")
        txt.pack(fill="both", expand=True, padx=12, pady=(12, 4))

        help_text = (
            "Step Gamma - QM Recover\n"
            "=======================\n\n"
            "Enter the QM method to be used by Pickyrecover.\n"
            "   • Examples: mp2, hf, b3lyp, pbe0.\n"
            "   • The value is passed to:  go.pickyrecover <method>\n\n"
            )
        txt.insert(tk.END, help_text)
        txt.configure(state="disabled")

        tk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 12))

    working_directory = cycle_paths[2]

    # 1) scegli cartella con file .log
    selected_folder = filedialog.askdirectory(title="Select folder for Gaussian files")
    if not selected_folder:
        messagebox.showwarning("Warning", "No folder selected. Operation aborted.")
        return

    i = 0
    try:
        for file in os.listdir(selected_folder):
            if file.lower().endswith(".log"):
                source = os.path.join(selected_folder, file)
                destination = working_directory
                shutil.copy(source, destination)
                i += 1
        messagebox.showinfo("Info", f"{i} files were copied to {destination}")
    except Exception as e:
        messagebox.showwarning("Warning", f"Error {e} while copying files .log")
        return

    # 2) finestra custom per metodo + help
    method = None
    prompt = tk.Tk()
    prompt.title("Pickyrecover method selection")
    prompt.geometry("360x150")
    prompt.transient()
    # prompt.grab_set()

    # header con bottone "?"
    header = tk.Frame(prompt)
    header.pack(fill="x", padx=10, pady=(10, 4))
    tk.Label(header, text="Specify the method (e.g., mp2, hf, b3lyp):").pack(side="left")
    tk.Button(header, text="?", width=2, command=lambda: show_help_step_gamma(prompt)).pack(side="right")

    # entry
    entry = tk.Entry(prompt, width=22, justify="left")
    entry.pack(fill="x", padx=10, pady=4)
    entry.focus_set()

    # pulsanti
    btns = tk.Frame(prompt)
    btns.pack(pady=8)

    def on_ok():
        nonlocal method
        method = entry.get().strip()
        prompt.destroy()
    def on_cancel():
        prompt.destroy()
    
    tk.Button(btns, text="OK", width=10, command=on_ok).pack(side="left", padx=5)
    tk.Button(btns, text="Cancel", width=10, command=on_cancel).pack(side="left", padx=5)

    prompt.bind("<Return>", lambda e: on_ok())
    prompt.bind("<Escape>", lambda e: on_cancel())
    prompt.wait_window(prompt)

    if not method:
        messagebox.showwarning("Warning", "No method specified. Operation aborted.")
        return

    # 3) run pickyrecover
    command = ["go.pickyrecover", method]
    gopicky(command, working_directory)

def step_delta(cycle_paths, cycle_num):
    
    working_directory = cycle_paths[3]
    for file in os.listdir(cycle_paths[1]):
        if file.endswith("top"):
            specie_name = os.path.basename(file).split('.')[0]

    copy_files(cycle_paths[2], "geo.list.dat", working_directory, f"cycle{cycle_num}.QM.dat")
    copy_files(os.path.join(picky_root,"Templates"), "pickyfit.template.inp", working_directory, f"pickyfit.{specie_name}.cycle{cycle_num}.inp")
    path = os.path.join(working_directory,f"pickyfit.{specie_name}.cycle{cycle_num}.inp")
    replace_row_in_file(path, "cycle", f"cycle{cycle_num}.QM.dat\n")
    edit_pickyfit_inp(path)
    command = ["go.pickyfit", f"{specie_name}.{os.path.basename(cycle_paths[0]).lower()}"]
    command_folder = working_directory
    gopicky(command, command_folder)

def step_eta(cycle_paths, cycle_num):

    working_directory = cycle_paths[4]
    rel_working_dir = os.path.relpath(working_directory, start=os.getcwd())
    prev_cycle_num = int(cycle_num) - 1
    for file in os.listdir(cycle_paths[1]):
        if file.endswith("top"):
            specie_name = os.path.basename(file).split('.')[0]
    if int(cycle_num) == 1:
        copy_files(os.path.join(picky_root, "Templates"), "mesh.inp", working_directory, "mesh.inp")
    else:
        copy_selected_file(working_directory, "mesh.inp", f"Select mesh file to copy inside {rel_working_dir}", "")

    copy_files(cycle_paths[3], "potgen.inp", working_directory, "cycle" + str(cycle_num) + ".potgen")
    copy_selected_file(working_directory, "cycle" + str(prev_cycle_num) + ".potgen", "Select previous trial parameters", "")

    command = ["go.getDeltaP", "-dp", f"cycle{int(prev_cycle_num)}", f"cycle{int(cycle_num)}"]
    command_folder = working_directory
    
    gopicky(command, command_folder)

    log_path = os.path.join(working_directory, "DeltaP.log")
    try:
        with open(log_path, 'r') as f:
            text = f.readlines()
            for line in text:
                if "Standard Deviation" in line:
                    std_dev = line.split()[-1]
                    messagebox.showinfo("Convergence test ended", f"Standard Deviation: {std_dev}")
                    break
                
    except Exception as e:
        messagebox.ERROR("Error", f"error:{e}")

def step_alpha(cycle_paths, cycle_num):
    
    replacements = {}
    working_directory = cycle_paths[5]
    for file in os.listdir(cycle_paths[1]):
        if file.endswith("top"):
            specie_name = os.path.basename(file).split('.')[0]

    copy_files(os.path.join(picky_root, "Templates"), "gromacs.directives.mdp", working_directory,"NPT.mdp")
    if int(cycle_num) == 1:
        copy_files(cycle_paths[1], "final.opls.gro", working_directory, "")
        copy_files(cycle_paths[1], f"{specie_name}.opls.top", working_directory, f"{specie_name}.cycle{cycle_num}.top")
    else:
        copy_files(cycle_paths[1], f"final.cycle{int(cycle_num) - 1}.gro", working_directory, "")
        copy_files(cycle_paths[1], f"{specie_name}.cycle{int(cycle_num) - 1}.top", working_directory, f"{specie_name}.cycle{cycle_num}.top")

    
    # aggiorna_file_con_input(os.path.join(working_directory, "NPT.mdp"))
    edit_npt_file(os.path.join(working_directory, "NPT.mdp"))
    
    file_path_for_extr = os.path.join(cycle_paths[3], "gromacs.prms")
    file_path_to_insert = os.path.join(cycle_paths[5], f"{specie_name}.cycle{cycle_num}.top")
    words_list = ["atomtypes", "atoms"]
    replacements = extract_section_from_file_with_list(file_path_for_extr, words_list)
    replace_sections_in_file(file_path_to_insert, replacements)
    
def main():

    main_GUI()

if __name__ == "__main__":
    main()
