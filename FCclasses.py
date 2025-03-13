import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Listbox, Toplevel, ttk
import os
import subprocess


DEFAULT_KEYWORDS = [
    "NAT", "NVIB", "DE", "HWHM2", "RESOL", "SPCMIN", "SPCMAX", "NMODE_EXC", 
    "NQMODE_EXC", "ROTATE", "VERBOSE", "BOLTZHR", "C1MAX", "C2MAX", "MAXINT", 
    "RR_NFIELD", "RR_FIELDMIN", "RR_FIELDMAX", "RR_POLAR", "RR_SINGLE_MODES", 
    "RR_SINGLE_MAXEXC", "RR_DOUBLE_MODES", "RR_DOUBLE_MAXEXC", "RR_SPEED", 
    "TRA_POLARIZED", "FORCE_REAL", "RM_COORD", "RM_COORD_INDS", "IC_FORM", 
    "RED2NONRED", "G2_VERT", "MASS_FILE", "HESS1_FILE", "HESS2_FILE", "GRAD1_FILE", 
    "GRADE2_FILE", "ENER1_FILE", "ENER2_FILE", "IC_FILE", "RM_IC_FILE", "MAGDIP_FILE", 
    "NRCOUP_FILE", "NAC_FILE", "NAC_REF", "DUSCH_FILE", "DISP_FILE", "FREQ1_FILE", 
    "FREQ2_FILE", "GRAD2_FILE", "GRAD2_COORD", "DIPDER_COORD", "NAC_COORD"
]

