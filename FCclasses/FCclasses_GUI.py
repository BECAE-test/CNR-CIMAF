#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import subprocess
import re

state1_file_name = ""
state2_file_name = ""
magdip_name = ""
eldip_name = ""

DEFAULT_KEYWORDS = [
    "BOLTZHR", "BROADFUN", "C1MAX", "C2MAX", "COORDS", "DE", "DISP_FILE", "DISP_OUT", "DIPDER_COORD", "DUSCH_FILE", "DUSCH_OUT",
    "ELDIP_FILE", "ENER1_FILE", "ENER2_FILE", "FORCE_REAL", "FREQ1_FILE", "FREQ2_FILE", "G2_VERT", "GRADE2_FILE", "GRAD1_FILE", "GRAD2_COORD", "GRAD2_FILE",
    "HESS1_FILE", "HESS2_FILE", "HR_OUT", "HWHM2", "IC_FILE", "IC_FORM", "MAGDIP_FILE", "MASS_FILE", "MAXINT", "METHOD", "MODEL", "NAC_COORD", "NAC_FILE", "NAC_REF",
    "NAT", "NMODE_EXC", "NORMALMODES", "NQMODE_EXC", "NRCOUP_FILE", "NVIB", "PROPERTY", "RED2NONRED", "RESOL", "RM_COORD", "RM_COORD_INDS", "RM_IC_FILE", "ROTATE",
    "RR_DOUBLE_MAXEXC", "RR_DOUBLE_MODES", "RR_FIELDMAX", "RR_FIELDMIN", "RR_NFIELD", "RR_POLAR", "RR_SINGLE_MAXEXC", "RR_SINGLE_MODES", "RR_SPEED", "SPCMAX", "SPCMIN",
    "STATE1_FILE", "STATE2_FILE", "TEMP", "TPA_POLARIZED", "TRA_POLARIZED", "VERBOSE", "FILENAME"
]

FULL_CONFIG_INP = """$$$
;GENERAL OPTIONS:
; NAT        = (read from structure files)
; NVIB       = (determined vibrational analysis)
PROPERTY     =   OPA   
MODEL        =   AH   
DIPOLE       =   FC   
DIPDER_COORD =   CARTESIAN  
TEMP         =     0.00
DE           =  (read)
BROADFUN     =   GAU  
HWHM         =   0.0100
RESOL        =   0.0010  ; (default: HWHM/10)
METHOD       =   TD   
ROT          =   1
SPCMIN       =  (estimated)
SPCMAX       =  (estimated)
;CLASSIC SPECTRUM
CLASSIC      =   YES 
CLASS_NTRIAL =   1000
CLASS_PRINT_CONF =  NO
;VIBRATIONAL ANALYSIS
NORMALMODES  =   COMPUTE  
RM_COORD     =   NONE    
COORDS       =   CARTESIAN  
FORCE_REAL   =   NO   
;INPUT DATA FILES
STATE1_FILE  =   state1.fcc
STATE2_FILE  =   state2.fcc
MASS_FILE    =   
ELDIP_FILE   =   eldip
MAGDIP_FILE  =   magdip
NAC_FILE     =   
NRCOUP_FILE  =   nrcoup
HESS1_FILE   =   hess1.fcc
HESS2_FILE   =   hess2.fcc
GRAD1_FILE   =   grad1.fcc
GRAD2_COORD  =   CARTESIAN
GRAD2_FILE   =   grad2.fcc
;VERBOSE LEVEL
VERBOSE      =   1
"""

REDUCED_CONFIG_INP = """$$$
PROPERTY     =   OPA  ; OPA/EMI/ECD/CPL/RR/TPA/TPCD/MCD/IC/NRSC
MODEL        =   AH   ; AS/ASF/AH/VG/VGF/VH
DIPOLE       =   FC   ; FC/HTi/HTf
TEMP         =   0.00 ; (temperature in K) 
;DE           = (read) ; (adiabatic/vertical energy in eV. By default, read from state files) 
BROADFUN     =   GAU  ; GAU/LOR/VOI
HWHM         =   0.01 ; (broadening width in eV)
METHOD       =   TD   ; TI/TD
;VIBRATIONAL ANALYSIS 
NORMALMODES  =   COMPUTE   ; COMPUTE/READ/IMPLICIT
COORDS       =   CARTESIAN ; CARTESIAN/INTERNAL
;INPUT DATA FILES 
STATE1_FILE  =   state1.fcc
STATE2_FILE  =   state2.fcc
ELDIP_FILE   =   eldip
"""
#  Dizionario che mappa il tipo ai relativi valori
CATEGORY_VALUES_MAP = {
    "PROPERTY": ["OPA", "EMI", "ECD", "CPL", "MCD", "TPA", "TPCD", "RR", "IC", "NRSC", "NR0", "VIB"],
    "BROADFUN": ["GAU", "LOR", "VOI"],
    "MODEL": ["AH", "VH", "AS", "VG", "ASF", "VGF"],
    "METHOD": ["TI", "TD", "D"],
    "DIPOLE": ["FC", "HTi", "HTf"],
    "ROTATE": ["-1", "0", "1", "2"],
    "VERBOSE": ["0", "1", "2", "3"],
    "RR_POLAR": ["W", "R", "C"],
    "RR_SPEED": ["YES", "NO"],
    "TPA_POLARIZED": ["LINEAR", "CIRCULAR"],
    "NORMALMODES": ["COMPUTE", "READ", "IMPLICIT"],
    "COORDS": ["CARTESIAN", "INTERNAL"],
    "FORCE_REAL": ["YES", "NO"],
    "RM_COORD": ["NONE", "S1GRAD", "S1MODES", "S2MODES", "FILE", "NRINDEX", "RINDEX"],
    "IC_FORM": ["ALL", "ZMAT", "FILE"],
    "RED2NONRED": ["REIMERS", "filename"],
    "G2_VERT": ["1", "2"],
    "GRAD2_COORD": ["CARTESIAN", "NORMALMODE1"],
    "DIPDER_COORD": ["CARTESIAN", "NORMALMODE1", "NORMALMODE2"],
    "NAC_COORD": ["CARTESIAN", "NORMALMODE1", "NORMALMODE2"],
    "NAC_REF": ["ICi", "ICf"]
}

