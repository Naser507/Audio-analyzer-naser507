from flask import Flask, request, jsonify, send_from_directory, send_file
import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import glob
import re
import traceback
import time
import json

# === Helper functions ===
def get_next_serial(tmp_dir):
    files = glob.glob(os.path.join(tmp_dir, "*"))
    serials = []
    for f in files:
        m = re.search(r"^(\d+)_", os.path.basename(f))
        if m:
            serials.append(int(m.group(1)))
    return max(serials, default=0) + 1

def cleanup_tmp(tmp_dir):
    """Delete files older than 5 minutes, but skip files being downloaded."""
    now = time.time()
    for f in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, f)

        # Skip lock files themselves
        if f.endswith(".lock"):
            continue

        # Skip files currently being downloaded
        lock_file = file_path + ".lock"
        if os.path.exists(lock_file):
            continue

        if os.path.isfile(file_path):
            if now - os.path.getctime(file_path) > 300:  # 5 minutes
                os.remove(file_path)

# === Setup paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")
TMP_DIR = "/dev/shm/audio-analyzer"
os.makedirs(TMP_DIR, exist_ok=True)

# Initialize Flask app
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

# === Serve frontend ===
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

# === Analyze audio ===
@app.route("/analyze", methods=["POST"])
def analyze_audio():
    try:
        if "audio_file" not in request.files:
            return jsonify({"status": "error", "message": "No audio file provided"}), 400

        audio_file = request.files["audio_file"]
        original_filename = audio_file.filename

        # Cleanup old files older than 5 minutes
        cleanup_tmp(TMP_DIR)

        # Get next serial number and build filenames
        serial = get_next_serial(TMP_DIR)
        base_filename = f"{serial}_{original_filename}"
        file_path = os.path.join(TMP_DIR, base_filename)
        audio_file.save(file_path)

        # Load audio and do analysis
        y, sr = librosa.load(file_path, sr=None)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = [pitches[magnitudes[:, i].argmax(), i] for i in range(magnitudes.shape[1])]
        pitch_values = [p for p in pitch_values if p > 0]

        harmonics = float(np.mean(pitch_values)) if pitch_values else 0
        noise = float(np.sqrt(np.mean(y**2)))

        # Generate spectrogram
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        plt.figure(figsize=(8, 4))
        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')

        spectrogram_filename = f"{serial}_{original_filename}_spectrogram.png"
        spectrogram_path = os.path.join(TMP_DIR, spectrogram_filename)
        plt.savefig(spectrogram_path)
        plt.close()

        # Build JSON response
        response = {
            "status": "success",
            "pitch": float(np.mean(pitch_values)) if pitch_values else 0,
            "harmonics": harmonics,
            "noise": noise,
            "spectrogram": f"/spectrogram/{spectrogram_filename}",
            "serial": serial,
            "filename": original_filename
        }

        # Save JSON report to TMP_DIR
        json_filename = f"{serial}_{original_filename}_report.json"
        json_path = os.path.join(TMP_DIR, json_filename)
        with open(json_path, "w") as f:
            json.dump(response, f)

        return jsonify(response)

    except Exception as e:
        print("Error inside /analyze:", e)
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# === Serve generated spectrograms ===
@app.route("/spectrogram/<path:filename>")
def serve_spectrogram(filename):
    file_path = os.path.join(TMP_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype="image/png")
    else:
        return jsonify({"status": "error", "message": "Spectrogram not found"}), 404

# === Download JSON report ===
@app.route("/report/<path:filename>")
def serve_report(filename):
    file_path = os.path.join(TMP_DIR, filename)
    lock_file = file_path + ".lock"
    if os.path.exists(file_path):
        open(lock_file, "w").close()  # create lock
        try:
            return send_file(file_path, mimetype="application/json", as_attachment=True)
        finally:
            os.remove(lock_file)  # remove lock after download
    else:
        return jsonify({"status": "error", "message": "Report not found"}), 404

# === Download spectrogram ===
@app.route("/spectrogram/download/<path:filename>")
def download_spectrogram(filename):
    file_path = os.path.join(TMP_DIR, filename)
    lock_file = file_path + ".lock"
    if os.path.exists(file_path):
        open(lock_file, "w").close()  # create lock
        try:
            return send_file(file_path, mimetype="image/png", as_attachment=True)
        finally:
            os.remove(lock_file)  # remove lock after download
    else:
        return jsonify({"status": "error", "message": "Spectrogram not found"}), 404

# === Run app ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
