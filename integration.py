import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.integrate import simpson
from scipy.stats import pearsonr

from utils import save_results


def integrate_peak(x, y, x_min, x_max):
    mask = (x >= x_min) & (x <= x_max)
    x_selected = x[mask]
    y_selected = y[mask]
    if x_selected[0] > x_selected[-1]:
        x_selected = x_selected[::-1]
        y_selected = y_selected[::-1]
    return simpson(y_selected, x_selected)


def run_peak_integration(x, ys, temperatures):
    n_peaks = int(input("Введите количество пиков: "))

    fig, ax = plt.subplots(figsize=(10, 6))
    plt.subplots_adjust(left=0.1, bottom=0.35 + n_peaks * 0.04)

    for i in range(ys.shape[1]):
        ax.plot(x, ys[:, i], alpha=0.5)

    ax.set_xlabel('Энергия (эВ)')
    ax.set_ylabel('Интенсивность (отн. ед./эВ)')
    ax.set_title('Выберите диапазоны интегрирования для каждого пика')
    ax.grid(True)

    sliders = []
    vlines = []
    fills = []

    x_mins = [x.min()] * n_peaks
    x_maxs = [x.max()] * n_peaks

    def update(val):
        # Удалить старые линии и заливки
        while vlines:
            vlines.pop().remove()
        while fills:
            fills.pop().remove()

        # Нарисовать новые
        for i in range(n_peaks):
            x_mins[i] = sliders[i * 2].val
            x_maxs[i] = sliders[i * 2 + 1].val
            if x_mins[i] > x_maxs[i]:
                x_mins[i], x_maxs[i] = x_maxs[i], x_mins[i]

            # Вертикальные маркеры
            vlines.append(ax.axvline(x_mins[i], color=f'C{i}', linestyle='--'))
            vlines.append(ax.axvline(x_maxs[i], color=f'C{i}', linestyle='--'))

            # Закрашивание
            mask = (x >= x_mins[i]) & (x <= x_maxs[i])
            fills.append(ax.fill_between(x[mask], ys[:, 0][mask], alpha=0.2, color=f'C{i}'))
            fills.append(ax.fill_between(x[mask], ys[:, -1][mask], alpha=0.2, color=f'C{i}'))

        fig.canvas.draw_idle()

    # Слайдеры
    for i in range(n_peaks):
        ax_min = plt.axes([0.1, 0.05 + i * 0.06, 0.35, 0.03])
        ax_max = plt.axes([0.55, 0.05 + i * 0.06, 0.35, 0.03])
        s_min = Slider(ax_min, f'E{i+1} min', x.min(), x.max(), valinit=x.min())
        s_max = Slider(ax_max, f'E{i+1} max', x.min(), x.max(), valinit=x.max())
        s_min.on_changed(update)
        s_max.on_changed(update)
        sliders.extend([s_min, s_max])

    update(None)
    plt.show()
    areas_by_peak = []
    for i in range(n_peaks):
        areas = []
        for j in range(ys.shape[1]):
            area = integrate_peak(x, ys[:, j], x_mins[i], x_maxs[i])
            areas.append(area)
        areas_by_peak.append(areas)
    sum_peaks = np.sum(areas_by_peak, axis=0)
    plt.plot(temperatures, sum_peaks, 'o-', label=f'Суммарная интенсивность')
    for i in range(n_peaks):
        plt.plot(temperatures, areas_by_peak[i], 'o-', label=f'Пик {i + 1}')
    plt.xlabel('Температура (K)')
    plt.ylabel('Площадь пика')
    plt.title('Зависимость площади пиков от температуры')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


    df = pd.DataFrame({'Temperature, K': temperatures})
    for i in range(n_peaks):
        df[f'Square of peak {i+1}'] = areas_by_peak[i]
    df['Summ of intensity'] = sum_peaks
    save = input("Сохранить результаты? (y/n): ").strip().lower()
    if save == 'y':
        save_results(df)
