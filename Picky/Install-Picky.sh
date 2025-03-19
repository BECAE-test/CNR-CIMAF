#!/bin/bash

folder=$(zenity --file-selection --directory --title="Seleziona una cartella")

if [ -n "$folder" ]; then
    echo "Cartella selezionata: $folder"
else
    echo "Nessuna cartella selezionata."
    exit 1
fi

# Definisci il file di configurazione
BASHRC_FILE=~/.bashrc

# Aggiorna PICKY in ~/.bashrc senza duplicati
if grep -q "^export PICKY=" "$BASHRC_FILE"; then
    sed -i.bak "s|^export PICKY=.*|export PICKY=\"$folder\"|" "$BASHRC_FILE"
else
    echo "export PICKY=\"$folder\"" >> "$BASHRC_FILE"
fi

# Ricarica ~/.bashrc per applicare subito la modifica
source "$BASHRC_FILE"

# Imposta PICKY per questa sessione
export PICKY="$folder"

# Ricarica ~/.bashrc per applicare subito la modifica
source "$BASHRC_FILE"

# Controlla se la directory e' prima di copiare
if ls "$PICKY/Bin/"* >/dev/null 2>&1; then
    sudo cp "$PICKY/Bin/"* /bin/
else
    echo "Errore: la directory $PICKY/bin/ è vuota o non esiste!"
    exit 1
fi

# Verifica se go.picky è disponibile prima di eseguirlo
if command -v go.picky &>/dev/null; then
    go.picky -f
else
    echo "Errore: go.picky non è stato trovato in /bin/!"
    exit 1
fi
