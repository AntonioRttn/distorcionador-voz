from flask import Flask, request, send_file
import wave
import numpy as np
from scipy.signal import resample

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['file']
        speed = float(request.form['speed'])
        pitch = int(request.form['pitch'])

        # Guardar archivo temporal
        filepath = 'input_audio.wav'
        file.save(filepath)

        # Leer archivo de audio
        with wave.open(filepath, 'rb') as wav:
            params = wav.getparams()
            frames = wav.readframes(params.nframes)
            samples = np.frombuffer(frames, dtype=np.int16)

        # Cambiar velocidad (resampleo)
        new_length = int(len(samples) / speed)
        samples = resample(samples, new_length).astype(np.int16)

        # Cambiar tono (ajustar frecuencia)
        pitch_factor = 2 ** (pitch / 12)  # Convertir semitonos a factor de frecuencia
        new_length = int(len(samples) / pitch_factor)
        samples = resample(samples, new_length).astype(np.int16)

        # Guardar el archivo de salida
        output_path = 'output_audio.wav'
        with wave.open(output_path, 'wb') as wav_out:
            wav_out.setparams(params)
            wav_out.setnframes(len(samples))
            wav_out.writeframes(samples.tobytes())

        return send_file(output_path, as_attachment=True)

    return '''
        <!doctype html>
        <title>Transformador de Voz</title>
        <h1>Sube un archivo de audio (.wav)</h1>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <label for="speed">Velocidad (ej. 1.0 para normal, 0.5 para lento, 2.0 para rápido):</label>
            <input type="text" name="speed" value="1.0" required>
            <label for="pitch">Tono (ej. +4 para agudo, -4 para grave):</label>
            <input type="text" name="pitch" value="0" required>
            <button type="submit">Procesar</button>
        </form>
    '''

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
