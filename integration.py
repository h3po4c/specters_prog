import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.integrate import simpson
from scipy.stats import pearsonr


def integrate_peak(x, y, x_min, x_max):
    mask = (x >= x_min) & (x <= x_max)
    x_selected = x[mask]
    y_selected = y[mask]
    if x_selected[0] > x_selected[-1]:
        x_selected = x_selected[::-1]
        y_selected = y_selected[::-1]
    return simpson(y_selected, x_selected)


def run_peak_integration(x, ys, temperatures):
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.subplots_adjust(left=0.1, bottom=0.35)
    for i in range(ys.shape[1]):
        ax.plot(x, ys[:, i], alpha=0.5)

    ax.set_xlabel('Энергия (эВ)')
    ax.set_ylabel('Интенсивность (отн. ед./эВ)')
    ax.set_title('Выберите диапазоны интегрирования для двух пиков')
    ax.grid(True)

    fill1 = None
    fill2 = None
    vlines = []

    ax_xmin1 = plt.axes([0.1, 0.2, 0.35, 0.03])
    ax_xmax1 = plt.axes([0.55, 0.2, 0.35, 0.03])
    ax_xmin2 = plt.axes([0.1, 0.1, 0.35, 0.03])
    ax_xmax2 = plt.axes([0.55, 0.1, 0.35, 0.03])

    slider_xmin1 = Slider(ax_xmin1, 'E1 min', x.min(), x.max(), valinit=x.min())
    slider_xmax1 = Slider(ax_xmax1, 'E1 max', x.min(), x.max(), valinit=x.max())
    slider_xmin2 = Slider(ax_xmin2, 'E2 min', x.min(), x.max(), valinit=x.min())
    slider_xmax2 = Slider(ax_xmax2, 'E2 max', x.min(), x.max(), valinit=x.max())

    def update(val):
        nonlocal fill1, fill2, vlines
        x1_min = slider_xmin1.val
        x1_max = slider_xmax1.val
        x2_min = slider_xmin2.val
        x2_max = slider_xmax2.val

        if x1_min > x1_max:
            x1_min, x1_max = x1_max, x1_min
        if x2_min > x2_max:
            x2_min, x2_max = x2_max, x2_min

        if fill1:
            fill1.remove()
        if fill2:
            fill2.remove()

        for vline in vlines:
            vline.remove()
        vlines = []

        mask1 = (x >= x1_min) & (x <= x1_max)
        mask2 = (x >= x2_min) & (x <= x2_max)
        fill1 = ax.fill_between(x[mask1], ys[:, 0][mask1], alpha=0.5, color='orange')
        fill2 = ax.fill_between(x[mask2], ys[:, 0][mask2], alpha=0.5, color='green')

        vlines.append(ax.axvline(x1_min, color='orange', linestyle='--'))
        vlines.append(ax.axvline(x1_max, color='orange', linestyle='--'))
        vlines.append(ax.axvline(x2_min, color='green', linestyle='--'))
        vlines.append(ax.axvline(x2_max, color='green', linestyle='--'))

        fig.canvas.draw_idle()

    slider_xmin1.on_changed(update)
    slider_xmax1.on_changed(update)
    slider_xmin2.on_changed(update)
    slider_xmax2.on_changed(update)

    update(None)
    plt.show()

    x1_min = slider_xmin1.val
    x1_max = slider_xmax1.val
    x2_min = slider_xmin2.val
    x2_max = slider_xmax2.val

    areas_peak1 = []
    areas_peak2 = []

    for i in range(ys.shape[1]):
        area1 = integrate_peak(x, ys[:, i], x1_min, x1_max)
        area2 = integrate_peak(x, ys[:, i], x2_min, x2_max)
        areas_peak1.append(area1)
        areas_peak2.append(area2)

    areas_peak1 = np.array(areas_peak1)
    areas_peak2 = np.array(areas_peak2)
    sum_peaks = areas_peak1 + areas_peak2

    correlation, _ = pearsonr(areas_peak1, areas_peak2)
    mean_sum = np.mean(sum_peaks)
    std_sum = np.std(sum_peaks)
    rel_std = std_sum / mean_sum * 100

    plt.figure(figsize=(10, 6))
    plt.plot(temperatures, areas_peak1, 'o-', label='Площадь Пика 1')
    plt.plot(temperatures, areas_peak2, 'o-', label='Площадь Пика 2')
    plt.plot(temperatures, sum_peaks, 'o-', label='Сумма Пиков')
    plt.hlines(0, temperatures.min(), temperatures.max(), colors='gray', linestyles=':')
    plt.hlines(mean_sum, temperatures.min(), temperatures.max(), colors='red', linestyles='--', label=f'Среднее: {mean_sum:.2f}, Погрешность: ±{rel_std:.2f}%')
    plt.fill_between(temperatures, mean_sum - std_sum, mean_sum + std_sum, color='red', alpha=0.2)
    plt.xlabel('Температура (K)')
    plt.ylabel('Площадь пика - Среднее')
    plt.title(f'Коэффициент корреляции: {correlation:.3f}')
    plt.legend()
    plt.grid(True)
    plt.show()
