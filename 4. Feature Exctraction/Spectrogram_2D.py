import numpy as np
import librosa
import librosa.display
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import glob

# Define the folder containing NPZ files.
npz_folder = r"C:\Users\Louis\MSc-Thesis-Louis\3. Data Preparation\Extracted Data"

# Get a list of all NPZ files in the folder.
npz_files = glob.glob(os.path.join(npz_folder, '*.npz'))
if not npz_files:
    print("No NPZ files found in the folder.")
    exit()

# Select the most recent NPZ file based on modification time.
most_recent_npz = max(npz_files, key=os.path.getmtime)
print(f"Most recent NPZ file found: {most_recent_npz}")

# Specify a manual NPZ file if desired; leave as None to use the most recent NPZ file.
manual_npz = None  # e.g., r'C:\path\to\your\file.npz'

# Use manual_npz if provided; otherwise, use the most recent NPZ file.
file_to_use = manual_npz if manual_npz is not None else most_recent_npz
print(f"Using NPZ file: {file_to_use}")

fs = 25  # Sampling frequency (Hz)
keys = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']


def plot_six_spectrograms(npz_file_path):
    data = np.load(npz_file_path)

    # Create a 2x3 subplot figure.
    fig = make_subplots(rows=2, cols=3,
                        subplot_titles=keys,
                        horizontal_spacing=0.08, vertical_spacing=0.1)

    # Parameters for mel spectrogram.
    n_fft = 2048
    hop_length = 512
    n_mels = 128

    row, col = 1, 1
    for i, key in enumerate(keys):
        signal = data[key]

        # Compute mel spectrogram using librosa.
        S = librosa.feature.melspectrogram(y=signal, sr=fs,
                                           n_fft=n_fft,
                                           hop_length=hop_length,
                                           n_mels=n_mels)
        S_db = librosa.power_to_db(S, ref=np.max)

        # Generate time vector for the spectrogram frames.
        t_spec = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=fs, hop_length=hop_length)
        # Get the mel frequency bins.
        mel_f = librosa.mel_frequencies(n_mels=S_db.shape[0], fmin=0, fmax=fs / 2)

        # Set color scale limits based on percentiles.
        vmin = np.percentile(S_db, 5)
        vmax = np.percentile(S_db, 95)

        heatmap = go.Heatmap(
            z=S_db,
            x=t_spec,
            y=mel_f,
            colorscale='Jet',
            zmin=vmin,
            zmax=vmax,
            colorbar=dict(title='Intensity [dB]'),
            showscale=True if i == 0 else False
        )
        fig.add_trace(heatmap, row=row, col=col)

        if col < 3:
            col += 1
        else:
            col = 1
            row += 1

    fig.update_layout(
        title="Mel Spectrograms for all 6 Sensor Channels (Plotly)",
        height=800,
        width=1200
    )
    fig.show()


def plot_six_ffts(npz_file_path):
    data = np.load(npz_file_path)

    # Create a 2x3 subplot figure for FFT plots.
    fig = make_subplots(rows=2, cols=3,
                        subplot_titles=keys,
                        horizontal_spacing=0.08, vertical_spacing=0.1)

    row, col = 1, 1
    for key in keys:
        signal = data[key]
        N = len(signal)
        fft_result = np.fft.fft(signal)
        freq = np.fft.fftfreq(N, d=1 / fs)

        # Only keep positive frequencies.
        pos_mask = freq >= 0
        freq = freq[pos_mask]
        fft_magnitude = np.abs(fft_result)[pos_mask]

        trace = go.Scatter(
            x=freq,
            y=fft_magnitude,
            mode='lines',
            name=key
        )
        fig.add_trace(trace, row=row, col=col)
        fig.update_xaxes(title_text="Frequency (Hz)", row=row, col=col)
        fig.update_yaxes(title_text="Magnitude", row=row, col=col)

        if col < 3:
            col += 1
        else:
            col = 1
            row += 1

    fig.update_layout(
        title="FFT (Magnitude Spectrum) for all 6 Sensor Channels (Plotly)",
        height=800,
        width=1200
    )
    fig.show()


def plot_six_time_domain(npz_file_path):
    data = np.load(npz_file_path)

    # Create a 2x3 subplot figure for time domain plots.
    fig = make_subplots(rows=2, cols=3,
                        subplot_titles=keys,
                        horizontal_spacing=0.08, vertical_spacing=0.1)

    row, col = 1, 1
    for key in keys:
        signal = data[key]
        N = len(signal)
        time_vector = np.arange(N) / fs

        trace = go.Scatter(
            x=time_vector,
            y=signal,
            mode='lines',
            name=key
        )
        fig.add_trace(trace, row=row, col=col)
        fig.update_xaxes(title_text="Time (sec)", row=row, col=col)
        fig.update_yaxes(title_text="Amplitude", row=row, col=col)

        if col < 3:
            col += 1
        else:
            col = 1
            row += 1

    fig.update_layout(
        title="Time Domain Signals for all 6 Sensor Channels (Plotly)",
        height=800,
        width=1200
    )
    fig.show()


# Generate the interactive plots using the selected NPZ file.
plot_six_spectrograms(file_to_use)
plot_six_ffts(file_to_use)
plot_six_time_domain(file_to_use)
