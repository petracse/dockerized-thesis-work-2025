# Instructions

## Backend Setup

### Activate Virtual Environment
First, navigate to the backend directory and activate the virtual environment:

```bash
cd backend
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

### Install Requirements
Install the dependencies listed in `requirements.txt` within the activated virtual environment:
```bash
pip install -r requirements.txt
deactivate
```

## Frontend Setup

### Install Node Dependencies
Navigate to the frontend directory and install the necessary packages:
```bash
cd frontend npm install
```

## Running the Application

### Start Flask and Vue.js
Use the provided script to start both the Flask backend and the Vue.js frontend:
```bash
./start_flask_and_npm.sh
```

## Stopping the Application

### Stop Flask and Vue.js
Use the provided script to stop both services:
```bash
./stop_flask_and_npm.sh
```


