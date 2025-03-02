#!/bin/bash

# Belépés a virtuális környezetbe
cd backend
source venv/bin/activate

# Flask alkalmazás indítása
flask run --port=5001 --debug > /dev/null 2>&1 &
echo "Flask alkalmazás elindítva a háttérben, port: 5001, debug módban."

# Kilépés a virtuális környezetből
deactivate

cd ..

# Belépés a tw-2025-1 mappába és npm run dev indítása
cd frontend
npm run dev > /dev/null 2>&1 &
echo "npm run dev elindítva a háttérben."

# read -n 1 -s
