import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import welch, detrend, butter, filtfilt, iirnotch
from fooof import FOOOF

class FOOOFAnalyzer:
    """Class to perform FOOOF analysis on a 1D signal and save results/plots."""

    def __init__(self, 
                 signal_obj, 
                 fs: float, 
                 out_dir: str = 'fooof_output', 
                 f_range: tuple = (1, 40),
                 peak_width_limits: tuple = (1, 8),
                 max_n_peaks: int = 6,
                 min_peak_height: float = 0.1,
                 peak_threshold: float = 2.0,
                 aperiodic_mode: str = 'fixed',
                 verbose: bool = False):
        """
        Initialize the FOOOF analyzer.

        Parameters:
        - signal_obj: object with a `.data` attribute (1D NumPy array).
        - fs: sampling frequency in Hz.
        - out_dir: directory to save outputs.
        - f_range: frequency range for FOOOF model fitting.
        - All other kwargs: FOOOF model tuning options.
        """
        self.signal = signal_obj.data
        self.fs = fs
        self.out_dir = out_dir
        self.f_range = f_range

        os.makedirs(self.out_dir, exist_ok=True)

        self.freqs = None
        self.psd = None
        self.results = {}

        self.fooof = FOOOF(
            peak_width_limits=peak_width_limits,
            max_n_peaks=max_n_peaks,
            min_peak_height=min_peak_height,
            peak_threshold=peak_threshold,
            aperiodic_mode=aperiodic_mode,
            verbose=verbose
        )


    def preprocess_signal(self,
                          detrend_signal: bool = True,
                          bandpass: tuple = (1, 40),
                          notch_freq: float = 60.0,
                          notch_quality: float = 30.0):
        """
        Preprocess the raw signal in-place by detrending, bandpass filtering, and notch filtering.
        """
        processed = self.signal.copy()

        # Detrend
        if detrend_signal:
            processed = detrend(processed)

        # Bandpass filter
        if bandpass is not None:
            low, high = bandpass
            nyq = self.fs / 2
            b, a = butter(N=4, Wn=[low / nyq, high / nyq], btype='band')
            processed = filtfilt(b, a, processed)

        # Notch filter (e.g. line noise at 60 Hz)
        if notch_freq is not None:
            nyq = self.fs / 2
            w0 = notch_freq / nyq
            b, a = iirnotch(w0, notch_quality)
            processed = filtfilt(b, a, processed)

        self.signal = processed

    def compute_psd(self, nperseg: int = 1024):
        """Compute the power spectral density using Welch's method."""
        freqs, psd = welch(self.signal, fs=self.fs, nperseg=nperseg)
        self.freqs = freqs
        self.psd = psd
        return freqs, psd

    def run_fooof(self):
        """Fit the FOOOF model to the PSD."""
        if self.freqs is None or self.psd is None:
            self.compute_psd()

        self.fooof.fit(self.freqs, self.psd, self.f_range)
        self.results = {
            'aperiodic_params': self.fooof.aperiodic_params_,
            'peak_params': self.fooof.peak_params_,
            'r_squared': self.fooof.r_squared_,
            'error': self.fooof.error_
        }

    def plot_results(self):
        """Save the FOOOF model plot."""
        fig_path = os.path.join(self.out_dir, 'fooof_fit.png')
        self.fooof.plot()
        plt.title('FOOOF Model Fit')
        plt.savefig(fig_path)
        plt.close()
        print(f"[Saved] FOOOF plot to {fig_path}")

    def sanity_psd_plot(self):
        """Plot and save the raw PSD (sanity check)."""
        plt.figure(figsize=(10, 5))
        plt.semilogy(self.freqs, self.psd, label='PSD')
        plt.xlim(self.f_range)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power')
        plt.title('Sanity Check: PSD')
        plt.grid(True)
        sanity_path = os.path.join(self.out_dir, 'sanity_check_psd.png')
        plt.savefig(sanity_path)
        plt.close()
        print(f"[Saved] Sanity PSD plot to {sanity_path}")

    def save_params(self):
        """Save extracted FOOOF parameters to CSV."""
        aperiodic_file = os.path.join(self.out_dir, 'aperiodic_params.csv')
        peak_file = os.path.join(self.out_dir, 'peak_params.csv')

        df = pd.DataFrame({
            'aperiodic_offset': [self.results['aperiodic_params'][0]],
            'aperiodic_exponent': [self.results['aperiodic_params'][1]],
            'r_squared': [self.results['r_squared']],
            'error': [self.results['error']],
        })
        df.to_csv(aperiodic_file, index=False)

        if len(self.results['peak_params']) > 0:
            peaks_df = pd.DataFrame(self.results['peak_params'], columns=['CF', 'PW', 'BW'])
            peaks_df.to_csv(peak_file, index=False)

        print(f"[Saved] Parameters to '{self.out_dir}'")

    def save_settings(self):
        """Save FOOOF settings used for the analysis."""
        settings_path = os.path.join(self.out_dir, 'fooof_settings.json')
        with open(settings_path, 'w') as f:
            json.dump(self.fooof.get_settings(), f, indent=4)
        print(f"[Saved] FOOOF settings to {settings_path}")

    def get_band_powers(self, bands=None):
        """
        Calculate power in specified frequency bands from PSD.

        Parameters:
        - bands: dict of {band_name: (low_freq, high_freq)}.
                 Defaults to common EEG bands if None.

        Returns:
        - dict of band powers {band_name: power}
        """
        if bands is None:
            bands = {
                'delta': (1, 4),
                'theta': (4, 8),
                'alpha': (8, 12),
                'beta': (12, 30),
                'gamma': (30, 40),
            }

        band_powers = {}
        for band_name, (low, high) in bands.items():
            mask = (self.freqs >= low) & (self.freqs <= high)
            power = np.trapz(self.psd[mask], self.freqs[mask])
            band_powers[band_name] = power

        return band_powers

    @staticmethod
    def plot_peak_features(all_peak_params_list):
        """
        Visualize peak center frequencies and powers across multiple FOOOF results.

        Parameters:
        - all_peak_params_list: list of peak_params arrays (each from one FOOOF fit).
          Each peak_params array shape: (n_peaks, 3) with columns CF, PW, BW.

        Produces:
        - Histogram of peak center frequencies
        - Scatter plot of peak frequency vs. power
        """
        all_cfs = []
        all_powers = []

        for peak_params in all_peak_params_list:
            if peak_params.size > 0:
                all_cfs.extend(peak_params[:, 0])
                all_powers.extend(peak_params[:, 1])

        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.hist(all_cfs, bins=30, color='skyblue', edgecolor='k')
        plt.xlabel('Peak Center Frequency (Hz)')
        plt.ylabel('Count')
        plt.title('Histogram of Peak Center Frequencies')

        plt.subplot(1, 2, 2)
        plt.scatter(all_cfs, all_powers, alpha=0.7)
        plt.xlabel('Peak Center Frequency (Hz)')
        plt.ylabel('Peak Power')
        plt.title('Peak Frequency vs. Power')

        plt.tight_layout()
        plt.show()

    def analyze(self):
        """Full analysis pipeline: preprocess → PSD → FOOOF → Plots → Save."""
        print("[INFO] Preprocessing signal...")
        self.preprocess_signal()
        print("[INFO] Computing PSD...")
        self.compute_psd()
        print("[INFO] Running FOOOF model...")
        self.run_fooof()
        print("[INFO] Generating sanity check plot...")
        self.sanity_psd_plot()
        print("[INFO] Plotting FOOOF model fit...")
        self.plot_results()
        print("[INFO] Saving parameters...")
        self.save_params()
        print("[INFO] Saving FOOOF settings...")
        self.save_settings()
        print("[INFO] Plotting time series, PSD, and FOOOF summary...")
        self.plot_time_psd_fooof(t=np.linspace(0, len(self.signal) / self.fs, len(self.signal)))
        print("[DONE] Analysis complete.")



    def plot_time_psd_fooof(self, t=None):
        """
        Plot the raw time series, PSD, and FOOOF fit together.
        
        Parameters:
        - t: Optional time vector (for time series plot). If None, x-axis will be samples.
        """
        fig, axs = plt.subplots(3, 1, figsize=(12, 10))

        # --- 1. Time series ---
        axs[0].plot(t if t is not None else np.arange(len(self.signal)), self.signal, color='black')
        axs[0].set_title("Preprocessed LFP Signal")
        axs[0].set_xlabel("Time (s)" if t is not None else "Samples")
        axs[0].set_ylabel("Amplitude")

        # --- 2. PSD ---
        axs[1].semilogy(self.freqs, self.psd, label="PSD", color='blue')
        axs[1].set_xlim(self.f_range)
        axs[1].set_title("Power Spectral Density")
        axs[1].set_xlabel("Frequency (Hz)")
        axs[1].set_ylabel("Power")
        axs[1].grid(True)

        # --- 3. FOOOF model fit ---
        self.fooof.plot(ax=axs[2], plot_peaks='shade', add_legend=True)
        axs[2].set_title("FOOOF Model Fit")

        plt.tight_layout()
        plot_path = os.path.join(self.out_dir, "summary_time_psd_fooof.png")
        plt.savefig(plot_path)
        plt.close()
        print(f"[Saved] Full summary plot to {plot_path}")