def FCclasses_install():
    """ Mostra una finestra per chiedere se installare FCclasses, e in caso positivo chiede una cartella. """

    def install_fcclasses(folder_path):
        """ Esegue i comandi di installazione all'interno della cartella selezionata. """
        comandi = [
            ["./configure"],  
            ["make"]
        ]
        risultati = {}

        for comando in comandi:
            try:
                process = subprocess.Popen(
                    comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=folder_path
                )
                
                stdout, stderr = process.communicate()  # Attende la fine del comando
                
                risultati[" ".join(comando)] = {
                    "stdout": stdout.strip(),
                    "stderr": stderr.strip(),
                    "returncode": process.returncode
                }
                
                if process.returncode != 0:
                    print(f"Errore nell'esecuzione di: {' '.join(comando)}")
                    print(stderr.strip())

            except Exception as e:
                risultati[" ".join(comando)] = {
                    "stdout": "",
                    "stderr": str(e),
                    "returncode": -1
                }
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
        
        return folder_path

    def on_yes():
        """ L'utente ha scelto di installare FCclasses, quindi chiede una cartella. """
        root.withdraw()  # Nasconde la finestra principale temporaneamente

        folder_path = filedialog.askdirectory(title="Select FCclasses folder")

        if folder_path:
            messagebox.showinfo("Folder selected", f"Selected folder is:\n{folder_path}")
            install_fcclasses(folder_path)  # Avvia l'installazione nella cartella scelta
        else:
            messagebox.showwarning("No folder selected", "The installation has been aborted.")

        root.destroy()

    def on_no():
        """ L'utente ha scelto di non installare. """
        messagebox.showinfo("Aswer", "FCclasses will not be installed.")
        root.destroy()

    # Creazione della finestra principale
    root = tk.Tk()
    root.title("FCclasses Install")

    # Ottieni le dimensioni dello schermo per centrare la finestra
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calcola la posizione per centrare la finestra
    pos_x = (screen_width // 2) - 100
    pos_y = (screen_height // 2) - 50

    # Imposta la posizione senza specificare dimensioni
    root.geometry(f"+{pos_x}+{pos_y}")

    # Etichetta con la domanda
    label = tk.Label(root, text="Do you want to install FCclasses?", font=("Arial", 14))
    label.pack(pady=10)

    # Contenitore per i pulsanti
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Pulsanti Yes e No
    yes_button = tk.Button(button_frame, text="Yes", command=on_yes, width=10)
    yes_button.pack(side=tk.LEFT, padx=10)

    no_button = tk.Button(button_frame, text="No", command=on_no, width=10)
    no_button.pack(side=tk.RIGHT, padx=10)

    # Avvio della finestra
    root.mainloop()

def FCclasses_test():
    global command_path
    command_path = ""
    """ Crea una finestra con una domanda e due pulsanti (Yes e No). """
    def on_yes():
        global command_path  # Permette di modificare la variabile globale

        # Se command_path non è già impostato, chiedi all'utente di selezionare una cartella
        if not command_path:
            selected_folder = filedialog.askdirectory(title="Select FCclasses folder for testing")
            if selected_folder:  # Controlla che l'utente abbia selezionato una cartella
                command_path = selected_folder
            else:
                messagebox.showwarning("Warning", "No folder selected. Operation canceled.")
                return  # Esci dalla funzione se l'utente ha annullato la selezione

        # Mostra il messaggio di conferma prima di chiudere la finestra
        messagebox.showinfo("Answer", "FCclasses will be tested")
        root.destroy()

        # Esegui il comando `make test` nella cartella selezionata
        try:
            result = subprocess.run(["make", "test"], cwd=command_path, capture_output=True, text=True, check=True)
            print("Comando eseguito con successo!")
            print(result.stdout)  # Stampa l'output del comando

        except subprocess.CalledProcessError as e:
            print(f"Errore durante l'esecuzione: {e}")
            print(f"Output dell'errore: {e.stderr}")  # Mostra l'output dell'errore

        except Exception as e:
            print(f"Errore imprevisto: {e}")

    def on_no():
        messagebox.showinfo("Aswer", "FCclasse won't be tested")
        root.destroy()

    # Creazione della finestra principale
    root = tk.Tk()
    root.title("FCclasses test")

    # Ottieni dimensioni dello schermo
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calcola la posizione per centrare la finestra
    pos_x = (screen_width // 2)
    pos_y = (screen_height // 2)

    # Imposta la posizione senza specificare dimensioni
    root.geometry(f"+{pos_x}+{pos_y}")

    # Etichetta con la domanda
    label = tk.Label(root, text="Do you want to test FCclasses?", font=("Arial", 14))
    label.pack(pady=10)

    # Contenitore per i pulsanti
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Pulsanti Yes e No
    yes_button = tk.Button(button_frame, text="Yes", command=on_yes, width=10)
    yes_button.pack(side=tk.LEFT, padx=10)

    no_button = tk.Button(button_frame, text="No", command=on_no, width=10)
    no_button.pack(side=tk.RIGHT, padx=10)

    # Avvio della finestra
    root.mainloop()

def select_files():
    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale
    
    file_paths = {}
    
    while "state1" not in file_paths:
        file1 = filedialog.askopenfilename(title="Seleziona il file relativo allo stato 1", filetypes=[("Tutti i file", "*.*")])
        if file1:
            file_paths["state1"] = file1
        else:
            messagebox.showwarning("Attenzione", "Devi selezionare un file per lo stato 1.")
            return None  # Termina il codice se viene premuto "Annulla"
    
    while "state2" not in file_paths:
        file2 = filedialog.askopenfilename(title="Seleziona il file relativo allo stato 2", filetypes=[("Tutti i file", "*.*")])
        if file2:
            file_paths["state2"] = file2
        else:
            messagebox.showwarning("Attenzione", "Devi selezionare un file per lo stato 2.")
            return None  # Termina il codice se viene premuto "Annulla"
    return file_paths

def execute_gen_fcc_state(file_name):
    try:
        result = subprocess.run(["gen_fcc_state", "-i", file_name], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Errore nell'esecuzione del comando: {e.stderr}"
    
def execute_gen_fcc_dipfile(file_name):
    try:
        result = subprocess.run(["gen_fcc_dipfile", "-i", file_name], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Errore nell'esecuzione del comando: {e.stderr}"

def execute_fcclasses3_inpTemplate():
    try:
        result = subprocess.run(["fcclasses3", "-h"], capture_output=True, text=True, check=True)
        with open("fcc.inp", "w") as file:
            file.write(result.stdout)
    except FileNotFoundError:
        print("Errore: Il comando 'fcclasses3' non è stato trovato. Assicurati che sia installato e nel PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Errore nell'esecuzione del comando: {e}")
    
def replace_word_in_file(file_path, target_word, replacement):
    try:
        with open(file_path, "r") as file:
            content = file.read()
        
        content = content.replace(target_word, replacement)
        
        with open(file_path, "w") as file:
            file.write(content)
        print(f"Sostituzione completata: '{target_word}' -> '{replacement}' in {file_path}.")
    except FileNotFoundError:
        print(f"Errore: Il file '{file_path}' non è stato trovato.")
    except Exception as e:
        print(f"Errore durante la modifica del file: {e}")

def edit_inp_file(file_path):
    """Apre un file di testo dato un percorso e lo visualizza nella GUI con una combobox per la selezione delle parole."""
    nlines = []
    def save_file():
        """Salva il contenuto della text area nel file specificato e chiude la finestra."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))  # Salva il contenuto della text area
            root.title(f"Editor - {file_path} (Salvato)")
            root.quit()  # Assicura la chiusura completa del loop tkinter
            root.destroy()  # Chiude la finestra
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il salvataggio:\n{e}")
    
    def cancel_action():
        """Chiude la finestra senza salvare."""
        root.quit()
        root.destroy()
    
    def extract_first_words():
        """Estrae la prima parola di ogni riga che non inizia con ';' o '$'."""
        words = []
        lines = content.split("\n")
        for line in lines[:-4]:
            line = line.strip()
            if line and not line.startswith(";") and not line.startswith("$"):
                first_word = line.split()[0]
                words.append(first_word)
        return words
    
    def on_close():
        """Gestisce la chiusura della finestra premendo la 'X'."""
        root.quit()
        root.destroy()
    
    def insert_keyword():
        """Inserisce il comando dell'Entry accanto alla parola selezionata nella Combobox nella riga specifica."""
        
                
        selected = word_combobox1.get()  # Parola selezionata nella combobox
        selected2 = word_combobox2.get()  # Parola selezionata nella combobox
        command = entry.get().upper()  # Comando da inserire nell'entry
        command2 = entry2.get().upper()  # Comando da inserire nell'entry  
        nselected = int(num_combobox2.get()) # Numero selezionato nella combobox

        # Verifica che la parola selezionata non sia vuota
        if not selected and not selected2:
            messagebox.showerror("Errore", "Nessuna parola selezionata!")
            return
        
        # Verifica che l'Entry non sia vuoto
        if not command and not command2:
            messagebox.showerror("Errore", "Devi inserire un comando!")
            return

        # Caricamento del file
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            text_area.insert(tk.END, content)
            update_line_numbers()

        except FileNotFoundError:
            content = ""
            text_area.insert(tk.END, "Errore: File non trovato!")
        except Exception as e:
            content = ""
            text_area.insert(tk.END, f"Errore durante l'apertura del file:\n{e}")
        update_line_numbers()

        
        if command:
            # Aggiorna il contenuto solo se la riga inizia con la parola selezionata
            new_content = ""
            for line in content.split("\n"):
                line = line.strip()  # Rimuove gli spazi vuoti ai margini
                if line:
                    if line.startswith(selected):
                        # Aggiungi il comando alla linea che inizia con la parola selezionata
                        parole = line.split()
                        if len(parole) > 2:  # Assicurati che ci sia una terza parola
                            parole[2] = command  # Modifica la terza parola
                        new_frase = "    ".join(parole)  # Ricostruisce la riga
                        new_content += new_frase + "\n"  # Aggiungi la riga modificata                
                    else:
                        new_content += line + "\n"  # Aggiungi le righe non modificate
                else: continue
                    
            # Aggiorna il contenuto dell'area di testo con il nuovo contenuto
            text_area.replace("1.0",tk.END,new_content)

            update_file()
            entry.delete(0,tk.END)
            entry2.delete(0,tk.END)
            update_line_numbers()
        #"""
        if command2:
            # Aggiorna il contenuto solo se la riga inizia con la parola selezionata
            new_content = ""
            for i, line in enumerate(content.split("\n"),start=1):
                line = line.strip()  # Rimuove gli spazi vuoti ai margini
                if line:
                    if nselected == i:
                        new_frase = selected2 + " = " + command2
                        new_content += line + "\n" + new_frase + "\n"
                    else:
                        new_content += line + "\n"  # Aggiungi le righe non modificate
                else: continue
            # Aggiorna il contenuto dell'area di testo con il nuovo contenuto
            text_area.replace("1.0",tk.END,new_content)
            line_numbers            
            update_file()
            entry.delete(0,tk.END)
            entry2.delete(0,tk.END)
            update_line_numbers()
        #"""
    def update_file():
        """Salva il contenuto della text area nel file specificato e chiude la finestra."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_area.get("1.0", tk.END))  # Salva il contenuto della text area
            root.title(f"Editor - {file_path} (Salvato)")         
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il salvataggio:\n{e}")    

    def update_line_numbers(event=None):
        """Aggiorna i numeri di riga nella barra laterale escludendo le righe vuote."""
        line_numbers_text.config(state="normal")
        line_numbers_text.delete("1.0", tk.END)
        
        # Ottieni tutte le righe del testo
        lines = text_area.get("1.0", tk.END).split("\n")
        
        # Filtra solo le righe non vuote e numerale
        non_empty_lines = [i + 1 for i, line in enumerate(lines) if line.strip()]  
        
        # Genera la stringa con i numeri di riga
        line_numbers = "\n".join(map(str, non_empty_lines))
        
        # Inserisce i numeri di riga aggiornati
        line_numbers_text.insert(tk.END, line_numbers)
        line_numbers_text.config(state="disabled")  # Impedisce modifiche manuali
        return line_numbers
            
    # Creazione della GUI
    root = tk.Tk()
    root.title(f"Editor - {file_path}")
    root.protocol("WM_DELETE_WINDOW", on_close)  # Gestisce la chiusura della finestra

    # Ottieni dimensioni dello schermo
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calcola la posizione per centrare la finestra
    pos_x = (screen_width // 2)
    pos_y = (screen_height // 2)

    # Imposta la posizione senza specificare dimensioni
    root.geometry(f"+{pos_x}+{pos_y}")

    # Frame principale
    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Barra laterale per i numeri di riga
    line_numbers_text = scrolledtext.ScrolledText(frame, width=4, padx=5, state="disabled", wrap="none", bg="lightgrey", font=("Arial", 12))
    line_numbers_text.pack(side="left", fill="y")

    # Area di testo con scrollbar
    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Arial", 12))
    text_area.pack(side="left", expand=True, fill="both")

    # Associa l'evento per aggiornare i numeri di riga quando il testo cambia o viene scrollato
    text_area.bind("<KeyRelease>", update_line_numbers)
    text_area.bind("<MouseWheel>", update_line_numbers)
    text_area.bind("<ButtonRelease>", update_line_numbers)

    # Pannello laterale destro
    side_panel2 = tk.Frame(frame)
    side_panel2.pack(side="right", fill="y", padx=10)

    # Pannello laterale destro
    side_panel1 = tk.Frame(frame)
    side_panel1.pack(side="right", fill="y", padx=10)

    
    # Caricamento del file
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            
            content = file.read()
        text_area.insert(tk.END, content)
        line_numbers = update_line_numbers()
    except FileNotFoundError:
        content = ""
        text_area.insert(tk.END, "Errore: File non trovato!")
    except Exception as e:
        content = ""
        text_area.insert(tk.END, f"Errore durante l'apertura del file:\n{e}")
    line_numbers = update_line_numbers()

    # Estrazione delle prime parole
    first_words = extract_first_words()
    
    # label combobox
    label = tk.Label(side_panel1, text="Select K-word in text")
    label.pack()
    # label combobox

    label = tk.Label(side_panel2, text="Select K-word NOT in text")
    label.pack()
    
    # Combobox per selezione parole
    selected_word = tk.StringVar()
    word_combobox1 = ttk.Combobox(side_panel1, textvariable=selected_word, values=first_words, state="readonly")
    word_combobox1.set(first_words[0] if first_words else "")  # Setta il primo valore se ci sono parole
    word_combobox1.pack(pady=5) 

    # Combobox per selezione parole
    word_combobox2 = ttk.Combobox(side_panel2, values=DEFAULT_KEYWORDS, state="readonly")
    word_combobox2.set(DEFAULT_KEYWORDS[0])  # Setta il primo valore se ci sono parole
    word_combobox2.pack(pady=5)

    # Label per selezione righe
    label = tk.Label(side_panel2, text="Select line number to insert after")
    label.pack(pady=5)

    # Combobox per selezione parole
    num_combobox2 = ttk.Combobox(side_panel2, values=line_numbers, state="readonly")
    num_combobox2.set(line_numbers[0])  # Setta il primo valore se ci sono parole
    num_combobox2.pack(pady=5)

    # Label per inserimento testo
    label = tk.Label(side_panel1, text="Insert mode for selected keywords")
    label.pack(pady=5)
    
    label = tk.Label(side_panel2, text="Insert mode for selected keywords")
    label.pack(pady=5)

    # finestra di inserimento testo
    entry = tk.Entry(side_panel1)
    entry.pack(pady=10)

    # finestra di inserimento testo
    entry2 = tk.Entry(side_panel2)
    entry2.pack(pady=10)

    # Pulsante Salva
    save_button = tk.Button(side_panel2, text="Save", command=save_file)
    save_button.pack(side="bottom", pady=10, padx=10)
    
    # Pulsante Annulla
    cancel_button = tk.Button(side_panel1, text="Cancel", command=cancel_action)
    cancel_button.pack(side="bottom", pady=10, padx=10)

    # Pulsante inserisci comando
    insert = tk.Button(side_panel2, text="Confirm keywords", command=insert_keyword)
    insert.pack(side="bottom", padx=10, pady=5)

    root.mainloop()  # Avvia la GUI quando richiesto

def run_fcclasses(file_path):
    
    try:
        process = subprocess.Popen(["fcclasses3", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return f"Errore nell'esecuzione del comando: {stderr}"
        return stdout
    except Exception as e:
        return f"Errore imprevisto: {str(e)}"

def main():
    file1_path = []
    file1_name = []
    file1_name_ext = []
    file2_path = []
    file2_name = []
    file2_name_ext = []

    FCclasses_install()
    FCclasses_test()
    selected_files = select_files()

    if selected_files:
       print(selected_files)
    else: return

    file1_path = selected_files["state1"]
    file2_path = selected_files["state2"]
    file1_name_ext = os.path.basename(file1_path)
    file2_name_ext = os.path.basename(file2_path)
    file1_name = os.path.splitext(file1_name_ext)[0]
    file2_name = os.path.splitext(file2_name_ext)[0]
    
    execute_gen_fcc_state(file1_name_ext)
    execute_gen_fcc_state(file2_name_ext)
    execute_gen_fcc_dipfile(file2_name_ext)
    execute_fcclasses3_inpTemplate()
    file_INP = "fcc.inp"
    file_INP_path = os.path.join(os.getcwd(), file_INP)
    replace_word_in_file(file_INP_path, "state1", file1_name)
    replace_word_in_file(file_INP_path, "state2", file2_name)
    replace_word_in_file(file_INP_path, "eldip", ("eldip_" + file2_name + "_fchk"))

    # Ora chiama edit_inp_file quando vuoi aprire l'editor
    edit_inp_file(file_INP_path)
    run_fcclasses(file_INP)
    return

if __name__ == "__main__":
    main()
