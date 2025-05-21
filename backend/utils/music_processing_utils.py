import numpy as np
import librosa
import soundfile as sf
import os
import librosa
from madmom.audio.chroma import DeepChromaProcessor
from hmmlearn import hmm
import tempfile
import shutil
import yt_dlp

def normalize_feature_sequence(X, norm='2', threshold=0.0001, v=None):
    return []

def compute_chromagram_from_filename(fn_wav, Fs=22050, N=4096, H=2048, gamma=None, version='STFT', norm='2'):
    return [], [], [], [], []

def load_hmm_parameters(folder):
    means = np.load(os.path.join(folder, 'means.npy'))
    covariances = np.load(os.path.join(folder, 'covariances.npy'))
    transmat = np.load(os.path.join(folder, 'transmat.npy'))
    startprob = np.load(os.path.join(folder, 'startprob.npy'))
    with open(os.path.join(folder, 'chord_list.txt'), 'r', encoding='utf-8') as f:
        idx_to_chord = {}
        for line in f:
            idx, chord = line.strip().split('\t')
            idx_to_chord[int(idx)] = chord
    return means, covariances, transmat, startprob, idx_to_chord

def build_hmm(means, covariances, transmat, startprob):
    n_components = means.shape[0]
    model = hmm.GaussianHMM(
        n_components=n_components,
        covariance_type="full",
        init_params="",
        params=""
    )
    model.means_ = means
    model.covars_ = covariances
    model.transmat_ = transmat
    model.startprob_ = startprob
    return model

def preemphasis(y, coef=0.97):
    return np.append(y[0], y[1:] - coef * y[:-1])

