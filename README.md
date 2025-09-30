# Chord Analyzer Web App

A minimal web application that lets users upload music files and automatically analyzes the chord progression using a Hidden Markov Model (HMM) over chromagram features. It also supports YouTube links: paste a URL, the app extracts the audio, and runs the same analysis pipeline.

### What it does

- Upload an audio file (e.g., WAV/MP3) or paste a YouTube link.
- The backend computes a chromagram and infers the most likely chord sequence with an HMM (Viterbi decoding).
- The frontend displays time-aligned chord labels and basic metadata.


### Tech stack

- Frontend: Vue.js single-page interface for uploads, progress, and result visualization.
- Backend: Flask API for file handling, YouTube audio extraction, feature computation, and HMM inference.


### Typical flow

1. Provide an audio file or YouTube link.
2. The server extracts features (chromagram), then runs HMM decoding to estimate chords.
3. Results are returned as time-stamped chord labels and estimated BPM, ready to render in the UI.

# Instructions

## Setup

```bash
docker build -t chord-recognizer-ep .
```


## Running the Application

```bash
docker run -p 80:80 chord-recognizer-ep
```

## Stopping the Application

```bash
Ctrl + C
```
