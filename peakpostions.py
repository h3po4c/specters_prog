from utils import save_results, show_found_peaks
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.signal import find_peaks


def run_peak_positions(x, ys, temperatures_all):
    n_peaks = int(input("Введите количество пиков для анализа: "))

    fig, ax = plt.subplots()
    for i in range(ys.shape[1]):
        ax.plot(x, ys[:, i], alpha=0.5)
    ax.set_title('Укажите примерное положение каждого пика')
    ax.set_xlabel('Энергия (эВ)')
    ax.set_ylabel('Интенсивность')

    sliders = []
    markers = []
    regions = []
    delta = 0.05
    delta_slider = plt.axes([0.15, 0.05 + n_peaks * 0.03, 0.7, 0.02])
    deltas = Slider(delta_slider, f'Ширина поиска', 0.01, 2, valinit=delta)

    for i in range(n_peaks):
        ax_slider = plt.axes([0.15, 0.05 + i * 0.03, 0.7, 0.02])
        s = Slider(ax_slider, f'Peak {i+1} pos', x.min(), x.max(), valinit=x[np.argmax(ys[:, 0])])
        sliders.append(s)
        marker = ax.axvline(s.val, color='C{}'.format(i), linestyle='--')
        markers.append(marker)
        region = ax.axvspan(s.val - delta, s.val + delta, color='C{}'.format(i), alpha=0.2)
        regions.append(region)

        def update_slider(val, i=i):
            delta = deltas.val
            markers[i].set_xdata([sliders[i].val])
            regions[i].remove()
            regions[i] = ax.axvspan(sliders[i].val - delta, sliders[i].val + delta, color='C{}'.format(i), alpha=0.2)
            regions[i].set_bounds(sliders[i].val - delta, 0, 2 * delta, 1)
            fig.canvas.draw_idle()

        deltas.on_changed(update_slider)
        s.on_changed(update_slider)

    plt.subplots_adjust(bottom=0.1 + n_peaks * 0.03)
    plt.show()

    peak_guesses = [s.val for s in sliders]

    peak_positions = [[] for _ in range(n_peaks)]

    for spectrum in ys.T:
        peaks, _ = find_peaks(spectrum)
        peak_x = x[peaks]
        peak_y = spectrum[peaks]

        for i, center in enumerate(peak_guesses):
            mask = (peak_x >= center - delta) & (peak_x <= center + delta)

            if np.any(mask):
                idx = peaks[mask][np.argmax(peak_y[mask])]
                peak_positions[i].append(x[idx])
            else:
                peak_positions[i].append(np.nan)

    data = {'Temperature (K)': temperatures_all}
    for i in range(n_peaks):
        show_found_peaks(x, ys, center, delta, i)
        data[f'Peak {i+1} Position (eV)'] = peak_positions[i]

    df = pd.DataFrame(data)

    plt.figure(figsize=(8, 5))
    for i in range(n_peaks):
        plt.plot(df['Temperature (K)'], df[f'Peak {i+1} Position (eV)'], 'o-', label=f'Peak {i+1}')

    plt.xlabel('Температура (K)')
    plt.ylabel('Положение пика (эВ)')
    plt.title('Смещение положения пиков в зависимости от температуры')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    save = input("Сохранить результаты? (y/n): ").strip().lower()
    if save == 'y':
        save_results(df)