SHOW_BUTTON_KEYWORDS = {
    "TR_POLATIZABILITY_STATEFIN_1",
    "TR_POLATIZABILITY_STATEFIN_2",
    "FILE",
    "FILENAME",
    "STATE1_FILE",
    "STATE2_FILE",
    "MASS_FILE",
    "HESS1_FILE",
    "HESS2_FILE",
    "GRAD1_FILE",
    "GRADE2_FILE",
    "ENER1_FILE",
    "ENER2_FILE",
    "IC_FILE",
    "RM_IC_FILE",
    "ELDIP_FILE",
    "MAGDIP_FILE",
    "NRCOUP_FILE",
    "NAC_FILE",
    "DUSCH_FILE",
    "DISP_FILE",
    "FREQ1_FILE",
    "FREQ2_FILE"
}

DEPENDENCIES = {
    "NRCOUP_FILE":      lambda ctx: ctx.get("PROPERTY") == "NRSC",
    "NAC_FILE":         lambda ctx: ctx.get("PROPERTY") == "IC",
    "RR_SPEED":         lambda ctx: ctx.get("METHOD") == "TI" and ctx.get("DIPOLE") == "FC",
    "S1GRAD":           lambda ctx: ctx.get("COORDS") == "CARTESIAN",
    "S1MODES":          lambda ctx: ctx.get("COORDS") == "CARTESIAN",
    "S2MODES":          lambda ctx: ctx.get("COORDS") == "CARTESIAN",
    "S1GRAD":           lambda ctx: ctx.get("COORDS") == "INTERNAL",
    "S1MODES":          lambda ctx: ctx.get("COORDS") == "INTERNAL",
    "S2MODES":          lambda ctx: ctx.get("COORDS") == "INTERNAL",
    "NONE":             lambda ctx: ctx.get("COORDS") == "INTERNAL",
    "FILE":             lambda ctx: ctx.get("COORDS") == "INTERNAL",
    "NRINDEX":          lambda ctx: ctx.get("COORDS") == "INTERNAL",
    "RINDEX":           lambda ctx: ctx.get("COORDS") == "INTERNAL",
    "ELDIP_FILE":       lambda ctx: ctx.get("PROPERTY") in ("OPA", "EMI", "ECD", "CPL", "MCD", "RR"),
    "MAGDIP_FILE":      lambda ctx: ctx.get("PROPERTY") in ("ECD", "CPL", "MCD"),
    "ROTATE":           lambda ctx: ctx.get("PROPERTY") in ("TPA", "TPDC", "IC"),
    "RR_NFIELD":        lambda ctx: ctx.get("METHOD") in ("TI", "TD"),
    "RR_FIELDMIN":      lambda ctx: ctx.get("METHOD") in ("TI", "TD"),
    "RR_FIELDMAX":      lambda ctx: ctx.get("METHOD") in ("TI", "TD"),
    "RR_POLAR":         lambda ctx: ctx.get("METHOD") in ("TI", "TD"),
    "RR_SINGLE_MODES":  lambda ctx: ctx.get("METHOD") in ("TI", "TD"),
    "RR_DINGLE_MAXEXC": lambda ctx: ctx.get("METHOD") in ("TI", "TD"),
    "RR_DOUBLE_MODES":  lambda ctx: ctx.get("METHOD") in ("TI", "TD"),
    "RR_DOUBLE_MAXEXC": lambda ctx: ctx.get("METHOD") in ("TI", "TD"),
    "RR_SPEED":         lambda ctx: ctx.get("METHOD") in ("TI", "TD"),
    "BOLTZTHR":         lambda ctx: ctx.get("METHOD") == "TI",
    "C1MAX":            lambda ctx: ctx.get("METHOD") == "TI",
    "C2MAX":            lambda ctx: ctx.get("METHOD") == "TI",
    "MAXINT":           lambda ctx: ctx.get("METHOD") == "TI",
    "BROADFUN":         lambda ctx: ctx.get("METHOD") == "TD"

}

def show_output(result, window_title):
    """
    Mostra l'output di un comando in una finestra popup con scorrimento.

    :param result: Oggetto con attributo .stdout contenente l'output da mostrare
    :param window_title: Titolo della finestra popup
    """
    if not window_title:
        window_title = "Command Output"

    # Crea una nuova finestra
    output_window = tk.Toplevel()
    output_window.title(window_title)
    output_window.geometry("600x400")

    # Aggiungi una Textbox scrollabile
    text_area = scrolledtext.ScrolledText(output_window, wrap=tk.WORD, width=70, height=20)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Inserisci l'output
    text_area.insert(tk.END, result.stdout if result and hasattr(result, 'stdout') else "No output available.")

    # Rendi la textbox sola lettura
    text_area.config(state=tk.DISABLED)

    # Bottone di chiusura
    close_btn = tk.Button(output_window, text="Close", command=output_window.destroy)
    close_btn.pack(pady=5)


