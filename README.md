# Audio Analyzer Webapp

A Flask-based web application to analyze audio files and generate detailed reports including pitch, harmonics, noise levels, and spectrogram images. The app is fully Dockerized for easy deployment and temporary in-memory storage.

---

## Features

- Upload WAV audio files through a simple web interface.
- Compute:
  - **Pitch**
  - **Harmonics**
  - **Noise levels**
- Generate **spectrogram images**.
- Generate **downloadable JSON reports** for each audio file.
- Temporary storage in RAM (`/dev/shm/audio-analyzer`) for fast processing.
- Automatic cleanup of files older than 5 minutes.
- Downloadable results, with lock mechanism to prevent deletion mid-download.

---

## Project Structure

audio-analyzer/
├── backend/
│ ├── app.py
│ └── requirements.txt
├── frontend/
│ ├── index.html
│ ├── script.js
│ └── style.css
├── Dockerfile
├── .dockerignore
└── README.md

yaml
Copy code

---

## Requirements

- Python 3.10+
- Flask
- librosa
- matplotlib
- numpy
- Docker (for containerized deployment)

Install dependencies:

```bash
pip install -r backend/requirements.txt
Usage
Run without Docker
bash
Copy code
cd backend
python app.py
Open your browser at http://localhost:5000.

Run with Docker
bash
Copy code
# Build the Docker image
docker build -t audio-analyzer .

# Run the container
docker run -d -p 5000:5000 audio-analyzer
Open your browser at http://localhost:5000 (or use the VM/host IP if running in a virtual machine).

Uploading & Downloading
Upload a WAV audio file using the web interface.

Wait for analysis to complete. JSON report and spectrogram image will be generated.

Click Download Report button to download the JSON report.

Click Download Spectrogram button to download the spectrogram image.

Note: The files are stored temporarily in RAM and are automatically deleted after 5 minutes if not downloaded. Downloads prevent the deletion during the process.

Docker Notes
The app uses /dev/shm/audio-analyzer for temporary RAM storage.

Ensure the container has sufficient memory for larger audio files.

Port 5000 is mapped to host; adjust if required.

License
MIT License

yaml
Copy code

---

### Git Commands to Push

```bash
# Stage the README changes
git add README.md

# Commit with message
git commit -m "Add complete README with features, usage, and Docker instructions"

# Push to GitHub
git push origin main
If you want, I can also write the final commands to commit everything together — app.py, frontend changes, Dockerfile, and README — in one single commit and push, so you don’t have to do it step by step.