def process_music_file_for_chords_deepchroma(hmm_folder, yt_url, is_youtube, song_path, expected_sr=44100):
    import logging
    logger = logging.getLogger("process_music_file_for_chords_deepchroma")
    logger.info(f"Függvényhívás: is_youtube={is_youtube}, yt_url={yt_url}, song_path={song_path}")

    cleanup_temp = False
    temp_dir = None

    try:
        if is_youtube:
            logger.info("YouTube letöltés indul...")
            import yt_dlp
            temp_dir = tempfile.mkdtemp()
            audio_path = os.path.join(temp_dir, 'audio')
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': audio_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'noplaylist': True,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt_url])
                logger.info(f"Letöltés sikeres, fájl: {audio_path}.wav")
            except Exception as e:
                logger.error(f"YT letöltési hiba: {e}", exc_info=True)
                raise

            # Mindig 44100 Hz-en olvassuk be
            try:
                y, sr = librosa.load(audio_path + ".wav", sr=expected_sr, mono=True)
                logger.info(f"Librosa load sikeres, shape={y.shape}, sr={sr}")
            except Exception as e:
                logger.error(f"Librosa load hiba: {e}", exc_info=True)
                raise
            cleanup_temp = True
        else:
            logger.info(f"Fájl beolvasás: {song_path}")
            y, sr = sf.read(song_path, dtype='float32')
            logger.info(f"Soundfile read: shape={y.shape}, sr={sr}")
            if y.ndim > 1:
                y = y.mean(axis=1)
                logger.info("Sztereó -> mono konvertálva")
            if sr != expected_sr:
                y = librosa.resample(y, orig_sr=sr, target_sr=expected_sr)
                sr = expected_sr
                logger.info(f"Resample: új sr={sr}")

        tuning = librosa.estimate_tuning(y=y, sr=sr)
        logger.info(f"Hangolás eltérés: {tuning:.4f} félhang")
        if abs(tuning) >= 0.10:
            y = librosa.effects.pitch_shift(y, sr=sr, n_steps=-tuning)
            logger.info("Pitch shift alkalmazva")

        chroma_hop_length = sr // 10
        dcp = DeepChromaProcessor()
        chroma_orig = dcp(y)
        logger.info(f"DeepChroma process kész, shape={chroma_orig.shape}")

        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        logger.info(f"Tempo: {tempo}, beat_frames: {len(beat_frames)}")

        beat_frame_indices = librosa.time_to_frames(
            beat_times,
            sr=sr,
            hop_length=chroma_hop_length
        )

        beat_chroma = []
        for i in range(len(beat_frame_indices) - 1):
            start = beat_frame_indices[i]
            end = beat_frame_indices[i+1]
            if end > start:
                frames = chroma_orig[start:end]
                if frames.shape[0] == 0:
                    avg = np.zeros(chroma_orig.shape[1])
                else:
                    avg = np.mean(frames, axis=0)
                norm = avg / (np.sum(avg) + 1e-8)
                lognorm = np.log1p(norm)
                beat_chroma.append(lognorm)
            else:
                avg = chroma_orig[start]
                norm = avg / (np.sum(avg) + 1e-8)
                lognorm = np.log1p(norm)
                beat_chroma.append(lognorm)
        beat_chroma = np.array(beat_chroma)

        means, covariances, transmat, startprob, idx_to_chord = load_hmm_parameters(hmm_folder)
        logger.info("HMM paraméterek betöltve")
        model = build_hmm(means, covariances, transmat, startprob)

        logprob, state_sequence = model.decode(beat_chroma)
        predicted_chords = [idx_to_chord[s] for s in state_sequence]
        logger.info(f"Akkord predikció kész, {len(predicted_chords)} akkord")

        chords_by_time = {float(f"{t:.3f}"): chord for t, chord in zip(beat_times[:-1], predicted_chords)}
        chords_by_time = merge_consecutive_chords(chords_by_time)
        chords_by_time = simplify_chords_dict(chords_by_time)
        bpm = estimate_bpm_fourier(beat_times)

        return chords_by_time, bpm

    except Exception as e:
        logger.error(f"Hiba a(z) {song_path if not is_youtube else yt_url} feldolgozásakor: {str(e)}", exc_info=True)
        return {}, None

    finally:
        if cleanup_temp and temp_dir:
            logger.info(f"Ideiglenes könyvtár törlése: {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)

def process_music_file_for_chords_cqt(hmm_folder, yt_url, is_youtube, song_path, expected_sr=44100):
    """
    Akkordfelismerés CQT + HMM alapján, opcionális YouTube letöltéssel.

    song_path: helyi fájl elérési útja (ha nem YouTube)
    hmm_folder: HMM paraméterek mappája
    yt_url: YouTube URL (ha is_youtube True)
    is_youtube: bool, letöltsön-e YouTube-ról
    expected_sr: elvárt mintavételezési frekvencia (default: 44100)
    """

    cleanup_temp = False
    temp_dir = None

    try:
        # 1. Audió beolvasás (YouTube vagy helyi fájl)
        if is_youtube:
            import yt_dlp
            temp_dir = tempfile.mkdtemp()
            audio_path = os.path.join(temp_dir, 'audio')
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': audio_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])
            y, sr = librosa.load(audio_path + ".wav", sr=expected_sr, mono=True)
            cleanup_temp = True
        else:
            y, sr = sf.read(song_path, dtype='float32')
            if y.ndim > 1:
                y = y.mean(axis=1)
            if sr != expected_sr:
                y = librosa.resample(y, orig_sr=sr, target_sr=expected_sr)
                sr = expected_sr

        # 2. Preemphasis
        y = preemphasis(y)

        # 3. Hangolás becslése
        tuning = librosa.estimate_tuning(y=y, sr=sr)

        # 4. CQT-kromagramma számítása
        chroma_hop_length = sr // 10  # 10 Hz frame rate
        chroma_orig = librosa.feature.chroma_cqt(
            y=y,
            sr=sr,
            hop_length=chroma_hop_length,
            n_chroma=12,
            tuning=tuning
        ).T  # shape: (n_frames, 12)

        # 5. Beat tracking
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        beat_frame_indices = librosa.time_to_frames(
            beat_times,
            sr=sr,
            hop_length=chroma_hop_length
        )

        # 6. Beat-enkénti súlyozott kromagramma
        beat_chroma = []
        for i in range(len(beat_frame_indices) - 1):
            start = beat_frame_indices[i]
            end = beat_frame_indices[i + 1]

            if start >= chroma_orig.shape[0]:
                continue
            end = min(end, chroma_orig.shape[0])

            if end > start:
                frames = chroma_orig[start:end]
                energies = np.sum(frames, axis=1)
                total_energy = np.sum(energies) + 1e-8
                weights = energies / total_energy
                weighted_avg = np.average(frames, axis=0, weights=weights)
            else:
                weighted_avg = chroma_orig[start]

            # Zajküszöbölés utólag
            thresholded = np.where(weighted_avg < 0.01, 0.0, weighted_avg)
            beat_chroma.append(thresholded)

        beat_chroma = np.array(beat_chroma)

        # 7. HMM betöltése
        means, covariances, transmat, startprob, idx_to_chord = load_hmm_parameters(hmm_folder)
        model = build_hmm(means, covariances, transmat, startprob)

        # 8. Predikció
        logprob, state_sequence = model.decode(beat_chroma)
        predicted_chords = [idx_to_chord[s] for s in state_sequence]

        # 9. Időpont - akkord párok
        chords_by_time = {float(f"{t:.3f}"): chord for t, chord in zip(beat_times[:-1], predicted_chords)}
        chords_by_time = merge_consecutive_chords(chords_by_time)
        chords_by_time = simplify_chords_dict(chords_by_time)
        bpm = estimate_bpm_fourier(beat_times)

        return chords_by_time, bpm

    except Exception as e:
        print(f"Hiba a(z) {song_path if not is_youtube else yt_url} feldolgozásakor: {str(e)}")
        return {}, None

    finally:
        if cleanup_temp and temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)



