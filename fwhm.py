import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.interpolate import interp1d
from matplotlib.widgets import Slider
from utils import save_results, show_found_peaks


def run_fwhm_analysis(x, ys, temperatures_all):
    def compute_fwhm(x, y, center, delta):
        from scipy.signal import find_peaks
        from scipy.interpolate import interp1d

        y = np.array(y)
        y_centered = y - np.min(y)

        # 1. Найти максимум в заданном диапазоне
        mask = (x >= center - delta) & (x <= center + delta)
        if np.sum(mask) < 5:
            return np.nan

        x_sub = x[mask]
        y_sub = y_centered[mask]

        peaks, _ = find_peaks(y_sub)
        if len(peaks) == 0:
            return np.nan

        local_peak_idx = peaks[np.argmax(y_sub[peaks])]
        global_peak_idx = np.where(y_centered == y_sub[local_peak_idx])[0][0]
        peak_y = y_centered[global_peak_idx]
        half_max = peak_y / 2

        # 2. Найти пересечения с уровнем полувысоты в полной кривой
        try:
            left_idx = np.where(y_centered[:global_peak_idx] <= half_max)[0][-1]
            x_left = interp1d(y_centered[left_idx:left_idx + 2], x[left_idx:left_idx + 2])(half_max)
        except:
            x_left = np.nan

        try:
            right_idx = np.where(y_centered[global_peak_idx:] <= half_max)[0][0] + global_peak_idx
            x_right = interp1d(y_centered[right_idx - 1:right_idx + 1], x[right_idx - 1:right_idx + 1])(half_max)
        except:
            x_right = np.nan

        if np.isnan(x_left) or np.isnan(x_right):
            return np.nan
        return abs(x_right - x_left)

    n_peaks = int(input("Введите количество пиков для анализа: "))

    fig, ax = plt.subplots()
    for i in range(ys.shape[1]):
        ax.plot(x, ys[:, i], alpha=0.3)
    ax.set_title('Выберите положения пиков и ширину поиска')
    ax.set_xlabel('Energy (eV)')
    ax.set_ylabel('Intensity')

    sliders = []
    markers = []
    regions = []
    initial_delta = 0.05  # Начальное значение дельты
    ax_delta = plt.axes([0.15, 0.05 + n_peaks * 0.03, 0.7, 0.02])
    slider_delta = Slider(ax_delta, 'Delta (eV)', 0.01, 0.3, valinit=initial_delta)

    for i in range(n_peaks):
        ax_slider = plt.axes([0.15, 0.05 + i * 0.03, 0.7, 0.02])
        init_val = x[np.argmax(ys[:, 0])] if i == 0 else x[np.argmax(ys[:, 0])]-0.1*i
        s = Slider(ax_slider, f'Peak {i+1}', x.min(), x.max(), valinit=init_val)
        sliders.append(s)
        marker = ax.axvline(s.val, color=f'C{i}', linestyle='--')
        region = ax.axvspan(s.val - initial_delta, s.val + initial_delta, color=f'C{i}', alpha=0.2)
        markers.append(marker)
        regions.append(region)

    def update(val):
        delta = slider_delta.val
        for i in range(n_peaks):
            marker = markers[i]
            region = regions[i]
            marker.set_xdata([sliders[i].val])
            region.remove()
            regions[i] = ax.axvspan(sliders[i].val - delta, sliders[i].val + delta, color=f'C{i}', alpha=0.2)
        fig.canvas.draw_idle()

    for s in sliders:
        s.on_changed(update)
    slider_delta.on_changed(update)

    plt.subplots_adjust(bottom=0.15 + n_peaks * 0.03)
    plt.show()

    peak_centers = [s.val for s in sliders]
    final_delta = slider_delta.val

    results = {'Temperature (K)': temperatures_all}
    for i, center in enumerate(peak_centers):
        fwhms = []
        for spectrum in ys.T:
            fwhms.append(compute_fwhm(x, spectrum, center=center, delta=final_delta))
        results[f'FWHM peak {i+1} (eV)'] = fwhms
        show_found_peaks(x, ys, center, final_delta, i)

    df = pd.DataFrame(results)

    plt.figure(figsize=(8, 5))
    for i in range(n_peaks):
        plt.plot(df['Temperature (K)'], df[f'FWHM peak {i+1} (eV)'], 'o-', label=f'Peak {i+1}')

    plt.xlabel('Temperature (K)')
    plt.ylabel('FWHM (eV)')
    plt.title('FWHM vs temperature')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    save = input("Сохранить результаты? (y/n): ").strip().lower()
    if save == 'y':
        save_results(df)