def generate_synthetic_lfp(duration=10.0, fs=1000, burst_bands=[(6, 10), (15, 25)],
                            noise_level=0.2, exponent=2.0, burst_power=0.5, seed=42):
    """
    Generate synthetic LFP with enhanced 1/f decay and subtle oscillatory bursts.

    Args:
        duration (float): Duration in seconds.
        fs (int): Sampling rate in Hz.
        burst_bands (list): List of (low, high) freq ranges for burst oscillations.
        noise_level (float): Std of additive white noise.
        exponent (float): Power exponent of 1/f component (higher = steeper decay).
        burst_power (float): Amplitude scale of bursts.
        seed (int): Random seed.

    Returns:
        np.ndarray: Synthetic LFP signal.
    """
    np.random.seed(seed)
    n_samples = int(duration * fs)
    t = np.linspace(0, duration, n_samples)

    # --- Create 1/f noise in frequency domain ---
    freqs = np.fft.rfftfreq(n_samples, d=1/fs)
    freqs[0] = freqs[1]  # avoid division by 0
    mag = 1 / (freqs ** exponent)  # 1/f^exponent
    phases = np.exp(1j * 2 * np.pi * np.random.rand(len(freqs)))
    fft_spectrum = mag * phases
    aperiodic = np.fft.irfft(fft_spectrum, n=n_samples)

    # --- Add oscillatory bursts ---
    bursts = np.zeros_like(t)
    for band in burst_bands:
        f = np.random.uniform(*band)
        burst_duration = np.random.uniform(0.3, 1.0)
        burst_start = np.random.randint(0, n_samples - int(burst_duration * fs))
        burst_end = burst_start + int(burst_duration * fs)
        envelope = np.hanning(burst_end - burst_start)
        sine = np.sin(2 * np.pi * f * t[:burst_end - burst_start])
        bursts[burst_start:burst_end] += burst_power * envelope * sine

    # --- Add white noise ---
    noise = np.random.normal(0, noise_level, size=n_samples)

    # --- Final signal ---
    signal = aperiodic + bursts + noise
    return signal



class SignalObject:
    """Simple signal wrapper with a `.data` attribute."""
    def __init__(self, data: np.ndarray):
        self.data = data


# ========================
# Example usage
# ========================
if __name__ == "__main__":
    duration = 10  # seconds

    lfp = generate_synthetic_lfp(duration=10.0, fs=1000)
    signal = SignalObject(lfp)


    analyzer = FOOOFAnalyzer(
        signal_obj=signal,
        fs=500,
        out_dir='fooof_results',
        f_range=(1, 40),
        peak_width_limits=(0.5, 12),
        max_n_peaks=8,
        min_peak_height=0.05,
        peak_threshold=1.5,
        aperiodic_mode='knee',
        verbose=False
    )

    analyzer.analyze()

    # Example: get band powers
    band_powers = analyzer.get_band_powers()
    print("Band Powers:", band_powers)

    # Example: visualize peaks from multiple analyses (dummy example)
    # plot_peak_features expects a list of arrays, e.g., [fooof1.peak_params_, fooof2.peak_params_]
    # Here, just use the current result as a singleton list
    FOOOFAnalyzer.plot_peak_features([analyzer.results['peak_params']])