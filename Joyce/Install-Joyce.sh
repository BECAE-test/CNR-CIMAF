#!/bin/bash

folder=$(zenity --file-selection --directory --title="Seleziona una cartella")

if [ -n "$folder" ]; then
    echo "Cartella selezionata: $folder"
else
    echo "Nessuna cartella selezionata."
    exit 1
fi

# Aggiorna JOYCE in ~/.bashrc senza duplicati
if grep -q "^export JOYCE=" ~/.bashrc; then
    sed -i "s|^export JOYCE=.*|export JOYCE=\"$folder\"|" ~/.bashrc
else
    echo "export JOYCE=\"$folder\"" >> ~/.bashrc
fi

# Imposta JOYCE direttamente per questo script
export JOYCE="$folder"

# Controlla se il file esiste prima di copiare
if [ -f "$JOYCE/bin/go.joyce" ]; then
    sudo cp "$JOYCE/bin/go.joyce" /bin/
else
    echo "Errore: il file $JOYCE/bin/go.joyce non esiste!"
    exit 1
fi

# Verifica se go.joyce è disponibile prima di eseguirlo
if command -v go.joyce &>/dev/null; then
    go.joyce -gfortran
else
    echo "Errore: go.joyce non è stato trovato in /bin/!"
    exit 1
fi