def edit_inp_file(file_path):
    """Opens a text file given a path and displays it in a GUI with a combobox for word selection.
    A collapsible help banner is shown at the top to guide the user.
    """
    # --- IMPORT ASSUMPTIONS ---
    # Richiede: import os, re, tkinter as tk, from tkinter import ttk, filedialog, messagebox, scrolledtext
    clicked_index = None

    # -----------------------------
    # HELP BANNER (top)
    # -----------------------------

    # -----------------------------
    # (Tutto il resto del tuo codice originale)
    # -----------------------------
    def select_file():
        file_sel = filedialog.askopenfilename(
            title="Select file",
            filetypes=[("All files", "*"), ("Data files", "*.dat"), ("Text files", "*.txt")],
            parent=root
        )
        if file_sel:
            filename = os.path.basename(file_sel)
            keyword = KW_in_text.get()
            if not keyword:
                return
            new_content = ""
            for line in text_area.get("1.0", tk.END).splitlines():
                line = line.strip()
                if line.startswith(keyword):
                    parts = line.split()
                    if len(parts) >= 3:
                        parts[2] = filename
                    new_line = "    ".join(parts)
                    new_content += new_line + "\n"
                else:
                    new_content += line + "\n"
            text_area.replace("1.0", tk.END, new_content)
            refresh_word_combobox2()

    def select_file_right():
        file_sel = filedialog.askopenfilename(
            title="Select file",
            filetypes=[("All files", "*"), ("Data files", "*.dat"), ("Text files", "*.txt")],
            parent=root
        )
        if not file_sel:
            return
        filename = os.path.basename(file_sel)
        keyword = (KW_not_in_text.get() or "").strip()
        if not keyword:
            return
        lines = text_area.get("1.0", tk.END).splitlines()
        found = False
        new_lines = []
        for raw in lines:
            line = raw.strip()
            if line.startswith(keyword):
                parts = line.split()
                if len(parts) >= 3:
                    parts[2] = filename
                    new_lines.append("    ".join(parts))
                else:
                    new_lines.append(f"{keyword}    =    {filename}")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"{keyword}    =    {filename}")
        text_area.replace("1.0", tk.END, "\n".join(new_lines) + "\n")
        refresh_word_combobox2()

    def new_dependence():
        nonlocal clicked_index
        label_index = 0
        selected_lines = []
        built_lines = []
        selected_output_index = [None]
        file_top_path = filedialog.askopenfilename(title="Select topology file")

        def get_next_label():
            nonlocal label_index
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            result = ""
            i = label_index
            while True:
                result = alphabet[i % 26] + result
                i = i // 26 - 1
                if i < 0:
                    break
            label_index += 1
            return result

        def on_click(event):
            index = text_widget.index(f"@{event.x},{event.y}")
            line_num = int(index.split('.')[0])
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            line_text = text_widget.get(line_start, line_end)
            if line_text.strip().startswith(";") or not line_text.strip():
                return
            for i, (ln, _, tag) in enumerate(selected_lines):
                if ln == line_num:
                    text_widget.tag_delete(tag)
                    selected_lines.pop(i)
                    generate_button.config(state=tk.NORMAL if len(selected_lines) == 2 else tk.DISABLED)
                    return
            tag_name = f"sel_{line_num}"
            text_widget.tag_add(tag_name, line_start, line_end)
            text_widget.tag_config(tag_name, background="lightblue")
            selected_lines.append((line_num, line_text, tag_name))
            if selected_lines:
                generate_button.config(state=tk.NORMAL)

        def generate_line():
            if not selected_lines:
                return
            label = get_next_label()
            for _, line_text, _ in selected_lines:
                cleaned_line = line_text.strip()
                if not cleaned_line:
                    continue
                first_char = cleaned_line[0]
                rest_of_line = cleaned_line[1:].strip()
                new_line = f"{first_char}{{{label}:1.0}} {rest_of_line}"
                output_widget.insert(tk.END, new_line + "\n")
                built_lines.append(new_line)
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

        def save_and_exit():
            output_text = '\n'.join(built_lines)
            if not output_text.strip():
                messagebox.showinfo("Info", "No content to save.")
                return
            out_path = filedialog.asksaveasfilename(
                defaultextension=".dat",
                filetypes=[("Data files", "*.dat"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Save generated block as...",
                parent=root
            )
            if out_path:
                try:
                    with open(out_path, "w") as f:
                        f.write(output_text + "\n")
                    messagebox.showinfo("Success", f"File saved:\n{out_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file:\n{e}")
            text_area.insert(tk.END, f"RM_IC_FILE = {os.path.basename(out_path)}")
            root_dep.destroy()
            return out_path

        # child window
        root_dep = tk.Toplevel()
        root_dep.title(f"Line selection - {file_top_path}")

        main_frame = tk.Frame(root_dep)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        text_widget = scrolledtext.ScrolledText(left_frame, width=80, height=20)
        text_widget.pack(padx=10, pady=10)
        text_widget.bind("<Button-1>", on_click)

        output_widget = scrolledtext.ScrolledText(left_frame, width=80, height=10)
        output_widget.pack(padx=10, pady=5)
        output_widget.bind("<Button-1>", on_output_click)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        logo_path = os.path.join(os.getcwd(), "table_IC.png")
        if os.path.exists(logo_path):
            try:
                logo = tk.PhotoImage(file=logo_path)
                logo_label = tk.Label(right_frame, image=logo)
                logo_label.image = logo
                logo_label.pack(pady=(0, 20))
            except Exception:
                tk.Label(right_frame, text="Image not available").pack(pady=(0, 20))
        else:
            tk.Label(right_frame, text="Image not found").pack(pady=(0, 20))

        generate_button = tk.Button(right_frame, text="Generate", command=generate_line, state=tk.DISABLED)
        generate_button.pack(pady=5, fill=tk.X)

        delete_button = tk.Button(right_frame, text="Delete selected line", command=delete_selected_output_line)
        delete_button.pack(pady=5, fill=tk.X)

        continue_button = tk.Button(right_frame, text="Continue", command=save_and_exit)
        continue_button.pack(pady=5, fill=tk.X)

        try:
            with open(file_top_path) as f:
                text_widget.insert(tk.END, f.read())
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {file_top_path}")
            root_dep.destroy()

        root_dep.mainloop()

    def on_text_click(event):
        nonlocal clicked_index
        clicked_index = text_area.index(f"@{event.x},{event.y}")

    def return_to_gui():
        root.destroy()
        gui.mainloop()

    def save_file_as():
        try:
            chosen_path = filedialog.asksaveasfilename(
                title="Save File As",
                defaultextension=".inp",
                filetypes=[("Inp Files", "*.inp"), ("All Files", "*.*")]
            )
            if not chosen_path:
                return
            with open(chosen_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
            root.title(f"Editor - {chosen_path} (Saved)")
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")

    def extract_first_words():
        words = []
        lines = text_area.get("1.0", tk.END).splitlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith(";") and not line.startswith("$"):
                first_word = line.split()[0]
                words.append(first_word)
        return words

    def on_close():
        root.quit()
        root.destroy()

    def refresh_word_combobox2():
        nonlocal first_words
        current_text = text_area.get("1.0", tk.END)
        first_words = extract_first_words()
        missing_keywords = get_missing_and_compatible_keywords(current_text, first_words)

        old_left = KW_in_text.get()
        KW_in_text.configure(values=first_words)
        if old_left in first_words:
            KW_in_text.set(old_left)
        elif first_words:
            KW_in_text.set(first_words[0])
        else:
            KW_in_text.set("")

        old_right = KW_not_in_text.get()
        KW_not_in_text.configure(values=missing_keywords)
        if old_right in missing_keywords:
            KW_not_in_text.set(old_right)
        elif missing_keywords:
            KW_not_in_text.set(missing_keywords[0])
        else:
            KW_not_in_text.set("")
        update_value_combobox(None)

    def insert_keyword_left():
        kWord_in_text = (KW_in_text.get() or "").strip()
        left_value = (mode_KW_in_text.get() or mode_KW_in_text_entry.get() or "").strip()
        if not kWord_in_text:
            messagebox.showerror("Error", "No word selected on the LEFT panel.")
            return
        if not left_value:
            messagebox.showerror("Error", "You must enter or select a value on the LEFT panel.")
            return

        new_content = ""
        for line in text_area.get("1.0", tk.END).split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith(kWord_in_text):
                words = line.split()
                if len(words) > 2:
                    words[2] = left_value
                else:
                    words = [kWord_in_text, "=", left_value]
                new_content += "    ".join(words) + "\n"
            else:
                new_content += line + "\n"
        text_area.replace("1.0", tk.END, new_content)
        mode_KW_in_text_entry.delete(0, tk.END)
        refresh_word_combobox2()

    def insert_keyword_right():
        kWord_not_in_text = (KW_not_in_text.get() or "").strip()
        right_value = (mode_KW_not_in_text.get() or mode_KW_not_in_text_entry.get() or "").strip()
        if not kWord_not_in_text:
            messagebox.showerror("Error", "No word selected on the RIGHT panel.")
            return
        if not right_value:
            messagebox.showerror("Error", "You must enter or select a value on the RIGHT panel.")
            return

        current_text = text_area.get("1.0", "end-1c").strip()
        lines = current_text.splitlines() if current_text else []
        replaced = False
        new_lines = []
        for raw in lines:
            line = raw.strip()
            if line.startswith(kWord_not_in_text):
                parts = line.split()
                if len(parts) >= 3:
                    parts[2] = right_value
                    new_lines.append("    ".join(parts))
                else:
                    new_lines.append(f"{kWord_not_in_text}    =    {right_value}")
                replaced = True
            else:
                new_lines.append(line)
        if not replaced:
            new_lines.append(f"{kWord_not_in_text}    =    {right_value}")

        text_area.replace("1.0", tk.END, "\n".join(new_lines) + "\n")
        mode_KW_not_in_text_entry.delete(0, tk.END)
        refresh_word_combobox2()

    def update_file():
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))
            root.title(f"Editor - {file_path} (Saved)")
        except Exception as e:
            messagebox.showerror("Error", f"Error while saving:\n{e}")

    def advanced_command():
        nonlocal first_words
        nonlocal KW_in_text
        nonlocal content
        text_area.delete("1.0", "end")
        text_area.insert("1.0", FULL_CONFIG_INP)
        first_words = extract_first_words()
        KW_in_text.configure(values=first_words)
        refresh_word_combobox2()

    def normal_command():
        nonlocal first_words
        nonlocal KW_in_text
        nonlocal content
        text_area.delete("1.0", "end")
        text_area.insert("1.0", REDUCED_CONFIG_INP)
        first_words = extract_first_words()
        KW_in_text.configure(values=first_words)
        refresh_word_combobox2()
        update_value_combobox(None)

    def update_value_combobox(event=None):
        context = extract_keywords_from_text(text_area.get("1.0", tk.END))
        kWord_in_text = selected_word.get()

        mode_KW_in_text.grid_forget()
        mode_KW_in_text_entry.grid_forget()
        select_file_button.grid_forget()

        show_button_left = (
            kWord_in_text in SHOW_BUTTON_KEYWORDS or
            any(v in SHOW_BUTTON_KEYWORDS for v in CATEGORY_VALUES_MAP.get(kWord_in_text, []))
        )
        if (kWord_in_text or "").strip().upper() not in ("RM_COORD", "MR_COORD") and show_button_left:
            select_file_button.grid(row=4, column=0, pady=5, sticky="ew")

        if kWord_in_text in CATEGORY_VALUES_MAP and is_compatible(kWord_in_text, context):
            values = CATEGORY_VALUES_MAP[kWord_in_text]
            mode_KW_in_text.configure(values=values)
            mode_KW_in_text.current(0)
            mode_KW_in_text.grid(row=2, column=0, pady=5, sticky="ew")
        else:
            entry_value_text.set("")
            if not show_button_left:
                mode_KW_in_text_entry.grid(row=3, column=0, pady=5, sticky="ew")

        kWord_not_in_text = KW_not_in_text.get()
        mode_KW_not_in_text.grid_forget()
        mode_KW_not_in_text_entry.grid_forget()
        select_file_not_in_text_button.grid_forget()

        show_button_right = (
            kWord_not_in_text in SHOW_BUTTON_KEYWORDS or
            any(v in SHOW_BUTTON_KEYWORDS for v in CATEGORY_VALUES_MAP.get(kWord_not_in_text, []))
        )
        if kWord_not_in_text != "RM_COORD" and show_button_right:
            select_file_not_in_text_button.grid(row=4, column=0, pady=5, sticky="ew")

        if kWord_not_in_text in CATEGORY_VALUES_MAP and is_compatible(kWord_not_in_text, context):
            mode_KW_not_in_text.configure(values=CATEGORY_VALUES_MAP[kWord_not_in_text])
            mode_KW_not_in_text.current(0)
            mode_KW_not_in_text.grid(row=2, column=0, pady=5, sticky="ew")
        else:
            entry_value_not_in_text.set("")
            if not show_button_right:
                mode_KW_not_in_text_entry.grid(row=3, column=0, pady=5, sticky="ew")

    def extract_keywords_from_text(text):
        keywords = {}
        for line in text.splitlines():
            if line.strip().startswith(";") or not line.strip():
                continue
            match = re.match(r"^(\w+)\s*=\s*(.+)", line.strip())
            if match:
                key, value = match.groups()
                value = value.split(";")[0].strip()
                keywords[key.upper()] = value.upper()
        return keywords

    def is_compatible(keyword, context):
        check = DEPENDENCIES.get(keyword)
        return check(context) if check else True

    def get_missing_and_compatible_keywords(content, first_words):
        context = extract_keywords_from_text(content)
        return [kw for kw in DEFAULT_KEYWORDS if kw not in first_words and is_compatible(kw, context)]

    # ------------- caricamento iniziale contenuto (come nel tuo codice) -------------
    loaded_file_path = None

    def _pick_inp_from_list(inp_files):
        win = tk.Toplevel()
        win.title("Select .inp from current folder")
        win.resizable(False, False)
        tk.Label(win, text="Found the following .inp files in the current folder:").pack(padx=10, pady=(10, 4), anchor="w")
        lb = tk.Listbox(win, height=min(12, max(4, len(inp_files))), exportselection=False)
        for f in inp_files:
            lb.insert(tk.END, f)
        lb.pack(padx=10, pady=4, fill="both", expand=True)
        choice = {"value": None}

        def load_selected():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("No selection", "Please select a file from the list.")
                return
            basename = inp_files[sel[0]]
            choice["value"] = os.path.join(os.getcwd(), basename)
            win.destroy()

        def load_template():
            choice["value"] = "__TEMPLATE__"
            win.destroy()

        def on_close():
            choice["value"] = None
            win.destroy()

        btn_frame = tk.Frame(win)
        btn_frame.pack(padx=10, pady=(4, 10), fill="x")
        tk.Button(btn_frame, text="Load selected", command=load_selected).pack(side="left")
        tk.Button(btn_frame, text="Load reduced template", command=load_template).pack(side="right")
        win.protocol("WM_DELETE_WINDOW", on_close)
        win.grab_set()
        win.transient()
        win.wait_window()
        return choice["value"]

    help_win = {"ref": None}  # per riusare la stessa finestra

    def open_help_window():
        """Apre (o porta avanti) una finestra di aiuto separata."""
        # se esiste già, mettila avanti
        if help_win["ref"] is not None and help_win["ref"].winfo_exists():
            help_win["ref"].deiconify()
            help_win["ref"].lift()
            help_win["ref"].focus_force()
            return

        hw = tk.Toplevel()
        help_win["ref"] = hw
        hw.title("Guida rapida all’editor .inp")
        hw.geometry("780x520")  # regola se vuoi
        hw.minsize(560, 360)

        # chiudi: azzera il riferimento
        def _on_close():
            try:
                hw.destroy()
            finally:
                help_win["ref"] = None
        hw.protocol("WM_DELETE_WINDOW", _on_close)

        # contenitore
        outer = tk.Frame(hw, padx=14, pady=14)
        outer.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(
            outer, text="❓ Guida rapida all’editor .inp",
            font=("Arial", 13, "bold")
        )
        title.pack(anchor="w", pady=(0, 8))

        # area scorrevole per il testo di aiuto
        st = scrolledtext.ScrolledText(outer, wrap=tk.WORD, font=("Arial", 10))
        st.pack(fill=tk.BOTH, expand=True)

        # testo help (modifica liberamente)
        st.insert(tk.END, (
            "• LEFT Panel (K-word in text): select a keyword already present and replace its value "
            "with one from the list or by typing it in manually. Use “Select file” when the keyword "
            "requires a file path.\n\n"
            "• RIGHT Panel (K-word not in text): choose a missing keyword and insert the line "
            "“KEY = value” (or replace it if it already exists). The “Select file” button appears "
            "only for file-like keywords.\n\n"
            "• Central editor: you can freely edit the text; the comboboxes update in real time "
            "\n\n"
            "• Templates: “Advanced properties” loads the complete configuration, "
            "while “Standard properties” loads the reduced one.\n\n"
            "• RM_IC_file: “Create RM_IC_file” opens a selector/preview to build the block "
            "and save it; upon closing, the reference in the text is updated "
            "(RM_IC_FILE = <file.dat>).\n\n"
            "• Saving: “Save” writes to the current file, while “Save file as” lets you choose "
            "a new path.\n\n"
            "Shortcuts: press F1 to open this help window."
        ))
        st.config(state="disabled")  # sola lettura

        # pulsante chiudi
        btn_row = tk.Frame(outer)
        btn_row.pack(fill=tk.X, pady=(10, 0))
        tk.Button(btn_row, text="Chiudi", command=_on_close).pack(side=tk.RIGHT)


    try:
        inp_in_dir = sorted([f for f in os.listdir(os.getcwd()) if f.lower().endswith(".inp")])
    except Exception:
        inp_in_dir = []

    if inp_in_dir:
        selected = _pick_inp_from_list(inp_in_dir)
        if selected == "__TEMPLATE__":
            content = REDUCED_CONFIG_INP
        elif selected:
            try:
                with open(selected, "r", encoding="utf-8") as f:
                    content = f.read()
                loaded_file_path = selected
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file:\n{e}\nThe reduced template will be used instead.")
                content = REDUCED_CONFIG_INP
        else:
            browse = messagebox.askyesno(
                "No choice made",
                "No file was selected.\nDo you want to select a .inp file to load?\n(Click 'No' to load the reduced template.)"
            )
            if browse:
                chosen = filedialog.askopenfilename(
                    title="Select .inp file",
                    initialdir=os.getcwd(),
                    filetypes=[("Input files", "*.inp"), ("All files", "*")]
                )
                if chosen:
                    try:
                        with open(chosen, "r", encoding="utf-8") as f:
                            content = f.read()
                        loaded_file_path = chosen
                    except Exception as e:
                        messagebox.showerror("Error", f"Error opening file:\n{e}\nThe reduced template will be used instead.")
                        content = REDUCED_CONFIG_INP
                else:
                    content = REDUCED_CONFIG_INP
            else:
                content = REDUCED_CONFIG_INP
    else:
        browse = messagebox.askyesno(
            "No .inp files found",
            "No '.inp' files were found in the current folder.\nDo you want to select a .inp file to load?\n(Click 'No' to load the reduced template.)"
        )
        if browse:
            chosen = filedialog.askopenfilename(
                title="Select .inp file",
                initialdir=os.getcwd(),
                filetypes=[("Input files", "*.inp"), ("All files", "*")]
            )
            if chosen:
                try:
                    with open(chosen, "r", encoding="utf-8") as f:
                        content = f.read()
                    loaded_file_path = chosen
                except Exception as e:
                    messagebox.showerror("Error", f"Error opening file:\n{e}\nThe reduced template will be used instead.")
                    content = REDUCED_CONFIG_INP
            else:
                content = REDUCED_CONFIG_INP
        else:
            content = REDUCED_CONFIG_INP

    if loaded_file_path:
        file_path = loaded_file_path

    # -----------------------------
    # MAIN WINDOW
    # -----------------------------
    root = tk.Toplevel()
    root.title(f"Editor - {file_path}")
    root.protocol("WM_DELETE_WINDOW", lambda: (root.quit(), root.destroy()))

    # grid base
    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    topbar = tk.Frame(root)
    topbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
    topbar.grid_columnconfigure(0, weight=1)

    tk.Label(topbar, text="Editor .inp", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w")
    tk.Button(topbar, text="?", width=3, command=open_help_window).grid(row=0, column=1, sticky="e")

    # bind F1 alla stessa finestra di aiuto
    root.bind("<F1>", lambda e: open_help_window())



    # main frame (come prima)
    frame = tk.Frame(root)
    frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(2, weight=1)
    frame.grid_columnconfigure(3, weight=0)
    frame.grid_columnconfigure(4, weight=0)

    # text area
    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Arial", 12))
    text_area.grid(row=0, column=2, sticky="nsew")
    text_area.delete("1.0", "end")
    text_area.insert("1.0", content)

    first_words = extract_first_words()

    # LEFT panel
    left_panel = tk.Frame(frame)
    left_panel.grid(row=0, column=3, padx=10, sticky="ns")
    left_panel.grid_rowconfigure(99, weight=1)
    left_panel.grid_columnconfigure(0, weight=1)

    tk.Label(left_panel, text="Select K-word in text").grid(row=0, column=0, pady=2, sticky="ew")
    selected_word = tk.StringVar()
    KW_in_text = ttk.Combobox(left_panel, textvariable=selected_word, values=first_words, state="readonly")
    if first_words:
        KW_in_text.current(0)
    KW_in_text.grid(row=1, column=0, pady=5, sticky="ew")

    selected_value = tk.StringVar()
    mode_KW_in_text = ttk.Combobox(left_panel, textvariable=selected_value, values=[], state="readonly")
    mode_KW_in_text.grid(row=2, column=0, pady=5, sticky="ew")

    entry_value_text = tk.StringVar()
    mode_KW_in_text_entry = ttk.Entry(left_panel, textvariable=entry_value_text)
    mode_KW_in_text_entry.grid(row=3, column=0, pady=5, sticky="ew")

    select_file_button = tk.Button(left_panel, text="Select file", command=select_file, height=1)
    select_file_button.grid(row=4, column=0, pady=5, sticky="ew")
    select_file_button.grid_remove()

    insert_left = tk.Button(left_panel, text="Replace", command=insert_keyword_left, height=1)
    insert_left.grid(row=11, column=0, padx=10, pady=5, sticky="ew")

    # RIGHT panel
    right_panel = tk.Frame(frame)
    right_panel.grid(row=0, column=4, padx=10, sticky="ns")
    right_panel.grid_rowconfigure(99, weight=1)
    right_panel.grid_columnconfigure(0, weight=1, minsize=220)

    tk.Label(right_panel, text="Select K-word NOT in text").grid(row=0, column=0, pady=2, sticky="ew")

    missing_keywords = get_missing_and_compatible_keywords(content, first_words)
    KW_not_in_text = ttk.Combobox(right_panel, values=missing_keywords, state="readonly")
    if missing_keywords:
        KW_not_in_text.current(0)
    KW_not_in_text.grid(row=1, column=0, pady=5, sticky="ew")

    selected_value_not_in_text = tk.StringVar()
    mode_KW_not_in_text = ttk.Combobox(right_panel, textvariable=selected_value_not_in_text, values=[], state="readonly")
    mode_KW_not_in_text.grid(row=2, column=0, pady=5, sticky="ew")

    entry_value_not_in_text = tk.StringVar()
    mode_KW_not_in_text_entry = ttk.Entry(right_panel, textvariable=entry_value_not_in_text)
    mode_KW_not_in_text_entry.grid(row=3, column=0, pady=5, sticky="ew")

    select_file_not_in_text_button = tk.Button(right_panel, text="Select file", command=select_file_right, height=1)
    select_file_not_in_text_button.grid(row=4, column=0, pady=5, sticky="ew")
    select_file_not_in_text_button.grid_remove()

    insert_right = tk.Button(right_panel, text="Insert", command=insert_keyword_right, height=1)
    insert_right.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

    insert_adv = tk.Button(right_panel, text="Advanced properties", command=advanced_command, height=1)
    insert_adv.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

    insert_std = tk.Button(right_panel, text="Standard properties", command=normal_command, height=1)
    insert_std.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

    insert_dep = tk.Button(right_panel, text="Create RM_IC_file", command=new_dependence, height=1)
    insert_dep.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

    save_button = tk.Button(right_panel, text="Save", command=update_file, height=1)
    save_button.grid(row=9, column=0, pady=10, sticky="ew")

    save_as_button = tk.Button(right_panel, text="Save file as", command=save_file_as, height=1)
    save_as_button.grid(row=10, column=0, pady=10, sticky="ew")

    close_button = tk.Button(right_panel, text="Close edit window", command=return_to_gui, height=1)
    close_button.grid(row=100, column=0, pady=10, sticky="ew")

    # bindings
    def extract_keywords_from_text_wrapper(text):
        return extract_keywords_from_text(text)

    text_area.bind("<KeyRelease>", lambda event: refresh_word_combobox2())
    text_area.bind("<Button-1>", on_text_click)
    KW_in_text.bind("<<ComboboxSelected>>", update_value_combobox)
    KW_not_in_text.bind("<<ComboboxSelected>>", update_value_combobox)

    if first_words:
        update_value_combobox(None)

    root.mainloop()


def FCclasses_install():
    """ Esegue i comandi di installazione all'interno della cartella selezionata. """
    
    def FCclasses_test():
        """ Crea una finestra con una domanda e due pulsanti (Yes e No). """
        ans = messagebox.askyesno(title="Test FCclasses", message="Do you want to test FCclasses?")
        if ans == True:
            try:
                result = subprocess.run(["make", "test"], cwd=folder_path, capture_output=True, text=True, check=True)
                print("Comando eseguito con successo!")
                print(result.stdout)  # Stampa l'output del comando

            except subprocess.CalledProcessError as e:
                print(f"Errore durante l'esecuzione: {e}")
                print(f"Output dell'errore: {e.stderr}")  # Mostra l'output dell'errore

            except Exception as e:
                print(f"Errore imprevisto: {e}")
        else:
            messagebox.showinfo(title="Info", message="FCclasses won't be tested")

    comandi = [["./configure"], ["make"]]
    risultati = {}
    folder_path = filedialog.askdirectory(title="Select FCclasses folder")

    if folder_path:
        messagebox.showinfo("Folder selected", f"Selected folder is:\n{folder_path}")    
    else:
        messagebox.showwarning("No folder selected", "The installation has been aborted.")
        
    for comando in comandi:
        try:
            process = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=folder_path)
            stdout, stderr = process.communicate()  # Attende la fine del comando
            risultati[" ".join(comando)] = {"stdout": stdout.strip(),"stderr": stderr.strip(),"returncode": process.returncode}
            
            if process.returncode != 0:
                print(f"Errore nell'esecuzione di: {' '.join(comando)}")
                print(stderr.strip())

        except Exception as e:
            risultati[" ".join(comando)] = {"stdout": "","stderr": str(e),"returncode": -1}
            print(f"Errore generale: {str(e)}")

    try:
        result = subprocess.run(["sudo", "make", "install"], cwd=folder_path, capture_output=True, text=True, check=True)
        print("Comando eseguito con successo!")
        print(result.stdout)  # Stampa l'output del comando (facoltativo)

    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione: {e}")
        print(f"Output dell'errore: {e.stderr}")  # Mostra l'output dell'errore

    except Exception as e:
        print(f"Errore imprevisto: {e}")

    messagebox.showinfo("Installation completed", "The program has been installed successfully!")
    
    FCclasses_test()
    return 

def select_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    file_paths = {}
    
    while "state1" not in file_paths:
        file1 = filedialog.askopenfilename(title="Select the file for state 1", filetypes=[("All files", "*.*")])
        if file1:
            file_paths["state1"] = file1
        else:
            return
    while "state2" not in file_paths:
        file2 = filedialog.askopenfilename(title="Select the file for state 2", filetypes=[("All files", "*.*")])
        if file2:
            file_paths["state2"] = file2
        else:
            return
    if not file1 and not file2:
        return None
    return file_paths

def execute_gen_commands(command, folder):
    try:
        result = subprocess.run(command, cwd=folder, capture_output=True, text=True, check=True)
        ans = messagebox.askyesno("Visualize output..", f"Do you want to visualize output from {command[0]}?")
        if ans:
            show_output(result, f"Output from {command[0]}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        show_output(e, f"Output from {command[0]}")
        return
    
def execute_fcclasses3_inpTemplate():
    try:
        result = subprocess.run(["fcclasses3", "-h"], capture_output=True, text=True, check=True)
        # print(result.stdout)
        with open("fcc.inp", "w") as file:
            file.write(result.stdout)
    except FileNotFoundError:
        messagebox.showerror("Error:", "The command 'fcclasses3' was not found. Make sure it is installed and in the PATH.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error:", f"Error executing the command: {e}")
    
def replace_word_in_file(file_path, target_word, replacement):
    try:
        with open(file_path, "r") as file:
            content = file.read()
        
        content = content.replace(target_word, replacement)
        
        with open(file_path, "w") as file:
            file.write(content)
        messagebox.showinfo("Successful:", f"Replacement completed: '{target_word}' -> '{replacement}' in {file_path}.")
    except FileNotFoundError:
        messagebox.showerror("Error:", f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        messagebox.showerror("Error:", f"Error while modifying the file: {e}")

def build_gen_fcc_state_command():
    """
    GUI to build a gen_fcc_state command by selecting .inp files from working_dir.
    Returns the assembled command as a list of strings (with filename cleaned).
    """
    command = []

    selected_file = filedialog.askopenfilename(title="Select file to run gen_fcc_state")
    if not selected_file:
        return 
    file_name = os.path.basename(selected_file)
    file_dir = os.path.dirname(selected_file)

    def show_help():
        help_win = tk.Toplevel(window)
        help_win.title("Help - gen_fcc_state")

        help_text = (
            "This interface allows you to build a 'gen_fcc_state' command.\n\n"
            "Steps:\n"
            "1️⃣ Select the checkpoint file you want to process (already done before opening this window).\n"
            "2️⃣ Optionally, you can add a command-line flag (default '-i')\n"
            "   - Example: '-i' will be included as a parameter in the command.\n"
            "3️⃣ The selected filename is automatically appended to the command.\n\n"
            "Final command example:\n"
            "    gen_fcc_state -i selected_file\n\n"
            "Press 'Confirm' to execute the command."
        )

        label = tk.Label(help_win, text=help_text, justify="left", padx=10, pady=10, wraplength=420)
        label.pack()

        close_btn = tk.Button(help_win, text="Close", command=help_win.destroy)
        close_btn.pack(pady=5)
    # -------------------------------------------------

    def confirm_inputs():
        cmd1 = entry1.get().strip()
        
        if not file_name:
            messagebox.showerror("Missing selection", "You must select a file.")
            return

        command.append("gen_fcc_state")
        if cmd1:
            command.append(cmd1)
        command.append(file_name)
        window.destroy()
        execute_gen_commands(command, file_dir)

    # --- GUI Setup ---
    window = tk.Tk()    
    window.title("Build gen_fcc_state command")

    # Top frame with help icon
    top_frame = tk.Frame(window)
    top_frame.pack(anchor="ne", pady=(5, 0), padx=5)
    
    help_button = tk.Button(top_frame, text="❓", command=show_help, relief="flat", font=("Arial", 10, "bold"))
    help_button.pack()

    # Command-line style row
    row_frame = tk.Frame(window)
    row_frame.pack(padx=10, pady=10)

    tk.Label(row_frame, text="gen_fcc_state").pack(side="left", padx=(0, 5))

    entry1 = tk.Entry(row_frame, width=5)
    entry1.pack(side="left", padx=5)
    entry1.insert(0,"-i")

    tk.Label(row_frame, text=f"{file_name}").pack(side="left", padx=(0, 5))

    # Confirm button
    confirm_button = tk.Button(window, text="Confirm", command=confirm_inputs)
    confirm_button.pack(pady=(0, 10))

    window.grab_set()
    window.wait_window()
    return

def build_gen_fcc_dipfile_command():
    """
    GUI to build a gen_fcc_dipfile command by selecting .inp files from working_dir.
    Returns the assembled command as a list of strings (with filename cleaned).
    """
    command = []

    selected_file = filedialog.askopenfilename(title="Select file to run gen_fcc_dipfile")
    if not selected_file:
        return
    file_name = os.path.basename(selected_file)
    file_dir = os.path.dirname(selected_file)

    def show_help():
        help_win = tk.Toplevel(window)
        help_win.title("Help - gen_fcc_dipfile")

        help_text = (
            "This interface allows you to build a 'gen_fcc_dipfile' command.\n\n"
            "Steps:\n"
            "1️⃣ Select the .inp file you want to process (already done before opening this window).\n"
            "2️⃣ Optionally, you can add a command-line flag (e.g., '-i')\n"
            "   - Example: '-i' will be included as a parameter in the command.\n"
            "3️⃣ The selected filename is automatically appended to the command.\n\n"
            "Final command example:\n"
            "    gen_fcc_dipfile -i selected_file.inp\n\n"
            "Press 'Confirm' to execute the command."
        )
        label = tk.Label(help_win, text=help_text, justify="left", padx=10, pady=10, wraplength=420)
        label.pack()

        close_btn = tk.Button(help_win, text="Close", command=help_win.destroy)
        close_btn.pack(pady=5)

    def confirm_inputs():
        cmd1 = entry1.get().strip()
        
        if not file_name:
            messagebox.showerror("Missing selection", "You must select a file.")
            return

        command.append("gen_fcc_dipfile")
        if cmd1:
            command.append(cmd1)
        command.append(file_name)
        window.destroy()
        execute_gen_commands(command, file_dir)

    # --- GUI Setup ---
    window = tk.Tk()    
    window.title("Build gen_fcc_dipfile command")

    # Top frame with help icon
    top_frame = tk.Frame(window)
    top_frame.pack(anchor="ne", pady=(5, 0), padx=5)
    help_button = tk.Button(top_frame, text="❓", command=show_help, relief="flat", font=("Arial", 10, "bold"))
    help_button.pack()

    # Command-line style row
    row_frame = tk.Frame(window)
    row_frame.pack(padx=10, pady=10)

    tk.Label(row_frame, text="gen_fcc_state").pack(side="left", padx=(0, 5))

    entry1 = tk.Entry(row_frame, width=5)
    entry1.pack(side="left", padx=5)
    entry1.insert(0,"-i")

    tk.Label(row_frame, text=f"{file_name}").pack(side="left", padx=(0, 5))

    # Confirm button
    confirm_button = tk.Button(window, text="Confirm", command=confirm_inputs)
    confirm_button.pack(pady=(0, 10))

    window.grab_set()
    window.wait_window()
    return

def run_fcclasses():
    file_path = filedialog.askopenfilename(title="Select input file to run", filetypes=[("inp", "*.inp*")])
    """Executes the 'fcclasses3' command with the given file path."""
    try:
        process = subprocess.run(["fcclasses3", file_path], capture_output=True, text=True, check=True)
        if process.returncode != 0:
            messagebox.showerror("Error", f"Unexpected error: {process.stderr}")
            return
        ans = messagebox.askyesno("Visualize output..", "Do you want to visualize output from FCclasses?")
        if ans:
            try:
                with open("fcc.out", "r") as f:
                    output = f.read()

                # Mostra il contenuto in una finestra popup
                output_window = tk.Toplevel()
                output_window.title("Output - fcc.out")
                output_window.geometry("600x400")

                text_area = scrolledtext.ScrolledText(output_window, wrap=tk.WORD, width=70, height=20)
                text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
                text_area.insert(tk.END, output)
                text_area.config(state=tk.DISABLED)

                close_btn = tk.Button(output_window, text="Close", command=output_window.destroy)
                close_btn.pack(pady=5)

            except FileNotFoundError:
                messagebox.showerror("Error", "fcc.out not found.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not read fcc.out:\n{e}")

    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")
        return

def generate_state_file():

    build_gen_fcc_state_command()  

def generate_dipole_file():
    
    build_gen_fcc_dipfile_command()
            
def select_state_files():
    global state1_file_name, state2_file_name
    state1_path = []
    # state1_file_name = ""
    file1_name_ext = []
    state2_path = []
    # state2_file_name = ""
    file2_name_ext = []
    selected_files = select_files()
    if not selected_files:
        messagebox.showerror("Error:", "No file selected!")
        return
    state1_path = selected_files["state1"]
    state2_path = selected_files["state2"]
    file1_name_ext = os.path.basename(state1_path)
    file2_name_ext = os.path.basename(state2_path)
    state1_file_name = os.path.splitext(file1_name_ext)[0]
    state2_file_name = os.path.splitext(file2_name_ext)[0]

def select_magdip_file():
    global magdip_name
    # magdip_name = ""
    magdip_path = []
    magdip_path = filedialog.askopenfilename(title="Select Magdip File")
    if not magdip_path:
        return
    magdip_name_ext = os.path.basename(magdip_path)
    magdip_name = os.path.splitext(magdip_name_ext)[0]

def select_eldip_file():
    global eldip_name
    # eldip_name = ""
    eldip_path = []
    eldip_path = filedialog.askopenfilename(title="Select Eldip File")
    if not eldip_path:
        messagebox.showerror("Error:", "No file selected!")
        return
    eldip_name_ext = os.path.basename(eldip_path)
    eldip_name = os.path.splitext(eldip_name_ext)[0]

def edit_input_file(file_INP_path):
    global state1_file_name, state2_file_name, magdip_name, eldip_name, gui
    edit_inp_file(file_INP_path)

def main():
    """Main function to execute the workflow for processing FCC classes files."""
    global gui
    file_INP = "fcc.inp"
    file_INP_path = os.path.join(os.getcwd(), file_INP)
    
    gui = tk.Tk()
    gui.title("Main GUI")
    
    btn1 = tk.Button(gui, text="Generate State File", width=20, height=1, command=lambda: generate_state_file())
    btn1.grid(row=0, column=0, padx=10, pady=5)

    btn2 = tk.Button(gui, text="Generate Dipole File", width=20, height=1, command=lambda: generate_dipole_file())
    btn2.grid(row=1, column=0, padx=10, pady=5)

    btn6 = tk.Button(gui, text="Edit Input File", width=20, height=1, command=lambda: edit_input_file(file_INP_path))
    btn6.grid(row=5, column=0, padx=10, pady=5)

    btn7 = tk.Button(gui, text="Run FCclasses", width=20, height=1, command=lambda: run_fcclasses())
    btn7 .grid(row=6, column=0, padx=10, pady=5)

    gui.mainloop()

    return

if __name__ == "__main__":
    main()