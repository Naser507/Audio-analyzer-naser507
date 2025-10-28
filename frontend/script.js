document.getElementById("uploadForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const fileInput = document.getElementById("audioFile");
    if (!fileInput.files.length) {
        alert("Please select an audio file.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("audio_file", file);

    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "Analyzing...";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            resultsDiv.innerHTML = `Error: ${err.message}`;
            return;
        }

        const data = await response.json();

        resultsDiv.innerHTML = `
            <p><strong>Filename:</strong> ${data.filename}</p>
            <p><strong>Pitch:</strong> ${data.pitch.toFixed(2)}</p>
            <p><strong>Harmonics:</strong> ${data.harmonics.toFixed(2)}</p>
            <p><strong>Noise:</strong> ${data.noise.toFixed(2)}</p>
            <p><strong>Spectrogram:</strong></p>
            <img src="${data.spectrogram}" alt="Spectrogram" style="max-width: 500px; display:block; margin-bottom: 10px;">
            <button id="downloadReport">Download JSON Report</button>
            <button id="downloadSpectrogram">Download Spectrogram</button>
        `;

        // Download JSON report
        document.getElementById("downloadReport").onclick = () => {
            window.location.href = `/report/${data.serial}_${data.filename}_report.json`;
        };

        // Download spectrogram
        document.getElementById("downloadSpectrogram").onclick = () => {
            window.location.href = `/spectrogram/download/${data.serial}_${data.filename}_spectrogram.png`;
        };

    } catch (error) {
        resultsDiv.innerHTML = "An unexpected error occurred: " + error;
        console.error(error);
    }
});
