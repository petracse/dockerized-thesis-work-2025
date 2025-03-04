#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

start_flask() {
    if command -v gnome-terminal &> /dev/null
    then
        gnome-terminal --title="Flask Backend" -- bash -c "cd $SCRIPT_DIR/backend && source venv/bin/activate && flask run --port=5001 --debug; exec bash" &
    else
        cmd.exe /c start wsl.exe -e bash -c "cd $SCRIPT_DIR/backend && source venv/bin/activate && flask run --port=5001 --debug" &
    fi
}

start_vue() {
    cd $SCRIPT_DIR/frontend
    npm run dev
}

start_flask
start_vue

