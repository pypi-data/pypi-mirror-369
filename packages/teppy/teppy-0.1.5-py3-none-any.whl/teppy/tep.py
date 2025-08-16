import numpy as np
import mne
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
from types import SimpleNamespace
from .helpers import (_compute_tep_peaks, _neigh_correction,
                     _validate_ntop, _validate_pick_ch,
                     _compute_timefreq)
from .timefreq import TimeFreq  # Import from sibling module

# -------------------------
# Core TEP Class
# -------------------------
class TEP:
    def __init__(self, epochs, exclude_channels=None,
                 p1_range=[0.01, 0.04], low_limit=35,
                 sign_corr='convexity'):
        """
        Initialize TEP object with automatic peak computation

        Args:
            epochs: mne.Epochs object
            exclude_channels: Channels to exclude
            p1_range: Time window for first peak detection (s)
            low_limit: Maximum frequency (Hz) considered for peak separation.
                Determines the minimum time interval between consecutive peaks as:
                    min_interval = 1/(low_limit * 2) seconds
                Lower values enforce stricter temporal separation (wider peak spacing).
                Higher values allow closer peak detection (tighter peak spacing).
                (Default: 35 Hz ≈ 14 ms separation)
            sign_corr: Method for signal correction
        """
        # Process epochs
        if exclude_channels:
            self.epochs = epochs.copy().drop_channels(exclude_channels)
        else:
            self.epochs = epochs.copy()

        # heuristic: data are either in V or µV: if data are in V, this condition is satisfied for typical EEG values
        if np.max(self.epochs._data) < 1e-3:
            self.epochs._data *= 1e6  # Convert to µV
        # Core data attributes
        self.tep_data = self.epochs.average()  # mne evoked object
        self.times = self.epochs.times
        self.ch_names = np.array(self.epochs.ch_names, dtype='object')

        # Create structured metadata container
        self.info = SimpleNamespace(
            n_channels=len(self.ch_names),
            n_epochs=len(self.epochs),
            sfreq=self.epochs.info['sfreq'],
            p1_range=p1_range,
            low_limit=low_limit,
            sign_corr=sign_corr
        )

        # Compute peaks immediately using helper function '_compute_tep_peaks'
        (self.idxs_peaks,
         self.amp_peaks,
         self.lat_peaks,
         self.amp_p2p,
         self.interpeak) = _compute_tep_peaks(
            times=self.times,
            tep_data=self.tep_data.get_data(),
            sfreq=self.info.sfreq,
            p1_range=p1_range,
            low_limit=low_limit,
            sign_corr=sign_corr
        )

    def __repr__(self):
        # Calculate time range
        time_range = (self.times[0], self.times[-1])
        time_str = f"{time_range[0]:.3f}-{time_range[1]:.3f}s"
        # Format sampling frequency
        sfreq_str = f"{self.info.sfreq:.1f} Hz"
        # Format peak detection parameters
        peak_info = (f"  P1 range: [{self.info.p1_range[0]:.3f}, {self.info.p1_range[1]:.3f}] s\n"
                     f"  Low limit: {self.info.low_limit} Hz\n"
                     f"  Sign correction: {self.info.sign_corr}")

        return (f"<TEP\n"
                f"  Channels: {self.info.n_channels}\n"
                f"  Epochs: {self.info.n_epochs}\n"
                f"  Time points: {len(self.times)}\n"
                f"  Time range: {time_str}\n"
                f"  Sampling: {sfreq_str}\n"
                f"  Peak detection:\n{peak_info}\n"
                f">")

    # -------------------------
    # Core Data Access Methods
    # -------------------------
    def get_epo(self, pick_ch=None):
        """Return epochs data (epochs × channels × time)"""
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.epochs.get_data()[:, ch_idxs]
        return self.epochs.get_data()

    def get_tep(self, pick_ch=None):
        """Return averaged TEP data (channels × time)"""
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.tep_data.get_data()[ch_idxs]
        return self.tep_data.get_data()

    def get_gmfp(self, pick_ch=None):
        """Return global(local) mean field power data (time)"""
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return np.sqrt(np.mean(self.tep_data.get_data()[ch_idxs] ** 2, 0))
        return np.sqrt(np.mean(self.tep_data.get_data() ** 2, 0))

    # -------------------------
    # Feature Access Methods
    # -------------------------
    def get_amplitudes(self, pick_ch=None, ntop=4, neighbors_correction=True, verbose=False):
        """Get peak amplitudes (P1, P2, P3)

        Args:
            pick_ch: Channels to select (list of names or indices). Overrides ntop.
            ntop: Number of top channels to return (ignored if pick_ch is used)
            - None: Returns all channels (unsorted)
            - int: Returns top N channels sorted by P1-P2 amplitude
                   (must be between 1 and total channel count)
            neighbors_correction: Apply spatial correction in the ntop selection
            verbose: Print selection details

        Returns:
            Array of channel peak amplitudes with shape (channels x 3), where the 
                second dimension correspond to P1, P2, and P3 amplitudes, respectively.
        """
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.amp_peaks[ch_idxs]

        if ntop is None or ntop == self.info.n_channels:
            return self.amp_peaks

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return self.amp_peaks[idxs_ntop]

    def get_latencies(self, pick_ch=None, ntop=4, neighbors_correction=True, verbose=False):
        """Get peak latencies (P1, P2, P3) in seconds

        Args:
            pick_ch: Channels to select (list of names or indices). Overrides ntop.
            ntop: Number of top channels to return (ignored if pick_ch is used)
            - None: Returns all channels (unsorted)
            - int: Returns top N channels sorted by P1-P2 amplitude
                   (must be between 1 and total channel count)
            neighbors_correction: Apply spatial correction in the ntop selection
            verbose: Print selection details

        Returns:
            Array of channel peak latencies with shape (channels x 3), where the 
                second dimension correspond to P1, P2, and P3 latencies, respectively.
        """
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.lat_peaks[ch_idxs]

        if ntop is None:
            return self.lat_peaks

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return self.lat_peaks[idxs_ntop]

    def get_peaktopeak(self, pick_ch=None, ntop=4, neighbors_correction=True, verbose=False):
        """Get peak-to-peak amplitudes (P1-P2, P2-P3)

        Args:
            pick_ch: Channels to select (list of names or indices). Overrides ntop.
            ntop: Number of top channels to return (ignored if pick_ch is used)
            - None: Returns all channels (unsorted)
            - int: Returns top N channels sorted by P1-P2 amplitude
                   (must be between 1 and total channel count)
            neighbors_correction: Apply spatial correction in the ntop selection
            verbose: Print selection details

        Returns:
            Array of channel peak-to-peak amplitudes with shape (channels x 2), where the 
                second dimension correspond to P1-P2, and P2-P2 peak-to-peak amplitudes, respectively.
        """
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.amp_p2p[ch_idxs]

        if ntop is None:
            return self.amp_p2p

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return self.amp_p2p[idxs_ntop]

    def get_interpeak(self, pick_ch=None, ntop=4, neighbors_correction=True, verbose=False):
        """Get interpeak intervals (P3-P1) in seconds

        Args:
            pick_ch: Channels to select (list of names or indices). Overrides ntop.
            ntop: Number of top channels to return (ignored if pick_ch is used)
            - None: Returns all channels (unsorted)
            - int: Returns top N channels sorted by P1-P2 amplitude
                   (must be between 1 and total channel count)
            neighbors_correction: Apply spatial correction in the ntop selection
            verbose: Print selection details

        Returns:
            Array of channel interpeak.
        """
        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return self.interpeak[ch_idxs]

        if ntop is None:
            return self.interpeak

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return self.interpeak[idxs_ntop]

    def get_slope_peaks(self, pick_ch=None, ntop=4, neighbors_correction=True, verbose=False):
        """Get slope between subsequent peaks (P1-P2, P2-P3). The unit is µV/ms

        Args:
            pick_ch: Channels to select (list of names or indices). Overrides ntop.
            ntop: Number of top channels to return (ignored if pick_ch is used)
            - None: Returns all channels (unsorted)
            - int: Returns top N channels sorted by P1-P2 amplitude
                   (must be between 1 and total channel count)
            neighbors_correction: Apply spatial correction in the ntop selection
            verbose: Print selection details

        Returns:
            Array of channel slopes with shape (channels x 2), where the 
                second dimension correspond to P1-P2, and P2-P3 slopes, respectively.
        """
        slope = lambda x1, y1, x2, y2: np.divide((y2 - y1), (x2 - x1),
                                                 out=np.full_like(x1, np.inf, dtype=float),
                                                 where=(x2 != x1))
        lat_p1, lat_p2, lat_p3 = self.lat_peaks.T * 1e3  # from s to ms
        amp_p1, amp_p2, amp_p3 = self.amp_peaks.T
        slope_p1p2 = slope(lat_p1, amp_p1, lat_p2, amp_p2)
        slope_p2p3 = slope(lat_p2, amp_p2, lat_p3, amp_p3)
        slope_peaks = np.vstack((slope_p1p2, slope_p2p3)).T

        if pick_ch is not None:
            ch_idxs = _validate_pick_ch(pick_ch, self.ch_names)
            return slope_peaks[ch_idxs]

        if ntop is None:
            return slope_peaks

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return slope_peaks[idxs_ntop]

    # -------------------------
    # Info selected channels
    # -------------------------
    def get_ntop_ch(self, ntop=4, neighbors_correction=True, verbose=False):
        """Get top channel names based on P1-P2 amplitude

        Args:
            ntop: Number of top channels to return.
            - int: Returns top N channels sorted by P1-P2 amplitude
            neighbors_correction: Apply spatial correction in the ntop selection
            verbose: Print selection details

        Returns:
            Array of channel names.
        """
        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False
        )
        return self.ch_names[idxs_ntop]

    def get_ntop_idx(self, ntop=4, neighbors_correction=True, return_orig=False, verbose=False):
        """Get top channel indices based on P1-P2 amplitude

        Args:
            ntop: Number of top channels to return.
            - int: Returns top N channels sorted by P1-P2 amplitude
            neighbors_correction: Apply spatial correction in the ntop selection
            return_orig: Return both corrected and original indices
            verbose: Print selection details

        Returns:
            idxs_ntop (and optionally idxs_ntop_orig).
        """
        # Get P1-P2 amplitudes (first column of amp_p2p)
        amp_p1p2 = self.amp_p2p[:, 0]
        # Get initial top channels based on amplitude
        idxs_ntop_orig = np.argsort(amp_p1p2)[::-1][:ntop]
        # Apply neighbor correction if requested
        if neighbors_correction:
            idxs_ntop, idxs_ntop_orig = _neigh_correction(
                self.epochs.info,
                amp_p1p2,
                idxs_ntop_orig
            )
        else:
            idxs_ntop = idxs_ntop_orig.copy()
        if verbose:
            if np.array_equal(idxs_ntop, idxs_ntop_orig):
                print(f'Neighbors correction not applied! Selected channels: {self.ch_names[idxs_ntop]}')
            else:
                print(f'New channels: {self.ch_names[idxs_ntop]}')
                print(f'Original channels: {self.ch_names[idxs_ntop_orig]}')
        if return_orig:
            return idxs_ntop, idxs_ntop_orig
        else:
            return idxs_ntop

    def info_ntop(self, ntop=4, neighbors_correction=True, verbose=False, ):
        """Get comprehensive info about top channels

        Args:
            ntop: Number of top channels.
            neighbors_correction: Apply spatial correction Apply spatial correction in the ntop selection.
            verbose: Print selection details (default: False).

        Returns dictionary with:
            - channels: Corrected channel names (if neighbors_correction is applied)
            - channels_original: Original channel names (before correction)
            - amplitudes: Peak amplitudes
            - latencies: Peak latencies
            - peak_to_peak: P1-P2 and P2-P3 amplitudes
            - interpeaks: P3-P1 intervals
        """
        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop, idxs_ntop_orig = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=True
        )

        return {
            'channels': self.ch_names[idxs_ntop].tolist(),
            'channels_original': self.ch_names[idxs_ntop_orig].tolist(),
            'amplitudes': self.amp_peaks[idxs_ntop],
            'latencies': self.lat_peaks[idxs_ntop],
            'peak_to_peak': self.amp_p2p[idxs_ntop],
            'interpeaks': self.interpeak[idxs_ntop],
            'slopes': self.get_slope_peaks(ntop=ntop, neighbors_correction=neighbors_correction)
        }

    # -------------------------
    # Visualization
    # -------------------------
    def plot_summary(self, ntop=4, tlim=(-100, 300), title='',
                     neighbors_correction=True, verbose=False,
                     cmap_topo='viridis', topo_lim=(0, None), table_max_ch=4):
        """
        Generate a comprehensive summary plot of TEP analysis on the selected channels

        The plot contains three panels:
        1. Time series: Shows TEP waveforms for top channels with detected peaks
        2. Latency table: Displays peak latencies for top channels
        3. Topographic map: Visualizes P1-P2 amplitude distribution

        Args:
            ntop: Number of top channels to display (default=4)
            tlim: Time limits for time series plot in milliseconds (default=(-100, 300))
            title: Main title for the plot (default='')
            neighbors_correction: Apply spatial neighbor correction to channel selection (default=True)
            verbose: Print channel selection details (default=False)
            cmap_topo: Colormap for topographic plot (default='Reds')
            topo_lim: Color limits for topographic plot as (vmin, vmax) (default=(0, None))
            table_max_ch: Maximum number of channels reported in the table (max number of rows)

        Returns:
            matplotlib.figure.Figure: The generated figure object

        Example:
            fig = tep.plot_summary(
                ntop=5,
                tlim=(-50, 250),
                title="Subject 01 - TEP Summary",
                cmap_topo='viridis',
                topo_lim=(0, 10)
            )
            fig.savefig('tep_summary.png')
        """

        ntop = _validate_ntop(ntop, self.info.n_channels)
        idxs_ntop = self.get_ntop_idx(
            ntop=ntop,
            neighbors_correction=neighbors_correction,
            verbose=verbose,
            return_orig=False)

        fig = plt.figure(figsize=(6, 5), dpi=300, facecolor='none')
        gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1])

        ax = fig.add_subplot(gs[0, :])
        plt.suptitle(title)
        plt.grid()
        peak_col = ['darkred', 'red', 'salmon']
        for i, ch in enumerate(idxs_ntop):
            peaks_time = self.lat_peaks[ch]
            lab = self.ch_names[ch]
            ax.plot(self.times * 1e3, self.tep_data.get_data()[ch], label=lab, lw=2)
            for p in range(3):
                pks_plot = ax.plot(peaks_time[p] * 1e3, self.tep_data.get_data()[ch, self.idxs_peaks[ch, p]],
                                   'o', ms=6, zorder=6, color=peak_col[p])
            ax.set_xlim(tlim)
            ax.set_xlabel('time (ms)')
            ax.set_ylabel(r'amplitude ($\mu$V)')
            ax.legend(fontsize=6)
        ax.legend()
        ax.set_xticks(np.arange(tlim[0], tlim[1] + 1, step=50))
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')

        ax2 = fig.add_subplot(gs[1, 0])
        ax2.axis('off')
        col_labels = [f'P$_{n + 1}$' for n in range(3)]
        row_labels = self.ch_names[idxs_ntop]
        rcol = plt.get_cmap('tab10').colors[:ntop]
        rcol = [(r, g, b, 0.5) for (r, g, b) in rcol]
        ccol = [mcolors.to_rgba(c, alpha=0.5) for c in peak_col]
        table = ax2.table(cellText=np.round(self.lat_peaks[idxs_ntop][:table_max_ch] * 1e3, 1),
                          rowLabels=row_labels[:table_max_ch], colLabels=col_labels,
                          loc='center', cellLoc='center', bbox=[0, 0, 1, 1],
                          rowColours=rcol[:table_max_ch], colColours=ccol)
        for key, cell in table.get_celld().items():
            cell.get_text().set_fontsize(14)
        for col in range(len(col_labels)):
            table[(0, col)].get_text().set_fontweight('bold')
        for row in range(len(row_labels[:table_max_ch])):
            table[(row + 1, -1)].get_text().set_fontweight('bold')

        ax3 = fig.add_subplot(gs[1, 1])
        amp_p1p2 = self.amp_p2p[:, 0]
        im, cn = mne.viz.plot_topomap(amp_p1p2, self.epochs.info, axes=ax3, names=self.ch_names,
                                      sensors=False, cmap=cmap_topo, vlim=topo_lim, contours=3)
        cax = fig.colorbar(im, ax=ax3, shrink=0.5)
        cax.set_label(f'peak-to-peak ($\\mu$V)', fontsize=8)

        plt.subplots_adjust(wspace=0, hspace=0.05)

        return fig
