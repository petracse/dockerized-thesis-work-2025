#!/bin/bash

# npm run dev leállítása (feltételezve, hogy az 5173-as porton fut)
if lsof -ti:5173 > /dev/null; then
    kill $(lsof -ti:5173)
    echo "npm run dev leállítva (5173-as port)."
else
    echo "npm run dev nem fut az 5173-as porton."
fi

# Belépés a virtuális környezetbe
cd backend
source venv/bin/activate

# Flask alkalmazás leállítása
if lsof -ti:5001 > /dev/null; then
    kill $(lsof -ti:5001)
    echo "Flask alkalmazás leállítva (5001-es port)."
else
    echo "Flask alkalmazás nem fut az 5001-es porton."
fi

# Kilépés a virtuális környezetből
deactivate

# read -n 1 -s