def merge_consecutive_chords(chords_by_time):
    merged_chords = {}
    previous_chord = None
    for time, chord in sorted(chords_by_time.items()):
        if chord != previous_chord:
            merged_chords[time] = chord
            previous_chord = chord
    return merged_chords

def estimate_bpm_fourier(beat_times, dt=0.05):
    if len(beat_times) < 2:
        return 0.0

    # Időtartomány
    t_start = beat_times[0]
    t_end = beat_times[-1]
    duration = t_end - t_start
    if duration <= 0:
        return 0.0

    # Időrács
    t = np.arange(t_start, t_end, dt)
    impulse = np.zeros_like(t)
    beat_indices = np.searchsorted(t, beat_times)
    # Vigyázat: lehet, hogy néhány index kilóg, ezért csak a tartományon belülieket állítjuk 1-re
    beat_indices = beat_indices[beat_indices < len(impulse)]
    impulse[beat_indices] = 1

    # DC komponens eltávolítása
    impulse = impulse - np.mean(impulse)

    # FFT
    spectrum = np.abs(np.fft.rfft(impulse))
    freqs = np.fft.rfftfreq(len(impulse), d=dt)

    # DC komponens kihagyása
    peak_idx = np.argmax(spectrum[1:]) + 1
    peak_freq = freqs[peak_idx]
    bpm = peak_freq * 60

    return bpm

def simplify_chord_name(chord):
    """
    Egyszerűsíti az akkord nevét:
    - 'A#:maj' -> 'A#'
    - 'A#:min' -> 'A#m'
    """
    if chord.endswith(':maj'):
        return chord[:-4]
    elif chord.endswith(':min'):
        return chord[:-4] + 'm'
    else:
        return chord

def simplify_chords_dict(chords_by_time):
    """
    chords_by_time: {időpont: akkord_név, ...}
    Visszaad: ugyanilyen dict, de egyszerűsített nevekkel.
    """
    return {time: simplify_chord_name(chord) for time, chord in chords_by_time.items()}
